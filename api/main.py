import time
from typing import Dict, List

from fastapi import FastAPI, Depends, HTTPException,  Request
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware 
from api.dtos.metricFilterParams import MetricsFilterParams, get_metrics_filters
from api.models.myLoginRequestForm import MyLoginRequestForm
from api.repositories.metrics_db_repository import MySQLMetricsDbRepository
from .auth.models import Token
from .auth.services import PasswordAuthenticationService
from .auth.dependencies import get_current_user
from .repositories.user_csv_repository import PolarsUserCsvRepository
from .repositories.metrics_csv_repository import PolarsMetricsCsvRepository

from scalar_fastapi import get_scalar_api_reference

from fastapi.concurrency import run_in_threadpool
from .config.config import Config

app = FastAPI(
    title="Desafio Técnico Monks - Python API",
    description="Documentação da API com Scalar",
    version="1.0.0",
    openapi_url="/openapi.json"  
)

db_config = {
    "host": Config.DB_URL,
    "user": Config.DB_USER,
    "password": Config.DB_PASSWORD,
    "database": Config.DB_NAME,
    "allow_local_infile": True
}
metrics_repo = MySQLMetricsDbRepository(db_config=db_config)

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
user_csv_repository = PolarsUserCsvRepository()
auth_service = PasswordAuthenticationService(user_csv_repository, pwd_context)
metrics_csv_repository = PolarsMetricsCsvRepository()

# middleware para devolver o tempo da requisição no header
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    end_time = time.perf_counter()
    execution_time_ms = (end_time - start_time) * 1000
    
    response.headers["X-Process-Time-Ms"] = str(execution_time_ms)
    
    print(f"Request to '{request.url.path}' took {execution_time_ms:.4f} ms")
    
    return response

@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}

@app.post("/login", response_model=Token)
async def login(form_data: MyLoginRequestForm = Depends()):
    """
    Utiliza as credenciais do arquivo csv para gerar token jwt para login.
    """

    user = auth_service.authenticate_user(form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    access_token = auth_service.create_access_token(data={"sub": user["email"], "role": user["role"]})
    return {"token": access_token}

@app.get("/metrics/csv")
async def get_metrics_csv(
    filters: MetricsFilterParams = Depends(get_metrics_filters),
    current_user: dict = Depends(get_current_user)
):
    """
    Busca as métricas pelo arquivo csv.
    """
    df = await run_in_threadpool(metrics_csv_repository.get_metrics, filters, current_user["role"])
    
    return {
        "data_preview": df.to_dicts()
    }


@app.get("/metrics/db", response_model=List[Dict])
def get_metrics_db(
    filters: MetricsFilterParams = Depends(get_metrics_filters),
    current_user: str = Depends(get_current_user)
):
    """
    Busca as métricas pelo banco de dados, preenchido com os valores importados do arquivo csv.
    """
    try:
        res = metrics_repo.get_metrics(filters=filters, user_role=current_user['role'])
        return res
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Something Went Wrong At Our Side.")