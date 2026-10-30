# Rastreabilidade: Jornada operacional da Retificação

Cada requisito → a tarefa que o implementa → o teste que o verifica. As tarefas estão em
[tasks.md](tasks.md). Os caminhos de teste são relativos a `backend/tests/`. `jornada` é
`interface/test_jornada_da_retificacao.py`; `auditoria` é
`interface/test_auditoria_passagem_da_retificacao.py`; `atos` é
`unit/interface/test_atos_da_retificacao.py`; `fusao` é `unit/publicacoes/test_fusao_da_edicao.py`.

| Requisitos | Tarefas | Testes |
|---|---|---|
| FR-2701 (seção "Retificações em curso" no detalhe do Edital, a todo o escopo) | T005, T006 | `auditoria::test_quem_homologa_encontra_a_retificacao_em_revisao_sem_conhecer_a_url`, `::test_a_lista_e_o_edital_citam_a_retificacao_pendente`; `jornada::test_h_cada_papel_alcanca_a_retificacao_pela_barra` |
| FR-2702 (situação, criação, justificativa, próximo responsável, ato da pessoa) | T003, T005 | `jornada::test_c_quem_elabora_ve_o_rascunho_ao_abrir_retificar_e_continua`; `atos::test_e_voce_quando_o_ato_principal_esta_entre_os_seus` |
| FR-2703 (publicada e cancelada fora; a publicada continua em Documentos publicados) | T006 | `jornada::test_g_publicada_sai_das_pendencias_e_documentos_e_consolidacao_ficam_integros`, `::test_g_cancelar_so_ao_gestor_e_so_em_elaboracao`; `auditoria::test_a_unica_porta_e_a_da_retificacao_ja_publicada` |
| FR-2704 (estado vazio no Edital publicado) | T006 | `jornada::test_h_sem_retificacao_o_edital_publicado_diz_que_nao_ha`, `::test_g_publicada_sai_das_pendencias…` |
| FR-2705 (o detalhe do Edital não cresce com as Retificações) | T003, T006 | `jornada::test_a_lista_e_o_edital_nao_crescem_com_as_retificacoes` |
| FR-2706 (marca na Lista, com o ato ou quem age) | T007 | `jornada::test_a_criar_retomar_editar_submeter_homologar_e_publicar` (as três marcas); `auditoria::test_quem_publica_encontra_a_retificacao_homologada_sem_conhecer_a_url` |
| FR-2707 (a Lista não cresce com Editais nem Retificações) | T003, T007 | `jornada::test_a_lista_e_o_edital_nao_crescem_com_as_retificacoes` |
| FR-2708 (texto, teclado, leitor de tela, 375 px) | T008, T025 | `interface/test_acessibilidade.py` (classes com regra na folha); a conferência no navegador em [verificacao.md](verificacao.md) |
| FR-2709 (Retificar mostra as em curso, oferece continuar, não impede) | T019 | `auditoria::test_quem_vai_compor_outro_rascunho_ve_o_primeiro_e_pode_continuar`; `jornada::test_c_quem_elabora_ve_o_rascunho_ao_abrir_retificar_e_continua` |
| FR-2710 (as quatro perguntas no detalhe) | T010 | `jornada::test_a_criar_retomar…` ("Aguardando quem homologa", "O próximo ato é seu") |
| FR-2711 (próximo responsável por situação, por papel, finais encerradas) | T003, T010 | `atos::test_quem_age_a_seguir_sai_da_situacao`, `::test_situacao_final_nao_tem_proximo_responsavel`; `jornada::test_g_cancelar_so_ao_gestor…` ("encerrada") |
| FR-2712 ("é você" pelas ofertas; segregação dita) | T003, T010 | `atos::test_e_voce_quando_o_ato_principal_esta_entre_os_seus`, `::test_quem_submeteu_e_homologou_ve_publicar_desabilitado_com_o_motivo` |
| FR-2713 (quem atuou) | T010 | `jornada::test_c_outra_elaboradora_retoma_o_rascunho_e_o_submete` (criou e submeteu distintos); a seção no template |
| FR-2714 (motivo da última devolução em destaque) | T018 | `jornada::test_b_duas_devolucoes_e_o_mesmo_registro_chega_a_publicacao` |
| FR-2715 ("Editar a Retificação" só em elaboração, a quem elabora) | T003, T018 | `atos::test_a_edicao_so_e_oferecida_a_quem_elabora_em_elaboracao`; `jornada::test_g_submetida_nao_oferece_cancelar_nem_editar` |
| FR-2716 (a mesma Retificação; identidade, criação, base, trilha) | T016 | `jornada::test_b_duas_devolucoes…` (mesmo `id`, uma Retificação), `::test_c_outra_elaboradora…` (`created_by` preservado) |
| FR-2717 (o formulário parte do proposto; justificativa e vigência preenchidas) | T016, T017 | `jornada::test_a_edicao_parte_do_que_o_rascunho_ja_declara` |
| FR-2718 (o ato inteiro contra a base; conferido reproduzido ou nada gravado) | T013, T014, T016 | `fusao::test_a_alteracao_intocada_continua_e_a_nova_entra_depois`, `::test_a_alteracao_tocada_passa_a_ter_o_valor_novo_sem_duplicar`, `::test_a_que_volta_ao_vigente_sai_do_ato`, `::test_o_acrescimo_editado_leva_o_campo_novo_dentro_dele`, `::test_o_acrescimo_removido_sai_sem_virar_remocao`, `::test_a_fusao_que_nao_reproduz_o_conferido_e_recusada`; `jornada::test_desfazer_tudo_e_recusado_sem_gravar`, `::test_so_a_justificativa_muda_e_grava` |
| FR-2719 (remoções listadas e desfazíveis) | T013, T017, T027 | `interface/test_jornada_da_retificacao_convergencia.py::test_a_remocao_declarada_se_desfaz_pela_edicao`; `fusao::test_a_remocao_desfeita_sai_do_ato`, `::test_desfazer_so_vale_para_remocao` |
| FR-2720 (conferência antes de gravar) | T016, T017 | `jornada::test_a_criar_retomar…` (o auxiliar `editar` exige "O que muda em relação ao rascunho" antes de confirmar) |
| FR-2721 (só em elaboração 409; sem permissão 403; fora do escopo 404) | T016 | `jornada::test_f_ato_concorrente_sobre_a_edicao_aberta_recusa_a_gravacao`, `::test_g_publicada_sai…` (409), `::test_editar_sem_permissao_e_403_com_a_permissao_nomeada`, `::test_e_outra_unidade_nao_ve_nem_edita` |
| FR-2722 (a revisão viaja; divergência recusa sem gravar nem interpretar) | T016, T017 | `jornada::test_f_duas_sessoes_editando_a_segunda_e_recusada_sem_gravar`, `::test_f_a_corrida_entre_conferir_e_gravar_e_recusada_pela_revisao` |
| FR-2723 (a edição na trilha, também pela API) | T015, T021 | `jornada::test_a_api_que_edita_o_rascunho_tambem_entra_na_trilha`, `::test_a_criar_retomar…`, `::test_c_outra_elaboradora…` |
| FR-2724 (sem gestos na edição) | T016, T017 | `jornada::test_a_edicao_parte_do_que_o_rascunho_ja_declara` ("Aplicar a todos" ausente) |
| FR-2725 (Publicar desabilitado com motivo; confirmação sem "Confirmar") | T003, T010, T011 | `auditoria::test_o_detalhe_nao_oferece_publicar_a_quem_a_segregacao_impede`; `jornada::test_d_quem_acumula_os_papeis_e_avisado_e_nao_recebe_o_botao_da_recusa`; `atos::test_quem_submeteu_e_homologou_ve_publicar_desabilitado_com_o_motivo` |
| FR-2726 (aviso ao homologar o que submeteu) | T011 | `atos::test_homologar_o_que_submeteu_avisa_sem_impedir`; `jornada::test_d_quem_acumula…` |
| FR-2727 (permissão, segregação e situação com frases próprias) | T011 | `jornada::test_d_as_recusas_dizem_qual_foi_a_causa`, `::test_d_quem_acumula…` ("Segregação de funções."); `atos::test_a_permissao_continua_vindo_antes_da_situacao_e_da_segregacao`, `::test_a_situacao_vem_antes_da_segregacao` |
| FR-2728 (a quem o ato entrega; quem age depois do ato) | T011 | `atos::test_cada_ato_diz_a_quem_entrega`, `::test_publicar_e_cancelar_nao_entregam_a_ninguem`; `jornada::test_a_criar_retomar…` |
| FR-2729 (devolver das duas origens leva ao mesmo registro editável, repetível) | T016, T020 | `jornada::test_b_duas_devolucoes_e_o_mesmo_registro_chega_a_publicacao` |
| FR-2730 (uma derivação dos atos) | T003 | `atos::test_as_ofertas_sao_os_atos_disponiveis_quando_nao_ha_segregacao`; `auditoria::test_o_detalhe_oferece_exatamente_o_que_o_servidor_aceita` |
| FR-2731 (nada novo de permissão, situação, transição; 403/404/409, CAS e trilha preservados; segregação lê quem submeteu) | T003, T020 | `auditoria::test_outra_unidade_nao_ve_nem_pratica`, `::test_a_segunda_homologacao_e_recusada_e_nao_duplica`, `::test_a_trilha_registra_ator_operacao_e_os_dois_estados`, `::test_caracterizacao_quem_so_compos_conclui_se_outra_pessoa_submeter`; `jornada::test_g_cancelar_so_ao_gestor…` |
| FR-2732 (sem fila, notificação, atribuição ou estado persistido) | — | por construção: nenhuma migration, e o próximo responsável é derivado (`atos::test_quem_age_a_seguir_sai_da_situacao`) |
| SC-971 (as jornadas por sessões independentes, só pela barra) | T020 | `jornada::test_a_…`, `::test_b_…`, `::test_c_…`, `::test_g_…`, `::test_h_cada_papel_alcanca_a_retificacao_pela_barra` |
| SC-972 (os quatro `xfail` passam sem a marca, asserções originais) | T009, T012 | `auditoria` (19 casos, nenhum `xfail`) |
| SC-973 (a tela oferece exatamente o que o servidor aceita) | T003, T010 | `auditoria::test_o_detalhe_oferece_exatamente_o_que_o_servidor_aceita`; `jornada::test_d_…` |
| SC-974 (consultas iguais com 1 e 5 Retificações, e com 1 e 3 Editais) | T020, T026 | `jornada::test_a_lista_e_o_edital_nao_crescem_com_as_retificacoes`; `interface/test_jornada_da_retificacao_convergencia.py::test_as_retificacoes_em_curso_de_varios_editais_sao_uma_consulta` |
| SC-975 (duas devoluções, mesmo identificador, uma Retificação) | T020 | `jornada::test_b_duas_devolucoes_e_o_mesmo_registro_chega_a_publicacao` |
| SC-976 (nenhuma gravação sobrescreve outra em silêncio) | T020 | `jornada::test_f_duas_sessoes…`, `::test_f_a_corrida…`, `::test_f_ato_concorrente…` |
| SC-977 (a suíte completa sem regressão) | T024 | [verificacao.md](verificacao.md) |
| SC-978 (a jornada com três pessoas reais) | — | pendente: depende do usuário |
