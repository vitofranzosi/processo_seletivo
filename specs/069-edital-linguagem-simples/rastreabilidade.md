# Rastreabilidade — 069, Edital oficial em linguagem simples (lote 1)

Cada requisito, critério, decisão e caso-limite da spec, com o teste que o prende. Os casos-limite
entram aqui porque nenhuma ferramenta os cobra. A faixa da `069` abre em **FR-1360** e **SC-516**; os
números são globais desde a `024`.

**Arquivos de teste**

| Sigla | Arquivo |
|---|---|
| RF | `backend/tests/unit/publicacoes/test_redacao_das_frases.py` (uma linha por variante do contrato de redação) |
| RD | `backend/tests/unit/publicacoes/test_redacao_no_documento.py` |
| RP | `backend/tests/integration/publicacoes/test_redacao_da_publicacao.py` |
| AO | `backend/tests/integration/classificacao/test_redacao_do_ato_publicado.py` |
| AC | `backend/tests/integration/publicacoes/test_acervo_da_069.py` |
| CB | `backend/tests/contract/test_comprovante_e_divulgacao_byte_a_byte.py` |
| FE | `backend/tests/unit/publicacoes/test_fonte_embutida.py` |
| HI | `backend/tests/unit/publicacoes/test_hierarquia_do_documento.py` |
| ME | `backend/tests/unit/publicacoes/test_metrica_do_documento.py` |
| CA | `backend/tests/unit/editais/test_catalogo_apresentado.py` |
| NA | `backend/tests/unit/publicacoes/test_numeracao_apresentada.py` |
| NC | `backend/tests/unit/editais/test_numeracao_apresentada_nas_conferencias.py` |
| AP | `backend/tests/unit/publicacoes/test_apresentacao_por_perguntas.py` |
| RE | `backend/tests/unit/publicacoes/test_resumo_do_edital.py` |
| AG | `backend/tests/unit/publicacoes/test_agrupamento_seguro.py` |
| RA | `backend/tests/integration/publicacoes/test_retificacao_de_edital_antigo.py` |
| RT | `backend/tests/unit/editais/test_remissao_pelo_titulo.py` |
| AR | `backend/tests/interface/test_aviso_de_remissao_na_revisao.py` |
| PG | `backend/tests/unit/publicacoes/test_paginacao_do_edital.py` |
| AQ | `backend/tests/unit/publicacoes/test_arquivo_do_edital.py` |
| NO | `backend/tests/integration/publicacoes/test_nome_do_arquivo.py` |
| DA | `backend/tests/unit/publicacoes/test_documento_da_auditoria_depois_da_069.py` |
| ID | `backend/tests/unit/publicacoes/test_itens_do_documento.py` (guardião da `065`, nas duas apresentações) |
| RV | `backend/tests/unit/interface/test_revisao.py`, `backend/tests/interface/test_correcoes_de_norma_na_revisao.py` |
| PO | `backend/tests/portal/test_acompanhamento_pela_situacao.py`, `backend/tests/integration/portal/test_teto_no_portal.py` |
| CO | `backend/tests/interface/test_conteudo_da_054.py`, `backend/tests/javascript/conteudo.test.js` |

## Requisitos funcionais

