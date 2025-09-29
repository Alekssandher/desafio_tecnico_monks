import os
import mysql.connector
import time
from pathlib import Path

config = {
    "host": os.getenv("DB_URL", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "batatinha22"),
    "database": os.getenv("DB_NAME", "desafio_monks"),
    "allow_local_infile": True
}

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_FILE = str(BASE_DIR / "data" / "metrics.csv")

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

def wait_for_db(max_retries=30, delay=2):
    """Aguarda o banco de dados ficar disponível"""
    retries = 0
    while retries < max_retries:
        try:
            conn = mysql.connector.connect(**config)
            conn.close()
            print("Banco de dados está pronto!")
            return True
        except mysql.connector.Error as e:
            retries += 1
            print(f"Aguardando banco de dados: (tentativa {retries}/{max_retries})")
            time.sleep(delay)
    
    print("Erro: Não foi possível conectar ao banco de dados")
    return False

def run_seed():

    if not os.path.exists(CSV_FILE):
        print(f"Erro: Arquivo CSV não encontrado em {CSV_FILE}")
        return
    
    print(f"Arquivo CSV encontrado: {CSV_FILE}")
    
    if not wait_for_db():
        return
    
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        print("Criando tabela metrics")
        for stmt in CREATE_TABLE_QUERY.split(";"):
            if stmt.strip():
                cursor.execute(stmt)

        print("Importando dados do CSV")
        cursor.execute(LOAD_DATA_QUERY)
        rows_imported = cursor.rowcount
        print(f"{rows_imported} registros importados")


        conn.commit()
        print("\nSeed executado \n")

    except mysql.connector.Error as e:
        print(f"Erro ao executar seed: {e}")
        
    except Exception as e:
        print(f"Erro inesperado: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("\n=== SEED DO BANCO DE DADOS ===\n")
    print(f"Host: {config['host']}")
    print(f"Database: {config['database']}")
    print(f"User: {config['user']}")
    print(f"CSV: {CSV_FILE}\n")
    
    run_seed()