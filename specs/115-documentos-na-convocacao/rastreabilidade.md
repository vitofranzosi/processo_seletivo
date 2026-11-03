# Rastreabilidade: Documentos e conferência na convocação (115)

Cada requisito → a tarefa que o implementa → o teste que o verifica. Caminhos de teste relativos a
`backend/tests/`. Abreviações:

- `dc` = `integration/convocacao/test_documentos_da_convocacao.py`
- `ec` = `integration/convocacao/test_aproveitamento_entre_chamadas.py`
- `al` = `integration/comissoes/test_alocacao_a_conferencia.py`
- `pz` = `integration/requerimentos/test_prazo_da_chamada.py`
- `pt` = `interface/test_portal_documentos_da_convocacao.py`
- `mx` = `interface/test_permissoes_dos_documentos_da_convocacao.py`
- `nv` = `navegador/test_jornada_dos_documentos_da_convocacao.py`
- `md` = `unit/editais/test_momento_do_documento.py`
- `pdf` = `unit/publicacoes/test_secao_da_convocacao.py`
- `fi` = `integration/inscricoes/test_documento_da_convocacao_fora_da_inscricao.py`
- `vc` = `test_vocabulario_dos_documentos_da_convocacao.py`

## Requisitos funcionais

| Requisito | Tarefas | Testes |
|---|---|---|
| FR-3563 (momento; ausência é a inscrição) | T008, T010, T012 | `md::test_a_ausencia_do_momento_e_a_inscricao`; `integration/publicacoes/test_elevacao_de_versao.py` (degrau 18); `pdf::test_sem_documento_na_convocacao_o_pdf_e_o_de_antes` |
| FR-3564 (momento publicado, não retificável) | T008, T012 | `contract/test_mutabilidade.py` (fixture `rascunho_completo` com o campo); `interface/test_retificar_exclusoes.py`; `contract/test_forma_publicada.py` |
| FR-3565 (mesmos atributos e validações) | T009, T010 | `md::test_a_aplicabilidade_da_convocacao_ve_so_o_documento_da_convocacao`; `interface/test_campos_vem_do_contrato.py` (84 retificáveis) |
| FR-3566 (aproveitamento e recusas) | T010, T012 | `md::test_o_aproveitamento_incoerente_e_recusado` (cinco casos), `::test_o_aproveitamento_valido_nao_tem_problema` |
| FR-3567 (obrigatoriedades independentes) | T010 | `md::test_o_aproveitamento_valido_nao_tem_problema` |
| FR-3568 (inscrição só com os da inscrição) | T010, T011 | `md::test_a_aplicabilidade_padrao_nao_ve_o_documento_da_convocacao`; `fi` inteiro |
| FR-3569 (seção do PDF) | T013 | `pdf` inteiro — ver *Divergências* em `verificacao.md` |
| FR-3570 (Retificação não oferece momento nem aproveitamento) | T012 | `interface/test_retificar_exclusoes.py`; `interface/test_campos_vem_do_contrato.py` |
| FR-3571 (a classificação não lê documento da convocação) | T011 | `md::test_a_aplicabilidade_padrao_nao_ve_o_documento_da_convocacao`; `fi::test_a_inscricao_e_enviada_sem_o_documento_da_convocacao` |
| FR-3572 (lista gravada na raiz, no ato) | T020 | `dc::test_a_raiz_da_chamada_grava_um_item_por_documento_da_convocacao` |
| FR-3573 (lista imutável, da chamada) | T019, T020 | `dc::test_a_sucessora_que_corrige_nao_grava_outra_lista`, `::test_o_item_da_lista_e_append_only`; `ec::test_a_chamada_nova_aproveita_o_que_nao_estava_pendente_sem_copia` |
| FR-3574 (sem exigência, como antes) | T020, T022 | `dc::test_sem_documento_na_convocacao_a_lista_fica_vazia`; `pt::test_sem_documento_na_convocacao_a_tela_e_a_de_antes` |
| FR-3575 (sem lista retroativa) | T020 | a migration `convocacao/0005` não percorre linha; `dc::test_sem_documento_na_convocacao_a_lista_fica_vazia` (convocação sem itens é sem exigência) |
| FR-3576 (aproveitamento da inscrição por referência) | T020 | `dc::test_o_certificado_enviado_na_inscricao_atende_a_convocacao_sem_copia`, `::test_sem_o_certificado_na_inscricao_o_item_nasce_a_apresentar`, `::test_a_referencia_a_documento_de_outra_inscricao_e_recusada_pelo_banco` |
| FR-3577 (o titular vê a lista) | T022 | `pt::test_a_convocada_ve_o_que_apresentar_e_ate_quando`; `nv::test_aluno_envia_corrige_a_pendencia_e_fica_apto` |
| FR-3578 (apresentar no prazo, mesma validação) | T021, T022 | `dc::test_o_titular_apresenta_e_cada_envio_e_uma_versao`, `::test_antes_do_envio_da_comunicacao_a_apresentacao_e_aceita`; `pt::test_a_convocada_envia_pelo_portal_e_le_o_resultado` |
| FR-3579 (versões append-only, `PROTECT`) | T019, T021 | `dc::test_o_titular_apresenta_e_cada_envio_e_uma_versao`, `::test_o_documento_da_inscricao_aproveitado_nao_sai_com_a_referencia` |
| FR-3580 (arquivo novo sucede a referência) | T021 | `dc::test_o_arquivo_novo_sucede_a_referencia` |
| FR-3581 (envio duplicado) | T021 | `dc::test_o_mesmo_arquivo_de_novo_nao_cria_versao`, `::test_duas_apresentacoes_com_o_mesmo_numero_sao_recusadas_pelo_banco` |
| FR-3582 (recusas sem gravar) | T021, T022 | `dc::test_o_arquivo_invalido_e_recusado_com_as_recusas_da_inscricao`, `::test_o_arquivo_acima_do_limite_e_recusado`, `::test_outro_candidato_recebe_a_recusa_de_inexistente`, `::test_depois_do_vencimento_a_apresentacao_e_recusada_e_nada_e_gravado`; `pt::test_o_arquivo_invalido_volta_com_a_recusa_da_inscricao` |
| FR-3583 (inscrição imutável; requerimento independente) | T021 | `dc::test_a_apresentacao_nao_toca_a_inscricao_enviada`; `integration/requerimentos/test_convivencia_com_o_anexo.py` (inalterado) |
| FR-3584 (portal mostra o resultado, não quem conferiu) | T022 | `pt::test_a_convocada_envia_pelo_portal_e_le_o_resultado` |
| FR-3585 (os três resultados) | T031 | `dc::test_pendente_exige_motivo_e_o_motivo_volta_ao_estado`, `::test_nao_se_aplica_sem_apresentacao_com_motivo`, `::test_conforme_exige_ter_aberto_a_versao_vigente` |
| FR-3586 (append-only; substituição com motivo) | T031 | `dc::test_mudar_a_conferencia_da_mesma_versao_exige_motivo`, `::test_a_conferencia_e_append_only` |
| FR-3587 (versão superada) | T031 | `dc::test_conferencia_sobre_versao_superada_e_recusada` |
| FR-3588 (conferência depois do vencimento) | T031 | `dc::test_a_conferencia_continua_depois_do_vencimento` |
| FR-3589 ("conforme" não é "autêntico") | T033, T041 | `vc::test_nenhuma_tela_dos_documentos_afirma_vinculo_nem_autenticidade`, `::test_a_conferencia_diz_conforme_ao_exigido` |
| FR-3590 (estado do item, derivado) | T031 | `dc::test_pendente_exige_motivo_e_o_motivo_volta_ao_estado` (pendente → complementado), `::test_o_certificado_enviado_na_inscricao_atende_a_convocacao_sem_copia` (recebido), `::test_nao_se_aplica_sem_apresentacao_com_motivo` |
| FR-3591 (estado da convocação) | T031 | `dc::test_o_aceite_espera_os_obrigatorios_conferidos` (decidida), `::test_sem_documento_na_convocacao_a_lista_fica_vazia` (sem exigência); `mx::test_a_conducao_mostra_o_resumo_e_o_caminho_dos_documentos` (para conferir) |
| FR-3592 (guarda do aceite e da regularização) | T032 | `dc::test_o_aceite_espera_os_obrigatorios_conferidos`; `nv::test_aluno_envia_corrige_a_pendencia_e_fica_apto` |
| FR-3593 (os outros desfechos livres; nada automático) | T032 | `dc::test_os_outros_desfechos_nao_dependem_dos_documentos`, `::test_o_vencimento_nao_produz_desfecho`; `nv::test_depois_do_prazo_nada_se_envia_e_nada_se_decide_sozinho` |
| FR-3594 (fundamento pré-redigido) | T034 | `dc::test_o_fundamento_do_indeferimento_vem_das_pendencias`; `mx::test_a_conducao_mostra_o_resumo_e_o_caminho_dos_documentos` |
| FR-3595 (predicado único) | T029, T033 | `al` inteiro; `mx` inteiro |
| FR-3596 (o alocado não desfecha) | T029 | `al::test_o_membro_alocado_confere_e_nao_desfecha`; `mx::test_o_membro_alocado_confere_e_nao_desfecha`; `nv::test_bolsista_devolve_a_ficha_o_alocado_confere_e_a_presidencia_aceita` |
| FR-3597 (alocação registrada e revogável) | T029, T030 | `al::test_a_revogacao_e_a_saida_da_comissao_tiram_o_alcance_na_hora`, `::test_o_membro_alocado_nao_aloca`; `nv::test_bolsista_devolve_a_ficha_o_alocado_confere_e_a_presidencia_aceita` |
| FR-3598 (auditor e consulta de inscrição não abrem) | T033 | `mx::test_quem_nao_confere_nao_abre_o_arquivo` |
| FR-3599 (404 fora do alcance, 403 sem base) | T033, T035 | `mx::test_o_membro_alocado_a_outro_perfil_recebe_inexistente`, `::test_de_outra_unidade_tudo_e_inexistente`, `::test_quem_nao_confere_nao_abre_o_arquivo`; `test_gramatica_das_portas.py` (inventário da `033`) |
| FR-3600 (só o titular, no portal) | T022 | `pt::test_outro_candidato_nao_alcanca_nem_a_lista_nem_o_arquivo`; `dc::test_outro_candidato_recebe_a_recusa_de_inexistente` |
| FR-3601 (nenhum papel nem capacidade nova) | T029 | `al::test_o_membro_so_alocado_a_etapa_nao_confere`; `interface/identidade.py` sem entrada nova em `PAPEIS` |
| FR-3602 (unidade de atuação nas linhas) | T019, T029 | `dc::test_conforme_exige_ter_aberto_a_versao_vigente` (`unidade_de_atuacao`); `al::test_o_membro_alocado_confere_e_nao_desfecha` |
| FR-3603 (trilha sem nome nem motivo) | T040 | `mx::test_a_abertura_fica_na_trilha_sem_o_nome_do_arquivo` |
| FR-3604 (consulta ao dossiê, A-07) | T040 | `mx::test_abrir_o_dossie_da_inscricao_deixa_rastro` |
| FR-3605 (hash reconferido na entrega) | T033 | `mx::test_o_gestor_e_a_presidencia_abrem_conferem_e_conduzem` (entrega verificada); a divergência usa o mesmo `INTEGRIDADE` da `009` |
| FR-3606 (sem lote; baixar individual registrado) | T033 | `mx::test_a_abertura_fica_na_trilha_sem_o_nome_do_arquivo`; nenhuma rota de lote em `interface/urls.py` |
| FR-3607 (resumo e ordem na condução) | T034 | `mx::test_a_conducao_mostra_o_resumo_e_o_caminho_dos_documentos`; `nv::test_aluno_envia_corrige_a_pendencia_e_fica_apto` |
| FR-3608 (página dos documentos) | T033 | `mx` inteiro; `nv` (a marca "aberto por você") |
| FR-3609 (sem lote) | T033 | a página não tem ação coletiva; `interface/test_telas_de_resultado_e_atos.py` (botões presos) |
| FR-3610 ("apto para formalização"; termos proibidos) | T034, T041 | `vc` inteiro; `nv::test_bolsista_devolve_a_ficha_o_alocado_confere_e_a_presidencia_aceita` |
| FR-3611 ("conforme" exige abrir a versão, nesta chamada) | T031 | `dc::test_conforme_exige_ter_aberto_a_versao_vigente`; `ec::test_a_abertura_na_chamada_anterior_nao_autoriza_o_conforme_da_nova`; `nv::test_a_chamada_nova_aproveita_e_confere_de_novo` |
| FR-3612 (textos do portal, 375 px) | T022 | `pt::test_a_convocada_envia_pelo_portal_e_le_o_resultado`, `::test_depois_do_vencimento_a_tela_diz_o_prazo_e_nao_oferece_envio`, `::test_o_certificado_da_inscricao_aparece_atendido`; `nv` (sem rolagem horizontal) |
| FR-3613 (sem leitura nova) | T022 | `pt::test_mostrar_a_lista_nao_registra_leitura_alem_da_convocacao` |
| FR-3614 (nenhuma mensagem) | T044 | `test_situacoes_de_mensagem.py` (inalterado, quatro situações) |
| FR-3615 (nada se exclui) | T019, T046 | `dc::test_o_item_da_lista_e_append_only`, `::test_a_conferencia_e_append_only`, `::test_o_documento_da_inscricao_aproveitado_nao_sai_com_a_referencia`; `integration/test_database_permissions.py` (49 tabelas) |
| FR-3616 (encerramento inalterado) | T045 | `dc::test_edital_encerrado_com_convocacao_em_aberto_continua_recebendo_e_conferindo` |
| FR-3617 (sem formulário de vinculação nem desfecho novo) | T044 | `pt::test_o_bolsista_baixa_o_modelo_anexo_e_nada_diz_bolsa_concedida`; `convocacao/domain/nomes.py` com as sete espécies de antes |
| FR-3618 (prazo novo é correção da convocação) | T028 | `dc::test_a_correcao_com_vencimento_novo_reabre_a_apresentacao`; `pz::test_a_correcao_com_vencimento_novo_reabre` |
| FR-3619 (aproveitamento entre chamadas) | T056 | `ec::test_a_chamada_nova_aproveita_o_que_nao_estava_pendente_sem_copia`, `::test_a_referencia_aponta_a_origem_e_nunca_outra_referencia` |
| FR-3620 (a conferência não se transporta) | T056 | `ec::test_a_chamada_nova_aproveita_o_que_nao_estava_pendente_sem_copia` |
| FR-3621 (a origem à vista na página) | T056 | `nv::test_a_chamada_nova_aproveita_e_confere_de_novo`; `ItemLido.exigencia_mudou` |
| FR-3622 (o Requerimento respeita o prazo da chamada) | T052 a T054 | `pz` inteiro, com e sem documento na chamada |

