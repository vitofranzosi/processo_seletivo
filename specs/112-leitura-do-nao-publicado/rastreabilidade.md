# Rastreabilidade: Leitura do conteúdo não publicado na gestão

Cada requisito → a decisão → a tarefa → o teste que o verificará. **A feature não está implementada**:
os nomes de teste abaixo são os **planejados**, e a T032 os confere contra os arquivos depois da
implementação. Caminhos relativos a `backend/tests/`: `REG` é
`publicacoes/test_leitura_do_nao_publicado.py`, `MAT` é
`authorization/test_leitura_do_nao_publicado.py`, `PAP` é
`authorization/test_papel_da_leitura_do_rascunho.py`, `ROT` é `test_rotas_do_nao_publicado.py`,
`GRA` é `test_gramatica_das_portas.py`, `VIS` é `authorization/test_visao_institucional.py`.

## Requisitos

| Requisitos | Decisões | Tarefas | Testes |
|---|---|---|---|
| FR-3501 (não publicado = sem Publicação, qualquer situação) | D-002 | T006, T007 | `REG::test_edital_cancelado_sem_publicacao_e_nao_publicado`, `::test_edital_publicado_e_cancelado_e_publicado` |
| FR-3502 (capacidade própria em quatro papéis, e só neles) | D-001 | T004, T005 | `PAP::test_a_grafia_da_permissao`, `::test_so_os_quatro_papeis_a_tem` |
| FR-3503 (conteúdo só com a capacidade) | D-002 | T006, T007, T015–T017 | `REG::test_conteudo_exige_a_permissao`; `MAT` linhas `CONTEUDO` e `EXISTENCIA` |
| FR-3504 (existência do Edital: capacidade, auditoria ou vínculo) | D-002, D-005 | T006, T007, T025 | `REG::test_existencia_do_edital_por_auditoria_e_por_vinculo`; `MAT` linhas `EXISTENCIA` |
| FR-3505 (existência da Retificação só com a capacidade; auditor na trilha) | D-002, D-005 | T006, T017 | `REG::test_retificacao_em_curso_so_com_a_permissao`; `MAT::test_auditor_ve_a_retificacao_so_na_trilha` |
| FR-3506 (uma regra, fora das views) | D-002, D-003 | T007, T008, T009 | `ROT::test_toda_rota_classificada_chama_a_porta_exigida` |
| FR-3507 (anexos pela mesma regra; emenda à FR-017 da `020`) | D-001 | T022, T023 | `MAT::test_publicador_e_gestor_abrem_anexo_do_rascunho` |
| FR-3508 (a lista omite o não publicado e a marca da Retificação) | D-006 | T011, T013 | `MAT::test_a_lista_do_integrante_so_tem_o_publicado` |
| FR-3509 (detalhe: 404 sem existência; reduzido com existência) | D-003, D-004 | T014, T026 | `MAT::test_detalhe_reduzido_a_quem_so_tem_a_existencia` |
| FR-3510 (detalhe do publicado sem Retificações em curso) | D-002 | T011, T014 | `MAT::test_detalhe_do_publicado_sem_retificacao_em_curso` |
| FR-3511 (composição, prévia, PDF, anexos, ato e fragmentos exigem conteúdo) | D-003 | T015, T016 | `MAT` linhas das rotas C do Edital |
| FR-3512 (Retificação em curso exige conteúdo; `retificar` omite a lista) | D-003 | T017 | `MAT` linhas das rotas C da Retificação |
| FR-3513 (Processo omite e recusa) | D-002, D-003 | T018 | `MAT` linhas `processo-*` e `supervisao`; `REG::test_processo_sem_edital_publicado_sem_vinculo` |
| FR-3514 (Visão Geral pela regra) | D-002 | T029 | `VIS::test_a_visao_aplica_a_leitura_do_nao_publicado` |
| FR-3515 (no backend, antes da leitura e do estado) | D-003 | T012 | `MAT::test_previa_sem_existencia_e_404_e_nao_409`, `::test_post_na_composicao_sem_existencia_e_404` |
| FR-3516 (Agenda, trilha da unidade, relatório, alocações e faixa não mudam) | D-007 | T030 | `MAT::test_agenda_so_tem_publicado`, `::test_faixa_nao_oferece_o_que_a_regra_recusa` |
| FR-3517 (404 a quem não tem a existência) | D-004 | T011, T020 | `MAT` linhas `NENHUM`; `GRA::test_o_inventario_cobre_toda_funcao_que_responde_inexistente` |
| FR-3518 (recusa explicada a quem só tem a existência) | D-004 | T025 | `MAT::test_recusa_explicada_usa_a_formulacao_canonica`; `GRA::test_toda_tela_que_manda_pedir_usa_a_formulacao_canonica` |
| FR-3519 (inventário da `033`) | D-004 | T020 | `GRA::test_o_inventario_cobre_toda_funcao_que_responde_inexistente`, `::test_nenhuma_porta_responde_inexistente_para_recusa_de_autorizacao` |
| FR-3520 (a recusa não diz situação, número, título nem autor) | D-004 | T011 | `MAT::test_o_404_e_identico_ao_do_inexistente` |
| FR-3521 (o efeito sobre cada papel é o da tabela) | D-001, D-002 | T011, T022, T025 | `MAT` inteira, parametrizada pela tabela da spec |
| FR-3522 (descrições e catálogo de acessos não mudam) | D-001 | T004 | `PAP::test_descricoes_e_numero_de_papeis_inalterados` |
| FR-3523 (papel novo não recebe a capacidade sem decisão) | D-001 | T004 | `PAP::test_so_os_quatro_papeis_a_tem` |
| FR-3524 (matriz rota × ator, por URL direta) | D-008 | T010, T011, T022, T025 | `MAT` |
| FR-3525 (guardião das rotas) | D-008 | T009 | `ROT::test_toda_rota_com_identificador_esta_no_inventario`, `::test_o_detector_reconhece_uma_rota_inventada` |
| FR-3526 (a lista sem consulta por linha) | D-006 | T013, T031 | `MAT::test_a_lista_faz_as_mesmas_consultas_com_e_sem_a_permissao` |
| FR-3527 (toda rota com identificador responde 404 sem existência, antes do estado) | D-003, D-004 | T019 | `MAT` linhas das rotas P; `ROT::test_toda_rota_classificada_chama_a_porta_exigida` |

