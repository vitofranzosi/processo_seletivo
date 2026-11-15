# Rastreabilidade: A habilitação do assistente do Edital pela interface

Cada requisito → a decisão → a tarefa → o teste que o verifica. Caminhos relativos a
`backend/tests/`:

- `HAB` é `integration/duvidas/test_habilitacao.py`;
- `AUT` é `authorization/test_habilitar_assistente.py`;
- `POR` é `portal/test_assistente_habilitado.py`;
- `PIL` é `interface/test_piloto_habilitado.py`;
- `TEL` é `interface/test_habilitacao_do_assistente.py`;
- `CFG` é `test_configuracao_producao.py`;
- `NAV` é `navegador/test_jornada_do_assistente.py`;
- `PRE` é `seguranca/test_homologacao_preservada.py`;
- `MIG` é `migrations/test_migrations.py`.

Os testes da `071` e da `074` que passam sem mudança são `interface/test_assistente.py`,
`interface/test_prototipo_do_assistente.py`, `portal/test_assistente_na_pagina.py` e
`integration/duvidas/test_exclusao.py`.

## Requisitos funcionais

| Requisito | Decisão | Tarefa | Verificado por |
|---|---|---|---|
| FR-7500 | D-001 | T005 | TEL `test_completa_a_pagina_nao_afirma_disponibilidade_e_nao_mostra_a_credencial` |
| FR-7501 | D-001, R-6 | T005 | HAB `test_sem_configuracao_completa_nao_habilita_e_diz_o_que_falta`; TEL `test_sem_servico_a_pagina_diz_o_que_falta_e_nao_oferece_habilitar` |
| FR-7502 | D-001 | T014 | TEL `test_completa_a_pagina_nao_afirma_disponibilidade_e_nao_mostra_a_credencial` (zero chamadas) |
| FR-7503 | D-001 | T012 | CFG `test_o_servico_local_em_producao_sobe_sem_o_atalho`; nenhuma recusa nova por configuração incompleta |
| FR-7504 | D-001 | T006 | HAB `test_sem_configuracao_completa_nao_habilita_e_diz_o_que_falta`, `test_desabilitar_nao_depende_da_configuracao`; as suítes da `071` e da `074` sem serviço |
| FR-7505 | D-005 | T012 | CFG `test_configuracao_insegura_impede_a_inicializacao` (serviço externo e tempo-limite sem o piloto) |
| FR-7506 | D-002 | T012 | CFG (caso `ASSISTENTE_PILOTO`); HAB `test_o_atalho_atende_sem_ato_fora_de_producao_e_nunca_em_producao` |
| FR-7507 | D-002 | — | CFG (caso `ASSISTENTE_NA_PAGINA_DO_EDITAL`); `portal/test_assistente_na_pagina.py` sem mudança |
| FR-7508 | D-002 | T009, T010 | HAB `test_habilitar_o_piloto_basta_fora_de_producao_sem_o_atalho`; POR e PIL com as duas chaves desligadas; NAV |
| FR-7509 | — | T011 | revisão: `avaliar_assistente` não confere mais a chave |
| FR-7510 | D-004 | T004 | AUT `test_a_grafia_da_permissao_e_a_mesma`, `test_nenhum_outro_papel_tem_a_permissao`; `seguranca/test_papel_institucional_administra_unidades.py` |
| FR-7511 | D-004, R-10 | T006, T014 | AUT `test_cada_caso_de_uso_recusa_sem_a_permissao`; TEL `test_a_demonstracao_e_recusada_e_nao_ve_o_item`, `test_o_administrador_de_acessos_da_unidade_e_recusado` |
| FR-7512 | D-004 | T004 | AUT `test_a_permissao_nao_da_o_uso_do_piloto` |
| FR-7513 | R-10 | T014, T015 | TEL `test_a_administradora_ve_o_item_ao_lado_de_unidades` |
| FR-7514 | D-003 | T006, T014 | HAB `test_habilitar_o_piloto_basta_fora_de_producao_sem_o_atalho`; TEL `test_habilitar_o_piloto_pela_tela_com_motivo`, `test_o_piloto_se_habilita_pela_tela_tambem_em_producao` |
| FR-7515 | D-003 | T009 | PIL `test_sem_ato_a_negativa_e_com_ato_quem_tem_o_papel_conversa` |
| FR-7516 | D-008 | T014 | TEL `test_habilitar_o_piloto_pela_tela_com_motivo` (a consequência diz "sessões acompanhadas") |
| FR-7517 | D-003 | T006 | HAB `test_a_pagina_publica_se_habilita_por_edital`, `test_edital_sem_pagina_publica_nao_se_habilita` |
| FR-7518 | D-005, R-4 | T006, T014 | HAB `test_em_producao_a_pagina_publica_e_recusada_nomeando_os_doze`; TEL `test_em_producao_a_tela_recusa_nomeando_os_requisitos` |
| FR-7519 | D-005 | T006, T010 | HAB `test_em_producao_o_ato_gravado_nao_abre_a_pagina`; POR `test_em_producao_o_ato_gravado_nao_abre_a_pagina`; PIL `test_a_pagina_do_edital_diz_se_a_pagina_publica_esta_aberta` |
| FR-7520 | D-003 | T010 | POR `test_o_edital_habilitado_oferece_o_painel_e_o_outro_nao`; NAV |
| FR-7521 | — | T010 | `portal/test_assistente_na_pagina.py` sem mudança (os mesmos envios e limites) |
| FR-7522 | — | T016 | PIL `test_a_pagina_do_edital_diz_se_a_pagina_publica_esta_aberta` |
| FR-7523 | D-006 | T006 | POR e PIL (a decisão nova vale na requisição seguinte) |
| FR-7524 | D-006, R-9 | T009, T010 | POR `test_desabilitado_no_meio_da_conversa_a_pergunta_seguinte_nao_chega_ao_modelo`, `test_quem_nunca_conversou_recebe_404_e_o_aviso_forjado_nao_aparece_com_o_painel`; PIL `test_desabilitado_a_pergunta_seguinte_recebe_a_negativa`; NAV |
| FR-7525 | D-006, R-5 | T009, T010 | HAB `test_habilitar_de_novo_muda_a_marca_da_conversa`; POR `test_habilitado_de_novo_a_conversa_recomeca_sem_o_historico`; PIL `test_habilitado_de_novo_a_conversa_recomeca` |
| FR-7526 | D-006 | T006 | HAB `test_desabilitar_e_ato_novo_e_o_estado_e_o_ultimo`; POR (a troca registrada continua) |
| FR-7527 | R-2 | T002, T003 | HAB `test_o_registro_recusa_alterar_e_excluir_no_banco`; PRE `test_as_tabelas_append_only_anteriores_continuam_todas`; MIG; `test_database_permissions.py` pela lista |
| FR-7528 | — | T006 | HAB `test_sem_motivo_recusa_e_nada_e_gravado`; TEL `test_habilitar_o_piloto_pela_tela_com_motivo` |
| FR-7529 | R-8 | T006, T007 | HAB `test_o_ato_vai_a_trilha_com_o_motivo_e_a_situacao`, `test_o_ato_do_edital_vai_a_trilha_da_unidade`; NAV |
| FR-7530 | — | T006 | HAB `test_o_ato_que_nao_muda_nada_e_recusado`; TEL `test_o_estado_mudado_recusa_a_confirmacao` |
| FR-7531 | R-3 | T006 | TEL `test_o_estado_mudado_recusa_a_confirmacao` (a reconferência); a trava consultiva, por revisão |
| FR-7532 | R-2 | T006, T014 | HAB `test_desabilitar_e_ato_novo_e_o_estado_e_o_ultimo`; TEL `test_habilitar_o_piloto_pela_tela_com_motivo` (o histórico com nome e motivo) |
| FR-7533 | D-005 | T001 | HAB `test_em_producao_a_pagina_publica_e_recusada_nomeando_os_doze`; TEL `test_em_producao_a_tela_recusa_nomeando_os_requisitos` |
| FR-7534 | D-007 | — | `integration/duvidas/test_exclusao.py` sem mudança |
| FR-7535 | D-007 | — | POR `test_em_producao_o_ato_gravado_nao_abre_a_pagina` (nada gravado em produção); `portal/test_assistente_na_pagina.py` sem mudança |
| FR-7536 | — | T019 | revisão da documentação |
| FR-7537 | — | T019 | revisão das notas na `071` e na `074` |

