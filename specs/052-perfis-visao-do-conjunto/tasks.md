# Tasks: Perfis de Vaga — a visão do conjunto e um editor por vez

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[contracts/tela-da-etapa.md](contracts/tela-da-etapa.md), [quickstart.md](quickstart.md)

**Tests**: pedidos. Cada requisito tem teste que falha sem o código, ou verificação no navegador
quando o shim não alcança (R-002, R-007); a [rastreabilidade](rastreabilidade.md) diz qual. Caminhos
relativos a `backend/`. **TV** = `tests/interface/test_visao_dos_perfis.py`; **TJ** =
`tests/javascript/perfis.test.js`.

## Phase 1: Setup

- [X] T001 Ambiente: `.env` com `DB_NAME=ps_052`, `uv sync --extra dev`, `make check`

## Phase 2: Foundational — o que o servidor entrega (bloqueia todas as histórias)

- [X] T002 [P] Filtro `legenda_do_perfil` em `processo_seletivo/interface/templatetags/interface_extras.py` e a legenda em `templates/interface/_perfil.html` (FR-944, R-006); TV da legenda nos três casos, e no fragmento de Perfil novo
- [X] T003 [P] `forms.perfis_alterados(digitados, gravados)` em `processo_seletivo/interface/forms.py` (R-004); TV: devolução sem mudança dá conjunto vazio; mudança num campo, numa Modalidade, numa linha do quadro e num fato acusa só aquele Perfil; Perfil sem par gravado é alterado
- [X] T004 Contexto da etapa Perfis em `processo_seletivo/interface/views.py`: `pendencias_por_perfil` (R-003) e `perfis_alterados` quando a tela volta do digitado; `_perfil.html` com `id="cartao-…"`, `data-pendencias`, `data-nao-salvo` (contrato); TV
- [X] T005 `data-resumo` nas opções de reserva e de forma de convocação em `_perfil.html` (R-005); TV
- [X] T006 Ordem da etapa em `templates/interface/compor_perfis.html`: `#visao-dos-perfis`, *Acrescentar Perfil*, controle do Edital, preencher, `#perfis` (UX-120, R-008); o `<script>` de `perfis.js`; TV da ordem, do contêiner, e de que nenhum cartão sai do servidor com `hidden` (FR-955)

## Phase 3: US1 — ver o conjunto e trabalhar num Perfil de cada vez (P1)

- [X] T007 `static/interface/perfis.js`: regras puras exportáveis para o node (resumo da linha a partir do cartão, cartão a abrir ao carregar, alterado na tela) e a montagem — tabela, cabeçalho do editor, `hidden`, *Editar*/*Anterior*/*Próximo*/*Voltar à lista*, foco, fragmento do endereço, contador oculto, linha acompanhando a digitação (FR-945–FR-953, UX-116–UX-119)
- [X] T008 [P] TJ das regras puras: resumo (código ausente, reserva limitada com limite, Modalidades, convocação pelo `data-resumo`), precedência da abertura, alterado por valor e por inserção
- [X] T009 [P] Estilo no `estilo_da_pagina` de `compor_perfis.html` (UX-118, UX-121), sem tocar `base.html`

## Phase 4: US2 — nunca travar em silêncio (P1)

- [X] T010 Ouvinte de `invalid` em captura (FR-954, R-002) em `perfis.js`; TJ da regra "primeiro da rodada"; verificação no navegador (quickstart 3)
- [X] T011 Abertura pela recusa e pelo fragmento (FR-953 b–d, R-007); verificação no navegador (quickstart 4 e 5)

## Phase 5: US3 — criar, duplicar, remover e aplicar como antes (P1)

- [X] T012 Observação de `#perfis` em `perfis.js`: cartão inserido abre (FR-956, FR-957); cartão removido leva a linha e move o foco (FR-958); passagem de 1↔2 Perfis (FR-945)
- [X] T013 TV: o conjunto de campos da etapa é o mesmo de hoje (SC-350) — nomes dos controles de `#formulario` antes e depois, e nenhum `name` criado pelo script (varredura do fonte)
- [X] T014 Suíte da `043`, da `051`, do quadro e do rascunho local sem mudança (FR-959, SC-353)

## Phase 6: US4 — ver onde está o problema (P1)

- [X] T015 Situação na linha a partir de `data-pendencias` e do alterado (FR-948, FR-949); TJ das frases; TV com Perfil sem forma de convocação num marco que corta

## Phase 7: Polish

- [X] T016 Manual (`doc/manual`) e o roteiro assistido, onde descrevem os cartões da etapa Perfis — conferido: a captura SS-013 é de um Perfil só, que não tem tabela (FR-945), e o roteiro conta interações, não descreve a tela; nada a mudar
- [X] T017 Rastreabilidade: uma linha por `FR-`, `SC-`, `UX-` e caso-limite
- [X] T018 `make lint check test-pg DB_NAME=ps_052`; quickstart inteiro no preview; medir SC-348 e SC-351
