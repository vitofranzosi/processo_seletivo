# Rastreabilidade: Os mesmos recortes no sorteio, na divulgação, na ocupação e na Supervisão (122)

Cada requisito → as tarefas que o implementam → os testes que o verificam. Os nomes foram conferidos
contra os arquivos depois da implementação. Caminhos relativos a `backend/tests/`. Abreviações:

- `up` = `unit/editais/test_papel_do_recorte.py` — papel, recusa e origem, sem banco
- `rc` = `integration/sorteios/test_recorte_excedente_recusado.py` — os três comandos
- `tp` = `integration/classificacao/test_recortes_alinhados_temporal.py` — a matriz temporal
- `sv` = `integration/supervisao/test_sinais_sem_recorte_excedente.py` — a Supervisão
- `it` = `interface/test_recortes_alinhados.py` — as telas
- `de` = `interface/test_destinos_do_edital.py` — a página do Edital, por ator (033, revisto)
- `ps` = `interface/test_previa_do_sorteio.py` — a prévia do sorteio (098, revisto)
- `pb` = `portal/test_recorte_excedente_publico.py` — o canal público
- `vf` = `verificacao.md`

## Requisitos funcionais

| Requisito | Tarefas | Testes |
|---|---|---|
| FR-3893 (uma derivação para sorteio, divulgação, condução, Supervisão) | T006, T009, T025 | `it::TestOSorteioTrabalhaNosTresRecortes::test_a_tela_mostra_tres_recortes_e_nenhum_bloco_de_ac`; `it::test_seis_superficies_contam_os_mesmos_tres_recortes` (SC-1166) |
| FR-3894 (só o apontamento decide) | T006 | `up::test_a_modalidade_chamada_ampla_sem_apontamento_e_operacional`; `it::test_perfil_sem_apontamento_trata_ac_como_recorte` |
| FR-3895 (a tela e a prévia do sorteio sem o recorte; a frase) | T009, T012, T013 | `it::test_a_tela_mostra_tres_recortes_e_nenhum_bloco_de_ac`; `ps::test_perfil_sem_reserva_tem_uma_lista_e_nao_fala_de_cotas` |
| FR-3896 (o marco sorteado sem esperar o excedente) | T009 | `it::test_o_marco_esta_sorteado_sem_esperar_por_ac` |
| FR-3897 (congelar recusado) | T006, T010 | `rc::test_congelar_a_relacao_da_modalidade_apontada_e_recusado`, `::test_suceder_a_relacao_excedente_com_motivo_tambem_e_recusado`; `up::test_a_recusa_nomeia_a_modalidade_e_manda_para_a_ampla` |
| FR-3898 (sortear a relação excedente congelada recusado) | T011 | `rc::test_a_relacao_excedente_congelada_nao_sorteia`, `::test_anular_e_sortear_de_novo_no_recorte_excedente_e_recusado` |
| FR-3899 (divulgar recusado; o anterior intacto) | T018 | `rc::test_divulgar_o_ato_excedente_e_recusado_e_nada_se_grava`, `::test_a_publicacao_excedente_feita_antes_fica_como_esta`, `::test_os_recortes_operacionais_continuam_divulgaveis` |
| FR-3900 (nenhum ato gravado no excedente; a computada normaliza) | T010, T011 | a normalização da `034` continua presa pelos testes dela (`unit/classificacao/test_recortes_do_marco.py`); o caminho do sorteio, por `rc::test_a_relacao_excedente_congelada_nao_sorteia` |
| FR-3901 (as quatro portas) | T013, T019, T022, T025 | `it::test_a_pagina_do_edital_tem_um_caminho_de_divulgacao_por_marco`, `::test_a_tela_do_sorteio_nao_oferece_publicar_o_ato_excedente`, `::test_a_tela_do_ato_excedente_explica_e_nao_oferece_publicar`, `::test_a_previa_do_ato_excedente_explica_e_nao_oferece_o_botao`; `sv::test_nenhum_sinal_aponta_o_recorte_excedente` |
| FR-3902 (o acervo intacto) | T029 | `rc::test_a_publicacao_excedente_feita_antes_fica_como_esta`; `tp::test_t1_apontar_a_modalidade_operacional_a_torna_acervo` |
| FR-3903 (a seção de histórico, com a frase da origem) | T029, T030 | `it::test_o_acervo_nascido_aparece_a_parte_com_a_frase_dele`, `::test_o_acervo_tornado_nomeia_a_retificacao`, `::test_sem_acervo_nao_ha_secao` |
| FR-3904 (tela do ato, Resultados divulgados e prévia marcados) | T022, T031 | `it::test_a_tela_do_ato_excedente_explica_e_nao_oferece_publicar`, `::test_resultados_divulgados_marca_a_publicacao_excedente`, `::test_a_previa_do_ato_excedente_explica_e_nao_oferece_o_botao` |
| FR-3905 (o canal público responde como antes) | — | `pb::test_a_pagina_publica_do_acervo_responde_sem_a_marca_da_gestao` (quatro páginas); a `122` não toca `portal/` (`git diff --stat main -- backend/processo_seletivo/portal` vazio) |
| FR-3906 (um caminho de divulgação por marco) | T019, T020 | `it::test_a_pagina_do_edital_tem_um_caminho_de_divulgacao_por_marco`; `de::test_o_publicador_puro_nao_ve_o_que_nao_e_dele`, `::test_quem_preside_e_publica_ve_a_uniao_sem_repetir`, `::test_marco_sem_ato_emitido_nao_oferece_divulgacao` |
| FR-3907 (o Publicador puro chega à prévia) | T019, T021 | `it::test_o_publicador_puro_chega_a_previa_de_cada_recorte_pelo_quadro`; `de::test_o_publicador_puro_ve_o_caminho_ate_a_divulgacao` |
| FR-3908 (o quadro: nome, estado, caminho até a prévia) | T021 | `it::test_o_publicador_puro_chega_a_previa_de_cada_recorte_pelo_quadro`, `::test_o_recorte_divulgado_leva_aos_resultados_divulgados` |
| FR-3909 (a Supervisão sem o excedente) | T025 | `sv::test_nenhum_sinal_aponta_o_recorte_excedente`; `tp::test_t1_apontar_a_modalidade_operacional_a_torna_acervo`, `::test_t3_trocar_o_apontamento_faz_as_duas_coisas_ao_mesmo_tempo` |
| FR-3910 (o sinal operacional continua, para a prévia dele) | T025 | `sv::test_o_recorte_operacional_nao_divulgado_continua_sinalizado` |
| FR-3911 (vigente decide; origem explica) | T006, T029 | `up::test_registro_feito_sob_o_apontamento_nasceu_excedente`, `::test_registro_operacional_que_uma_retificacao_apontou_se_tornou_excedente`, `::test_uma_retificacao_alheia_ao_apontamento_nao_muda_a_origem` |
| FR-3912 (papel mudado: obsoleto, causa nomeada) | T034 | `tp::test_t2_retirar_o_apontamento_nao_reabilita_o_ato_nascido_excedente`, `::test_t3_trocar_o_apontamento_faz_as_duas_coisas_ao_mesmo_tempo`, `::test_a_ampla_nao_muda_de_papel_e_continua_valendo`; `up::test_a_retificacao_que_mudou_o_papel_e_a_primeira_diferente` |
| FR-3913 (apontar torna acervo, sem sinal) | T025, T029 | `tp::test_t1_apontar_a_modalidade_operacional_a_torna_acervo`; `it::test_o_acervo_tornado_nomeia_a_retificacao` |
| FR-3914 (sem tabela, coluna, situação) | — | `makemigrations --check` na verificação (`vf`) |
| FR-3915 (portal e avisos não mudam) | — | `pb::test_a_pagina_publica_do_acervo_responde_sem_a_marca_da_gestao[selecao]`; `git diff` sem `portal/` nem `avisos/` |
| FR-3916 (o relatório pelos recortes operacionais) | T032 | `it::TestORelatorioDoEditalContaOsRecortesOperacionais::test_o_ato_excedente_nao_divulgado_nao_vira_linha_nem_pendencia`, `::test_a_publicacao_excedente_feita_aparece_marcada` |


