# Tasks: As telas filhas da Distribuição e a auditoria da comissão, quarto incremento

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[quickstart.md](quickstart.md)

**Tests**: incluídos — a rastreabilidade deste repositório é verificada por teste, e cada requisito
tem linha em [rastreabilidade.md](rastreabilidade.md). Caminhos relativos a `backend/`; os templates
estão em `processo_seletivo/interface/templates/interface/`.

## Phase 1: Setup

- [x] T001 Banco do inventário próprio (`ps_inventario_080`, cópia do `ps_inventario_telas`, `migrate --check` limpo), banco de teste próprio (`DB_NAME=ps_080`), `uv sync --extra dev --extra assistente` e a entrada `telas-080` no `.claude/launch.json` (porta 8082)
- [x] T002 Inventário de antes, nos dois estados da barra, sobre `fbe5bba3`, guardado em `depois-da-080/antes/`; comparado com `depois-da-079/` — 0 estouros, nenhum `status` diferente, e só `auditoria-comissao` e `aviso` com altura diferente, por dado (R-006 da pesquisa, achados)

## Phase 2: Foundational

Nenhuma: o bloco `caminho_do_contexto` do cabeçalho existe desde a `077`, e o parcial do produto desde a `078`.

## Phase 3: User Story 1 — onde estou, dito uma vez só (P1) 🎯 MVP

**Goal**: a trilha no cabeçalho nas sete telas.

**Independent Test**: a página tem uma `nav` "Trilha de navegação", no cabeçalho de contexto, e o `main` começa pelo título.

- [x] T003 [P] [US1] `impedimentos.html`, `ocorrencia.html`, `resultados.html`, `conclusoes.html`, `distribuicao_remover_confirmar.html`: a trilha da Distribuição com a tela no fim, no bloco `caminho_do_contexto` (R-001; FR-1800, FR-1801, FR-1802)
- [x] T004 [P] [US1] `auditoria.html`: a trilha da avaliação e a da comissão no bloco; a do Edital com o `block.super` e a trilha no conteúdo (R-002; FR-1800, FR-1801, FR-1802, FR-1803)
- [x] T005 [US1] Testes em `tests/interface/test_telas_filhas_da_distribuicao.py`: a trilha única no cabeçalho e o conteúdo pelo título nas cinco filhas por endereço, na conferência da retirada e na Auditoria da comissão; a Auditoria do Edital com o cabeçalho da `076`; a mesma trilha para presidência e auditoria (FR-1800 a FR-1804, SC-702, SC-703)
- [x] T006 [US1] Os guardiões da `077` e da `079` que fixavam as filhas com o cabeçalho da `076`: o da `079` sai, com um comentário que aponta para o arquivo novo; o da `077` passa à Auditoria do Edital (R-006)

## Phase 4: User Story 2 — o que acabou de acontecer (P2)

**Goal**: as mensagens do último envio logo abaixo do título.

**Independent Test**: em Registrar ocorrência e nas Conclusões, o erro e o resultado antes da ajuda; o erro do filtro no filtro.

- [x] T007 [P] [US2] `ocorrencia.html` e `conclusoes.html`: o erro e o resultado logo depois do `p.sub`, com o comentário do porquê (R-003; FR-1806)
- [x] T008 [US2] Testes: o erro da ocorrência antes de "Não há desfazer." e esta antes do formulário; a resposta da reabertura antes da ajuda e do filtro; o erro do filtro dentro do filtro (FR-1806)

## Phase 5: User Story 3 — Impedimentos com título para o que se faz (P2)

- [x] T009 [US3] `impedimentos.html`: a `section` com `h2` "Registrar um impedimento" em volta do formulário (R-004; FR-1807)
- [x] T010 [US3] Teste: a seção com os três campos e o botão, antes das avaliações fora do conjunto (FR-1807)

## Phase 6: User Story 4 — "Filtrar" é a ação principal das consultas (P3)

- [x] T011 [US4] `auditoria.html` e `conclusoes.html`: "Filtrar" como `botao` (R-005; FR-1808)
- [x] T012 [US4] Testes: "Filtrar" com o desenho de ação principal nas três consultas; as ações que não se desfazem com o desenho de antes, uma vez cada (FR-1808, FR-1809)

## Phase 7: Polish & verificação

- [x] T013 `make lint check` e `make test-pg DB_NAME=ps_080` (FR-1811, SC-704) — 11 648 passando e 11 pulados, nenhuma falha, em 513s com 4 workers
- [x] T014 Inventário refeito com `BARRA=expandida` e `BARRA=recolhida` em `doc/inventario-visual-da-gestao-2026-10-16/depois-da-080/`, comparado por `comparar.py`, por `medidas.py` e pixel a pixel com o de antes; as capturas das seis telas do escopo, antes e depois; a seção "Depois da 080" no `doc/inventario-visual-da-gestao-2026-10-16.md` (FR-1805, FR-1810, SC-700, SC-701)
- [x] T015 O percurso do quickstart no navegador, a 1280 e a 375 px, pelo teclado (FR-1805, SC-705)
- [x] T016 `rastreabilidade.md` com cada FR e SC; a `FR-1748` da `077`, a `FR-1769` da `078` e a `FR-1782` da `079` anotadas como emendadas, na spec e na rastreabilidade de cada uma; a linha da `080` no README

## Dependencies

T003 e T004 primeiro; T007, T009 e T011 tocam os mesmos templates depois deles. Os testes de cada
fase depois da mudança dela. T013–T016 depois de tudo.

## Implementation Strategy

US1 primeiro: é o desenho que a `077`, a `078` e a `079` já provaram, e sozinha fecha o MVP. Depois
US2 e US3, e US4 por último. Cada fase termina com os testes dela passando.
