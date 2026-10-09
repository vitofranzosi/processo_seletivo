# Rastreabilidade — 066 · Avisos complementares aos candidatos

**Frase que governa**: *o aviso aponta para um ato que já existe. Ele não é o ato, não muda o ato e
não decide quem o ato alcançou.*

Cada linha aponta o lugar do código e o que o prende.

Caminhos: A = `processo_seletivo/avisos/`; I = `processo_seletivo/interface/`.

Testes, sob `tests/`:

| Sigla | Arquivo | Sigla | Arquivo |
|---|---|---|---|
| **TR** | `integration/avisos/test_aviso_do_resultado.py` | **TF** | `integration/avisos/test_despacho_falhas.py` |
| **TRt** | `integration/avisos/test_aviso_da_retificacao.py` | **TX** | `integration/avisos/test_despacho_concorrencia.py` |
| **TC** | `integration/avisos/test_aviso_da_chamada.py` | **TJ** | `integration/avisos/test_chave_e_janela.py` |
| **TA** | `integration/avisos/test_autorizacao.py` | **TO** | `integration/avisos/test_orcamento_do_aviso.py` |
| **TM** | `integration/avisos/test_modelos.py` | **TT** | `interface/test_avisos.py` |
| **TD** | `integration/avisos/test_despacho.py` | **TU** | `unit/avisos/` |
| **TV** | `test_vocabulario_do_aviso.py` | **TS** | `test_situacoes_de_mensagem.py` |
| **TG** | `test_avisos_sem_correio_real.py` | **TP** | `authorization/test_papel_do_aviso.py` |

---