| Requisito | O que prende | Teste |
|---|---|---|
| FR-1360 | a redação 2 de cada variante do contrato | RF (todas as funções `test_c*`, `test_k*`, `test_t*`, `test_r*`, `test_s*`, `test_v*`, `test_e*`, `test_d*`, `test_p*`, `test_f1_*`, `test_g1_*`); RD `test_cada_frase_do_contrato_sai_onde_a_variante_existe` |
| FR-1361 | a equivalência de cada variante | RF (a nota de equivalência de cada caso); `demonstracao/equivalencia.md` |
| FR-1362 | a frase dos suplentes só sem cadastro de reserva | RF `test_k7_suplentes_sem_cadastro_de_reserva_em_nenhum_perfil`, `test_k8_suplentes_com_cadastro_de_reserva_nao_ganham_a_explicacao`, `test_k7_sem_suplentes_nao_ha_o_que_explicar`; RD `test_sem_cadastro_os_suplentes_sao_explicados_e_com_cadastro_nao` |
| FR-1363 | recurso sem canal, nome entre aspas | RF `test_r1_recurso_admitido_contra_marco_com_nome` a `test_r5_silencio_nao_vira_negativa`, `test_r_a_revisao_diz_deste_marco` |
| FR-1364 | a mesma frase no documento, na Revisão e no portal | RV; PO; RF `test_a_forma_por_extenso_do_portal_e_da_revisao` |
| FR-1365 | Perfil pelo código, "Localidade", sem "polo/turma/curso" fora do dado | AG `test_polo_turma_e_curso_so_onde_o_dado_os_traz`, `test_o_perfil_e_referido_pelo_codigo_e_a_localidade_pelo_rotulo` |
| FR-1366 | nenhum termo interno na redação gerada, nas duas apresentações | RD `test_nenhum_termo_interno_na_redacao_gerada`, `test_o_termo_escrito_pelo_elaborador_sai_literal_e_nao_conta`, `test_a_leitura_pega_o_termo_que_o_sistema_voltasse_a_gerar`; RA `test_o_consolidado_sai_com_a_redacao_a_fonte_e_o_sumario_sem_resumo`; DA `test_os_rotulos_internos_e_a_descricao_sairam` |
| FR-1367 | o catálogo apresentado | CA `test_o_catalogo_vigente_tem_a_ordem_e_os_titulos_apresentados`, `test_chaves_tipos_e_origens_sao_os_da_054`, `test_a_assinatura_da_069_e_por_perguntas`, `test_assinatura_desconhecida_cai_na_plana` |
| FR-1368 | seções reunidas como subseções N.k | CA `test_as_secoes_apresentadas_sao_as_da_spec`; NA `test_por_perguntas_a_secao_e_n_e_a_chave_reunida_e_n_k`; AP `test_as_secoes_reunidas_saem_como_subsecoes`, `test_o_atendimento_sai_dentro_da_inscricao` |
| FR-1369 | cada regra gerada na seção que trata dela | AP `test_o_recurso_do_marco_sai_em_como_recorrer`, `test_a_forma_de_convocacao_sai_em_como_sera_a_convocacao`, `test_os_requisitos_dos_perfis_saem_em_quem_pode_se_inscrever`, `test_o_periodo_e_os_dados_declarados_saem_em_como_se_inscrever`, `test_o_requerimento_e_lembrado_em_documentos_e_na_inscricao` |
| FR-1370 | o resumo, só de dado, com o item | RE `test_cada_linha_aponta_o_item_certo`, `test_o_resumo_so_repete_dado_do_snapshot`, `test_o_resumo_sai_no_documento_com_a_nota_de_nao_substituicao` |
| FR-1371 | o resumo nas palavras do candidato | RE `test_em_a_as_vagas_por_localidade_e_o_cadastro_por_extenso`, `test_em_b_as_vagas_imediatas_pelos_codigos_e_os_demais_em_cadastro`, `test_acima_de_cinco_localidades_so_a_contagem`, `test_a_selecao_em_poucas_palavras` |
| FR-1372 | o sumário com a página de cada seção | AQ `test_o_sumario_diz_a_pagina_em_que_cada_secao_comeca_e_leva_ate_ela` |
| FR-1373 | as vagas pelo dado | AG `test_matriz_unica_quando_todo_perfil_tem_vaga`, `test_perfis_de_mesmo_nome_em_tabela_propria_com_o_nome_na_legenda`, `test_a_tabela_de_reserva_sem_ampla_concorrencia` |
| FR-1374 | atributos comuns uma vez | AG `test_em_todos_os_perfis_so_com_o_que_e_igual`, `test_um_perfil_so_sem_em_todos_os_perfis_nem_faixa` |
| FR-1375 | agrupamento por identidade, unidades indivisíveis, faixa contígua | AG `test_a_faixa_so_quando_os_codigos_sao_contiguos`, `test_partilha_parcial_o_comum_sai_uma_vez`, `test_partilha_parcial_a_unidade_do_corte_sai_inteira_em_cada_grupo`, `test_partilha_parcial_o_desempate_inteiro` |
| FR-1376 | os dados do sorteio inteiros | RF `test_s1_a_s7_metodo_comum`, `test_s3_metodo_proprio_igual_ao_comum`, `test_s4_metodo_proprio_divergente`; AG `test_o_metodo_proprio_de_um_marco_sai_com_os_dados_proprios`, `test_o_metodo_comum_sai_uma_vez` |
| FR-1377 | as siglas no anúncio em caixa alta | AP `test_as_siglas_ficam_no_anuncio_em_caixa_alta` |
| FR-1378 | a descrição fora do ato | AP `test_a_descricao_do_edital_nao_sai_no_ato`; DA `test_os_rotulos_internos_e_a_descricao_sairam` |
| FR-1379 | "Autenticidade" | RF `test_f1_autenticidade`; AP `test_o_fecho_diz_autenticidade` |
| FR-1380 | a fonte embutida e a licença | FE `test_o_edital_declara_as_duas_fontes_embutidas_nos_recursos_de_sempre`, `test_o_arquivo_embutido_e_o_ttf_versionado`, `test_os_arquivos_versionados_sao_os_registrados_na_origem`, `test_a_licenca_acompanha_os_arquivos`, `test_o_subconjunto_nao_usa_nome_reservado` |
| FR-1381 | a medição pela fonte que o arquivo embute | FE `test_nenhuma_linha_passa_da_margem_pela_metrica_da_fonte_embutida`, `test_o_subconjunto_cobre_todo_caractere_que_a_grafia_aceita`; ME |
| FR-1382 | a hierarquia tipográfica | HI (todos) |
| FR-1383 | comprovante e divulgação byte a byte | CB (todos); FE `test_a_helvetica_do_comprovante_continua_medindo_como_antes` |
| FR-1384 | título e idioma | AQ `test_info_tem_titulo_e_autor_sem_data`, `test_o_catalogo_declara_idioma_titulo_na_janela_e_marcadores` |
| FR-1385 | marcadores | AQ `test_os_marcadores_sao_as_secoes_e_subsecoes_na_pagina_em_que_comecam` |
| FR-1386 | links, nenhum endereço acrescentado | AQ `test_o_sumario_diz_a_pagina_em_que_cada_secao_comeca_e_leva_ate_ela`, `test_os_enderecos_do_texto_viram_link_e_nenhum_e_acrescentado` |
| FR-1387 | o nome do arquivo no download | NO (todos) |
| FR-1388 | sem promessa de acessibilidade | AQ `test_sem_identificador_nem_marcacao`; `verificacao.md`, *Acessibilidade* |
| FR-1389 | nenhum título órfão | PG `test_nenhum_titulo_no_pe_da_pagina` |
| FR-1390 | linha de tabela inteira, cabeçalho repetido, sem linha só | PG `test_a_continuacao_da_tabela_repete_o_cabecalho`, `test_a_tabela_que_quebra_deixa_ao_menos_duas_linhas_de_cada_lado` |
| FR-1391 | blocos relacionados juntos, divisão segura | PG `test_nenhuma_pagina_so_com_o_fecho`, `test_o_item_maior_que_a_pagina_se_parte_sem_pagina_vazia`; AG `test_partilha_parcial_a_unidade_do_corte_sai_inteira_em_cada_grupo` |
| FR-1392 | equilíbrio | PG `test_nenhuma_pagina_quase_vazia_salvo_a_ultima`; `backend/tests/unit/publicacoes/test_atribuicoes_consolidadas.py` `test_a_subsecao_comum_que_cabe_numa_pagina_sai_inteira_e_o_titulo_nunca_fica_sozinho` |
| FR-1393 | o hash do já submetido; bytes determinísticos; a prévia | AC `test_o_hash_do_conteudo_homologado_antes_nao_muda`, `test_o_homologado_antes_da_troca_e_recusado_na_publicacao`; AQ `test_os_mesmos_bytes_em_duas_composicoes`; AP `test_a_previa_compoe_pela_apresentacao_por_perguntas`, `test_a_previa_e_o_publicado_tem_as_mesmas_paginas` |
| FR-1394 | o publicado intocado; a plana nos Editais antigos | AC `test_o_documento_publicado_antes_e_servido_com_os_bytes_gravados`; RA (todos); NA `test_na_plana_os_numeros_sao_os_de_sempre` |
| FR-1395 | o texto livre literal | AP `test_cada_paragrafo_de_texto_livre_sai_literalmente`; RD `test_o_termo_escrito_pelo_elaborador_sai_literal_e_nao_conta`; RT `test_o_texto_nao_muda` |
| FR-1396 | a conferência por enunciado | `demonstracao/equivalencia.md`; DA `test_todo_fato_de_antes_esta_no_documento_novo` |
| FR-1397 | a redação histórica do ato publicado | RP (todos); AO (todos) |
| FR-1398 | o inventário dos leitores | `research.md`, R-004 (cada leitor classificado); AO; RV; PO |
| FR-1399 | as remissões intocadas | NC (todos); RA `test_o_consolidado_tem_os_mesmos_itens_que_o_original`, `test_a_tela_de_retificacao_mostra_os_numeros_do_original`; ID |
| FR-1400 | o aviso de remissão textual | RT (todos); AR (todos) |

