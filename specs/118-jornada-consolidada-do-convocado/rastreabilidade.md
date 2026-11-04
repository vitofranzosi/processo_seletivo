# Rastreabilidade: A jornada consolidada do candidato convocado (118)

Cada requisito → a tarefa que o implementa → o teste que o verifica. Caminhos de teste relativos a
`backend/tests/`. Abreviações:

- `ob` = `unit/portal/test_obrigacoes_da_convocacao.py` — a projeção pura
- `si` = `unit/portal/test_situacao_da_inscricao.py` — a ação do acompanhamento
- `jc` = `interface/test_portal_jornada_consolidada.py` — as telas, por cenário
- `nv` = `navegador/test_jornada_consolidada_do_convocado.py` — Chromium, 375 px e desktop
- `dc` = `interface/test_portal_documentos_da_convocacao.py`
- `cc` = `interface/test_portal_caminho_da_convocacao.py`
- `pc` = `integration/requerimentos/test_prazo_da_chamada.py`
- `id` = `integration/convocacao/test_documentos_da_convocacao.py`
- `vd` = `test_vocabulario_dos_documentos_da_convocacao.py`
- `vr` = `test_vocabulario_do_requerimento.py`
- `vc` = `test_vocabulario_da_convocacao.py`
- `sm` = `test_situacoes_de_mensagem.py`

As letras entre parênteses são os cenários do plano (A–K, B2, L, M, N, K2, G0, N0, M0).

## Requisitos funcionais

