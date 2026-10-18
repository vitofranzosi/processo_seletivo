# Rastreabilidade — 093

Caminhos de teste relativos a `backend/tests/`; "o arquivo" é `interface/test_falha_de_csrf.py`, e
"navegador" é a prova do R-005. Confirmados na implementação.

| Requisito | Onde é provado |
|---|---|
| FR-2150 | O arquivo (`test_a_recusa_vem_na_moldura_da_area[gestao]`: `interface/recusa.html` sobre `interface/base.html`); navegador |
| FR-2151 | O arquivo (`test_a_recusa_vem_na_moldura_da_area[portal]`; `test_fora_das_duas_areas_a_moldura_e_a_do_portal`); navegador |
| FR-2152 | O arquivo (todos os casos conferem 403); `interface/test_csrf.py` |
| FR-2153 | O arquivo (`test_a_mensagem_diz_o_que_aconteceu_e_o_que_fazer`, nas duas áreas) |
| FR-2154 | O arquivo (`test_o_motivo_vai_ao_registro_e_nao_a_pagina`: nenhum dos quatro termos no texto visível; `test_fora_das_duas_areas_a_moldura_e_a_do_portal`) |
| FR-2155 | O arquivo (`test_o_motivo_vai_ao_registro_e_nao_a_pagina`: uma linha, com o motivo e o caminho); R-003; navegador (o terminal) |
| FR-2156 | O arquivo (`test_reabre_a_pagina_de_origem_quando_e_do_sistema`; `test_nunca_oferece_link_para_fora`, com outro site, sem origem e `javascript:`) |
| FR-2157 | O arquivo (`test_sem_estilo_nem_script_embutido_e_sob_a_politica`); `interface/test_politica_de_conteudo.py` (nenhum modelo com estilo embutido); navegador (zero violações) |
| FR-2158 | `interface/test_csrf.py`, sem mudança (inclusive a API isenta); o arquivo (`test_o_ajuste_do_framework_aponta_para_a_view_do_sistema`); `make check` |
| FR-2159 | Diff do PR (`shared/politica_de_conteudo.py` intocado); o arquivo (o cabeçalho é a `POLITICA`, e nenhum `-Report-Only`) |
| FR-2160 | O arquivo (`test_a_mesma_pagina_com_a_depuracao_ligada`); diff do PR (nenhuma dependência, permissão ou migration) |
| SC-827 | Navegador (R-005) |
| SC-828 | O arquivo (`test_o_motivo_vai_ao_registro_e_nao_a_pagina`) |
| SC-829 | `make test-pg`; diff do PR (`interface/test_csrf.py` intocado) |
