# Quickstart: Andamento da seleção

## Automático

Banco de teste próprio (um por worktree) e o par `TEST_DB_ENGINE` + `DB_USER`:

```bash
cd backend
TEST_DB_ENGINE=postgresql DB_USER=$USER DB_NAME=spec127 uv run pytest \
  tests/unit/interface/test_andamento_situacoes.py \
  tests/unit/interface/test_andamento_composicao.py \
  tests/unit/interface/test_providencias.py \
  tests/interface/test_andamento_do_edital.py \
  tests/interface/test_andamento_coerencia.py \
  tests/performance/test_andamento_em_escala.py -q
```

E a verificação completa, como pede o CLAUDE.md:

```bash
cd backend && make lint check && DB_NAME=spec127 make test-pg
```

## Visual (banco descartável)

O clone do banco do guia, com os Editais 35 e 57 (sorteio), 91 (pontuação), 51 (pontuação com
Etapa governada), 72 (sorteio enumerando Etapa) e 90 (em elaboração):

```bash
docker exec ps-sorteio-35 sh -c 'createdb -U postgres -T processo_seletivo_guia ps_spec127'
cd backend && DB_HOST=localhost DB_PORT=55435 DB_NAME=ps_spec127 DB_USER=postgres \
  DB_PASSWORD=estudo uv run python manage.py migrate
```

Servidor com o seletor de identidade ligado (`INTERFACE_SELETOR_IDENTIDADE=true`) e o mesmo banco;
o roteiro `specs/127-andamento-da-selecao/capturas/capturar.py` entra por papel (gestor,
presidência, publicador, elaborador) e captura o detalhe de cada Edital a 1280 e a 375 px, antes e
depois, com o nível 2 recolhido e aberto. As capturas ficam em `capturas/`.

## O que conferir

| Edital | Papel | Esperado |
|---|---|---|
| 35 | gestor | "1 é sua": emitir a comunicação (Cefor · ampla); quem publica: definitivo; Atenção às duas Etapas; Polo Vitória fora |
| 35 | publicador | o definitivo como seu, com link à prévia |
| 35 | elaborador | providências de outros papéis, sem link; sem "Andamento da seleção" |
| 57 | gestor | duas listas em situações diferentes: uma *Pendente* (congelar), outra *Aguarda* (extração) |
| 91 | presidência | avaliar e distribuir como suas; Entrevista em Atenção; ordem fora das providências |
| 51 | gestor | P2: a Etapa governada depois do corte; Técnico de Laboratório *Não se aplica* |
| 72 | gestor | S2: a decisória não eliminatória enumerada como Atenção |
| 90 | elaborador | o cartão de hoje, com a trilha |

## Roteiro com pessoas (SC-1245)

O roteiro do estudo (`validacao.md`), com as telas implementadas no lugar das maquetes: as cinco
tarefas, os critérios fixados antes, e a repetição das tarefas 1 e 2 no 91. **Inspeção não
substitui teste com pessoas**: os resultados entram em `verificacao.md` quando o usuário conduzir
as sessões.
