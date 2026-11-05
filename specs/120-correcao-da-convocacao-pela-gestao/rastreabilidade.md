# Rastreabilidade: A correção da convocação pela gestão (120)

Cada requisito → o teste que o verifica. As tarefas entram pela `/speckit-tasks`, depois da aprovação
do plano; os nomes dos testes abaixo são os planejados, e a implementação os confirma ou os corrige
aqui. Caminhos relativos a `backend/tests/`. Abreviações:

- `up` = `unit/convocacao/test_correcao_pura.py` — espécie da sucessora e assinatura
- `sv` = `integration/convocacao/test_correcao_da_convocacao.py` — o comando e o fluxo
- `it` = `interface/test_correcao_da_convocacao.py` — a tela da condução
- `pf` = `performance/test_convocacao.py`
- `js` = `javascript/correcao-da-convocacao.test.js`
- `nv` = `navegador/test_jornada_da_correcao_da_convocacao.py` — Chromium, gestão em desktop, portal a 375 px
- `pc` = `integration/requerimentos/test_prazo_da_chamada.py` — já existe
- `vc` = `test_vocabulario_da_convocacao.py` — já existe
- `vf` = `verificacao.md` — a demonstração humana, com capturas

## Requisitos funcionais

| Requisito | Testes |
|---|---|
| FR-3837 (a ação nos três estados em aberto, para quem pode convocar) | `it::test_a_acao_aparece_com_prazo_em_curso`, `::test_a_acao_aparece_com_vencimento_decorrido`, `::test_a_acao_aparece_sem_comunicacao_enviada` |
| FR-3838 (a ação ausente: desfecho, sucedida, sem vencimento, Processo final, quem só lê) | `it::test_sem_acao_na_chamada_com_desfecho`, `::test_sem_acao_na_chamada_sem_vencimento`, `::test_sem_acao_com_o_processo_encerrado`, `::test_sem_acao_para_o_membro_da_conferencia`, `::test_sem_acao_para_a_auditoria`, `::test_a_sucedida_nao_tem_cartao` |
| FR-3839 (o recorte impedido: limitação, causa e caminho, sem formulário) | `it::test_apuracao_superada_mostra_a_limitacao_e_o_caminho`, `::test_apuracao_ausente_mostra_a_limitacao`, `::test_ordem_nao_vigente_mostra_a_limitacao`; `nv::test_com_a_apuracao_superada_nenhum_cartao_oferece_formulario` |
| FR-3840 (motivo obrigatório) | `sv::test_sem_motivo_a_correcao_e_recusada_pelo_campo`; `it::test_motivo_vazio_volta_ao_cartao_com_o_vencimento` |
| FR-3841 (vencimento obrigatório e futuro, sem pré-preenchimento) | `sv::test_sem_vencimento_a_correcao_e_recusada_pelo_campo`, `::test_vencimento_passado_e_recusado`; `it::test_o_vencimento_nao_vem_preenchido`, `::test_vencimento_passado_volta_ao_cartao_com_o_motivo` |
| FR-3842 (complemento opcional, gravado com o derivado) | `sv::test_o_complemento_entra_no_fundamento_gravado` |
| FR-3843 (a convocação nomeada, conferida sob a trava) | `sv::test_a_nomeada_sucedida_e_recusada_e_nao_corrige_a_sucessora`, `::test_a_nomeada_com_desfecho_e_recusada_e_nao_pratica_chamada_nova`, `::test_a_nomeada_de_outra_inscricao_e_nao_encontrada`, `::test_a_nomeada_de_outro_recorte_e_nao_encontrada`, `::test_duas_correcoes_concorrentes_so_uma_grava` |
| FR-3844 (a prévia: pessoa, chamada, vencimento, espécie, fundamento, forma, efeito, o que reabre, o que continua) | `it::test_a_previa_mostra_cada_valor_com_a_origem`, `::test_a_previa_diz_que_reabre_so_na_chamada_vencida`, `::test_a_previa_diz_a_comunicacao_pela_forma`, `::test_a_previa_diz_as_tres_regras_sem_vencimento`; `js::estende`, `js::antecipa`, `js::mantem`, `js::pelo_evento`, `js::sem_valor` |
| FR-3845 (irreversibilidade; o botão com o protocolo) | `it::test_o_formulario_declara_a_irreversibilidade`, `::test_o_botao_nomeia_o_protocolo` |
| FR-3846 (pelo comando de convocar; nada novo além das duas conferências) | `sv::test_a_sucessora_aponta_a_corrigida_e_reaproveita_a_chamada`; `test_dependencia_da_convocacao.py` (já existe) |
| FR-3847 (403 sem base; 404 fora do escopo; nada gravado) | `it::test_o_post_sem_base_recebe_403_e_nada_grava`, `::test_o_post_de_outra_unidade_recebe_404_e_nada_grava` |
| FR-3848 (sem duplicidade; a repetição devolve o primeiro resultado) | `sv::test_a_repeticao_devolve_o_resultado_por_mensagem_individual`, `::test_a_repeticao_devolve_o_resultado_por_publicacao`, `::test_a_repeticao_devolve_a_falha_sem_reenviar`; `it::test_o_duplo_post_corrige_uma_vez` |
| FR-3849 (o resultado: dois vencimentos, o efeito, a comunicação; o cartão da sucessora) | `it::test_o_resultado_diz_estendido`, `::test_o_resultado_diz_antecipado`, `::test_o_resultado_diz_mantido`, `::test_o_cartao_mostra_a_sucessora_corrigida` |
| FR-3850 (a recusa no cartão, com os campos; o cartão que mudou) | `it::test_a_recusa_do_dominio_volta_ao_cartao_com_os_campos`, `::test_o_cartao_sucedido_cita_o_motivo_e_nao_o_preenche`, `::test_o_cartao_com_desfecho_cita_o_motivo_sem_formulario` |
| FR-3851 (a trilha) | `sv::test_a_trilha_nomeia_a_corrigida_o_motivo_e_os_dois_vencimentos` |
| FR-3852 (o histórico, N + 1 linhas) | `it::test_duas_correcoes_deixam_tres_linhas_no_historico` |
| FR-3853 (filas e lote não mudam) | `it::test_quem_tem_chamada_em_aberto_continua_fora_da_fila`; `sv::test_o_lote_continua_sem_sucessao` |
| FR-3854 (o portal pelas regras de hoje; a US2 é condição de conclusão) | `nv::test_corrigida_na_gestao_o_convocado_complementa_e_envia`; `pc::test_a_correcao_com_vencimento_novo_reabre` (já existe); `vf` |
| FR-3855 (sem consulta por cartão) | `pf::test_a_correcao_nao_custa_consulta_por_cartao` |
| FR-3856 (o nome do ato; sem "prorrogação") | `it::test_o_ato_se_chama_corrigir_esta_convocacao`; `vc` (o parcial novo entra na lista) |
| FR-3857 (a prévia confirmada) | `up::test_a_assinatura_muda_com_cada_componente`, `::test_a_assinatura_nao_muda_com_o_complemento`; `sv::test_apuracao_seguinte_no_intervalo_recusa_a_previa`, `::test_retificacao_no_intervalo_recusa_a_previa`, `::test_especie_mudada_no_intervalo_recusa_a_previa`; `it::test_a_previa_superada_volta_com_a_previa_nova_e_os_campos` |

