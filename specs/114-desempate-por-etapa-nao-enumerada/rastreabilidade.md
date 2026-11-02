# Rastreabilidade: Desempate pela nota de Etapa que o marco não enumera

Cada requisito → a tarefa que o implementa → o teste que o verifica. As tarefas estão em
[tasks.md](tasks.md); os caminhos de teste são relativos a `backend/tests/`. Abreviações:
`a11` = `integration/classificacao/test_desempate_por_etapa_nao_enumerada.py`; `universo` =
`unit/classificacao/test_universo_classificavel.py`; `ato` =
`integration/classificacao/test_imutabilidade_do_ato.py`; `equivalencia` =
`integration/classificacao/test_previa_equivale_ao_oficial.py`.

| Requisitos | Tarefas | Testes |
|---|---|---|
| FR-3546 (o critério compara a nota da Etapa citada, enumerada ou não) | T002, T004, T005 | `a11::test_a_nota_de_etapa_nao_enumerada_desfaz_o_empate`; `universo::test_a_nota_da_etapa_do_desempate_chega_ao_desempate_e_nao_a_nota_final`; `unit/classificacao/test_desempate.py::test_etapas_do_desempate_sao_as_comparadas_e_nao_enumeradas` |
| FR-3547 (a nota não entra na combinada nem no motivo de ausência) | T005 | `a11::test_a_nota_de_etapa_nao_enumerada_desfaz_o_empate`; `universo::test_a_nota_da_etapa_do_desempate_chega_ao_desempate_e_nao_a_nota_final`, `::test_sem_nota_na_etapa_do_desempate_o_motivo_de_ausencia_nao_a_cita` |
| FR-3548 (a eliminação na Etapa do desempate não tira da ordem) | T005, T008, T009 | `a11::test_eliminado_na_entrevista_continua_classificado_pela_prova`; `universo::test_eliminacao_na_etapa_do_desempate_nao_tira_da_ordem` |
| FR-3549 (os Resultados lidos entram no universo) | T004, T006 | `a11::test_o_ato_cita_a_nota_que_desempatou_e_se_reproduz` |
| FR-3550 (Resultado novo ou sucessor obsoleta a ordem) | T011, T020, T021 | `a11::test_a_nota_que_chega_depois_obsoleta_a_ordem`, `::test_recurso_deferido_na_entrevista_obsoleta_a_ordem_e_a_sucessora_inverte` (os dois conferem também o filtro da Supervisão e da condução do marco; sem a correção de `candidato_a_obsoleto`, falham — conferido em 02/11), `::test_recurso_deferido_na_entrevista_obsoleta_o_corte_que_leu_a_ordem` |
| FR-3551 (a conferência no banco aceita a Etapa citada, e só ela) | T003, T012 | `ato::test_a_trigger_aceita_resultado_da_etapa_que_o_criterio_compara`, `::test_a_trigger_continua_recusando_etapa_que_nem_se_enumera_nem_se_compara`, `::test_a_trigger_recusa_resultado_real_de_etapa_nao_enumerada` (inalterado); `migrations/test_migrations.py` (contagem e reversão) |
| FR-3552 (a reprodução devolve as posições do ato) | T010, T013 | `a11::test_o_ato_cita_a_nota_que_desempatou_e_se_reproduz`, `::test_eliminado_na_entrevista_continua_classificado_pela_prova`, `::test_recurso_deferido_na_entrevista_obsoleta_a_ordem_e_a_sucessora_inverte`; `unit/classificacao/test_reproducao.py` (inalterado, atos anteriores) |
| FR-3553 (sem Resultado, vale o "quando o valor falta"; a emissão sai) | T008 | `a11::test_sem_nota_na_entrevista_vale_o_quando_falta_e_a_ordem_sai`, `::test_a_nota_que_chega_depois_obsoleta_a_ordem` |
| FR-3554 (a proveniência grava a nota comparada) | T006 | `a11::test_o_ato_cita_a_nota_que_desempatou_e_se_reproduz` |
| FR-3555 (a prévia dá nota fictícia na Etapa do desempate) | T014, T016 | `unit/classificacao/test_cenarios_da_previa.py::test_a_nota_do_desempate_acompanha_os_empates_plantados`, `::test_etapa_decisoria_do_desempate_nao_recebe_nota` |
| FR-3556 (equivalência verificada com a Etapa do desempate) | T015 | `equivalencia::test_a_previa_e_o_oficial_concordam_desempatando_por_etapa_nao_enumerada` (conferido em 02/11: com o filtro antigo do cálculo, os dois casos falham) |
| FR-3557 (marco sem o critério não muda) | T017 | `equivalencia` inteiro, com as tabelas absolutas inalteradas; `integration/classificacao/test_ordem_sem_reserva_nao_muda.py` |
| SC-1073 | T006 | `a11::test_a_nota_de_etapa_nao_enumerada_desfaz_o_empate`, sem `xfail` |
| SC-1074 | T008 | `a11::test_eliminado_na_entrevista_continua_classificado_pela_prova` |
| SC-1075 | T011 | `a11::test_recurso_deferido_na_entrevista_obsoleta_a_ordem_e_a_sucessora_inverte` |
| SC-1076 | T015 | `equivalencia::test_a_previa_e_o_caminho_oficial_concordam` e `::test_a_previa_e_o_oficial_concordam_desempatando_por_etapa_nao_enumerada` |
| SC-1077 | T017 | `equivalencia::test_a_ordem_com_criterios_eliminacao_e_ausencia_e_a_da_tabela`, `::test_cada_recorte_tem_o_universo_e_a_ordem_da_tabela`, sem edição das tabelas |
