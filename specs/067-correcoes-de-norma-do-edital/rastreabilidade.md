# Rastreabilidade — 067, correções de norma do Edital em PDF

Cada requisito, critério, decisão e caso-limite da spec, com o teste que o prende. Os casos-limite
entram aqui porque nenhuma ferramenta os cobra (nota em *Assumptions* da spec).

**Arquivos de teste**

| Sigla | Arquivo |
|---|---|
| PR | `backend/tests/unit/editais/test_predicados_da_067.py` |
| FR | `backend/tests/unit/publicacoes/test_frase_de_recurso.py` |
| AS | `backend/tests/unit/editais/test_arredondamento_sob_sorteio.py` |
| DS | `backend/tests/unit/publicacoes/test_documento_sob_sorteio.py` |
| PV | `backend/tests/unit/publicacoes/test_perfil_sem_vaga_imediata.py` |
| CR | `backend/tests/unit/editais/test_conferencia_do_recurso.py` |
| TR | `backend/tests/interface/test_correcoes_de_norma_na_revisao.py` |
| EM | `backend/tests/integration/classificacao/test_emissao_de_marco_por_sorteio.py` |
| NP | `backend/tests/integration/publicacoes/test_correcoes_de_norma_na_publicacao.py` |
| DA | `backend/tests/unit/publicacoes/test_documento_da_auditoria_depois_da_067.py` |
| ID | `backend/tests/unit/publicacoes/test_itens_do_documento.py` (guardião da `065`, bytes esperados novos) |
| RV | `backend/tests/unit/interface/test_revisao.py` (atualizado de propósito) |
| CT | `backend/tests/contract/test_documento_publicado.py` (fixture de bytes **inalterada**) |

## Requisitos funcionais

