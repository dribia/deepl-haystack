PROJECT:= deepl_haystack
TESTS:= tests

.PHONY: check test codestyle docstyle lint pip

check: format lint

format:
	poetry run ruff format $(PROJECT) tests
	poetry run ruff check --fix --unsafe-fixes $(PROJECT) $(TESTS)

lint:
	poetry run ruff format --check $(PROJECT) $(TESTS)
	poetry run ruff check $(PROJECT) $(TESTS)
	poetry run mypy $(PROJECT)

lock:
	poetry lock --no-update

test:
	poetry run pytest

test-cov:
	poetry run pytest --cov --cov-report=html --cov-report=xml
