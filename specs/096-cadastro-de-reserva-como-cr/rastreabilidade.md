# Rastreabilidade — 096, cadastro de reserva sem vaga imediata impresso como CR

Cada requisito, critério, decisão e caso-limite da spec, com o teste que o prende. Os casos-limite
entram aqui porque nenhuma ferramenta os cobra (nota em *Assumptions* da spec).

**Arquivos de teste**

| Sigla | Arquivo |
|---|---|
| PR | `backend/tests/unit/editais/test_cadastro_sem_vaga_imediata.py` |
| CR | `backend/tests/unit/publicacoes/test_cadastro_de_reserva_como_cr.py` |
| RF | `backend/tests/unit/publicacoes/test_previa_reserva_o_fecho.py` |
| DA | `backend/tests/unit/publicacoes/test_documento_da_auditoria_depois_da_096.py` |
| RT | `backend/tests/integration/publicacoes/test_cadastro_de_reserva_na_retificacao.py` |
| PM | `backend/tests/unidades/test_previa_mede_o_fecho.py` |
| PO | `backend/tests/integration/portal/test_detalhe_selecao.py` (o teste da `FR-136` revisto de propósito) |
| ID | `backend/tests/unit/publicacoes/test_itens_do_documento.py` (bytes do B da `096`, do A da `069`) |
| D9 | `backend/tests/unit/publicacoes/test_documento_da_auditoria_depois_da_069.py` (idem) |
| CT | `backend/tests/contract/test_documento_publicado.py` (fixture de bytes **inalterada**; a prévia com a autoridade prevista) |
| EQ | `backend/tests/unit/publicacoes/test_equivalencia_da_consolidacao.py` (a nota não é frase de Perfil) |
| PV | `backend/tests/unit/publicacoes/test_perfil_sem_vaga_imediata.py` (a nota não é regra de reserva no cadastro) |

A faixa do cabeçalho, **FR-2400** e **SC-900**, abre nos dois primeiros identificadores, que estão
abaixo.

## Requisitos funcionais

| Requisito | Teste |
|---|---|
| FR-2400 | PR `test_zero_vaga_e_cadastro_declarado_e_cr` (o predicado lê o inteiro, e nada o grava); RT `test_a_retificacao_que_da_vagas_ao_cr_imprime_o_numero_e_tira_a_nota` (a homologação lê `0` e `2` como inteiros) |
| FR-2401 | SC-903: nenhum teste de validação, apuração, ocupação, classificação ou convocação mudou (`git diff main -- backend/tests/unit/ocupacao backend/tests/unit/convocacao backend/tests/unit/classificacao backend/processo_seletivo/ocupacao backend/processo_seletivo/convocacao backend/processo_seletivo/classificacao` vazio) |
| FR-2402 | PR, os quatro testes; CR `test_a_celula_de_vagas`, `test_a_celula_e_a_mesma_nas_duas_redacoes` |
| FR-2403 | CR `test_na_tabela_de_perfis_o_cadastro_sem_vaga_sai_cr` (limitado e ilimitado) |
| FR-2404 | CR `test_no_perfil_unico_o_par_diz_cr_e_a_nota_sai_depois_dos_pares`, `test_no_perfil_unico_sem_cr_o_par_e_o_numero_e_nao_ha_nota` |
| FR-2405 | CR `test_em_b_por_perguntas_os_tutores_presenciais_saem_cr_com_a_nota`, `test_por_perguntas_um_perfil_so_cr` |
| FR-2406 | CR `test_a_nota_sai_quando_algum_e_cr`, `test_a_nota_nao_sai_sem_cr`, `test_a_nota_sai_depois_da_grade_em_corpo_de_tabela`, `test_sem_nenhum_cr_a_tabela_sai_sem_nota`; DA `test_cada_cr_e_de_um_tutor_presencial_e_a_nota_vem_depois_deles` |
| FR-2407 | CR `test_o_total_soma_so_as_vagas_e_sai`, `test_todos_cr_sem_linha_de_total` |
| FR-2408 | CR `test_sem_cadastro_continua_zero_ao_lado_de_cr`, `test_a_celula_de_vagas` (com vaga, com e sem cadastro) |
| FR-2409 | CR `test_sem_nenhum_cr_a_tabela_sai_sem_nota`, `test_sem_nota_a_tabela_e_a_de_antes`; ID e D9 no cenário A; CT `test_o_documento_publicado_continua_byte_a_byte_o_mesmo` |
| FR-2410 | CR `test_a_nota_nao_e_tabela_nem_desloca_a_numeracao`; ID `test_os_itens_sao_os_que_a_composicao_escreve` |
| FR-2411 | RT `test_a_retificacao_que_da_vagas_ao_cr_imprime_o_numero_e_tira_a_nota`, `test_a_retificacao_que_zera_um_perfil_com_cadastro_imprime_cr` |
| FR-2412 | RT, os dois acima (antes e depois pela tela de homologação, `_alteracoes_legiveis`) |
| FR-2413 | RT `test_o_documento_ja_publicado_nao_muda`; CT (fixture inalterada) |
| FR-2414 | PO `test_cadastro_reserva_sem_vaga_imediata_e_oferta_e_nao_ausencia` |
| FR-2415 | PO `test_cadastro_reserva_sem_vaga_imediata_e_oferta_e_nao_ausencia`, `test_o_perfil_com_vaga_continua_com_o_numero_e_a_pagina_nao_usa_a_sigla` |
| FR-2416 | PO `test_o_perfil_com_vaga_continua_com_o_numero_e_a_pagina_nao_usa_a_sigla` |
| FR-2417 | Nenhum código da gestão mudou, e os testes dela continuam verdes; conferido pelo navegador (`verificacao.md`, T035: os dezesseis "Vagas imediatas" em `0` na tela de Retificação); a prévia, por RF e PM |
| FR-2418 | RF `test_no_cenario_b_a_previa_pagina_o_corpo_como_o_publicado`, `test_no_cenario_b_o_sumario_da_previa_diz_as_paginas_do_publicado`, `test_sem_a_reserva_o_cenario_b_volta_a_divergir`; CT `test_o_corpo_normativo_quebra_nas_mesmas_paginas_na_previa_e_no_publicado`, `test_removidas_as_diferencas_permitidas_as_composicoes_sao_equivalentes` |
| FR-2419 | RF `test_a_reserva_tem_a_geometria_do_fecho_real`, `test_nenhuma_linha_da_reserva_e_vazia_onde_o_fecho_tem_texto` |
| FR-2420 | RF `test_entre_varias_previstas_reserva_a_mais_alta`, `test_sem_prevista_reserva_o_fecho_sem_nome_nem_cargo`; PM `test_as_previstas_sao_as_vigentes_na_data`, `test_a_tela_da_previa_mede_pelas_vigentes_e_nao_as_imprime` |
| FR-2421 | RF `test_a_previa_nao_imprime_a_autoridade_nem_o_resumo`, `test_o_publicado_recusa_fecho_previsto`; PM `test_a_tela_da_previa_mede_pelas_vigentes_e_nao_as_imprime` |

