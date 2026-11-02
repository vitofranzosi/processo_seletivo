# Rastreabilidade: Encerramento seguro do Edital

Cada requisito → a tarefa que o implementa → o teste que o verifica. As tarefas estão em
[tasks.md](tasks.md); os caminhos de teste são relativos a `backend/tests/`. Abreviações:
`pendencias` = `unit/processos/test_pendencias_do_edital.py`; `seguro` =
`integration/processos/test_encerramento_seguro.py`; `concorrente` =
`integration/processos/test_encerramento_concorrente.py`; `confirmacao` =
`interface/test_confirmacao_do_encerramento.py`.

| Requisitos | Tarefas | Testes |
|---|---|---|
| FR-3528 (recusa com a lista, sem gravar nada; tela e serviço) | T012, T013, T015 | `seguro::test_recurso_aguardando_impede_e_julgado_libera` (e os demais de `seguro`, pelo `recusa`, que compara situação, revisão, ato e trilha); `contract/test_finalizacao_api.py::test_closing_with_an_impediment_is_a_conflict_listing_it`; `confirmacao::test_o_post_com_impedimento_devolve_409_com_a_lista_de_agora` |
| FR-3529 (período com término em curso ou por abrir; sem término não impede) | T011 | `pendencias::test_periodo_em_curso_com_termino_impede_e_diz_ate_quando`, `::test_periodo_por_abrir_impede`, `::test_periodo_sem_termino_so_adverte`; `seguro::test_periodo_com_termino_em_curso_impede`, `::test_periodo_por_abrir_impede` |
| FR-3530 (prazo recursal declarado e computável em curso) | T003, T011 | `pendencias::test_prazo_declarado_em_curso_impede_e_some_quando_fecha`, `::test_marco_que_nao_admite_recurso_nao_impede_nem_adverte`, `::test_sem_resultado_divulgado_nao_ha_prazo`; `seguro::test_prazo_recursal_em_curso_impede` |
| FR-3531 (recurso aguardando admissibilidade ou julgamento) | T002, T011 | `pendencias::test_recurso_admitido_sem_decisao_impede`, `::test_recurso_sem_juizo_tambem_impede`, `::test_recurso_indeferido_deixa_de_impedir` |
| FR-3532 (reavaliação ou providência pendente) | T004, T011 | `pendencias::test_reavaliacao_determinada_passa_a_impedir_no_lugar_do_recurso`, `::test_providencia_determinada_impede`; `seguro::test_reavaliacao_pendente_impede` |
| FR-3533 (Retificação homologada) | T011 | `pendencias::test_homologada_impede_e_as_em_curso_so_advertem`, `::test_duas_homologadas_sao_dois_impedimentos`; `seguro::test_retificacao_homologada_impede_e_publicada_libera` |
| FR-3534 (as advertências) | T019, T020 | `pendencias::test_periodo_sem_termino_so_adverte`, `::test_prazo_nao_declarado_so_adverte`, `::test_homologada_impede_e_as_em_curso_so_advertem`; `seguro::test_o_que_so_se_adverte_nao_impede`; `confirmacao::test_sem_impedimento_as_advertencias_vem_a_parte_e_o_confirmar_aparece` |
| FR-3535 (a mesma regra da `099`) | T004, T020 | `confirmacao::test_toda_providencia_do_relatorio_depois_do_ato_foi_dita_antes`; a `099` inalterada (`unit/interface/test_relatorio_do_edital.py`, `interface/test_relatorio.py`) |
| FR-3536 (cancelar nunca recusa; "Serão atingidos") | T013, T024 | `seguro::test_cancelar_e_aceito_com_tudo_junto`; `pendencias::test_no_cancelamento_tudo_e_advertencia`; `confirmacao::test_cancelar_lista_o_que_sera_atingido_e_deixa_confirmar` |
| FR-3537 (impedimentos antes, sem confirmar) | T015, T016 | `confirmacao::test_recurso_aguardando_impede_e_o_gestor_ve_a_contagem_e_a_quem_pedir` |
| FR-3538 (caminho só a quem a tela aceita) | T014 | `confirmacao::test_recurso_aguardando_impede_e_o_gestor_ve_a_contagem_e_a_quem_pedir`, `::test_quem_julga_recebe_o_caminho_ate_os_recursos`, `::test_periodo_em_curso_oferece_retificar_so_a_quem_retifica` |
| FR-3539 (advertências à parte) | T021 | `confirmacao::test_sem_impedimento_as_advertencias_vem_a_parte_e_o_confirmar_aparece` |
| FR-3540 (sem dado pessoal) | T014, T020 | `confirmacao::test_nenhum_dado_pessoal_na_confirmacao` |
| FR-3541 ("Nenhuma pendência registrada no GPS…") | T021 | `confirmacao::test_sem_nada_a_dizer_a_frase_e_a_do_gps` |
| FR-3542 (consequências sem "conclusão regular") | T022 | `confirmacao::test_as_consequencias_nao_afirmam_conclusao` |
| FR-3543 (no instante do ato; concorrência; reexibe a lista) | T013, T015 | `concorrente::test_recurso_confirmado_antes_do_encerramento_o_impede` (falha sem a trava do Processo, conferido em 01/11); `confirmacao::test_o_post_com_impedimento_devolve_409_com_a_lista_de_agora` |
| FR-3544 (Retificação parada) | T026 | `interface/test_retificacao_parada.py::test_encerrado_com_retificacao_em_elaboracao_e_em_revisao`, `::test_cancelado_com_retificacao_homologada`, `::test_com_o_edital_publicado_o_proximo_passo_continua` |
| FR-3545 (nada posterior muda; A-09 intacto; Processo intacto) | T008, T027, T029 | `concorrente::test_encerramento_confirmado_antes_nao_e_desfeito_pelo_que_vem_depois`; `integration/publicacoes/test_retificacao_de_edital_encerrado.py` (inteiro, com `tests/fixtures/encerramento.py`); `acceptance/test_us7_finalizacao.py` (inalterado) |
| SC-1067 (cada impedimento recusa, sem mudança) | T007, T009, T010 | os seis primeiros de `seguro`; `contract/test_finalizacao_api.py::test_closing_with_an_impediment_is_a_conflict_listing_it` |
| SC-1068 (cancelamento com tudo junto) | T023 | `seguro::test_cancelar_e_aceito_com_tudo_junto` |
| SC-1069 (providências do relatório exibidas antes) | T018 | `confirmacao::test_toda_providencia_do_relatorio_depois_do_ato_foi_dita_antes` |
| SC-1070 (concorrência) | T008 | `concorrente::test_recurso_confirmado_antes_do_encerramento_o_impede` |
| SC-1071 (contagem a quem não julga; sem dado pessoal) | T010, T017 | `confirmacao::test_recurso_aguardando_impede_e_o_gestor_ve_a_contagem_e_a_quem_pedir`, `::test_nenhum_dado_pessoal_na_confirmacao` |
| SC-1072 (< 1 s com 400 inscrições) | T017, T030 | `performance/test_confirmacao_do_encerramento.py::test_o_numero_de_consultas_nao_cresce_com_as_inscricoes` (23 consultas com 38 e com 362); a medição isolada em [verificacao.md](verificacao.md) |

