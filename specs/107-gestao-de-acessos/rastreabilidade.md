# Rastreabilidade: Gestão de acessos pela interface

Cada requisito → a tarefa que o implementa → o teste que o verifica. Caminhos relativos a
`backend/tests/`: `TEL` é `seguranca/test_telas_de_acesso.py`, `PRZ` é
`seguranca/test_sessao_com_prazo.py`, `CON` é `seguranca/test_concorrencia_das_telas.py`, `PRV` é
`seguranca/test_privilegios_das_telas.py`, `NAV` é `navegador/test_jornadas_de_acesso.py`, `PROD` é
`test_configuracao_producao.py`.

## Requisitos

| Requisitos | Tarefas | Testes |
|---|---|---|
| FR-3101 (tela sem acesso, toda porta leva a ela) | T008 | `TEL::test_quem_entra_sem_vinculo_ve_a_tela_sem_acesso_com_o_proprio_nome`, `::test_toda_porta_leva_quem_esta_sem_acesso_a_tela_sem_acesso`, `::test_a_tela_sem_acesso_nao_atende_quem_nao_entrou_nem_quem_tem_acesso`; `NAV::test_us1_quem_entra_sem_acesso_ve_o_proprio_nome_e_a_quem_pedir` |
| FR-3102 (troca a partir da tela sem acesso, sem mais nada) | T008 | `TEL::test_quem_perdeu_a_unidade_ativa_troca_pela_tela_sem_acesso` |
| FR-3103 (o nome, e não o identificador) | T003, T009 | `TEL::test_a_barra_mostra_o_nome_e_nao_o_identificador`, `::test_sem_nome_a_barra_usa_o_email_e_nunca_o_identificador`; `NAV::test_us1_…`, `::test_us3_…` |
| FR-3104 (unidade ativa e seletor na barra) | T003, T009 | `TEL::test_o_seletor_da_barra_troca_a_unidade_sem_levar_permissao`, `::test_com_um_escopo_so_nao_ha_seletor`; `NAV::test_us2_a_troca_de_unidade_pela_barra_muda_as_permissoes`, `::test_us4_…` |
| FR-3105 (demonstração com a barra de sempre) | T009 | `TEL::test_a_demonstracao_ve_a_barra_de_sempre`; a suíte do seletor, sem mudança |
| FR-3106, FR-3107 (quem atua e histórico, só da unidade) | T002, T010, T011 | `TEL::test_a_tela_lista_quem_atua_na_unidade_pelo_nome`, `::test_o_historico_mostra_concessao_e_revogacao_com_motivo`; `NAV::test_us3_…` |
| FR-3108, FR-3109 (papéis operacionais; unidade da sessão) | T010 | `TEL::test_papel_de_acesso_pela_porta_da_unidade_e_recusado`, `::test_a_unidade_do_formulario_e_ignorada` |
| FR-3110, FR-3111 (revogar só do escopo; botão só onde vale) | T010, T013 | `TEL::test_vinculo_de_outra_unidade_e_nao_encontrado`, `::test_o_administrador_da_unidade_nao_revoga_outro_administrador`; `test_gramatica_das_portas.py::test_o_inventario_cobre_toda_funcao_que_responde_inexistente` |
| FR-3112 a FR-3115 (busca: capacidade, piso, teto, universo, sem termo no endereço) | T002, T010 | `TEL::test_a_busca_exige_tres_letras_e_nao_lista_sem_termo`, `::test_a_busca_para_em_dez_e_avisa`, `::test_a_busca_nao_mostra_o_ator_nem_inativo_nem_identificadores`, `::test_a_busca_e_recusada_a_quem_nao_concede` |
| FR-3116, FR-3117 (confirmação antes de gravar; motivo) | T010, T011 | `TEL::test_a_concessao_pela_tela_passa_pela_confirmacao_e_vale_na_requisicao_seguinte`, `::test_sem_motivo_a_confirmacao_volta_e_nada_e_gravado`, `::test_a_revogacao_pela_tela_vale_com_a_sessao_da_pessoa_aberta` |
| FR-3118 (a confirmação reconfere) | T002, T010 | `TEL::test_autoconcessao_montada_a_mao_e_recusada`, `::test_pessoa_desativada_entre_a_busca_e_a_confirmacao_e_recusada`, `::test_a_confirmacao_reenviada_nao_duplica`, `::test_identificador_que_nao_e_de_pessoa_e_recusado` |
| FR-3119 (gravação e trilha na mesma transação, pelas funções da `106`) | T010 | `TEL::test_a_concessao_pela_tela_…`, `::test_a_revogacao_pela_tela_…`; `CON::test_duas_concessoes_do_mesmo_papel_gravam_uma`, `::test_duas_revogacoes_do_mesmo_vinculo_gravam_uma` |
| FR-3120, FR-3121 (administração institucional) | T002, T010 | `TEL::test_o_institucional_concede_o_administrador_de_acessos_de_uma_unidade`, `::test_o_institucional_nao_concede_papel_operacional_nem_a_si`, `::test_o_institucional_revoga_so_administrador_de_acessos`, `::test_o_administrador_da_unidade_nao_abre_a_administracao_institucional`; `NAV::test_us4_…` |
| FR-3122 (duração máxima; a troca não renova) | T005 | `PRZ::test_a_atividade_constante_nao_passa_da_duracao_maxima`, `::test_a_troca_de_unidade_nao_renova_a_duracao`, `::test_sessao_sem_os_instantes_vence` |
| FR-3123 (inatividade; automática e fora da gestão não contam) | T005 | `PRZ::test_a_sessao_vale_ate_o_limite_de_inatividade_e_cai_nele`, `::test_a_requisicao_automatica_nao_conta_como_atividade`, `::test_requisicao_fora_da_gestao_nao_conta_como_atividade` |
| FR-3124 (limites da configuração; produção os exige) | T006 | `PRZ::test_os_limites_vem_da_configuracao`; `PROD::test_com_provedor_producao_exige_os_dois_prazos_da_sessao`, `::test_com_provedor_e_prazos_declarados_producao_sobe`, `::test_sem_provedor_producao_nao_pede_os_prazos` |
| FR-3125 (término com trilha e motivo na página de acesso) | T005, T009 | `PRZ::test_o_termino_por_inatividade_vai_a_trilha_e_a_pagina_de_acesso_diz_por_que`, `::test_a_atividade_constante_…`; `NAV::test_us5_a_sessao_termina_por_inatividade_e_a_pagina_diz_por_que` |
| FR-3126 (demonstração e portal fora do prazo) | T005 | `PRZ::test_a_demonstracao_nao_tem_prazo`, `::test_o_portal_do_candidato_nao_e_alcancado` |
| FR-3127, FR-3128 (só institucional; barra por capacidade) | T010, T012 | `TEL::test_a_demonstracao_nao_alcanca_as_telas_de_acesso`, `::test_a_busca_e_recusada_a_quem_nao_concede`; `interface/test_shell_da_gestao.py` sem mudança |
| FR-3129 (pessoa por identificador reconferido; nenhuma identidade do cliente) | T010 | `TEL::test_identificador_que_nao_e_de_pessoa_e_recusado`, `::test_autoconcessao_montada_a_mao_e_recusada`; `seguranca/test_entrada_institucional.py::test_cabecalho_do_cliente_nao_autentica` (`106`) |
| FR-3130 (CSP) | T011 | `interface/test_politica_de_conteudo.py` e `interface/test_folha_estatica.py`, que leem todo template e toda folha |
| FR-3131 (jornadas por navegador, preparação → ações → verificações) | T016–T018 | `NAV`, os cinco casos |
| FR-3132 (assistir com um comando) | T019 | `make test-navegador`; executado sem janela em 30/10 (ver [verificação](verificacao.md)) |
| FR-3133 (dois roteiros, sem promessa manual) | T020, T021 | [quickstart](quickstart.md); `doc/homologacao-com-o-seletor-de-demonstracao.md` |
| FR-3134 (sem tabela, sem migration, seletor igual; só a recusa de pessoa inativa) | T002 | `make check` (`makemigrations --check`); `migrations/test_migrations.py` e `integration/test_database_permissions.py` sem mudança de contagem; `TEL::test_pessoa_desativada_entre_a_busca_e_a_confirmacao_e_recusada` |

