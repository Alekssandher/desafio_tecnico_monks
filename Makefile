PYTHON = poetry run python
UVICORN = poetry run uvicorn
APP = api.main:app
PORT = 8000
HOST = 127.0.0.1

run:
	$(UVICORN) $(APP) --reload --host $(HOST) --port $(PORT)

seed:
	$(PYTHON) api/seeds/metrics_seed.py
# 	$(PYTHON) apy/seeds/users_seed.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete