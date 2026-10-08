# Rastreabilidade — 064 · As atribuições idênticas saem uma vez no documento do Edital

**Frase que governa**: *o documento diz uma vez o que é igual, e diz a cada Perfil onde está.*

Cada linha aponta o lugar do código e o que o prende. **TA** =
`tests/unit/publicacoes/test_atribuicoes_consolidadas.py`, novo; **TC** =
`tests/contract/test_documento_publicado.py`; **TR** =
`tests/integration/publicacoes/test_retificacoes.py`; **V** = a [verificação](verificacao.md).

P = `backend/processo_seletivo/publicacoes/infrastructure/pdf.py`, o único arquivo de produção
alterado.

---

## 1. Requisitos funcionais

| Identificador | Onde entrou | O que o prende |
|---|---|---|
| **FR-1186** | P`_atribuicoes_comuns`: os parágrafos de `_paragrafos` do primeiro Perfil do grupo, na ordem (D-005) | TA `test_dois_perfis_iguais_saem_numa_subsecao_comum_com_remissao`, `test_dez_perfis_de_mesmo_texto_imprimem_o_texto_uma_vez`, `test_cada_perfil_tem_no_documento_exatamente_as_atribuicoes_da_versao` |
| **FR-1187** | P`grupos_de_atribuicoes`: chave = parágrafos de `_paragrafos` sobre `grafia.normalizar`, cada um reduzido às palavras (D-002 e a emenda dela) | TA `test_textos_identicos_agrupam`, `test_o_que_o_documento_nao_distingue_nao_impede`, `test_o_que_o_documento_distingue_impede`, `test_o_que_a_grafia_normaliza_nao_impede` (função e documento), `test_caracteres_sem_grafia_diferentes_nao_se_juntam` |
| **FR-1188** | P`grupos_de_atribuicoes`: só chave não vazia, só grupo de dois ou mais, nada com um Perfil | TA `test_texto_vazio_nunca_agrupa`, `test_edital_de_um_perfil_nao_tem_grupo`, `test_mesma_denominacao_e_textos_diferentes_nao_agrupam`, `test_denominacoes_diferentes_e_o_mesmo_texto_agrupam`, `test_o_que_nao_e_identico_sai_inteiro_em_cada_perfil`, `test_a_mesma_denominacao_nao_junta_textos_diferentes`, `test_texto_vazio_nao_imprime_rotulo_nem_subsecao` |
| **FR-1189** | P`_perfis`: a lista `comuns`, numerada a partir de `N+1` uma vez só; P`_codigos_enumerados` e P`_linhas_sem_partir` no título (D-003) | TA `test_dois_perfis_iguais_saem_numa_subsecao_comum_com_remissao`, `test_dois_grupos_saem_em_duas_subsecoes_na_ordem_do_primeiro_perfil`, `test_todos_os_perfis_no_mesmo_grupo_sao_nomeados_no_titulo`, `test_os_grupos_seguem_a_ordem_do_primeiro_perfil_de_cada_um`, `test_o_titulo_quebra_entre_os_codigos_e_nunca_dentro_de_um`, `test_codigo_com_o_separador_da_enumeracao_vai_entre_aspas` |
| **FR-1190** | P`_perfis`: `_pares` com "Atribuições" e "as descritas no item …" no lugar do bloco, com o espaço de sub-bloco (`antes=ANTES_DE_BLOCO`); o ramo de antes intacto para o não agrupado (D-004) | TA `test_dois_perfis_iguais_saem_numa_subsecao_comum_com_remissao`, `test_o_perfil_de_texto_proprio_entre_os_agrupados_continua_no_lugar`, `test_a_remissao_fica_no_lugar_do_bloco_em_negrito_e_com_o_espaco_de_sub_bloco` |
| **FR-1191** | consequência de FR-1186 e FR-1190: o número da remissão e o da subseção saem do mesmo dicionário, na mesma composição | TA `test_cada_perfil_tem_no_documento_exatamente_as_atribuicoes_da_versao` (nove cenários; reconstrói pelo documento, com normalização escrita no teste, D-006), `test_o_item_de_varias_linhas_sai_palavra_a_palavra`. Prova de mutação em V: omitir parágrafo, desviar a remissão ou inverter a ordem reprova sete dos nove cenários |
| **FR-1192** | as subseções comuns vêm **depois** dos Perfis e não abrem tabela; `numeracao()` e `_Numerador` não foram tocados | TA `test_a_numeracao_dos_perfis_das_secoes_e_das_tabelas_nao_se_move`, `test_as_remissoes_do_texto_livre_continuam_apontando_o_mesmo_lugar` |
| **FR-1193** | P`_atribuicoes_comuns`: bloco **coeso**, título `junto=True`, cada parágrafo num bloco (D-005) | TA `test_a_subsecao_comum_que_cabe_numa_pagina_sai_inteira_e_o_titulo_nunca_fica_sozinho` (catorze posições de partida), `test_a_subsecao_comum_maior_que_a_pagina_quebra_entre_paragrafos_e_conclui`. Prova de mutação em V: com `coeso=False`, nove das catorze posições reprovam |
| **FR-1194** | uma função de composição para os dois modos; com um Perfil, `grupos_de_atribuicoes` devolve vazio e o caminho é o de antes | TC `test_o_documento_publicado_continua_byte_a_byte_o_mesmo` (fixture **não** regerada); TC `test_o_corpo_normativo_quebra_nas_mesmas_paginas_na_previa_e_no_publicado[atribuicoes-comuns]`, `test_removidas_as_diferencas_permitidas_as_composicoes_sao_equivalentes[atribuicoes-comuns]`, `test_o_cenario_de_atribuicoes_comuns_compoe_mesmo_a_subsecao_comum`; TA `test_edital_de_um_perfil_nao_tem_subsecao_comum_nem_remissao` |
| **FR-1195** | só P mudou: `git diff main --stat` não alcança modelo, migration, snapshot, tela nem portal | TA `test_compor_nao_toca_o_conteudo_nem_a_impressao_digital_dele`, `test_agrupar_nao_altera_os_perfis`; `make check` (nenhuma migration); V, o escopo do diff |
| **FR-1196** | nenhum caminho de regerar documento; a Retificação compõe pela mesma função | TR `test_a_retificacao_reagrupa_as_atribuicoes_e_o_documento_original_nao_muda`; os guardiões append-only existentes, sem edição (`tests/integration/test_database_permissions.py`, `tests/integration/test_imutabilidade_do_historico.py`) |
| **FR-1197** | o resto do laço de `_perfis` intocado | TA `test_os_demais_blocos_continuam_em_cada_perfil` |