## Critérios de sucesso

| Critério | Teste ou medição |
|---|---|
| SC-900 | DA, os dois testes, nas três composições do B; CR `test_em_b_por_perguntas_os_tutores_presenciais_saem_cr_com_a_nota`; fluxo real (`verificacao.md`, T033: 16 `CR`, 0 células `0`) |
| SC-901 | ID e D9: o A continua com os bytes da `069`; CT: a fixture de contrato byte a byte |
| SC-902 | PO, os dois testes; navegador (`verificacao.md`, T035) |
| SC-903 | `make lint check test-pg` (`verificacao.md`, Suíte completa) |
| SC-904 | RF, os três primeiros testes (3 composições × 3 autoridades, e a prova sem a reserva) |

## Decisões

| Decisão | Onde se prende |
|---|---|
| D-001 | PR (o predicado lê o dado, e o dado não muda); RT (a homologação lê inteiros) |
| D-002 | CR `test_a_sigla_e_a_nota_sao_as_da_equipe`; DA (uma nota por tabela com `CR`); EQ e PV (a nota não é regra) |
| D-003 | RT, os dois testes de Retificação |
| D-004 | PO, os dois testes |
| D-005 | PR `test_o_acervo_sem_quadro_e_cr_e_para_a_067_continua_sem_vaga_nao` |
| D-006 | CR `test_a_celula_de_vagas`, `test_a_celula_e_a_mesma_nas_duas_redacoes`, `test_por_perguntas_um_perfil_so_cr` |
| D-007 | CR `test_a_nota_sai_depois_da_grade_em_corpo_de_tabela`, `test_a_nota_nao_vai_junto` |
| D-008 | CR `test_a_nota_nao_e_tabela_nem_desloca_a_numeracao` |
| D-009 | DA; ID; D9 |
| D-010 | PO `test_cadastro_reserva_sem_vaga_imediata_e_oferta_e_nao_ausencia` |
| D-011 | FR-2417 e D-003 acima; o corpus da `070` sem mudança (`git diff main -- backend/tests/fixtures/corpus_070` vazio) |
| D-012 | RF, todos; PM, todos |
| D-013 | RF `test_a_reserva_tem_a_geometria_do_fecho_real`, `test_nenhuma_linha_da_reserva_e_vazia_onde_o_fecho_tem_texto`; CT (o `corpo_normativo` reconhece `Fecho do ato: `) |

## Casos-limite

| Caso | Teste |
|---|---|
| 0 vaga e sem cadastro | CR `test_sem_cadastro_continua_zero_ao_lado_de_cr`, `test_no_perfil_unico_sem_cr_o_par_e_o_numero_e_nao_ha_nota` |
| 0 no total e linha positiva | PR `test_os_demais_nao_sao_cr[total 0 com linha positiva]`; CR `test_o_incoerente_continua_zero` |
| Com vaga e cadastro | CR `test_a_celula_de_vagas[com vaga e cadastro]` |
| Cadastro limitado em 0 | CR `test_o_cadastro_limitado_a_zero_sai_cr` (a incoerência fica como achado, T037) |
| Edital já publicado | RT `test_o_documento_ja_publicado_nao_muda` |
| Prévia na gestão | RF e PM |
| Telas da gestão | FR-2417 acima |
| Numeração e remissões | CR `test_a_nota_nao_e_tabela_nem_desloca_a_numeracao` |
| Extração de texto | DA (a nota e o `CR` saem como texto, e são lidos pelo `texto_de`) |
| O assistente de dúvidas | fora do escopo; achado registrado (T037) |
| Várias autoridades de alturas diferentes | RF `test_entre_varias_previstas_reserva_a_mais_alta` (o limite, para a mais baixa, está na spec) |
| Nenhuma autoridade vigente | RF `test_sem_prevista_reserva_o_fecho_sem_nome_nem_cargo` |