| Requisito | O que prende | Teste |
|---|---|---|
| FR-1300 | afirmativa com o nome entre aspas; singular; extenso | FR `test_a_afirmativa_nomeia_o_resultado_entre_aspas`, `test_um_dia_e_singular`, `test_o_prazo_tem_a_grafia_do_documento` |
| FR-1301 | negativa com o nome | FR `test_a_negativa_tambem_nomeia_o_resultado` |
| FR-1302 | nome → código → frase de antes | FR `test_sem_nome_o_resultado_e_o_do_codigo`, `test_sem_nome_e_sem_codigo_a_frase_de_antes_e_a_previa_nao_inventa_nome` |
| FR-1303 | silêncio e prazo inválido sem frase | FR `test_o_silencio_e_o_prazo_invalido_continuam_sem_frase` |
| FR-1304 | uma frase para documento, prévia, consolidado e Revisão | FR `test_a_previa_imprime_a_mesma_frase`, `test_a_revisao_diz_o_resultado_pela_denominacao_da_linha_de_cima`; RV `test_a_classificacao_mostra_o_metodo_comum_e_o_que_o_marco_declara`; NP `test_o_publicado_antes_nao_muda_e_a_retificacao_sai_pelas_regras_novas` |
| FR-1305 | Evento de recurso por palavra iniciada por "recurs" | CR `test_o_evento_de_recurso_e_o_que_tem_palavra_iniciada_por_recurs` (8 casos) |
| FR-1306 | um aviso; regras agrupadas; Eventos na ordem; "N Perfis" | CR `test_o_cenario_a_tem_um_aviso_so_com_os_dois_lados`, `test_o_cenario_b_lista_os_quatro_eventos_na_ordem_e_resume_os_perfis`, `test_a_negativa_tambem_e_regra_de_recurso`, `test_mesmo_nome_e_prazos_diferentes_sao_duas_regras`, `test_cronograma_sem_evento_de_recurso_e_dito` |
| FR-1307 | a orientação, sem afirmar correspondência | CR `test_o_cenario_a_tem_um_aviso_so_com_os_dois_lados` (mensagem literal), `test_cronograma_sem_evento_de_recurso_e_dito` |
| FR-1308 | sem regra em marco, sem aviso | CR `test_sem_regra_de_recurso_em_marco_nenhum_nao_ha_aviso_mesmo_com_eventos_de_recurso` |
| FR-1309 | aviso em todo ato, nunca impede | CR `test_na_retificacao_continua_aviso`; NP `test_a_submissao_devolve_o_aviso_e_o_edital_publica`, `test_o_edital_com_o_aviso_e_o_sorteio_sem_arredondamento_publica_e_imprime_o_novo`, `test_o_publicado_antes_nao_muda_e_a_retificacao_sai_pelas_regras_novas`; TR `test_a_revisao_mostra_o_aviso_com_link_para_o_cronograma_e_nao_impede` |
| FR-1310 | o aviso não muda nada | CR `test_a_conferencia_nao_altera_o_conteudo` |
| FR-1311 | sob sorteio declarado a ausência não é recusada; pontuação e acervo continuam | AS `test_sob_sorteio_a_ausencia_nao_e_recusada` (8 casos), `test_sob_pontuacao_a_ausencia_continua_recusada`, `test_sem_forma_declarada_a_ausencia_continua_recusada_mesmo_com_metodo_proprio` |
| FR-1312 | o declarado continua conferido na forma | AS `test_sob_sorteio_o_declarado_continua_conferido_na_forma` (5 casos) |
| FR-1313 | sem "Arredondamento" sob sorteio, declarado ou não | DS `test_sob_sorteio_declarado_nem_arredondamento_nem_empate_mesmo_declarados`, `test_o_cenario_a_da_auditoria_nao_tem_nenhuma_das_duas_linhas` |
| FR-1314 | sem "Empate no corte" sob sorteio | DS os mesmos; `test_sob_pontuacao_os_dois_continuam` (contraprova) |
| FR-1315 | a Revisão segue o documento | TR `test_a_revisao_do_marco_por_sorteio_nao_lista_arredondamento_nem_empate`, `test_a_revisao_do_marco_por_pontuacao_continua_listando`; RV `test_a_classificacao_mostra_o_metodo_comum_e_o_que_o_marco_declara` |
| FR-1316 | o cartão não mostra nem grava; volta preenchido | TR `test_o_cartao_por_sorteio_nao_mostra_o_arredondamento_e_o_leva_oculto`, `test_o_cartao_por_sorteio_leva_oculto_o_arredondamento_que_o_marco_tinha`, `test_ao_passar_para_pontuacao_os_campos_voltam_preenchidos`, `test_salvar_o_marco_por_sorteio_nao_grava_arredondamento` |
| FR-1317 | a dica de vazio da Retificação | TR `test_na_retificacao_o_vazio_do_modo_sob_sorteio_nao_anuncia_impedimento`, `test_na_retificacao_o_vazio_do_modo_sob_pontuacao_continua_anunciando` |
| FR-1318 | a emissão recusa antes de calcular | EM `test_a_emissao_recusa_o_sorteio_antes_de_calcular`, `test_o_calculo_de_um_marco_por_sorteio_sem_arredondamento_quebraria` |
| FR-1319 | o sorteio e a divulgação não leem arredondamento | EM `test_o_sorteio_sem_arredondamento_produz_a_ordem_do_algoritmo`, `test_a_divulgacao_nao_depende_do_arredondamento_do_marco_por_sorteio` |
| FR-1320 | o predicado | PR `test_sem_vaga_imediata` (9 casos) |
| FR-1321 | sem quadro nem reversão; tabelas sem lacuna; contagem da `065` | PV `test_sem_vaga_imediata_nem_quadro_nem_reversao_e_o_resto_fica`, `test_as_tabelas_seguintes_sao_numeradas_sem_lacuna`, `test_a_contagem_de_tabelas_segue_o_documento`, `test_a_contagem_de_tabelas_dos_cenarios_segue_o_documento`; ID (guardião, verde) |
| FR-1322 | o resto fica; nenhuma frase nova | PV `test_sem_vaga_imediata_nem_quadro_nem_reversao_e_o_resto_fica`, `test_nenhuma_frase_nova_sobre_a_reserva_no_cadastro` |
| FR-1323 | com vaga, quadro inteiro e reversão | PV `test_com_vaga_o_quadro_sai_inteiro_com_a_linha_em_zero_e_a_reversao` |
| FR-1324 | a validação do Perfil sem vaga não muda | PV `test_a_validacao_do_perfil_sem_vaga_nao_muda` |
| FR-1325 | documento gerado não é recomposto | NP `test_o_publicado_antes_nao_muda_e_a_retificacao_sai_pelas_regras_novas` (bytes servidos e gravados) |
| FR-1326 | composto depois sai pelas regras novas, inclusive o consolidado | NP o mesmo; cenário A retificado pelo fluxo real ([verificacao.md](verificacao.md)) |
| FR-1327 | a forma do conteúdo não muda | NP o mesmo (`canonical_schema_version`); nenhuma migration no diff |
| FR-1328 | publicado não é reavaliado | NP `test_a_pagina_do_edital_publicado_nao_mostra_o_aviso` |

