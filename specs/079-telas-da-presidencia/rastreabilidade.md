# Rastreabilidade — 079

Caminhos de teste relativos a `backend/tests/`. "Navegador" é o percurso do [quickstart](quickstart.md);
"inventário" é a comparação com a linha de base `depois-da-078`, em
[`depois-da-079/`](../../doc/inventario-visual-da-gestao-2026-10-16/depois-da-079/), pelo `comparar.py`
e, campo a campo, pelo `medidas.py`.

| Requisito | Onde é provado |
|---|---|
| FR-1780 | `interface/test_telas_da_presidencia.py` (`test_na_comissao_a_trilha_sobe_ao_cabecalho`, `test_na_conferencia_a_trilha_passa_pela_comissao`, `test_na_alocacao_a_trilha_sobe_e_a_barra_continua_no_topo`, `test_na_distribuicao_a_trilha_continua_pela_alocacao`) |
| FR-1781 | `interface/test_telas_da_presidencia.py` (`trilha_unica_no_cabecalho` e o conteúdo que começa pelo título, nos mesmos testes); `interface/test_telas_de_quem_elabora.py` (`test_o_produto_da_trilha_tem_uma_fonte_so`) e `interface/test_acessibilidade_da_012.py`, sem mudança |
| FR-1782 | `interface/test_telas_de_uso_diario.py` (`test_fora_das_telas_de_uso_diario_o_cabecalho_e_o_da_076`, que a `080` passou da Trilha da avaliação à Auditoria do Edital); `interface/test_telas_filhas_da_distribuicao.py` (`test_a_auditoria_do_edital_continua_com_o_cabecalho_da_076`). Emendada pela `080`: as filhas da Distribuição e a Auditoria da comissão têm a trilha no cabeçalho (`FR-1800` da `080`), e o guardião da `079` que as fixava, `test_as_filhas_da_distribuicao_continuam_com_o_cabecalho_da_076`, saiu |
| FR-1783 | Inventário — as quatro telas a 375 px sem estouro; navegador a 375 px |
| FR-1784 | `interface/test_telas_da_presidencia.py` (`test_na_alocacao_a_trilha_sobe_e_a_barra_continua_no_topo`); `interface/test_shell_da_gestao.py` (`test_na_alocacao_a_barra_fica_no_topo`) e `interface/test_polish_da_057.py`, sem mudança; inventário — a Alocação a 1280 px sem estouro, nos dois estados da barra; navegador |
| FR-1785 | `interface/test_telas_da_presidencia.py` (`test_os_lugares_da_etapa_vem_logo_abaixo_do_titulo`, `test_as_mensagens_do_ultimo_envio_vem_antes_da_faixa`) |
| FR-1786 | `interface/test_telas_da_presidencia.py` (`test_nenhuma_acao_da_distribuicao_sai_do_lugar`); `interface/test_distribuicao.py`, `interface/test_consolidar_todas_as_prontas.py` e `interface/test_avisos_antes_da_tentativa.py`, sem mudança |
| FR-1787 | `interface/test_telas_da_presidencia.py` (`test_os_membros_tem_titulo_com_a_comissao_inteira`); `interface/test_jornada_da_presidente.py` (os filtros da comissão), sem mudança |
| FR-1788 | `interface/test_telas_da_presidencia.py` (`test_comissao_vazia_nao_tem_filtro_e_leva_a_inclusao`, `test_recorte_vazio_mantem_o_filtro`) |
| FR-1789 | `interface/test_telas_da_presidencia.py` (`test_na_conferencia_a_trilha_passa_pela_comissao`, de um e da lista); `interface/test_comissao.py`, sem mudança |
| FR-1790 | `interface/test_telas_da_presidencia.py` (`test_a_alocacao_salva_alocacao`, `test_sem_presidencia_a_alocacao_continua_sem_botao`); `interface/test_alocacoes.py` (`test_comissao_sem_presidente_nao_deixa_distribuir`, com o rótulo novo) |
| FR-1791 | Inventário refeito com `BARRA=expandida` e `BARRA=recolhida`, comparado por `comparar.py` e por `medidas.py` |
| FR-1792 | `interface/test_acessibilidade.py`, `interface/test_larguras.py`, `interface/test_estaticos.py`, `interface/test_polish_da_055.py` (`test_a_acao_principal_nao_tem_o_desenho_de_acao_de_linha`), `test_vocabulario_da_composicao.py`; `performance/test_escala_da_mesa.py` (`test_a_tela_de_distribuicao_nao_cresce_com_o_trabalho_ja_feito`) |
| SC-690 | Inventário: estouram a 375 e a 1280 px, zero; nenhum `status` diferente |
| SC-691 | Inventário: fora de `comissao`, `alocacoes` e `distribuicao`, nenhuma variante muda de largura ou altura |
| SC-692 | `interface/test_telas_da_presidencia.py` (uma trilha por página, no cabeçalho, cada nível como link) |
| SC-693 | Inventário — a faixa medida no navegador antes e depois, a 1280 e a 375 px |
| SC-694 | `performance/test_escala_da_mesa.py`; a medida antes e depois na tarefa T013 |
| SC-695 | `make test-pg` |
| SC-696 | Navegador só pelo teclado, a 1280 e a 375 px |
