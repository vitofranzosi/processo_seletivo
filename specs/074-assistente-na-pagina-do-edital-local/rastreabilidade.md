# Rastreabilidade — 074

Caminhos de teste relativos a `backend/tests/`. "Navegador" é o percurso do [quickstart](quickstart.md).

| Requisito | Onde é provado |
|---|---|
| FR-1680 | `interface/test_assistente.py` (`test_nenhuma_rota_publica_leva_ao_piloto`, as três rotas nomeadas e 404 sem a chave); `portal/test_assistente_na_pagina.py` (`test_desligada_a_pagina_nao_traz_o_painel_e_as_rotas_nao_existem`, `test_ligada_o_candidato_abre_o_painel_sem_identidade_da_gestao`); navegador |
| FR-1681 | `portal/test_assistente_na_pagina.py` (sugestão pela `070`, pergunta livre pela `perguntar`, escolha da opção, simulação só no protótipo); `interface/test_prototipo_do_assistente.py`, sem alteração |
| FR-1682 | `portal/test_assistente_na_pagina.py` (`test_a_conversa_e_da_sessao_e_do_edital`, `test_a_conversa_do_prototipo_nao_aparece_na_pagina`, `test_mostrar_a_pagina_nao_grava_conversa_na_sessao`, `Cache-Control` privado) |
| FR-1683 | `test_configuracao_producao.py` (`test_configuracao_insegura_impede_a_inicializacao`, caso `ASSISTENTE_NA_PAGINA_DO_EDITAL`) |
| FR-1684 | Registro: *Pendências para a implantação*, na spec |
| FR-1685 | Os envios chamam a `perguntar` e a `responder_sugestao` da `071`, com os limites delas (`interface/test_prototipo_do_assistente.py` e os testes da `071`); `portal/test_assistente_na_pagina.py` (`test_edital_sem_pagina_publica_nao_chega_ao_modelo`, `test_nova_conversa_tem_teto_por_sessao_e_edital`) |
| SC-640 | `portal/test_assistente_na_pagina.py`; navegador (sugestões); a pergunta livre real é a T013 |
| SC-641 | `portal/test_assistente_na_pagina.py`; `test_configuracao_producao.py` |
| SC-642 | `portal/test_assistente_na_pagina.py` |
