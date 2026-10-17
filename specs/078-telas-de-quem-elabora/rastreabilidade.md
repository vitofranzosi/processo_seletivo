# Rastreabilidade — 078

Caminhos de teste relativos a `backend/tests/`. "Navegador" é o percurso do [quickstart](quickstart.md);
"inventário" é a comparação com a linha de base `depois-da-077`, em
[`depois-da-078/`](../../doc/inventario-visual-da-gestao-2026-10-16/depois-da-078/), e a das capturas,
pixel a pixel, com as de antes tiradas no mesmo dia.

| Requisito | Onde é provado |
|---|---|
| FR-1760 | `interface/test_telas_de_quem_elabora.py` (`test_toda_moldura_que_rola_e_referencia_do_que_carrega`, que varre os templates e reprova moldura que role sem posição); `interface/test_polish_da_058.py` e `interface/test_acessibilidade.py` (`test_o_cabecalho_da_matriz_nao_e_fixado_dentro_de_um_contentor_de_rolagem`), sem mudança; inventário — as conclusões preservadas com `scrollWidth` de 375 sem a regra da tela |
| FR-1761 | `interface/test_telas_de_quem_elabora.py` (`test_todo_grupo_de_campos_pode_encolher`); inventário — reaproveitar e os anexos da composição com `scrollWidth` de 375 sem a regra da tela |
| FR-1762 | `interface/test_telas_de_quem_elabora.py` (`test_as_regras_pontuais_da_077_sairam_das_telas`); `interface/test_telas_de_uso_diario.py` (`test_cada_correcao_vale_so_na_sua_tela`, com a do sorteio, e `test_a_tabela_da_retificacao_rola_na_propria_moldura`); inventário |
| FR-1763 | Inventário — fora das telas desta feature, nenhuma variante muda de largura nem de altura, nos dois estados da barra; a sonda do R-001 — nenhuma caixa se move |
| FR-1764 | `interface/test_telas_de_quem_elabora.py` (`test_no_processo_o_que_fazer_vem_antes_dos_editais_e_do_pulso`, `test_no_processo_publicado_o_pulso_vem_depois_e_os_atos_nao_mudam`); `interface/test_polish_da_058.py`, `interface/test_processo.py`, `interface/test_supervisao.py`, sem mudança |
| FR-1765 | `interface/test_telas_de_quem_elabora.py` (`test_no_edital_o_que_fazer_vem_antes_de_quem_atuou`, papel a papel); `interface/test_polish_da_057.py`, `interface/test_conducao_dos_bloqueios.py`, sem mudança |
| FR-1766 | `interface/test_telas_de_quem_elabora.py` (a ordem no HTML é a ordem empilhada); navegador a 375 px |
| FR-1767 | `interface/test_telas_de_quem_elabora.py` (`test_no_processo_a_trilha_sobe_ao_cabecalho`, `test_no_edital_a_trilha_sobe_ao_cabecalho`, `test_em_toda_etapa_da_composicao_a_trilha_passa_pelo_processo`, nas nove etapas) |
| FR-1768 | `interface/test_telas_de_quem_elabora.py` (`trilha_unica_no_cabecalho` e o conteúdo que começa pelo título, nos mesmos testes); `interface/test_compor.py` (`test_estrutura_acessivel_da_composicao`) e `interface/test_acessibilidade_da_012.py`, sem mudança |
| FR-1769 | `interface/test_telas_de_uso_diario.py` (`test_fora_das_telas_de_uso_diario_o_cabecalho_e_o_da_076`); `interface/test_shell_da_gestao.py` (`test_abaixo_da_secao_o_caminho_a_nomeia_e_nao_repete_a_trilha`, agora nas inscrições recebidas) |
| FR-1770 | Inventário — as telas de quem elabora a 375 px sem estouro; navegador a 375 px |
| FR-1771 | `interface/test_telas_de_quem_elabora.py` (`test_os_editais_do_processo_sao_a_tabela_da_lista`) |
| FR-1772 | `interface/test_telas_de_quem_elabora.py` (`test_processo_sem_edital_mostra_o_estado_vazio`, com e sem quem cria Edital) |
| FR-1773 | `interface/test_telas_de_quem_elabora.py` (`test_os_editais_do_processo_sao_a_tabela_da_lista`, a tabela na moldura); inventário — o detalhe do Processo a 375 px sem estouro |
| FR-1774 | Inventário refeito com `BARRA=expandida` e `BARRA=recolhida`, comparado por `comparar.py` e campo a campo |
| FR-1775 | `interface/test_acessibilidade.py`, `interface/test_larguras.py`, `interface/test_estaticos.py`, `test_vocabulario_da_composicao.py`; `performance/test_escala_da_mesa.py` (`test_a_tela_de_distribuicao_nao_cresce_com_o_trabalho_ja_feito`) |
| FR-1776 | `interface/test_telas_de_quem_elabora.py` (`test_sem_secao_do_processo_a_faixa_nao_vem`) |
| SC-680 | `interface/test_telas_de_quem_elabora.py` (`test_as_regras_pontuais_da_077_sairam_das_telas`); inventário — as três telas com `scrollWidth` de 375 |
| SC-681 | Inventário: estouram a 375 e a 1280 px, zero; nenhum `status` diferente |
| SC-682 | Inventário: só as 14 variantes desta feature mudam de largura ou altura |
| SC-683 | `interface/test_telas_de_quem_elabora.py` (a ordem das regiões); inventário — no PS-DEMO-2026 a 1280 px, o cartão sai de y ≈ 1700 para y ≈ 345 |
| SC-684 | `interface/test_telas_de_quem_elabora.py` (uma trilha por página, no cabeçalho, cada nível como link) |
| SC-685 | `make test-pg` |
| SC-686 | Navegador só pelo teclado, a 1280 e a 375 px |
