# Rastreabilidade: A experiência da convocação, incremento 1 (121)

Cada requisito → a tarefa que o implementa → o teste que o verifica. Caminhos de teste relativos a
`backend/tests/`. Abreviações:

- `pa` = `unit/convocacao/test_prazo_apresentado.py` — o prazo apresentado, sem banco
- `em` = `unit/convocacao/test_escolha_da_mensagem.py` — a escolha da mensagem e o resumo do modelo
- `um` = `unit/convocacao/test_mensagem.py` — o envio pela função, com o `locmem`
- `ob` = `unit/portal/test_obrigacoes_da_convocacao.py` — a projeção, com a chamada
- `pc` = `interface/test_portal_convocacao.py` — a tela da convocação
- `jc` = `interface/test_portal_jornada_consolidada.py` — as telas da `118`, por cenário
- `dc` = `interface/test_portal_documentos_da_convocacao.py` — o envio de documento e a volta
- `cc` = `interface/test_portal_caminho_da_convocacao.py`
- `co` = `interface/test_correcao_da_convocacao.py` — a prévia da correção na gestão
- `ca` = `authorization/test_convocacao_alheia.py`
- `de` = `integration/portal/test_destino_da_convocacao.py` — o link, o acesso e o destino
- `ac` = `integration/portal/test_contexto_do_acesso.py`
- `rp` = `portal/test_resultados_por_perfil.py`
- `vp` = `portal/test_vocabulario_das_telas_publicas.py`
- `mc` = `integration/convocacao/test_mensagem_da_convocacao.py` — a mensagem de verdade
- `vm` = `integration/convocacao/test_versao_do_modelo.py` — a versão do modelo gravada
- `sm` = `test_situacoes_de_mensagem.py`
- `vc` = `test_vocabulario_da_convocacao.py`, `vd` = `test_vocabulario_dos_documentos_da_convocacao.py`
- `pl` = `interface/test_politica_de_conteudo.py`
- `js` = `javascript/envio.test.js` e `javascript/arquivo.test.js`, pelo `test_javascript.py`
- `nv` = `navegador/test_jornada_da_convocacao_121.py` — Chromium, 375 px, 320 px e desktop
- `nc` = `navegador/test_jornada_consolidada_do_convocado.py`

As letras entre parênteses são os cenários da `118` (`tests/fixtures/jornada_do_convocado.py`); `corr`
é o A corrigido pela `120`.

## Requisitos funcionais

