from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt
from ..config.config import Config

class AuthenticationService(ABC):
    @abstractmethod
    def verify_password(self, plain: str, hashed: str) -> bool:
        pass

    @abstractmethod
    def authenticate_user(self, email: str, password: str) -> Optional[dict[str, str]]:
        pass

    @abstractmethod
    def create_access_token(self, data: dict[str, str], expires_delta: Optional[timedelta] = None) -> str:
        pass

class PasswordAuthenticationService(AuthenticationService):
    def __init__(self, user_repository, pwd_context: CryptContext):
        self.user_repository = user_repository
        self.pwd_context = pwd_context

    def verify_password(self, plain: str, hashed: str) -> bool:
        return self.pwd_context.verify(plain, hashed)

    def authenticate_user(self, email: str, password: str) -> Optional[dict[str, str]]:
        user = self.user_repository.get_user(email)
        if not user or not self.verify_password(password, user["password"]):
            return None
        return user

    def create_access_token(self, data: dict[str, str], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, Config.SECRET_KEY, algorithm=Config.ALGORITHM)