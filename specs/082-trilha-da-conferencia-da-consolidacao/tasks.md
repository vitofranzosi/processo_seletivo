# Tasks: A trilha da conferência da consolidação no cabeçalho de contexto

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[quickstart.md](quickstart.md)

**Tests**: incluídos — a rastreabilidade deste repositório é verificada por teste, e cada requisito
tem linha em [rastreabilidade.md](rastreabilidade.md). Caminhos relativos a `backend/`; o template está
em `processo_seletivo/interface/templates/interface/`.

## Phase 1: Setup

- [x] T001 Banco de demonstração próprio (`ps_inventario_082`, cópia do `ps_inventario_081`, `migrate --check` limpo), banco de teste próprio (`DB_NAME=ps_082`) e `uv sync --extra dev --extra assistente`

## Phase 2: Foundational

Nenhuma: o bloco `caminho_do_contexto` existe desde a `077`, e o parcial do produto desde a `078`.

## Phase 3: User Story 1 — onde estou, dito uma vez só, também antes de consolidar (P1) 🎯 MVP

**Goal**: a trilha da Distribuição com "Conferir" no fim, no cabeçalho da conferência.

**Independent Test**: a página tem uma `nav` "Trilha de navegação", no cabeçalho de contexto, e o `main` começa pelo título, pelos dois caminhos.

- [x] T002 [US1] `consolidacao_confirmar.html`: a trilha no bloco `caminho_do_contexto`, e a `nav.trilha` fora do conteúdo (R-001; FR-1840, FR-1841, FR-1842)
- [x] T003 [US1] Testes em `tests/interface/test_trilha_da_conferencia_da_consolidacao.py`, com cenário próprio: a trilha pela seleção e por todas as prontas; o alcance, o que fica de fora e o botão de perigo iguais, e nada consolidado; a abertura da trilha (R-002; FR-1840 a FR-1844, SC-720, SC-721) — conferidos contra o template de antes: os de trilha reprovam, os de "não muda" passam
- [x] T004 [US1] `FR-1803` da `080` anotada como emendada, na spec e na matriz

## Phase 4: Polish

- [x] T005 Percurso do quickstart no navegador, a 1280 e a 375 px, pelo teclado (FR-1845, SC-722)
- [x] T006 A linha da `082` no `README.md`
- [x] T007 `make lint check test-pg` com `DB_NAME=ps_082` (SC-723)