## Requisitos de experiência

| Requisito | Teste |
|---|---|
| UX-190 | CR `test_a_mensagem_nao_tem_codigo_caminho_nem_nome_de_campo` |
| UX-191 | TR `test_a_revisao_mostra_o_aviso_com_link_para_o_cronograma_e_nao_impede` |
| UX-192 | TR `test_a_reversao_do_perfil_sem_vaga_diz_que_nao_sai_no_documento`, `test_a_reversao_do_perfil_com_vaga_nao_tem_a_nota` |
| UX-193 | TR `test_a_ajuda_diz_que_o_arredondamento_e_da_ordem_por_pontuacao` |

## Critérios de sucesso

| Critério | Evidência |
|---|---|
| SC-500 | FR `test_o_documento_do_cenario_a_nomeia_o_resultado_nos_quatro_marcos`; DS `test_o_cenario_a_da_auditoria_nao_tem_nenhuma_das_duas_linhas`; cenário A pelo fluxo real |
| SC-501 | PV `test_o_cenario_b_tem_dois_quadros_e_duas_reversoes`; cenário B pelo fluxo real (44 → 36 páginas) |
| SC-502 | DA `test_a_diferenca_do_cenario_a_e_so_a_pretendida`, `test_a_diferenca_do_cenario_b_e_so_a_pretendida`; a mesma regra sobre os PDFs do fluxo real, antes × depois |
| SC-503 | AS; NP `test_a_submissao_devolve_o_aviso_e_o_edital_publica`; cenário A sem arredondamento: recusado na `main`, publicado na `067` |
| SC-504 | CR (cenários A e B); TR; cenários pelo fluxo real (o aviso na submissão) |
| SC-505 | CT `test_o_documento_publicado_continua_byte_a_byte_o_mesmo`, sem tocar a fixture |
| SC-506 | NP `test_o_publicado_antes_nao_muda_e_a_retificacao_sai_pelas_regras_novas`; A publicado na `main` e retificado na `067`, SHA-256 do original igual antes e depois |
| SC-507 | `make lint check test-pg` ([verificacao.md](verificacao.md)) |

## Decisões

| Decisão | Teste |
|---|---|
| D-001 | FR (as frases, literais) |
| D-002 | CR; NP (nunca impede) |
| D-003 | PV `test_nenhuma_frase_nova_sobre_a_reserva_no_cadastro` |
| D-004 | PR `test_sorteio_e_a_forma_declarada`; AS e DS (acervo sem forma) |
| D-005 | FR `test_o_prazo_tem_a_grafia_do_documento`; CR (mesmo prazo no aviso) |
| D-006 | CR (código, caminho, severidade); NP (`advertencias_do_ato` mostra) |
| D-007 | PR `test_sem_vaga_imediata`; PV `test_a_contagem_de_tabelas_segue_o_documento` |
| D-008 | TR (cartão: oculto, gravação, volta) |
| D-009 | EM `test_a_emissao_recusa_o_sorteio_antes_de_calcular` |
| D-010 | DA; ID; CT |
| D-011 | NP `test_o_publicado_antes_nao_muda_e_a_retificacao_sai_pelas_regras_novas` |
| D-012 | FR `test_a_revisao_diz_o_resultado_pela_denominacao_da_linha_de_cima`; RV `test_marcos_iguais_em_perfis_diferentes_aparecem_uma_vez`, `test_o_marco_que_diverge_diz_em_que` (verdes) |

