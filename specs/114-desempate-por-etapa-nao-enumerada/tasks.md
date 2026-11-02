# Tasks: Desempate pela nota de Etapa que o marco não enumera

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/universo-do-ato.md](contracts/universo-do-ato.md)

**Tests**: pedidos pela spec (cada FR tem teste; o do A11 perde o `xfail`). Caminhos relativos a
`backend/`.

## Phase 1: Setup

- [x] T001 Trazer o teste do A11 do commit `5dc7f420` para
  `tests/integration/classificacao/test_desempate_por_etapa_nao_enumerada.py`, ainda com `xfail`, e
  conferir que ele falha como esperado contra PostgreSQL.

## Phase 2: Foundational

- [x] T002 Criar `etapas_do_desempate(marco)` em `processo_seletivo/classificacao/domain/desempate.py`
  (R-002), com teste unitário em `tests/unit/classificacao/test_universo_classificavel.py` ou no
  arquivo unitário de desempate existente.
- [x] T003 Criar a migration `processo_seletivo/classificacao/migrations/0007_desempate_por_etapa_nao_enumerada.py`
  (R-003), com reversão para o texto exato da `0003`; atualizar a contagem de `classificacao` de 6 para
  7 em `tests/migrations/test_migrations.py`.

## Phase 3: User Story 1 — O critério separa pela nota da Etapa citada (P1)

**Independent Test**: o teste do A11 passa sem `xfail`.

- [x] T004 [US1] Em `processo_seletivo/classificacao/application/calculo.py`, ler na mesma consulta os
  Resultados vigentes de `enumeradas + etapas_do_desempate(marco)`; o universo passa a citá-los
  (FR-3546, FR-3549).
- [x] T005 [US1] Em `processo_seletivo/classificacao/domain/universo_classificavel.py`, montar
  `pontuacoes` de todo Resultado lido e procurar a eliminação só entre os de Etapas enumeradas
  (FR-3547, FR-3548).
- [x] T006 [US1] Retirar o `xfail` do teste do A11 e acrescentar a conferência da proveniência gravada
  (FR-3554) e da pontuação combinada (FR-3547), emitindo o ato.
- [x] T007 [P] [US1] Teste unitário de `preparar` com Resultado de Etapa do desempate: pontuação presente,
  combinada inalterada, motivo de ausência inalterado.

## Phase 4: User Story 2 — Eliminação na Etapa do desempate não tira da ordem (P1)

- [x] T008 [US2] Teste de integração: eliminado na Entrevista (nota abaixo da mínima) continua com
  posição pela Prova; sem nota na Entrevista, vale o `whenMissing` e a emissão sai (FR-3548, FR-3553).
- [x] T009 [P] [US2] Teste unitário de `preparar`: eliminação na Etapa do desempate não gera sem posição;
  eliminação na enumerada continua gerando.

## Phase 5: User Story 3 — Recurso na Etapa do desempate obsoleta a ordem (P1)

- [x] T010 [US3] Em `processo_seletivo/classificacao/application/reproducao.py`, procurar a eliminação só
  entre os Resultados citados de Etapas enumeradas (FR-3552, R-004).
- [x] T011 [US3] Teste de integração: emitir; deferir recurso que corrige a nota da Entrevista;
  `estado_da_ordem`/`comparar` acusa Resultados alterados; a sucessora inverte; a reprodução dos dois atos
  não diverge (FR-3550, FR-3552).
- [x] T012 [P] [US3] Teste da trigger: ato com Resultado de Etapa nem enumerada nem citada é recusado;
  com Resultado da Etapa citada, aceito (FR-3551).
- [x] T013 [P] [US3] Teste da reprodução com eliminado na Etapa do desempate: o ato emitido e o reproduzido
  coincidem (FR-3552).

## Phase 6: User Story 4 — A prévia equivale ao oficial (P2)

- [x] T014 [US4] Em `processo_seletivo/classificacao/domain/cenarios_da_previa.py`, criar
  `com_notas_do_desempate(candidatos, etapas)` (R-006); em
  `processo_seletivo/classificacao/application/previa.py`, aplicá-la nos dois modos (FR-3555).
