# Rastreabilidade: Entrega documental controlada ao setor da formalização (117)

Cada requisito → a tarefa que o implementa → o teste que o verifica. Caminhos de teste relativos a
`backend/tests/`. Abreviações:

- `df` = `integration/formalizacao/test_definicao.py`
- `ac` = `integration/formalizacao/test_acesso.py`
- `cj` = `unit/formalizacao/test_conjunto.py`
- `cm` = `unit/formalizacao/test_caminhos.py`
- `tr` = `unit/formalizacao/test_grafia_da_trilha.py`
- `ex` = `integration/formalizacao/test_exportacao.py`
- `cp` = `integration/formalizacao/test_comprovante.py`
- `fa` = `integration/formalizacao/test_falhas.py`
- `cv` = `integration/formalizacao/test_ciclo_de_vida.py`
- `cc` = `integration/formalizacao/test_concorrencia.py`
- `mx` = `interface/test_permissoes_da_formalizacao.py`
- `vc` = `interface/test_vocabulario_da_formalizacao.py`
- `ai` = `interface/test_arquivo_indisponivel.py`
- `pa` = `authorization/test_papel_da_formalizacao.py`
- `pf` = `performance/test_exportacao_de_formalizacao.py`
- `nv` = `navegador/test_jornada_da_formalizacao.py`

## Requisitos funcionais