## Critérios de sucesso

| Critério | Tarefas | Testes |
|---|---|---|
| SC-1081 (aluno de ponta a ponta) | T047 | `nv::test_aluno_envia_corrige_a_pendencia_e_fica_apto` |
| SC-1082 (bolsista, sem termos proibidos) | T036, T047 | `nv::test_bolsista_devolve_a_ficha_o_alocado_confere_e_a_presidencia_aceita`; `pt::test_o_bolsista_baixa_o_modelo_anexo_e_nada_diz_bolsa_concedida`; `vc` |
| SC-1083 (aproveitamento sem arquivo novo) | T015 | `dc::test_o_certificado_enviado_na_inscricao_atende_a_convocacao_sem_copia`; `nv::test_o_certificado_da_inscricao_atende_sem_reenvio` |
| SC-1084 (inscrição sem os documentos da convocação) | T007 | `fi` inteiro |
| SC-1085 (Editais sem documento da convocação inalterados) | T006 | `pdf::test_sem_documento_na_convocacao_o_pdf_e_o_de_antes`; a suíte anterior sem edição de expectativa, salvo as contagens nomeadas em `verificacao.md` |
| SC-1086 (guarda em 100%; nada automático) | T027, T028 | `dc::test_o_aceite_espera_os_obrigatorios_conferidos`, `::test_o_vencimento_nao_produz_desfecho` |
| SC-1087 (matriz de permissões) | T024 | `mx` inteiro |
| SC-1088 (trilha com ator e unidade) | T038, T039 | `mx::test_a_abertura_fica_na_trilha_sem_o_nome_do_arquivo`, `::test_abrir_o_dossie_da_inscricao_deixa_rastro` |
| SC-1089 (navegador, 375 px e desktop, sem CSP) | T047 | `nv` inteiro (a fixture `tela` reprova violação no console) |
| SC-1090 (três tabelas append-only, 49) | T018, T019 | `integration/test_database_permissions.py`; `seguranca/test_homologacao_preservada.py` |
| SC-1091 (abrir e conferir em três interações) | T033 | `nv::abrir_e_conferir` (abrir, escolher, registrar), na mesma página |
| SC-1092 (chamada nova sem arquivo novo nem "conforme") | T055 | `ec::test_a_chamada_nova_aproveita_o_que_nao_estava_pendente_sem_copia` |
| SC-1093 (prazo único no Requerimento) | T053 | `pz` inteiro |

