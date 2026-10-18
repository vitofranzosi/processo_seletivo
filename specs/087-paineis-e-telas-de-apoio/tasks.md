# Tasks: Os painéis e as telas de apoio da gestão, nono incremento

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[quickstart.md](quickstart.md)

**Tests**: incluídos — a rastreabilidade deste repositório é verificada por teste, e cada requisito
tem linha em [rastreabilidade.md](rastreabilidade.md). Caminhos relativos a `backend/`; os templates
estão em `processo_seletivo/interface/templates/interface/`.

## Phase 1: Setup

- [x] T001 Banco do inventário próprio (`ps_inventario_087`, cópia do `ps_inventario_080`, `migrate --check` limpo), banco de teste próprio (`DB_NAME=ps_087`) e `uv sync --extra dev --extra assistente`. O `.claude/launch.json` não muda: o inventário sobe o próprio servidor, e o percurso usa um `runserver` à mão (quickstart)
- [x] T002 Inventário de antes, nos dois estados da barra, sobre `cf6d7372`, guardado em `depois-da-087/antes/`; comparado com `depois-da-080/` — 0 estouros, nenhum `status` diferente, nenhuma variante com medida diferente

## Phase 2: Foundational

Nenhuma: o bloco `caminho_do_contexto` do cabeçalho existe desde a `077`, e o parcial do produto desde a `078`.

## Phase 3: User Story 1 — onde estou, dito uma vez só (P1) 🎯 MVP

**Goal**: a trilha no cabeçalho nas oito telas.

**Independent Test**: a página tem uma `nav` "Trilha de navegação", no cabeçalho de contexto, e o `main` começa pelo título.

- [x] T003 [P] [US1] `visao_geral.html`, `autoridades.html`: a seção como página atual, no bloco (R-001; FR-1970, FR-1971)
- [x] T004 [P] [US1] `supervisao.html`, `processo_confirmar.html`, `processo_criar.html`: a trilha no bloco, e fora do conteúdo (R-001; FR-1970, FR-1972, FR-1973)
- [x] T005 [P] [US1] `duvidas.html`, `assistente.html`, `confirmar.html`: a trilha do Edital com a tela no fim, e fora do conteúdo (R-001, R-003; FR-1970, FR-1972, FR-1973)
- [x] T006 [US1] Testes em `tests/interface/test_paineis_e_telas_de_apoio.py`: a trilha única no cabeçalho e o conteúdo pelo título nas oito; a barra na mesma seção; o custo zero de consulta, provado por mutação (FR-1970 a FR-1974, FR-1978, SC-772, SC-773)
- [x] T007 [US1] O guardião da `076` que lia o texto do cabeçalho na Visão Geral passa a ler a trilha (R-004)

## Phase 4: User Story 2 — "Perguntar" é a ação principal (P2)

- [x] T008 [US2] `assistente.html`: "Perguntar" como `botao`, com o comentário do porquê (R-002; FR-1976)
- [x] T009 [US2] Testes: um `botao` só no Assistente e nas Respostas; "Começar outra conversa" e "Consultar neste instante" com o desenho de antes; "Confirmar" e "Encerrar a vigência" com o desenho de antes; a conferência com recusa certa sem "Confirmar" (FR-1976, FR-1977)

## Phase 5: User Story 3 — os painéis dizem só o que o banco tem (P1)

- [x] T010 [US3] Testes: os quatro indicadores da Visão Geral e o Pulso da Supervisão, na ordem de antes, sem percentual (FR-1978)

## Phase 6: Polish & verificação

- [x] T011 `make lint check` e `make test-pg DB_NAME=ps_087` (FR-1979, SC-774)
- [x] T012 Inventário refeito com `BARRA=expandida` e `BARRA=recolhida` em `doc/inventario-visual-da-gestao-2026-10-16/depois-da-087/`, comparado por `comparar.py` e por `medidas.py` com o de antes; as capturas das telas do escopo, antes e depois; a seção "Depois da 087" no `doc/inventario-visual-da-gestao-2026-10-16.md` (FR-1975, FR-1979, SC-770, SC-771)
- [x] T013 O percurso do quickstart no navegador, a 1280 e a 375 px, pelo teclado (FR-1975, SC-775)
- [x] T014 A contagem do fechamento por `trilhas_no_cabecalho.py`, refeita depois de trazer a `main`, e a lista no PR (R-005; SC-776)
- [x] T015 `rastreabilidade.md` com cada FR e SC; a linha da `087` no README

## Dependencies

T003 a T005 primeiro; T008 toca o template de T005 depois dele. Os testes de cada fase depois da
mudança dela. T011–T015 depois de tudo; T014 depois do `git merge origin/main`.

## Implementation Strategy

US1 primeiro: é o desenho que a `077` à `080` já provaram, e sozinha fecha o MVP. Depois US2, e US3
por último, que só prova o que não mudou.
