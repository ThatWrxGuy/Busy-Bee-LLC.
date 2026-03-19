.PHONY: install test run audit

install:
	pip install -e .[dev]

test:
	pytest

run:
	uvicorn app.api.main:app --reload

audit:
	python scripts/audit/governance_audit.py
