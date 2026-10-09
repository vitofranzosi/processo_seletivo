# Rastreabilidade — 068, o que se repete por Perfil sai uma vez no Edital em PDF

Cada requisito, critério, decisão e caso-limite da spec, com o teste que o prende. Os casos-limite
entram aqui porque nenhuma ferramenta os cobra.

**Arquivos de teste**

| Sigla | Arquivo |
|---|---|
| CP | `backend/tests/unit/publicacoes/test_consolidacao_por_perfil.py` |
| EQ | `backend/tests/unit/publicacoes/test_equivalencia_da_consolidacao.py` |
| DA | `backend/tests/unit/publicacoes/test_documento_da_auditoria_depois_da_068.py` |
| ID | `backend/tests/unit/publicacoes/test_itens_do_documento.py` (guardião da `065`, bytes esperados novos) |
| CT | `backend/tests/contract/test_documento_publicado.py` (fixture de bytes de um Perfil **inalterada**) |
| RT | `backend/tests/integration/publicacoes/test_retificacoes.py` |
| RA | `backend/tests/integration/publicacoes/test_documento_da_retificacao_que_acrescenta.py` (atualizado de propósito) |
| PV | `backend/tests/unit/publicacoes/test_perfil_sem_vaga_imediata.py` (atualizado de propósito) |

## Requisitos funcionais