## Casos-limite

| Caso | Requisito | Teste |
|---|---|---|
| Convocação sem exigência documental | FR-3574 | `dc::test_sem_documento_na_convocacao_a_lista_fica_vazia`; `pt::test_sem_documento_na_convocacao_a_tela_e_a_de_antes` |
| Convocação registrada antes da feature | FR-3575 | idem (sem itens é sem exigência) |
| Convocação corrigida por sucessão | FR-3573 | `dc::test_a_sucessora_que_corrige_nao_grava_outra_lista` |
| Nova chamada da mesma inscrição | FR-3619 a FR-3621 | `ec` inteiro |
| Referência da chamada anterior que era referência | FR-3619 | `ec::test_a_referencia_aponta_a_origem_e_nunca_outra_referencia` |
| Item que não existia na chamada anterior | FR-3619 | `ec::test_a_chamada_nova_aproveita_o_que_nao_estava_pendente_sem_copia` (pendente e a apresentar) |
| Requerimento depois do vencimento | FR-3622 | `pz::test_depois_do_vencimento_o_requerimento_nao_se_abre_nem_se_envia` |
| Requerimento da inscrição atualizado na chamada | FR-3622 | `pz` (o sucessor passa pela mesma recusa em `autorizacao_para_atualizar`) |
| Convocação para regularizar | FR-3622 | chamada nova, com prazo próprio: `pz::test_a_correcao_com_vencimento_novo_reabre` (mesma regra) |
| Retificação depois da convocação | FR-3573 | a lista cita a versão em que nasceu: `dc::test_a_raiz_da_chamada_grava_um_item_por_documento_da_convocacao` |
| Envio duplicado | FR-3581 | `dc::test_o_mesmo_arquivo_de_novo_nao_cria_versao` |
| Arquivo inválido | FR-3582 | `dc::test_o_arquivo_invalido_e_recusado_com_as_recusas_da_inscricao` |
| Envio depois do vencimento | FR-3582, FR-3622 | `dc::test_depois_do_vencimento_a_apresentacao_e_recusada_e_nada_e_gravado` |
| Envio antes da comunicação | FR-3578 | `dc::test_antes_do_envio_da_comunicacao_a_apresentacao_e_aceita` |
| Convocação sem vencimento | FR-3578 | `prazo.decorrido` devolve falso sem vencimento (`unit/convocacao` da `019`); `pz::test_sem_a_comunicacao_o_prazo_nao_corre` |
| Conferência sobre versão superada | FR-3587 | `dc::test_conferencia_sobre_versao_superada_e_recusada` |
| Conferência depois do desfecho | FR-3588 | `conferir` recusa `chamada_fechada`; a página não oferece o formulário com desfecho (`pode_conferir`) |
| "Conforme" sem abrir | FR-3611 | `dc::test_conforme_exige_ter_aberto_a_versao_vigente` |
| Obrigatório "não se aplica" | FR-3592 | `dc::test_nao_se_aplica_sem_apresentacao_com_motivo` (estado atendido) |
| Facultativo não conferido | FR-3592 | `LeituraDocumental.facultativos_sem_conferencia`; advertência na página |
| Aproveitado sem documento na inscrição | FR-3576 | `dc::test_sem_o_certificado_na_inscricao_o_item_nasce_a_apresentar` |
| Divergência de hash | FR-3605 | mesmo caminho do `INTEGRIDADE` da `009` em `documento_da_convocacao` |
| Membro alocado inativado | FR-3597 | `al::test_a_revogacao_e_a_saida_da_comissao_tiram_o_alcance_na_hora` |
| Edital encerrado com convocação em aberto | FR-3616 | `dc::test_edital_encerrado_com_convocacao_em_aberto_continua_recebendo_e_conferindo` |
| Duas inscrições em Editais distintos | FR-3576 | a referência é da mesma inscrição, e o gatilho recusa a de outra: `dc::test_a_referencia_a_documento_de_outra_inscricao_e_recusada_pelo_banco` |
| Pendente e aceite tentado | FR-3592 | `dc::test_o_aceite_espera_os_obrigatorios_conferidos` |
| Acesso indevido | FR-3595 a FR-3600 | `mx` inteiro; `pt::test_outro_candidato_nao_alcanca_nem_a_lista_nem_o_arquivo` |
