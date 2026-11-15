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
# **De onde vem o dump da referência.** Ele não mora no repositório, e não há caminho padrão: diga-o
# em `REFERENCIA_DUMP`. Para regerá-lo a partir do zero, de `backend/`:
#
#   sh ../doc/auditoria-design-system-2026-11-14/referencia-p0/scripts/montar_banco.sh ps_p0_referencia
#   pg_dump -Fc -f <arquivo>.dump ps_p0_referencia
#
# O primeiro passo monta o banco com `seed_demo` e os 17 cenários de treinamento, e o README da
# `referencia-p0/` explica por que os prazos dependem do dia em que ele roda.
#
# Rode de `backend/` da branch do piloto, com `LC_ALL` exportado (macOS com PostgreSQL do Homebrew).
set -e
BANCO=${1:?referencia, lista, v3, v4, v5 ou v6}
DUMPS=${2:-}
ALVO=ps_piloto_validacao

if [ "$BANCO" = referencia ]; then
  ORIGEM="${REFERENCIA_DUMP:?o caminho do dump da referência (ver o cabeçalho deste roteiro)}"
else
  ORIGEM="${DUMPS:?a pasta dos dumps da jornada}/$BANCO.dump"
fi
[ -f "$ORIGEM" ] || { echo "não achei $ORIGEM" >&2; exit 1; }

dropdb --if-exists "$ALVO"
createdb "$ALVO"
# A restauração que falha derruba o roteiro: um `|| true` aqui anunciava "pronto" num banco vazio.
# Com `--no-owner --no-privileges`, os dumps da referência e das tarefas restauram sem aviso nenhum
# (conferido em 15/11), e não há aviso esperado a filtrar.
pg_restore --no-owner --no-privileges --exit-on-error -d "$ALVO" "$ORIGEM"
DB_NAME=$ALVO DB_USER=$USER DB_RUNTIME_USER=$USER DJANGO_SETTINGS_MODULE=config.settings.development \
  uv run python manage.py migrate --no-input >/dev/null
EDITAIS=$(psql -At -d "$ALVO" -c "select count(*) from processos_edital")
[ "$EDITAIS" -gt 0 ] || { echo "o banco $ALVO restaurou sem Edital nenhum: $ORIGEM é o dump certo?" >&2; exit 1; }
echo "Banco $ALVO pronto, com $EDITAIS Editais, a partir de $ORIGEM."

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
