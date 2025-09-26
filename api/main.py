from fastapi import FastAPI, Depends, HTTPException, Query
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware 
from api.dtos.metricFilterParams import MetricsFilterParams, get_metrics_filters
from api.models.myLoginRequestForm import MyLoginRequestForm
from .auth.models import Token
from .auth.services import PasswordAuthenticationService
from .auth.dependencies import get_current_user
from .repositories.user_repository import PolarsUserRepository
from .repositories.metrics_repository import PolarsMetricsRepository
from .utils.timing import time_function

from scalar_fastapi import get_scalar_api_reference

app = FastAPI(
    title="Desafio Técnico Monks - Python API",
    description="Documentação da API com Scalar",
    version="1.0.0",
    openapi_url="/openapi.json"  
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        scalar_proxy_url="https://proxy.scalar.com",
        
        
    )

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
user_repository = PolarsUserRepository()
auth_service = PasswordAuthenticationService(user_repository, pwd_context)
metrics_repository = PolarsMetricsRepository()

@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}

@app.post("/login", response_model=Token)
async def login(form_data: MyLoginRequestForm = Depends()):
    user = auth_service.authenticate_user(form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    access_token = auth_service.create_access_token(data={"sub": user["email"], "role": user["role"]})
    return {"token": access_token}

@app.get("/metrics")
async def get_metrics(
    filters: MetricsFilterParams = Depends(get_metrics_filters),
    current_user: dict = Depends(get_current_user)
):
    df, polars_time = time_function(
        metrics_repository.get_metrics,
        filters,
        user_role=current_user["role"]
    )

    return {
        "polars_read_time_seconds": polars_time,
        "data_preview": df.to_dicts()
    }

