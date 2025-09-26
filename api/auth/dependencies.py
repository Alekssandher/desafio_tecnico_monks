from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from jose import JWTError, jwt
from ..config.config import Config
from ..repositories.user_repository import PolarsUserRepository

bearer_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    user_repository: PolarsUserRepository = Depends(PolarsUserRepository)
) -> dict:
    token = credentials.credentials  
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