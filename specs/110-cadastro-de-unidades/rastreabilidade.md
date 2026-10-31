# Rastreabilidade: Cadastro de unidades administrado pela aplicação

Cada requisito → a decisão → a tarefa → o teste que o verifica. **Os nomes são os reais**, conferidos
na T049 contra os arquivos, depois da implementação. Caminhos relativos a `backend/tests/`: `SEM` é
`unidades/test_semente.py`, `REG` é `unidades/test_regra_da_unidade.py`, `ADM` é
`unidades/test_administrar_unidades.py`, `CMP` é `unidades/test_compatibilidade_do_registro.py`,
`AUT` é `authorization/test_administrar_unidades.py`, `ISO` é
`interface/test_isolamento_entre_unidades.py`, `ESC` é `integration/test_escopo_imutavel.py`,
`TEL` é `interface/test_telas_de_unidades.py`, `NAV` é `navegador/test_jornada_de_unidades.py`,
`PAP` é `seguranca/test_papel_institucional_administra_unidades.py`, `HOM` é `homologacao/test_entrada_de_homologacao.py`.

Revista em 31/10/2026 com a revisão final: tarefas renumeradas pelos três incrementos (D-019), e as
linhas de FR-3339 a FR-3343, SC-1048 e EC-16 a EC-18 acrescentadas. Na simplificação do mesmo dia
(D-002, papel institucional existente), FR-3340, FR-3341, EC-16, T019 e T020 foram retirados; as
linhas ficam, marcadas, porque os números ficam reservados.

## Requisitos

