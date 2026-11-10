# Tasks: A convocação e a conferência documental, pelas perguntas de quem conduz

**Input**: `specs/143-convocacao-e-documentos/` (spec, plan, research, data-model, contracts, quickstart)

**Tests**: pedidos — a rastreabilidade é verificada por teste (CLAUDE.md), e a spec exige que nada
mude nos números nem nos comandos.

Caminhos relativos a `backend/`.

## Phase 1: Setup

- [x] T001 Banco descartável `ps143` com os cenários da `134` e a entrada `convocacao-143` em `../.claude/launch.json` (acrescentada, sem sobrescrever o arquivo)
- [x] T002 Capturas do antes em `../specs/143-convocacao-e-documentos/capturas/antes-*.png` com `../specs/143-convocacao-e-documentos/passeio/passeio.py`

## Phase 2: Foundational

- [x] T003 `processo_seletivo/avisos/application/pendencias.py`: `previa` devolve também `por_chamada` (`{str(raiz.id): motivo}`), da mesma `Selecao` (R-2)
- [x] T004 Módulo de leitura `processo_seletivo/interface/conducao_da_convocacao.py`: `contexto_do_recorte`, `Passo` e `passo_da_chamada`, `avisos_por_raiz` e `situacao_do_aviso`, `indice`, `anotar`, `pessoas_do_recorte` (data-model)
- [x] T005 [P] Testes unitários do passo, da situação do aviso e do índice em `tests/unit/interface/test_conducao_da_convocacao.py`

## Phase 3: User Story 1 — o índice e o contexto da convocação (P1)

**Independent Test**: C10 diz "3 titulares a convocar"; C12, "3 com documento a conferir" com link à primeira chamada.

- [x] T006 [US1] View `convocacao` em `processo_seletivo/interface/views.py`: contexto do recorte, `confere`, `anotar` e `indice`
- [x] T007 [US1] `processo_seletivo/interface/templates/interface/convocacao.html`: cabeçalho com contexto e o índice `#neste-recorte`
- [x] T008 [P] [US1] Folha `processo_seletivo/interface/static/interface/telas/convocacao.css`, pelo bloco `estilo_da_pagina`

## Phase 4: User Story 2 — as vagas em dois grupos (P1)

- [x] T009 [US2] Seção `#numeros` em `convocacao.html`: grupo da apuração (com a data de emissão) e grupo das chamadas; a frase e a explicação recolhida da ocupação

## Phase 5: User Story 3 — o cartão da chamada e o aviso da pendência (P1)

- [x] T010 [US3] Cartão em `convocacao.html`: `id="convocacao-<id>"`, o passo primeiro, a situação do aviso, a ação do passo para quem pode, o desfecho aberto quando é o passo, as excepcionais numa linha secundária
- [x] T011 [US3] As três áreas ("Convocar", "Acompanhar e conferir", "Fila, suplentes e regularização") em `convocacao.html`, com os ids da `139`

## Phase 6: User Story 4 — os documentos da pessoa (P1)

- [x] T012 [US4] View `documentos_da_convocacao` em `processo_seletivo/interface/views.py`: contexto, passo, aviso, resumo, pessoas do recorte (anterior, seguinte, próxima a conferir), `pode_emitir`
- [x] T013 [US4] `processo_seletivo/interface/templates/interface/convocacao_documentos.html` e `static/interface/telas/convocacao-documentos.css`

## Phase 7: User Story 5 — exceções e explicações (P2)

- [x] T014 [US5] Explicações recolhidas de Ocupação, Corte, Desfecho e Sucessão em `convocacao.html` e a frase da área da fila

## Phase 8: Polish

- [x] T015 Testes de tela nos cenários da `134` em `tests/integration/treinamento/test_convocacao_pelas_perguntas.py` (índice, vagas, passo, aviso nos três momentos, documentos, permissões, 139)
- [x] T016 Ajustar os testes que liam a redação antiga, sem afrouxar o que eles provam
- [x] T017 `make lint check test-pg` com `DB_NAME` próprio
- [x] T018 Passeios com Playwright nos C10, C11, C12, C15, como presidência e como auditoria, a 1440 e a 375; capturas do depois e `verificacao.md`
- [x] T019 `rastreabilidade.md` (FR, SC, UX e casos-limite → tarefa → teste)

## Dependencies

T003 → T004 → (T006, T012). US1 a US3 tocam o mesmo template e vão em sequência; US4 é independente
das outras depois de T004. T015–T019 no fim.

## Implementation Strategy

MVP: US1 + US3 (o índice e o cartão), que respondem as perguntas do dia. Depois US2, US4 e US5.
