from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from typing import Optional
from datetime import date
from .auth.models import Token
from .auth.services import PasswordAuthenticationService
from .auth.dependencies import get_current_user
from .repositories.user_repository import PolarsUserRepository
from .repositories.metrics_repository import PolarsMetricsRepository
from .utils.timing import time_function

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
user_repository = PolarsUserRepository()
auth_service = PasswordAuthenticationService(user_repository, pwd_context)
metrics_repository = PolarsMetricsRepository()

@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}

@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    access_token = auth_service.create_access_token(data={"sub": user["email"], "role": user["role"]})
    return {"token": access_token}

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
    df, polars_time = time_function(
        metrics_repository.get_metrics,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
        order_by=order_by,
        descending=descending,
        user_role=current_user["role"]
    )
    return {
        "polars_read_time_seconds": polars_time,
        "data_preview": df.to_dicts()
    }