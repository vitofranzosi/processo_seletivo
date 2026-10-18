# Tasks: As telas dos avisos aos candidatos, quinto grupo da etapa 4

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[quickstart.md](quickstart.md)

**Tests**: incluídos — a rastreabilidade deste repositório é verificada por teste, e cada requisito
tem linha em [rastreabilidade.md](rastreabilidade.md). Caminhos relativos a `backend/`; os templates
estão em `processo_seletivo/interface/templates/interface/`.

## Phase 1: Setup

- [x] T001 Banco do inventário próprio (`ps_inventario_086`, cópia do `ps_inventario_telas`, `migrate --check` limpo), banco de teste próprio (`DB_NAME=ps_086`) e `uv sync --extra dev --extra assistente`; nenhuma entrada nova no `.claude/launch.json`
- [x] T002 Inventário de antes, nos dois estados da barra, sobre `cf6d7372`, guardado em `depois-da-086/antes/`; comparado com `depois-da-080/` — nenhuma variante diferente

## Phase 2: Foundational

Nenhuma: o bloco `caminho_do_contexto` do cabeçalho existe desde a `077`, o parcial do produto desde a `078`, e `.vazio`, `.salvar` e `.acoes-do-painel` têm regra na folha comum.

## Phase 3: User Story 1 — onde estou, nas telas de um Edital (P1) 🎯 MVP

**Goal**: a trilha no cabeçalho, pelo Processo, nos Avisos aos candidatos, no histórico e na interrupção.

**Independent Test**: a página tem uma `nav` "Trilha de navegação", no cabeçalho de contexto, com o Processo e o Edital, e o `main` começa pelo título.

- [x] T003 [P] [US1] `avisos_do_edital.html`, `aviso.html`, `aviso_interromper.html`: a trilha do Edital com a tela no fim, no bloco `caminho_do_contexto`; a interrupção passa pelos Avisos aos candidatos (R-001; FR-1940, FR-1941, FR-1945)
- [x] T004 [US1] Testes em `tests/interface/test_telas_dos_avisos.py`: a trilha única no cabeçalho, os níveis em ordem e o conteúdo pelo título; a interrupção recusada; a mesma trilha para quem avisa e quem só consulta (FR-1940, FR-1941, FR-1945, FR-1946, SC-762, SC-763)

## Phase 4: User Story 2 — a prévia diz a porta (P1)

**Goal**: a trilha da prévia é a da tela de onde ela se abre.

**Independent Test**: nas três variantes, o nível acima é a porta, com o rótulo dela, e cada link leva aonde diz.

- [x] T005 [US2] `aviso_previa.html`: o reenvio primeiro, pelos Avisos aos candidatos e pelo aviso anterior; depois a chamada, pela Convocação; por fim o resultado, pelos Avisos aos candidatos — com o comentário do porquê (R-002; FR-1942, FR-1943)
- [x] T006 [US2] Testes: a prévia do resultado, a do reenvio de falhas, a da chamada e a do reenvio justificado de um aviso de chamada; nenhum rótulo de trilha com dois destinos; a frase de que é uma prévia antes de tudo (FR-1942, FR-1943, FR-1951)

## Phase 5: User Story 3 — os modelos na seção da barra (P2)

- [x] T007 [US3] `modelos_de_aviso.html` e `modelo_de_aviso.html`: a trilha a partir da seção; "Novo modelo" em `p.acoes-do-painel` (R-003, R-005; FR-1944, FR-1950)
- [x] T008 [US3] Testes: a lista sem link e sem *Processos Seletivos*, com a barra marcando a mesma seção; a edição e o modelo novo com a seção como link; o modelo recusado (FR-1944, FR-1950)

## Phase 6: User Story 4 — o desenho comum (P3)

- [x] T009 [P] [US4] Os três estados vazios em `p.vazio`; os botões da edição de um modelo e da interrupção em `p.salvar` (R-004, R-005; FR-1948, FR-1949)
- [x] T010 [US4] Testes: os dois estados vazios dos Avisos aos candidatos num Edital sem resultado, o dos modelos; o rodapé dos dois formulários, com os mesmos botões; as ações que não se desfazem com o desenho de antes (FR-1948, FR-1949, FR-1951)

## Phase 7: Polish & Cross-Cutting

- [x] T011 `FR-1803` da `080` anotada como emendada; a linha da spec no README
- [x] T012 Inventário de depois nos dois estados da barra, comparado por `comparar.py` e `medidas.py` com o de antes, e pixel a pixel fora do escopo; capturas e `resultados.json` em `depois-da-086/`; seção "Depois da 086" no `doc/inventario-visual-da-gestao-2026-10-16.md` (FR-1952, SC-760, SC-761)
- [x] T013 Percurso do [quickstart](quickstart.md) no navegador, a 1280 e a 375 px, pelo teclado (FR-1947, SC-765)
- [x] T014 `make lint check test-pg DB_NAME=ps_086` (SC-764)

## Dependencies & Execution Order

T001 → T002 → (T003, T005, T007, T009 em paralelo, arquivos distintos) → testes de cada história → T011 → T012, T013 → T014.