## Casos-limite

| Caso-limite | Tarefa | Teste |
|---|---|---|
| Sem período designado | T011 | `pendencias::test_sem_periodo_designado_nao_impede`; `confirmacao::test_sem_nada_a_dizer_a_frase_e_a_do_gps` |
| Período cancelado por Retificação | T011 | `pendencias::test_periodo_cancelado_nao_impede_quaisquer_que_sejam_as_datas` |
| Período sem término declarado (D-008) | T011, T019 | `pendencias::test_periodo_sem_termino_so_adverte` |
| Período encerrado | T011 | `pendencias::test_periodo_encerrado_nao_impede` |
| Período prorrogado (vale o vigente) | T011 | por construção: `situacoes` lê `effective_version` no instante do ato |
| Retificação homologada com vigência futura | T011 | por construção: o filtro é só a situação da Retificação |
| Várias Retificações em curso | T011, T019 | `pendencias::test_homologada_impede_e_as_em_curso_so_advertem`, `::test_duas_homologadas_sao_dois_impedimentos` |
| Marco que não admite recurso | T011 | `pendencias::test_marco_que_nao_admite_recurso_nao_impede_nem_adverte` |
| Prazo de recurso não declarado ou não computável (D-002) | T011, T019 | `pendencias::test_prazo_nao_declarado_so_adverte` |
| Recurso não admitido ou decidido | T011 | `pendencias::test_recurso_indeferido_deixa_de_impedir` |
| Recurso julgado com reavaliação determinada | T011 | `pendencias::test_reavaliacao_determinada_passa_a_impedir_no_lugar_do_recurso` |
| Ato concorrente entre abrir a tela e confirmar | T013 | `concorrente::test_recurso_confirmado_antes_do_encerramento_o_impede`; `confirmacao::test_o_post_com_impedimento_devolve_409_com_a_lista_de_agora` |
| Rascunho com o período encerrado (D-007) | T011 | por construção: `_dos_rascunhos` só conta com o período aberto, e só no cancelamento |
| Quem encerra sem permissão de julgar | T014 | `confirmacao::test_recurso_aguardando_impede_e_o_gestor_ve_a_contagem_e_a_quem_pedir` |
| Repetição do pedido já concluído | T013 | `seguro::test_repetir_o_pedido_concluido_devolve_o_ato_sem_reconferir` |
| Edital ainda não publicado | — | inalterado: `acceptance/test_us7_finalizacao.py`; `encerramento.da_confirmacao` devolve vazio |
