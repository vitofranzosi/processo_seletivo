# Tasks: As quatro decisões de produto da etapa 4

**Input**: [spec.md](spec.md), [plan.md](plan.md), [quickstart.md](quickstart.md)

**Tests**: incluídos — a rastreabilidade deste repositório é verificada por teste, e cada requisito
tem linha em [rastreabilidade.md](rastreabilidade.md). Caminhos relativos a `backend/`; os templates
estão em `processo_seletivo/interface/templates/interface/`.

## Phase 1: Setup

- [x] T001 Spec, plano, quickstart, tarefas e rastreabilidade; a linha do `README`; as quatro decisões do usuário de 18/10/2026 registradas (D-001 a D-004)
- [ ] T002 Conferir com `gh pr view N --json state` que os PRs 298, 300, 302 e 304 estão mergeados; sem os quatro, parar aqui
- [ ] T003 `git merge origin/main`; `uv sync --extra dev --extra assistente`; banco do inventário próprio (`ps_inventario_088`, `migrate --check` limpo); banco de teste próprio (`DB_NAME=ps_088`)
- [ ] T004 Inventário de antes, nos dois estados da barra, sobre a `main` mergeada, em `doc/inventario-visual-da-gestao-2026-10-16/depois-da-088/antes/`

## Phase 2: Foundational

Nenhuma: o bloco `caminho_do_contexto` existe desde a `077`, e `_navegacao_do_recorte` desde a `034`.

## Phase 3: User Story 1 — a tela impressa diz de onde é (P1) 🎯 MVP

**Goal**: o cabeçalho de contexto no papel, sem "Trocar identidade", com a barra lateral fora.

**Independent Test**: com a mídia de impressão, a trilha vem antes do título nas quatro telas da `SC-780`.

- [ ] T005 [US1] `base.html`, `@media print`: o cabeçalho sai em bloco, sem altura mínima e sem moldura; `.cabecalho-de-contexto>a` e `.barra-lateral` ficam fora; comentário de Django com a decisão; nenhuma linha com `}}` (FR-2000 a FR-2004; D-001, D-005)
- [ ] T006 [US1] Testes em `tests/interface/test_decisoes_da_etapa_4.py`: a regra lida da folha; a trilha dentro do cabeçalho e "Trocar identidade" como o único link fora dela, na inscrição da Mesa, num Ato, numa Inscrição recebida e num Recurso (FR-2000 a FR-2002, SC-780)

## Phase 4: User Story 2 — dois avisos do mesmo dia têm nomes diferentes (P2)

**Goal**: o rótulo do aviso na trilha com a hora.

**Independent Test**: dois avisos do mesmo dia, em minutos diferentes, com rótulos diferentes nas três telas.

- [ ] T007 [P] [US2] `aviso.html`, `aviso_interromper.html`, `aviso_previa.html`: o rótulo do aviso na trilha com `às H:i`, como o título (FR-2010 a FR-2012; D-003, D-007)
- [ ] T008 [US2] Testes: o rótulo com a hora de America/Sao_Paulo num aviso das 22:30 de Brasília; dois avisos do mesmo dia com rótulos diferentes (FR-2010, FR-2011, SC-782)
- [ ] T009 [US2] `tests/interface/test_telas_dos_avisos.py` (da `086`): as duas asserções que prendem *Aviso de DD/MM/AAAA* passam a esperar a hora, com comentário apontando a `FR-2010` (FR-2026)

## Phase 5: User Story 3 — do Ato, a Classificação do mesmo recorte (P2)

**Goal**: "Classificação" leva ao recorte do ato.

**Independent Test**: no Ato da lista PPI, seguir o link abre a Classificação com a PPI como recorte atual.

- [ ] T010 [US3] `views.py`, `ato_de_ordenacao`: `url_da_classificacao` pelo `_navegacao_do_recorte` com `atual=ato.lista_id`; `ato_ordenacao.html` usa a variável (FR-2020 a FR-2022; D-004, D-006)
- [ ] T011 [US3] Testes: Ato da lista PPI — o link com o recorte e o destino com a PPI como recorte atual; Ato da ampla concorrência — o link de antes (FR-2020, FR-2022, SC-783)

## Phase 6: Polish

- [ ] T012 Anotações de substituição nas specs de origem: o caso-limite "Impressão" da `076` e o da `077`; a decisão 002 da `081`; a decisão 005, a decisão 006 e a `FR-1881` da `084`; a `FR-1941` da `086` — cada uma apontando para a `088`
- [ ] T013 Inventário de depois nos dois estados da barra, comparado por `comparar.py` e `medidas.py`; conferência de impressão das quatro telas por emulação e por `--print-to-pdf`; seção "Depois da 088" no inventário (SC-781)
- [ ] T014 `make lint check test-pg DB_NAME=ps_088 POSTGRES_USER=$USER`, com `LC_ALL=pt_BR.UTF-8` (FR-2025, FR-2026, SC-784)
- [ ] T015 Commit e PR contra a `main`, sem merge
