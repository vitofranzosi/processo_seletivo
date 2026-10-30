# Rastreabilidade: Identidade institucional preparada

Cada requisito → a tarefa que o implementa → o teste que o verifica. Caminhos de teste relativos a
`backend/tests/`: `ENT` é `seguranca/test_entrada_institucional.py`, `VIN` é
`seguranca/test_vinculos.py`, `ATI` é `seguranca/test_ativacao.py`, `HOM` é
`seguranca/test_homologacao_preservada.py`, `PROD` é `test_configuracao_producao.py`.

## Os doze testes do pedido

| # | Teste do pedido | Onde |
|---|---|---|
| 1 | Acesso atual funciona em homologação controlada | `HOM::test_o_seletor_identifica_como_antes`, `::test_sem_provedor_a_pagina_de_acesso_e_a_de_antes`, `::test_com_provedor_o_seletor_continua_e_nao_cria_identidade` |
| 2 | Modo demonstração recusado em produção | `ATI::test_sob_a_marca_de_producao_o_seletor_nao_existe_mesmo_ligado`, `::test_sessao_de_demonstracao_aberta_cai_sob_a_marca_de_producao`; `PROD::test_seletor_ao_lado_do_provedor_continua_recusado` e o caso `INTERFACE_SELETOR_IDENTIDADE` de `::test_configuracao_insegura_impede_a_inicializacao` |
| 3 | Identidade institucional simulada produz o `Actor` esperado | `ENT::test_a_entrada_institucional_produz_o_ator_dos_vinculos` |
| 4 | Mesmo usuário em duas unidades com papéis diferentes | `ENT::test_a_mesma_pessoa_em_duas_unidades_tem_as_permissoes_da_unidade_ativa`, `::test_a_troca_para_unidade_sem_vinculo_e_recusada` |
| 5 | Revogação de papel impede novas operações | `ENT::test_a_revogacao_vale_na_requisicao_seguinte`, `::test_a_revogacao_de_um_papel_tira_so_aquele` |
| 6 | Sem autoconcessão | `VIN::test_ninguem_concede_a_si_mesmo`, `::test_ninguem_revoga_o_proprio_vinculo`, `::test_o_institucional_nao_concede_a_si_mesmo` |
| 7 | Administrador de unidade não concede em outra unidade | `VIN::test_administrador_da_unidade_nao_concede_em_outra`, `::test_administrador_da_unidade_nao_revoga_em_outra` |
| 8 | Segregação de funções usa identidade estável | `ENT::test_a_segregacao_reconhece_a_pessoa_em_outra_sessao` |
| 9 | Autorização por comissão não cria acesso indevido após revogação | `ENT::test_a_presidencia_nao_alcanca_quem_perdeu_o_vinculo` |
| 10 | Configuração incompleta de produção não autentica por *fallback* | `ATI::test_producao_sem_provedor_bloqueia_sem_oferecer_demonstracao`, `::test_o_provedor_de_teste_nao_autentica_sob_a_marca_de_producao`, `::test_sessao_institucional_cai_quando_o_provedor_some`; `PROD::test_provedor_institucional_nao_implantavel_impede_a_inicializacao`, `::test_provedor_que_se_declara_de_teste_impede_a_inicializacao` |
| 11 | Registros históricos e documentos íntegros | `HOM::test_a_migration_da_106_so_cria_tabelas_e_gatilhos`, `::test_as_tabelas_append_only_anteriores_continuam_todas`; `migrations/test_migrations.py` |
| 12 | Testes funcionais existentes continuam passando | a suíte inteira contra PostgreSQL ([verificação](verificacao.md)) |

## Requisitos

