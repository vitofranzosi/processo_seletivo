# Tasks: Jornada operacional da Retificação

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/telas.md](contracts/telas.md)

**Tests**: pedidos pela feature (jornadas A a H por sessões independentes, e os quatro `xfail` da
auditoria). Caminhos relativos à raiz do repositório.

## Phase 1: Setup

- [X] T001 Trazer o relatório e o teste da auditoria do PR #338 para a branch: `doc/auditoria-retificacao-passagem-e-sorteio-2026-10-29.md`, `backend/tests/interface/test_auditoria_passagem_da_retificacao.py`
- [X] T002 Acrescentar a linha da `103` na tabela de incrementos do `README.md`

## Phase 2: Foundational (bloqueia todas as histórias)

- [X] T003 Derivação dos atos em `backend/processo_seletivo/interface/atos_retificacao.py`: `EM_CURSO`, `PROXIMO_RESPONSAVEL`, `participantes`, `motivo_previsivel` (segregação pelas funções de `publicacoes/application/selectors.py`), `ofertas`, `impedimento` com `segregacao`, `proximo_passo`, `pode_editar`, `fecharia_a_publicacao`, `resumo`, `em_curso_por_edital` (R-001)
- [X] T004 [P] Testes unitários da derivação em `backend/tests/unit/interface/test_atos_da_retificacao.py`: próximo responsável por situação, "é você", segregação em `publicar`, aviso de homologação, ofertas iguais a `disponiveis` sem segregação, finais sem próximo

## Phase 3: User Story 1 — encontrar o trabalho sem endereço (P1) 🎯 MVP

**Goal**: quem homologa e quem publica alcançam a Retificação a partir da barra.
**Independent Test**: `test_quem_homologa_encontra…` e `test_quem_publica_encontra…` passam sem `xfail`.

- [X] T005 [US1] Parcial `backend/processo_seletivo/interface/templates/interface/_retificacoes_em_curso.html` (situação, criação, justificativa, próximo responsável, ato da pessoa, link) (R-003)
- [X] T006 [US1] Seção "Retificações em curso" no detalhe do Edital: contexto em `backend/processo_seletivo/interface/views.py` (`detalhe`) e template `detalhe.html`, com estado vazio para Edital publicado (FR-2701–FR-2705)
- [X] T007 [US1] Marca por Retificação na célula de situação da Lista: uma consulta em `views.lista`, template `lista.html` (FR-2706–FR-2708, R-002)
- [X] T008 [US1] Regras das classes novas em `backend/processo_seletivo/interface/static/interface/telas/lista.css` e na folha comum da gestão
- [X] T009 [US1] (SC-972) Retirar as marcas `xfail` de AUD-RET-01 (três casos) em `backend/tests/interface/test_auditoria_passagem_da_retificacao.py`, sem mudar as asserções; ajustar `test_hoje_nenhuma_tela…` e `test_a_unica_porta…`, que descrevem o defeito, para a forma corrigida

## Phase 4: User Story 3 — passagem de bastão e segregação antecipada (P1)

**Goal**: o detalhe e a confirmação respondem às quatro perguntas e não oferecem o que o servidor recusa.
**Independent Test**: `test_o_detalhe_nao_oferece_publicar…` passa sem `xfail`; a matriz papel × situação concorda.

- [X] T010 [US3] Detalhe da Retificação: contexto em `views.retificacao_detalhe` e template `retificacao_detalhe.html` — passagem de bastão, ofertas com motivo, "Quem atuou", encerrada (FR-2710–FR-2713, FR-2725)
- [X] T011 [US3] Confirmação: `views.praticar_ato_retificacao`, `retificacao_confirmar.html` e `_impedimento.html` — entrega do ato, aviso de homologação, impedimento por segregação (FR-2726–FR-2728)
- [X] T012 [US3] Retirar o `xfail` de AUD-RET-03 em `test_auditoria_passagem_da_retificacao.py`

## Phase 5: User Story 2 — retomar e corrigir no mesmo registro (P1)

**Goal**: a edição do mesmo registro, com revisão e trilha.
**Independent Test**: jornada B (duas devoluções) termina publicada com o mesmo identificador.

