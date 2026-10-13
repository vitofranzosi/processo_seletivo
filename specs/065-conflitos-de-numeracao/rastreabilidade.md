# Rastreabilidade — 065, conflitos de numeração

Cada requisito, critério, decisão e caso-limite da spec, com o teste que o prende. Os casos-limite
entram aqui porque nenhuma ferramenta os cobra (nota em *Assumptions* da spec).

> **Nota da `067` (09/10/2026).** `test_o_documento_publicado_na_auditoria_sai_com_os_mesmos_bytes`
> foi renomeado para `test_o_documento_da_auditoria_sai_com_os_bytes_esperados_depois_da_067`: a
> `067` muda o documento de propósito (ED-02, ED-03, ED-12), e os bytes esperados passaram a ser os
> de `specs/067-correcoes-de-norma-do-edital/demonstracao/`. A prova de `FR-1219` sobre a composição
> da `065` continua na fixture de contrato, que não mudou.

**Arquivos de teste**

| Sigla | Arquivo |
|---|---|
| ND | `backend/tests/unit/editais/test_numeracao_digitada.py` |
| CN | `backend/tests/unit/editais/test_conflito_de_numeracao.py` |
| RM | `backend/tests/unit/editais/test_remissoes.py` |
| ID | `backend/tests/unit/publicacoes/test_itens_do_documento.py` |
| NR | `backend/tests/interface/test_numeracao_na_revisao.py` |
| NP | `backend/tests/integration/publicacoes/test_numeracao_na_publicacao.py` |
| CT | `backend/tests/contract/test_documento_publicado.py` (inalterado) |

## Requisitos funcionais

| Requisito | O que prende | Teste |
|---|---|---|
| FR-1198 | parágrafos da composição, texto normalizado | CN `test_linha_em_branco_nao_conta_como_paragrafo`, `test_zero_a_esquerda_e_invisivel_colado_nao_sao_conflito` |
| FR-1199 | forma do número de subitem e os legítimos, inclusive os intervalos de hora e de data | ND `test_reconhece_o_numero_de_subitem`, `test_numero_legitimo_nao_e_subitem` (49 casos), `test_o_intervalo_so_e_excluido_pela_expressao_inteira` |
| FR-1200 | conflito comprovado, inclusive no preâmbulo | CN `test_subitens_de_outra_secao_sao_um_conflito_comprovado_e_impeditivo`, `test_subitem_no_preambulo_e_conflito` |
| FR-1201 | título transcrito como suspeita | ND `test_reconhece_o_titulo_transcrito`, `test_nao_e_titulo_transcrito`; CN `test_titulo_transcrito_com_outro_numero_e_suspeita` |
| FR-1202 | a numeração do momento | CN `test_a_conferencia_acompanha_a_numeracao_do_momento` |
| FR-1203 | nada é renumerado | NR `test_o_texto_gravado_e_o_que_foi_escrito` |
| FR-1204 | remissões e exclusões, em todo texto impresso | ND `test_reconhece_a_remissao_interna`, `test_remissao_a_outro_ato_ou_a_anexo_nao_e_deste_documento`; RM `test_a_remissao_e_procurada_em_todo_texto_impresso` |
| FR-1205 | itens do documento pela regra da composição | ID `test_os_itens_sao_os_que_a_composicao_escreve` (9 casos) |
| FR-1206 | remissão ambígua nomeia os itens | RM `test_numero_com_dois_itens_e_remissao_ambigua_que_nomeia_os_dois` |
| FR-1207 | remissão sem destino | RM `test_numero_sem_item_e_remissao_sem_destino` |
| FR-1208 | suspeitas (quadro; destino em conflito) | RM `test_quadro_e_suspeita`, `test_destino_unico_em_paragrafo_em_conflito_e_suspeita` |
| FR-1209 | destino único não gera achado | RM `test_destino_unico_coerente_nao_gera_achado`, `test_nenhuma_mensagem_diz_que_a_remissao_esta_certa` |
| FR-1210 | impeditivo no Edital | CN `test_subitens_de_outra_secao_sao_um_conflito_comprovado_e_impeditivo`; NP `test_a_submissao_com_conflito_e_recusada_nomeando_secao_e_paragrafos`, `test_a_publicacao_aplica_a_mesma_regra` |
| FR-1211 | remissões e suspeitas são avisos | RM `test_numero_com_dois_itens…`, `test_na_retificacao_as_remissoes_continuam_avisos`, `test_os_codigos_de_aviso_nao_coincidem_com_impeditivo_nenhum` |
| FR-1212 | superfícies, link à seção, recusa com a mesma mensagem | NR `test_o_conflito_aparece_na_etapa_na_revisao_e_no_edital`, `test_o_link_do_achado_leva_a_legenda_da_secao`, `test_a_submissao_e_recusada_e_corrigir_libera` |
| FR-1213 | na Retificação, só avisos | CN `test_na_retificacao_o_conflito_e_aviso_com_codigo_proprio`; NP `test_a_retificacao_que_desloca_a_numeracao_avisa_e_publica`, `test_a_retificacao_de_edital_que_ja_tinha_conflito_publica_com_aviso` |
| FR-1214 | o que a mensagem de numeração diz | CN `test_subitens_de_outra_secao…`, `test_o_trecho_e_cortado_em_fim_de_palavra_com_reticencias` |
| FR-1215 | um achado por seção | CN `test_subitens_de_outra_secao…` (um achado), `test_o_cenario_b_tem_os_cinco_conflitos_da_auditoria` |
| FR-1216 | o que a mensagem de remissão diz | RM `test_numero_com_dois_itens…` (literal, lugar, parágrafo, "não sabe") |
| FR-1217 | comprovado ou suspeita | CN `test_subitens_de_outra_secao…`, `test_titulo_transcrito_com_outro_numero_e_suspeita`; RM `test_quadro_e_suspeita` |
| FR-1218 | Edital publicado não é conferido | NP `test_o_edital_publicado_com_conflito_nao_e_reavaliado_nem_recomposto` |
| FR-1219 | o documento não muda | ID `test_o_documento_publicado_na_auditoria_sai_com_os_mesmos_bytes` (A e B); CT fixture de bytes |
| FR-1220 | nenhum dado novo | ID `test_a_funcao_nao_muda_o_snapshot`; nenhuma migration no diff |

