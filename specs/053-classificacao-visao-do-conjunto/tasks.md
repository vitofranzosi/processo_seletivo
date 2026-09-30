# Tasks: Classificação — a visão do conjunto e um Perfil por vez

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[contracts/tela-da-etapa.md](contracts/tela-da-etapa.md), [quickstart.md](quickstart.md)

**Tests**: pedidos. Cada requisito tem teste que falha sem o código, ou verificação no navegador
quando o shim não alcança (R-007 da `052`, R-007 desta); a [rastreabilidade](rastreabilidade.md) diz
qual. Caminhos relativos a `backend/`. **TC** = `tests/interface/test_visao_da_classificacao.py`;
**TJC** = `tests/javascript/classificacao.test.js`.

## Phase 1: Setup

- [X] T001 Ambiente: `.env` com `DB_NAME=ps_053`, `uv sync --extra dev`; banco de demonstração `ps_053_demo` com 7 Perfis compostos pelo gesto da `051` (quickstart, *Preparar*)
- [X] T002 Linha de base: `make check` e as suítes que não podem mudar — `test_aplicar_a_todos.py`, `test_padroes_da_composicao.py`, `test_acessibilidade_da_classificacao.py`, `test_visao_dos_perfis.py`, `test_rascunho_local.py`, `test_compor_classificacao.py` e `test_javascript.py` — contra PostgreSQL, antes de qualquer mudança

## Phase 2: Foundational — o script comum (bloqueia todas as histórias)

- [X] T003 Extrair `static/interface/vista-do-conjunto.js` do `perfis.js` (R-001): regras puras `situacao`, `cartaoAAbrir`, `controleAlterado`, e `montar(config)` com tabela, editor, um cartão por vez, fragmento, `invalid` (agora também abrindo `details`, R-007), `hashchange`, rolagem ao carregar, observação da lista; o recusado passa a ser também o dono do primeiro alvo do resumo `.erro` (R-006); célula com lista vira um `div` por item
- [X] T004 `static/interface/perfis.js` reduzido à declaração dos Perfis (colunas, `lerCartao`, `resumo`, `percentual`), reexportando para o node as mesmas regras; `compor_perfis.html` carrega o comum antes; `perfis.test.js` sem mudança e verde
- [X] T005 [P] `templates/interface/_estilo_da_vista.html` com as regras da vista, incluído no `estilo_da_pagina` de `compor_perfis.html` (R-011, UX-128); `test_a_tabela_rola_dentro_do_proprio_conteiner` verde
- [X] T006 Guardião do script em `tests/interface/test_visao_dos_perfis.py` varrendo `vista-do-conjunto.js`, `perfis.js` e `classificacao.js` (R-001, SC-358); a etapa Perfis verificada no preview depois da extração (quickstart 13)

## Phase 3: US1 — ver o conjunto e trabalhar num Perfil de cada vez (P1)

- [X] T007 [US1] `templates/interface/compor_classificacao.html`: `#classificacao-perfis`, `fieldset.linha.perfil#cartao-<id>` com `data-codigo`/`data-denominacao`/`data-localidade`, legenda por `legenda_do_perfil` (FR-960); `#visao-da-classificacao` antes do método comum (UX-127, FR-977, R-010); scripts `vista-do-conjunto.js` e `classificacao.js`; o include do estilo; TC da ordem, da legenda, do contêiner e de que nenhum cartão sai com `hidden` (FR-974)
- [X] T008 [P] [US1] `data-resumo-*` em `templates/interface/_marco.html` (forma da ordem, corte, rádios do recurso, `data-metodo-do-marco` no bloco do método) e em `templates/interface/_criterio.html` (tipo), com as frases dos `resumo-do-bloco` (R-003); só atributos, nenhuma ajuda nova no cartão (UX-129); TC das frases; suítes da `051` e da `030` verdes
- [X] T009 [US1] `static/interface/classificacao.js`: colunas (R-002), leitura do cartão do Perfil e dos marcos, as regras puras exportadas (`resumoDoMarco`, `resumoDoPerfil`, `recurso`, `corte`, `criterio`), e `VistaDoConjunto.montar` (FR-961–FR-963, FR-968–FR-971, UX-123–UX-126); a linha acompanha acrescentar e remover marco e critério e a reconstrução do cartão (FR-975)
- [X] T010 [P] [US1] TJC: linha com um marco, com dois, sem marco; marco sem código; corte fixo com quantidade; recurso com prazo; critério com e sem alvo; método próprio só sob sorteio

