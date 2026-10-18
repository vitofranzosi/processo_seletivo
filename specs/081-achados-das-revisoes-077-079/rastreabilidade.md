# Rastreabilidade — 081

Caminhos de teste relativos a `backend/tests/`. "Navegador" é o percurso do [quickstart](quickstart.md);
"inventário" é a comparação com a linha de base de antes, em
[`depois-da-081/antes/`](../../doc/inventario-visual-da-gestao-2026-10-16/depois-da-081/antes/), pelo
`comparar.py` e pelo `medidas.py`.

| Requisito | Onde é provado |
|---|---|
| FR-1820 | `interface/test_achados_das_revisoes.py` (`test_consolidar_as_selecionadas_tem_o_desenho_dos_atos_irreversiveis`, `test_a_marca_nao_estica_em_linha_flexivel`); navegador a 1280 e a 375 px |
| FR-1821 | `interface/test_achados_das_revisoes.py` (`test_consolidar_as_selecionadas_continua_onde_e_como_estava`); `interface/test_distribuicao.py` e `interface/test_telas_da_presidencia.py` (`test_nenhuma_acao_da_distribuicao_sai_do_lugar`), sem mudança de ordem |
| FR-1822 | `interface/test_achados_das_revisoes.py` (`test_a_alocacao_sem_presidencia_diz_alocar`); `interface/test_alocacoes.py` (`test_comissao_sem_presidente_nao_deixa_distribuir`); `interface/test_telas_da_presidencia.py` (`test_sem_presidencia_a_alocacao_continua_sem_botao`) |
| FR-1823 | `interface/test_achados_das_revisoes.py` (`test_nenhum_modulo_importa_o_cenario_da_presidencia`); os testes da `012`, da `077`, da `079` e da `080`, que passam com a fixture declarada em cada módulo |
| FR-1827 | `interface/test_achados_das_revisoes.py` (`test_a_marca_descreve_o_botao_para_quem_nao_a_ve`, `test_consolidar_as_prontas_tem_o_mesmo_desenho`) |
| FR-1828 | `interface/test_achados_das_revisoes.py` (`test_consolidar_as_prontas_tem_o_mesmo_desenho`); `interface/test_telas_da_presidencia.py` (`test_nenhuma_acao_da_distribuicao_sai_do_lugar`, quatro cheios); `interface/test_consolidar_todas_as_prontas.py`, sem mudança |
| FR-1824 | `interface/test_achados_das_revisoes.py` (`test_toda_trilha_do_cabecalho_abre_com_a_mesma_navegacao`) |
| FR-1825 | Inventário refeito com `BARRA=expandida` e `BARRA=recolhida`, comparado por `comparar.py` e por `medidas.py` |
| FR-1826 | `interface/test_acessibilidade.py`, `interface/test_larguras.py`, `interface/test_estaticos.py`, `interface/test_polish_da_055.py`, `performance/test_escala_da_mesa.py` |
| SC-710 | A tabela de decisões da [spec](spec.md): dez achados, dez destinos |
| SC-711 | `interface/test_achados_das_revisoes.py` (`test_consolidar_as_selecionadas_tem_o_desenho_dos_atos_irreversiveis`, `test_consolidar_as_prontas_tem_o_mesmo_desenho`, `test_a_marca_descreve_o_botao_para_quem_nao_a_ve`) |
| SC-712 | `interface/test_achados_das_revisoes.py` (`test_a_alocacao_sem_presidencia_diz_alocar`) |
| SC-713 | `interface/test_achados_das_revisoes.py` (`test_nenhum_modulo_importa_o_cenario_da_presidencia`) |
| SC-714 | Inventário: estouram a 375 e a 1280 px, zero; nenhum `status` diferente; só a Distribuição muda de medida |
| SC-715 | `make test-pg` |
