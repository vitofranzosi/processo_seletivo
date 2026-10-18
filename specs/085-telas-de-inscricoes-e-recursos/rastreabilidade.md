# Rastreabilidade — 085

Caminhos de teste relativos a `backend/tests/`. "Navegador" é o percurso do [quickstart](quickstart.md);
"inventário" é a comparação com a linha de base de antes, em
[`depois-da-085/antes/`](../../doc/inventario-visual-da-gestao-2026-10-16/depois-da-085/antes/), pelo
`comparar.py`, pelo `medidas.py` e pixel a pixel.

| Requisito | Onde é provado |
|---|---|
| FR-1910 | `interface/test_telas_de_inscricoes_e_recursos.py` (`test_nas_inscricoes_a_trilha_e_a_do_edital_com_a_tela`, `test_na_inscricao_recebida_a_trilha_passa_pelas_inscricoes`, `test_nos_recursos_e_no_recurso_a_trilha_e_a_do_edital`) |
| FR-1911 | os mesmos testes (os níveis do Edital em ordem e o rótulo da tela no fim); `test_no_rascunho_a_pagina_atual_e_em_preenchimento` |
| FR-1912 | os mesmos testes (`trilha_unica_no_cabecalho` e o conteúdo que começa pelo título); `interface/test_telas_de_quem_elabora.py` (`test_o_produto_da_trilha_tem_uma_fonte_so`), sem mudança |
| FR-1913 | `interface/test_telas_de_inscricoes_e_recursos.py` (`test_nos_recursos_e_no_recurso_a_trilha_e_a_do_edital`: cada nível abre para quem julga); a tabela das portas no R-001 da pesquisa |
| FR-1914 | `interface/test_telas_de_inscricoes_e_recursos.py` (`test_na_inscricao_recebida_a_trilha_passa_pelas_inscricoes`, `test_o_recurso_continua_condicionando_os_caminhos`); `authorization/test_consulta_administrativa.py` e `interface/test_proveniencia_do_recurso.py`, sem mudança |
| FR-1915 | `interface/test_telas_de_inscricoes_e_recursos.py` (`test_a_recusa_continua_com_o_cabecalho_da_076`); `interface/test_telas_de_uso_diario.py` (`test_fora_das_telas_de_uso_diario_o_cabecalho_e_o_da_076`), sem mudança; `interface/test_shell_da_gestao.py` (`test_abaixo_da_secao_o_caminho_a_nomeia_e_nao_repete_a_trilha`, agora nos Avisos do Edital) |
| FR-1916 | Inventário — as cinco variantes do escopo a 375 px sem estouro, nos dois estados da barra; navegador a 375 px |
| FR-1917 | `interface/test_telas_de_inscricoes_e_recursos.py` (`sem_consulta_ao_processo`, nas quatro telas); `interface/test_proveniencia_do_recurso.py` e `interface/test_instrucao_na_peca.py` (orçamentos do Recurso), sem mudança; a medida antes e depois no R-002 da pesquisa |
| FR-1918 | `interface/test_telas_de_inscricoes_e_recursos.py` (`test_sem_inscricao_recebida_a_lista_mostra_o_estado_vazio`, `test_os_rascunhos_sao_regiao_nomeada_e_continuam_advertidos`) |
| FR-1919 | `interface/test_telas_de_inscricoes_e_recursos.py` (`test_os_rascunhos_sao_regiao_nomeada_e_continuam_advertidos`); `integration/interface/test_inscricoes_recebidas.py`, sem mudança |
| FR-1920 | `interface/test_telas_de_inscricoes_e_recursos.py` (`test_o_recurso_continua_condicionando_os_caminhos`); `authorization/test_julgamento_de_recurso.py` (`test_o_impedimento_e_nomeado_na_tela_antes_de_qualquer_botao`) e `interface/test_polish_da_055.py`, sem mudança |
| FR-1921 | Inventário refeito com `BARRA=expandida` e `BARRA=recolhida`, comparado por `comparar.py`, por `medidas.py` e pixel a pixel |
| FR-1922 | `interface/test_acessibilidade.py`, `interface/test_larguras.py`, `interface/test_estaticos.py`, `interface/test_polish_da_055.py`, `test_vocabulario_da_composicao.py`, `test_vocabulario_do_resultado.py` |
| SC-750 | Inventário: estouram a 375 e a 1280 px, zero; nenhum `status` diferente |
| SC-751 | Inventário: fora das cinco variantes do escopo, nenhuma muda de largura ou altura |
| SC-752 | `interface/test_telas_de_inscricoes_e_recursos.py` (uma trilha por página, no cabeçalho, cada nível como link) |
| SC-753 | `interface/test_telas_de_inscricoes_e_recursos.py` (o Processo na trilha das quatro telas); a contagem de antes no R-001 da pesquisa |
| SC-754 | `interface/test_telas_de_inscricoes_e_recursos.py` (`sem_consulta_ao_processo`); a medida 15, 6, 5 e 8 antes e depois no R-002 da pesquisa |
| SC-755 | `make test-pg` |
| SC-756 | Navegador pelo teclado, a 1280 e a 375 px |
