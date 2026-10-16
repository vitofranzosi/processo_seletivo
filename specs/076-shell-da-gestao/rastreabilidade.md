# Rastreabilidade — 076

Caminhos de teste relativos a `backend/tests/`. "Navegador" é o percurso do [quickstart](quickstart.md);
"inventário" é a comparação com a linha de base de 16/10.

| Requisito | Onde é provado |
|---|---|
| FR-1710 | `interface/test_shell_da_gestao.py` (`test_com_identidade_a_tela_tem_barra_e_cabecalho_de_contexto`); inventário (as 84 variantes carregam com a moldura) |
| FR-1711 | `interface/test_shell_da_gestao.py` (`test_sem_identidade_o_topo_tem_so_a_marca`) |
| FR-1712 | `interface/test_shell_da_gestao.py` (`test_o_salto_continua_o_primeiro_e_pula_a_barra`); `interface/test_acessibilidade.py` (o alvo do salto); navegador só pelo teclado |
| FR-1713 | `interface/test_shell_da_gestao.py` (`test_montar_a_barra_nao_consulta_o_banco`, que confere os dois grupos; `test_os_itens_sao_exatamente_os_destinos_que_abrem`); `interface/test_lista.py` (os botões da lista continuam) |
| FR-1714 | `interface/test_shell_da_gestao.py` (`test_os_itens_sao_exatamente_os_destinos_que_abrem`, `test_grupo_sem_item_nao_aparece`, `test_a_lista_e_a_barra_oferecem_as_mesmas_secoes`); `interface/test_tela_de_autoridades.py`; `authorization/test_visao_institucional.py` |
| FR-1715 | `interface/test_shell_da_gestao.py` (`test_montar_a_barra_nao_consulta_o_banco`, `test_o_portal_nao_recebe_barra`); os orçamentos de consulta que já existiam (`performance/test_comissao_em_escala.py`, `interface/test_instrucao_na_peca.py`) |
| FR-1716 | `interface/test_shell_da_gestao.py` (`test_a_secao_sai_do_endereco`, `test_na_propria_secao_o_item_e_a_pagina_atual`, `test_abaixo_da_secao_o_caminho_leva_a_ela_e_nao_repete_a_trilha`) |
| FR-1717 | `interface/test_shell_da_gestao.py` (`test_com_identidade_a_tela_tem_barra_e_cabecalho_de_contexto`) |
| FR-1718 | `interface/test_shell_da_gestao.py` (`test_na_propria_secao_o_item_e_a_pagina_atual`, `test_abaixo_da_secao_o_caminho_leva_a_ela_e_nao_repete_a_trilha`) |
| FR-1719 | `interface/test_shell_da_gestao.py` (`test_no_celular_a_barra_recolhe_sem_script`); `interface/test_visao_geral.py` (a Visão Geral sem script); navegador a 375 px — Enter abre, Tab entra, Esc fecha |
| FR-1720 | inventário refeito com a moldura e comparado tela a tela ([doc](../../doc/inventario-visual-da-gestao-2026-10-16.md)) |
| FR-1721 | `interface/test_shell_da_gestao.py` (`test_os_itens_sao_exatamente_os_destinos_que_abrem`); a suíte de autorização inteira, sem mudança |
| FR-1722 | `performance/test_escala_da_mesa.py` (`test_a_tela_de_distribuicao_nao_cresce_com_o_trabalho_ja_feito`); `interface/test_acessibilidade.py` (`test_nenhuma_classe_citada_deixa_de_existir_na_folha`) |
| FR-1723 | `interface/test_acessibilidade.py`, `interface/test_larguras.py`, `interface/test_estaticos.py`, `test_vocabulario_da_composicao.py` sobre o `base.html` novo |
| FR-1724 | `interface/test_shell_da_gestao.py` (`test_na_alocacao_a_barra_fica_recolhida`); inventário (a Alocação a 1280 px sem estouro) |
| SC-660 | Navegador: um clique na barra a 1280 px; "Seções" e o item a 375 px |
| SC-661 | `interface/test_shell_da_gestao.py` (`test_os_itens_sao_exatamente_os_destinos_que_abrem`, parametrizado por todo papel e pela identidade só com vínculo) |
| SC-662 | Inventário refeito e comparado com o `resultados.json` da linha de base |
| SC-663 | `make test-pg` |
| SC-664 | Navegador só pelo teclado, a 1280 e a 375 px |
