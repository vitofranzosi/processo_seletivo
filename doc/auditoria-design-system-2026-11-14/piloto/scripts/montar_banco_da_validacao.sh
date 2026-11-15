#!/bin/sh
# Prepara o banco e as duas versões para a validação com a equipe e para o rastreio (172, US4 e US5).
#
#   sh montar_banco_da_validacao.sh <banco> [pasta-dos-dumps]
#
# <banco> é `referencia` (a cópia da referência da P0, migrada) ou uma tarefa da validação
# (`lista`, `v3`, `v4`, `v5`, `v6`), cujo dump sai da jornada
# `tests/navegador/test_banco_da_validacao_do_piloto.py` (PILOTO_DS_BANCO=<pasta-dos-dumps>).
#
# O banco restaurado é sempre `ps_piloto_validacao`, e as duas entradas do `.claude/launch.json` —
# `piloto-antiga` (8172, a `main`) e `piloto-nova` (8173, a branch do piloto) — servem o mesmo: as
# tarefas não confirmam ato, e a sessão é a única coisa que se grava. Uma tarefa por vez; trocar de
# tarefa é rodar de novo e reiniciar os dois servidores.
#
# **O `ps_p0_referencia` não é tocado.** Ele ficou para trás das migrations que entraram depois da
# P0 (a 167, a 168 e a 170), e migrá-lo mudaria a referência. A cópia é que se migra.
#
# A versão antiga roda de uma worktree destacada da `main`, `piloto-172-antiga`, ao lado das outras
# em `.claude/worktrees/`. Este roteiro a cria, ou a leva à `main` de agora se ela já existe.
#
# Rode de `backend/` da branch do piloto, com `LC_ALL` exportado (macOS com PostgreSQL do Homebrew).
set -e
BANCO=${1:?referencia, lista, v3, v4, v5 ou v6}
DUMPS=${2:-}
NOTAS="$HOME/Library/Application Support/Claude/side-session-notes/local_5a9cc322-5ca4-4c5c-b88b-c997a960b0b8"
ALVO=ps_piloto_validacao

if [ "$BANCO" = referencia ]; then
  ORIGEM="${REFERENCIA_DUMP:-$NOTAS/ps_p0_referencia.dump}"
else
  ORIGEM="${DUMPS:?a pasta dos dumps da jornada}/$BANCO.dump"
fi
[ -f "$ORIGEM" ] || { echo "não achei $ORIGEM" >&2; exit 1; }

dropdb --if-exists "$ALVO"
createdb "$ALVO"
pg_restore --no-owner --no-privileges -d "$ALVO" "$ORIGEM" || true
DB_NAME=$ALVO DB_USER=$USER DB_RUNTIME_USER=$USER DJANGO_SETTINGS_MODULE=config.settings.development \
  uv run python manage.py migrate --no-input >/dev/null
echo "Banco $ALVO pronto, a partir de $ORIGEM."

RAIZ=$(cd "$(git rev-parse --git-common-dir)/.." && pwd)
ANTIGA="$RAIZ/.claude/worktrees/piloto-172-antiga"
git fetch -q origin main
if [ -d "$ANTIGA" ]; then
  git -C "$ANTIGA" checkout -q --detach origin/main
else
  git worktree add -q --detach "$ANTIGA" origin/main
fi
echo "Versão antiga em $ANTIGA, na main $(git -C "$ANTIGA" rev-parse --short HEAD)."
echo "Suba piloto-antiga (8172) e piloto-nova (8173)."