## Requisitos do incremento 2 (especificados, não implementados)

| Requisitos | Tarefas | Testes |
|---|---|---|
| FR-3135 a FR-3142 (suspensão) | T025–T028 | a escrever em T031 e T032 |
| FR-3143 a FR-3146 (reativação) | T025, T027, T028 | a escrever em T031 e T032 |
| FR-3147, FR-3148 (retirar e substituir a administração institucional) | T029 | a escrever em T031 |
| FR-3149 (registros append-only, migration só cria) | T024 | a escrever em T031; os guardiões de contagem |
| FR-3150, FR-3151 (o nome nas demais telas) | T030 | a escrever em T031 |

## Critérios

| Critério | Como se mede |
|---|---|
| SC-1011 (concessão em até quatro telas, sem digitar identificador) | `NAV::test_us3_…`: lista → conceder (busca e escolha na mesma tela) → confirmação → lista com o aviso |
| SC-1012 (revogação vale na requisição seguinte, sessão aberta) | `TEL::test_a_revogacao_pela_tela_vale_com_a_sessao_da_pessoa_aberta`; `NAV::test_us3_…` |
| SC-1013 (zero caminhos de autoconcessão, outra unidade, lista sem termo) | `TEL::test_autoconcessao_montada_a_mao_e_recusada`, `::test_vinculo_de_outra_unidade_e_nao_encontrado`, `::test_a_unidade_do_formulario_e_ignorada`, `::test_a_busca_exige_tres_letras_e_nao_lista_sem_termo` |
| SC-1014 (as cinco histórias no navegador, sem ação fora dele) | `NAV`, os cinco casos |
| SC-1015 (suíte existente sem mudar resultado esperado) | a suíte inteira contra PostgreSQL; os ajustes de teste existentes estão listados na [verificação](verificacao.md) |
| SC-1016 (demonstração sem consulta a mais) | os orçamentos de consulta das telas existentes (`tests/performance/`), sem mudança; `seguranca/test_entrada_institucional.py::test_o_ator_custa_no_maximo_duas_consultas_por_requisicao` (`106`) para o institucional |
| SC-1017 a SC-1020 (incremento 2) | a medir quando o incremento 2 for implementado (T031, T032) |