## Requisitos de experiência

| Requisito | Teste |
|---|---|
| UX-159 | CN `test_a_mensagem_nao_tem_codigo_caminho_nem_campo`; NR `test_o_conflito_aparece_na_etapa…` |
| UX-160 | NR `test_o_conflito_aparece_na_etapa…` (número da legenda = número do achado), `test_o_link_do_achado_leva_a_legenda_da_secao` |
| UX-161 | NR `test_a_remissao_ambigua_vem_depois_do_conflito_da_mesma_secao`, `test_remissoes_repetidas_se_dobram_e_o_conflito_nunca` |

## Critérios de sucesso

| Critério | Teste ou medida |
|---|---|
| SC-462 | CN `test_o_cenario_b_tem_os_cinco_conflitos_da_auditoria`; fluxo real em [verificacao.md](verificacao.md) |
| SC-463 | RM `test_no_cenario_b_o_item_8_1_e_a_unica_remissao_ambigua` |
| SC-464 | ND `test_numero_legitimo_nao_e_subitem`, `test_o_conjunto_de_prova_tem_o_tamanho_que_a_spec_pede`; CN `test_o_cenario_a_nao_tem_achado_de_numeracao`; RM `test_no_cenario_a_nao_ha_remissao_a_acusar` |
| SC-465 | [verificacao.md](verificacao.md), cenário B corrigido |
| SC-466 | ID `test_o_documento_publicado_na_auditoria_sai_com_os_mesmos_bytes`; NP `test_o_edital_publicado_com_conflito…` |
| SC-467 | RM `test_nenhuma_mensagem_diz_que_a_remissao_esta_certa`, `test_destino_unico_coerente_nao_gera_achado` |
| SC-468 | CN `test_cada_trecho_do_cenario_b_esta_no_texto_cru_da_secao` |
| SC-469 | NP `test_a_submissao_com_conflito…`, `test_a_submissao_so_com_aviso_e_aceita_e_o_aviso_volta_na_resposta`; [verificacao.md](verificacao.md) |
| SC-470 | NP `test_a_retificacao_que_desloca_a_numeracao_avisa_e_publica`; [verificacao.md](verificacao.md) |

## Decisões

