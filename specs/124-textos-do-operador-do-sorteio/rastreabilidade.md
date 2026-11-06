# Rastreabilidade: Os textos que o operador do sorteio lê (124)

Cada requisito → as tarefas que o implementam → os testes que o verificam. Caminhos relativos a
`backend/tests/`. Abreviações:

- `fa` = `integration/sorteios/test_falha_de_acesso_a_fonte.py`
- `ts` = `interface/test_tela_do_sorteio.py`
- `mm` = `interface/test_metodo_do_marco.py`
- `vf` = [verificacao.md](verificacao.md)

## Requisitos funcionais

| Requisito | Tarefas | Testes |
|---|---|---|
| FR-3961 (o motivo com as palavras da conferência) | T001, T002, T004 | `fa::test_a_observacao_diz_o_motivo_com_as_palavras_da_conferencia` (cinco falhas); `fa::test_a_recusa_nao_traz_nome_de_excecao_nem_asteriscos`; `fa::test_o_adaptador_da_loteria_separa_os_dois_desfechos` |
| FR-3962 (o detalhe técnico no log, com a correlação) | T002, T004, T012 | `fa::test_o_detalhe_tecnico_vai_para_o_log_com_a_correlacao`; `fa::test_a_observacao_diz_o_motivo_com_as_palavras_da_conferencia` (as `falhas`); `integration/sorteios/test_superficies_da_semente.py::test_a_porta_da_fonte_devolve_material_bruto_e_nao_semente` |
| FR-3963 (a recusa sem marcação, e sem contradizer a evidência) | T003, T004, T012 | `fa::test_a_recusa_nao_traz_nome_de_excecao_nem_asteriscos` |
| FR-3964 (só o dia, e 00h00 como limite) | T005, T006 | `ts::test_a_fonte_que_publica_so_o_dia_nao_parece_ter_dado_a_hora` |
| FR-3965 (a fonte que publica a hora; a fora do vocabulário) | T005, T006 | `ts::test_a_fonte_que_publica_a_hora_continua_dizendo_que_a_publica`, `::test_a_fonte_fora_do_vocabulario_nao_ganha_afirmacao` |
| FR-3966 (o item da ocorrência na ajuda da etapa) | T007, T008 | `mm::test_a_ajuda_da_etapa_explica_a_ocorrencia_a_quem_enxerga`; `interface/test_compor_classificacao.py::test_cada_item_da_ajuda_leva_ao_campo_que_explica`; `interface/test_medida_dos_campos.py::test_toda_descricao_escondida_continua_apontada_por_algum_campo` |
| FR-3967 (as mesmas frases) | T007, T008 | `mm::test_a_ajuda_da_etapa_usa_as_frases_da_descricao_do_campo`; `mm::test_o_campo_pede_so_o_numero` |
| FR-3968 (o comportamento não muda) | — | `fa::test_a_falha_de_acesso_nao_registra_ocorrencia_nenhuma`, `::test_depois_da_falha_a_ocorrencia_declarada_continua_sendo_a_que_vale`; `integration/sorteios/test_consulta_da_fonte.py::test_a_observacao_continua_com_tres_tentativas` |

## Critérios de sucesso

| Critério | Verificação |
|---|---|
| SC-1191 | `fa::test_a_recusa_nao_traz_nome_de_excecao_nem_asteriscos` (cinco falhas) |
| SC-1192 | `vf`, as três telas |