| Requisitos | Tarefas | Testes |
|---|---|---|
| FR-3001 (seletor igual) | T010, T013 | `HOM::test_o_seletor_identifica_como_antes`, `::test_sem_provedor_a_pagina_de_acesso_e_a_de_antes`; a suíte |
| FR-3002 (demonstração não cria nem se converte) | T010, T013 | `HOM::test_com_provedor_o_seletor_continua_e_nao_cria_identidade`, `::test_a_identidade_de_demonstracao_nao_se_converte_em_institucional`, `::test_so_com_a_entrada_institucional_o_envio_do_seletor_nao_vale` |
| FR-3003 (seletor recusado sob produção em execução) | T015 | `ATI::test_sob_a_marca_de_producao_o_seletor_nao_existe_mesmo_ligado`, `::test_sessao_de_demonstracao_aberta_cai_sob_a_marca_de_producao` |
| FR-3004 (identificador interno imutável) | T004, T005, T009 | `ENT::test_o_primeiro_acesso_cria_a_pessoa_e_o_seguinte_nao_muda_o_identificador`; `VIN::test_o_identificador_da_pessoa_nao_muda_e_ela_nao_se_exclui` |
| FR-3005 (identidade externa única, nunca por e-mail) | T004, T009 | `ENT::test_identidade_de_outro_provedor_e_recusada`; `HOM::test_a_identidade_de_demonstracao_nao_se_converte_em_institucional`; `VIN::test_vinculo_e_identidade_externa_nao_mudam_no_banco` |
| FR-3006 (primeiro acesso cria; seguintes atualizam) | T009 | `ENT::test_o_primeiro_acesso_cria_a_pessoa_e_o_seguinte_nao_muda_o_identificador` |
| FR-3007 (pessoa não se exclui; sem senha; superusuário inerte) | T005, T009 | `VIN::test_o_identificador_da_pessoa_nao_muda_e_ela_nao_se_exclui`; `ATI::test_usuario_e_senha_nao_autenticam`, `::test_superusuario_sem_vinculo_nao_tem_ator`, `::test_o_unico_backend_e_o_institucional` |
| FR-3008 (vínculo e revogação imutáveis) | T004, T005 | `VIN::test_vinculo_e_identidade_externa_nao_mudam_no_banco`, `::test_o_save_recusa_reescrever`, `::test_a_segunda_revogacao_o_banco_recusa` |
| FR-3009 (catálogo de acesso à parte) | T007 | `VIN::test_o_catalogo_de_acesso_nao_entra_no_seletor`; `ENT::test_a_presidencia_nao_alcanca_quem_perdeu_o_vinculo` (integrante) |
| FR-3010 (operacional exige `acesso:gerir`; outra unidade é 404) | T008 | `VIN::test_administrador_da_unidade_nao_concede_em_outra`, `::test_concede_papel_operacional_com_trilha` |
| FR-3011 (administrador de acessos pelo institucional; institucional só pelo comando) | T008, T017 | `VIN::test_o_institucional_concede_o_administrador_de_qualquer_unidade`, `::test_administrador_da_unidade_nao_concede_papel_de_acesso`, `::test_administrador_institucional_nao_se_concede_pela_aplicacao`, `::test_o_institucional_nao_tem_poder_operacional` |
| FR-3012 (ninguém concede a si mesmo) | T008 | `VIN::test_ninguem_concede_a_si_mesmo`, `::test_ninguem_revoga_o_proprio_vinculo`, `::test_o_institucional_nao_concede_a_si_mesmo` |
| FR-3013 (recusas da concessão) | T008 | `VIN::test_concessao_recusa_o_malformado`, `::test_concessao_em_unidade_nao_registrada_e_recusada`, `::test_o_mesmo_papel_vigente_nao_se_concede_duas_vezes`, `::test_a_sincronizacao_recusa_o_codigo_reservado` |
| FR-3014 (revogação) | T008 | `VIN::test_revogacao_com_trilha_e_uma_vez_so`, `::test_a_segunda_revogacao_o_banco_recusa` |
| FR-3015 (trilha da concessão e da revogação) | T008 | `VIN::test_concede_papel_operacional_com_trilha`, `::test_revogacao_com_trilha_e_uma_vez_so` |
| FR-3016 (leitura exige `acesso:consultar`) | T008 | `VIN::test_a_consulta_dos_vinculos_exige_a_permissao` |
| FR-3017 (`Actor` dos vínculos, por requisição) | T010 | `ENT::test_a_entrada_institucional_produz_o_ator_dos_vinculos`, `::test_a_revogacao_vale_na_requisicao_seguinte` |
| FR-3018 (sem vínculo, sem `Actor`) | T010 | `ENT::test_sem_vinculo_entra_mas_nao_tem_ator`, `::test_a_presidencia_nao_alcanca_quem_perdeu_o_vinculo` |
| FR-3019 (unidade ativa e troca) | T010, T013 | `ENT::test_a_mesma_pessoa_em_duas_unidades_tem_as_permissoes_da_unidade_ativa`, `::test_a_troca_para_unidade_sem_vinculo_e_recusada` |
| FR-3020 (entrada roda a sessão; entrada e saída na trilha) | T010 | `ENT::test_a_entrada_troca_a_sessao`, `::test_a_entrada_vai_a_trilha_com_escopo`; `HOM::test_a_sessao_de_demonstracao_e_a_institucional_nao_se_misturam` |
| FR-3021 (desativada perde a sessão) | T009 | `ENT::test_pessoa_desativada_perde_a_sessao` |
| FR-3022 (contrato; nenhum cabeçalho) | T009, T013 | `ENT::test_cabecalho_do_cliente_nao_autentica`, `::test_identidade_de_outro_provedor_e_recusada` |
| FR-3023 (estado de uso único) | T013 | `ENT::test_retorno_sem_a_ida_e_recusado_sem_criar_pessoa`, `::test_retorno_com_estado_divergente_e_recusado`, `::test_o_retorno_nao_vale_duas_vezes`, `::test_o_retorno_le_o_state_do_protocolo_e_nao_o_nome_interno`, `::test_o_adaptador_pode_dizer_onde_o_estado_volta` |
| FR-3024 (simulado só no teste) | T012, T016 | `PROD::test_provedor_institucional_nao_implantavel_impede_a_inicializacao`, `::test_provedor_que_se_declara_de_teste_impede_a_inicializacao`; `ATI::test_o_provedor_marcado_de_teste_fora_de_tests_tambem_nao` |
| FR-3025 (botão só com provedor) | T013 | `HOM::test_sem_provedor_a_pagina_de_acesso_e_a_de_antes`, `::test_com_provedor_o_seletor_continua_e_nao_cria_identidade` |
| FR-3026 (recusas de produção) | T016 | `PROD::test_provedor_institucional_nao_implantavel_impede_a_inicializacao`, `::test_provedor_que_se_declara_de_teste_impede_a_inicializacao`, `::test_producao_sem_provedor_sobe_com_o_backend_institucional_e_sem_seletor`; `ATI::test_o_provedor_de_teste_nao_autentica_sob_a_marca_de_producao` |
| FR-3027 (sem provedor, 503 sem demonstração) | T016 | `ATI::test_producao_sem_provedor_bloqueia_sem_oferecer_demonstracao`; `PROD::test_producao_sem_provedor_sobe_com_o_backend_institucional_e_sem_seletor` |
| FR-3028 (origem não admitida encerra a sessão) | T010 | `ATI::test_sessao_institucional_cai_quando_o_provedor_some`, `::test_sessao_institucional_nao_vira_demonstracao_com_o_seletor_ligado`, `::test_sessao_de_demonstracao_aberta_cai_sob_a_marca_de_producao` |
| FR-3029 (comando do primeiro administrador) | T017 | `VIN::test_o_comando_concede_o_primeiro_administrador_e_recusa_o_segundo_sem_marca`, `::test_o_comando_exige_motivo`; `seguranca/test_concorrencia.py::test_duas_primeiras_administracoes_simultaneas_gravam_uma_so`, `::test_com_adicional_explicito_as_duas_simultaneas_valem`; `seguranca/test_privilegios.py::test_a_runtime_obtem_a_trava_da_administracao_institucional` |
| FR-3030 (migration só cria e protege) | T005, T006 | `HOM::test_a_migration_da_106_so_cria_tabelas_e_gatilhos`, `::test_as_tabelas_append_only_anteriores_continuam_todas`; `migrations/test_migrations.py` |
| FR-3031 (documentos de homologação e de ativação) | T019, T020 | por construção: [`doc/homologacao-com-o-seletor-de-demonstracao.md`](../../doc/homologacao-com-o-seletor-de-demonstracao.md), [`doc/ativacao-do-sso-institucional.md`](../../doc/ativacao-do-sso-institucional.md) |
| SC-1001 (suíte sem mudança de resultado esperado) | T022 | a suíte; [verificação](verificacao.md) |
| SC-1002 (os doze testes) | T011, T014, T018 | a tabela acima |
| SC-1003 (zero caminhos de demonstração em produção) | T015, T016 | os testes 2 e 10 acima |
| SC-1004 (revogação na requisição seguinte) | T010 | `ENT::test_a_revogacao_vale_na_requisicao_seguinte`, `::test_a_presidencia_nao_alcanca_quem_perdeu_o_vinculo` |
| SC-1005 (até duas consultas) | T010 | `ENT::test_o_ator_custa_no_maximo_duas_consultas_por_requisicao` |
| SC-1006 (demonstração sem consulta a mais) | T010 | os orçamentos de consulta existentes da suíte, que identificam pelo seletor e não mudaram |
