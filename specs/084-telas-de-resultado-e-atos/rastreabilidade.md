# Rastreabilidade — 084

Caminhos de teste relativos a `backend/tests/`. "Navegador" é o percurso do [quickstart](quickstart.md);
"inventário" é a comparação com a linha de base de antes, em
[`depois-da-084/antes/`](../../doc/inventario-visual-da-gestao-2026-10-16/depois-da-084/antes/), pelo
`comparar.py`, pelo `medidas.py` e pixel a pixel.

| Requisito | Onde é provado |
|---|---|
| FR-1880 | `interface/test_telas_de_resultado_e_atos.py` (`test_a_trilha_mora_no_bloco_do_cabecalho`, nas onze; `test_nas_telas_do_marco_a_trilha_e_a_do_edital_com_a_tela`; `test_na_conferencia_da_emissao_o_marco_volta_ao_recorte`; `test_no_corte_historico_a_trilha_termina_na_emissao`; `test_no_sorteio_a_trilha_e_a_do_edital`; `test_na_exportacao_a_trilha_e_a_do_edital`) |
| FR-1881 | `interface/test_telas_de_resultado_e_atos.py` (os níveis do Edital em ordem e o rótulo da tela no fim, nos mesmos testes; `test_nos_historicos_a_trilha_passa_pela_tela_de_origem_no_mesmo_recorte`; `test_o_ato_de_classificacao_ganha_o_edital_na_trilha`); `interface/test_navegacao_entre_recortes.py` (`test_a_confirmacao_volta_para_o_recorte_que_se_esta_confirmando`), sem mudança |
| FR-1882 | `interface/test_telas_de_resultado_e_atos.py` (`test_a_trilha_mora_no_bloco_do_cabecalho` e `trilha_unica_no_cabecalho` com o conteúdo pelo título, nos testes renderizados); `interface/test_telas_de_quem_elabora.py` (`test_o_produto_da_trilha_tem_uma_fonte_so`) e `interface/test_acessibilidade_da_012.py`, sem mudança |
| FR-1883 | `interface/test_telas_de_resultado_e_atos.py` (`test_quem_audita_le_a_mesma_trilha_de_quem_conduz`; `test_na_exportacao_a_trilha_e_a_do_edital`, por quem só exporta); navegador como `paulo.presidente`, `inventario.auditora` e `inventario.exportadora` |
| FR-1884 | Inventário — as dez telas do escopo a 375 px sem estouro, nos dois estados da barra; navegador a 375 px, no Ato de classificação |
| FR-1885 | Diff dos onze templates: só a trilha muda; `interface/test_convocacao.py`, `interface/test_corte.py`, `interface/test_ocupacao.py`, `interface/test_console_do_sorteio.py`, `test_vocabulario_da_ocupacao.py` e `interface/test_exportacao_de_matriculas.py`, sem mudança |
| FR-1886 | `interface/test_telas_de_resultado_e_atos.py` (`test_nenhum_botao_muda_de_rotulo_desenho_ou_lugar`, nas onze; `test_nenhuma_acao_que_nao_se_desfaz_ganhou_peso`; `test_na_conferencia_da_emissao_o_marco_volta_ao_recorte`) |
| FR-1887 | Diff dos onze templates; `test_vocabulario_da_composicao.py`, `test_vocabulario_do_resultado.py` e `test_vocabulario_da_ocupacao.py`, sem mudança |
| FR-1888 | Inventário refeito com `BARRA=expandida` e `BARRA=recolhida`, comparado por `comparar.py`, por `medidas.py` e pixel a pixel |
| FR-1889 | `interface/test_acessibilidade.py`, `interface/test_larguras.py`, `interface/test_estaticos.py`, `interface/test_polish_da_055.py`, `test_vocabulario_da_composicao.py` |
| SC-740 | Inventário: estouram a 375 e a 1280 px, zero; nenhum `status` diferente |
| SC-741 | Inventário: fora das dez telas do escopo, nenhuma variante muda de largura ou altura |
| SC-742 | `interface/test_telas_de_resultado_e_atos.py` (uma trilha por página, no cabeçalho, cada nível como link) |
| SC-743 | `interface/test_telas_de_resultado_e_atos.py` (o Processo e o Edital na trilha das onze, pela fonte); a contagem de antes na pesquisa (R-001) |
| SC-744 | `make test-pg` |
| SC-745 | Navegador pelo teclado, a 1280 e a 375 px |
