# Tasks: As telas de resultado e dos atos depois da inscrição

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[quickstart.md](quickstart.md)

**Tests**: incluídos — a rastreabilidade deste repositório é verificada por teste, e cada requisito
tem linha em [rastreabilidade.md](rastreabilidade.md). Caminhos relativos a `backend/`; os templates
estão em `processo_seletivo/interface/templates/interface/`.

## Phase 1: Setup

- [x] T001 Banco do inventário próprio (`ps_inventario_084`, cópia do `ps_inventario_telas`, `migrate --check` limpo), banco de teste próprio (`DB_NAME=ps_084`) e `uv sync --extra dev --extra assistente`; nenhuma entrada nova no `.claude/launch.json` — o servidor sobe com as variáveis na linha de comando
- [x] T002 Inventário de antes, nos dois estados da barra, sobre `cf6d7372`, guardado em `depois-da-084/antes/`; comparado com `depois-da-080/` — nenhuma variante diferente

## Phase 2: Foundational

Nenhuma: o bloco `caminho_do_contexto` do cabeçalho existe desde a `077`, e o parcial do produto desde a `078`.

## Phase 3: User Story 1 — onde estou, dito uma vez só (P1) 🎯 MVP

**Goal**: a trilha no cabeçalho nas onze telas.

**Independent Test**: a página tem uma `nav` "Trilha de navegação", no cabeçalho de contexto, e o `main` começa pelo título.

- [x] T003 [P] [US1] `ordenacao.html`, `sorteio.html`, `corte.html`, `ocupacao.html`, `convocacao.html`, `matriculas.html`: a trilha do Edital com a tela no fim, no bloco `caminho_do_contexto` (R-001; FR-1880, FR-1881, FR-1882)
- [x] T004 [P] [US1] `ordenacao_confirmar.html`, `ato_ordenacao.html`, `corte_historico.html`, `ocupacao_historico.html`, `convocacao_historico.html`: o mesmo, com os níveis que cada uma tinha depois do Edital — o recorte da conferência e o da Convocação preservados; o Edital, que faltava, no Ato (R-001; FR-1880, FR-1881, FR-1882)
- [x] T005 [US1] Testes em `tests/interface/test_telas_de_resultado_e_atos.py`: o bloco nas onze, pela fonte; a trilha única no cabeçalho e o conteúdo pelo título nas telas renderizadas, na conferência pelo POST, no Ato pelo link da Classificação; a mesma trilha para gestão, auditoria e exportação (FR-1880 a FR-1883, SC-742, SC-743)

## Phase 4: User Story 2 — o ato continua com o peso que tinha (P1)

**Goal**: nenhum botão, mensagem ou texto muda.

**Independent Test**: os botões de envio das onze telas, na ordem, com o rótulo e o desenho de antes.

- [x] T006 [US2] Testes: os 24 botões de envio congelados por tela; a contagem de desenhos (20 de ação principal, 2 de perigo, 2 secundários) (FR-1886, D-004)
- [x] T007 [US2] Conferido pelo diff que nenhuma linha fora da trilha mudou nos onze templates (FR-1885, FR-1887)

## Phase 5: Polish & verificação

- [x] T008 `make lint check` e `make test-pg DB_NAME=ps_084` (FR-1889, SC-744)
- [x] T009 Inventário refeito com `BARRA=expandida` e `BARRA=recolhida` em `doc/inventario-visual-da-gestao-2026-10-16/depois-da-084/`, comparado por `comparar.py`, por `medidas.py` e pixel a pixel com o de antes; as capturas das dez telas do escopo, antes e depois; a seção "Depois da 084" no `doc/inventario-visual-da-gestao-2026-10-16.md` (FR-1884, FR-1888, SC-740, SC-741)
- [x] T010 O percurso do quickstart no navegador, a 1280 e a 375 px, pelo teclado (FR-1884, SC-745)
- [x] T011 `rastreabilidade.md` com cada FR e SC; a emenda da `FR-1803` da `080` declarada na spec; a linha da `084` no README
- [x] T012 Revisão do PR (`/code-review`, 18/10): os níveis do Edital num parcial, `_ate_o_edital_na_trilha.html`, com guardião; a contagem de desenhos lida dos templates; a impressão sem o Edital (D-005) e o link da Classificação sem o recorte no Ato (D-006) registrados na spec e na pesquisa, sem correção

## Dependencies

T003 e T004 primeiro, independentes entre si; T005 e T006 depois deles. T008–T011 depois de tudo.

## Implementation Strategy

Uma fase de mudança só, a US1; a US2 é a prova de que nada mais mudou, e se escreve junto.
