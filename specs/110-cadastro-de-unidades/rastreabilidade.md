# Rastreabilidade: Cadastro de unidades administrado pela aplicação

Cada requisito → a decisão → a tarefa → o teste que o verifica. **Os testes são os planejados**: os
nomes se confirmam na T049, depois da implementação. Caminhos relativos a `backend/tests/`: `SEM` é
`unidades/test_semente.py`, `REG` é `unidades/test_regra_da_unidade.py`, `ADM` é
`unidades/test_administrar_unidades.py`, `CMP` é `unidades/test_compatibilidade_do_registro.py`,
`AUT` é `authorization/test_administrar_unidades.py`, `ISO` é
`authorization/test_isolamento_entre_unidades.py`, `ESC` é `integration/test_escopo_imutavel.py`,
`TEL` é `interface/test_telas_de_unidades.py`, `NAV` é `navegador/test_jornada_de_unidades.py`,
`PAP` é `seguranca/test_papel_do_registro.py`, `HOM` é `homologacao/test_entrada_de_homologacao.py`.

Revista em 31/10/2026 com a revisão final: tarefas renumeradas pelos três incrementos (D-019), e as
linhas de FR-3339 a FR-3343, SC-1048 e EC-16 a EC-18 acrescentadas.

## Requisitos

| Requisitos | Decisões | Tarefas | Testes |
|---|---|---|---|
| FR-3301 (o banco é a fonte; nenhum passo altera nem recusa unidade) | D-001 | T022–T024 | `SEM::test_a_semente_nao_desfaz_a_tela`, `::test_a_inicializacao_nao_altera_o_registro` |
| FR-3302 (semeia só registro vazio; diz quando não se aplica) | D-001, D-004 | T022, T023 | `SEM::test_registro_vazio_e_semeado`, `::test_registro_preenchido_nao_grava_nem_le_o_arquivo` |
| FR-3303 (não falha por unidade fora do arquivo nem por divergência) | D-001 | T022 | `SEM::test_unidade_fora_do_arquivo_permanece`, `::test_valores_diferentes_no_arquivo_nao_se_aplicam` |
| FR-3304 (valida pela regra única quando se aplica; trilha da implantação) | D-004, D-005 | T015, T022 | `SEM::test_arquivo_malformado_so_falha_com_registro_vazio`, `::test_registro_vazio_e_semeado` |
| FR-3305 (idempotente; modelos iniciais garantidos) | D-004 | T023 | `SEM::test_modelos_iniciais_idempotentes`, `::test_duas_sementes_simultaneas_gravam_uma_vez` |
| FR-3306 (os três roteiros chamam a semente pelo nome novo; o anterior fica como apelido que avisa) | D-003 | T023, T024 | `SEM::test_os_roteiros_chamam_a_semente`, `::test_o_nome_anterior_roda_a_semente_e_avisa` |
| FR-3307 (documentação operacional) | D-003 | T045–T047 | `SEM::test_os_roteiros_chamam_a_semente` (o guia); leitura na revisão do PR |
| FR-3308 (a permissão num papel institucional próprio, e só nele) | D-002 | T016, T018 | `AUT::test_a_grafia_da_permissao_e_a_mesma`, `::test_nenhum_outro_papel_tem_a_permissao`; `PAP::test_o_papel_do_registro_so_tem_a_permissao` |
| FR-3309 (conferida na aplicação, escopo institucional) | D-006 | T028–T030 | `AUT::test_cada_caso_de_uso_recusa_sem_a_permissao` |
| FR-3310 (nenhuma outra capacidade; só a implantação concede, retira e substitui) | D-002 | T018–T020 | `AUT::test_a_permissao_nao_abre_processo_edital_nem_acesso`; `PAP::test_conceder_retirar_e_substituir_com_papel`, `::test_segunda_pessoa_pede_adicional_por_papel`, `::test_sem_papel_os_comandos_fazem_o_de_antes` |
| FR-3311 (nenhuma unidade altera o próprio cadastro) | D-002 | T028–T030 | `AUT::test_papel_de_unidade_e_recusado_inclusive_na_propria`, `::test_institucional_com_escopo_de_unidade_e_recusado` |
| FR-3312 (só a entrada institucional) | D-011 | T036 | `TEL::test_a_demonstracao_e_recusada_e_nao_ve_o_item`; `AUT::test_a_demonstracao_e_recusada` |
| FR-3313 (motivo; quem, quando, antes e depois) | D-006, D-008 | T028–T030 | `ADM::test_cada_ato_grava_o_evento_no_escopo_da_unidade`, `::test_sem_motivo_nada_e_gravado` |
| FR-3314 (a lista) | D-011 | T036, T039 | `TEL::test_a_lista_mostra_ativas_e_desativadas` |
| FR-3315 (a ficha e o histórico; 404 do inexistente) | D-009, D-011 | T036, T038, T041 | `TEL::test_a_ficha_mostra_o_historico_da_implantacao_e_da_pessoa`, `::test_codigo_inexistente_e_404`; `test_gramatica_das_portas.py::test_o_inventario_cobre_toda_funcao_que_responde_inexistente` |
| FR-3316 (os campos do cadastro; nasce ativa) | D-006 | T028, T039 | `ADM::test_registrar_uma_unidade`; `TEL::test_o_cadastro_passa_pela_conferencia` |
| FR-3317 (formato, reservado, único; aviso de permanência) | D-005 | T015, T028, T039 | `REG::test_codigo_fora_do_formato_e_recusado`, `::test_codigo_institucional_e_recusado`; `ADM::test_codigo_repetido_e_recusado`; `TEL::test_a_conferencia_avisa_que_o_codigo_e_permanente` |
| FR-3318 (uma regra para cadastro, edição e semente) | D-005 | T015, T022 | `REG::*`; `SEM::test_arquivo_malformado_so_falha_com_registro_vazio` |
| FR-3319 (modelos iniciais no cadastro, uma vez) | D-006 | T028 | `ADM::test_os_modelos_iniciais_nascem_uma_vez` |
| FR-3320 (disponível na requisição seguinte) | D-006 | T028 | `ADM::test_unidade_nova_disponivel_para_acesso_processo_e_autoridade`; `NAV::test_de_unidade_inexistente_a_processo_criado` |
| FR-3321 (edita os campos, nunca o código) | D-006 | T029 | `ADM::test_alterar_grava_antes_e_depois`, `::test_o_codigo_enviado_na_alteracao_e_ignorado` |
| FR-3322 (sem mudança, recusa) | D-006 | T029 | `ADM::test_nada_mudou_e_recusado_sem_evento` |
| FR-3323 (não altera o publicado) | — (congelamento da `060`) | T044 | `CMP::test_editar_a_unidade_nao_muda_o_publicado` |
| FR-3324 (prévia; nada antes da confirmação) | D-010 | T037, T039 | `TEL::test_a_previa_usa_as_linhas_do_compositor`, `::test_a_conferencia_nao_grava`, `::test_a_edicao_mostra_antes_e_depois` |
| FR-3325 (a confirmação reconfere; versão) | D-007 | T029 | `ADM::test_duas_alteracoes_concorrentes_a_segunda_e_recusada` |
| FR-3326 (desativar: motivo e consequências) | D-006 | T030, T039 | `TEL::test_a_desativacao_diz_as_consequencias`; `ADM::test_desativada_nao_recebe_processo_e_conduz_o_existente` |
| FR-3327 (reativar) | D-006 | T030 | `ADM::test_reativada_volta_a_receber_processo` |
| FR-3328 (transição repetida recusada) | D-006 | T030 | `ADM::test_transicoes_repetidas_sao_recusadas` |
| FR-3329 (nenhuma exclusão) | — (gatilho da `060`) | T036 | `TEL::test_nenhuma_tela_oferece_exclusao`; regressão `test_nenhuma_unidade_se_exclui` da `060` |
| FR-3330 (aviso da moldura) | D-006 | T030, T039 | `TEL::test_o_aviso_da_moldura_aparece_quando_muda_o_numero_de_ativas` |
| FR-3331 (eventos que a trilha da `108` lê) | D-008 | T028–T030 | `ADM::test_cada_ato_grava_o_evento_no_escopo_da_unidade`, `::test_a_trilha_da_unidade_le_os_atos` |
| FR-3332 (ato e evento na mesma transação) | D-006 | T028–T030 | `ADM::test_falha_no_evento_desfaz_o_ato` |
| FR-3333 (escopo de Processo e Edital imutável no banco) | D-013 | T004 | `ESC::test_update_do_escopo_e_recusado`, `::test_save_que_muda_o_escopo_e_recusado`, `::test_sql_direto_e_recusado`, `::test_save_sem_mudanca_e_aceito` |
| FR-3334 (código e exclusão continuam recusados) | — (gatilhos da `060`) | T007 | `ESC::test_os_gatilhos_da_060_continuam`; regressão `test_o_codigo_da_unidade_nao_muda` |
| FR-3335 (testes criam na outra unidade) | D-013 | T006 | `integration/agenda/test_fonte.py::test_edital_de_outro_escopo_nao_aparece_nem_pelo_filtro` |
| FR-3336 (isolamento nas quatro áreas) | D-014 | T008 | `ISO::test_ocupacao_alheia`, `::test_recurso_alheio`, `::test_requerimento_alheio`, `::test_api_administrativa_alheia` |
| FR-3337 (instalação existente sem ação) | D-001 | T044 | `CMP::test_o_cefor_continua_sem_acao` |
| FR-3338 (seletor e `seed_demo`) | — | T024, T044 | `CMP::test_seed_demo_continua`; `TEL::test_a_demonstracao_e_recusada_e_nao_ve_o_item`; a suíte do seletor, sem mudança |
| FR-3339 (nenhuma tela concede papel institucional) | D-002 | T019 | `PAP::test_a_aplicacao_nao_concede_o_papel_do_registro` |
| FR-3340 (suspensão de papel institucional só pela implantação) | D-002 | T019 | `PAP::test_so_a_implantacao_suspende_o_administrador_do_registro` |
| FR-3341 (quem só tem o papel do registro: escopo institucional, barra, recusa nos acessos) | D-002 | T040, T042 | `TEL::test_os_dois_papeis_institucionais_separados_e_juntos` |
| FR-3342 (provedor de homologação sobre o simulado, só no teste; produção recusa; sem criptografia própria) | D-018 | T010–T012 | `HOM::test_producao_recusa_o_provedor_no_boot`, `::test_producao_recusa_o_provedor_em_execucao` |
| FR-3343 (só as pessoas do provedor; bilhete de uso único; a gestão confere o estado) | D-018 | T010, T012 | `HOM::test_a_pagina_lista_so_as_pessoas_do_provedor`, `::test_escolher_entra_no_escopo_dos_vinculos`, `::test_o_bilhete_nao_serve_duas_vezes`, `::test_retorno_sem_estado_e_recusado` |