| Requisito | Tarefas | Testes |
|---|---|---|
| FR-3653 (definição por Edital, de qualquer momento, vazia por padrão) | T004, T011 | `df::test_a_definicao_comeca_vazia_e_nada_fica_disponivel`; `cj::test_so_os_documentos_definidos_aparecem` |
| FR-3654 (grava quem gere a comissão; o setor não) | T011, T012 | `df::test_quem_grava_quem_le_e_quem_e_recusado` (seis linhas); `mx::test_formalizacao_com_designacao_sem_restricao` (`gravar_definicao` 403) |
| FR-3655 (append-only, versionada, motivo obrigatório; cada exportação grava a versão) | T004, T005, T011, T025 | `df::test_a_gravacao_sem_motivo_e_recusada_e_nada_e_gravado`, `::test_o_motivo_vazio_tambem_e_recusado_pelo_banco`, `::test_a_definicao_e_append_only_por_gatilho`; `ex::test_completo_mostra_o_resultado_e_o_zip_tem_o_verificado` (registro com a definição) |
| FR-3656 (versão nova vale para a seguinte, sem mudar as passadas) | T011, T018 | `df::test_a_versao_nova_vale_para_a_consulta_seguinte`; `cj::test_a_versao_da_definicao_e_a_que_se_passa`; `ex::test_defasada_pela_definicao` |
| FR-3657 (fora do snapshot, do hash e do PDF; sem Retificação) | T011 | `df::test_o_conteudo_publicado_nao_muda` |
| FR-3658 (os dois avisos, sem impedir) | T011, T012 | `df::test_os_avisos_saem_do_momento_e_do_recorte`, `::test_a_tela_mostra_os_avisos_sem_impedir_a_gravacao`; `nv::test_cenario_a_define_verifica_completo_e_baixa` |
| FR-3659 (o arquivo aproveitado sai uma vez, pelo item da convocação) | T018 | `cj::test_o_arquivo_aproveitado_por_referencia_sai_uma_vez` |
| FR-3660 (os Editais existentes começam vazios; nenhuma migration cria definição) | T005, T011 | `df::test_a_definicao_comeca_vazia_e_nada_fica_disponivel`; `migrations/test_migrations.py` (a `0001` só cria tabelas e gatilhos) |
| FR-3661 (o papel Formalização, uma capacidade, nenhum papel existente a ganha) | T007 | `pa::test_so_o_papel_da_formalizacao_tem_a_permissao`, `::test_o_papel_da_formalizacao_nao_concede_mais_nada`, `::test_a_grafia_e_a_mesma_nos_dois_lugares` |
| FR-3662 (designação append-only com Perfis opcionais, revogação com motivo) | T004, T015 | `ac::test_designar_grava_com_motivo_e_vai_as_duas_trilhas`, `::test_revogar_e_designar_de_novo_muda_os_perfis`, `::test_designacao_e_revogacao_sao_append_only_por_gatilho` |
| FR-3663 (`acesso:gerir`, papel vigente, sem autodesignação; mudar Perfis é revogar) | T015, T016 | `ac::test_designar_quem_nao_tem_o_papel_e_recusado_com_codigo_proprio`, `::test_ninguem_designa_a_si_mesmo`, `::test_a_autodesignacao_e_recusada_pelo_banco_tambem`, `::test_a_presidencia_designa_no_proprio_processo` (até 12/11, `test_a_presidencia_nao_designa`), `::test_o_perfil_de_fora_do_edital_e_recusado`, `::test_uma_designacao_vigente_por_edital_e_pessoa`, `::test_duas_designacoes_simultaneas_gravam_uma`, `::test_a_tela_de_acessos_designa_e_revoga` |
| FR-3664 (o predicado único, na mesma requisição) | T014, T020, T025 | `ac::test_sem_o_papel_a_recusa_nomeia_o_papel`, `::test_o_papel_sem_designacao_no_edital_e_inexistente`, `::test_pessoa_de_perfil_fora_da_designacao_e_inexistente`; `mx` (todas as linhas) |
| FR-3665 (nenhuma outra base alcança; o predicado não alcança a conferência) | T014, T020 | `mx::test_as_demais_bases_nao_alcancam_a_pagina_do_setor` (cinco bases); `ac::test_quem_confere_nao_alcanca_a_formalizacao_e_o_setor_nao_alcanca_a_conferencia`; `nv::test_cenario_e_o_controle_de_acesso_pelas_urls` |
| FR-3666 (404 fora do alcance; 403 nomeando o papel) | T014, T021 | `mx::test_formalizacao_no_perfil_a_e_pessoa_do_perfil_b`, `::test_formalizacao_sem_designacao_no_edital`, `::test_designacao_vigente_e_papel_revogado`, `::test_ator_de_outra_unidade_recebe_inexistente_em_tudo` |
| FR-3667 (revogação do papel, da designação e suspensão cortam na seguinte) | T014 | `ac::test_o_papel_revogado_corta_todas_as_designacoes`, `::test_a_revogacao_da_designacao_corta_na_requisicao_seguinte`, `::test_a_suspensao_corta_o_acesso`; `cp::test_depois_da_revogacao_do_papel_e_recusa_de_autorizacao` |
| FR-3668 (a condução vê as designações; trilha da unidade e do Edital; revista em 12/11) | T015, T016, T035, T042 | `ac::test_quem_gere_a_comissao_sem_presidir_ve_as_designacoes_so_para_leitura` (até 12/11, `test_a_presidencia_ve_as_designacoes_na_conducao_so_para_leitura`), `::test_a_presidencia_designa_e_revoga_na_tela_da_definicao`, `::test_designar_grava_com_motivo_e_vai_as_duas_trilhas` |
| FR-3669 (apto: desfecho vigente da chamada mais recente, lido na hora) | T018 | `cj::test_so_quem_tem_aceite_vigente_esta_apto`, `::test_os_desfechos_que_incluem_sao_os_da_convocacao`, `::test_o_aceite_sucedido_por_indeferimento_tira_a_pessoa`, `::test_a_convocacao_corrigida_le_a_vigente`, `::test_vale_a_chamada_mais_recente` |
| FR-3670 (conjunto: item conforme da convocação e documento da inscrição) | T018 | `cj::test_o_da_inscricao_sai_sem_conferencia_e_diz_isso`, `::test_so_os_documentos_definidos_aparecem` |
| FR-3671 (convocação sem conforme vigente não sai; inscrição sai e diz isso) | T018, T020, T024 | `cj::test_documento_da_convocacao_sem_conferencia_conforme_vigente_nao_sai`, `::test_o_da_inscricao_sai_sem_conferencia_e_diz_isso`; `nv::test_cenario_a_define_verifica_completo_e_baixa` (a nota na tela) |
| FR-3672 (as seis situações; só indisponível e integridade excluem) | T006, T018 | `cj::test_nao_se_aplica_e_nao_apresentado_deixam_a_pessoa_completa`, `::test_a_conferencia_nao_se_aplica_e_situacao_nao_se_aplica`; `ex::test_parcial_nomeia_os_excluidos_antes_do_download` |
| FR-3673 (nada fora da definição, de não apto, nem Requerimento, nota ou parecer) | T018, T024 | `cj::test_so_os_documentos_definidos_aparecem`, `::test_so_quem_tem_aceite_vigente_esta_apto`; `ex::test_completo_mostra_o_resultado_e_o_zip_tem_o_verificado` (o manifesto sem CPF) |
| FR-3674 (seletor único) | T018, T025 | `ex::test_o_sha256_de_cada_arquivo_e_do_pacote_confere` (o manifesto e o registro do mesmo conjunto); `pf::test_a_pagina_e_a_verificacao_nao_consultam_por_pessoa` |
| FR-3675 (a barra pela capacidade; a lista só com designação vigente) | T020 | `mx::test_formalizacao_sem_designacao_no_edital` (lista 200, página 404); `interface/test_shell_da_gestao.py::test_cada_item_tem_icone_decorativo_e_nome_acessivel`; `nv::test_cenario_a_define_verifica_completo_e_baixa` |
| FR-3676 (a página: aptos por Perfil, protocolo, chamada, última exportação; sem CPF) | T020 | `nv::test_cenario_a_define_verifica_completo_e_baixa`; `ex::test_parcial_nomeia_os_excluidos_antes_do_download` (o histórico na página) |
| FR-3677 (visualizar primária, sem cache; baixar individual com nome do sistema) | T020 | `fa::test_o_arquivo_ausente_na_pagina_do_setor_e_indisponivel_e_nao_500`; `cm::test_o_download_individual_usa_protocolo_e_requisito`; `verificacao.md` (cabeçalhos medidos) |
| FR-3678 (sem definição: os aptos e o porquê, sem exportação) | T020 | `df::test_a_definicao_comeca_vazia_e_nada_fica_disponivel` |
| FR-3679 (histórico de exportações no alcance) | T020, T026 | `ex::test_parcial_nomeia_os_excluidos_antes_do_download`; `nv::test_cenario_a_define_verifica_completo_e_baixa` |
| FR-3680 (linguagem simples, 375 px, termos vedados) | T020, T023 | `vc` (todas); `nv::test_cenario_a_define_verifica_completo_e_baixa`, `::test_cenario_f_a_verificacao_parcial_vem_antes_do_download` (`scrollWidth` a 375) |
| FR-3681 (um controle de recorte, o Perfil) | T020 | `ex::test_o_recorte_por_perfil` |
| FR-3682 (três alcances; seleção por POST; id fora do alcance recusa tudo) | T025, T026 | `ex::test_a_selecao_exporta_so_as_marcadas`, `::test_o_recorte_por_perfil`, `::test_post_forjado_com_pessoa_fora_do_alcance_recusa_tudo`; `mx::test_as_urls_levam_so_identificadores_opacos` |
| FR-3683 (nada fora do alcance; a lista sem marcação) | T020, T025 | `ex::test_a_lista_comeca_sem_marcacao`; `df::test_a_tela_mostra_os_avisos_sem_impedir_a_gravacao` |
| FR-3684 (verificação antes, resultado primeiro, botão com N e parcial) | T025, T026 | `ex::test_completo_mostra_o_resultado_e_o_zip_tem_o_verificado`, `::test_parcial_nomeia_os_excluidos_antes_do_download`, `::test_verificacao_sem_pessoa_incluivel_nao_tem_botao`; `nv::test_cenario_f_a_verificacao_parcial_vem_antes_do_download` |
| FR-3685 (pessoa única: ZIP ou página com o motivo) | T025, T026 | `ex::test_pessoa_unica_completa_sai_num_clique`, `::test_pessoa_unica_com_falha_recebe_pagina_e_nada_e_registrado` |
| FR-3686 (ZIP sem compressão, pasta por pessoa, nome do arquivo) | T024 | `ex::test_completo_mostra_o_resultado_e_o_zip_tem_o_verificado`, `::test_duas_exportacoes_iguais_dao_entradas_identicas`; `cm::test_o_nome_do_pacote_nao_tem_dado_pessoal_e_diz_parcial` |
| FR-3687 (o manifesto: cabeçalho e uma linha por documento, sem CPF) | T024 | `ex::test_parcial_nomeia_os_excluidos_antes_do_download`, `::test_completo_mostra_o_resultado_e_o_zip_tem_o_verificado` |
| FR-3688 (temporário sem nome, que deixa de existir; `attachment` sem cache) | T024 | `cv::test_o_temporario_nao_tem_nome_no_disco`, `::test_sucesso_fecha_o_temporario_solta_a_trava_e_nada_sobra`, `::test_o_cliente_que_desconecta_fecha_o_temporario_e_o_registro_continua`; `ex::test_completo_mostra_o_resultado_e_o_zip_tem_o_verificado` (`no-store`) |
| FR-3689 (o download exige o comprovante e recompõe a verificação) | T025 | `ex::test_defasada_pelo_desfecho`, `::test_defasada_pela_definicao`, `::test_defasada_pelo_arquivo_trocado`; `cp` |
| FR-3689a (comprovante assinado, de 15 minutos, do ator; recusas antes de ler) | T024a, T025 | `cp::test_adulterado_num_byte_e_invalido`, `::test_um_resumo_sha256_montado_a_mao_e_invalido`, `::test_assinado_com_outro_sal_e_invalido`, `::test_expirado_depois_de_15_minutos`, `::test_emitido_para_outro_servidor_e_invalido`, `::test_emitido_para_outra_unidade_e_invalido`, `::test_o_reuso_dentro_da_validade_e_outra_exportacao_registrada`, `::test_o_comprovante_nao_leva_dado_pessoal` |
| FR-3689b (o resumo cobre incluídas, excluídas e motivos; tudo relido) | T024a, T025 | `ex::test_defasada_pela_designacao_revogada_e_concedida_de_novo`, `::test_defasada_pelo_excluido_restaurado`, `::test_defasada_pelo_motivo_trocado`, `::test_defasada_pelo_desfecho` |
| FR-3690 (hash na mesma leitura que copia) | T024, T025 | `ex::test_o_sha256_de_cada_arquivo_e_do_pacote_confere`, `::test_defasada_pelo_arquivo_trocado` |
| FR-3691 (limite antes de ler, com o tamanho por pessoa) | T025, T026 | `fa::test_o_limite_recusa_antes_de_ler_e_mostra_o_tamanho_por_pessoa` |
| FR-3692 (trava de transação por servidor, sem espera, solta no commit, rollback e conexão) | T025 | `cc::test_a_segunda_verificacao_do_mesmo_servidor_e_recusada`, `::test_a_segunda_montagem_do_mesmo_servidor_e_recusada`, `::test_a_de_outro_servidor_nao_e_recusada`; `cv::test_a_conexao_fechada_solta_a_trava`, `::test_excecao_injetada_desfaz_fecha_e_solta` |
| FR-3693 (exportar não escreve nada além do registro) | T025 | `df::test_o_conteudo_publicado_nao_muda`; `ex::test_completo_mostra_o_resultado_e_o_zip_tem_o_verificado` (um registro só) |
| FR-3694 (a pessoa com falha fica inteira fora) | T025 | `ex::test_parcial_nomeia_os_excluidos_antes_do_download` (sem pasta do ausente) |
| FR-3695 (arquivo ausente é indisponível, sem 500, nas views novas e nas existentes) | T008, T009 | `ai` (inscrição, mesa e convocação); `fa::test_o_arquivo_ausente_na_pagina_do_setor_e_indisponivel_e_nao_500`, `::test_ausente_e_divergente_vao_para_a_trilha_sem_nome_de_arquivo` |
| FR-3696 (divergência grava integridade e não serve) | T025 | `fa::test_ausente_e_divergente_vao_para_a_trilha_sem_nome_de_arquivo`; `ex::test_parcial_nomeia_os_excluidos_antes_do_download` |
| FR-3697 (registro só para pacote gerado, completo ou parcial) | T004, T025 | `ex::test_verificacao_sem_pessoa_incluivel_nao_tem_botao`, `::test_so_quem_nao_tem_documento_sobra_e_nao_ha_o_que_baixar`, `::test_quem_nao_tem_documento_a_exportar_nao_entra_na_exportacao`, `::test_pessoa_unica_com_falha_recebe_pagina_e_nada_e_registrado`, `::test_defasada_pelo_desfecho`; `fa::test_a_excecao_na_montagem_e_desfeita_e_dita` |
| FR-3698 (registro depois do pacote e antes da resposta; a transferência não o altera) | T025 | `cv::test_o_registro_existe_so_depois_do_pacote`, `::test_o_cliente_que_desconecta_fecha_o_temporario_e_o_registro_continua` |
| FR-3699 (os eventos, sem nome nem arquivo) | T006, T035 | `tr::test_toda_operacao_da_feature_tem_rotulo_na_trilha`, `::test_nenhum_rotulo_afirma_o_que_o_gps_nao_sabe`; `fa::test_ausente_e_divergente_vao_para_a_trilha_sem_nome_de_arquivo`; `vc::test_a_pagina_diz_disponibilizado_e_nao_mais` |
| FR-3700 (o registro append-only com ids e hashes) | T004, T005 | `ex::test_o_sha256_de_cada_arquivo_e_do_pacote_confere`; `seguranca/test_homologacao_preservada.py::test_as_tabelas_append_only_anteriores_continuam_todas`; `integration/test_database_permissions.py` (parametrizado por `TABELAS_APPEND_ONLY`) |
| FR-3701 (nenhum estado por pessoa além de "última exportação") | T018 | `nv::test_cenario_a_define_verifica_completo_e_baixa` (a linha *"Ainda não exportada"*); `vc::test_nenhuma_tela_afirma_o_que_o_gps_nao_sabe` |
| FR-3702 (o auditor vê trilha e históricos; não abre nem exporta) | T020, T035 | `df::test_quem_grava_quem_le_e_quem_e_recusado` (auditor lê, sem formulário); `mx::test_as_demais_bases_nao_alcancam_a_pagina_do_setor` (auditor) |
| FR-3703 (nenhum log com nome, CPF ou arquivo; URLs opacas) | T031 | `fa::test_os_logs_das_falhas_nao_levam_dado_pessoal`; `mx::test_as_urls_levam_so_identificadores_opacos` |
| FR-3704 (nenhuma cópia persistente) | T024 | `cv::test_sucesso_fecha_o_temporario_solta_a_trava_e_nada_sobra`, `::test_recusa_solta_a_trava_e_nada_sobra` |
| FR-3705 (só a revisão normativa e a correção do arquivo indisponível na `009` e na `115`) | T002, T008 | `test_citacoes_de_requisito.py`; `ai` |
| FR-3706 (a exceção vale só para esta exportação; texto da D-016) | T002 | revisão em `specs/009-inscricao-simples-documentos/spec.md` (FR-069) e `specs/115-documentos-na-convocacao/spec.md` (FR-3606) |
| FR-3707 (sem recebimento, encaminhamento, integração, e-mail ou assincronia) | — | por ausência: nenhuma rota, tarefa ou envio; `vc::test_nenhuma_tela_afirma_o_que_o_gps_nao_sabe` |
| FR-3708 (nenhuma unicidade presume a unidade do ator) | T004 | `formalizacao/models.py` (só índices; a unidade de atuação gravada em cada linha) |
| FR-3709 (designação e definição por Edital) | T004 | `ac::test_uma_designacao_vigente_por_edital_e_pessoa`; `df::test_cada_gravacao_e_uma_versao_e_o_historico_diz_a_diferenca` |
| FR-3710 (o encerramento não fecha página nem exportação) | T016, T018 | `designar.ESTADOS_DESIGNAVEIS` (publicado e encerrado); `ac::test_edital_sem_publicacao_nao_recebe_designacao`; o seletor não lê o estado do Edital |
| FR-3711 (o histórico da definição, à condução e ao auditor; não ao setor) | T011, T012 | `df::test_cada_gravacao_e_uma_versao_e_o_historico_diz_a_diferenca`, `::test_quem_grava_quem_le_e_quem_e_recusado` |
| FR-3712 (nomes normalizados, um nível, colisões com sufixo) | T010, T024 | `cm` (todas); `ex::test_duas_exportacoes_iguais_dao_entradas_identicas` |
| FR-3713 (manifesto UTF-8 com BOM, RFC 4180, células neutralizadas) | T010, T024 | `cm::test_a_celula_que_comecaria_uma_formula_ganha_apostrofo`, `::test_a_celula_comum_nao_muda`; `ex::test_completo_mostra_o_resultado_e_o_zip_tem_o_verificado` (BOM) |
| FR-3714 (exceção: rollback, temporário fechado, trava solta, página, evento) | T025, T026, T032 | `fa::test_a_excecao_na_montagem_e_desfeita_e_dita`, `::test_a_excecao_na_verificacao_tambem`; `cv::test_excecao_injetada_desfaz_fecha_e_solta` |