| Requisito | Tarefas | Testes |
|---|---|---|
| FR-3858 (o título por estado; nenhum promete vaga) | T011, T013 | `ob::test_o_titulo_por_estado` (4 estados); `pc::TestAChamada::test_fechada_so_conta_o_que_houve` (G, M, I1), `::test_o_titulo_nao_se_repete_num_h2` (C1, G), `::test_sem_documento_a_chamada_sem_a_frase_antiga` (B); `jc::test_g_o_prazo_terminou_com_o_resumo_e_o_requerimento`, `::test_n_o_pedido_e_nunca_enviado_aparece_como_nao_enviado`, `::test_i_depois_do_resultado_a_pagina_e_so_historico` |
| FR-3859 (a ordem da chamada) | T012, T013 | `pc::TestAChamada::test_a_ordem_da_chamada` (C1, com o contexto *"‹Perfil› · Edital ‹NN/AAAA›"*) |
| FR-3860 (a etapa descreve a chamada, sem imperativo) | T011 | `ob::test_a_etapa_descreve_a_chamada_e_nao_o_estado` (4 linhas, antes e depois do envio), `::test_o_requerimento_na_inscricao_nao_entra_na_etapa`, `::TestOCartaoDoPrazo::test_so_facultativo_segue_a_118`; `pc::test_a_chamada_responde_pelo_proprio_texto` |
| FR-3861 (o cartão do prazo; nada encolhe) | T012, T016 | `ob::TestOCartaoDoPrazo` (data, dia, contagem; K; sem vencimento); `pc::TestAConvocacaoDaPropriaPessoa::test_com_o_prazo_correndo_o_cartao_diz_a_data_o_dia_e_a_contagem`; `jc::test_k_e_k2_nenhuma_data_aparece_como_prazo` (K, K2); `nv::test_sem_rolagem_horizontal_a_320_com_fonte_e_zoom` |
| FR-3862 (o resumo do que falta, ou a conclusão) | T011 | `ob::TestAAcao::test_sem_tarefa_sem_acao`; `jc::test_e_enviados_aguardando_nada_por_enquanto_e_a_frase_de_conclusao` (E), `::test_f_a_pendencia_vem_primeiro_com_o_motivo_e_o_selo` (F) |
| FR-3863 (um link, *"Ver o que preciso fazer"*, à primeira tarefa) | T011, T012, T014 | `ob::TestAAcao` (pendente antes da que falta; a primeira a enviar; o Requerimento quando é a única; sem tarefa), `::test_so_o_requerimento_a_preencher_leva_ao_requerimento`; `jc::test_c1_e_c2_o_acompanhamento_representa_o_conjunto` (C1), `::test_f_a_pendencia_vem_primeiro_com_o_motivo_e_o_selo` (F), `::test_j_a_pendencia_sem_envio_diz_envie_o_arquivo` (J), `::test_l_o_opcional_se_envia_sem_tarefa_nenhuma` (L); `nc::test_f_pelo_teclado_a_ordem_e_a_visual_e_o_foco_se_ve` |
| FR-3864 (a consequência uma vez, e a ressalva) | T011, T012, T014 | `ob::test_a_ressalva_so_fala_de_matricula_com_o_requerimento`; `pc::TestAChamada::test_a_consequencia_uma_vez_so` (C1, K, G, I1, M), `::test_a_ordem_da_chamada` |
| FR-3865 (o andamento: só obrigatórios, sem o Requerimento, sem barra) | T011, T014 | `ob::test_o_andamento_conta_so_obrigatorios_e_sem_o_requerimento`; `jc::test_e_enviados_aguardando_nada_por_enquanto_e_a_frase_de_conclusao`, `::test_l_o_opcional_se_envia_sem_tarefa_nenhuma`; `dc::TestAConfirmacao::test_cada_volta_mostra_so_o_seu_envio` |
| FR-3866 (os blocos da `118` depois do andamento) | T014 | `pc::TestAChamada::test_aberta_mantem_os_blocos_da_118_depois_do_andamento` (F); `jc::test_c1_e_c2_o_acompanhamento_representa_o_conjunto` |
| FR-3867 (fechada: nada da chamada aberta) | T011, T012 | `ob::TestAAcao::test_fechada_nao_tem_nada_da_chamada_aberta`; `pc::TestAChamada::test_fechada_so_conta_o_que_houve` (G, M, I1) |
| FR-3868 (sem documento: título, cartão e correção) | T012, T013 | `pc::TestAChamada::test_sem_documento_a_chamada_sem_a_frase_antiga` (B), `pc::TestAConvocacaoDaPropriaPessoa::test_a_tela_mostra_a_chamada_o_prazo_e_o_que_fazer` (`:107`, reescrito), `::test_com_o_prazo_correndo_o_cartao_diz_a_data_o_dia_e_a_contagem`; `jc::test_b_e_b2_sem_documento_ficam_como_hoje`; `dc::test_sem_documento_na_convocacao_a_tela_e_a_de_antes` |
| FR-3869 (a correção no cartão; a substituída nos três textos) | T019, T020, T021 | `ob::TestOCartaoDoPrazo::test_a_correcao_e_dita_no_cartao`, `ob::TestASubstituida` (comunicada, publicação, não comunicada, a última da anterior, sem motivo); `pc::TestACorrecaoNoPortal` (comunicada, não comunicada, publicação, todos os estados, A–B–C com B falhada); `cc::TestAcompanhamento::test_a_sucessora_ocupa_o_lugar_da_sucedida`; `jc::test_com_a_vigente_sucedendo_outra_o_custo_continua_o_mesmo` |
| FR-3870 (a volta em `#confirmacao`, com foco sem script) | T050, T051, T052 | `ob::TestAConfirmacaoDoEnvio`; `dc::TestAConfirmacao` (aceito, cada volta, o último, o mesmo arquivo), `dc::test_a_convocada_envia_pelo_portal_e_le_o_resultado` (`:94`, reescrito); `nv::test_sem_script_o_foco_vai_a_confirmacao` |
| FR-3871 (a recusa no cartão, com o foco) | T050, T052 | `dc::TestARecusaNoCartao` (sem arquivo, não PDF, acima do limite, fora do prazo); `nv::test_com_script_o_foco_vai_a_recusa_no_cartao` |
| FR-3872 (os três scripts da inscrição, e nenhum novo) | T053 | `dc::test_a_convocacao_carrega_os_tres_scripts_e_nenhum_outro`; `js` (`envio.test.js`: com e sem htmx, a volta pelo cache; `arquivo.test.js`: o nome escolhido); `pl::test_nenhum_modelo_tem_script_embutido_nem_atributo_de_evento`; `nv::test_escolhido_o_arquivo_o_cartao_diz_o_nome` |
| FR-3873 (uma função, no fuso da instalação) | T006, T007 | `pa::TestODiaLocal`, `pa::TestOFusoDoServidorNaoMuda`; `ob::test_data_hora_e_ate_delegam_ao_prazo_apresentado`; `um::test_o_prazo_e_dito_no_fuso_de_quem_le` |
| FR-3874 (a contagem em dias de calendário) | T006 | `pa::TestAContagem` (23h59, 00h01, uma hora antes, o próprio instante, vencido, *"nunca falta 1 dia"*) |
| FR-3875 (`HHhMM` no portal e no e-mail) | T006, T042 | `pa::TestOFormatoDaHora`; `um::test_o_prazo_em_sao_paulo_sai_tres_horas_antes_do_utc` (`:170`, revisto); `mc::TestAsVariantes::test_o_assunto_e_a_frase` (zero `HH:MM`) |
| FR-3876 (sem sessão, o acesso, antes de qualquer consulta) | T026 | `ca::test_sem_sessao_real_inventado_e_alheio_recebem_o_mesmo_redirecionamento`, `::test_nenhuma_consulta_a_inscricao_ao_edital_nem_a_convocacao_antes_da_resposta`, `::test_so_o_email_na_sessao_sem_codigo_conta_como_sem_sessao`, `::test_sem_sessao_nenhuma_rota_revela_se_a_inscricao_existe` (`:148`, revisto) |
| FR-3877 (com outra identidade, a recusa de inexistente; a escrita como hoje) | T026 | `ca::test_a_rota_de_joao_responde_a_maria_como_inscricao_inexistente`; `de::TestOsDestinosHostis::test_sem_sessao_as_rotas_de_escrita_respondem_como_hoje` |
| FR-3878 (o destino em quatro camadas) | T027 | `de::TestOsDestinosHostis` (outro host, `javascript:`, `//`, rota fora da lista, rota inexistente; consulta e fragmento); `rp::test_o_destino_na_convocacao_volta_a_convocacao_reconstruida` |
| FR-3879 (depois do código, a convocação, nos três percursos; o destino não autoriza) | T027 | `de::TestOsTresPercursos` (sessão vencida, reconciliação, primeiro acesso), `de::TestODestinoNaoAutoriza`; `nv::test_do_link_ao_codigo_a_convocacao` |
| FR-3880 (as telas de acesso dizem para onde se vai, sem nomear nada) | T028, T029 | `ac::test_a_caminho_da_convocacao_as_duas_telas_dizem_para_onde_se_vai`, `::test_o_texto_e_o_mesmo_para_identificador_real_inventado_e_alheio`, `::test_sem_destino_de_convocacao_nenhuma_frase_nova`; `nv::test_do_link_ao_codigo_a_convocacao` |
| FR-3881 (nada se escreve por GET além do de hoje; abrir não move prazo) | T026 | `de::TestNadaSeEscrevePorGet::test_abrir_nao_move_prazo_e_so_registra_leitura_com_sessao_titular`; `jc::test_nenhum_get_grava_alem_da_leitura_da_convocacao` |
| FR-3882 (HTML e texto, o texto com tudo) | T042, T043 | `mc::TestAsDuasPartes::test_o_texto_puro_contem_cada_frase_do_html` |
| FR-3883 (a ordem da mensagem inicial; o link da convocação) | T042 | `mc::TestAsDuasPartes::test_o_link_e_o_da_convocacao_da_inscricao`, `::test_com_a_base_o_link_e_absoluto`; `um::TestOQueAMensagemDiz`; `cc::TestMinhasInscricoes::test_a_mensagem_aponta_a_convocacao_da_inscricao` (`:221`, revisto) |
| FR-3884 (o assunto e a frase pelo que a chamada pede) | T041, T042 | `em::TestAVariante`; `mc::TestAsVariantes::test_o_assunto_e_a_frase` (C1, A, B, sem documento nem Requerimento), `::test_sem_vencimento_o_assunto_nao_leva_data`, `::test_todos_os_obrigatorios_aproveitados_ainda_pedem_documentos`; `um::TestOQueAMensagemDiz::test_o_assunto_nomeia_o_edital` |
| FR-3885 (a mensagem da correção cita a última enviada com sucesso) | T041, T042, T043 | `em::TestACadeia` (as sete linhas da R-002); `mc::TestACadeia` (os cinco cenários da D-008) |
| FR-3886 (nada de dado pessoal, imagem ou endereço externo) | T042 | `mc::TestAsDuasPartes::test_nada_externo_nem_dado_da_pessoa`; `um::TestOQueAMensagemNaoDiz` |
| FR-3887 (a identificação institucional vem da unidade) | T043 | `mc::TestAsDuasPartes::test_a_identificacao_institucional_vem_da_unidade`; `unidades/test_identificacao_multiunidade.py::test_4_a_convocacao_e_o_comprovante_assinam_pela_unidade` |
| FR-3888 (a reserva, a repetição sem envio, a falha contada, a publicação sem e-mail) | T043 | `mc::TestARepeticao::test_a_mesma_chave_nao_envia`; `um::test_o_retorno_zero_do_correio_e_falha`; `integration/convocacao/test_comunicacao.py` (sem mudança); `sm` (sem mudança) |
| FR-3889 (a escolha só de registros; a versão do modelo gravada, também na falha) | T039, T040, T041, T043 | `mc::TestAReconstrucao`; `vm::TestAGravacao`, `vm::TestAPreservacao`, `vm::TestSemRetroatividade`, `vm::TestRecuperavelPeloGit`; `em::TestAIdentificacaoDoModelo` |
| FR-3890 (a prévia da correção diz que corrige a anterior) | T044 | `co::TestAPrevia::test_a_previa_diz_a_comunicacao_pela_forma` |
| FR-3891 (só a coluna e a migration da D-009; 53 tabelas append-only) | T039, T040 | `vm::TestSemRetroatividade::test_a_migration_so_acrescenta_a_coluna`; `integration/test_database_permissions.py` (sem mudança, parametrizado por `TABELAS_APPEND_ONLY`); `sm` |
| FR-3892 (os textos novos sob as varreduras de vocabulário) | T045 | `vc` e `vd` (com o parcial da chamada e os quatro modelos nas listas literais); `vp::test_as_telas_de_acesso_a_caminho_da_convocacao` |

