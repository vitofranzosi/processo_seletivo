#!/bin/sh
# Monta do zero o banco da referência: migrations, Unidades, seed_demo e os 17 cenários de
# treinamento. Rode a partir da raiz do repositório. Apaga o banco do nome dado, se existir.
set -e
BANCO=${1:-ps_p0_referencia}
cd backend
export LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=$BANCO \
  DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true SORTEIO_FONTE_DE_DEMONSTRACAO=true \
  CENARIOS_DE_TREINAMENTO=true ARQUIVOS_CANDIDATOS_RAIZ=/private/tmp/claude-501/ps-p0-referencia-arquivos
dropdb --if-exists "$BANCO"; createdb "$BANCO"
uv run python manage.py migrate -v 0
uv run python manage.py semear_unidades
uv run python manage.py seed_demo
uv run python manage.py carregar_cenarios_de_treinamento --banco "$BANCO"