| Decisão | Teste |
|---|---|
| D-001 | CN `test_subitens_de_outra_secao…`; NP `test_a_submissao_com_conflito…` |
| D-002 | CN `test_na_retificacao_o_conflito_e_aviso_com_codigo_proprio`; NP as duas de Retificação |
| D-003 | RM `test_a_remissao_e_procurada_em_todo_texto_impresso`, `test_destino_unico_coerente_nao_gera_achado` |
| D-004 | ID `test_os_itens_sao_os_que_a_composicao_escreve` |
| D-005 | ND inteiro (sem banco) |
| D-006 | RM `test_os_codigos_de_aviso_nao_coincidem_com_impeditivo_nenhum`; NP `test_a_retificacao_que_desloca…` (o aviso não é subtraído). Prova de reprovação em [verificacao.md](verificacao.md) |
| D-007 | NR `test_a_remissao_ambigua_vem_depois_do_conflito_da_mesma_secao` |
| D-008 | NR `test_o_link_do_achado_leva_a_legenda_da_secao` |
| D-009 | CN `test_zero_a_esquerda_e_invisivel_colado…`, `test_o_trecho_e_cortado…` |
| D-010 | ND inteiro |
| D-011 | RM as três espécies e o destino único |
| D-012 | NP as duas de Retificação |
| D-013 | NP `test_o_edital_publicado_com_conflito…` |
| D-014 | ID `test_o_documento_publicado_na_auditoria…`; CT |
| D-015 | os testes de orçamento de consulta da interface, inalterados e verdes na suíte |
| D-016 | NR `test_remissoes_repetidas_se_dobram_e_o_conflito_nunca` |
| D-017 | ND `test_numero_legitimo_nao_e_subitem` (os cinco da revisão e três variações), `test_o_intervalo_so_e_excluido_pela_expressao_inteira`, `test_numero_maior_que_o_de_subitem_e_ignorado_inteiro`, `test_na_lista_so_o_numero_maior_e_ignorado`; CN `test_intervalo_de_hora_ou_de_data_nao_e_conflito_e_o_conflito_real_continua_impeditivo`; RM `test_remissao_acima_de_quatro_niveis_nao_vira_remissao_a_outro_item` |

## Casos-limite da spec

| Caso-limite | Teste |
|---|---|
| Data, número de lei, valor, hora, percentual, ordinal, decimal com unidade, processo/CEP/telefone, ano, lista de um nível | ND `test_numero_legitimo_nao_e_subitem` |
| Decimal com multiplicador; intervalo de horas; intervalo de datas | ND `test_numero_legitimo_nao_e_subitem`, `test_o_intervalo_so_e_excluido_pela_expressao_inteira`; CN `test_intervalo_de_hora_ou_de_data_nao_e_conflito…` |
| Invisível colado do Word; zero à esquerda | CN `test_zero_a_esquerda_e_invisivel_colado_nao_sao_conflito`; ND `04.1` |
| Subitem de três ou quatro níveis | ND `4.2.1`, `4.2.1.3` |
| Separadores depois do número | ND `4.1.`, `4.1)`, `4.1 –`, `4.1 -`, `4.1` |
| Marcador antes do número | ND `• 4.1`, espaços iniciais |
| Parágrafo como o documento o compõe | CN `test_linha_em_branco_nao_conta_como_paragrafo` |
| Seção misturada | CN `test_secao_misturada_acusa_so_os_de_outra_secao` |
| Seção vazia | CN `test_secao_vazia_nao_e_conferida` |
| Seção com norma acrescentada pelo sistema | CN `test_a_frase_do_teto_nao_e_lida_so_o_texto_do_autor` |
| Título do original colado (outro número / mesmo número) | CN `test_titulo_transcrito_com_outro_numero_e_suspeita`, `test_titulo_transcrito_com_o_mesmo_numero_fica_fora` |
| Edital criado a partir de outro | coberto pela regra, que lê o conteúdo do Edital novo; sem teste próprio — o reaproveitamento grava as seções como qualquer rascunho |
| Formas reconhecidas de remissão (lista, intervalo, Tabela, Quadro) | ND `test_reconhece_a_remissao_interna` |
| Remissão a outro ato ou a Anexo | ND `test_remissao_a_outro_ato…`; RM `test_remissao_a_outro_ato_ou_anexo_nao_e_conferida` |
| Remissão a subitem em conflito | RM `test_destino_unico_em_paragrafo_em_conflito_e_suspeita` |
| Remissão a nível único | RM `test_remissao_a_secao_so_e_acusada_acima_do_total` |
| Número maior que o de subitem | ND `test_numero_maior_que_o_de_subitem_e_ignorado_inteiro`, `test_na_lista_so_o_numero_maior_e_ignorado`; RM `test_remissao_acima_de_quatro_niveis…` |
| "Tabela N" | RM `test_tabela_so_e_acusada_acima_do_total` |
| Mesma remissão repetida | RM `test_a_mesma_remissao_na_mesma_secao_sai_uma_vez` |
| Onde se procura remissão | RM `test_a_remissao_e_procurada_em_todo_texto_impresso`, `test_o_rotulo_do_anexo_e_o_titulo_da_secao_nao_sao_remissao` |
| Achados refeitos a cada leitura | CN `test_a_conferencia_acompanha_a_numeracao_do_momento` |
| Prévia e documento sem marca | ID `test_o_documento_publicado_na_auditoria…`; CT |
| Edital publicado fora de Retificação | NP `test_o_edital_publicado_com_conflito…` |
| Retificação que introduz conflito | NP `test_a_retificacao_que_desloca_a_numeracao_avisa_e_publica`; [verificacao.md](verificacao.md) |
| Conteúdo malformado | CN `test_a_conferencia_nao_quebra_sobre_conteudo_malformado` |