## Phase 4: US2 — conferir o "aplicar a todos" sem abrir cartão (P1)

- [X] T011 [US2] `origens.origem_dos_marcos(perfis, alcance)` em `processo_seletivo/interface/origens.py` (FR-964, R-004); `_pendencias(..., snapshot=)` em `views.py` para montar o snapshot uma vez; `data-origem` no cartão; TC: aplicado e confirmado → origem nos destinos; editado e gravado → a origem sai; Perfil de dois marcos → sem origem
- [X] T012 [US2] TC: a prévia e o cancelamento voltam com `data-devolvido`; `test_aplicar_a_todos.py` e `test_padroes_da_composicao.py` sem mudança (FR-976–FR-978, SC-360)

## Phase 5: US3 — nunca travar em silêncio, nunca perder o lugar (P1)

- [X] T013 [US3] `_recusa` com o ramo da Classificação em `processo_seletivo/interface/views.py` (FR-973, R-006): marco → controle ou cartão do marco; critério → controle; Perfil → cartão; TC: recusa de critério aponta `criterio-<P>-0-0-target`, recusa de campo sem controle aponta `marco-<P>-0`, e o `id` apontado existe no HTML devolvido (SC-357)
- [X] T014 [US3] Verificação no navegador: inválido escondido (marco, critério, bloco fechado), recusa do servidor, envio que volta sem gravar (quickstart 4–6; FR-971, FR-972, SC-356)

## Phase 6: US4 — ver onde está o problema (P1)

- [X] T015 [US4] Bloco de pendências em `compor_classificacao.html` (FR-966); `data-pendencias` por `_pendencias_por_perfil` sobre `_pendencias_da_etapa(…, "classificacao")` em `views.py` (FR-965); TC: pendência de marco vai à linha do Perfil e ao bloco
- [X] T016 [US4] `_marcos_alterados(digitados, edital)` em `processo_seletivo/interface/views.py` (R-005) e `data-nao-salvo`; TC: a devolução sem mudança não acusa nada (o guardião), a mudança num campo do marco, num critério, marco novo e marco removido acusam só aquele Perfil (FR-967)

## Phase 7: US5 — não perder o digitado (P2)

- [X] T017 [US5] `data-rascunho`/`data-lista` no formulário e `rascunho.js` na etapa (FR-979, R-009); `tests/interface/test_rascunho_local.py` com a Classificação na lista das etapas; TC: restaurar devolve os marcos e marca os Perfis como alterados; verificação no navegador (quickstart 8)

## Achados do percurso (quickstart), corrigidos

- [X] T021 [US5] `static/interface/rascunho.js`: a lista de escolha múltipla guardada e comparada opção por opção — a restauração perdia Etapas do marco; teste de fonte em `tests/interface/test_rascunho_local.py` e verificação no navegador (quickstart 8)
- [X] T022 [US3] `vista-do-conjunto.js`: o endereço que aponta o cartão rola ao título do editor, e não ao centro do cartão (quickstart 6)
- [X] T023 [US1] `_estilo_da_vista.html`: código do Perfil e do marco sem quebra, com classe própria (`codigo` já tinha regra em `base.html`)

## Phase 8: Polish

- [X] T018 Rastreabilidade: uma linha por `FR-`, `SC-`, `UX-` e caso-limite em `specs/053-classificacao-visao-do-conjunto/rastreabilidade.md`
- [X] T019 Manual e roteiro assistido (`doc/manual`), onde descrevem os cartões da etapa Classificação — conferir e ajustar
- [X] T020 `make lint check test-pg DB_NAME=ps_053`; quickstart inteiro no preview; medir SC-354 e SC-355; árvore de acessibilidade (SC-359)

## Dependencies

- T003 → T004 → T006; T003 → T009. T005 antes de T007.
- T007 → T008–T017 (o template é o mesmo arquivo; T008 é outro template e corre em paralelo).
- US2 (T011) e US4 (T015, T016) tocam o contexto da mesma view: em sequência.
- T018–T020 no fim.

## Implementation Strategy

O MVP é a Phase 2 com a US1: a tabela e um Perfil por vez, com a etapa Perfis intacta. A US3 é a que
decide se isto é seguro, e o navegador a verifica antes da US4 e da US5.
