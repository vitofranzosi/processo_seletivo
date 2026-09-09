# O `.env` não é carregado por ninguém em execução nativa: o projeto não usa `python-dotenv`, e
# `manage.py` lê só o que estiver exportado no ambiente. Era por isso que a instrução "copie o
# `.env.example` e ajuste" não tinha efeito nenhum — o arquivo era escrito e nunca lido. Os alvos
# abaixo o carregam; um `manage.py` chamado à mão fora do `make` continua sem enxergá-lo.
# Dentro do container as variáveis já chegam prontas pelo `env_file` do compose, e três delas são
# deliberadamente diferentes das do arquivo: o banco atende em `db`, não em `localhost`. Como
# `include` **sobrepõe** variável de ambiente, carregar o `.env` aqui desfaria exatamente essas
# três — e a suíte rodada de dentro do container tentaria conectar no host errado. Daí a guarda.
ifndef EM_CONTAINER
ifneq (,$(wildcard .env))
include .env
export
endif
endif

.PHONY: install check lint test test-pg contract preparar provisionar migrate runserver seed

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

# A suíte de verdade. O alvo `test` acima cai para SQLite, e nesse modo 182 casos são pulados e 21
# falham — ver `doc/achado-suite-em-sqlite.md`. Aqui ela roda contra o PostgreSQL, conectando com o
# superusuário porque criar o banco de teste é privilégio que a role de runtime não tem.
# `DB_RUNTIME_USER` é o que precisa ser sobrescrito, e não `DB_USER`: as settings preferem o
# primeiro, e mexer só no segundo não muda conexão nenhuma.
test-pg:
	TEST_DB_ENGINE=postgresql \
	DB_RUNTIME_USER='$(POSTGRES_USER)' DB_RUNTIME_PASSWORD='$(POSTGRES_PASSWORD)' \
	uv run pytest

contract:
	uv run pytest -m contract

# Preparação do banco na execução nativa. A ordem — provisionar, migrar, provisionar de novo — é a
# que `provisionar_papeis` documenta: papel e privilégio padrão antes de qualquer tabela, e
# privilégio sobre tabela só depois que ela existe. Todos os três são idempotentes.
#
# `provisionar` precisa de um papel que possa criar papéis. `DB_RUNTIME_USER` é sobrescrito na
# linha de comando para que a **conexão** use o superusuário enquanto os papéis criados continuam
# sendo os do `.env`.
# Sub-make em cada linha, e não `preparar: provisionar migrate provisionar`, porque o make executa
# cada alvo **uma vez por invocação**: a segunda passada — a que tranca as tabelas — seria
# silenciosamente descartada como já satisfeita, e o banco subiria com metade da imutabilidade.
preparar:
	$(MAKE) provisionar
	$(MAKE) migrate
	$(MAKE) provisionar

provisionar:
	DB_ROLE=runtime DB_RUNTIME_USER='$(POSTGRES_USER)' DB_RUNTIME_PASSWORD='$(POSTGRES_PASSWORD)' \
	uv run python manage.py provisionar_papeis \
		--migration-role '$(DB_MIGRATION_USER)' --migration-password '$(DB_MIGRATION_PASSWORD)' \
		--runtime-role '$(DB_RUNTIME_USER)' --runtime-password '$(DB_RUNTIME_PASSWORD)'

migrate:
	DB_ROLE=migration uv run python manage.py migrate

runserver:
	uv run python manage.py runserver

seed:
	uv run python manage.py seed_demo
