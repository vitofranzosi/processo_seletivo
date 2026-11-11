# Rastreabilidade: A publicação das convocações no GPS (148)

Cada requisito → a tarefa que o implementa → o teste que o verifica. Caminhos relativos a
`backend/tests/`. Abreviações:

- `ato` = `integration/convocacao/test_publicacao_de_convocados.py` — o ato, os efeitos, o prazo
- `int` = `interface/test_publicacao_de_convocados.py` — portal, área do candidato e gestão
- `vc` = `test_vocabulario_da_convocacao.py` — as telas e módulos novos na lista literal
- `ac` = `interface/test_acessibilidade.py` e `interface/test_folha_estatica.py` — classes e folhas
- `mi` = `migrations/test_migrations.py` e `seguranca/test_homologacao_preservada.py`
- `nav` = validação em navegador real, com as capturas em `capturas/` (ver [verificacao](verificacao.md))

A faixa abre em **FR-5401** e **SC-1701**, e gasta até FR-5436 e SC-1715. Nenhum `UX-` foi aberto.

## Os doze casos de validação do pedido

| Caso do pedido | Critério | Teste |
|---|---|---|
| 1 — convocação por e-mail, sem alterar o marco de prazo | SC-1701 | `ato::test_a_mensagem_enviada_entra_como_divulgacao_e_o_prazo_nao_muda` |
| 2 — publicação nativa como ato oficial | SC-1702 | `ato::test_a_publicacao_nativa_convoca_e_o_prazo_corre_dela` |
| 3 — publicação externa com referência registrada | SC-1703 | `ato::test_a_publicacao_externa_registrada_continua_e_a_relacao_a_cita` |
| 4 — múltiplas chamadas na mesma seleção | SC-1704 | `ato::test_a_suplente_chamada_depois_entra_na_2a_publicacao`, `nav` |
| 5 — uma chamada com diferentes vagas/listas | SC-1705 | `ato::test_uma_publicacao_com_duas_listas_tem_um_grupo_para_cada`, `nav` |
| 6 — convocação por sucessão | SC-1706 | `ato::test_a_suplente_chamada_depois_entra_na_2a_publicacao` |
| 7 — retificação após publicação | SC-1707 | `ato::test_a_correcao_de_convocacao_publicada_sai_marcada_na_seguinte`, `nav` |
| 8 — tentativa de publicação duplicada | SC-1708 | `ato::test_a_mesma_chave_devolve_o_mesmo_ato_e_outra_chave_e_recusada`, `ato::test_o_banco_recusa_a_mesma_convocacao_em_duas_publicacoes` |
| 9 — acesso público sem autenticação | SC-1709 | `int::test_a_secao_a_relacao_e_o_documento_abrem_sem_sessao` |
| 10 — proteção de informações pessoais | SC-1710 | `int::test_a_pagina_e_o_documento_nao_publicam_dado_pessoal_alem_dos_quatro` |
| 11 — compatibilidade com registros anteriores | SC-1711 | `int::test_sem_publicacao_a_selecao_nao_tem_a_secao`, `ato::test_a_publicacao_externa_registrada_continua_e_a_relacao_a_cita` |
| 12 — consistência entre página, PDF e área do candidato | SC-1712 | `int::test_pagina_documento_e_area_do_candidato_dizem_o_mesmo`, `nav` |

## Requisitos funcionais

