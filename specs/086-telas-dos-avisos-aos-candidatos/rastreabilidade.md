# Rastreabilidade — 086

Caminhos de teste relativos a `backend/tests/`. "Navegador" é o percurso do [quickstart](quickstart.md);
"inventário" é a comparação com a linha de base de antes, em
[`depois-da-086/antes/`](../../doc/inventario-visual-da-gestao-2026-10-16/depois-da-086/antes/), pelo
`comparar.py`, pelo `medidas.py` e pixel a pixel.

| Requisito | Onde é provado |
|---|---|
| FR-1940 | `interface/test_telas_dos_avisos.py` (`test_nos_avisos_do_edital_a_trilha_passa_pelo_processo`, `test_no_aviso_e_na_interrupcao_a_trilha_passa_pelos_avisos`, `test_a_previa_do_resultado_pende_dos_avisos_do_edital`, `test_nos_modelos_a_trilha_comeca_na_secao_da_barra`, `test_no_modelo_a_trilha_volta_aos_modelos`) |
| FR-1941 | `interface/test_telas_dos_avisos.py` (os níveis do Edital em ordem e o rótulo da tela no fim, nos três primeiros; `test_a_interrupcao_recusada_tem_a_mesma_trilha_e_o_erro_abaixo_do_titulo`) |
| FR-1942 | `interface/test_telas_dos_avisos.py` (`test_a_previa_do_resultado_pende_dos_avisos_do_edital`, `test_a_previa_do_reenvio_pende_do_aviso_anterior`, `test_a_previa_da_chamada_pende_da_convocacao_e_o_reenvio_do_aviso`) |
| FR-1943 | `interface/test_telas_dos_avisos.py` (`test_todo_link_da_trilha_leva_aonde_diz`, `test_a_previa_da_chamada_pende_da_convocacao_e_o_reenvio_do_aviso`) |
| FR-1944 | `interface/test_telas_dos_avisos.py` (`test_nos_modelos_a_trilha_comeca_na_secao_da_barra`, `test_no_modelo_a_trilha_volta_aos_modelos`, `test_o_modelo_recusado_termina_em_novo_modelo`); `interface/test_shell_da_gestao.py` (`test_a_secao_sai_do_endereco`), sem mudança |
| FR-1945 | `interface/test_telas_dos_avisos.py` (`trilha_unica_no_cabecalho` e o conteúdo que começa pelo título em todos; `test_nenhuma_das_seis_tem_trilha_no_conteudo`); `interface/test_telas_de_quem_elabora.py` (`test_o_produto_da_trilha_tem_uma_fonte_so`), sem mudança |
| FR-1946 | `interface/test_telas_dos_avisos.py` (`test_quem_so_consulta_le_a_mesma_trilha_de_quem_avisa`, em duas telas) |
| FR-1947 | Inventário — as telas do escopo a 375 px sem estouro, nos dois estados da barra; navegador a 375 px, com a trilha de sete níveis do reenvio |
| FR-1948 | `interface/test_telas_dos_avisos.py` (`test_os_avisos_do_edital_vazios_tem_o_estado_vazio_comum`, `test_nos_modelos_a_trilha_comeca_na_secao_da_barra`); navegador no 76/2027 |
| FR-1949 | `interface/test_telas_dos_avisos.py` (`test_no_modelo_a_trilha_volta_aos_modelos`, `test_a_interrupcao_recusada_tem_a_mesma_trilha_e_o_erro_abaixo_do_titulo`) |
| FR-1950 | `interface/test_telas_dos_avisos.py` (`test_nos_modelos_a_trilha_comeca_na_secao_da_barra`) |
| FR-1951 | `interface/test_telas_dos_avisos.py` (`test_as_acoes_que_nao_se_desfazem_nao_mudam_de_desenho`, `test_a_previa_do_resultado_pende_dos_avisos_do_edital`); `interface/test_avisos.py`, sem mudança |
| FR-1952 | Inventário refeito com `BARRA=expandida` e `BARRA=recolhida`, comparado por `comparar.py`, por `medidas.py` e pixel a pixel; `interface/test_acessibilidade.py`, `interface/test_larguras.py`, `interface/test_estaticos.py`, `interface/test_polish_da_055.py`, `test_vocabulario_do_aviso.py` |
| SC-760 | Inventário: estouram a 375 e a 1280 px, zero; nenhum `status` diferente |
| SC-761 | Inventário: fora das nove variantes do escopo, nenhuma muda de largura ou altura |
| SC-762 | `interface/test_telas_dos_avisos.py` (uma trilha por página, no cabeçalho, cada nível como link) |
| SC-763 | `interface/test_telas_dos_avisos.py` (o Processo nas quatro telas de um Edital; `test_todo_link_da_trilha_leva_aonde_diz`; os modelos sem *Processos Seletivos*); a contagem de antes na pesquisa (R-001, R-002, R-003) |
| SC-764 | `make test-pg` |
| SC-765 | Navegador pelo teclado, a 1280 e a 375 px |
