# Tasks: O shell da gestão

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[quickstart.md](quickstart.md)

**Tests**: incluídos — a rastreabilidade deste repositório é verificada por teste, e cada requisito
tem linha em [rastreabilidade.md](rastreabilidade.md). Caminhos relativos a `backend/`.

**Antes de implementar**: DP-1, DP-2 e DP-3 da spec respondidas pelo responsável pelo produto —
feito em 16/10.

## Phase 1: Setup

- [x] T001 Banco de teste próprio (`DB_NAME=ps_076`) e o `ps_inventario_telas` de pé para o inventário; `uv sync --extra dev`

## Phase 2: Foundational — a navegação derivada da sessão

- [x] T002 `processo_seletivo/interface/navegacao.py`: os itens (rótulo, rota, grupo, predicado), a seção pelo prefixo do caminho e `contexto_da_navegacao(request)` (FR-1713, FR-1714, FR-1715, FR-1716)
- [x] T003 O processador em `config/settings/base.py`, e a view `lista` lendo os `pode_*` dos predicados de `navegacao.py` (R-002)
- [x] T004 [P] Testes da navegação — itens por papel, grupo vazio ausente, seção atual por prefixo, nenhuma consulta — em `tests/interface/test_shell_da_gestao.py`

## Phase 3: User Story 1 — de qualquer tela, qualquer seção (P1) 🎯 MVP

**Goal**: a barra lateral em toda tela da gestão, com as seções que o papel alcança.

**Independent Test**: como Gestor, qualquer tela traz os cinco itens, e cada um leva à seção.

- [x] T005 [US1] A moldura em `processo_seletivo/interface/templates/interface/base.html`: `.barra` com marca, seções e pé; `.area` com o cabeçalho de contexto e o `main` de sempre; sem identidade, o `header.topo` só com a marca (FR-1710, FR-1711, FR-1712, FR-1717)
- [x] T006 [US1] As regras da moldura na folha do `base.html`, num trecho próprio depois das de `header.topo`, prosa em `{% comment %}`; impressão sem barra nem caminho
- [x] T007 [P] [US1] Testes da moldura — presente com identidade, ausente sem ela, link de salto primeiro, `main#conteudo` intacto — em `tests/interface/test_shell_da_gestao.py`

## Phase 4: User Story 2 — nunca oferecer o que a autorização recusa (P1)

**Goal**: os itens da barra são exatamente os destinos que a identidade abre.

**Independent Test**: para cada papel e para a presidência, cada item responde 200 e cada ausente responde a recusa de antes.

- [x] T008 [US2] Teste papel a papel que compara os itens da barra com a resposta real de cada um dos cinco destinos, em `tests/interface/test_shell_da_gestao.py` (FR-1714, FR-1721, SC-661)

## Phase 5: User Story 3 — saber onde se está (P2)

**Independent Test**: em telas de seções diferentes, o caminho e o destaque nomeiam a mesma seção.

- [x] T009 [US3] O caminho até a seção e "Trocar identidade" no cabeçalho de contexto, e `aria-current` no item (FR-1716, FR-1718, R-004)
- [x] T010 [P] [US3] Testes do caminho e do destaque — Edital em Processos Seletivos, Etapa em Minhas Etapas, a trilha da tela intacta e não repetida — em `tests/interface/test_shell_da_gestao.py`
- [x] T011 [US3] Conferir que o caminho não duplica a trilha das 54 telas que a têm

## Phase 6: User Story 4 — no celular, a barra recolhe (P2)

**Independent Test**: a 375 px a barra começa fechada, abre pelo botão, e nenhuma tela estoura.

- [x] T012 [US4] O botão "Seções" com `popovertarget`, o painel `popover` e as regras — sempre aberto na tela larga, recolhido abaixo de 64rem, `@supports` para navegador sem `popover` — no `base.html` (FR-1719, R-005)
- [x] T013 [P] [US4] Testes: o botão e o painel presentes e ligados, nenhum `script` na moldura, em `tests/interface/test_shell_da_gestao.py`; no navegador, abrir e fechar por toque, Enter e Esc

## Phase 7: Polish e prova

- [x] T014 Ajustar os testes que leem o cabeçalho de hoje (lista em `plan.md`, *Testes que mudam*)
- [x] T015 Medir a distribuição contra o teto de 120 000 (FR-1722)
- [x] T016 `rastreabilidade.md`; o estudo em `doc/` apontando para a 076; README/AGENTS se citarem o cabeçalho da gestão
- [x] T017 Navegador a 1280 e 375 px e só pelo teclado (quickstart, SC-660, SC-664)
- [x] T018 Inventário visual refeito com a moldura e comparado tela a tela com a linha de base; o resultado em `doc/` (FR-1720, SC-662)
- [x] T020 A barra recolhida na Alocação por Etapa, pela rota (FR-1724, DP-4), com teste em `tests/interface/test_shell_da_gestao.py`; `tests/integration/avaliacoes/test_documento.py` passa a ler o primeiro item da lista **do conteúdo**
- [x] T019 `make lint check test-pg` com `DB_NAME` próprio (SC-663)

## Phase 8: User Story 5 — a barra retrátil (emenda de 16/10)

**Goal**: na tela larga, recolher a barra a uma faixa de ícones e encontrá-la recolhida na tela seguinte.

**Independent Test**: recolher, navegar, recarregar; a barra continua recolhida, com nome acessível e dica em cada item.

- [x] T021 [US5] Emenda da spec, do plano e da pesquisa (FR-1725 a FR-1732, SC-665 a SC-667, DP-5, DP-6, R-009)
- [x] T022 [US5] Ícone por seção em `processo_seletivo/interface/navegacao.py`, as iniciais da pessoa, e o modo da Alocação renomeado para `no_topo` (FR-1731, FR-1725)
- [x] T023 [US5] `processo_seletivo/interface/static/interface/shell.js` e `tests/javascript/shell.test.js` (FR-1727, FR-1728, FR-1729)
- [x] T024 [US5] A marcação e a folha no `base.html`: sprite, sigla, controle, rótulos que viram dica, avatar, os dois estados a partir de 64rem, movimento reduzido (FR-1725, FR-1726, FR-1730)
- [x] T025 [P] [US5] Testes em `tests/interface/test_shell_da_gestao.py`; `tests/interface/test_visao_geral.py` passa a olhar o conteúdo da tela (FR-1732, DP-6)
- [x] T026 [US5] Navegador: expandida, recolhida, troca repetida, navegação e recarga, celular, teclado e dicas (quickstart)
- [x] T027 [US5] Inventário com a barra expandida e com ela recolhida, `BARRA=` no roteiro (SC-667)

## Dependencies

- Phase 2 bloqueia todas as histórias. US1 bloqueia US3 e US4 (a moldura é onde o caminho e o botão
  moram). US2 depende só da Phase 2 e de T005.
- T018 depende de toda a implementação; T019 é a última.

## Implementation Strategy

US1 + US2 são o MVP — a barra certa para cada papel. US3 e US4 completam o desenho; o inventário e a
suíte fecham a feature. Tudo num PR só, porque as histórias mexem no mesmo `base.html`.