## Critérios de sucesso

| Critério | Testes |
|---|---|
| SC-1165 (a jornada do operador) | `navegador/test_jornada_dos_recortes.py::test_a_jornada_dos_tres_recortes_sem_cobranca_da_lista_excedente`, com capturas em `capturas/`; o percurso humano num banco de demonstração fica para o usuário (`vf`) |
| SC-1166 (seis superfícies, três recortes) | `it::test_seis_superficies_contam_os_mesmos_tres_recortes` |
| SC-1167 (um caminho por marco; dois cliques até a prévia) | `it::test_a_pagina_do_edital_tem_um_caminho_de_divulgacao_por_marco`, `::test_o_publicador_puro_chega_a_previa_de_cada_recorte_pelo_quadro` |
| SC-1168 (zero sinais sobre o excedente) | `sv::test_nenhum_sinal_aponta_o_recorte_excedente` |
| SC-1169 (três comandos recusam; nenhuma porta oferece) | `rc` inteiro; `it::TestQuemDivulgaEncontraCadaRecorte` |
| SC-1170 (o acervo consultável; o canal público igual) | `pb::test_a_pagina_publica_do_acervo_responde_sem_a_marca_da_gestao`; `it::test_o_acervo_nascido_aparece_a_parte_com_a_frase_dele` |
| SC-1171 (papel mudado não volta a valer sem ato novo) | `tp::test_t2_retirar_o_apontamento_nao_reabilita_o_ato_nascido_excedente`, `::test_t3_trocar_o_apontamento_faz_as_duas_coisas_ao_mesmo_tempo` |