## Critérios de sucesso

| Critério | Testes |
|---|---|
| SC-1150 (a chamada responde pelo próprio texto, por cenário) | `pc::test_a_chamada_responde_pelo_proprio_texto` (C1, F, G, I1, corr); o link da mensagem em `mc::TestAsDuasPartes::test_o_link_e_o_da_convocacao_da_inscricao` |
| SC-1151 (a ação é o primeiro controle depois do resumo, à primeira tarefa) | `ob::TestAAcao`; `pc::TestAChamada::test_a_ordem_da_chamada`; `jc` (C1, F, J); `nv::test_a_acao_na_primeira_tela_com_folga` (A, C1, C2, F, J, corr) |
| SC-1152 (a 375 × 812, a ação com folga de uma linha) | `nv::test_a_acao_na_primeira_tela_com_folga`; `nc::test_cada_cenario_nas_duas_larguras` |
| SC-1153 (sem rolagem horizontal a 320 px, com fonte a 150 % e zoom de 200 %) | `nv::test_sem_rolagem_horizontal_a_320_com_fonte_e_zoom` (C1, F, G, I1, corr) |
| SC-1154 (o dia da semana nos 365 dias; 23h30; a contagem; outro fuso de servidor) | `pa::TestODiaDaSemana`, `pa::TestODiaLocal`, `pa::TestAContagem`, `pa::TestOFusoDoServidorNaoMuda` |
| SC-1155 (zero `HH:MM` no prazo) | `pa::TestOFormatoDaHora`; `mc::TestAsVariantes::test_o_assunto_e_a_frase`; `um::test_o_prazo_em_sao_paulo_sai_tres_horas_antes_do_utc` |
| SC-1156 (do link à convocação nos três percursos) | `de::TestOsTresPercursos`; `nv::test_do_link_ao_codigo_a_convocacao` |
| SC-1157 (sem sessão, a mesma resposta e zero consultas) | `ca::test_sem_sessao_real_inventado_e_alheio_recebem_o_mesmo_redirecionamento`, `::test_nenhuma_consulta_a_inscricao_ao_edital_nem_a_convocacao_antes_da_resposta` |
| SC-1158 (os destinos hostis viram a lista ou o reconstruído) | `de::TestOsDestinosHostis` |
| SC-1159 (o texto contém o HTML; nada externo nem da pessoa) | `mc::TestAsDuasPartes` |
| SC-1160 (a mensagem da sucessora pela D-008) | `em::TestACadeia`; `mc::TestACadeia`; `pc::TestACorrecaoNoPortal::test_a_falha_no_meio_descreve_a_imediatamente_anterior` |
| SC-1161 (a repetição não envia; as quatro situações) | `mc::TestARepeticao`, `mc::test_as_quatro_situacoes_continuam_quatro`; `sm` (sem mudança) |
| SC-1162 (o foco na confirmação sem script, e na recusa) | `nv::test_sem_script_o_foco_vai_a_confirmacao`, `::test_com_script_o_foco_vai_a_recusa_no_cartao`; `dc::TestAConfirmacao`, `dc::TestARecusaNoCartao` |
| SC-1163 (o nome do arquivo escolhido) | `js` (`arquivo.test.js`); `nv::test_escolhido_o_arquivo_o_cartao_diz_o_nome` |
| SC-1164 (a matriz de clientes de e-mail; SPF, DKIM e DMARC) | **humana**, antes do uso real, sobre o SMTP de homologação |
| SC-1172 (a versão do modelo gravada, conferível e preservada) | `vm` (gravação, correspondência, preservação, sem retroatividade, repetição, Git); `em::TestAIdentificacaoDoModelo` |