## Critérios de sucesso

| Critério | Teste ou medição |
|---|---|
| SC-516 | DA `test_todo_fato_de_antes_esta_no_documento_novo`, `test_localidades_documentos_e_perfis_estao_todos` |
| SC-517 | `demonstracao/equivalencia.md` (frases novas listadas para aprovação) |
| SC-518 | RD `test_nenhum_termo_interno_na_redacao_gerada`; RA |
| SC-519 | FE `test_nenhuma_linha_passa_da_margem_pela_metrica_da_fonte_embutida`; três motores em `verificacao.md` |
| SC-520 | AQ `test_os_marcadores_sao_as_secoes_e_subsecoes_na_pagina_em_que_comecam`, `test_o_sumario_diz_a_pagina_em_que_cada_secao_comeca_e_leva_ate_ela` |
| SC-521 | PG (todos, sobre A, B, a variante e sintéticos) |
| SC-522 | CB (todos) |
| SC-523 | AQ `test_os_mesmos_bytes_em_duas_composicoes`; DA `test_o_documento_sai_com_os_bytes_gravados`; AC `test_o_hash_do_conteudo_homologado_antes_nao_muda` |
| SC-524 | AG `test_perfis_de_mesmo_nome_em_tabela_propria_com_o_nome_na_legenda`, `test_em_todos_os_perfis_so_com_o_que_e_igual` |