| Requisito | O que prende | Teste |
|---|---|---|
| FR-1340 | identidade do texto impresso; o título do Perfil fora; qualquer linha diferente separa | CP `test_marcos_e_requisitos_identicos_agrupam_todos`, `test_qualquer_linha_diferente_separa_os_marcos`, `test_o_titulo_que_nomeia_o_perfil_nao_entra_na_comparacao`, `test_requisitos_diferentes_nao_agrupam` |
| FR-1341 | só com dois ou mais Perfis; compor não muda conteúdo nem impressão digital | CP `test_um_perfil_nao_tem_plano`, `test_compor_nao_muda_o_snapshot_nem_o_hash`, `test_o_plano_nao_muda_o_snapshot` |
| FR-1342 | tabela de vagas em matriz, nenhum quadro nem modalidades no Perfil; forma longa quando não cabe | CP `test_a_tabela_de_vagas_e_uma_matriz_perfil_por_lista`, `test_nenhum_perfil_imprime_o_proprio_quadro_nem_a_propria_tabela_de_modalidades`, `test_a_matriz_que_nao_cabe_sai_na_forma_longa`; CT `test_as_duas_tabelas_de_vagas_nao_se_chamam_a_mesma_coisa` |
| FR-1343 | números do quadro; "—" na lista não declarada; sem linha para quem não tem quadro ou vaga | CP `test_lista_que_o_perfil_nao_declara_sai_com_traco_e_nao_com_zero`, `test_perfil_sem_vaga_imediata_ou_sem_quadro_nao_tem_linha`, `test_nenhum_perfil_com_quadro_nao_tem_tabela_de_vagas_e_as_tabelas_seguem_sem_lacuna`; PV `test_o_cenario_b_tem_vagas_so_dos_dois_perfis_com_vaga_e_uma_reversao` |
| FR-1344 | modalidades agrupadas, legenda com os códigos ou sem eles | CP `test_uma_tabela_de_modalidades_quando_todas_sao_iguais_na_ordem_das_colunas`, `test_modalidades_diferentes_saem_em_tabelas_por_grupo_com_os_codigos`, `test_grupo_de_um_perfil_e_nomeado_no_singular` |
| FR-1345 | uma ordem de listas (ED-11) | CP `test_a_ordem_das_listas_e_a_do_quadro_e_nao_a_do_codigo`, `test_a_lista_que_so_um_quadro_declara_vem_depois_e_a_que_nenhum_declara_por_ultimo`, `test_uma_tabela_de_modalidades_quando_todas_sao_iguais_na_ordem_das_colunas` |
| FR-1346 | subseção comum de marcos e remissão | CP `test_os_marcos_iguais_saem_uma_vez_numa_subsecao_que_nomeia_os_perfis`, `test_cada_perfil_do_grupo_remete_a_subsecao_e_nenhum_outro_remete`, `test_marcos_diferentes_em_todos_nao_criam_subsecao`, `test_perfil_sem_marco_nao_remete_nem_imprime_marcos` |
| FR-1347 | a frase que aplica os marcos a cada Perfil separadamente | CP `test_a_frase_que_aplica_os_marcos_a_cada_perfil_vem_antes_deles` |
| FR-1348 | o texto dos marcos, linha a linha | CP `test_os_marcos_da_subsecao_sao_linha_a_linha_os_do_perfil`; EQ `test_cada_perfil_tem_depois_exatamente_a_regra_que_tinha_antes` |
| FR-1349 | método comum uma vez; remissão; método próprio no marco | CP `test_o_metodo_comum_sai_uma_vez_quando_todos_os_marcos_sao_iguais`, `test_dois_grupos_pelo_metodo_comum_imprimem_as_linhas_uma_vez_e_o_segundo_remete`, `test_o_perfil_com_marco_proprio_imprime_o_metodo_e_o_grupo_seguinte_remete_a_ele`, `test_metodo_proprio_continua_no_marco_e_agrupa_quando_identico`, `test_marcos_com_metodo_proprio_e_com_o_comum_nao_se_juntam` |
| FR-1350 | reversão abaixo da tabela de vagas, com códigos quando não vale para todos | CP `test_cada_frase_sai_uma_vez_sem_prefixo_quando_vale_para_todos`, `test_a_reversao_vem_logo_abaixo_da_tabela_de_vagas_e_a_convocacao_depois_das_modalidades`, `test_especies_diferentes_saem_uma_por_especie_com_os_codigos`, `test_perfil_sem_reversao_nao_e_alcancado_e_os_outros_sao_nomeados`, `test_perfil_fora_da_tabela_de_vagas_nao_e_alcancado_pela_reversao` |
| FR-1351 | convocação pela mesma regra, sobre o Edital inteiro | CP `test_um_perfil_so_e_nomeado_no_singular`, `test_perfil_sem_forma_declarada_nao_e_alcancado_pela_convocacao`; EQ `test_a_leitura_pega_a_frase_que_alcancasse_outro_perfil` |
| FR-1352 | requisitos comuns e remissão | CP `test_os_requisitos_iguais_saem_uma_vez_e_cada_perfil_remete`, `test_requisitos_diferentes_saem_no_proprio_perfil`, `test_requisitos_vazios_nao_agrupam_e_perfil_sem_marco_nao_entra` |
| FR-1353 | equivalência por Perfil | EQ `test_cada_perfil_tem_depois_exatamente_a_regra_que_tinha_antes` (13 casos, entre eles os cenários A e B), `test_a_leitura_pega_a_regra_que_se_perdesse`, `test_a_leitura_pega_a_frase_que_alcancasse_outro_perfil`, `test_o_antes_reconstruido_e_o_que_o_pdf_da_067_imprimia`; fluxo real em `verificacao.md` |
| FR-1354 | toda remissão aponta subseção que nomeia o Perfil, e só os nomeados remetem | CP `test_a_remissao_de_cada_perfil_e_o_numero_da_subsecao_do_grupo_dele`, `test_cada_perfil_do_grupo_remete_a_subsecao_e_nenhum_outro_remete` |
| FR-1355 | itens e tabelas pela regra da composição | ID `test_os_itens_sao_os_que_a_composicao_escreve` (todos os casos), CP `test_a_conferencia_de_remissoes_le_as_subsecoes_novas`; PV `test_a_contagem_de_tabelas_segue_o_documento`, `test_a_contagem_de_tabelas_dos_cenarios_segue_o_documento` |
| FR-1356 | um Perfil, mesmos bytes; prévia e publicado iguais | CP `test_edital_de_um_perfil_sai_como_antes`; CT `test_o_documento_publicado_continua_byte_a_byte_o_mesmo`, `test_o_corpo_normativo_quebra_nas_mesmas_paginas_na_previa_e_no_publicado` (cenários consolidados A e B), `test_removidas_as_diferencas_permitidas_as_composicoes_sao_equivalentes` |
| FR-1357 | paginação: marco quebra entre partes; cabeçalho da tabela repetido | CP `test_o_marco_da_subsecao_comum_quebra_entre_as_partes_e_nunca_dentro_de_uma`, `test_o_cabecalho_da_tabela_de_vagas_se_repete_na_quebra_de_pagina` |
| FR-1358 | publicado não muda; Retificação agrupa pela versão nova | RT `test_a_retificacao_reagrupa_os_marcos_e_o_documento_original_nao_muda`; RA `test_o_documento_da_retificacao_mostra_as_seis` |
| FR-1359 | subseções depois do último Perfil, na ordem atribuições, requisitos, marcos | CP `test_as_subsecoes_seguem_atribuicoes_requisitos_e_marcos`, `test_as_subsecoes_saem_na_ordem_atribuicoes_requisitos_marcos`, `test_grupo_de_um_nao_existe_e_os_grupos_seguem_o_primeiro_perfil` |