## Critérios de sucesso

| Critério | Testes |
|---|---|
| SC-1101 (no máximo 4 gestos no Cenário A) | `nv::test_cenario_a_define_verifica_completo_e_baixa`: *Verificar e exportar todos os aptos*, ler, *Baixar pacote* — três gestos |
| SC-1102 (nada fora da definição, de não apto ou de fora do Perfil) | `cj::test_so_os_documentos_definidos_aparecem`, `::test_so_quem_tem_aceite_vigente_esta_apto`; `mx::test_formalizacao_no_perfil_a_e_pessoa_do_perfil_b` |
| SC-1103 (o desfecho corrigido tira a pessoa sem ação de ninguém) | `cj::test_o_aceite_sucedido_por_indeferimento_tira_a_pessoa`; `ex::test_defasada_pelo_desfecho` |
| SC-1104 (toda URL e POST, por linha da matriz, recebe a recusa da matriz) | `mx` (sete linhas, nove portas); `ac::test_a_tela_de_acessos_recusa_quem_nao_administra` |
| SC-1105 (1 ausente e 1 divergente em 5: parcial 3 de 5 antes do download) | `ex::test_parcial_nomeia_os_excluidos_antes_do_download`; `nv::test_cenario_f_a_verificacao_parcial_vem_antes_do_download` |
| SC-1106 (nada sobra e a trava sai, em todo desfecho) | `cv` (todas) |
| SC-1107 (SHA-256 de cada arquivo e do pacote) | `ex::test_o_sha256_de_cada_arquivo_e_do_pacote_confere` |
| SC-1108 (entradas idênticas byte a byte) | `ex::test_duas_exportacoes_iguais_dao_entradas_identicas` |
| SC-1109 (visualizar e baixar sem exportar; a trilha distingue) | `nv::test_cenario_a_define_verifica_completo_e_baixa`; `mx::test_formalizacao_com_designacao_sem_restricao`; `tr::test_toda_operacao_da_feature_tem_rotulo_na_trilha` |
| SC-1110 (revogação ou suspensão recusa a seguinte) | `ac::test_o_papel_revogado_corta_todas_as_designacoes`, `::test_a_revogacao_da_designacao_corta_na_requisicao_seguinte`, `::test_a_suspensao_corta_o_acesso` |
| SC-1111 (verificação e montagem do Cenário A medidas em separado, < 30 s; consultas planas) | `pf::test_o_cenario_a_verifica_e_monta_em_menos_de_30_segundos_cada`, `::test_a_pagina_e_a_verificacao_nao_consultam_por_pessoa` |
| SC-1112 (nenhuma tela com os termos vedados) | `vc` (todas) |
| SC-1113 (o ZIP é o verificado; as cinco mudanças são defasada; comprovante recusado sem ler) | `ex::test_defasada_*` (seis casos); `cp` (todas) |
| SC-1114 (nomes hostis: nada sai da pasta, nada se repete, nada vira fórmula) | `cm` (todas) |

