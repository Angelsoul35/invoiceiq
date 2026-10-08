.PHONY: install test lint run demo clean

install:
	pip install -e ".[dev]"

test:
	pytest --cov=invoiceiq --cov-report=term-missing

lint:
	ruff check invoiceiq tests

run:
	uvicorn invoiceiq.main:app --reload --port 8000

demo:
	python -m invoiceiq.cli demo

clean:
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov
