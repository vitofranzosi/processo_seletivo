.PHONY: install check lint test contract

install:
	uv sync --extra dev

check:
	uv run python manage.py check
	uv run python manage.py makemigrations --check --dry-run

# Os **dois** passos que o CI roda, e nessa ordem. Rodar só `ruff check` declarava verde local e
# quebrava no CI mesmo assim — foi o que aconteceu com a leva da `015`, que passou por quatro
# checkpoints "verdes" e morreu no primeiro passo do pipeline, antes de o pytest sequer rodar
# (015, T123).
lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run pytest

contract:
	uv run pytest -m contract

