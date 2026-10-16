# Rastreabilidade — 075

Caminhos de teste relativos a `backend/tests/`. "Navegador" é o percurso do [quickstart](quickstart.md).

| Requisito | Onde é provado |
|---|---|
| FR-1690 | `interface/test_entrada_da_gestao.py` (`test_a_pagina_de_acesso_apresenta_o_produto_e_a_entrada`); navegador |
| FR-1691 | `interface/test_entrada_da_gestao.py` (`test_sem_metodo_a_pagina_diz_que_a_entrada_nao_esta_configurada`, `test_sem_metodo_a_escolha_nao_existe_e_o_envio_nao_grava`); `interface/test_lista.py` (`test_seletor_de_identidade_nao_existe_com_a_configuracao_desligada`) |
| FR-1692 | `interface/test_entrada_da_gestao.py` (`test_a_escolha_agrupa_e_descreve_sem_codigo_de_permissao`); `interface/test_caminho_ate_a_mesa.py` (`test_a_tela_de_identificacao_oferece_quem_tem_trabalho`, `test_a_lista_nao_promete_papel_que_ela_nao_concede`) |
| FR-1693 | `interface/test_entrada_da_gestao.py` (`test_entrar_pela_comissao_nao_concede_papel`, `test_entrar_por_uma_responsabilidade_concede_so_ela`, `test_o_nome_sugerido_e_o_de_quem_exerceu_o_papel_na_trilha`, `test_sem_ninguem_na_trilha_o_nome_se_denuncia_como_demonstracao`) |
| FR-1694 | `interface/test_entrada_da_gestao.py` (`test_envio_sem_nome_volta_com_a_recusa_junto_do_campo`); `interface/test_caminho_ate_a_mesa.py` (`test_a_identidade_escolhida_tem_prioridade_sobre_o_campo`) |
| FR-1695 | `interface/test_entrada_da_gestao.py` (`test_a_busca_so_aparece_acima_de_oito_entradas`, `test_sem_comissao_a_busca_nao_vem_e_o_grupo_nao_aparece`); `javascript/acesso.test.js`; navegador |
| FR-1696 | `interface/test_entrada_da_gestao.py` (`test_a_porta_manda_ao_acesso_com_o_proprio_endereco`, `test_o_destino_atravessa_a_escolha_e_e_seguido`, `test_destino_fora_da_gestao_ou_em_laco_e_ignorado`, `test_porta_alcancada_por_post_nao_guarda_destino`); `interface/test_lista.py` (`test_lista_exige_identificacao`) |
| FR-1697 | `interface/test_entrada_da_gestao.py` (`test_sair_leva_a_pagina_de_acesso`, `test_identificado_a_pagina_oferece_continuar_ou_trocar`) |
| FR-1698 | `interface/test_entrada_da_gestao.py` (`test_a_sessao_grava_a_origem`, `test_a_demonstracao_nao_sobrevive_ao_seletor_desligado`, `test_sessao_anterior_sem_origem_conta_como_demonstracao`) |
| FR-1699 | `interface/test_entrada_da_gestao.py` (`test_o_portal_oferece_a_gestao_onde_ha_por_onde_entrar`, `test_sem_metodo_o_portal_nao_oferece_a_gestao`); `integration/portal/test_porta_de_entrada.py` |
| FR-1700 | `interface/test_entrada_da_gestao.py` (`test_o_portal_oferece_a_gestao_onde_ha_por_onde_entrar`, `test_a_pagina_de_acesso_apresenta_o_produto_e_a_entrada`); navegador a 375 px |
| FR-1701 | `interface/test_entrada_da_gestao.py` (`test_todo_papel_tem_descricao_e_nenhuma_descricao_sobra`) |
| FR-1702 | `interface/test_entrada_da_gestao.py` (`test_os_prototipos_do_estudo_sairam`) |
| SC-650 | Navegador: raiz → "Área de gestão" → "Acessar ambiente de demonstração" → identidade |
| SC-651 | `interface/test_entrada_da_gestao.py` (`test_a_escolha_agrupa_e_descreve_sem_codigo_de_permissao`) |
| SC-652 | `interface/test_entrada_da_gestao.py` (os testes de `FR-1696`) |
| SC-653 | `interface/test_entrada_da_gestao.py` (os testes de `FR-1691`, `FR-1698` e `FR-1699`) |
| SC-654 | Navegador a 375 px e só pelo teclado; `interface/test_acessibilidade.py` sobre os templates novos |
| SC-655 | `make test-pg` |