## Critérios de sucesso

| Critério | Tarefas | Verificação |
|---|---|---|
| SC-1061 (100% da matriz) | T011, T022, T025 | `MAT` |
| SC-1062 (zero mudança de expectativa fora das listadas) | T002, T021, T024 | a lista §Testes que mudam, conferida contra o diff do PR |
| SC-1063 (o integrante não descobre nada) | T011, T033 | `MAT` e o [quickstart](quickstart.md), passo 2 |
| SC-1064 (rota nova sem classificação reprova) | T009 | `ROT::test_o_detector_reconhece_uma_rota_inventada` |
| SC-1065 (mesmo número de consultas na lista) | T031 | `MAT::test_a_lista_faz_as_mesmas_consultas_com_e_sem_a_permissao` |
| SC-1066 (presidência e publicador seguem; validação humana) | T033 | sessão de homologação com o usuário |

## Casos-limite

| Caso | Tarefas | Teste |
|---|---|---|
| EC-1 | T006 | `REG::test_edital_cancelado_sem_publicacao_e_nao_publicado` |
| EC-2 | T006 | `REG::test_edital_publicado_e_cancelado_e_publicado` |
| EC-3 | T006 | `REG::test_retificacao_cancelada_sem_publicacao` |
| EC-4 | T012 | `MAT::test_previa_sem_existencia_e_404_e_nao_409` |
| EC-5 | T012 | `MAT::test_post_na_composicao_sem_existencia_e_404` |
| EC-6 | T006, T018 | `REG::test_processo_sem_edital_publicado_sem_vinculo` |
| EC-7 | — | coberto pela resolução por requisição da `106`; sem teste novo |
| EC-8 | T006 | `REG::test_a_permissao_vale_so_no_escopo_ativo` |
| EC-9 | T009 | `ROT` (classe F) |
| EC-10 | T030 | `MAT::test_faixa_nao_oferece_o_que_a_regra_recusa` |
| EC-11 | T029 | `VIS::test_a_visao_aplica_a_leitura_do_nao_publicado` |
| EC-12 | T030 | `MAT::test_agenda_so_tem_publicado` |

## Testes que mudam

Preenchida pela T002, antes da implementação. Vazia nesta revisão da spec.
