from fastapi import Query, Depends
from typing import Optional
from pydantic import BaseModel
from datetime import date

class MetricsFilterParams(BaseModel):
    start_date: Optional[date] = Query(None, description="Data inicial")
    end_date: Optional[date] = Query(None, description="Data final")
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros")
    offset: int = Query(0, ge=0, description="Deslocamento para paginação")
    order_by: Optional[str] = Query(None, description="Coluna para ordenação")
    descending: bool = Query(False, description="True para ordem decrescente")

def get_metrics_filters(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    order_by: Optional[str] = Query(None),
    descending: bool = Query(False)
) -> MetricsFilterParams:
    return MetricsFilterParams(
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
        order_by=order_by,
        descending=descending
    )