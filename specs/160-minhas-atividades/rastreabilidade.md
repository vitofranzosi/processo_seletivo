# Rastreabilidade: Minhas atividades (160)

Os caminhos são relativos a `backend/tests/`. Abreviações:

- `uni` = `unit/interface/test_atividades.py` (as funções puras, sem banco)
- `tela` = `interface/test_minhas_atividades.py` (as jornadas pela página)
- `coe` = `interface/test_minhas_atividades_coerencia.py` (a página contra o Centro)
- `esc` = `performance/test_minhas_atividades_em_escala.py` (o custo)
- `lista` = `interface/test_organizacao_da_lista.py` (a nota da faixa)
- `ver` = [verificacao.md](verificacao.md) (o que se conferiu fora da suíte)

A faixa abre em **FR-6851**, **SC-2271** e **UX-711**, e gasta até FR-6884, SC-2281 e UX-715.

| Requisito | Tarefa | Teste |
|---|---|---|
| FR-6851 | T024 | `tela::test_o_nome_visivel_e_minhas_atividades_e_o_endereco_fica`; os 11 arquivos de T025 |
| FR-6852 | T023, T024 | `tela::test_o_nome_visivel_e_minhas_atividades_e_o_endereco_fica` |
| FR-6853 | T026 | `ver` (guia da equipe e manual) |
| FR-6854 | T006 | `tela::test_o_gestor_que_preside_ve_os_atos_do_processo_dele`, `coe::test_o_gestor_que_nao_preside_nao_tem_linha_de_conducao` |
| FR-6855 | T006, T008 | `tela::test_processo_encerrado_nao_e_lido` |
| FR-6856 | T006, T015 | `tela::test_o_avaliador_ve_avaliar_com_a_alocacao_e_o_link_da_mesa`, `esc::test_o_membro_paga_o_mesmo_com_uma_e_com_onze_comissoes` |
| FR-6857 | T019, T020 | `tela::test_o_gestor_alocado_a_um_perfil_ve_so_a_conferencia_dele`, `tela::test_o_membro_alocado_a_outro_perfil_nao_ve_a_conferencia`, `uni::test_a_conferencia_por_alocacao_fica_so_com_o_perfil_alocado` |
| FR-6858 | T018 | `tela::test_o_gestor_sem_presidencia_nao_ve_conducao_e_a_derivacao_nao_roda` |
| FR-6859 | T005, T007 | `coe::*` |
| FR-6860 | T007 | `coe::*` (o segundo sentido) |
| FR-6861 | T008, T011 | `tela::test_a_presidencia_ve_os_atos_dela_com_a_base_e_o_link` |
| FR-6862 | T003, T008 | `tela::test_a_presidente_que_publica_nao_ve_publicar_o_resultado`, `uni::test_a_presidencia_fica_com_a_conducao_e_a_conferencia_e_nada_mais` |
| FR-6863 | T003, T008 | `uni::test_a_presidencia_fica_com_a_conducao_e_a_conferencia_e_nada_mais`, `tela::test_a_espera_fica_recolhida_com_a_origem_da_data_e_sem_atraso` |
| FR-6864 | T004, T014, T016 | `uni::test_a_avaliacao_sai_da_carga_com_a_frase_do_andamento_e_o_numero_da_mesa`, `tela::test_o_avaliador_ve_avaliar_com_a_alocacao_e_o_link_da_mesa`, `coe::test_p1_a_presidencia_e_o_avaliador` |
| FR-6865 | T003, T009 | `uni::test_o_mesmo_ato_sem_numero_junta_entre_editais`, `uni::test_o_ato_com_numero_nunca_junta_nem_com_o_mesmo_numero`, `uni::test_a_lista_vazia_nao_junta_com_a_lista_com_inscritos` |
| FR-6866 | T003 | `uni::test_o_obsoleto_vem_primeiro_depois_o_edital_mais_antigo_e_a_data_nao_ordena` |
| FR-6867 | T011 | `uni::test_a_avaliacao_sai_da_carga_com_a_frase_do_andamento_e_o_numero_da_mesa` (a fase da avaliação); a fase das demais vem de `centro.fase_da_providencia` |
| FR-6868 | T021, T022 | `uni::test_a_espera_entra_qualquer_que_seja_o_papel_seguinte_menos_a_formalizacao`, `tela::test_a_espera_fica_recolhida_com_a_origem_da_data_e_sem_atraso` |
| FR-6869 | T021 | `tela::test_a_espera_fica_recolhida_com_a_origem_da_data_e_sem_atraso` |
| FR-6870 | T003, T021 | `uni::test_as_esperas_juntam_pela_razao_inteira_com_a_data` |
| FR-6871 | T012 | `tela::test_a_presidencia_ve_os_atos_dela_com_a_base_e_o_link` (a nota na página) |
| FR-6872 | T012, T020 | `tela::test_a_presidente_que_publica_nao_ve_publicar_o_resultado`, `tela::test_o_gestor_sem_presidencia_nao_ve_conducao_e_a_derivacao_nao_roda` |
| FR-6873 | T014 | `tela::test_o_membro_sem_pendencia_le_que_nada_depende_dele_no_que_a_pagina_cobre` |
| FR-6874 | T006, T008 | `tela::test_o_edital_que_nao_pode_ser_lido_e_dito_e_nao_vira_nada_a_fazer` |
| FR-6875 | T012, T017 | `tela::*` (as três seções); `ver` |
| FR-6876 | T017 | os testes do estado vazio de T017; `ver` |
| FR-6877 | T015 | `esc::test_o_membro_paga_o_mesmo_com_uma_e_com_onze_comissoes` |
| FR-6878 | T034 | `esc::test_a_presidencia_paga_um_teto_por_edital_no_sorteio`, `esc::test_a_presidencia_paga_um_teto_por_edital_na_pontuacao`, `esc::test_a_presidencia_paga_um_teto_por_edital_na_convocacao` |
| FR-6879 | T030 a T033 | `unit/publicacoes/test_versao_da_requisicao.py`; `esc::test_a_versao_por_requisicao_nao_muda_o_que_a_derivacao_diz`; `performance/test_andamento_em_escala.py` (o Centro) |
| FR-6880 | T027, T028 | `lista::test_a_nota_diz_onde_esta_cada_familia_e_nao_conta_atividades` |
| FR-6881 | T027, T028 | `lista::test_a_nota_vem_antes_do_primeiro_item_e_nomeia_as_familias`, `lista::test_a_frase_vazia_nomeia_as_mesmas_familias_da_mesma_fonte` |
| FR-6882 | T029 | `performance/test_trabalho_em_escala.py`, `performance/test_lista_em_escala.py`, sem mudar os tetos |
| FR-6883 | T012 | os títulos das seções no modelo; `ver` |
| FR-6884 | T005, T006 | a leitura não grava (`atividades.py` não tem escrita); `coe::*` (o link leva à tela que verifica) |
| SC-2271 | T007, T016 | `coe::*` |
| SC-2272 | T015 | `esc::test_o_membro_paga_o_mesmo_com_uma_e_com_onze_comissoes` |
| SC-2273 | T018 | `tela::test_o_gestor_que_preside_ve_os_atos_do_processo_dele`, `tela::test_o_gestor_sem_presidencia_nao_ve_conducao_e_a_derivacao_nao_roda` |
| SC-2274 | T034 | `esc::test_a_presidencia_paga_um_teto_por_edital_*` |
| SC-2275 | T009, T037 | `uni::test_o_mesmo_ato_sem_numero_junta_entre_editais`; `ver` (cenários de treinamento) |
| SC-2276 | T008 | `tela::test_o_edital_que_nao_pode_ser_lido_e_dito_e_nao_vira_nada_a_fazer` |
| SC-2277 | T021 | `tela::test_a_espera_fica_recolhida_com_a_origem_da_data_e_sem_atraso` |
| SC-2278 | T023 | `tela::test_o_nome_visivel_e_minhas_atividades_e_o_endereco_fica` |
| SC-2279 | T027 | `lista::*` (as três da nota) |
| SC-2280 | T033 | `esc::test_a_versao_por_requisicao_nao_muda_o_que_a_derivacao_diz`, `esc::test_a_presidencia_paga_um_teto_por_edital_*`, `performance/test_andamento_em_escala.py`; `ver` |
| SC-2281 | T037 | humano, pendente |
| UX-711 | T012 | o título "Para fazer agora · N atos em M Editais"; `ver` |
| UX-712 | T022 | `tela::test_a_espera_fica_recolhida_com_a_origem_da_data_e_sem_atraso` |
| UX-713 | T011 | o ato é o link, com o verbo da derivação; `coe::*` |
| UX-714 | T013, T036 | `ver` (375 px, pela sessão que captura as telas) |
| UX-715 | T011 | o sinal e a palavra da situação no parcial; `ver` |
