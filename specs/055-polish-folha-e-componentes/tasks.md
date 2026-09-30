# Tasks: Polish da folha e dos componentes

**Input**: Design documents from `specs/055-polish-folha-e-componentes/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/folha.md](contracts/folha.md), [quickstart.md](quickstart.md)

**Tests**: incluídos. A Constituição (V) pede que cada requisito tenha o que o prenda, e as guardas da
folha deste repositório são testes que leem a folha e os templates. As medidas de tela vão para
[verificacao.md](verificacao.md).

**Regra de toda tarefa que toca `interface/templates/interface/base.html`**: editar a regra **no
lugar**, apagar a regra substituída junto, e rodar em seguida
`tests/interface/test_acessibilidade.py` e `tests/interface/test_larguras.py` (D-001).

Caminhos relativos à raiz do repositório; `F` = `backend/processo_seletivo/interface/templates/interface`,
`P` = `backend/processo_seletivo/portal/templates/portal`.

## Phase 1: Setup

- [x] T001 Medir a margem do teto da distribuição com o teste isolado e registrar em `specs/055-polish-folha-e-componentes/research.md` (D-001)
- [x] T002 Medir o "antes" de todas as telas do quickstart §2 e gravar em `specs/055-polish-folha-e-componentes/verificacao.md`; salvar as capturas "antes" em `specs/055-polish-folha-e-componentes/capturas/`

## Phase 2: Foundational

- [x] T003 Criar `backend/tests/interface/test_polish_da_055.py` com os auxiliares que leem a folha sem comentários (reusar `sem_prosa` e `FONTE` de `tests/interface/test_acessibilidade.py`)

**Checkpoint**: margem conhecida, "antes" gravado, arquivo de teste pronto.

---

## Phase 3: User Story 1 — números com o seu rótulo (P1) 🎯 MVP

**Goal**: Corte, histórico do Corte, Ocupação e histórico da Ocupação no desenho de blocos da Convocação.

**Independent Test**: abrir o Corte e a Ocupação do 51/2026 e conferir cada número no bloco do seu rótulo.

- [x] T004 [P] [US1] Testes em `backend/tests/interface/test_polish_da_055.py`: os quatro templates usam `ul.resumo` com `li>strong`, nenhum usa `dl.resumo`, e a `section` do recorte não leva `.resumo` (**FR-1000** a **FR-1003**, **UX-134**)
- [x] T005 [US1] Trocar o `dl.resumo` da faixa calculada por `ul.resumo` em `F/corte.html`, com a nota de origem do alvo dentro do `li` dele
- [x] T006 [P] [US1] O mesmo nos dois `dl.resumo` de `F/corte_historico.html`
- [x] T007 [P] [US1] Em `F/ocupacao.html`: tirar `.resumo` da `section`; `dl.meta` dos quatro números (e o de "Publicadas" sozinho) vira `ul.resumo`
- [x] T008 [P] [US1] O mesmo em `F/ocupacao_historico.html`

**Checkpoint**: US1 verde por teste e por medida.

---

## Phase 4: User Story 2 — tabelas densas e números comparáveis (P1)

**Goal**: linha das Inscrições ≤ 45 px; pontuação à direita.

- [x] T009 [P] [US2] Testes em `backend/tests/interface/test_polish_da_055.py`: `th,td` com `.5rem .75rem`; a tabela de `ordenacao.html` com `.tabela` e a pontuação com `numero` (**FR-1004**, **FR-1005**)
- [x] T010 [US2] Em `F/base.html`: padding de `th,td` para `.5rem .75rem`; apagar as declarações iguais de `.conferencia-lote th,td` e `.distribuicao th,td` (D-010)
- [x] T011 [US2] Manter `.tabela td.numero` na folha — generalizar órfã `.tabela` (D-011)
- [x] T012 [P] [US2] Em `F/ordenacao.html`: `class="tabela"` na tabela da ordem, e `class="numero"` no `th` e no `td` da Pontuação combinada

---

## Phase 5: User Story 3 — botões com hierarquia e a mesma altura (P1)

**Goal**: 40 px para todo botão e para a ação em barra; ações principais como `.botao`; o botão do portal com peso.

- [x] T013 [P] [US3] Testes em `backend/tests/interface/test_polish_da_055.py`: `.botao` com borda transparente e `line-height` declarado; `.secundario` sem `border-width` próprio; `.perigoso` sem `border:none`; `.acao` partilha a geometria dentro de `.navegacao-etapa`, `.salvar` e `.filtros`; as quatro ações de **FR-1008** com `botao` (**FR-1006** a **FR-1008**, **UX-135**)
- [x] T014 [P] [US3] Em `backend/tests/interface/test_acessibilidade.py`: a guarda `test_todo_botao_de_envio_declara_o_seu_peso` passa a varrer também os templates do portal (**FR-1009**, D-017)
- [x] T015 [US3] Em `F/base.html`: geometria partilhada `.botao,:is(.navegacao-etapa,.salvar,.filtros) .acao`; `.botao` com `border:1px solid transparent`; `.botao.secundario` com `border-color`; `.botao.perigoso` sem `border:none` (D-002, D-003, D-004)
- [x] T016 [P] [US3] `acao` → `botao` no "Filtrar" de `F/inscricoes.html`, `F/distribuicao.html`, `F/comissao.html` e no "Ver o que sairá vazio" de `F/matriculas.html` (D-005)
- [x] T017 [P] [US3] `class="secundario"` em "Guardar e continuar depois", `P/requerimento.html`

---

## Phase 6: User Story 4 — títulos em escala (P2)

- [x] T018 [P] [US4] Testes em `backend/tests/interface/test_polish_da_055.py`: `h3` global de 1 rem; peso 600 para os três níveis; nenhuma regra por contêiner põe `h2` em 1 rem, salvo `.barra-do-painel`; `.secao-da-retificacao>h2` sem caixa-alta (**FR-1010**, **FR-1011**)
- [x] T019 [US4] Em `F/base.html`: `h3{font-size:1rem}` e `h1,h2,h3{font-weight:600}`; tirar o tamanho de `.cartao h2`, `.pendencias h2`, `.consequencias h2`, `.conferencia h3`; tirar tamanho, caixa-alta e espaçamento de `.secao-da-retificacao>h2` (D-008)

---

## Phase 7: User Story 5 — controles e barra de filtro alinhados (P2)

- [x] T020 [P] [US5] Testes em `backend/tests/interface/test_polish_da_055.py`: a regra de altura da gestão e a do portal; a barra por `flex-start`; a margem do contêiner do botão igual à altura do rótulo; a ajuda dos filtros continua com `aria-describedby` (**FR-1012** a **FR-1014**, **UX-136**)
- [x] T021 [US5] Em `F/base.html`: `select,input:not([type$=box],[type=radio],[type=file]){height:2.5rem}` (D-009)
- [x] T022 [US5] Em `F/base.html`: `.filtro,.filtros` com `align-items:flex-start`; `.filtro .salvar,.filtros .acoes,.filtro .escolha` com `margin-top:1.46875rem`; `.filtro .escolha` com `height:2.5rem` (D-006)
- [x] T023 [P] [US5] Em `P/base.html`: altura `2.625rem` nos controles de uma linha de `.campo` (D-016)

---

## Phase 8: User Story 6 — espaço proporcional ao conteúdo (P3)

- [x] T024 [P] [US6] Testes em `backend/tests/interface/test_polish_da_055.py`: a grade da seleção sem a área `sorteio` quando não há sorteio, e com ela quando há; `auto-fill` e o teto dos largos no portal; os dois campos da Comissão com tipo e o teto do identificador; o `.arquivo` com `width:auto` (**FR-1015**, **FR-1016**)
- [x] T025 [P] [US6] Em `P/base.html`: as duas grades de `.corpo-da-selecao` por `:has(>.sorteio-da-selecao)` (D-012)
- [x] T026 [P] [US6] Em `P/base.html`: `.grade-de-campos` com `auto-fill`; `max-width:40rem` no controle de `.campo.largo` (D-013)
- [x] T027 [P] [US6] Em `F/comissao.html`: `type="text"` nos dois campos de inclusão e `{% block estilo_da_pagina %}` com o teto de `20rem` do identificador (D-014)
- [x] T028 [US6] Em `F/base.html`: `input[type="file"].arquivo` com `width:auto` (D-015)

---

## Phase 9: Polish & Cross-Cutting

- [x] T029 Medir o teto de novo e declarar o saldo em `specs/055-polish-folha-e-componentes/verificacao.md` (**FR-1017**)
- [x] T030 Registrar em `doc/achado-resumo-na-secao-das-matriculas.md` o `.resumo` da `section` da Matrículas (D-019)
- [ ] T031 `cd backend && make lint check test-pg DB_NAME=ps_055`; sem editar arquivo durante a suíte (**SC-384**); conferir no `git diff` que nenhum texto de interface, view, formulário, domínio ou PDF mudou (**FR-1019**)
- [x] T032 Medir o "depois" de todas as telas, a 1280 px e a 375 px nas quatro telas de **FR-1018**; capturas "depois"; tabela antes/depois em `specs/055-polish-folha-e-componentes/verificacao.md` (**SC-371** a **SC-383**, **SC-385**)
- [x] T033 Escrever `specs/055-polish-folha-e-componentes/rastreabilidade.md`, requisito a requisito
- [ ] T034 Reverter a entrada `polish-055` de `.claude/launch.json`; commit e PR sem merge

---

## Dependencies & Execution Order

- **Setup (T001, T002)** antes de tudo: o "antes" precisa ser medido com a folha intocada.
- **T003** antes dos testes de cada história.
- **US1** e **US6 (portal)** não tocam `F/base.html` e podem correr em paralelo com as demais.
- **US2 → US3 → US4 → US5 → T028**: todas editam `F/base.html`, e em sequência — o saldo de
  caracteres é somado a cada uma e medido no fim de US5.
- **Polish** depois de todas.

## Parallel Example: User Story 1

```text
T006 corte_historico.html   T007 ocupacao.html   T008 ocupacao_historico.html
```

## Implementation Strategy

- **MVP**: US1 — o Corte é tela de ato irreversível, e é o item de maior impacto.
- Depois US2 e US3 (P1), na ordem da matriz da auditoria; então US4, US5 e US6.
- Se o teto não comportar tudo: entregar na ordem G1, G2+G3, G4+G5, G6, G7, G8, D1, F7 e registrar
  o que faltou.