## Critérios de sucesso

| Critério | Como se mede | Teste |
|---|---|---|
| SC-1041 (unidade operável sem repositório, deploy nem servidor) | a jornada sem ação fora do navegador; `git status` limpo | `NAV::test_de_unidade_inexistente_a_processo_criado` |
| SC-1042 (semente e inicialização deixam o registro idêntico) | comparação campo a campo e contagem de eventos | `SEM::test_a_inicializacao_nao_altera_o_registro`, `::test_a_semente_nao_desfaz_a_tela` |
| SC-1043 (zero caminhos sem a permissão) | matriz de papéis × atos, pela aplicação e pela tela, com envio forjado | `AUT::*`; `TEL::test_envio_forjado_sem_permissao_e_recusado` |
| SC-1044 (todo ato com evento completo) | um evento por ato, com os campos do data-model | `ADM::test_cada_ato_grava_o_evento_no_escopo_da_unidade` |
| SC-1045 (publicado byte a byte) | resumo do documento e do conteúdo antes e depois | `CMP::test_editar_a_unidade_nao_muda_o_publicado` |
| SC-1046 (até três telas) | a jornada conta as navegações | `NAV::test_de_unidade_inexistente_a_processo_criado`; `TEL::test_o_cadastro_passa_pela_conferencia` |
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
| EC-6 (desativar com certame aberto; contagem) | T030, T039 | `TEL::test_a_desativacao_diz_as_consequencias` |
| EC-7 (a segunda ativa muda a moldura; aviso) | T030, T039 | `TEL::test_o_aviso_da_moldura_aparece_quando_muda_o_numero_de_ativas` |
| EC-8 (institucional com escopo de unidade) | T034 | `AUT::test_institucional_com_escopo_de_unidade_e_recusado` |
| EC-9 (código forjado na edição) | T029 | `ADM::test_o_codigo_enviado_na_alteracao_e_ignorado`; `TEL::test_codigo_no_corpo_da_edicao_e_ignorado` |
| EC-10 (demonstração recusada antes de ler) | T036 | `TEL::test_a_demonstracao_e_recusada_e_nao_ve_o_item` |
| EC-11 (semente malformada só com registro vazio) | T022 | `SEM::test_arquivo_malformado_so_falha_com_registro_vazio` |
| EC-12 (canal apagado volta ao institucional) | T029 | `ADM::test_canal_apagado_volta_ao_institucional` |
| EC-13 (Reitoria é unidade como as outras) | T028 | `ADM::test_reitoria_e_unidade_sem_leitura_dos_campi` |
| EC-14 (autoridade de desativada continua editável) | T033 | `ADM::test_autoridade_de_desativada_continua_editavel` |
| EC-15 (teste cria na outra unidade) | T006 | `integration/agenda/test_fonte.py::test_edital_de_outro_escopo_nao_aparece_nem_pelo_filtro` |
| EC-16 (só um dos dois papéis institucionais) | T034, T042 | `AUT::test_administrador_de_acessos_sem_o_papel_do_registro_e_recusado`; `TEL::test_os_dois_papeis_institucionais_separados_e_juntos` |
| EC-17 (roteiro com o nome anterior do comando) | T023, T025 | `SEM::test_o_nome_anterior_roda_a_semente_e_avisa` |
| EC-18 (conceder o papel do registro pela tela) | T019, T021 | `PAP::test_a_aplicacao_nao_concede_o_papel_do_registro` |

## Os quinze testes do pedido

Mapeados um a um no [plan](plan.md), §Os quinze testes obrigatórios do pedido.
