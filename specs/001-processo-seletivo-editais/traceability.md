# Matriz de Rastreabilidade: Processo Seletivo e Editais

**Feature**: `001-processo-seletivo-editais` | **Tarefa**: T093 | **Data**: 2026-08-28

**Escopo**: 38 Requisitos Funcionais ativos, 29 cenários de aceitação e 10 Critérios de Sucesso.
FR-037 e SC-002/009/010 estão formalmente diferidos para a especificação de frontend e não integram
os critérios de aceite deste incremento backend.

**Método**: cada linha aponta os testes automatizados que exercitam o requisito. Onde a cobertura é
parcial ou inexistente, a linha diz isso explicitamente — a matriz registra o estado real, não a
intenção. As referências são verificadas por
`tests/contract/test_traceability.py::test_every_referenced_test_exists`, que falha se um teste
citado aqui deixar de existir.

## Situação consolidada

| | Total | Coberto | Parcial | Sem cobertura | Diferido |
|---|---|---|---|---|---|
| Requisitos Funcionais | 39 | 35 | 3 | 0 | 1 |
| Cenários de aceitação | 29 | 26 | 3 | 0 | 0 |
| Critérios de Sucesso | 10 | 7 | 0 | 0 | 3 |

Três requisitos ficam em **parcial** e estão detalhados em [Lacunas conhecidas](#lacunas-conhecidas).
A mais relevante é FR-023: o documento publicado ainda não reproduz o conteúdo normativo completo.

## Requisitos Funcionais

| FR | Requisito | Evidência | Situação |
|---|---|---|---|
| FR-001 | Estruturar Processo com primeiro Edital, identidades distintas | `tests/integration/processos/test_creation.py::test_process_and_first_edital_are_atomic`, `tests/acceptance/test_us1_processos_editais.py::test_us1_create_add_and_activate` | Coberto |
| FR-002 | Edital pertence a exatamente um Processo; Processo admite vários | `tests/integration/processos/test_creation.py::test_second_edital_has_independent_identity_and_state` | Coberto |
| FR-003 | Impedir Processo sem Edital e criação parcial | `tests/integration/processos/test_creation.py::test_missing_first_edital_creates_nothing`, `tests/integration/processos/test_creation.py::test_duplicate_identifier_leaves_no_partial_process` | Coberto |
| FR-004 | Ciclos de vida de Processo e Edital separados | `tests/acceptance/test_us1_processos_editais.py::test_us1_create_add_and_activate`, `tests/acceptance/test_us7_finalizacao.py::test_us7_process_keeps_its_status_until_an_explicit_act` | Coberto |
| FR-005 | Estados do Processo; ativação e encerramento como atos explícitos | `tests/unit/processos/test_finalizacao.py::test_only_an_active_process_can_be_closed`, `tests/unit/processos/test_finalizacao.py::test_process_can_be_cancelled_before_a_final_state`, `tests/unit/processos/test_finalizacao.py::test_final_process_states_never_return_to_a_previous_one` | Coberto |
| FR-006 | Estados do Edital; Encerrado distinto de Cancelado | `tests/unit/processos/test_finalizacao.py::test_only_a_published_edital_reaches_regular_conclusion`, `tests/unit/processos/test_finalizacao.py::test_cancelled_edital_is_not_presented_as_regular_conclusion`, `tests/acceptance/test_us7_finalizacao.py::test_us7_closing_an_edital_is_not_treated_as_cancellation` | Coberto |
| FR-007 | Edital registra número, ano, título, vínculo, situação e histórico | `tests/contract/test_processos_api.py::test_create_response_matches_contract`, `tests/integration/processos/test_creation.py::test_process_and_first_edital_are_atomic` | Coberto |
| FR-008 | Identidade interna separada do código institucional; unicidade | `tests/integration/processos/test_creation.py::test_duplicate_identifier_leaves_no_partial_process`, `tests/authorization/test_processos.py::test_cross_scope_process_is_not_revealed` | Coberto |
| FR-009 | Incluir um ou vários Perfis no Edital | `tests/acceptance/test_us2_perfis.py::test_us2_replaces_profiles_without_affecting_other_edital`, `tests/integration/editais/test_perfis.py::test_profile_code_is_unique_only_inside_its_edital` | Coberto |
| FR-010 | Perfil mantém identificação, requisitos, vagas e classificação | `tests/unit/editais/test_perfis.py::test_allows_immediate_vacancies_without_reserve`, `tests/integration/editais/test_perfis.py::test_profile_code_is_unique_only_inside_its_edital` | Coberto |
| FR-011 | Vagas e modalidades pertencem ao Perfil, sem propagação | `tests/acceptance/test_us2_perfis.py::test_us2_replaces_profiles_without_affecting_other_edital`, `tests/integration/editais/test_perfis.py::test_profile_code_is_unique_only_inside_its_edital` | Coberto |
| FR-012 | Cadastro Reserva inexistente, limitado ou ilimitado | `tests/unit/editais/test_perfis.py::test_allows_limited_and_unlimited_reserve_without_immediate_vacancies`, `tests/unit/editais/test_perfis.py::test_rejects_incompatible_reserve_configuration`, `tests/integration/editais/test_perfis.py::test_database_rejects_incompatible_reserve_limit` | Coberto |
| FR-013 | Regra Normativa separada do resultado, com fundamento e vigência | `tests/unit/editais/test_perfis.py::test_rejects_duplicate_competition_modality_codes` | **Parcial** — ver L1 |
| FR-014 | Regras configuráveis não alteram retroativamente Publicações | `tests/integration/publicacoes/test_publicar_edital.py::test_database_trigger_rejects_publication_update` | **Parcial** — ver L1 |
| FR-015 | Cada Edital possui Cronograma próprio | `tests/acceptance/test_us3_cronograma.py::test_us3_keeps_schedules_independent`, `tests/integration/editais/test_cronograma.py::test_each_edital_has_an_independent_schedule` | Coberto |
| FR-016 | Evento admite data pontual ou período, ordem e situação | `tests/unit/editais/test_cronograma.py::test_accepts_point_and_period_events`, `tests/contract/test_cronograma_api.py::test_openapi_event_contract_supports_point_and_period` | Coberto |
| FR-017 | Validar início não posterior ao término e vínculo correto | `tests/unit/editais/test_cronograma.py::test_rejects_inverted_period`, `tests/integration/editais/test_cronograma.py::test_database_rejects_event_with_end_before_start`, `tests/acceptance/test_us3_cronograma.py::test_us3_rejects_inverted_period_without_partial_change` | Coberto |
| FR-018 | Alterar um Cronograma não altera os demais | `tests/acceptance/test_us3_cronograma.py::test_us3_keeps_schedules_independent`, `tests/integration/editais/test_cronograma.py::test_each_edital_has_an_independent_schedule` | Coberto |
| FR-019 | Validar completude e classificar achados por severidade | `tests/unit/editais/test_publicacao.py::test_blocking_findings_prevent_incomplete_edital`, `tests/unit/editais/test_publicacao.py::test_warning_does_not_make_complete_edital_invalid`, `tests/contract/test_edital_draft_api.py::test_submission_returns_warnings_so_the_responsible_can_decide` | Coberto |
| FR-020 | Erros impeditivos bloqueiam; avisos permanecem visíveis | `tests/contract/test_edital_draft_api.py::test_blocking_error_stops_submission_and_names_the_cause`, `tests/contract/test_edital_draft_api.py::test_submission_returns_warnings_so_the_responsible_can_decide` | Coberto |
| FR-021 | Autorização explícita e segregação de funções na publicação | `tests/authorization/test_publicacao.py::test_one_actor_cannot_prepare_homologate_and_publish`, `tests/authorization/test_foundation.py::test_missing_permission_is_denied` | Coberto |
| FR-022 | Publicação registra versão, responsável, Autoridade Signatária e instante | `tests/acceptance/test_us4_publicacao.py::test_us4_complete_publication_flow`, `tests/contract/test_publicacao_edital_api.py::test_openapi_has_explicit_publication_workflow_and_signatory`, `tests/contract/test_consulta_publica_api.py::test_publication_detail_matches_contract` | Coberto |
| FR-023 | Documento corresponde integralmente ao homologado, com integridade verificável | `tests/acceptance/test_us4_publicacao.py::test_us4_complete_publication_flow`, `tests/contract/test_consulta_publica_api.py::test_publication_detail_matches_contract` | **Parcial** — ver L2 |
| FR-024 | Publicação imutável, não substituível por operação comum | `tests/integration/publicacoes/test_publicar_edital.py::test_database_trigger_rejects_publication_update`, `tests/integration/test_database_permissions.py::test_trigger_rejects_mutation_even_for_a_privileged_role`, `tests/integration/test_database_permissions.py::test_runtime_role_has_no_update_or_delete_privilege` | Coberto |
| FR-025 | Preparar, revisar, homologar e publicar Retificações | `tests/acceptance/test_us5_retificacoes.py::test_us5_retification_flow`, `tests/integration/publicacoes/test_retificacoes.py::test_published_retification_preserves_original_and_creates_consolidated_version` | Coberto |
| FR-026 | Retificação altera qualquer conteúdo, identifica mudanças, vigência não retroativa | `tests/integration/publicacoes/test_retificacoes.py::test_retification_changes_vacancies_and_schedule_inside_snapshot_lists`, `tests/integration/publicacoes/test_retificacoes.py::test_retification_with_future_effective_date_materializes_version_at_that_boundary`, `tests/unit/publicacoes/test_consolidacao.py::test_retification_replaces_vacancies_inside_profile_list` | Coberto |
| FR-027 | Estados da Retificação; só a Publicação altera o vigente | `tests/authorization/test_consulta_publica.py::test_unpublished_retification_is_not_revealed_to_the_public`, `tests/acceptance/test_us5_retificacoes.py::test_us5_retification_flow` | Coberto |
| FR-028 | Versão consolidada por Publicação e por início de vigência | `tests/acceptance/test_us6_consulta_publica.py::test_us6_current_version_identifies_the_acts_that_compose_it`, `tests/integration/publicacoes/test_consulta_temporal.py::test_future_retification_only_takes_effect_from_its_declared_instant` | Coberto |
| FR-029 | Consultar vigente e conteúdo em data informada | `tests/integration/publicacoes/test_consulta_temporal.py::test_validity_starts_inclusively_at_the_boundary`, `tests/integration/publicacoes/test_consulta_temporal.py::test_no_version_was_in_force_before_the_first_publication`, `tests/acceptance/test_us6_consulta_publica.py::test_us6_past_instant_reproduces_the_version_then_in_force` | Coberto |
| FR-030 | Identificar o ato que produziu cada alteração, sem retroatividade | `tests/acceptance/test_us6_consulta_publica.py::test_us6_current_version_identifies_the_acts_that_compose_it`, `tests/integration/publicacoes/test_consulta_temporal.py::test_history_query_does_not_apply_later_rules_to_earlier_instants` | Coberto |
| FR-031 | Consulta pública só de conteúdo publicado; elaboração exige autorização | `tests/authorization/test_consulta_publica.py::test_public_consultation_needs_no_credentials`, `tests/authorization/test_consulta_publica.py::test_public_projection_never_exposes_elaboration_identifiers`, `tests/authorization/test_consulta_publica.py::test_public_projection_never_exposes_audit_trail` | Coberto |
| FR-032 | Auditoria com ator, ação, objeto, instante, estados e motivo | `tests/authorization/test_finalizacao.py::test_final_act_audits_actor_reason_and_state_transition`, `tests/authorization/test_auditoria_api.py::test_audit_query_returns_events_of_the_actor_scope`, `tests/integration/test_database_permissions.py::test_runtime_role_cannot_erase_the_audit_trail_it_wrote` | Coberto |
| FR-033 | Negar por padrão e impedir acesso por manipulação de identificador | `tests/authorization/test_foundation.py::test_anonymous_is_denied`, `tests/authorization/test_processos.py::test_cross_scope_process_is_not_revealed`, `tests/authorization/test_finalizacao.py::test_final_acts_do_not_cross_institutional_scope`, `tests/authorization/test_auditoria_api.py::test_audit_query_does_not_cross_institutional_scope` | Coberto |
| FR-034 | Cancelamento motivado e auditado; Processo bloqueado por Edital aberto | `tests/acceptance/test_us7_finalizacao.py::test_us7_cancelling_a_process_is_blocked_until_every_edital_is_final`, `tests/acceptance/test_us7_finalizacao.py::test_us7_cancelling_a_published_edital_preserves_its_publications`, `tests/unit/processos/test_finalizacao.py::test_cancelling_a_process_is_blocked_and_names_the_pending_editais` | Coberto |
| FR-035 | Desfecho impede transições incompatíveis, preservando consultas | `tests/acceptance/test_us7_finalizacao.py::test_us7_closed_process_keeps_history_and_rejects_incompatible_changes`, `tests/authorization/test_finalizacao.py::test_finalized_process_blocks_new_changes_to_its_editais`, `tests/unit/processos/test_finalizacao.py::test_final_process_rejects_further_changes_to_its_editais` | Coberto |
| FR-036 | Concorrência sem perda de atualização nem versão obsoleta | `tests/integration/test_foundation.py::test_compare_and_swap_rejects_stale_revision`, `tests/integration/publicacoes/test_publicar_edital.py::test_concurrent_publications_create_exactly_one`, `tests/integration/processos/test_finalizacao_concorrente.py::test_concurrent_cancellations_produce_exactly_one_act`, `tests/integration/publicacoes/test_retificacoes.py::test_stale_retification_revision_is_rejected` | Coberto |
| FR-037 | Confirmação antes de operação irreversível | — | **Diferido** (frontend) |
| FR-038 | Mensagens claras para validação, negação e consulta sem versão vigente | `tests/contract/test_openapi_conformance.py::test_problem_responses_conform_to_the_contract`, `tests/acceptance/test_us6_consulta_publica.py::test_us6_reports_absence_of_effective_version_without_substituting_the_current_one` | Coberto |
| FR-039 | Precedência por vigência, cumulativa, desempate pela última publicada | `tests/unit/publicacoes/test_consolidacao.py::test_future_effective_dates_compose_by_vigencia_not_by_publication_order`, `tests/unit/publicacoes/test_consolidacao.py::test_same_effective_time_accumulates_and_later_publication_wins_conflict`, `tests/integration/publicacoes/test_consulta_temporal.py::test_out_of_order_publications_compose_by_validity_not_by_publication_order` | Coberto |

## Cenários de aceitação

### US1 — Estruturar Processo Seletivo e Edital

| # | Cenário | Evidência | Situação |
|---|---|---|---|
| 1 | Criação conjunta com identidades distintas | `tests/integration/processos/test_creation.py::test_process_and_first_edital_are_atomic` | Coberto |
| 2 | Segundo Edital com situação e cronograma independentes | `tests/integration/processos/test_creation.py::test_second_edital_has_independent_identity_and_state` | Coberto |
| 3 | Dados ausentes ou identificação duplicada não deixam estrutura parcial | `tests/integration/processos/test_creation.py::test_missing_first_edital_creates_nothing`, `tests/integration/processos/test_creation.py::test_duplicate_identifier_leaves_no_partial_process` | Coberto |
| 4 | Ativação explícita e auditada, sem alterar os Editais | `tests/acceptance/test_us1_processos_editais.py::test_us1_create_add_and_activate` | Coberto |

### US2 — Configurar Perfis, Vagas e Concorrência

| # | Cenário | Evidência | Situação |
|---|---|---|---|
| 1 | Dois Perfis mantidos separadamente | `tests/acceptance/test_us2_perfis.py::test_us2_replaces_profiles_without_affecting_other_edital`, `tests/integration/editais/test_perfis.py::test_profile_code_is_unique_only_inside_its_edital` | Coberto |
| 2 | Cadastro Reserva ilimitado sem exigir vagas imediatas | `tests/unit/editais/test_perfis.py::test_allows_limited_and_unlimited_reserve_without_immediate_vacancies` | Coberto |
| 3 | Regra de Modalidade distinta do resultado, sem propagação | `tests/unit/editais/test_perfis.py::test_rejects_duplicate_competition_modality_codes` | **Parcial** — ver L1 |

### US3 — Definir Cronograma Independente

| # | Cenário | Evidência | Situação |
|---|---|---|---|
| 1 | Eventos pontuais e períodos na sequência definida | `tests/unit/editais/test_cronograma.py::test_accepts_point_and_period_events`, `tests/contract/test_cronograma_api.py::test_openapi_event_contract_supports_point_and_period` | Coberto |
| 2 | Cronogramas de dois Editais não interferem | `tests/acceptance/test_us3_cronograma.py::test_us3_keeps_schedules_independent` | Coberto |
| 3 | Período invertido rejeitado com explicação | `tests/acceptance/test_us3_cronograma.py::test_us3_rejects_inverted_period_without_partial_change`, `tests/integration/editais/test_cronograma.py::test_database_rejects_event_with_end_before_start` | Coberto |

### US4 — Validar e Publicar Edital

| # | Cenário | Evidência | Situação |
|---|---|---|---|
| 1 | Publicação registra versão, responsável, signatário e documento | `tests/acceptance/test_us4_publicacao.py::test_us4_complete_publication_flow` | Coberto |
| 2 | Erro impeditivo bloqueia e separa erros de avisos | `tests/contract/test_edital_draft_api.py::test_blocking_error_stops_submission_and_names_the_cause`, `tests/unit/editais/test_publicacao.py::test_warning_does_not_make_complete_edital_invalid` | Coberto |
| 3 | Alteração direta de versão publicada é rejeitada | `tests/integration/publicacoes/test_publicar_edital.py::test_database_trigger_rejects_publication_update` | Coberto |
| 4 | Documento consultado corresponde ao conteúdo homologado | `tests/acceptance/test_us4_publicacao.py::test_us4_complete_publication_flow` | **Parcial** — ver L2 |
| 5 | Uma pessoa não conclui sozinha elaboração, homologação e Publicação | `tests/authorization/test_publicacao.py::test_one_actor_cannot_prepare_homologate_and_publish` | Coberto |

### US5 — Retificar sem Reescrever o Passado

| # | Cenário | Evidência | Situação |
|---|---|---|---|
| 1 | Retificação altera Cronograma, Perfil e vagas, preservando a versão anterior | `tests/integration/publicacoes/test_retificacoes.py::test_retification_changes_vacancies_and_schedule_inside_snapshot_lists` | Coberto |
| 2 | Linha histórica com ordem, autoria, efeitos e consolidadas | `tests/acceptance/test_us6_consulta_publica.py::test_us6_anonymous_reaches_original_retifications_and_every_consolidated_version` | **Parcial** — ver L3 |
| 3 | Retificação não publicada não altera a versão pública | `tests/authorization/test_consulta_publica.py::test_unpublished_retification_is_not_revealed_to_the_public` | Coberto |
| 4 | Vigência futura só passa a vigorar na data declarada | `tests/integration/publicacoes/test_consulta_temporal.py::test_future_retification_only_takes_effect_from_its_declared_instant` | Coberto |
| 5 | Publicação fora da ordem de vigência compõe cumulativamente | `tests/integration/publicacoes/test_consulta_temporal.py::test_out_of_order_publications_compose_by_validity_not_by_publication_order` | Coberto |
| 6 | Vigências idênticas: prevalece a publicada por último no conflito | `tests/unit/publicacoes/test_consolidacao.py::test_same_effective_time_accumulates_and_later_publication_wins_conflict` | Coberto |

### US6 — Consultar Conteúdo Vigente e Histórico

| # | Cenário | Evidência | Situação |
|---|---|---|---|
| 1 | Versão vigente identifica os atos que a compõem | `tests/acceptance/test_us6_consulta_publica.py::test_us6_current_version_identifies_the_acts_that_compose_it` | Coberto |
| 2 | Consulta por data passada reproduz a versão de então | `tests/acceptance/test_us6_consulta_publica.py::test_us6_past_instant_reproduces_the_version_then_in_force` | Coberto |
| 3 | Público alcança original, Retificações e consolidadas, sem elaboração | `tests/acceptance/test_us6_consulta_publica.py::test_us6_anonymous_reaches_original_retifications_and_every_consolidated_version`, `tests/authorization/test_consulta_publica.py::test_public_projection_never_exposes_elaboration_identifiers` | Coberto |

### US7 — Cancelar ou Encerrar com Preservação

| # | Cenário | Evidência | Situação |
|---|---|---|---|
| 1 | Cancelar Edital publicado preserva Publicações e histórico | `tests/acceptance/test_us7_finalizacao.py::test_us7_cancelling_a_published_edital_preserves_its_publications` | Coberto |
| 2 | Processo encerrado mantém histórico e recusa alterações incompatíveis | `tests/acceptance/test_us7_finalizacao.py::test_us7_closed_process_keeps_history_and_rejects_incompatible_changes` | Coberto |
| 3 | Editais em estado final não encerram o Processo automaticamente | `tests/acceptance/test_us7_finalizacao.py::test_us7_process_keeps_its_status_until_an_explicit_act` | Coberto |
| 4 | Cancelamento do Processo bloqueado, identificando os Editais pendentes | `tests/acceptance/test_us7_finalizacao.py::test_us7_cancelling_a_process_is_blocked_until_every_edital_is_final` | Coberto |
| 5 | Encerramento regular não é tratado como cancelamento | `tests/acceptance/test_us7_finalizacao.py::test_us7_closing_an_edital_is_not_treated_as_cancellation` | Coberto |

## Critérios de Sucesso

| SC | Critério | Evidência | Situação |
|---|---|---|---|
| SC-001 | Todo Processo tem ao menos um Edital; todo Edital pertence a um Processo | `tests/integration/processos/test_creation.py::test_missing_first_edital_creates_nothing` | Coberto |
| SC-002 | Estruturação completa em até 15 minutos | — | **Diferido** (frontend) |
| SC-003 | Alterações em um Edital não modificam outro | `tests/acceptance/test_us3_cronograma.py::test_us3_keeps_schedules_independent`, `tests/acceptance/test_us2_perfis.py::test_us2_replaces_profiles_without_affecting_other_edital` | Coberto |
| SC-004 | Erro impeditivo sempre bloqueia; Publicação corresponde ao homologado | `tests/contract/test_edital_draft_api.py::test_blocking_error_stops_submission_and_names_the_cause`, `tests/acceptance/test_us4_publicacao.py::test_us4_complete_publication_flow` | Coberto |
| SC-005 | 20 Retificações: versão vigente e histórica em até 10 s por consulta | `tests/integration/publicacoes/test_consulta_temporal.py::test_twenty_retifications_recompose_every_requested_version` | Coberto |
| SC-006 | Edição ou exclusão de Publicação sempre rejeitada | `tests/integration/test_database_permissions.py::test_trigger_rejects_mutation_even_for_a_privileged_role`, `tests/integration/test_database_permissions.py::test_runtime_role_has_no_update_or_delete_privilege` | Coberto |
| SC-007 | Operações críticas produzem auditoria completa, sem dado sensível | `tests/authorization/test_finalizacao.py::test_final_act_audits_actor_reason_and_state_transition`, `tests/authorization/test_auditoria_api.py::test_audit_query_never_exposes_idempotency_keys_or_content` | Coberto |
| SC-008 | Operações sem permissão negadas; identificador não concede acesso | `tests/authorization/test_foundation.py::test_missing_permission_is_denied`, `tests/authorization/test_finalizacao.py::test_final_acts_do_not_cross_institutional_scope` | Coberto |
| SC-009 | 90% dos representantes concluem os fluxos na primeira tentativa | — | **Diferido** (frontend) |
| SC-010 | Fluxos críticos concluíveis por teclado | — | **Diferido** (frontend) |

## Lacunas conhecidas

### L1 — Regra Normativa sem cobertura própria (FR-013, FR-014, US2 cenário 3)

`RegraNormativa` persiste `foundation`, `version`, `percentage`, `calculation`, `rounding`,
`distribution`, `call_rules` e `effective_from`, e esses campos entram no snapshot canônico. Não há
teste que exija fundamento e vigência, nem que demonstre a separação entre a regra e o resultado de
sua aplicação. FR-014 fica coberto apenas de forma indireta, pela imutabilidade das Publicações.

O risco é baixo hoje, porque nenhum cálculo de cota é executado neste incremento — a feature
registra a regra sem aplicá-la. Ele cresce quando o módulo de classificação consumir essas regras.

**Recomendação**: testes de domínio exigindo `foundation` e `version`, e um teste demonstrando que
alterar uma `RegraNormativa` não altera nenhuma `VersaoConsolidada` já materializada.

### L2 — Documento publicado não reproduz o conteúdo normativo (FR-023, US4 cenário 4)

`render_edital_pdf` gera um PDF determinístico contendo apenas título, número/ano e o SHA-256 do
snapshot. Perfis, vagas, modalidades e Cronograma **não** são renderizados. FR-023 exige que o
documento corresponda integralmente aos dados estruturados e ao conteúdo editorial homologado, e a
Constituição exige que a cadeia "dados estruturados → versão homologada → PDF publicado" seja
demonstrável.

O que já está garantido: o PDF é determinístico, deriva do snapshot homologado, carrega o hash desse
snapshot e é imutável. O que falta é o conteúdo em si.

T057 previa "renderizador inicial", então a lacuna é conhecida, mas ela impede declarar FR-023
atendido. Enquanto existir, um Edital publicado não pode ser divulgado apenas pelo PDF.

**Recomendação**: tratar o renderizador completo como incremento próprio, com teste que extraia o
texto do PDF e confronte cada Perfil e Evento do snapshot homologado.

### L3 — Autoria não aparece na linha histórica pública (US5 cenário 2)

O cenário pede que a linha histórica apresente "ordem cronológica, autoria, efeitos e versões
consolidadas". A consulta pública entrega ordem, efeitos e versões, mas **não** a autoria: `published_by`
é omitido deliberadamente da projeção pública, e `tests/authorization/test_consulta_publica.py::test_public_projection_never_exposes_elaboration_identifiers`
verifica justamente essa omissão.

Isto é uma tensão real entre US5 cenário 2 e FR-031, que restringe a consulta pública ao conteúdo
"destinado à divulgação". A implementação optou por FR-031. A Autoridade Signatária **é** exposta em
`PublicacaoDetalheResponse`; o que se omite é o operador que executou a publicação.

**Recomendação**: decisão institucional explícita. Se a autoria operacional for informação pública,
US5 cenário 2 prevalece e a projeção deve incluí-la; se não for, o cenário deve ser reescrito para
dizer que a autoria consta da trilha administrativa, disponível em `GET /admin/auditoria`.

## Observações de conformidade

- **FR-020 corrigido durante esta tarefa.** A submissão calculava os achados de validação e o
  serializer os descartava, embora `EditalAdminResponse` já declarasse `validationFindings`. Os
  avisos agora acompanham a resposta, com severidade e caminho.
- **Contrato alterado em T090.** `kind` foi declarado nos três schemas do histórico e `provenance`
  em `VersaoConsolidadaResponse`. Ambos já eram devolvidos pela implementação de US6; a divergência
  foi detectada por `tests/contract/test_openapi_conformance.py::test_public_responses_conform_to_the_contract`.
- **Defeito aberto fora desta matriz.** Publicar uma Retificação cujo conteúdo consolidado é idêntico
  ao já publicado devolve HTTP 500 por colisão em `document_hash`, em vez de um Problem Details. Não
  afeta nenhum FR diretamente, mas viola a exigência de falhas diagnosticáveis sem exposição indevida.