## Casos-limite

| Caso | Testes |
|---|---|
| Perfil sem apontamento | `it::test_perfil_sem_apontamento_trata_ac_como_recorte`; `up::test_a_modalidade_chamada_ampla_sem_apontamento_e_operacional` |
| Apontamento para Modalidade sem inscrito | coberto pela regra: sem registro não há o que recusar nem explicar, e a frase da FR-3895 depende só do apontamento (`it::test_a_tela_mostra_tres_recortes_e_nenhum_bloco_de_ac`) |
| Marco por classificação computada | `de::test_o_publicador_puro_ve_o_caminho_ate_a_divulgacao` (o cenário de `de` é computado) |
| Pedido repetido com a mesma chave | `rc::test_o_pedido_repetido_devolve_o_desfecho_anterior` |
| Sucessão no recorte excedente | `rc::test_suceder_a_relacao_excedente_com_motivo_tambem_e_recusado`, `::test_anular_e_sortear_de_novo_no_recorte_excedente_e_recusado` |
| Ato excedente obsoleto e vigente: nenhum é trabalho | `sv::test_nenhum_sinal_aponta_o_recorte_excedente` |
| Ato excedente já divulgado como definitivo | `rc::test_a_publicacao_excedente_feita_antes_fica_como_esta` (a natureza não muda a recusa, que vem antes dela) |
| Edital sem marco por sorteio | `it::test_sem_acervo_nao_ha_secao` |
| Ator que não alcança o marco | `it::test_quem_nao_alcanca_o_marco_nao_ve_o_registro` |
| Edital encerrado ou cancelado | inalterado: a Supervisão já não sinaliza trabalho nesse Edital (`integration/supervisao/test_sinais.py`, da `038`) |

## Casos temporais (R-11)

| Caso | Teste |
|---|---|
| T1 | `tp::test_t1_apontar_a_modalidade_operacional_a_torna_acervo` |
| T2 | `tp::test_t2_retirar_o_apontamento_nao_reabilita_o_ato_nascido_excedente` |
| T3 | `tp::test_t3_trocar_o_apontamento_faz_as_duas_coisas_ao_mesmo_tempo` |
| T4 | `up::test_uma_retificacao_alheia_ao_apontamento_nao_muda_a_origem` |
| T5 | `up::test_o_tornado_nomeia_a_primeira_retificacao_e_nao_a_ultima` |
| T6 | `rc::test_a_relacao_excedente_congelada_nao_sorteia` |
| T7 | `up::test_registro_feito_sob_o_apontamento_nasceu_excedente` (a frase sai da versão do registro) |
