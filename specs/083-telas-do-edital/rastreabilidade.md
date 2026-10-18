# Rastreabilidade — 083

Caminhos de teste relativos a `backend/tests/`. "Navegador" é o percurso do [quickstart](quickstart.md);
"inventário" é a comparação com a linha de base de antes, em
[`depois-da-083/antes/`](../../doc/inventario-visual-da-gestao-2026-10-16/depois-da-083/antes/), pelo
`comparar.py`, pelo `medidas.py` e pixel a pixel.

| Requisito | Onde é provado |
|---|---|
| FR-1850 | `interface/test_telas_do_edital.py` (`test_em_novo_edital_a_trilha_termina_no_processo`, `test_na_previa_a_trilha_passa_pelo_processo`, `test_em_partir_de_um_anterior_a_trilha_passa_pela_composicao`, `test_na_conferencia_da_troca_a_trilha_e_a_de_partir_de_um_anterior`, `test_na_retificacao_a_trilha_passa_pelo_processo_e_o_que_fazer_vem_primeiro`, `test_na_auditoria_do_edital_a_trilha_sobe_ao_cabecalho`, `test_no_marco_a_trilha_passa_pelo_processo_e_a_conferencia_pelo_marco`, `test_na_publicacao_o_nivel_da_classificacao_nomeia_e_so_abre_para_quem_alcanca`) |
| FR-1851 | `interface/test_telas_do_edital.py` (os níveis em ordem e o rótulo da tela no fim, nos mesmos testes; Compor na conferência da troca) |
| FR-1852 | `interface/test_telas_do_edital.py` (`trilha_unica_no_cabecalho` e o conteúdo que começa pelo título, nos mesmos testes); `interface/test_telas_de_quem_elabora.py` (`test_o_produto_da_trilha_tem_uma_fonte_so`) e `interface/test_acessibilidade_da_012.py`, sem mudança |
| FR-1853 | `interface/test_telas_de_uso_diario.py` (`test_fora_das_telas_de_uso_diario_o_cabecalho_e_o_da_076`, agora na Supervisão) |
| FR-1854 | `interface/test_telas_do_edital.py` (`test_na_publicacao_o_nivel_da_classificacao_nomeia_e_so_abre_para_quem_alcanca`: texto para quem só publica, link para quem preside e publica) |
| FR-1855 | Inventário — as telas do escopo a 375 px sem estouro, nos dois estados da barra; navegador a 375 px |
| FR-1856 | `interface/test_telas_do_edital.py` (`test_em_retificar_a_recusa_vem_antes_de_como_funciona`, `test_na_previa_de_publicacao_a_recusa_vem_antes_da_frase_da_previa`); a Condução do marco sem mudança de ordem (D-007), pelo inventário |
| FR-1857 | `interface/test_telas_do_edital.py` (`test_na_retificacao_a_trilha_passa_pelo_processo_e_o_que_fazer_vem_primeiro`) |
| FR-1858 | `interface/test_telas_do_edital.py` (`test_em_partir_de_um_anterior_filtrar_e_a_acao_do_filtro`) |
| FR-1859 | `interface/test_telas_do_edital.py` ("Confirmar" e "Cancelar e voltar" na conferência do ato, "Substituir o conteúdo", a conferência do gesto, "Publicar este resultado"); `interface/test_retificar.py`, `interface/test_reaproveitar.py`, `interface/test_conducao_do_marco.py` e `interface/test_publicar_resultado.py`, sem mudança |
| FR-1860 | Inventário refeito com `BARRA=expandida` e `BARRA=recolhida`, comparado por `comparar.py`, por `medidas.py` e pixel a pixel |
| FR-1861 | `interface/test_acessibilidade.py`, `interface/test_larguras.py`, `interface/test_estaticos.py`, `interface/test_polish_da_055.py`, `test_vocabulario_da_composicao.py` |
| SC-730 | Inventário: estouram a 375 e a 1280 px, zero; nenhum `status` diferente |
| SC-731 | Inventário: fora das telas do escopo, nenhuma variante muda de largura ou altura |
| SC-732 | `interface/test_telas_do_edital.py` (uma trilha por página, no cabeçalho, cada nível alcançável como link) |
| SC-733 | `interface/test_telas_do_edital.py` (o Processo e Processos Seletivos na trilha das doze); a contagem de antes na pesquisa (R-001) |
| SC-734 | `make test-pg` |
| SC-735 | Navegador pelo teclado, a 1280 e a 375 px |
