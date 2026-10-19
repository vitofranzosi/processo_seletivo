# Tasks: A limpeza dos achados da etapa 4

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[quickstart.md](quickstart.md)

**Tests**: incluídos — a rastreabilidade deste repositório é verificada por teste, e cada requisito
tem linha em [rastreabilidade.md](rastreabilidade.md). Caminhos relativos a `backend/`; os templates
estão em `processo_seletivo/interface/templates/interface/`.

## Phase 1: Setup

- [x] T001 Conferir que o PR 306 (`089`) está na `main` e trazê-la (`git merge origin/main`); `uv sync --extra dev --extra assistente`; banco de teste `DB_NAME=ps_090`
- [x] T002 Banco do inventário próprio (`ps_inventario_090`, cópia do `ps_inventario_089`, `migrate --check` limpo)
- [x] T003 A variante `aviso-do-resultado-pelo-marco` em `capturar.py`; inventário de antes, nos dois estados da barra, em `depois-da-090/antes/`
- [x] T004 Medir as consultas de Resultados, Trilha da avaliação e Conclusões preservadas, com quem preside e quem só audita, e da prévia pelas duas portas, antes da mudança

## Phase 2: Foundational

Nenhuma.

## Phase 3: User Story 1 — o ato sem volta é anunciado (P1) 🎯 MVP

**Independent Test**: todo ato irreversível dos três detalhes tem a marca como descrição; nenhum outro tem.

- [x] T005 [US1] `processo_detalhe.html`, `_acao_do_edital.html`, `retificacao_detalhe.html`: `id` na marca, `aria-describedby` no link (R-001; FR-2060, FR-2061)
- [x] T006 [US1] Testes: nos três detalhes, cada marca descreve o link que a precede, só os irreversíveis têm descrição, o ato indisponível continua com o motivo (FR-2060, FR-2061, SC-801)

## Phase 4: User Story 2 — a trilha não oferece porta fechada (P1)

**Independent Test**: com quem preside, links; com quem só audita, texto; nenhum link da trilha recusa quem a lê; consultas iguais.

- [x] T007 [US2] `views.py`: `_etapa_para_auditar` devolve `pode_gerir_a_comissao`, calculado uma vez; as três views o entregam (R-002; FR-2064)
- [x] T008 [US2] `resultados.html`, `conclusoes.html`, `auditoria.html`: Alocação e Etapa condicionais (R-002; FR-2062)
- [x] T009 [US2] Testes: presidência, gestão sistêmica e auditoria nas três telas; todo link da trilha seguido pela mesma pessoa responde 200; consultas iguais às do T004 (FR-2062, FR-2063, FR-2064, SC-802)
- [x] T010 [US2] `FR-1800` e `FR-1804` da `080` anotadas como emendadas; a decisão 003 da `080`, como substituída (FR-2072)

## Phase 5: User Story 3 — o rodapé quebra a linha (P2)

- [x] T011 [US3] `gestao.css`: `flex-wrap:wrap` em `.salvar` (R-003; FR-2065)
- [x] T012 [US3] Teste: a regra comum do rodapé quebra a linha, lida pela folha aplicada (FR-2065); a prova de medida é o inventário (FR-2066, SC-803)

## Phase 6: User Story 4 — a prévia volta para onde se veio (P2)

- [x] T013 [US4] `publicacoes_do_marco.html`: `de=marco` no link (R-004; FR-2067)
- [x] T014 [US4] `avisos.py`: `voltar`, `de` e `pode_ver_a_classificacao` com a porta dos Resultados divulgados; porta ignorada para quem não a abre (R-004; FR-2067, FR-2068)
- [x] T015 [US4] `aviso_previa.html`: `de` nos dois formulários; o ramo da trilha (R-004; FR-2067, FR-2068)
- [x] T016 [US4] Testes: a trilha e "Cancelar" pelas duas portas; a porta depois de "Usar este modelo" e da recusa do envio; porta desconhecida e porta que quem lê não abre; o aviso confirmado igual; consultas (FR-2067, FR-2068, FR-2069, SC-804)
- [x] T017 [US4] `FR-1942` e `FR-1946` da `086` anotadas como emendadas (FR-2072)

## Phase 7: Polish

- [x] T018 Inventário de depois, nos dois estados da barra, em `depois-da-090/`; `comparar.py` e `medidas.py` contra `depois-da-090/antes/` (FR-2070, SC-805)
- [x] T019 Percurso do quickstart no navegador, a 1280 e a 375 px, com quem preside e com quem só audita
- [x] T020 O inventário em `doc/` e a linha do README
- [ ] T021 `make lint check test-pg DB_NAME=ps_090 POSTGRES_USER=$USER` (FR-2071, SC-806)
- [x] T022 `/code-review` no PR; corrigir os achados confirmados