## Casos-limite

| Caso | Testes |
|---|---|
| Prazo não iniciado (K) | `ob::TestOCartaoDoPrazo::test_o_prazo_nao_iniciado_diz_so_a_frase`; `jc::test_k_e_k2_nenhuma_data_aparece_como_prazo`; `pc::TestAChamada::test_a_consequencia_uma_vez_so` (K) |
| Sem vencimento registrado | `ob::TestOCartaoDoPrazo::test_sem_vencimento`; `mc::TestAsVariantes::test_sem_vencimento_o_assunto_nao_leva_data`; `um::TestOQueAMensagemDiz::test_edital_sem_prazo_publicado_nao_ganha_um` |
| Vencimento hoje, ainda não passado | `pa::TestAContagem::test_conta_dias_de_calendario`, `::test_hoje_sem_o_dia_da_semana` |
| Vencimento à meia-noite local | `pa::TestODiaLocal::test_vencimento_a_meia_noite_e_o_instante_no_fuso` |
| Vencimento às 23h30 locais | `pa::TestODiaLocal::test_vencimento_as_23h30_locais_e_o_dia_local` |
| Chamada só com documento facultativo | `ob::TestOCartaoDoPrazo::test_so_facultativo_segue_a_118`; `em::TestAVariante` (só facultativo); `jc::test_l_o_opcional_se_envia_sem_tarefa_nenhuma` |
| Todos os obrigatórios aproveitados | `mc::TestAsVariantes::test_todos_os_obrigatorios_aproveitados_ainda_pedem_documentos` (D); `jc::test_d_o_aproveitado_nao_parece_pronto_nem_reenviado` |
| Cadeia sem nenhuma mensagem enviada | `em::TestACadeia::test_a_e_b_falhadas_c_e_a_inicial`; `mc::TestACadeia::test_a_e_b_falhadas_c_e_a_inicial` |
| A da imediatamente anterior falhou, outra foi enviada | `em::TestACadeia::test_a_enviada_b_falhada_c_cita_a`; `mc::TestACadeia::test_a_enviada_b_falhada_c_cita_a`; `pc::TestACorrecaoNoPortal::test_a_falha_no_meio_descreve_a_imediatamente_anterior` |
| Correção da correção, sem falha | `em::TestACadeia::test_a_e_b_enviadas_c_cita_b`; `mc::TestACadeia::test_a_e_b_enviadas_c_cita_b` |
| Convocação por publicação | `em::TestACadeia::test_a_por_publicacao_c_e_a_inicial`; `vm::TestAGravacao::test_a_publicacao_nao_tem_modelo`; `pc::TestACorrecaoNoPortal::test_por_publicacao` |
| O mesmo arquivo enviado de novo | `ob::TestAConfirmacaoDoEnvio::test_o_mesmo_arquivo`; `dc::TestAConfirmacao::test_o_mesmo_arquivo_de_novo` |
| Vários envios seguidos | `dc::TestAConfirmacao::test_cada_volta_mostra_so_o_seu_envio` |
| Recusa por prazo encerrado no envio | `dc::TestARecusaNoCartao::test_fora_do_prazo` |
| Sessão identificada, sem código provado | `ca::test_so_o_email_na_sessao_sem_codigo_conta_como_sem_sessao` |
| Pedido sem sessão a uma rota de escrita | `de::TestOsDestinosHostis::test_sem_sessao_as_rotas_de_escrita_respondem_como_hoje` |
| Destino guardado de outra visita | `de::TestODestinoNaoAutoriza::test_destino_guardado_de_outra_visita` |
| Pessoa com mais de uma inscrição convocada | `de::TestODestinoNaoAutoriza::test_cada_inscricao_leva_a_propria_convocacao` |
| Aguardando ou não convocado na rota da convocação | `pc::TestAChamada::test_sem_convocacao_o_titulo_de_hoje`; `pc::TestAsDuasAusencias` |
