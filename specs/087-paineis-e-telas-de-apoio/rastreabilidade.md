# Rastreabilidade — 087

Caminhos de teste relativos a `backend/tests/`. "Navegador" é o percurso do [quickstart](quickstart.md);
"inventário" é a comparação com a linha de base de antes, em
[`depois-da-087/antes/`](../../doc/inventario-visual-da-gestao-2026-10-16/depois-da-087/antes/), pelo
`comparar.py` e pelo `medidas.py`.

| Requisito | Onde é provado |
|---|---|
| FR-1970 | `interface/test_paineis_e_telas_de_apoio.py` (`test_nos_paineis_de_secao_a_trilha_e_a_propria_secao`, `test_na_supervisao_a_trilha_passa_pelo_processo`, `test_na_conferencia_do_ato_do_processo_a_trilha_termina_no_ato`, `test_nas_telas_do_assistente_a_trilha_e_a_do_edital`, `test_na_conferencia_do_ato_do_edital_a_trilha_passa_pelo_processo`, `test_em_criar_processo_a_trilha_e_a_da_lista`) |
| FR-1971 | `interface/test_paineis_e_telas_de_apoio.py` (`test_nos_paineis_de_secao_a_trilha_e_a_propria_secao`, na Visão Geral e nas Autoridades); `interface/test_shell_da_gestao.py` (`test_na_propria_secao_o_item_e_a_pagina_atual`, emendado) |
| FR-1972 | `interface/test_paineis_e_telas_de_apoio.py` (os níveis em ordem e o rótulo da tela no fim, nos testes da `FR-1970`) |
| FR-1973 | `interface/test_paineis_e_telas_de_apoio.py` (`trilha_unica_no_cabecalho` e o conteúdo que começa pelo título, nos mesmos testes); `interface/test_telas_de_quem_elabora.py` (`test_o_produto_da_trilha_tem_uma_fonte_so`), sem mudança |
| FR-1974 | `interface/test_paineis_e_telas_de_apoio.py` (a barra na seção de antes, nas oito telas — `barra_em_processos_seletivos` em seis, o item como página nos dois painéis); `interface/test_telas_de_uso_diario.py` (`test_fora_das_telas_de_uso_diario_o_cabecalho_e_o_da_076`) e `interface/test_shell_da_gestao.py` (`test_abaixo_da_secao_o_caminho_a_nomeia_e_nao_repete_a_trilha`), sem mudança |
| FR-1975 | Inventário — as telas do escopo a 375 px sem estouro, nos dois estados da barra; navegador a 375 px |
| FR-1976 | `interface/test_paineis_e_telas_de_apoio.py` (`test_no_assistente_perguntar_e_a_acao_principal`, `test_nas_respostas_a_acao_principal_continua_ver_a_resposta`) |
| FR-1977 | `interface/test_paineis_e_telas_de_apoio.py` (`test_a_conferencia_do_edital_continua_com_o_mesmo_confirmar`, `test_a_conferencia_do_processo_possivel_continua_com_o_mesmo_confirmar`, `test_a_conferencia_do_processo_com_recusa_certa_continua_sem_confirmar`, `test_o_confirmar_dos_atos_tem_o_desenho_de_antes`, `test_encerrar_a_vigencia_continua_perigoso`) |
| FR-1978 | `interface/test_paineis_e_telas_de_apoio.py` (`test_a_visao_geral_tem_os_mesmos_quatro_indicadores`, `test_a_supervisao_tem_o_mesmo_pulso`, `test_o_processo_da_trilha_nao_custa_consulta`, este provado por mutação); `interface/test_visao_geral.py` e `interface/test_supervisao.py`, sem mudança |
| FR-1979 | Inventário refeito com `BARRA=expandida` e `BARRA=recolhida`, comparado por `comparar.py` e por `medidas.py`; `interface/test_acessibilidade.py`, `interface/test_larguras.py`, `interface/test_estaticos.py`, `interface/test_polish_da_055.py`, `test_vocabulario_da_composicao.py` |
| SC-770 | Inventário: estouram a 375 e a 1280 px, zero; nenhum `status` diferente |
| SC-771 | Inventário: fora das telas do escopo, nenhuma variante muda de largura ou altura |
| SC-772 | `interface/test_paineis_e_telas_de_apoio.py` (uma trilha por página, no cabeçalho, cada nível como link) |
| SC-773 | `interface/test_paineis_e_telas_de_apoio.py` (o Processo na trilha das três telas do Edital); a contagem de antes na pesquisa (R-001) |
| SC-774 | `make test-pg` |
| SC-775 | Navegador pelo teclado, a 1280 e a 375 px |
| SC-776 | `doc/inventario-visual-da-gestao-2026-10-16/trilhas_no_cabecalho.py`, antes e depois (R-005); a lista no PR |