## 1. Requisitos funcionais

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-1241** | A`application/destinatarios.py` (`universo_do_resultado`, `universo_da_chamada`); nenhuma rota de aviso sem ato | TR, TC (`AVISO_SEM_ATO`); TT |
| **FR-1242** | A`models.py` sem coluna de efeito; nenhum import de escrita da convocação em A`application/` | TC `test_nenhum_registro_de_convocacao_muda` |
| **FR-1243** | A confirmação é gesto; `publicar` e `comunicar` não importam A | TR `test_publicar_nao_dispara_aviso`; TRt `test_retificar_sem_gesto_nao_avisa_ninguem` |
| **FR-1244** | A`application/comando.py` `recusar_processo_em_estado_final` | TA `test_processo_em_estado_final_recusa` |
| **FR-1245** | A`application/destinatarios.py` (`forma_declarada` da versão citada); I`avisos.py` `chamadas_publicadas` | TC `test_mensagem_individual_nao_tem_aviso` |
| **FR-1246** | `universo_do_resultado` lê as `SituacaoDivulgada` | TR `test_os_destinatarios_sao_todos_os_considerados_inclusive_sem_posicao` |
| **FR-1247** | `ja_avisadas`, `naturezas_pendentes` (`D-002`) | TR `test_avisada_a_publicacao_nao_ha_publicacao_nova`; TRt `test_so_a_retificadora_e_nova_e_os_destinatarios_sao_os_dela` |
| **FR-1248** | A`domain/mensagem.py` `LINHA_DA_RETIFICACAO` | TRt `test_a_linha_fixa_diz_que_retifica_e_nao_que_algo_mudou`; TU `test_mensagem.py` |
| **FR-1249** | `UNIQUE (aviso, inscricao)`; dedupe em `universo_do_resultado` | TR; TO |
| **FR-1250** | `identidade/application/endereco.py`, usado por `comunicar` e pelos avisos | TR; `integration/convocacao/test_comunicacao.py` |
| **FR-1251** | `universo_da_chamada`, `elegibilidade_da_convocacao` (`D-003`) | TC `test_o_universo_e_a_publicacao_inteira_e_a_mensagem_vai_a_quem_segue` |
| **FR-1252** | sem filtro nem exclusão na prévia; `_recusar_sem_elegivel` | TR `test_sem_endereco_fica_registrado_e_fora_do_envio`; TC `test_todas_vencidas_e_recusado` |
| **FR-1253** | `DestinatarioDoAviso` com endereço e elegibilidade gravados | TRt `test_o_primeiro_aviso_continua_como_foi` |
| **FR-1254** | A`domain/mensagem.py` `validar_texto` | TU `test_mensagem.py` `test_texto_invalido_e_recusado_com_o_campo` |
| **FR-1255** | A`domain/variaveis.py` `VARIAVEIS` | TU `test_variaveis.py` |
| **FR-1255a** | `{link_da_publicacao}` = `portal:resultado`, que responde depois da sucessão | TRt `test_o_link_congelado_no_aviso_antigo_leva_a_vigente` |
| **FR-1256** | `variaveis.validar` | TU `test_variaveis.py`; TM `test_variavel_desconhecida_e_recusada_com_o_nome`; TT |
| **FR-1257** | A`domain/mensagem.py` `RODAPE`, `FRASE_DA_CHAMADA` | TU `test_mensagem.py`; TC `test_o_rodape_diz_que_o_prazo_nao_corre_do_aviso` |
| **FR-1258** | I`templates/interface/aviso_previa.html` e `modelo_de_aviso.html` (orientação fixa) | TT `test_a_previa_diz_o_numero_a_orientacao_o_rodape_e_a_irreversibilidade` |
| **FR-1259** | A`application/previa.py` `assinatura`, `compor` | TR `test_previa_defasada_e_recusada`; TT |
| **FR-1260** | A`application/modelos.py`; `ModeloDeAviso.delete()` e gatilho | TM; TU `test_append_only.py` |
| **FR-1260a** | A`domain/modelos_iniciais.py`; `garantir_modelos_iniciais` no `sincronizar_unidades` | TM `test_os_tres_iniciais_nascem_ativos_na_primeira_sincronizacao`, `test_duas_sincronizacoes_ao_mesmo_tempo_nao_duplicam`, `test_o_texto_editado_nao_e_sobrescrito`; TU `test_modelos_iniciais.py` |
| **FR-1261** | `Aviso.assunto` e `Aviso.corpo` congelados; `salvar_como_novo_modelo` | TM `test_editar_o_modelo_nao_muda_o_aviso_enviado` |
| **FR-1262** | `confirmar_aviso_do_resultado` (justificativa) | TR `test_com_justificativa_e_reenvio_ligado_ao_anterior`; TC `test_avisar_de_novo_exige_justificativa` |
| **FR-1263** | `comando_de_aviso` reserva a idempotência | TR `test_o_duplo_clique_devolve_o_mesmo_aviso` |
| **FR-1264** | `confirmar_reenvio`, `universo_do_reenvio`, `ALCANCE_DO_REENVIO` | TJ `test_o_expirado_so_volta_por_aviso_filho`, `test_o_segundo_reenvio_de_falhas_do_mesmo_aviso_e_recusado`, `test_o_que_o_reenvio_nao_entregou_se_reenvia_a_partir_dele`; TT `test_o_reenvio_de_falhas_mostra_o_texto_do_anterior_sem_edicao`, `test_o_reenvio_de_falhas_feito_some_do_pai_e_vira_link` |
| **FR-1265** | A confirmação não envia; `despachar_avisos` | TR `test_a_confirmacao_nao_envia_nada`; TD |
| **FR-1266** | A`application/despacho.py` `_iniciar` antes do envio | TF `test_tentativa_orfa_e_marcada_indeterminada_e_nao_se_repete` |
| **FR-1267** | `_marcar_orfas`; `resposta.do_envio` | TF `test_aceita_e_derruba_e_indeterminada_para_a_execucao_e_nunca_se_repete`; TU `test_resposta.py` |
| **FR-1268** | `_trava_global`; `UNIQUE (destinatario, numero)` | TX `test_duas_execucoes_ao_mesmo_tempo_uma_sai_pela_trava`, `test_a_mesma_tentativa_duas_vezes_e_barrada_pelo_banco` |
| **FR-1269** | A`domain/resposta.py` pela fase; `estado.proxima_tentativa_em` | TU `test_resposta.py`, `test_estado.py`; TF `test_falha_temporaria_espera_o_intervalo_e_esgota_no_limite`, `test_recusa_5xx_e_definitiva_e_nao_se_tenta` |
| **FR-1270** | `AVISOS_LIMITE_POR_MINUTO`; `EMAIL_TIMEOUT` | TD `test_o_limite_por_execucao`; `unit/test_configuracao_de_correio.py` |
| **FR-1271** | `_mensagem`: um `to`, sem `cc` nem `bcc` | TD `test_uma_mensagem_por_destinatario_com_um_endereco_so` |
| **FR-1272** | A`application/selectors.py` `despacho_parado` | TT `test_o_alerta_de_despacho_parado_aparece_depois_do_limite` |
| **FR-1273** | A`application/interromper.py`; `travar_o_aviso` antes de cada tentativa | TX `test_interromper_no_meio_da_execucao_impede_a_tentativa_seguinte`, `test_aviso_interrompido_nao_tenta_os_pendentes` |
| **FR-1274** | `base_do_aviso` pela origem (`D-004`) | TA `test_a_porta_por_origem` |
| **FR-1275** | I`identidade.py` `PAPEIS` | TP |
| **FR-1276** | filtro por `institution_scope` em toda consulta | TA `test_outra_unidade_e_inexistente`; TT `test_outra_unidade_e_inexistente`; TM `test_outra_unidade_nao_ve_o_modelo` |
| **FR-1277** | seis tabelas em `TABELAS_APPEND_ONLY` com gatilho; `ModeloDeAviso` com `record_event` | TU `test_append_only.py`; `migrations/test_migrations.py`; `integration/test_database_permissions.py`; TM `test_cada_mudanca_vai_a_trilha_com_antes_e_depois` |
| **FR-1278** | `_gravar` com `auditar` sem endereço | TR `test_a_trilha_nao_copia_os_enderecos` |
| **FR-1279** | `resposta` sem o texto do servidor | TU `test_resposta.py` `test_o_detalhe_nao_leva_o_endereco`; TF `test_o_detalhe_tecnico_nao_leva_endereco_nem_nome` |
| **FR-1280** | `test_situacoes_de_mensagem.py` com quatro situações e a revisão da `066` | TS |
| **FR-1281** | `get_connection()` no despacho | TG |
| **FR-1282** | `recusar_se_desabilitado`; `despachar` desabilitado | TA `test_chave_desligada_recusa_antes_de_tudo`; TJ `test_desligada_o_despacho_nao_tenta_nada`, `test_desligada_o_reenvio_e_recusado`, `test_desligada_o_historico_continua_legivel`; TT `test_a_chave_desligada_explica_e_nao_oferece_formulario`, `test_a_chave_desligada_ainda_oferece_interromper` |
| **FR-1283** | A`domain/estado.py` `janela_passou`, `EXPIRADA_SEM_ENVIO` | TU `test_estado.py` `TestAJanela`; TJ `test_religada_fora_da_janela_expira_sem_envio`, `test_o_timer_parado_por_dias_nao_dispara_o_antigo`; TD `test_janela_vencida_expira_sem_envio` |

