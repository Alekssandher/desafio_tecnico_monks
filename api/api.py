from datetime import date, datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, Query
from passlib.context import CryptContext
app = FastAPI()


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}

import polars as pl
import time
import os
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY") 
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# utilitários
def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_user(username: str):

    df = pl.scan_csv("api/data/users.csv")
    
    result = df.filter(pl.col("username") == username).collect()

    if result.is_empty():
        return None
    
    return result.to_dicts()[0]

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or not password == user["password"]:
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def time_function(func, *args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    return result, end_time - start_time

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user["username"],
            "role": user["role"]
            },
            expires_delta=access_token_expires
    )
    return {"access_token": access_token}


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")

        if username is None or role is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError as e:
        print("Erro JWT:", e)
        raise HTTPException(status_code=401, detail="Token inválido")
    user = get_user(username)
    if user is None:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return user

@app.get("/metrics")
async def get_metrics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    order_by: Optional[str] = Query(None, description="Coluna para ordenação"),
    descending: bool = Query(False, description="True para ordem decrescente"),
    current_user: dict = Depends(get_current_user)
):
    def read_and_limit():
        df = pl.scan_csv(
            "api/data/metrics.csv",
            try_parse_dates=True,
            ignore_errors=True,
        )
        print("Current user:", current_user)

        if current_user["role"] != "admin":
            df = df.drop("cost_micros")

        df = df.with_columns(
            pl.col("date").cast(pl.Date, strict=False).fill_null(pl.date(2000, 1, 1)),
            pl.col("account_id").cast(pl.Int64, strict=False).fill_null(0),
            pl.col("campaign_id").cast(pl.Int64, strict=False).fill_null(0),
            pl.col("clicks").cast(pl.Float64, strict=False).fill_null(0.0),
            pl.col("conversions").cast(pl.Float64, strict=False).fill_null(0.0),
            pl.col("impressions").cast(pl.Float64, strict=False).fill_null(0.0),
            pl.col("interactions").cast(pl.Float64, strict=False).fill_null(0.0),
        )

        if start_date:
            df = df.filter(pl.col("date") >= start_date)
        if end_date:
            df = df.filter(pl.col("date") <= end_date)

        if order_by:

            available_cols = df.schema.keys()
            if order_by in available_cols:
                df = df.sort(order_by, descending=descending)

        
        return df.slice(offset, limit).collect()

    df, polars_time = time_function(read_and_limit)
    return {
        "polars_read_time_seconds": polars_time,
        "data_preview": df.to_dicts()
    }