from abc import ABC, abstractmethod
from typing import Optional
from datetime import date
import polars as pl

class MetricsRepository(ABC):
    @abstractmethod
    def get_metrics(self, start_date: Optional[date], end_date: Optional[date], limit: int, offset: int,
                    order_by: Optional[str], descending: bool, user_role: str) -> pl.DataFrame:
        pass

class PolarsMetricsRepository(MetricsRepository):
    def get_metrics(self, start_date: Optional[date], end_date: Optional[date], limit: int, offset: int,
                    order_by: Optional[str], descending: bool, user_role: str) -> pl.DataFrame:
        df = pl.scan_csv("api/data/metrics.csv", try_parse_dates=True, ignore_errors=True)

        if user_role != "admin":
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

        if order_by and order_by in df.schema.keys():
            df = df.sort(order_by, descending=descending)

        return df.slice(offset, limit).collect()