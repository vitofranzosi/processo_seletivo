# Quickstart: validar a tela do sorteio (142)

## Banco descartável

```bash
cd backend
createdb ps142_dev
make preparar DB_NAME=ps142_dev POSTGRES_DB=ps142_dev
# a autoridade da suíte, para os cenários assinarem
DB_NAME=ps142_dev DB_USER=$USER DB_RUNTIME_USER=$USER uv run python manage.py shell -c \
  "import sys; sys.path.insert(0, '.'); from tests.fixtures.autoridades import garantir_o_cefor; garantir_o_cefor()"
for c in C06 C07; do
  CENARIOS_DE_TREINAMENTO=true SORTEIO_FONTE_DE_DEMONSTRACAO=true ARQUIVOS_CANDIDATOS_RAIZ=/tmp/ps142-arquivos \
  DB_NAME=ps142_dev DB_USER=$USER DB_RUNTIME_USER=$USER \
  uv run python manage.py carregar_cenarios_de_treinamento --cenario $c --banco ps142_dev \
    --autoridade 00000000-0000-0000-0000-000000000601
done
createdb -T ps142_dev ps142_base   # a cópia limpa: os atos são irreversíveis
```

O servidor é a entrada `jornada-do-sorteio-142` do `.claude/launch.json` (porta 8142).

## As capturas

```bash
cd backend && uv run python ../specs/142-jornada-do-sorteio/capturas/capturar.py depois
```

Antes de cada rodada: parar o servidor, `dropdb ps142_dev && createdb -T ps142_base ps142_dev`, subir
de novo. O roteiro pratica, na ordem: C07 (as duas fixadas, sem semente); C06 nada fixado → a ampla
→ a PPP → a semente → o sorteio da ampla → o da PPP; o Centro; a auditoria; a rodada 2 do C06 com a
semente antes da PPP e o sorteio recusado; e a 375 px.

## O que conferir

1. Os quatro passos no alto, com a tarefa de agora marcada (SC-1540).
2. A situação de cada lista igual à do Centro (SC-1541).
3. Os mesmos formulários antes e depois em cada estado (SC-1542).
4. A ordem sorteada com 10 e 3 posições, e nenhuma frase de divulgação (SC-1543, SC-1544).
5. Sem rolagem horizontal a 375 px e sem violação de CSP (SC-1545).
6. Sem "Nenhum corte emitido" antes do sorteio (SC-1546).