## 2. Experiência e linguagem

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **UX-171** | "aviso" em todas as telas e mensagens | TV |
| **UX-172** | `nomes.ROTULO_DO_ESTADO` | TV; TT `test_confirmar_pela_tela_leva_ao_historico` |
| **UX-173** | `aviso_previa.html` "Enviar a N pessoas" e a seção de consequências | TT `test_a_previa_diz_o_numero_a_orientacao_o_rodape_e_a_irreversibilidade` |
| **UX-174** | `publicacoes_do_marco.html`; `convocacao.html` (`chamadas_publicadas`) | TT `test_o_historico_do_marco_oferece_avisar_a_quem_publica`, `test_quem_so_audita_nao_ve_o_botao`; TC `test_a_tela_da_convocacao_oferece_o_aviso_por_publicacao` |
| **UX-175** | `contexto_do_marco`, `linha_de_estado` | TT `test_o_historico_do_marco_oferece_avisar_a_quem_publica` |
| **UX-176** | lista de variáveis e rodapé fixo no editor | TT `test_a_previa_diz_o_numero_a_orientacao_o_rodape_e_a_irreversibilidade` |
| **UX-177** | `aviso_interromper.html` | TT `test_interromper_diz_que_o_aceito_nao_volta` |
| **UX-178** | `aviso_previa.html`, contagem de não elegíveis com motivo | TC `test_o_universo_e_a_publicacao_inteira_e_a_mensagem_vai_a_quem_segue` |

## 3. Critérios de sucesso

| Identificador | Como se mede | Onde |
|---|---|---|
| **SC-481** | nenhuma mensagem fora do ato, uma por inscrição | TR; TD; TX |
| **SC-482** | confirmação de 1.002 destinatários em menos de 2 s, com as mesmas consultas | TO `test_a_confirmacao_nao_cresce_e_responde_em_menos_de_dois_segundos` |
| **SC-483** | 500 destinatários, limite 60, em 9 execuções | TF `test_quinhentos_com_o_limite_inicial_terminam_em_nove_execucoes` |
| **SC-484** | nenhuma indeterminada repetida, nenhuma duplicada | TF; TX |
| **SC-485** | compor e confirmar a partir de um modelo em até 3 minutos | `verificacao.md`, roteiro §1 |
| **SC-486** | nenhuma superfície diz entregue, recebida ou lida | TV |
| **SC-487** | outra unidade responde como inexistente | TA; TT; TM |
| **SC-488** | nenhum teste alcança servidor real | TG |
