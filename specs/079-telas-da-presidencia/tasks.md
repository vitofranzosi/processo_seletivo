# Tasks: As telas da presidência da comissão, terceiro incremento

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[quickstart.md](quickstart.md)

**Tests**: incluídos — a rastreabilidade deste repositório é verificada por teste, e cada requisito
tem linha em [rastreabilidade.md](rastreabilidade.md). Caminhos relativos a `backend/`; os templates
estão em `processo_seletivo/interface/templates/interface/`.

## Phase 1: Setup

- [x] T001 Banco de teste próprio (`DB_NAME=ps_079`), o `ps_inventario_telas` em dia com as migrations, `uv sync --extra dev --extra assistente` e a entrada `telas-079` no `.claude/launch.json` (porta 8081)
- [x] T002 Inventário de antes, nos dois estados da barra, sobre `e781dfb3`, comparado com `depois-da-078/` campo a campo — sem diferença nenhuma; teto da Distribuição no cenário de escala medido antes — 95 144 caracteres (95 610 bytes); a faixa da Distribuição medida no navegador — y ≈ 644 a 1280 px, y ≈ 998 a 375 px

## Phase 2: Foundational

Nenhuma: o bloco `caminho_do_contexto` do cabeçalho existe desde a `077`, e o parcial do produto desde a `078`.

## Phase 3: User Story 1 — onde estou, dito uma vez só (P1) 🎯 MVP

**Goal**: a trilha no cabeçalho nas quatro telas da presidência.

**Independent Test**: a página tem uma `nav` "Trilha de navegação", no cabeçalho de contexto, e o `main` começa pelo título.

- [ ] T003 [P] [US1] `comissao.html` e `comissao_confirmar.html`: a trilha sai do conteúdo e vai ao bloco `caminho_do_contexto`, com o produto pelo parcial (R-001; FR-1780, FR-1781)
- [ ] T004 [P] [US1] `alocacoes.html`: a trilha no bloco; nada mais na moldura da matriz (R-001; FR-1780, FR-1781, FR-1784)
- [ ] T005 [P] [US1] `distribuicao.html`: a trilha no bloco, com a Alocação por Etapa como nível acima da Etapa (R-001; FR-1780, FR-1781)
- [ ] T006 [US1] Testes em `tests/interface/test_telas_da_presidencia.py`: a trilha única no cabeçalho e o conteúdo pelo título nas quatro telas, a conferência da inclusão e a da lista; a Alocação com a barra no topo; as filhas da Distribuição com o cabeçalho da `076` (FR-1780, FR-1781, FR-1782, FR-1784, SC-692)

## Phase 4: User Story 2 — os lugares da Etapa logo abaixo do título (P1)

**Goal**: a faixa da Distribuição antes da ficha.

**Independent Test**: a faixa vem depois do título e das mensagens do último envio, antes da ficha, com os mesmos quatro links; as ações não se movem.

- [ ] T007 [US2] `distribuicao.html`: o `p.acoes-do-painel` com Impedimentos, Registrar ocorrência, Resultados e Trilha logo depois do resultado do lote, antes da ficha, com o comentário dele (R-002; FR-1785, FR-1786)
- [ ] T008 [US2] Testes em `tests/interface/test_telas_da_presidencia.py`: a faixa antes da ficha e depois do resultado; os mesmos links na mesma ordem; a ordem relativa das ações e das frases que as precedem igual à de antes (FR-1785, FR-1786)

## Phase 5: User Story 3 — a Comissão com título para quem está nela (P2)

**Goal**: a seção dos membros e o estado vazio da Comissão.

**Independent Test**: "Membros (N)" com o filtro e a lista; sem membro, sem filtro e com o link para a inclusão.

- [ ] T009 [US3] `comissao.html`: a `section` com `h2` "Membros (N)" envolvendo o filtro, a linha do recorte e a lista; sem membro, sem filtro, com o estado vazio que leva a `#adicionar-titulo` (R-003; FR-1787, FR-1788)
- [ ] T010 [US3] Testes em `tests/interface/test_telas_da_presidencia.py`: o título com o total, inclusive filtrado; a comissão vazia sem filtro e com o link; o recorte vazio com o filtro; a conferência sem mudança de conteúdo (FR-1787, FR-1788, FR-1789)

## Phase 6: User Story 4 — a ação principal da Alocação diz o que faz (P3)

**Goal**: "Salvar alocação".

**Independent Test**: com presidência e membros, o botão diz "Salvar alocação"; sem presidência, não há botão.

- [ ] T011 [US4] `alocacoes.html`: "Salvar alocação"; `doc/manual/00-arquitetura-do-manual.md` (C-13) com o rótulo atual (R-004; FR-1790)
- [ ] T012 [US4] Testes em `tests/interface/test_telas_da_presidencia.py`: o rótulo com presidência e a ausência sem ela (FR-1790)

## Phase 7: Polish & verificação

- [ ] T013 `make lint check` e `make test-pg DB_NAME=ps_079`; o teto da Distribuição medido de novo (FR-1792, SC-694, SC-695)
- [ ] T014 Inventário refeito com `BARRA=expandida` e `BARRA=recolhida` em `doc/inventario-visual-da-gestao-2026-10-16/depois-da-079/`, comparado por `comparar.py` e por `medidas.py` (novo, na pasta do inventário) com `depois-da-078/`; as capturas das telas que mudaram; a seção "Depois da 079" no `doc/inventario-visual-da-gestao-2026-10-16.md` (FR-1783, FR-1784, FR-1791, SC-690, SC-691, SC-693)
- [ ] T015 O percurso do quickstart no navegador, a 1280 e a 375 px, só pelo teclado (FR-1783, SC-696)
- [ ] T016 `rastreabilidade.md` com cada FR e SC; a `FR-1769` da `078` anotada como emendada, na spec e na rastreabilidade dela; a linha da `079` no README, se a tabela de incrementos a cobrar

## Dependencies

US1 toca os quatro templates; US2 e US3 tocam `distribuicao.html` e `comissao.html` depois dela
(T005 → T007; T003 → T009); US4 toca `alocacoes.html` depois de T004. T013–T016 depois de tudo.

## Parallel Example

T003, T004 e T005 são arquivos diferentes e podem ir juntos; depois, T007, T009 e T011, também em
arquivos diferentes.

## Implementation Strategy

US1 primeiro: é o desenho que a `077` e a `078` já provaram, e sozinha já fecha o MVP. Depois US2 e
US3, e US4 por último. Cada fase termina com os testes dela passando.
