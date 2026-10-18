# Rastreabilidade — 080

Caminhos de teste relativos a `backend/tests/`. "Navegador" é o percurso do [quickstart](quickstart.md);
"inventário" é a comparação com a linha de base de antes, em
[`depois-da-080/antes/`](../../doc/inventario-visual-da-gestao-2026-10-16/depois-da-080/antes/), pelo
`comparar.py`, pelo `medidas.py` e pixel a pixel.

| Requisito | Onde é provado |
|---|---|
| FR-1800 | `interface/test_telas_filhas_da_distribuicao.py` (`test_nas_filhas_a_trilha_e_a_da_distribuicao_com_a_tela`, em cinco telas; `test_na_conferencia_da_retirada_a_trilha_passa_pela_etapa`; `test_na_auditoria_da_comissao_a_trilha_sobe_ao_cabecalho`) |
| FR-1801 | `interface/test_telas_filhas_da_distribuicao.py` (os níveis da Distribuição, em ordem, e o rótulo da tela no fim, nos mesmos testes) |
| FR-1802 | `interface/test_telas_filhas_da_distribuicao.py` (`trilha_unica_no_cabecalho` e o conteúdo que começa pelo título, nos mesmos testes); `interface/test_telas_de_quem_elabora.py` (`test_o_produto_da_trilha_tem_uma_fonte_so`) e `interface/test_acessibilidade_da_012.py`, sem mudança |
| FR-1803 | `interface/test_telas_de_uso_diario.py` (`test_fora_das_telas_de_uso_diario_o_cabecalho_e_o_da_076`, que a `083` passou da Auditoria do Edital à Supervisão). Emendada pela `083`: a Auditoria do Edital tem a trilha no cabeçalho (`FR-1850` da `083`), e o guardião desta spec que a fixava, `test_a_auditoria_do_edital_continua_com_o_cabecalho_da_076`, saiu |
| FR-1804 | `interface/test_telas_filhas_da_distribuicao.py` (`test_quem_audita_le_a_mesma_trilha_de_quem_preside`, em três telas); navegador como `inventario.auditora` |
| FR-1805 | Inventário — as seis telas do escopo a 375 px sem estouro, nos dois estados da barra; navegador a 375 px |
| FR-1806 | `interface/test_telas_filhas_da_distribuicao.py` (`test_na_ocorrencia_o_erro_vem_antes_da_explicacao`, `test_nas_conclusoes_a_resposta_da_reabertura_vem_antes_do_filtro`, `test_nas_conclusoes_o_erro_do_filtro_fica_no_filtro`) |
| FR-1807 | `interface/test_telas_filhas_da_distribuicao.py` (`test_impedimentos_tem_titulo_para_o_registro`) |
| FR-1808 | `interface/test_telas_filhas_da_distribuicao.py` (`test_nas_consultas_filtrar_e_a_acao_principal`, em três telas); `interface/test_polish_da_055.py`, sem mudança |
| FR-1809 | `interface/test_telas_filhas_da_distribuicao.py` (`test_as_acoes_que_nao_se_desfazem_nao_mudam_de_desenho`, `test_na_conferencia_da_retirada_a_trilha_passa_pela_etapa`); `interface/test_distribuicao.py`, sem mudança |
| FR-1810 | Inventário refeito com `BARRA=expandida` e `BARRA=recolhida`, comparado por `comparar.py`, por `medidas.py` e pixel a pixel |
| FR-1811 | `interface/test_acessibilidade.py`, `interface/test_larguras.py`, `interface/test_estaticos.py`, `interface/test_polish_da_055.py`, `test_vocabulario_da_composicao.py`, `test_vocabulario_do_resultado.py` |
| SC-700 | Inventário: estouram a 375 e a 1280 px, zero; nenhum `status` diferente |
| SC-701 | Inventário: fora das seis telas do escopo, nenhuma variante muda de largura ou altura |
| SC-702 | `interface/test_telas_filhas_da_distribuicao.py` (uma trilha por página, no cabeçalho, cada nível como link) |
| SC-703 | `interface/test_telas_filhas_da_distribuicao.py` (o Processo e a Alocação por Etapa na trilha das seis filhas); a contagem de antes na pesquisa (R-001) |
| SC-704 | `make test-pg` |
| SC-705 | Navegador pelo teclado, a 1280 e a 375 px |