- [x] T015 [US4] Em `tests/integration/classificacao/test_previa_equivale_ao_oficial.py`, acrescentar o
  marco que desempata por Etapa não enumerada: gravar as notas da Entrevista dos candidatos da prévia e
  comparar as duas pontas (FR-3556).
- [x] T016 [P] [US4] Teste unitário de `com_notas_do_desempate`: iguais nas enumeradas ficam iguais;
  ausência propaga.

## Phase 7: Polish

- [x] T017 Conferir que as tabelas absolutas da `094` passam sem edição (FR-3557, SC-1077).
- [x] T018 Escrever `specs/114-desempate-por-etapa-nao-enumerada/rastreabilidade.md`.
- [x] T019 `cd backend && make lint check test-pg` com `DB_NAME` próprio.

## Phase 8: Achados da revisão de código (02/11)

- [x] T020 Em `processo_seletivo/interface/supervisao.py`, `candidato_a_obsoleto` passa a olhar também
  as Etapas do desempate: sem isso a Supervisão e a condução do marco diziam "feito" de uma ordem
  obsoleta pela nota da Entrevista (FR-3550).
- [x] T021 Teste do corte: recurso deferido na Etapa do desempate obsoleta a geração que leu a ordem
  (research R-005).
- [x] T022 A regra "a consequência só das enumeradas" num lugar só,
  `universo_classificavel.que_decidem_posicao`, chamada pelo preparo e pela reprodução.
- [x] T023 A `0007` aceita `tiebreakers` que não seja lista sem levantar erro na emissão.

## Phase 9: Revisão do PR (02/11)

- [x] T024 `etapas_que_a_ordem_le(marco)` em `processo_seletivo/classificacao/domain/desempate.py`, chamada
  por `calculo.py` e por `interface/supervisao.candidato_a_obsoleto` (R-008).
- [x] T025 [US5] `recursos/application/selectors._etapas_do_marco` passa a ser a dependência efetiva:
  recurso pendente, reavaliação pendente e providência a jusante sobre a nota que desempata (FR-3559 a
  FR-3561).
- [x] T026 [US5] A `0007` substitui também `check_decision_citation_coherence`, e a reversão restaura o
  texto da `0004` (FR-3560).
- [x] T027 [US5] Testes em `tests/integration/classificacao/test_desempate_por_etapa_nao_enumerada.py`:
  recurso pendente, reavaliação, providência citada e cumprida, e o controle sem o critério. Conferido
  em 02/11 que os três primeiros falham com a pertinência antiga, e o da providência sem a trigger nova.
- [x] T028 [US3] Os testes de obsolescência conferem as três telas juntas: tela da classificação,
  condução do marco e Supervisão (`_obsoleta_nas_tres_telas`).
- [x] T029 [US6] O caso `desempate_por_outra_etapa` em `cenarios_da_previa.py` e `previa.py`, oferecido
  só no marco que desempata por Etapa com nota que não enumera (`interface/previa_da_classificacao.py`)
  (FR-3558, R-007).
- [x] T030 [P] [US6] Testes em `tests/unit/classificacao/test_previa.py` e o caso novo em
  `tests/integration/classificacao/test_previa_equivale_ao_oficial.py` (SC-1079).
- [x] T031 [US7] `tests/integration/classificacao/test_desempate_pela_etapa_que_o_corte_governa.py`: o
  percurso inteiro e os três cenários da D-007 (FR-3562, SC-1080).
- [x] T032 Spec, pesquisa, plano, rastreabilidade e quickstart revistos; D-003, D-005 e D-006 revistas,
  D-007 nova.

## Dependencies

T001 → T002, T003 → US1 (T004, T005 → T006) → US2, US3 (independentes entre si) → US4 → Polish.
US2 e US3 dependem de T004/T005; US4 depende de T005. T007, T009, T012, T013 e T016 são de arquivos
distintos e podem correr em paralelo.

## Implementation Strategy

MVP = US1 (o A11 resolvido). US2 e US3 fecham o que a correção ingênua quebraria (classificação e
obsolescência), e entram no mesmo PR: sem elas a correção não é segura. US4 mantém a prévia honesta.