| Requisito | Tarefas | Testes |
|---|---|---|
| FR-3721 (projeção derivada, sem relógio nem banco; a causa do fechamento, com o Processo antes do prazo) | T008, T010 | `ob::test_a_projecao_nao_consulta_o_banco`, `::test_processo_e_prazo_juntos_vale_o_processo`, `::test_sem_item_pedido_nao_ha_projecao`; `jc::test_m_o_processo_encerrado_nao_diz_prazo_vencido_nem_promete_conferencia` (M) |
| FR-3722 (o momento e exatamente uma categoria por item) | T008 | `ob::test_cada_item_cai_em_exatamente_uma_categoria` (10 estados × 2 situações × 4 momentos), `::test_a_categoria_nao_muda_com_o_momento`, `::test_o_desfecho_com_o_processo_aberto_nao_reabre_a_escrita` |
| FR-3723 (o facultativo fora das contagens, e sempre alcançável) | T008, T019 | `ob::test_o_facultativo_fica_fora_dos_totais_e_da_frase`; `jc::test_l_o_opcional_se_envia_sem_tarefa_nenhuma` (L) |
| FR-3724 (o que está com a comissão não é tarefa; o aproveitado não é reenviado nem atendido) | T008, T020 | `ob::test_o_texto_de_cada_celula`, `::test_o_processo_nao_diz_prazo_vencido_nem_promete_conferencia`; `jc::test_d_o_aproveitado_nao_parece_pronto_nem_reenviado` (D) |
| FR-3725 (as sete linhas do Requerimento, a exigência e a situação antes da disponibilidade) | T008, T010 | `ob::test_as_sete_linhas_do_requerimento` (13 casos, com 3a), `::test_o_pedido_e_nao_enviado_nunca_vira_nao_pedido_depois_do_desfecho`, `::test_o_processo_nao_alcanca_o_requerimento_na_inscricao`, `::test_o_requerimento_so_e_tarefa_com_a_chamada_aberta`; `jc::test_n_o_pedido_e_nunca_enviado_aparece_como_nao_enviado` (N) |
| FR-3726 (a ordem do candidato: pendência, o que falta, o Requerimento) | T008 | `ob::test_a_ordem_e_pendencia_depois_o_que_falta_depois_o_requerimento`; `jc::test_f_a_pendencia_vem_primeiro_com_o_motivo_e_o_selo` (F) |
| FR-3727 (os totais, só de obrigatórios) | T008 | `ob::test_o_facultativo_fica_fora_dos_totais_e_da_frase`, `::test_a_ordem_e_pendencia_depois_o_que_falta_depois_o_requerimento` |
| FR-3728 (a frase de conclusão, e a do opcional) | T008 | `ob::test_a_frase_de_conclusao_com_e_sem_opcional`, `::test_com_tarefa_nao_ha_frase_de_conclusao`, `::test_nenhuma_frase_afirma_o_que_ninguem_decidiu`; `jc::test_e_enviados_aguardando_nada_por_enquanto_e_a_frase_de_conclusao` (E), `::test_l_o_opcional_se_envia_sem_tarefa_nenhuma` (L) |
| FR-3729 (a projeção não decide nada) | T008 | `ob::test_a_categoria_nao_muda_com_o_momento`, `::test_o_desfecho_com_o_processo_aberto_nao_reabre_a_escrita`, `::test_nenhuma_frase_afirma_o_que_ninguem_decidiu` |
| FR-3730 (a ação com documento, as cinco linhas, o link sempre à convocação) | T013, T014 | `si::TestAcaoComDocumento` (linhas 1 a 5, `test_nenhum_rotulo_de_link_que_navega_comeca_por_enviar`); `jc::test_c1_e_c2_o_acompanhamento_representa_o_conjunto` (C1, C2), `::test_g_o_prazo_terminou_com_o_resumo_e_o_requerimento` (G), `::test_m_o_processo_encerrado_nao_diz_prazo_vencido_nem_promete_conferencia` (M) |
| FR-3731 (o Requerimento enviado como linha secundária) | T013, T015 | `si::TestAcaoComDocumento::test_c2_o_enviado_nunca_e_a_acao_principal`, `::test_linha_5_sem_tarefa_a_frase_de_conclusao`; `jc::test_c1_e_c2_o_acompanhamento_representa_o_conjunto` (C2) |
| FR-3732 (sem documento, a ação de hoje; a linha estritamente informativa) | T013 | `si::TestSemDocumentoComoHoje` (B, B2, G0, N0, M0, com e sem rascunho); `jc::test_b_e_b2_sem_documento_ficam_como_hoje` (B, B2), `::test_sem_documento_o_requerimento_nao_enviado_e_dito_sem_acao` (G0, N0, M0) |
| FR-3733 (encerrada, o que ficou sem envio, sem convite) | T013, T026 | `si::TestAcaoComDocumento::test_linha_2_processo_sem_prazo_vencido_nem_conferencia`, `::test_linha_3_prazo_usa_o_nucleo`; `jc::test_g_o_prazo_terminou_com_o_resumo_e_o_requerimento` (G) |
| FR-3734 (nenhuma consulta sem convocação; número fixo com ela) | T014 | `jc::test_sem_convocacao_o_acompanhamento_nao_le_documentos_da_convocacao`, `::test_as_duas_telas_custam_o_mesmo_com_um_e_com_seis_itens`; medida antes/depois em `verificacao.md` |
| FR-3735 (os cinco blocos, nesta ordem; 3 e 4 nunca vazios) | T019 | `jc::test_c1_e_c2_o_acompanhamento_representa_o_conjunto`, `::test_l_o_opcional_se_envia_sem_tarefa_nenhuma` (L), `::test_e_enviados_aguardando_nada_por_enquanto_e_a_frase_de_conclusao` (E) |
| FR-3736 (o bloco "O que fazer agora": frase, tarefas com âncora, um botão que não diz "Enviar") | T019, T022 | `jc::test_c1_e_c2_o_acompanhamento_representa_o_conjunto` (C1), `::test_f_a_pendencia_vem_primeiro_com_o_motivo_e_o_selo` (F), `::test_j_a_pendencia_sem_envio_diz_envie_o_arquivo` (J); `nv::test_cada_cenario_nas_duas_larguras` (primeira tela), `::test_f_pelo_teclado_a_ordem_e_a_visual_e_o_foco_se_ve` (âncora leva o foco) |
| FR-3737 (o bloco "Prazo") | T019, T028 | `ob::test_sem_prazo_correndo_nenhuma_frase_diz_ate`; `jc::test_k_e_k2_nenhuma_data_aparece_como_prazo` (K, K2) |
| FR-3738 (o bloco "O que falta", com os opcionais sob "Opcional") | T019, T020 | `jc::test_l_o_opcional_se_envia_sem_tarefa_nenhuma` (L); `nv::test_cada_cenario_nas_duas_larguras` (K2) |
| FR-3739 (o bloco "O que você já apresentou", com o envio de outro arquivo recolhido) | T019, T020 | `jc::test_f_a_pendencia_vem_primeiro_com_o_motivo_e_o_selo` (F), `::test_l_o_opcional_se_envia_sem_tarefa_nenhuma` (L), `::test_c1_e_c2_o_acompanhamento_representa_o_conjunto` (C2) |
| FR-3740 (os dados do ato, visíveis, no fim) | T019 | `jc::test_k_e_k2_nenhuma_data_aparece_como_prazo` (a data só em "Sobre esta convocação") |
| FR-3741 (encerrada, por causa: o prazo ou o Processo; nenhum formulário) | T026 | `ob::test_o_vencido_usa_o_nucleo_e_inclui_o_requerimento_no_resumo`, `::test_o_processo_nao_diz_prazo_vencido_nem_promete_conferencia`; `jc::test_g_o_prazo_terminou_com_o_resumo_e_o_requerimento` (G), `::test_m_o_processo_encerrado_nao_diz_prazo_vencido_nem_promete_conferencia` (M) |
| FR-3742 (decidida, só histórico) | T026 | `ob::test_decidida_sem_aguardando_nem_convite`; `jc::test_i_depois_do_resultado_a_pagina_e_so_historico` (I1, I2), `::test_n_o_pedido_e_nunca_enviado_aparece_como_nao_enviado` (N) |
| FR-3743 (sem documento, a estrutura de hoje com o texto comum) | T019, T026 | `jc::test_b_e_b2_sem_documento_ficam_como_hoje`, `::test_sem_documento_e_sem_requerimento_a_instrucao_neutra`, `::test_sem_documento_o_requerimento_nao_enviado_e_dito_sem_acao`; `dc::test_sem_documento_na_convocacao_a_tela_e_a_de_antes` |
| FR-3744 (o selo em texto, o destaque do pendente, o marcador que não é botão de opção) | T020, T021 | `jc::test_f_a_pendencia_vem_primeiro_com_o_motivo_e_o_selo` (F), `::test_j_a_pendencia_sem_envio_diz_envie_o_arquivo` (J); `ob::test_o_facultativo_recebido_usa_a_linha_do_estado_com_o_selo`; `interface/test_acessibilidade.py::test_nenhuma_classe_citada_deixa_de_existir_na_folha` |
| FR-3745 (título por cartão, nomes acessíveis, descrição com a situação, Tab e foco) | T020 | `jc::test_f_cada_botao_diz_o_nome_do_documento`; `nv::test_f_pelo_teclado_a_ordem_e_a_visual_e_o_foco_se_ve`, `::test_cada_cenario_nas_duas_larguras` (nomes únicos) |
| FR-3746 (o texto de cada célula, nas quatro colunas) | T008, T018 | `ob::test_o_texto_de_cada_celula` (13 linhas × 4 colunas), `::test_sem_prazo_correndo_nenhuma_frase_diz_ate`; `dc::test_a_convocada_envia_pelo_portal_e_le_o_resultado`, `::test_o_certificado_da_inscricao_aparece_atendido`, `::test_a_pendencia_sobre_o_que_nao_chegou_mostra_o_motivo` |
| FR-3747 (um formato de prazo) | T028 | `ob::test_o_formato_do_prazo_e_um_so`; `cc::TestAcompanhamento::test_a_secao_mostra_a_chamada_o_prazo_e_o_caminho`, `::test_a_sucessora_ocupa_o_lugar_da_sucedida`; `jc::test_b_e_b2_sem_documento_ficam_como_hoje` (o Requerimento, B) |
| FR-3748 (o núcleo do vencido, nas telas e nas recusas; nunca com o Processo) | T009 | `pc::test_depois_do_vencimento_o_requerimento_nao_se_abre_nem_se_envia`; `id::test_depois_do_vencimento_a_apresentacao_e_recusada_e_nada_e_gravado`, `::test_com_o_processo_encerrado_a_recusa_nao_diz_que_o_prazo_venceu`; `si::TestSemDocumentoComoHoje::test_m0_vencido_nao_usa_o_nucleo`; `jc::test_g_o_prazo_terminou_com_o_resumo_e_o_requerimento` (G) |
| FR-3749 (o prazo não iniciado prevalece) | T008, T028 | `ob::test_sem_prazo_correndo_nenhuma_frase_diz_ate`, `::test_prazo_nao_iniciado_sem_nada_a_enviar_nao_diz_que_ja_pode_enviar`; `si::TestAcaoComDocumento::test_prazo_nao_iniciado_diz_que_ja_pode_enviar_sem_data`; `jc::test_k_e_k2_nenhuma_data_aparece_como_prazo` (K, K2); `dc::test_a_convocada_ve_o_que_apresentar_e_ate_quando` |
| FR-3750 (o rótulo do desfecho e a frase do aceite, nas duas telas) | T026 | `si::TestSemDocumentoComoHoje::test_a_frase_do_aceite_so_nos_desfechos_que_incluem`, `si::TestAcaoComDocumento::test_linha_1_decidida_leva_ao_que_foi_enviado`; `jc::test_i_depois_do_resultado_a_pagina_e_so_historico` (I1, I2) |
| FR-3751 (o vocabulário, e as varreduras alcançam os arquivos novos) | T003 | `ob::test_nenhuma_frase_afirma_o_que_ninguem_decidiu`; `vd::test_nenhuma_tela_dos_documentos_afirma_vinculo_nem_autenticidade` (com `portal/obrigacoes.py` e os parciais novos); `vr::test_a_lista_de_superficies_existe_inteira`; `vc::test_nenhuma_superficie_da_019_afirma_o_que_ela_nao_conhece` |
| FR-3752 (o enviado: "Voltar à convocação" e a explicação por momento) | T027 | `jc::test_c1_e_c2_o_acompanhamento_representa_o_conjunto` (atualização admitida), `::test_i_depois_do_resultado_a_pagina_e_so_historico` (I1, não admitida); `interface/test_portal_requerimento.py` (sem convocação, como antes) |
| FR-3753 (o prazo na página do Requerimento a preencher) | T027, T028 | `jc::test_b_e_b2_sem_documento_ficam_como_hoje` (B) |
| FR-3754 (vencido sem rascunho, desfechada sem envio, Processo encerrado: a página diz o estado, e o GET não cria rascunho) | T027 | `jc::test_g_o_prazo_terminou_com_o_resumo_e_o_requerimento` (G), `::test_n_o_pedido_e_nunca_enviado_aparece_como_nao_enviado` (N, com e sem rascunho), `::test_m_o_processo_encerrado_nao_diz_prazo_vencido_nem_promete_conferencia` (M); `interface/test_portal_requerimento.py::TestOEstadoAindaIndisponivel::test_na_convocacao_sem_chamada_a_tela_diz_que_ainda_nao_e_a_hora` |
| FR-3755 (o aviso do envio com documento) | T027 | `jc::test_o_aviso_do_envio_com_documento_aponta_a_convocacao`, `::test_o_aviso_do_envio_sem_documento_e_o_de_hoje` |
| FR-3756 (nada gravado nem criado; titularidade, recusa e resposta privada iguais) | T025a | `jc::test_nenhum_get_grava_alem_da_leitura_da_convocacao` (C2, G, M), `::test_a_inscricao_alheia_e_a_inexistente_recebem_a_mesma_recusa`, `::test_sem_documento_o_requerimento_nao_enviado_e_dito_sem_acao`; `manage.py makemigrations --check` em `verificacao.md` |
| FR-3757 (nenhuma mensagem nova) | — | `sm::test_nenhum_modulo_envia_fora_das_situacoes_declaradas`, `::test_sao_quatro_situacoes_e_a_quarta_e_o_aviso` (sem edição) |
| FR-3758 (a gestão não muda) | — | `vd::test_a_conducao_diz_apto_para_formalizacao` (sem edição); nenhum template ou view da gestão no diff |
| FR-3759 ("Minhas inscrições" não muda) | — | `cc::TestMinhasInscricoes` (seis casos, sem edição) |