| Requisitos | Decisões | Tarefas | Testes |
|---|---|---|---|
| FR-3301 (o banco é a fonte; nenhum passo altera nem recusa unidade) | D-001 | T022–T024 | `SEM::test_a_semente_nao_desfaz_a_tela`, `::test_a_inicializacao_nao_altera_o_registro` |
| FR-3302 (semeia só registro vazio; diz quando não se aplica) | D-001, D-004 | T022, T023 | `SEM::test_registro_vazio_e_semeado_com_trilha_da_implantacao`, `::test_registro_preenchido_nao_grava_nem_le_o_arquivo` |
| FR-3303 (não falha por unidade fora do arquivo nem por divergência) | D-001 | T022 | `SEM::test_unidade_fora_do_arquivo_e_valores_diferentes_permanecem`, `::test_unidade_fora_do_arquivo_e_valores_diferentes_permanecem` |
| FR-3304 (valida pela regra única quando se aplica; trilha da implantação) | D-004, D-005 | T015, T022 | `SEM::test_arquivo_malformado_falha_com_registro_vazio_sem_gravar_nada`, `::test_registro_vazio_e_semeado_com_trilha_da_implantacao` |
| FR-3305 (idempotente; modelos iniciais garantidos) | D-004 | T023 | `SEM::test_os_modelos_iniciais_sao_garantidos_uma_vez`, `::test_duas_sementes_simultaneas_gravam_uma_vez` |
| FR-3306 (os três roteiros chamam a semente pelo nome novo; o anterior fica como apelido que avisa) | D-003 | T023, T024 | `SEM::test_os_roteiros_do_repositorio_chamam_a_semente_pelo_nome_novo`, `::test_o_nome_anterior_roda_a_semente_e_avisa` |
| FR-3307 (documentação operacional) | D-003 | T045–T047 | `SEM::test_os_roteiros_do_repositorio_chamam_a_semente_pelo_nome_novo` (o guia); leitura na revisão do PR |
| FR-3308 (a permissão no papel institucional existente, e só nele; nada novo de autorização) | D-002 | T016, T018 | `AUT::test_a_grafia_da_permissao_e_a_mesma`, `::test_nenhum_outro_papel_tem_a_permissao`; `PAP::test_o_papel_institucional_tem_as_duas_permissoes_e_o_rotulo_novo` |
| FR-3309 (conferida na aplicação, escopo institucional) | D-006 | T028–T030 | `AUT::test_cada_caso_de_uso_recusa_sem_a_permissao` |
| FR-3310 (nenhuma outra capacidade; comandos sem mudança; ampliação só com autorização) | D-002 | T018, T021, T047 | `AUT::test_a_permissao_nao_abre_processo_edital_nem_acesso`; `PAP::test_concedido_pelo_comando_de_sempre_alcanca_as_duas_capacidades`; o passo 0 da [migração](migracao.md), conferido no deploy |
| FR-3311 (nenhuma unidade altera o próprio cadastro) | D-002 | T028–T030 | `AUT::test_papel_de_unidade_e_recusado_inclusive_na_propria`, `::test_cada_caso_de_uso_recusa_sem_a_permissao` |
| FR-3312 (só a entrada institucional) | D-011 | T036 | `TEL::test_a_demonstracao_e_recusada_e_nao_ve_o_item`; `AUT::test_cada_caso_de_uso_recusa_sem_a_permissao` |
| FR-3313 (motivo; quem, quando, antes e depois) | D-006, D-008 | T028–T030 | `ADM::test_cada_ato_grava_o_evento_no_escopo_da_unidade`, `::test_sem_motivo_nada_e_gravado` |
| FR-3314 (a lista) | D-011 | T036, T039 | `TEL::test_a_lista_mostra_ativas_e_desativadas` |
| FR-3315 (a ficha e o histórico; 404 do inexistente) | D-009, D-011 | T036, T038, T041 | `TEL::test_a_ficha_mostra_o_historico_da_implantacao_e_da_pessoa`, `::test_codigo_inexistente_e_404`; `test_gramatica_das_portas.py::test_o_inventario_cobre_toda_funcao_que_responde_inexistente` |
| FR-3316 (os campos do cadastro; nasce ativa) | D-006 | T028, T039 | `ADM::test_registrar_uma_unidade`; `TEL::test_o_cadastro_passa_pela_conferencia_que_nao_grava` |
| FR-3317 (formato, reservado, único; aviso de permanência) | D-005 | T015, T028, T039 | `REG::test_caixa_e_espaco_no_codigo_sao_recusados_sem_conversao`, `::test_codigo_institucional_e_recusado`; `ADM::test_codigo_repetido_e_recusado`; `TEL::test_o_cadastro_passa_pela_conferencia_que_nao_grava` |
| FR-3318 (uma regra para cadastro, edição e semente) | D-005 | T015, T022 | `REG::*`; `SEM::test_arquivo_malformado_falha_com_registro_vazio_sem_gravar_nada` |
| FR-3319 (modelos iniciais no cadastro, uma vez) | D-006 | T028 | `ADM::test_os_modelos_iniciais_nascem_uma_vez_com_a_pessoa_como_autora` |
| FR-3320 (disponível na requisição seguinte) | D-006 | T028 | `ADM::test_unidade_nova_disponivel_para_acesso_processo_e_autoridade`; `NAV::test_de_unidade_inexistente_a_processo_criado` |
| FR-3321 (edita os campos, nunca o código) | D-006 | T029 | `ADM::test_alterar_grava_antes_e_depois`, `::test_o_codigo_enviado_na_alteracao_e_ignorado` |
| FR-3322 (sem mudança, recusa) | D-006 | T029 | `ADM::test_nada_mudou_e_recusado_sem_evento` |
| FR-3323 (não altera o publicado) | — (congelamento da `060`) | T044 | `CMP::test_editar_a_unidade_nao_muda_o_publicado` |
| FR-3324 (prévia; nada antes da confirmação) | D-010 | T037, T039 | `TEL::test_a_previa_usa_as_linhas_do_compositor`, `::test_o_cadastro_passa_pela_conferencia_que_nao_grava`, `::test_a_edicao_mostra_antes_e_depois_e_ignora_o_codigo` |
| FR-3325 (a confirmação reconfere; versão) | D-007 | T029 | `ADM::test_duas_alteracoes_concorrentes_a_segunda_e_recusada` |
| FR-3326 (desativar: motivo e consequências) | D-006 | T030, T039 | `TEL::test_a_desativacao_diz_as_consequencias_e_desativa`; `ADM::test_desativada_nao_recebe_processo_e_conduz_o_existente` |
| FR-3327 (reativar) | D-006 | T030 | `ADM::test_reativada_volta_a_receber_processo` |
| FR-3328 (transição repetida recusada) | D-006 | T030 | `ADM::test_transicoes_repetidas_sao_recusadas` |
| FR-3329 (nenhuma exclusão) | — (gatilho da `060`) | T036 | `TEL::test_nenhuma_tela_oferece_exclusao`; regressão `test_nenhuma_unidade_se_exclui` da `060` |
| FR-3330 (aviso da moldura) | D-006 | T030, T039 | `TEL::test_o_aviso_da_moldura_aparece_quando_muda_o_numero_de_ativas` |
| FR-3331 (eventos que a trilha da `108` lê) | D-008 | T028–T030 | `ADM::test_cada_ato_grava_o_evento_no_escopo_da_unidade`, `TEL::test_a_trilha_da_unidade_le_os_atos` |
| FR-3332 (ato e evento na mesma transação) | D-006 | T028–T030 | `ADM::test_falha_no_evento_desfaz_o_ato` |
| FR-3333 (escopo de Processo e Edital imutável no banco) | D-013 | T004 | `ESC::test_update_do_escopo_e_recusado`, `::test_save_que_muda_o_escopo_e_recusado`, `::test_sql_direto_e_recusado`, `::test_save_sem_mudanca_e_aceito` |
| FR-3334 (código e exclusão continuam recusados) | — (gatilhos da `060`) | T007 | `ESC::test_os_gatilhos_da_060_continuam`; regressão `test_o_codigo_da_unidade_nao_muda` |
| FR-3335 (testes criam na outra unidade) | D-013 | T006 | `integration/agenda/test_fonte.py::test_edital_de_outro_escopo_nao_aparece_nem_pelo_filtro` |
| FR-3336 (isolamento nas quatro áreas) | D-014 | T008 | `ISO::test_a_ocupacao_alheia_e_inexistente_e_nao_grava`, `::test_o_recurso_alheio_e_inexistente_e_nao_grava`, `::test_o_requerimento_e_o_documento_alheios_sao_inexistentes`, `::test_a_api_administrativa_nao_alcanca_processo_nem_edital_alheios` (nomes reais, incremento A) |
| FR-3337 (instalação existente sem ação) | D-001 | T044 | `CMP::test_o_cefor_continua_sem_acao` |
| FR-3338 (seletor e `seed_demo`) | — | T024, T044 | `integration/test_seed_demo.py` (a suíte de sempre); `TEL::test_a_demonstracao_e_recusada_e_nao_ve_o_item`; a suíte do seletor, sem mudança |
| FR-3339 (a tela continua recusando conceder o papel institucional) | D-002 | T021 | `PAP::test_a_aplicacao_continua_recusando_conceder_o_papel` |
| FR-3340 — *retirada (D-002); a suspensão segue a FR-3136 da `107`* | — | — | — |
| FR-3341 — *retirada (D-002)* | — | — | — |
| FR-3342 (provedor de homologação sobre o simulado, só no teste; produção recusa; sem criptografia própria) | D-018 | T010–T012 | `test_configuracao_producao.py::test_provedor_institucional_nao_implantavel_impede_a_inicializacao[tests.homologacao.provedor.ProvedorDeHomologacao]`, `::test_o_provedor_de_homologacao_copiado_para_fora_de_tests_ainda_e_recusado`; `HOM::test_o_provedor_e_o_simulado_e_se_declara_de_teste`, `::test_sob_a_marca_de_producao_o_provedor_nao_existe` (nomes reais, incremento B) |
| FR-3343 (só as pessoas do provedor; bilhete de uso único; a gestão confere o estado) | D-018 | T010, T012 | `HOM::test_a_pagina_lista_so_as_pessoas_do_provedor`, `::test_escolher_entra_no_escopo_dos_vinculos`, `::test_sem_pessoa_cadastrada_a_pagina_diz_como_cadastrar`, `::test_o_bilhete_escolhido_nao_serve_duas_vezes`, `::test_retorno_sem_o_estado_da_ida_e_recusado` (nomes reais, incremento B) |