## Requisitos de experiência

| Requisito | Tarefa | Verificado por |
|---|---|---|
| UX-810 | T014 | TEL `test_sem_servico_a_pagina_diz_o_que_falta_e_nao_oferece_habilitar` |
| UX-811 | T014 | TEL `test_em_producao_a_tela_recusa_nomeando_os_requisitos` |
| UX-812 | T014 | TEL `test_habilitar_o_piloto_pela_tela_com_motivo`, `test_habilitar_e_desabilitar_um_edital_pela_tela` |
| UX-813 | T010 | POR `test_desabilitado_no_meio_da_conversa_a_pergunta_seguinte_nao_chega_ao_modelo`; NAV |
| UX-814 | T016 | PIL `test_a_pagina_do_edital_diz_se_a_pagina_publica_esta_aberta` |

## Critérios de sucesso

| Critério | Verificado por |
|---|---|
| SC-2450 | TEL `test_sem_servico_a_pagina_diz_o_que_falta_e_nao_oferece_habilitar`, `test_completa_a_pagina_nao_afirma_disponibilidade_e_nao_mostra_a_credencial` |
| SC-2451 | NAV `test_habilitar_conversar_e_desabilitar` |
| SC-2452 | HAB `test_o_registro_recusa_alterar_e_excluir_no_banco`, `test_o_ato_vai_a_trilha_com_o_motivo_e_a_situacao` |
| SC-2453 | HAB e POR (em produção); TEL `test_em_producao_a_tela_recusa_nomeando_os_requisitos`; CFG |
| SC-2454 | AUT `test_cada_caso_de_uso_recusa_sem_a_permissao`; TEL |
| SC-2455 | as suítes da `071` e da `074` sem mudança de comportamento |
| SC-2456 | POR `test_habilitado_de_novo_a_conversa_recomeca_sem_o_historico` |
| SC-2457 | humano: a demonstração do quickstart, roteiro C |
