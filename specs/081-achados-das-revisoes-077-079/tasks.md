# Tasks: Os achados das revisões da 077 e da 079

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[quickstart.md](quickstart.md)

**Tests**: incluídos — a rastreabilidade deste repositório é verificada por teste, e cada requisito
tem linha em [rastreabilidade.md](rastreabilidade.md). Caminhos relativos a `backend/`; os templates
estão em `processo_seletivo/interface/templates/interface/`.

## Phase 1: Setup

- [x] T001 Banco do inventário próprio (`ps_inventario_081`, cópia do `ps_inventario_080`, `migrate --check` limpo), banco de teste próprio (`DB_NAME=ps_081`), `uv sync --extra dev --extra assistente` e a entrada `telas-081` no `.claude/launch.json` (porta 8083)
- [x] T002 Inventário de antes, nos dois estados da barra, sobre `cf6d7372`, guardado em `depois-da-081/antes/`; comparado com `depois-da-080/` pelo `medidas.py` — nenhuma variante diferente
- [x] T003 O destino de cada um dos dez achados, na tabela de decisões da spec (SC-710)

## Phase 2: Foundational

Nenhuma.

## Phase 3: User Story 1 — o que não se desfaz não pesa como a rotina (P1) 🎯 MVP

**Goal**: na Distribuição, um botão cheio sobre a seleção, e a marca "irreversível" na consolidação.

**Independent Test**: "Consolidar as selecionadas" é `botao secundario` seguido da marca; "Distribuir as selecionadas" é `botao`.

- [x] T004 [US1] `distribuicao.html`: "Consolidar as selecionadas" com `botao secundario` e a marca (R-001; FR-1820, FR-1821)
- [x] T005 [US1] `base.html`: `align-self:center` na regra da `.marca-irreversivel` (R-002; FR-1820)
- [x] T006 [US1] Testes em `tests/interface/test_achados_das_revisoes.py`: o desenho dos dois botões, a marca logo depois, a frase antes deles, destino e valor iguais; a regra da marca na folha (FR-1820, FR-1821, SC-711)
- [x] T007 [US1] `test_telas_da_presidencia.py::test_nenhuma_acao_da_distribuicao_sai_do_lugar`: a contagem de `class="botao"` passa de 6 para 5, com o porquê (R-006)

## Phase 4: User Story 2 — a Alocação diz alocar (P2)

- [x] T008 [US2] `alocacoes.html`: "Designe a presidência antes de alocar." (R-003; FR-1822)
- [x] T009 [US2] `test_alocacoes.py` e `test_telas_da_presidencia.py`: a frase nova; teste novo de que nenhum texto visível da Alocação diz "antes de distribuir" (FR-1822, SC-712)

## Phase 5: User Story 3 — uma fixture, um dono (P3)

- [x] T010 [US3] A montagem do `cenario` de `test_acessibilidade_da_012.py` para `tests/fixtures/mesa.py` (`montar_cenario_da_presidencia`); a fixture declarada em cada um dos quatro módulos, sem o import e sem os `noqa` (R-004; FR-1823)
- [x] T011 [US3] Guardiões em `tests/interface/test_achados_das_revisoes.py`: nenhum módulo importa o `cenario`; toda trilha sobrescrita abre com a mesma navegação nomeada (R-004, R-005; FR-1823, FR-1824, SC-713)

## Phase 6: Polish

- [x] T012 Inventário de depois, nos dois estados da barra, em `depois-da-081/`; `comparar.py` e `medidas.py` contra `depois-da-081/antes/` (FR-1825, SC-714)
- [x] T013 Percurso do quickstart no navegador, a 1280 e a 375 px
- [x] T014 Teto da distribuição (`performance/test_escala_da_mesa.py`) medido antes e depois
- [x] T015 README (a linha da `081` na tabela de incrementos) e o inventário em `doc/`
- [x] T016 `make lint check test-pg DB_NAME=ps_081` (FR-1826, SC-715)

## Phase 7: Emenda da revisão do PR (18/10)

- [x] T017 `distribuicao.html`: `aria-describedby` das duas consolidações para a marca; "Consolidar as N prontas" com `botao secundario` e a marca (R-007; FR-1827, FR-1828)
- [x] T018 `base.html`: a regra da marca sem o contêiner (R-002; FR-1820)
- [x] T019 `tests/fixtures/mesa.py`: a montagem sobre `montar_banca`, com código e chaves do `seed` (R-004; FR-1823)
- [x] T020 `test_achados_das_revisoes.py`: testes da descrição acessível e das prontas; o guardião da fixture sobre todos os donos; o da trilha sem rigidez; o aviso e a regra sem texto literal; mutação nos dois guardiões (R-005, R-007; FR-1823, FR-1824, FR-1827, FR-1828, SC-711)
- [x] T021 `test_telas_da_presidencia.py`: a contagem de cheios passa a 4, e o comentário diz o que mudou (R-006)
- [x] T022 Inventário de depois refeito nos dois estados da barra; `make lint check test-pg DB_NAME=ps_081` (FR-1825, FR-1826, SC-714, SC-715)
- [x] T023 Segunda revisão do PR: os guardiões aceitam `endblock` nomeado e chamada por atributo; comentário da marca, botão das prontas e docstring de `montar_banca` acertados; a marca fora da Distribuição registrada (R-008)