## Critérios de sucesso

| Critério | Como se mede | Teste |
|---|---|---|
| SC-1041 (unidade operável sem repositório, deploy nem servidor) | a jornada sem ação fora do navegador; `git status` limpo | `NAV::test_de_unidade_inexistente_a_processo_criado` |
| SC-1042 (semente e inicialização deixam o registro idêntico) | comparação campo a campo e contagem de eventos | `SEM::test_a_inicializacao_nao_altera_o_registro`, `::test_a_semente_nao_desfaz_a_tela` |
| SC-1043 (zero caminhos sem a permissão) | matriz de papéis × atos, pela aplicação e pela tela, com envio forjado | `AUT::*`; `TEL::test_envio_forjado_sem_permissao_e_recusado` |
| SC-1044 (todo ato com evento completo) | um evento por ato, com os campos do data-model | `ADM::test_cada_ato_grava_o_evento_no_escopo_da_unidade` |
| SC-1045 (publicado byte a byte) | resumo do documento e do conteúdo antes e depois | `CMP::test_editar_a_unidade_nao_muda_o_publicado` |
| SC-1046 (até três telas) | a jornada conta as navegações | `NAV::test_de_unidade_inexistente_a_processo_criado`; `TEL::test_o_cadastro_passa_pela_conferencia_que_nao_grava` |
| SC-1047 (suíte sem mudança de resultado, salvo as três exceções) | `make test-pg` contra a base | T009, T014, T050, registrado no `verificacao.md` |
| SC-1048 (validação funcional por uma pessoa, sem ajuda) | o roteiro G, conduzido com uma pessoa da equipe | **critério de aceite humano, sem teste automatizado**: T051, em seção própria do `verificacao.md` |