## Critérios de sucesso

| Critério | Teste ou medição |
|---|---|
| SC-510 | DA `test_as_paginas_caem_ate_a_meta[A]`; fluxo real: 9 → 6 páginas, Perfis 5 → 3 (`verificacao.md`) |
| SC-511 | DA `test_as_paginas_caem_ate_a_meta[B]`; fluxo real: 36 → 14, Perfis 30 → 9 |
| SC-512 | DA `test_o_que_se_repetia_sai_uma_vez` (13 trechos) |
| SC-513 | EQ, como o FR-1353; fluxo real com zero diferença em A e B |
| SC-514 | DA `test_o_espaco_liberado_nao_vira_branco`; fluxo real: 161 → 61 pt em A, 4162 → 173 pt em B; páginas olhadas (`demonstracao/`) |
| SC-515 | CT `test_o_documento_publicado_continua_byte_a_byte_o_mesmo`; RT; suíte completa em `verificacao.md` |

## Decisões

| Decisão | Teste |
|---|---|
| D-001 | CP `test_as_subsecoes_seguem_atribuicoes_requisitos_e_marcos` (os números dos Perfis e das atribuições não mudam) |
| D-002 | CP `test_a_tabela_de_vagas_e_uma_matriz_perfil_por_lista`, `test_uma_tabela_de_modalidades_quando_todas_sao_iguais_na_ordem_das_colunas` |
| D-003 | CP `test_os_requisitos_iguais_saem_uma_vez_e_cada_perfil_remete`, `test_o_que_a_grafia_normaliza_nao_impede_o_agrupamento` |

## Casos-limite

| Caso | Teste |
|---|---|
| Edital de um Perfil | CP `test_edital_de_um_perfil_sai_como_antes`; CT (bytes) |
| Dois Perfis, marcos diferentes | CP `test_marcos_diferentes_em_todos_nao_criam_subsecao` |
| Dois grupos de marcos | CP `test_grupo_de_um_nao_existe_e_os_grupos_seguem_o_primeiro_perfil` |
| Diferença só no título do marco do Perfil | CP `test_o_titulo_que_nomeia_o_perfil_nao_entra_na_comparacao` |
| Método próprio idêntico em cada Perfil | CP `test_metodo_proprio_continua_no_marco_e_agrupa_quando_identico` |
| Marco que diverge do método comum | CP `test_marcos_com_metodo_proprio_e_com_o_comum_nao_se_juntam` |
| Método comum em grupos diferentes | CP `test_dois_grupos_pelo_metodo_comum_imprimem_as_linhas_uma_vez_e_o_segundo_remete`, `test_o_perfil_com_marco_proprio_imprime_o_metodo_e_o_grupo_seguinte_remete_a_ele` |
| Perfil sem marco | CP `test_perfil_sem_marco_nao_remete_nem_imprime_marcos` |
| Perfil sem quadro ou sem vaga imediata | CP `test_perfil_sem_vaga_imediata_ou_sem_quadro_nao_tem_linha`; PV |
| Nenhum Perfil com quadro | CP `test_nenhum_perfil_com_quadro_nao_tem_tabela_de_vagas_e_as_tabelas_seguem_sem_lacuna` |
| Conjuntos diferentes de modalidades | CP `test_lista_que_o_perfil_nao_declara_sai_com_traco_e_nao_com_zero`, `test_modalidades_diferentes_saem_em_tabelas_por_grupo_com_os_codigos` |
| Muitas listas | CP `test_a_matriz_que_nao_cabe_sai_na_forma_longa` |
| Modalidade sem percentual ou fundamento | CP `test_uma_tabela_de_modalidades_quando_todas_sao_iguais_na_ordem_das_colunas` (linha AC com "—") |
| Código com vírgula ou " e " | CP `test_codigo_com_o_separador_da_enumeracao_vai_entre_aspas_no_titulo_e_na_frase` |
| Código com espaço | CP `test_o_codigo_com_espaco_nunca_se_parte_na_frase`, `test_as_linhas_por_pedacos_nunca_partem_um_codigo` |
| Retificação que desfaz um grupo | RT `test_a_retificacao_reagrupa_os_marcos_e_o_documento_original_nao_muda` |
| Caractere que a grafia normaliza | CP `test_o_que_a_grafia_normaliza_nao_impede_o_agrupamento` |
