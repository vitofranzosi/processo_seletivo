# Rastreabilidade: A tela do sorteio como a jornada de quem o conduz (142)

Cada requisito → a tarefa que o implementa → o teste ou a medição que o verifica. Caminhos relativos
a `backend/tests/`. Abreviações:

- `uj` = `unit/interface/test_jornada_do_sorteio.py` — os passos, sem banco
- `ij` = `interface/test_jornada_do_sorteio.py` — a tela, contra PostgreSQL, num certame de três listas
- `ts` = `interface/test_tela_do_sorteio.py`, `ta` = `interface/test_telas_de_resultado_e_atos.py`
- `cap` = o roteiro `specs/142-jornada-do-sorteio/capturas/capturar.py`, sobre o C06 e o C07 da `134`

A faixa abre em **FR-4900**, **SC-1540** e **UX-350**. Gastos até FR-4918, SC-1546 e UX-352; o resto
da reserva (até o requisito quatro mil novecentos e quarenta e nove, o critério mil quinhentos e
cinquenta e nove e a regra trezentos e sessenta e nove) fica livre.

## Requisitos funcionais

| Requisito | Tarefa | Verificação |
|---|---|---|
| FR-4900 — quatro passos, nomes de `conceitos.py` | T004, T007 | `uj::test_os_quatro_passos_na_ordem_com_os_nomes_do_centro`, `ij::test_nada_preparado_os_quatro_passos_na_ordem_e_fixar_e_a_tarefa_de_agora` |
| FR-4901 — o que pede, alcança, desencadeia, se volta atrás | T004, T007 | `uj::test_cada_passo_diz_o_que_pede_alcanca_desencadeia_e_se_volta_atras`, `uj::test_os_textos_da_tela_nao_usam_os_termos_que_ela_define` |
| FR-4902 — a situação vem da derivação | T004, T006 | `ij::test_a_tela_diz_o_mesmo_que_o_centro_e_a_providencia_chega_a_execucao`, `uj::test_a_ordem_gravada_e_dita_pelo_fato_e_nao_pela_celula_do_sorteio` |
| FR-4903 — os formulários sob as condições de antes | T011, T013, T019 | `cap` (os formulários iguais nos 13 estados, `verificacao.md`), `ts::test_os_destinos_de_post_desta_tela_sao_declarados_e_finitos`, `ij::test_fixar_a_lista_vazia_por_formulario_forjado_e_recusado_como_antes` |
| FR-4904 — as seções na ordem dos passos, o contexto no alto | T007 | `ij::test_nada_preparado_os_quatro_passos_na_ordem_e_fixar_e_a_tarefa_de_agora` |
| FR-4905 — quantas listas, em que situação | T004, T007 | `uj::test_uma_lista_fixada_e_outra_nao_o_passo_conta_as_duas_e_a_semente_nao_trava`, `ij::test_a_ampla_fixada_e_a_ppi_pendente`, `ij::test_uma_sorteada_e_a_outra_nao` |
| FR-4906 — a semente do marco, uma vez | T004, T013 | `uj::test_a_semente_e_do_marco_e_aparece_uma_vez`, `ij::test_com_a_semente_o_sorteio_e_a_vez_e_a_semente_aparece_uma_vez` |
| FR-4907 — o método recolhido, inteiro | T013 | `ij::test_nada_preparado_os_quatro_passos_na_ordem_e_fixar_e_a_tarefa_de_agora`, `interface/test_relacao_de_habilitados.py::test_a_tela_mostra_o_metodo_lido_do_edital_e_a_previa_da_relacao` |
| FR-4908 — a conferência no cartão | T011 | `ij::test_a_conferencia_vem_no_cartao_antes_do_botao`, `uj::test_o_depois_de_fixar_acompanha_a_situacao_da_semente` |
| FR-4909 — a observação como antes | T009 | `ij::test_a_ampla_fixada_e_a_ppi_pendente`, `ta::test_nenhuma_acao_que_nao_se_desfaz_ganhou_peso` |
| FR-4910 — a tarefa de agora | T004, T009 | `uj::test_nada_preparado_o_primeiro_passo_e_a_tarefa_de_agora`, `uj::test_o_sinal_do_passo_e_o_da_lista_mais_urgente`, `ij::test_todas_fixadas_a_semente_e_a_vez`, `ij::test_com_fixar_como_a_vez_sortear_e_secundario_e_o_texto_fala_dos_numeros`, `ij::test_com_tudo_fixado_sortear_volta_a_ser_o_botao_principal` |
| FR-4911 — a execução por lista | T013 | `ij::test_com_a_semente_o_sorteio_e_a_vez_e_a_semente_aparece_uma_vez`, `ij::test_uma_sorteada_e_a_outra_nao`, `ts::test_a_anulacao_e_percorrivel_pela_tela` |
| FR-4912 — a ordem gravada | T004, T015 | `ij::test_uma_sorteada_e_a_outra_nao`, `ij::test_o_sorteio_concluido`, `ij::test_depois_de_sortear_a_cota_a_mensagem_e_a_abertura_sao_da_cota` |
| FR-4913 — relação, ordem, classificação e corte; a divulgação pelo dado | T015 | `ij::test_uma_sorteada_e_a_outra_nao`, `uj::test_a_divulgacao_so_e_afirmada_quando_a_celula_e_do_ato_vigente` |
| FR-4914 — o corte só com sorteio | T015 | `ij::test_nada_preparado_os_quatro_passos_na_ordem_e_fixar_e_a_tarefa_de_agora`, `ij::test_uma_sorteada_e_a_outra_nao` |
| FR-4915 — os destinos da `139` e o da execução | T003 | `uj::test_a_execucao_tem_ancora_propria_e_a_tela_le_a_mesma_funcao`, `ij::test_a_tela_diz_o_mesmo_que_o_centro_e_a_providencia_chega_a_execucao`, `integration/treinamento/test_chegada_e_volta_nos_cenarios.py::test_c06` |
| FR-4916 — a mensagem do ato e o próximo, no alto | T007 | `ij::test_a_ampla_fixada_e_a_ppi_pendente`, `interface/test_console_do_sorteio.py` |
| FR-4917 — quem só lê | T017 | `uj::test_quem_so_le_nao_tem_tarefa_de_agora`, `ij::test_a_auditoria_ve_os_passos_sem_controle_e_sem_tarefa_de_agora` |
| FR-4918 — sem derivação | T004 | `uj::test_sem_derivacao_os_passos_existem_sem_situacao` |

