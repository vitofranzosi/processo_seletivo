# Rastreabilidade: O andamento diz o que cada providência é (135)

Cada requisito → as tarefas que o implementam → os testes que o verificam. Caminhos relativos a
`backend/tests/`. Abreviações:

- `un` = `unit/interface/test_andamento_o_que_cada_providencia_e.py` — as quatro correções, puras
- `cr` = `integration/classificacao/test_listas_sem_concorrente.py` — o critério da lista vazia
- `ce` = `integration/treinamento/test_andamento_dos_cenarios.py` — C04, C06, C08, C12 e C14
- `es` = `performance/test_andamento_em_escala.py` — o orçamento da `127`, sem mudança
- `nv` = conferência no navegador, em [verificacao.md](verificacao.md)

## Requisitos funcionais

| Requisito | Tarefas | Testes |
|---|---|---|
| FR-4670 (o critério da tela da ordenação) | T006, T007, T008 | `cr::test_sem_autodeclarado_as_duas_reservadas_sao_vazias_e_a_ampla_nunca`; `cr::test_com_um_autodeclarado_a_lista_nao_e_vazia` (as duas comparam com a proposta da tela, lista a lista); `nv` (a tela da ordenação da PPP do C08 diz "Ninguém concorreu por este recorte") |
| FR-4671 (*Pendente*, de quem conduz, com a nota) | T008 | `un::test_a_ordem_da_lista_vazia_continua_pendente_e_diz_o_que_e`; `ce::test_a_ordem_da_ppp_em_que_ninguem_concorre_diz_isso_para_qualquer_papel`; `ce::test_c08_a_pagina_do_edital_diz_que_ninguem_concorre_no_nivel_1_e_na_matriz` |
| FR-4672 (a frase no ato) | T008 | `un::test_a_ordem_da_lista_vazia_continua_pendente_e_diz_o_que_e`; `un::test_a_providencia_carrega_o_dado_e_a_frase_para_qualquer_papel`; `ce::test_a_ordem_da_ppp_em_que_ninguem_concorre_diz_isso_para_qualquer_papel` |
| FR-4673 (o dado na providência) | T004, T008 | `un::test_a_providencia_carrega_o_dado_e_a_frase_para_qualquer_papel`; `ce::test_a_ordem_da_ppp_em_que_ninguem_concorre_diz_isso_para_qualquer_papel` |
| FR-4674 (o agrupamento) | T009 | `un::test_a_vazia_nao_se_junta_a_lista_com_inscritos`; `un::test_a_vazia_nao_se_junta_mesmo_que_a_frase_coincida`; `un::test_duas_vazias_viram_uma_providencia_no_plural`; `un::test_duas_sucessoras_vazias_tambem_vao_ao_plural`; `un::test_uma_vazia_so_continua_no_singular` |
| FR-4675 (o "Próximo nesta lista") | T008 | `ce::test_c08_o_proximo_nesta_lista_diz_a_mesma_frase` |
| FR-4676 (nenhuma situação muda) | T008 | `un::test_a_lista_vazia_nao_muda_situacao_nenhuma`; `un::test_a_ordem_obsoleta_de_lista_que_ficou_vazia_leva_a_nota`; as suítes da `127` e da `128` sem mudança de expectativa |
| FR-4677 (o divulgado como dado) | T003, T004, T012 | `un::test_a_celula_do_resultado_diz_o_que_o_publico_le`; `un::test_o_preliminar_com_a_ordem_obsoleta_e_depois_e_diz_preliminar`; `ce::test_a_celula_do_resultado_diz_o_que_o_publico_le_em_cada_cenario` |
| FR-4678 (a situação de antes, D-002) | T012 | `un::test_a_celula_do_resultado_diz_o_que_o_publico_le`; `ce::test_o_preliminar_publicado_continua_sem_ser_feito`; os casos da `127` e da `133` em `unit/interface/test_andamento_situacoes.py` |
| FR-4679 (decide o dado, e não a nota) | T012, T013 | `un::test_a_redacao_da_nota_nao_decide_a_situacao`; `un::test_o_resumo_do_perfil_le_o_dado_e_nao_a_nota`; `un::test_o_preliminar_com_a_ordem_obsoleta_conta_como_publicado_no_resumo` |
| FR-4680 (a nota de antes) | T012 | `un::test_a_redacao_da_nota_nao_decide_a_situacao`; `ce::test_o_preliminar_publicado_continua_sem_ser_feito` |
| FR-4681 (a razão sem a alternativa) | T015, T016 | `un::test_com_o_preliminar_publicado_a_espera_do_prazo_nao_oferece_o_preliminar`; `un::test_com_o_preliminar_publicado_a_espera_do_recurso_nao_oferece_o_preliminar`; `un::test_sem_a_data_da_janela_a_espera_tambem_nao_oferece_o_preliminar`; `ce::test_a_espera_do_definitivo_nao_oferece_publicar_como_preliminar`; `nv` |
| FR-4682 (a mensagem da aferição intacta) | T015 | `un::test_as_mensagens_da_afericao_continuam_oferecendo_o_preliminar`; `ce::test_c08_na_previa_de_publicacao_a_mensagem_e_a_de_antes`; `ce::test_c08_a_previa_de_publicacao_mostra_a_mensagem_de_antes`; `nv` |
| FR-4683 (as outras razões) | T016 | `un::test_as_outras_razoes_continuam_as_da_afericao` |
| FR-4684 (a contagem diz o escopo) | T019 | `un::test_o_resumo_do_perfil_diz_que_conta_as_providencias_dos_marcos`; `ce::test_c06_o_resumo_do_perfil_diz_o_escopo_e_os_numeros_sao_os_de_antes` |
| FR-4685 (os números de antes, D-004) | T019 | `un::test_o_resumo_do_perfil_diz_que_conta_as_providencias_dos_marcos`; `un::test_sem_providencia_de_marco_a_contagem_nao_aparece`; `un::test_o_cartao_continua_com_a_contagem_do_edital`; `ce::test_c06_o_resumo_do_perfil_diz_o_escopo_e_os_numeros_sao_os_de_antes` |
| FR-4686 (custo fixo por Edital) | T007, T008, T022 | `cr::test_a_pergunta_custa_ate_duas_consultas_e_nao_cresce_com_as_inscricoes`; `es::test_a_pontuacao_com_etapas_nao_cresce_com_as_inscricoes` e os outros dois, com os tetos de antes |
| FR-4687 (nada muda em comando, acesso ou documento) | T021, T023 | a suíte inteira contra PostgreSQL; nenhum comando, permissão ou template de documento no diff |