## Critérios de sucesso

| Critério | Testes |
|---|---|
| SC-1141 (um envio, pela tela, nos três estados) | `nv::test_corrigida_na_gestao_o_convocado_complementa_e_envia`; `it::test_a_acao_aparece_*`; `vf` |
| SC-1142 (a jornada ao portal, e o fechamento de novo depois do vencimento novo) | `nv::test_corrigida_na_gestao_o_convocado_complementa_e_envia`; `sv::test_vencido_o_novo_prazo_tudo_fecha_junto`; `vf` |
| SC-1143 (cada recusa grava zero) | `sv::test_nenhuma_recusa_grava_convocacao_comunicacao_nem_trilha` (parametrizado pelas recusas); `it::test_o_post_sem_base_*`, `::test_o_post_de_outra_unidade_*` |
| SC-1144 (dois envios: uma sucessora, um evento, no máximo uma mensagem, nos três resultados) | `sv::test_a_repeticao_devolve_o_resultado_por_*`, `::test_a_repeticao_devolve_a_falha_sem_reenviar` |
| SC-1145 (duas correções: três linhas; lista, apresentações e conferências iguais) | `it::test_duas_correcoes_deixam_tres_linhas_no_historico`; `sv::test_a_correcao_nao_toca_lista_apresentacoes_nem_conferencias` |
| SC-1146 (apuração superada: todos os cartões com a limitação, nenhum formulário) | `it::test_apuracao_superada_mostra_a_limitacao_e_o_caminho`; `nv::test_com_a_apuracao_superada_nenhum_cartao_oferece_formulario` |
| SC-1147 (mesmas consultas com 1 e com 20) | `pf::test_a_correcao_nao_custa_consulta_por_cartao` |
| SC-1148 (os campos sobrevivem à recusa) | `it::test_motivo_vazio_volta_ao_cartao_com_o_vencimento`, `::test_vencimento_passado_volta_ao_cartao_com_o_motivo`, `::test_a_recusa_do_dominio_volta_ao_cartao_com_os_campos`, `::test_a_previa_superada_volta_com_a_previa_nova_e_os_campos` |
| SC-1149 (um evento de trilha com ator, motivo, corrigida e vencimentos) | `sv::test_a_trilha_nomeia_a_corrigida_o_motivo_e_os_dois_vencimentos` |