## Regras de experiência

| Regra | Verificação |
|---|---|
| UX-350 — palavra e sinal | `ij::test_a_ampla_fixada_e_a_ppi_pendente` (o sinal e a palavra no texto do cartão) |
| UX-351 — lista ordenada, link para a seção, ordem do teclado | `ij::test_nada_preparado_os_quatro_passos_na_ordem_e_fixar_e_a_tarefa_de_agora`; `cap` |
| UX-352 — 375 px, CSP | `cap` (sem rolagem horizontal e sem violação nos estados medidos); `interface/test_acessibilidade*.py`, `test_estaticos*` na suíte |

## Critérios de sucesso

| Critério | Verificação |
|---|---|
| SC-1540 — fixar acima de observar | `cap`: estados 01, 02 e 04 (`verificacao.md`); `ij::test_nada_preparado_os_quatro_passos_na_ordem_e_fixar_e_a_tarefa_de_agora` |
| SC-1541 — a mesma situação do Centro | `ij::test_a_tela_diz_o_mesmo_que_o_centro_e_a_providencia_chega_a_execucao`; capturas `*-11-*` |
| SC-1542 — os mesmos formulários | `cap`: 13 de 13 estados iguais (`verificacao.md`) |
| SC-1543 — N posições | `ij::test_uma_sorteada_e_a_outra_nao`, `ij::test_o_sorteio_concluido` |
| SC-1544 — sem frase de divulgação | `ij::test_uma_sorteada_e_a_outra_nao` |
| SC-1545 — 375 px e CSP | `cap` |
| SC-1546 — sem "Nenhum corte emitido" antes do sorteio | `ij::test_nada_preparado_os_quatro_passos_na_ordem_e_fixar_e_a_tarefa_de_agora`, `ij::test_uma_sorteada_e_a_outra_nao` |
