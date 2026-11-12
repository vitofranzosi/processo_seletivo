# Rastreabilidade: Convocar e publicar num gesto só (159)

Caminhos relativos a `backend/tests/`. Abreviações:

- `int` = `integration/convocacao/test_convocar_e_publicar.py`
- `tela` = `interface/test_convocar_e_publicar_na_tela.py`
- `bot` = `interface/test_telas_de_resultado_e_atos.py` (os botões e o peso deles)
- `nav` = o percurso no navegador com o cenário C10 (ver o PR)

A faixa abre em **FR-6801** e **SC-2251**, e gasta até FR-6818 e SC-2256.

| Requisito | Tarefa | Teste |
|---|---|---|
| FR-6801 | T002, T004, T005, T006 | `int::test_por_mensagem_uma_confirmacao_convoca_envia_e_publica`, `tela::test_por_mensagem_a_conferencia_mostra_o_publico_e_a_confirmacao_publica` |
| FR-6802 | T005, T006 | `tela::test_por_mensagem_a_conferencia_mostra_o_publico_e_a_confirmacao_publica`, `nav` |
| FR-6803 | T005, T006 | `tela::*`, `bot` |
| FR-6804 | T005, T006 | o parcial e a conferência sem autoridade desabilitam o botão; `nav` |
| FR-6805 | T002 | `int::test_por_mensagem_uma_confirmacao_convoca_envia_e_publica` |
| FR-6806 | T002, T007 | `int::test_a_mensagem_que_falhou_fica_fora_e_o_reenvio_publica_a_que_saiu` |
| FR-6807 | T003 | `int::test_a_mensagem_que_falhou_fica_fora_e_o_reenvio_publica_a_que_saiu` |
| FR-6808 | T005 | `tela::test_por_publicacao_dois_botoes_e_o_gps_publica_como_ato_oficial`, `int::test_sem_veiculo_a_forma_por_publicacao_nao_presume_o_gps` |
| FR-6809 | T001, T002 | `int::test_no_gps_convocar_e_publicar_sao_um_instante`, `int::test_no_gps_sem_declaracao_nada_e_convocado` |
| FR-6810 | T002 | `int::test_sem_veiculo_a_forma_por_publicacao_nao_presume_o_gps` |
| FR-6811 | T003 | `int::test_o_registro_externo_tambem_divulga_e_o_prazo_corre_do_registro` |
| FR-6812 | T002, T007 | `int::test_a_falha_da_publicacao_nao_desfaz_a_convocacao_e_a_repeticao_a_completa` |
| FR-6813 | T002 | `int::test_a_falha_da_publicacao_nao_desfaz_a_convocacao_e_a_repeticao_a_completa` |
| FR-6814 | T007 | a seção da tela do recorte e a página da `149`, com os testes delas |
| FR-6815 | T001 | `int::test_a_mensagem_que_falhou_fica_fora_e_o_reenvio_publica_a_que_saiu` |
| FR-6816 | T004, T006 | `int::test_a_suplente_chamada_por_mensagem_sai_numa_publicacao`, `int::test_a_correcao_publicada_no_gps_sai_marcada` |
| FR-6817 | T004 | `int::test_a_correcao_publicada_no_gps_sai_marcada` |
| FR-6818 | T001 | os testes da `149` e da `050`, que continuam passando |

| Critério | Teste |
|---|---|
| SC-2251 | `int::test_por_mensagem_uma_confirmacao_convoca_envia_e_publica`, `tela::test_por_mensagem_a_conferencia_mostra_o_publico_e_a_confirmacao_publica`, `nav` |
| SC-2252 | `int::test_a_mensagem_que_falhou_fica_fora_e_o_reenvio_publica_a_que_saiu` |
| SC-2253 | `int::test_no_gps_convocar_e_publicar_sao_um_instante`, `int::test_no_gps_sem_declaracao_nada_e_convocado` |
| SC-2254 | `int::test_o_registro_externo_tambem_divulga_e_o_prazo_corre_do_registro` |
| SC-2255 | `int::test_a_falha_da_publicacao_nao_desfaz_a_convocacao_e_a_repeticao_a_completa` |
| SC-2256 | `int::test_a_suplente_chamada_por_mensagem_sai_numa_publicacao`, `int::test_a_correcao_publicada_no_gps_sai_marcada` |
