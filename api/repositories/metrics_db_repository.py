
from abc import ABC, abstractmethod
from typing import Dict, List

import mysql.connector

from api.dtos.metricFilterParams import MetricsFilterParams


class MetricsDbRepository(ABC):
    @abstractmethod
    def get_metrics(self, filters: MetricsFilterParams, user_role: str) -> List[Dict]:
        pass

class MySQLMetricsDbRepository(MetricsDbRepository):
    def __init__(self, db_config):
        self.db_config = db_config

    def get_metrics(self, filters: MetricsFilterParams, user_role: str) -> List[Dict]:
        
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor(dictionary=True)

        try:
            columns = ["date", "account_id", "campaign_id", "clicks", "conversions", "impressions", "interactions"]
            if user_role == "admin":
                columns.append("cost_micros")

            query = f"SELECT {', '.join(columns)} FROM metrics WHERE 1=1"
            params = []

            if filters.start_date:
                query += " AND date >= %s"
                params.append(filters.start_date)
            if filters.end_date:
                query += " AND date <= %s"
                params.append(filters.end_date)

            if filters.order_by and filters.order_by in columns:
                direction = "DESC" if filters.descending else "ASC"
                query += f" ORDER BY {filters.order_by} {direction}"

            query += " LIMIT %s OFFSET %s"
            params.extend([filters.limit, filters.offset])

            cursor.execute(query, params)
            results = cursor.fetchall()

            return results

        finally:
            cursor.close()
            conn.close()