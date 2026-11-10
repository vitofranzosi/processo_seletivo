# Rastreabilidade: O sorteio de cada vaga no cartão dela (145)

Caminhos relativos a `backend/tests/`. Abreviações:

- `pg` = `portal/test_sorteio_na_pagina_do_edital.py`
- `un` = `unit/portal/test_sorteios_por_vaga.py`
- `gr` = `interface/test_polish_da_055.py`

| Requisito | Tarefa | Teste |
|---|---|---|
| FR-5150 | T001, T004 | `un::test_a_vaga_sem_relacao_nao_ganha_nada`, `pg::test_a_relacao_da_vaga_esta_no_cartao_dela_e_so_nele` |
| FR-5151 | T001, T004 | `un::test_os_marcos_vem_na_ordem_do_edital_e_so_entao_sao_nomeados` |
| FR-5152 | T001 | `un::test_a_ampla_vem_primeiro_e_as_listas_na_ordem_que_o_perfil_declara`, `pg::test_tres_listas_abrem_sob_um_controle_com_a_ampla_primeiro` |
| FR-5153 | T001 | `pg::test_a_lista_sem_modalidade_e_dita_ampla_concorrencia`, `un::test_a_lista_que_o_vigente_nao_nomeia_e_lida_da_versao_que_a_relacao_citou` |
| FR-5154 | T001, T004 | `un::test_o_estado_e_dito_uma_vez_so_quando_as_listas_estao_no_mesmo_ponto`, `un::test_listas_fechadas_em_instantes_diferentes_nao_ganham_uma_data_so`, `pg::test_sorteada_uma_lista_de_tres_o_cartao_e_o_resumo_dizem_o_andamento` |
| FR-5155 | T004 | `pg::test_a_relacao_da_vaga_esta_no_cartao_dela_e_so_nele`, `pg::test_realizado_o_sorteio_a_pagina_muda_de_frase_e_abre_a_verificacao` |
| FR-5156 | T004 | `pg::test_sorteada_uma_lista_de_tres_o_cartao_e_o_resumo_dizem_o_andamento` |
| FR-5157 | T004 | `pg::test_a_relacao_da_vaga_esta_no_cartao_dela_e_so_nele`, `pg::test_tres_listas_abrem_sob_um_controle_com_a_ampla_primeiro` |
| FR-5158 | T003 | `pg::test_o_resumo_do_edital_vem_antes_das_vagas_e_nao_nomeia_vaga`, `pg::test_sem_relacao_publicada_a_pagina_nao_inventa_bloco_de_sorteio` |
| FR-5159 | T003, T005 | `pg::test_o_resumo_do_edital_vem_antes_das_vagas_e_nao_nomeia_vaga`, `gr::test_a_selecao_sem_sorteio_nao_reserva_a_area_dele` |
| FR-5160 | T001, T003 | `un::test_a_relacao_de_vaga_que_o_vigente_nao_lista_fica_no_resumo` |
| FR-5161 | T001 | `pg::test_o_cartao_com_tres_listas_custa_as_mesmas_duas_consultas` |
| FR-5162 | T001 a T005 | `pg::test_a_tabela_de_participantes_nao_vem_para_esta_pagina`, `pg::test_a_relacao_sucedida_nao_e_anunciada_como_atual` |
| UX-400 | T005 | verificação no preview, a 375 |
| UX-401 | T004 | leitura da árvore de acessibilidade no preview |
| UX-402 | T004 | o console do preview, sem violação da política de conteúdo |
| SC-1600 | T008 | medida no preview, a 375 |
| SC-1601 | T007 | `pg::test_tres_listas_abrem_sob_um_controle_com_a_ampla_primeiro` |
| SC-1602 | T007 | `pg::test_o_cartao_com_tres_listas_custa_as_mesmas_duas_consultas` |
| SC-1603 | T007 | os seis primeiros casos de `pg`, sem mudança de expectativa |
