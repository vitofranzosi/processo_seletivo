# Rastreabilidade — 077

Caminhos de teste relativos a `backend/tests/`. "Navegador" é o percurso do [quickstart](quickstart.md);
"inventário" é a comparação com a linha de base do shell, em
[`depois-da-077/`](../../doc/inventario-visual-da-gestao-2026-10-16/depois-da-077/).

| Requisito | Onde é provado |
|---|---|
| FR-1740 | `interface/test_telas_de_uso_diario.py` (`test_a_faixa_da_lista_tem_so_novo_processo`); `interface/test_shell_da_gestao.py` (`test_a_lista_deixou_as_secoes_para_a_barra`, papel a papel) |
| FR-1741 | `interface/test_telas_de_uso_diario.py` (`test_a_faixa_da_lista_tem_so_novo_processo`, `test_sem_acao_a_lista_nao_tem_faixa`) |
| FR-1742 | `interface/test_shell_da_gestao.py` (`test_os_itens_sao_exatamente_os_destinos_que_abrem`, sem mudança); `interface/test_tela_de_autoridades.py`; `authorization/test_visao_institucional.py` |
| FR-1743 | `interface/test_telas_de_uso_diario.py` (`test_cada_correcao_vale_so_na_sua_tela`, `test_a_tabela_da_retificacao_rola_na_propria_moldura`); inventário — as cinco telas com `scrollWidth` de 375 |
| FR-1744 | `interface/test_telas_de_uso_diario.py` (`test_a_tabela_da_retificacao_rola_na_propria_moldura`); inventário — o mesmo `h1` e o mesmo título nas cinco telas; navegador a 375 px |
| FR-1745 | `interface/test_telas_de_uso_diario.py` (`test_cada_correcao_vale_so_na_sua_tela`, a regra fora da folha comum); inventário — nenhuma outra variante muda de largura |
| FR-1746 | `interface/test_telas_de_uso_diario.py` (`test_na_raiz_da_secao_a_trilha_tem_um_nivel`, `test_na_etapa_a_trilha_sobe_ao_cabecalho`, `test_na_inscricao_da_mesa_a_trilha_sobe_ao_cabecalho`) |
| FR-1747 | `interface/test_telas_de_uso_diario.py` (`trilha_unica_no_cabecalho` em cada um dos testes acima; `test_pela_gestao_a_trilha_continua_pela_alocacao`); `interface/test_acessibilidade_da_012.py` (`test_as_telas_tem_titulo_e_trilha_de_navegacao`, sem mudança) |
| FR-1748 | `interface/test_telas_de_uso_diario.py` (`test_fora_das_telas_de_uso_diario_o_cabecalho_e_o_da_076`); `interface/test_shell_da_gestao.py` (`test_abaixo_da_secao_o_caminho_a_nomeia_e_nao_repete_a_trilha`, sem mudança) |
| FR-1749 | inventário — as quatro telas de uso diário a 375 px sem estouro; navegador a 375 px |
| FR-1750 | inventário refeito com `BARRA=expandida` e `BARRA=recolhida`, comparado por `comparar.py` |
| FR-1751 | `interface/test_acessibilidade.py`, `interface/test_larguras.py`, `interface/test_estaticos.py`, `test_vocabulario_da_composicao.py`; `performance/test_escala_da_mesa.py` (`test_a_tela_de_distribuicao_nao_cresce_com_o_trabalho_ja_feito`) |
| SC-670 | `interface/test_telas_de_uso_diario.py` (`test_a_faixa_da_lista_tem_so_novo_processo`, `test_sem_acao_a_lista_nao_tem_faixa`) |
| SC-671 | Inventário: estouram a 375 px, de 5 para 0; a 1280 px, 0 |
| SC-672 | Inventário: `comparar.py` contra `com-o-shell/` e `com-o-shell/recolhida/`, sem problema |
| SC-673 | `interface/test_telas_de_uso_diario.py` (uma trilha por página, no cabeçalho, e cada nível como link) |
| SC-674 | `make test-pg` |
| SC-675 | Navegador só pelo teclado, a 1280 e a 375 px |