## Casos-limite

| Caso | Tarefa | Teste |
|---|---|---|
| EC-1 (código com caixa ou espaço, sem conversão) | T015 | `REG::test_caixa_e_espaco_no_codigo_sao_recusados_sem_conversao` |
| EC-2 (mesmo código ao mesmo tempo) | T028 | `ADM::test_dois_cadastros_do_mesmo_codigo_gravam_um` |
| EC-3 (edição sem mudança) | T029 | `ADM::test_nada_mudou_e_recusado_sem_evento` |
| EC-4 (só espaços) | T015, T029 | `REG::test_espacos_das_pontas_sao_aparados`; `ADM::test_nada_mudou_e_recusado_sem_evento` |
| EC-5 (desativar a única ativa) | T030 | `ADM::test_desativar_a_unica_ativa_e_permitido` |
| EC-6 (desativar com certame aberto; contagem) | T030, T039 | `TEL::test_a_desativacao_diz_as_consequencias_e_desativa` |
| EC-7 (a segunda ativa muda a moldura; aviso) | T030, T039 | `TEL::test_o_aviso_da_moldura_aparece_quando_muda_o_numero_de_ativas` |
| EC-8 (institucional com escopo de unidade) | T034 | `AUT::test_cada_caso_de_uso_recusa_sem_a_permissao` |
| EC-9 (código forjado na edição) | T029 | `ADM::test_o_codigo_enviado_na_alteracao_e_ignorado`; `TEL::test_a_edicao_mostra_antes_e_depois_e_ignora_o_codigo` |
| EC-10 (demonstração recusada antes de ler) | T036 | `TEL::test_a_demonstracao_e_recusada_e_nao_ve_o_item` |
| EC-11 (semente malformada só com registro vazio) | T022 | `SEM::test_arquivo_malformado_falha_com_registro_vazio_sem_gravar_nada`, `::test_o_comando_transforma_a_recusa_em_erro_de_comando` |
| EC-12 (canal apagado volta ao institucional) | T029 | `ADM::test_canal_apagado_volta_ao_institucional` |
| EC-13 (Reitoria é unidade como as outras) | T028 | `ADM::test_reitoria_e_unidade_como_as_outras_sem_leitura_dos_campi` |
| EC-14 (autoridade de desativada continua editável) | T033 | `ADM::test_autoridade_de_desativada_continua_editavel` |
| EC-15 (teste cria na outra unidade) | T006 | `integration/agenda/test_fonte.py::test_edital_de_outro_escopo_nao_aparece_nem_pelo_filtro` |
| EC-16 — *retirado (D-002)* | — | — |
| EC-17 (roteiro com o nome anterior do comando) | T023, T025 | `SEM::test_o_nome_anterior_roda_a_semente_e_avisa` |
| EC-18 (conceder o papel institucional pela tela) | T021 | `PAP::test_a_aplicacao_continua_recusando_conceder_o_papel` |

## Os quinze testes do pedido

Mapeados um a um no [plan](plan.md), §Os quinze testes obrigatórios do pedido.
