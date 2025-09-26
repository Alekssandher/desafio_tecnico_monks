from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from ..config.config import Config
from ..repositories.user_repository import PolarsUserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme), user_repository: PolarsUserRepository = Depends(PolarsUserRepository)) -> dict:
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if email is None or role is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError as e:
        print("Erro JWT:", e)
        raise HTTPException(status_code=401, detail="Token inválido")
    user = user_repository.get_user(email)
    if user is None:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return user