## Casos-limite

| Caso | Teste |
|---|---|
| Marco sem nome; sem nome e sem código | FR `test_sem_nome_o_resultado_e_o_do_codigo`, `test_sem_nome_e_sem_codigo_a_frase_de_antes_e_a_previa_nao_inventa_nome` |
| Nome com aspas | FR `test_o_nome_e_aparado_e_sai_como_foi_escrito_inclusive_com_aspas` |
| Nome longo | FR `test_o_nome_longo_quebra_sem_ser_truncado` |
| Prazo fora da tabela de extenso | FR `test_o_prazo_tem_a_grafia_do_documento[11-…]` |
| Unidade do prazo | só dias corridos existe; a frase não lê `unit` (FR, todos os casos com `DIAS_CORRIDOS`) |
| Dois marcos no mesmo Perfil | FR `test_dois_marcos_no_mesmo_perfil_nomeiam_cada_um_o_seu_resultado` |
| O mesmo marco em vários Perfis | FR `test_o_documento_do_cenario_a_nomeia_o_resultado_nos_quatro_marcos` |
| "Prazo recursal" conta; "Concurso", "percurso" não | CR `test_o_evento_de_recurso_e_o_que_tem_palavra_iniciada_por_recurs` |
| Evento cancelado | CR `test_o_evento_cancelado_continua_listado_como_o_documento_o_imprime` |
| Evento de um instante | CR `test_evento_sem_termino_e_dito_pelo_inicio` |
| Mesmo nome e mesmo prazo → uma linha; prazos diferentes → duas | CR `test_o_cenario_a_tem_um_aviso_so_com_os_dois_lados`, `test_mesmo_nome_e_prazos_diferentes_sao_duas_regras` |
| Marco que nega recurso entra no aviso | CR `test_a_negativa_tambem_e_regra_de_recurso` |
| Nenhum marco declara recurso | CR `test_sem_regra_de_recurso_em_marco_nenhum_nao_ha_aviso_mesmo_com_eventos_de_recurso` |
| Retificação: aviso, nunca impede | CR `test_na_retificacao_continua_aviso`; NP |
| Edital publicado: sem aviso | NP `test_a_pagina_do_edital_publicado_nao_mostra_o_aviso` |
| Marco sem forma declarada (acervo) | AS `test_sem_forma_declarada_…`; DS `test_o_acervo_sem_forma_declarada_sai_como_sempre_saiu` |
| Arredondamento malformado sob sorteio | AS `test_sob_sorteio_o_declarado_continua_conferido_na_forma` |
| Retificação de pontuação para sorteio | DS `test_sob_sorteio_declarado_nem_arredondamento_nem_empate_mesmo_declarados` (o declarado não sai) |
| Retificação de sorteio para pontuação sem arredondamento | AS `test_a_retificacao_que_passa_de_sorteio_para_pontuacao_sem_arredondamento_e_recusada` |
| Troca da forma na tela | TR `test_ao_passar_para_pontuacao_os_campos_voltam_preenchidos`, `test_o_cartao_por_sorteio_leva_oculto_o_arredondamento_que_o_marco_tinha` |
| Perfil incoerente (total 0, linha positiva) | PR; PV `test_o_incoerente_continua_com_quadro_para_que_o_erro_se_veja` |
| Sem vaga e sem cadastro | PR; PV `test_sem_vaga_e_sem_cadastro_tambem_nao_tem_quadro_nem_reversao` |
| Perfil sem quadro declarado | PR `test_sem_vaga_imediata` (ausente e `[]` → falso); o quadro já não saía |
| Tabela de Perfis e linha de total | PV `test_a_tabela_de_perfis_continua_sem_total_quando_o_edital_nao_tem_vaga` |
| Numeração das tabelas | PV `test_as_tabelas_seguintes_sao_numeradas_sem_lacuna`; ID |
| Validação do Perfil sem vaga | PV `test_a_validacao_do_perfil_sem_vaga_nao_muda` |
