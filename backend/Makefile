.PHONY: install check lint test contract

install:
	uv sync --extra dev

check:
	uv run python manage.py check
	uv run python manage.py makemigrations --check --dry-run

lint:
	uv run ruff check .

test:
	uv run pytest

contract:
	uv run pytest -m contract