| Requisito | Tarefa | Teste |
|---|---|---|
| FR-5401 | T003, T004, T005 | `ato::test_uma_publicacao_com_duas_listas_tem_um_grupo_para_cada`, `ato::test_a_suplente_chamada_depois_entra_na_2a_publicacao` |
| FR-5402 | T003, T005 | `ato::test_a_publicacao_nativa_convoca_e_o_prazo_corre_dela` |
| FR-5403 | T005, T014 | `ato::test_sem_a_declaracao_do_veiculo_a_publicacao_que_convoca_e_recusada`, `int::test_a_previa_da_gestao_nao_grava_e_o_formulario_publica` |
| FR-5404 | T003, T004 | `ato::test_vencimento_ja_passado_fica_fora_com_o_motivo` |
| FR-5405 | T003, T005 | `ato::test_a_mensagem_enviada_entra_como_divulgacao_e_o_prazo_nao_muda`, `ato::test_a_publicacao_externa_registrada_continua_e_a_relacao_a_cita` |
| FR-5406 | T003 | `ato::test_a_mensagem_que_nao_saiu_nao_entra_em_publicacao_nenhuma` |
| FR-5407 | T001, T002, T005 | `ato::test_a_mesma_chave_devolve_o_mesmo_ato_e_outra_chave_e_recusada`, `ato::test_o_banco_recusa_a_mesma_convocacao_em_duas_publicacoes` |
| FR-5408 | T003, T004, T005 | `ato::test_a_previa_mostra_o_que_seria_publicado_e_nao_grava_nada`, `ato::test_a_previa_que_envelheceu_e_recusada` |
| FR-5409 | T005 | `ato::test_a_publicacao_nativa_convoca_e_o_prazo_corre_dela` (signatário) |
| FR-5410 | T001, T002, T006 | `ato::test_as_tres_tabelas_recusam_alteracao_e_exclusao_no_banco`, `ato::test_o_gatilho_recusa_vinculo_com_comunicacao_que_nao_saiu`, `mi` |
| FR-5411 | T005 | `ato::test_a_publicacao_nativa_convoca_e_o_prazo_corre_dela` (trilha) |
| FR-5412 | T003, T006, T010 | `int::test_a_pagina_e_o_documento_nao_publicam_dado_pessoal_alem_dos_quatro` |
| FR-5413 | T005, T006, T010 | `int::test_pagina_documento_e_area_do_candidato_dizem_o_mesmo` |
| FR-5414 | T003 | `ato::test_uma_publicacao_com_duas_listas_tem_um_grupo_para_cada` |
| FR-5415 | T003, T006, T010 | `int::test_pagina_documento_e_area_do_candidato_dizem_o_mesmo` (prazo do grupo) |
| FR-5416 | T003, T010 | `int::test_a_secao_a_relacao_e_o_documento_abrem_sem_sessao` |
| FR-5417 | T003, T004 | `ato::test_a_correcao_de_convocacao_publicada_sai_marcada_na_seguinte` |
| FR-5418 | T010 | `int::test_a_secao_a_relacao_e_o_documento_abrem_sem_sessao`, `int::test_publicacao_inexistente_e_404` |
| FR-5419 | T009, T010 | `int::test_a_secao_a_relacao_e_o_documento_abrem_sem_sessao` (os bytes gravados) |
| FR-5420 | T009, T010 | `ato::test_a_correcao_de_convocacao_publicada_sai_marcada_na_seguinte`, `nav` |
| FR-5421 | T009, T011 | `int::test_a_secao_a_relacao_e_o_documento_abrem_sem_sessao`, `nav` |
| FR-5422 | T011 | `int::test_a_secao_a_relacao_e_o_documento_abrem_sem_sessao` |
| FR-5423 | T011 | `int::test_sem_publicacao_a_selecao_nao_tem_a_secao` |
| FR-5424 | T010, T011, T016 | `ac`, `nav` (375, 1280 e 1920 px) |
| FR-5425 | T012 | `int::test_pagina_documento_e_area_do_candidato_dizem_o_mesmo`, `nav` |
| FR-5426 | T012 | `int::test_pagina_documento_e_area_do_candidato_dizem_o_mesmo` |
| FR-5427 | T014 | `int::test_a_previa_da_gestao_nao_grava_e_o_formulario_publica` |
| FR-5428 | T014 | `int::test_a_previa_da_gestao_nao_grava_e_o_formulario_publica` |
| FR-5429 | T014 | `int::test_a_previa_da_gestao_nao_grava_e_o_formulario_publica` (o botão) |
| FR-5430 | T014 | `int::test_a_previa_da_gestao_nao_grava_e_o_formulario_publica`, `nav` |
| FR-5431 | T015 | `int::test_a_tela_do_recorte_leva_a_publicar_no_gps_e_mantem_o_registro_externo`, `nav` |
| FR-5432 | T014 | `int::test_a_pagina_de_publicacao_pede_identificacao` |
| FR-5433 | T018 | `ato::test_a_publicacao_externa_registrada_continua_e_a_relacao_a_cita` |
| FR-5434 | T015, T018 | `int::test_a_tela_do_recorte_leva_a_publicar_no_gps_e_mantem_o_registro_externo`, a suíte da `125` |
| FR-5435 | T018 | `ato::test_o_aviso_da_chamada_publicada_alcanca_a_publicacao_nativa`, `nav` |
| FR-5436 | T004, T009 | `int::test_a_pagina_publica_custa_o_mesmo_com_mais_gente`, `ato::test_uma_publicacao_com_duas_listas_tem_um_grupo_para_cada` |

## Critérios de sucesso

| Critério | Teste |
|---|---|
| SC-1701 | `ato::test_a_mensagem_enviada_entra_como_divulgacao_e_o_prazo_nao_muda` |
| SC-1702 | `ato::test_a_publicacao_nativa_convoca_e_o_prazo_corre_dela` |
| SC-1703 | `ato::test_a_publicacao_externa_registrada_continua_e_a_relacao_a_cita` |
| SC-1704 | `ato::test_a_suplente_chamada_depois_entra_na_2a_publicacao`, `nav` |
| SC-1705 | `ato::test_uma_publicacao_com_duas_listas_tem_um_grupo_para_cada` |
| SC-1706 | `ato::test_a_suplente_chamada_depois_entra_na_2a_publicacao` |
| SC-1707 | `ato::test_a_correcao_de_convocacao_publicada_sai_marcada_na_seguinte` |
| SC-1708 | `ato::test_a_mesma_chave_devolve_o_mesmo_ato_e_outra_chave_e_recusada`, `ato::test_o_banco_recusa_a_mesma_convocacao_em_duas_publicacoes` |
| SC-1709 | `int::test_a_secao_a_relacao_e_o_documento_abrem_sem_sessao`, `int::test_a_pagina_de_publicacao_pede_identificacao` |
| SC-1710 | `int::test_a_pagina_e_o_documento_nao_publicam_dado_pessoal_alem_dos_quatro` |
| SC-1711 | `int::test_sem_publicacao_a_selecao_nao_tem_a_secao` |
| SC-1712 | `int::test_pagina_documento_e_area_do_candidato_dizem_o_mesmo` |
| SC-1713 | `nav` — medido `scrollWidth == innerWidth` em 375, 1280 e 1920 px |
| SC-1714 | `ato::test_a_previa_mostra_o_que_seria_publicado_e_nao_grava_nada`, `int::test_a_previa_da_gestao_nao_grava_e_o_formulario_publica` |
| SC-1715 | `int::test_a_pagina_publica_custa_o_mesmo_com_mais_gente`, `ato::test_uma_publicacao_com_duas_listas_tem_um_grupo_para_cada` (a prévia com um e com dois recortes) |