## Revisão de 12/11/2026 — a presidência também designa (D-025)

Prefixos: `ac` = `tests/integration/formalizacao/test_acesso.py`; `ps` =
`tests/interface/test_passagem_ao_setor.py`; `gp` = `tests/test_gramatica_das_portas.py`.

| Requisito | Tarefas | Testes |
|---|---|---|
| FR-6700 (duas bases; só a presidência do próprio Processo; `comissao:gerir` sem presidir não basta) | T041, T044 | `ac::test_a_presidencia_designa_no_proprio_processo`, `::test_so_a_presidencia_do_proprio_processo_designa` (cinco atores) |
| FR-6701 (o papel continua com `acesso:gerir`; só quem já o tem) | T041, T044 | `ac::test_a_presidencia_nao_designa_quem_nao_tem_o_papel`, `::test_designar_quem_nao_tem_o_papel_e_recusado_com_codigo_proprio` |
| FR-6702 (sem autodesignação nem autorrevogação, em qualquer base) | T041, T044 | `ac::test_a_presidencia_nao_designa_a_si_mesma`, `::test_ninguem_designa_a_si_mesmo` |
| FR-6703 (qualquer base revoga qualquer designação do Edital) | T041, T042, T044 | `ac::test_cada_base_revoga_a_designacao_da_outra`, `::test_a_presidencia_designa_e_revoga_na_tela_da_definicao` |
| FR-6704 (designar não dá à presidência os documentos) | T044 | `ac::test_designar_nao_da_a_presidencia_acesso_aos_documentos` |
| FR-6705 (as duas trilhas, com motivo, autor e base) | T041, T044 | `ac::test_a_presidencia_designa_no_proprio_processo`, `::test_cada_base_revoga_a_designacao_da_outra` |
| FR-6706 (encerrar não revoga; a designação segue os estados de hoje) | T044 | `ac::test_o_encerramento_do_edital_nao_revoga_nem_impede_designar`, `::test_edital_sem_publicacao_nao_recebe_designacao` |
| FR-6707 (404 fora do escopo ou de outro Edital; 403 nomeando as duas bases) | T041, T042, T044 | `ac::test_so_a_presidencia_do_proprio_processo_designa`, `::test_designacao_de_outro_edital_e_inexistente_na_tela`, `::test_quem_gere_a_comissao_sem_presidir_ve_as_designacoes_so_para_leitura`; `gp::test_o_inventario_cobre_toda_funcao_que_responde_inexistente` |
| FR-6708 (a providência e a advertência seguem o predicado; a FR-6111 da `153` revista) | T043, T044 | `ps::test_sem_designacao_a_providencia_e_de_quem_administra_os_acessos`, `::test_a_presidencia_ve_a_designacao_como_dela`, `::test_a_tela_de_encerrar_diz_a_quem_pedir`, `::test_a_presidencia_recebe_o_caminho_da_designacao_ao_encerrar` |
| UX-700 (a seção designa e revoga para quem pode; só leitura para os demais) | T042, T044 | `ac::test_a_presidencia_designa_e_revoga_na_tela_da_definicao`, `::test_quem_gere_a_comissao_sem_presidir_ve_as_designacoes_so_para_leitura` |
| UX-701 (sem ninguém com o papel: a quem pedir, sem link à tela de acessos) | T042, T044 | `ac::test_sem_ninguem_com_o_papel_a_secao_diz_a_quem_pedir` |
| UX-702 (recusa de negócio e sucesso voltam à seção) | T042, T044 | `ac::test_a_presidencia_designa_e_revoga_na_tela_da_definicao` |
| SC-2200 | T044 | `ac::test_so_a_presidencia_do_proprio_processo_designa`, `::test_a_presidencia_designa_no_proprio_processo` |
| SC-2201 | T044 | `ac::test_designar_nao_da_a_presidencia_acesso_aos_documentos` |
| SC-2202 | T044 | `ac::test_cada_base_revoga_a_designacao_da_outra` |
| SC-2203 | T044 | `ac::test_a_presidencia_nao_designa_a_si_mesma`, `::test_a_presidencia_nao_designa_quem_nao_tem_o_papel` |
| SC-2204 | T044 | `ac::test_a_presidencia_designa_no_proprio_processo` |