## 2. Critérios de sucesso

| Identificador | O que o prende |
|---|---|
| **SC-457** | TA `test_dez_perfis_de_mesmo_texto_imprimem_o_texto_uma_vez`; V, a amostra de dez polos composta e olhada página a página |
| **SC-458** | TA `test_cada_perfil_tem_no_documento_exatamente_as_atribuicoes_da_versao` |
| **SC-459** | TA `test_a_numeracao_dos_perfis_das_secoes_e_das_tabelas_nao_se_move` |
| **SC-460** | TC, os dois testes de prévia × publicado no cenário `atribuicoes-comuns`, e o byte a byte da fixture |
| **SC-461** | TR `test_a_retificacao_reagrupa_as_atribuicoes_e_o_documento_original_nao_muda`; `make lint check test-pg` com banco próprio, o total em V |

## 3. Casos-limite da spec

Não têm identificador e por isso nenhuma ferramenta os cobra; cada um tem a sua linha.

| Caso-limite | O que o prende |
|---|---|
| Diferença só de espaço | TA `test_o_que_o_documento_nao_distingue_nao_impede` (cinco variantes) |
| Diferença de quebra de linha | TA `test_o_que_o_documento_distingue_impede[quebra-a-menos]`, `[quebra-a-mais]` |
| Diferença de pontuação, maiúscula, acento ou símbolo | TA `test_o_que_o_documento_distingue_impede[pontuacao]`, `[maiuscula]`, `[acento]`; `test_a_comparacao_e_do_texto_registrado_e_nao_do_impresso` |
| Mesmos itens em outra ordem | TA `test_o_que_o_documento_distingue_impede[outra-ordem]` |
| Subconjunto | TA `test_o_que_o_documento_distingue_impede[subconjunto]`, `test_o_que_nao_e_identico_sai_inteiro_em_cada_perfil[subconjunto]` |
| Texto vazio em vários Perfis | TA `test_texto_vazio_nunca_agrupa`, `test_texto_vazio_nao_imprime_rotulo_nem_subsecao` |
| Mesmo texto, denominações diferentes | TA `test_denominacoes_diferentes_e_o_mesmo_texto_agrupam` |
| Dois grupos no mesmo Edital | TA `test_dois_grupos_saem_em_duas_subsecoes_na_ordem_do_primeiro_perfil` |
| Todos os Perfis no mesmo grupo | TA `test_todos_os_perfis_no_mesmo_grupo_sao_nomeados_no_titulo` |
| Código com espaço, num título longo | TA `test_o_titulo_quebra_entre_os_codigos_e_nunca_dentro_de_um` |
| Código com vírgula ou com " e " | TA `test_codigo_com_o_separador_da_enumeracao_vai_entre_aspas` |
| Três ou mais no grupo e um de texto próprio entre eles | TA `test_o_perfil_de_texto_proprio_entre_os_agrupados_continua_no_lugar` |
| Retificação que acrescenta Perfil de mesmo texto | TA `test_o_perfil_acrescentado_com_o_mesmo_texto_entra_no_grupo` |
| Retificação que deixa o grupo com um Perfil | TA `test_o_grupo_reduzido_a_um_perfil_se_desfaz`; TR `test_a_retificacao_reagrupa_as_atribuicoes_e_o_documento_original_nao_muda` (de três para dois) |
| Caractere que a grafia normaliza | TA `test_o_que_a_grafia_normaliza_nao_impede` (quatro pares, na função e na prévia) |
| Caractere que o documento não representa | TA `test_caracteres_sem_grafia_diferentes_nao_se_juntam` |
| Item partido em duas linhas por quebra rígida | TA `test_o_que_o_documento_distingue_impede[quebra-a-mais]` |