## Casos-limite

Os casos-limite são requisitos sem identificador: cada um tem a sua linha, na ordem da spec.

| Caso-limite | Testes |
|---|---|
| Chamada sem comunicação enviada: corrigível; a comunicação pendente da corrigida sai da lista das que não saíram | `it::test_a_acao_aparece_sem_comunicacao_enviada`, `::test_a_pendente_da_corrigida_sai_das_comunicacoes_que_nao_sairam` |
| Correção em cadeia: a sucessora é corrigível; o número da chamada é o mesmo | `sv::test_a_sucessora_tambem_se_corrige_com_a_mesma_chamada` |
| Vencimento anterior ao atual, mas futuro: admitido, com o aviso e o resultado "antecipado" | `sv::test_vencimento_anterior_futuro_e_admitido`; `it::test_o_resultado_diz_antecipado`; `js::antecipa` |
| Chamada sem vencimento: sem ação | `it::test_sem_acao_na_chamada_sem_vencimento`; `sv::test_a_nomeada_sem_vencimento_e_recusada` |
| Chamada para regularizar em aberto: corrigível, com a espécie dela | `sv::test_a_chamada_para_regularizar_se_corrige_sem_a_guarda_de_ordem` |
| Espécie derivada diferente da corrigida: a sucessora leva a derivada, e a prévia mostra | `up::test_a_especie_da_sucessora_segue_a_posicao`; `it::test_a_previa_diz_quando_a_especie_muda` |
| Fundamento diferente: a prévia diz quando cita outra apuração ou versão | `it::test_a_previa_diz_quando_o_fundamento_muda` |
| Apuração seguinte, ou Retificação, entre a prévia e a confirmação: prévia superada | `sv::test_apuracao_seguinte_no_intervalo_recusa_a_previa`, `::test_retificacao_no_intervalo_recusa_a_previa`; `it::test_a_previa_superada_volta_com_a_previa_nova_e_os_campos` |
| O cartão mudou no intervalo: o motivo para copiar, o formulário da sucessora vazio | `it::test_o_cartao_sucedido_cita_o_motivo_e_nao_o_preenche`, `::test_o_cartao_com_desfecho_cita_o_motivo_sem_formulario` |
| Ordem sucedida, apuração ausente ou superada: limitação; no intervalo, a recusa com a orientação | `it::test_apuracao_superada_mostra_a_limitacao_e_o_caminho`, `::test_ordem_nao_vigente_mostra_a_limitacao`, `::test_impedimento_no_intervalo_volta_com_a_orientacao` |
| Processo em estado final: sem ação; o POST recusado | `it::test_sem_acao_com_o_processo_encerrado`; `sv::test_com_o_processo_encerrado_a_correcao_e_recusada` |
| Requerimento em rascunho: continua, e se envia depois da correção | `nv::test_corrigida_na_gestao_o_convocado_complementa_e_envia`; `pc::test_o_rascunho_feito_no_prazo_continua_legivel_e_nao_se_envia` (já existe) |
| Conferências da chamada: conforme continua conforme; pendente continua pendente, e a complementação entra para conferência | `sv::test_a_correcao_nao_toca_lista_apresentacoes_nem_conferencias`; `nv::test_corrigida_na_gestao_o_convocado_complementa_e_envia` |
| Desfecho que inclui, depois da correção: na sucessora, com a pendência bloqueando o aceite | `sv::test_o_desfecho_se_registra_na_sucessora_e_a_pendencia_bloqueia` |
| Membro alocado à conferência: lê, sem ação; POST 403 | `it::test_sem_acao_para_o_membro_da_conferencia`, `::test_o_post_sem_base_recebe_403_e_nada_grava` |

## Identificadores

| Identificador | Situação |
|---|---|
| FR-3837, SC-1141 | a abertura da faixa, citada no cabeçalho da spec; são requisitos, cobertos acima |
| UX- | nenhum aberto |
