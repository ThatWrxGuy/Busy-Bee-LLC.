install:
	pip install -e .[dev]

train:
	python scripts/train.py

test:
	pytest --cov=src/busy_bee --cov-report=term-missing

serve:
	uvicorn busy_bee.api.app:create_app --factory --reload --host 0.0.0.0 --port 8000

lint:
	ruff check src tests scripts