## Decisões

| Decisão | Teste |
|---|---|
| D-001 | CA `test_o_catalogo_vigente_tem_a_ordem_e_os_titulos_apresentados`; AP |
| D-002 | FE |
| D-003 | RA |
| D-004 | RF `test_k7_suplentes_sem_cadastro_de_reserva_em_nenhum_perfil`, `test_k8_suplentes_com_cadastro_de_reserva_nao_ganham_a_explicacao` |
| D-005 | RE; `demonstracao/equivalencia.md` |
| D-006 | RF `test_t1_a_t7_criterios_de_desempate`, `test_t1_forma_generica_sem_deduzir_idade_pelo_rotulo` |
| D-007 | RF `test_g1_a_g3_regras_de_classificacao`; RA |

## Casos-limite

| Caso | Teste |
|---|---|
| Edital de um Perfil só | AG `test_um_perfil_so_sem_em_todos_os_perfis_nem_faixa`; ID |
| Todos os Perfis sem vaga imediata | RE `test_todos_os_perfis_sem_vaga_imediata`; AG `test_perfis_de_mesmo_nome_em_tabela_propria_com_o_nome_na_legenda` (a forma em partes) |
| Lista sem percentual (PTT) | AG `test_a_lista_sem_percentual_sai_com_travessao` |
| Códigos não contíguos | AG `test_a_faixa_so_quando_os_codigos_sao_contiguos` |
| Dois marcos no mesmo Perfil | AG `test_dois_marcos_no_mesmo_perfil_saem_nomeados` |
| Método de sorteio próprio | AG `test_o_metodo_proprio_de_um_marco_sai_com_os_dados_proprios`; RF `test_s4_metodo_proprio_divergente` |
| Recurso vedado; silêncio | RF `test_r3_recurso_vedado`, `test_r5_silencio_nao_vira_negativa` |
| Nome de marco sem gênero | RF `test_r1_recurso_admitido_contra_marco_com_nome` |
| Texto livre que cita seção pelo título antigo | RT `test_secao_repartida_avisa_com_o_trecho_e_os_destinos`; AR |
| Termo interno escrito pelo Elaborador | RD `test_o_termo_escrito_pelo_elaborador_sai_literal_e_nao_conta` |
| Remissão gerada na apresentação plana | RA `test_o_consolidado_tem_os_mesmos_itens_que_o_original` |
| Texto livre que repete regra gerada | AP `test_cada_paragrafo_de_texto_livre_sai_literalmente` |
| Texto livre que diverge do sistema (achado) | AP `test_cada_paragrafo_de_texto_livre_sai_literalmente`; `doc/achado-sorteio-condicionado-no-texto-e-incondicional-no-sistema.md` |
| Requisito sem comprovante (achado) | DA `test_localidades_documentos_e_perfis_estao_todos` (o dado reproduzido); `doc/achado-requisito-sem-comprovante-correspondente.md` |
| Caractere sem grafia na fonte | FE `test_o_subconjunto_cobre_todo_caractere_que_a_grafia_aceita` |
| Prévia | AP `test_a_previa_compoe_pela_apresentacao_por_perguntas`, `test_a_previa_e_o_publicado_tem_as_mesmas_paginas` |
| Item de lista maior que uma página | PG `test_o_item_maior_que_a_pagina_se_parte_sem_pagina_vazia` |
| Sigla no título | AP `test_as_siglas_ficam_no_anuncio_em_caixa_alta` |
| Endereço escrito no texto livre | AQ `test_os_enderecos_do_texto_viram_link_e_nenhum_e_acrescentado` |