- [X] T013 [P] [US2] Fusão conferida em `backend/processo_seletivo/publicacoes/domain/fusao.py` (R-006)
- [X] T014 [P] [US2] Testes unitários da fusão em `backend/tests/unit/publicacoes/test_fusao_da_edicao.py`: campo tocado, intocado, de volta ao vigente, acréscimo editado, acréscimo removido, remoção desfeita, remoção nova, inconsistência recusada
- [X] T015 [US2] `edit_retification` registra `ALTERAR_RASCUNHO` com revisões e `correlation_id`; a API o repassa — `publicacoes/application/retificacoes.py`, `publicacoes/api/views.py` (R-008, FR-2723); `alteracoes_declaradas` pública
- [X] T016 [US2] Partir `views.retificar` em porta e miolo (`_compor_retificacao`), sem mudar a criação; porta nova `retificacao_editar` e rota `retificacao-editar` em `interface/urls.py` (R-005, R-007, R-009; FR-2716, FR-2721, FR-2722)
- [X] T017 [US2] Modo de edição em `retificar.html`: título, aviso, `revisao`, remoções a desfazer, rótulos, sem gestos; regras em `retificar.css` (FR-2717–FR-2720, FR-2724)
- [X] T018 [US2] "Editar a Retificação" e o motivo da devolução no detalhe (FR-2714, FR-2715)

## Phase 6: User Story 4 — ver as em curso ao criar (P2)

- [X] T019 [US4] Aviso com o parcial e "Continuar a elaboração" na tela de Retificar (FR-2709)

## Phase 7: User Story 5 e jornadas — exceções e testes de ponta a ponta (P2)

- [X] T020 [US5] `backend/tests/interface/test_jornada_da_retificacao.py`: jornadas A (fluxo completo), B (devolução de revisão e de homologada, duas vezes), C (interrompida e retomada por outra pessoa), D (segregação e vários papéis), E (outra unidade), F (concorrência na edição e no ato), G (publicação, documentos, consolidação e trilha), H (navegação sem URL), cancelamento só ao Gestor, recusas 403/409/412 da edição, estado vazio e orçamento de consultas (FR-2729, FR-2730, FR-2731, FR-2732; SC-971, SC-973, SC-974, SC-975, SC-976)
- [X] T021 [US5] Teste da trilha da edição pela API em `backend/tests/integration/publicacoes/` (o evento `ALTERAR_RASCUNHO`)

## Phase 8: Polish & Cross-Cutting

- [X] T022 `rastreabilidade.md` com uma linha por FR e SC; `verificacao.md` com os números reais
- [X] T023 Rodar as suítes de Edital, Retificação e publicação; `uv run pytest tests/test_citacoes_de_requisito.py`
- [X] T024 `cd backend && make lint check test-pg`, registrar os números (SC-977); SC-978 fica para a sessão com pessoas
- [X] T025 Conferir 375 px e teclado nas telas tocadas (navegador do painel)

## Dependencies & Execution Order

- T003 bloqueia US1, US3 e US4. US2 depende de T003 só para o detalhe (T018).
- T013/T014 são independentes de tudo o mais e podem correr em paralelo com US1.
- T020 depende de todas as histórias.

## Parallel Opportunities

- T004 com T005; T013 e T014 com Phase 3.

## Implementation Strategy

MVP: Phase 2 + US1 (a descoberta), que já resolve o achado que parou a reunião. Depois US3, US2, US4
e as jornadas.

## Phase 9: Convergence

- [X] T026 Medir que a leitura das Retificações em curso é uma consulta para vários Editais, em `backend/tests/interface/test_jornada_da_retificacao_convergencia.py` per SC-974 (partial)
- [X] T027 Desfazer pela tela uma remoção declarada, em `backend/tests/interface/test_jornada_da_retificacao_convergencia.py` per FR-2719 (partial)
- [X] T028 Citar a entrada `retificacao-103` do `.claude/launch.json` no `quickstart.md` como o servidor da verificação manual per plan: verificação no navegador (unrequested)