## Critérios de sucesso

| Critério | Testes |
|---|---|
| SC-1117 (com documento, o link principal leva à convocação; nenhuma obrigação sem menção) | `si::TestAcaoComDocumento` (linhas 1 a 5); `jc::test_c1_e_c2_o_acompanhamento_representa_o_conjunto` (C2), `::test_f_a_pendencia_vem_primeiro_com_o_motivo_e_o_selo` (F), `::test_h_tudo_conferido_diz_conferido_e_nao_diz_tudo_certo` (H) |
| SC-1118 (zero falsas conclusões) | `si::TestAcaoComDocumento::test_c2_o_enviado_nunca_e_a_acao_principal`; `ob::test_nenhuma_frase_afirma_o_que_ninguem_decidiu`; `jc::test_d_o_aproveitado_nao_parece_pronto_nem_reenviado` (D), `::test_h_tudo_conferido_diz_conferido_e_nao_diz_tudo_certo` (H) |
| SC-1119 (o bloco 1 na primeira tela a 375 px; o selo verificável sem cor) | `nv::test_cada_cenario_nas_duas_larguras` (A, C1, C2, F, J); `jc::test_f_a_pendencia_vem_primeiro_com_o_motivo_e_o_selo` |
| SC-1120 (I1 e I2 sem formulário nem convite) | `jc::test_i_depois_do_resultado_a_pagina_e_so_historico` (I1, I2) |
| SC-1121 (um formato; o mesmo núcleo nas telas e nas recusas; K sem data como prazo) | `ob::test_o_formato_do_prazo_e_um_so`; `pc::test_depois_do_vencimento_o_requerimento_nao_se_abre_nem_se_envia`; `id::test_depois_do_vencimento_a_apresentacao_e_recusada_e_nada_e_gravado`; `jc::test_k_e_k2_nenhuma_data_aparece_como_prazo` (K) |
| SC-1122 (Tab na ordem visual, foco visível, nomes únicos, sem rolagem horizontal, sem violação de CSP) | `nv::test_f_pelo_teclado_a_ordem_e_a_visual_e_o_foco_se_ve`, `::test_cada_cenario_nas_duas_larguras` (22 cenários, as duas larguras) |
| SC-1123 (B, B2 e o Edital sem nada: as telas e a ação de hoje) | `jc::test_b_e_b2_sem_documento_ficam_como_hoje`, `::test_sem_documento_e_sem_requerimento_a_instrucao_neutra`; `si::TestSemDocumentoComoHoje::test_b_e_b2_sem_linha_informativa`; as expectativas editadas estão nomeadas em `verificacao.md` |
| SC-1124 (as quatro perguntas por cenário) | `verificacao.md` |
| SC-1125 (consultas: sem convocação como antes; com convocação, a mesma com um e com seis itens) | `jc::test_sem_convocacao_o_acompanhamento_nao_le_documentos_da_convocacao`, `::test_as_duas_telas_custam_o_mesmo_com_um_e_com_seis_itens`; medida antes/depois em `verificacao.md` |
| SC-1126 (cada combinação em exatamente uma categoria) | `ob::test_cada_item_cai_em_exatamente_uma_categoria`, `::test_as_sete_linhas_do_requerimento`, `::test_o_requerimento_so_e_tarefa_com_a_chamada_aberta` |
| SC-1127 (L, M, N, K2; nenhuma escrita; a mesma recusa) | `jc::test_l_o_opcional_se_envia_sem_tarefa_nenhuma`, `::test_m_o_processo_encerrado_nao_diz_prazo_vencido_nem_promete_conferencia`, `::test_n_o_pedido_e_nunca_enviado_aparece_como_nao_enviado`, `::test_k_e_k2_nenhuma_data_aparece_como_prazo`, `::test_nenhum_get_grava_alem_da_leitura_da_convocacao`, `::test_a_inscricao_alheia_e_a_inexistente_recebem_a_mesma_recusa` |
| SC-1128 (G0, N0 e M0: a linha sem link, a ação de hoje, nada gravado, a mesma contagem) | `jc::test_sem_documento_o_requerimento_nao_enviado_e_dito_sem_acao` (com e sem rascunho), `::test_a_linha_informativa_nao_acrescenta_consulta`; `si::TestSemDocumentoComoHoje`; a divergência da contagem do acompanhamento está em `verificacao.md` |
