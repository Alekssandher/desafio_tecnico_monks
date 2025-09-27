import os
import mysql.connector

config = {
    "host": "localhost",
    "user": "root",
    "password": "batatinha22",
    "database": "desafio_monks",
    "allow_local_infile": True  
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CSV_FILE = os.path.join(BASE_DIR, "data", "metrics.csv")

CREATE_TABLE_QUERY = """
DROP TABLE IF EXISTS metrics;
CREATE TABLE metrics (
    date DATE,
    account_id BIGINT,
    campaign_id BIGINT,
    clicks FLOAT,
    conversions FLOAT,
    impressions FLOAT,
    interactions FLOAT,
    cost_micros BIGINT
);
"""

LOAD_DATA_QUERY = f"""
LOAD DATA LOCAL INFILE '{CSV_FILE}'
INTO TABLE metrics
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(account_id, campaign_id, cost_micros, clicks, conversions, impressions, interactions, @date)
SET date = STR_TO_DATE(@date, '%Y-%m-%d');
"""

CREATE_INDEXES = f"""
CREATE INDEX idx_date ON metrics(date);
CREATE INDEX idx_campaign_id ON metrics(campaign_id);
"""

def run_seed():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    try:
        print("Criando tabela metrics")
        for stmt in CREATE_TABLE_QUERY.split(";"):
            if stmt.strip():
                cursor.execute(stmt)

        print("Importando CSV")
        cursor.execute(LOAD_DATA_QUERY)

      

        conn.commit()
        print("Feito")

    except Exception as e:
        print("Erro ao rodar seed:", e)

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    run_seed()