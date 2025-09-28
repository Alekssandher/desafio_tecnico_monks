from abc import ABC, abstractmethod
from typing import Optional
import polars as pl

class UserCsvRepository(ABC):
    @abstractmethod
    def get_user(self, email: str) -> Optional[dict]:
        pass

class PolarsUserCsvRepository(UserCsvRepository):
    def get_user(self, email: str) -> Optional[dict]:
        df = pl.scan_csv("api/data/users.csv")
        result = df.filter(pl.col("email") == email).collect()
        return result.to_dicts()[0] if not result.is_empty() else None