# Rastreabilidade — 082

Caminhos de teste relativos a `backend/tests/`. "Navegador" é o percurso do [quickstart](quickstart.md).

| Requisito | Onde é provado |
|---|---|
| FR-1840 | `interface/test_trilha_da_conferencia_da_consolidacao.py` (`test_a_trilha_e_a_da_distribuicao_com_conferir`, pelos dois caminhos; `test_a_trilha_abre_com_a_mesma_navegacao_das_outras_telas`); `interface/test_telas_de_quem_elabora.py` (`test_o_produto_da_trilha_tem_uma_fonte_so`), sem mudança |
| FR-1841 | `interface/test_trilha_da_conferencia_da_consolidacao.py` (os níveis da Distribuição, em ordem, e "Conferir" no fim) |
| FR-1842 | `interface/test_trilha_da_conferencia_da_consolidacao.py` (`trilha_unica_no_cabecalho` e o conteúdo que começa pelo título; a `nav.trilha` fora do template) |
| FR-1843 | `interface/test_trilha_da_conferencia_da_consolidacao.py` (parametrizado: pela seleção e por todas as prontas) |
| FR-1844 | `interface/test_trilha_da_conferencia_da_consolidacao.py` (`test_o_alcance_e_o_ato_continuam_os_mesmos`, `test_o_que_fica_de_fora_continua_declarado`); `interface/test_prontidao_na_tela.py` e `interface/test_consolidar_todas_as_prontas.py`, sem mudança |
| FR-1845 | Navegador a 375 e a 1280 px; `interface/test_acessibilidade.py`, `interface/test_larguras.py`, `interface/test_estaticos.py` |
| SC-720 | `interface/test_trilha_da_conferencia_da_consolidacao.py` (uma trilha por página, no cabeçalho, cada nível como link) |
| SC-721 | `interface/test_trilha_da_conferencia_da_consolidacao.py` (o Processo e a Alocação por Etapa na trilha); as outras seis em `interface/test_telas_filhas_da_distribuicao.py`; a contagem de antes na pesquisa (R-001) |
| SC-722 | Navegador: `scrollWidth` igual a `clientWidth` a 375 e a 1280 px |
| SC-723 | `make test-pg` |