## Critérios de sucesso

| Critério | Testes |
|---|---|
| SC-1460 | `ce::test_a_ordem_da_ppp_em_que_ninguem_concorre_diz_isso_para_qualquer_papel` (C08, C12, C14; presidência e Publicador); `nv` |
| SC-1461 | `ce::test_c04_a_ppp_com_inscritos_nao_menciona_lista_vazia`; `nv` |
| SC-1462 | `ce::test_a_espera_do_definitivo_nao_oferece_publicar_como_preliminar`; `ce::test_c08_na_previa_de_publicacao_a_mensagem_e_a_de_antes`; `ce::test_c08_a_previa_de_publicacao_mostra_a_mensagem_de_antes`; `nv` |
| SC-1463 | `un::test_a_redacao_da_nota_nao_decide_a_situacao`; `un::test_o_resumo_do_perfil_le_o_dado_e_nao_a_nota` |
| SC-1464 | `ce::test_c06_o_resumo_do_perfil_diz_o_escopo_e_os_numeros_sao_os_de_antes` |
| SC-1465 | `es` (os três casos, com os tetos de antes); `cr::test_a_pergunta_custa_ate_duas_consultas_e_nao_cresce_com_as_inscricoes` |
| SC-1466 | `make check` (`makemigrations --check`); a suíte contra PostgreSQL, em [verificacao.md](verificacao.md) |
