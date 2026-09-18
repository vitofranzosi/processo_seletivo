# O "antes" de `tests/authorization` — T002

Registrado **antes de qualquer mudança**, e versionado junto do inventário porque a `T032` é o
portão que decide se a feature entra: um "antes" que mora só em `/tmp` some numa reinicialização, e
aí o critério da `SC-168` deixa de ser refazível por quem revisa o PR.

A leitura é por AST, e não por `grep`: cada asserção é registrada com o caso em que mora, e as
marcadas `STATUS` são as que contêm literal inteiro — as únicas que a feature podia tocar. As demais
são a asserção de **quem entra**, e o diff delas tem de ser vazio.

```text
T002 — o estado de tests/authorization ANTES da 033.

Arquivos: 39
Casos:    197
Asserções: 371

As linhas marcadas STATUS contêm literal inteiro — é onde 404 pode virar 403.
As demais são a asserção de QUEM entra, e não podem mudar (SC-168).

=== tests/authorization/test_acesso_a_etapa.py (7 casos) ===
  test_a_etapa_alocada_abre  (linha 25)
      STATUS | assert client.get(url(edital_a, etapa_a1)).status_code == 200
  test_a_etapa_vizinha_do_mesmo_edital_devolve_404  (linha 31)
      STATUS | assert client.get(url(edital_a, etapa_a2)).status_code == 404
  test_a_etapa_de_outro_processo_devolve_404  (linha 40)
      STATUS | assert client.get(url(edital_b, etapa_b1)).status_code == 404
  test_uuid_adulterado_devolve_404  (linha 48)
      STATUS | assert resposta.status_code == 404
  test_escopo_alheio_devolve_404  (linha 57)
      STATUS | assert client.get(url(edital_a, etapa_a1)).status_code == 404
  test_privilegio_administrativo_nao_injeta_etapa_em_minhas_etapas  (linha 63)
             | assert "Você não possui Etapas atribuídas" in corpo
  test_remover_a_alocacao_revoga_o_acesso_na_hora  (linha 74)
      STATUS | assert client.get(url(edital_a, etapa_a1)).status_code == 200
      STATUS | assert client.get(url(edital_a, etapa_a1)).status_code == 404
             | assert "Você não possui Etapas atribuídas" in corpo

=== tests/authorization/test_acesso_sem_prova.py (8 casos) ===
  test_informar_o_endereco_alheio_e_abrir_o_convite_nao_da_sessao  (linha 29)
             | assert not autenticado(client), "entrou sem provar o controle do endereço"
             | assert resposta["Location"] == reverse("portal:acesso")
             | assert not CandidateIdentity.objects.filter(credenciais__email_canonico=DA_VITIMA).exists()
             | assert not CandidateEmail.objects.filter(email_canonico=DA_VITIMA).exists()
  test_o_convite_tambem_nao_cede_por_post  (linha 41)
             | assert not autenticado(client), corpo
             | assert resposta["Location"] == reverse("portal:acesso")
  test_um_identificador_de_desafio_forjado_na_sessao_nao_serve  (linha 50)
             | assert not autenticado(client)
             | assert resposta["Location"] == reverse("portal:acesso")
  test_um_desafio_real_mas_nao_consumido_tambem_nao_serve  (linha 63)
             | assert desafio.consumido_em is None
             | assert not autenticado(client)
             | assert resposta["Location"] == reverse("portal:acesso")
  test_a_area_pessoal_nao_se_alcanca_por_fora  (linha 80)
      STATUS | assert resposta.status_code == 302, rota
             | assert resposta["Location"] == reverse("portal:acesso"), rota
  test_a_retomada_nao_se_alcanca_por_fora  (linha 88)
             | assert resposta["Location"] == reverse("portal:acesso")
             | assert not autenticado(client)
  test_nenhuma_rota_do_acesso_concede_nada_sem_prova  (linha 108)
             | assert not autenticado(client), f"{metodo} {rota}"
      STATUS | assert resposta.status_code in (302, 404), f"{metodo} {rota} -> {resposta.status_code}"
             | assert not CandidateEmail.objects.filter(email_canonico=DA_VITIMA).exists()
             | assert resposta["Location"] == reverse("portal:acesso"), f"{metodo} {rota}"
  test_a_tela_do_codigo_sozinha_nao_autentica  (linha 126)
      STATUS | assert resposta.status_code == 200
             | assert not autenticado(client)

=== tests/authorization/test_anexos.py (7 casos) ===
  test_o_artefato_nao_publicado_nao_tem_endereco_publico  (linha 30)
      STATUS | assert api_client.get(reverse("public-anexo", args=[artefato.id])).status_code == 404
  test_o_artefato_publicado_dispensa_identificacao  (linha 37)
      STATUS | assert api_client.get(reverse("public-anexo", args=[artefato.id])).status_code == 200
  test_quem_elabora_alcanca_o_artefato_do_rascunho  (linha 45)
      STATUS | assert resposta.status_code == 200
             | assert resposta["Cache-Control"].startswith("no-store")
  test_quem_homologa_alcanca_o_artefato_do_rascunho  (linha 61)
      STATUS | assert resposta.status_code == 200
  test_sem_identificacao_o_artefato_do_rascunho_nao_e_entregue  (linha 75)
      STATUS | assert resposta.status_code in (302, 403, 404)
      STATUS | assert resposta.status_code != 200
  test_ator_autenticado_sem_a_capacidade_nao_recebe_os_bytes  (linha 91)
      STATUS | assert resposta.status_code == 404
  test_a_classificacao_so_e_oferecida_a_quem_pode_abri_la  (linha 114)
             | assert "/marcos/" in de_quem_audita, "quem audita lê o marco, e a tela precisa oferecê-lo"
             | assert "/marcos/" not in de_quem_julga, (         "quem julga recursos recebe 404 no marco; a tela não pode convidá-lo para lá"     )

=== tests/authorization/test_arquivo_do_candidato.py (5 casos) ===
  test_a_titular_ve_o_que_enviou  (linha 32)
      STATUS | assert resposta.status_code == 200
             | assert resposta.headers["Content-Type"] == "application/pdf"
             | assert "inline" in resposta.headers["Content-Disposition"]
             | assert "no-store" in resposta.headers["Cache-Control"]
  test_outro_candidato_nao_alcanca_o_arquivo  (linha 49)
      STATUS | assert resposta.status_code == 404
             | assert b"%PDF" not in resposta.content
  test_sem_identidade_o_arquivo_nao_e_entregue  (linha 62)
      STATUS | assert resposta.status_code == 404
  test_requisito_sem_arquivo_recusa_como_inexistente  (linha 77)
      STATUS | assert resposta.status_code == 404
  test_o_arquivo_nao_tem_endereco_publico  (linha 89)

=== tests/authorization/test_auditoria_api.py (8 casos) ===
  test_audit_query_denies_by_default  (linha 21)
      STATUS | assert negado.status_code == 403
             | assert negado.json()["code"] == "forbidden"
      STATUS | assert api_client.get(URL).status_code == 401
  test_audit_query_returns_events_of_the_actor_scope  (linha 30)
      STATUS | assert response.status_code == 200
             | assert set(body) == {"items", "nextCursor"}
             | assert body["items"], "o fluxo de publicação deve ter gerado auditoria"
             | assert set(primeiro) == {         "eventId",         "occurredAt",         "actorSubject",         "permission",         "operation",         "aggregateType",         "aggregateId",         "previousState",         "newState",         "previousRevision",         "newRevision",         "reason",         "correlationId",     }
  test_audit_query_never_exposes_idempotency_keys_or_content  (linha 56)
             | assert RegistroAuditoria.objects.exclude(idempotency_key="").exists()
             | assert "idempotency" not in corpo.lower()
             | assert "content" not in corpo.lower()
             | assert chave not in corpo
  test_audit_query_does_not_cross_institutional_scope  (linha 71)
             | assert RegistroAuditoria.objects.filter(institution_scope="cefor").exists()
      STATUS | assert response.status_code == 200
             | assert response.json()["items"] == []
  test_audit_query_filters_by_aggregate  (linha 87)
      STATUS | assert response.status_code == 200
             | assert itens
             | assert {item["aggregateType"] for item in itens} == {"ProcessoSeletivo"}
             | assert {item["aggregateId"] for item in itens} == {str(processo.id)}
  test_audit_query_paginates_newest_first_without_repeating  (linha 103)
      STATUS | assert len(todos) > 2
      STATUS | assert instantes == sorted(instantes, reverse=True)
      STATUS | assert len(primeira["items"]) == 2
             | assert primeira["nextCursor"]
             | assert segunda["nextCursor"] is None
             | assert primeira["items"] + segunda["items"] == todos
  test_audit_query_rejects_limit_outside_the_contract  (linha 124)
      STATUS | assert response.status_code == 400
             | assert response.json()["code"] == "invalid_limit"
  test_audit_query_rejects_corrupted_cursor  (linha 132)
      STATUS | assert response.status_code == 400
             | assert response.json()["code"] == "invalid_cursor"

=== tests/authorization/test_classificacao.py (6 casos) ===
  test_gestao_e_auditoria_consultam  (linha 47)
      STATUS | assert client.get(_consulta(edital_com_marco)).status_code == 200
  test_auditoria_consulta_e_nao_emite  (linha 52)
      STATUS | assert client.get(_consulta(edital_com_marco)).status_code == 200
      STATUS | assert (         client.post(_emissao(edital_com_marco), {"chave_idempotencia": "auditor"}).status_code         == 404     )
      STATUS | assert AtoDeOrdenacao.objects.count() == 0
  test_sem_base_recebe_404_uniforme  (linha 62)
      STATUS | assert client.get(_consulta(edital_com_marco)).status_code == 404
      STATUS | assert (         client.post(_emissao(edital_com_marco), {"chave_idempotencia": "intruso"}).status_code         == 404     )
      STATUS | assert AtoDeOrdenacao.objects.count() == 0
  test_outro_escopo_recebe_404_uniforme  (linha 72)
      STATUS | assert client.get(_consulta(edital_com_marco)).status_code == 404
      STATUS | assert (         client.post(_emissao(edital_com_marco), {"chave_idempotencia": "fora"}).status_code == 404     )
      STATUS | assert AtoDeOrdenacao.objects.count() == 0
  test_o_formulario_nao_aceita_a_ordem_do_navegador  (linha 81)
             | assert 'name="chave_idempotencia"' in corpo
             | assert str(PROFILE_ID) not in corpo or "profile_id" not in corpo
             | assert f'name="{campo}"' not in corpo
  test_fato_usado_no_desempate_so_aparece_para_gestao_e_auditoria  (linha 90)
      STATUS | assert autorizada.status_code == 200
             | assert str(segredo) in autorizada.content.decode()
             | assert "private" in autorizada.headers["Cache-Control"]
      STATUS | assert negada.status_code == 404
             | assert str(segredo) not in negada.content.decode()

=== tests/authorization/test_consolidacao.py (4 casos) ===
  test_quem_preside_consolida  (linha 44)
      STATUS | assert tentar(pronto, ator_institucional("maria"), chave="p1")["feitas"] == 1
  test_o_avaliador_alocado_nao_consolida  (linha 48)
      STATUS | assert recusa.value.status == 404
      STATUS | assert ResultadoEtapa.objects.count() == 0
  test_a_auditoria_le_e_nao_consolida  (linha 56)
      STATUS | assert recusa.value.status == 404
  test_ator_de_outro_escopo_institucional_recebe_a_resposta_uniforme  (linha 63)
      STATUS | assert recusa.value.status == 404

=== tests/authorization/test_consulta_administrativa.py (6 casos) ===
  test_papel_sem_a_permissao_nao_alcanca_a_lista  (linha 37)
      STATUS | assert resposta.status_code == 403
  test_o_gestor_alcanca  (linha 48)
      STATUS | assert client.get(reverse("interface:inscricoes", args=[selecao.id])).status_code == 200
  test_sem_permissao_o_detalhe_e_o_arquivo_tambem_sao_recusados  (linha 57)
      STATUS | assert detalhe.status_code == 403
      STATUS | assert arquivo.status_code == 403
             | assert b"%PDF" not in arquivo.content
  test_escopo_institucional_diferente_nao_enxerga  (linha 73)
      STATUS | assert lista.status_code == 404
      STATUS | assert detalhe.status_code == 404
  test_sem_identificar_se_a_consulta_leva_a_identificacao  (linha 87)
      STATUS | assert resposta.status_code == 302
             | assert reverse("interface:identificar") in resposta["Location"]
  test_o_candidato_nao_alcanca_a_consulta_administrativa  (linha 98)
      STATUS | assert resposta.status_code == 302, "a gestão manda identificar-se"

=== tests/authorization/test_consulta_de_resultado.py (6 casos) ===
  test_presidencia_e_auditoria_consultam  (linha 34)
      STATUS | assert client.get(consulta(cenario)).status_code == 200
  test_a_auditoria_nao_ganha_o_botao_de_consolidar  (linha 39)
      STATUS | assert resposta.status_code in (302, 404)
      STATUS | assert ResultadoEtapa.objects.count() == 0
  test_quem_nao_tem_nada_recebe_a_resposta_uniforme  (linha 55)
      STATUS | assert client.get(consulta(cenario)).status_code == 404
  test_a_auditoria_le_o_resultado_e_nao_alcanca_a_ocorrencia  (linha 69)
      STATUS | assert client.get(consulta(cenario)).status_code == 200
      STATUS | assert client.get(ocorrencia(cenario)).status_code == 404
      STATUS | assert resposta.status_code == 404
      STATUS | assert ResultadoEtapa.objects.count() == 0
  test_a_presidencia_alcanca_a_ocorrencia  (linha 89)
      STATUS | assert client.get(ocorrencia(cenario)).status_code == 200
  test_quem_nao_tem_nada_recebe_a_uniforme_na_ocorrencia  (linha 94)
      STATUS | assert client.get(ocorrencia(cenario)).status_code == 404

=== tests/authorization/test_consulta_publica.py (6 casos) ===
  test_public_consultation_needs_no_credentials  (linha 24)
      STATUS | assert api_client.get(url).status_code == 200, url
  test_unpublished_retification_is_not_revealed_to_the_public  (linha 39)
      STATUS | assert api_client.get(f"/api/v1/public/retificacoes/{rascunho.id}").status_code == 404
      STATUS | assert vigente["content"]["profiles"][0]["immediateVacancies"] == 1
             | assert str(rascunho.id) not in [item["id"] for item in historico["items"]]
  test_public_projection_never_exposes_elaboration_identifiers  (linha 62)
             | assert str(revisao.id) not in corpo
             | assert "prepared_by" not in corpo and "preparedBy" not in corpo
             | assert "revisao" not in corpo and "revisionId" not in corpo
             | assert publicacao.published_by not in corpo
  test_public_projection_never_exposes_audit_trail  (linha 76)
             | assert RegistroAuditoria.objects.exists()
             | assert "correlation" not in corpo.lower()
             | assert "homologated_by" not in corpo and "homologatedBy" not in corpo
             | assert str(registro.event_id) not in corpo
  test_public_endpoints_reject_write_attempts  (linha 98)
      STATUS | assert api_client.post(url, {}, format="json").status_code == 405, url
      STATUS | assert api_client.delete(url).status_code == 405, url
  test_public_query_does_not_reveal_editais_from_another_edital  (linha 110)
      STATUS | assert response.status_code == 404
             | assert response.json()["code"] == "no_effective_version"
             | assert historico["items"] == []

=== tests/authorization/test_demonstracao_de_seguranca.py (6 casos) ===
  test_caso_1_trocar_o_identificador_nao_alcanca_nada_de_outro  (linha 82)
      STATUS | assert client.get(endereco).status_code == 404, endereco
  test_caso_2_conhecer_o_cpf_alheio_nao_da_acesso  (linha 100)
             | assert "Você ainda não possui inscrições" in corpo
             | assert str(de_maria.id) not in corpo
             | assert do_atacante.cpf_normalizado == "", "nenhum vínculo com o CPF de ninguém"
      STATUS | assert client.get(reverse("portal:inscricao", args=[de_maria.id])).status_code == 404
  test_caso_3_agir_antes_nao_reserva_o_cpf_alheio  (linha 119)
             | assert de_maria.status == Inscricao.Status.SUBMETIDA, "a legítima não é recusada"
             | assert de_maria.identity_subject == MARIA.subject
  test_caso_4_quem_controla_a_caixa_hoje_entra_na_propria_identidade  (linha 150)
             | assert "Você ainda não possui inscrições" in corpo
             | assert Inscricao.objects.get(identity_subject=legada.subject), "a legada segue intacta"
  test_caso_5_recusar_por_engano_e_retomar  (linha 185)
             | assert "Você ainda não possui inscrições" not in corpo
             | assert CandidateEmail.objects.get(email_canonico="maria@antiga.test").identidade_id == (         legada.pk     )
  test_caso_6_a_sessao_conhecida_nao_vale_depois_do_acesso  (linha 226)
             | assert client.session.session_key != conhecida
             | assert identidade_do_candidato.CHAVE_SESSAO in client.session

=== tests/authorization/test_distribuicao.py (7 casos) ===
  test_quem_gere_a_comissao_alcanca  (linha 31)
      STATUS | assert client.get(tela).status_code == 200
  test_a_presidencia_alcanca_pela_propria_presidencia  (linha 37)
      STATUS | assert client.get(tela).status_code == 200
  test_quem_apenas_atua_na_etapa_nao_distribui  (linha 46)
      STATUS | assert client.get(tela).status_code == 404
  test_quem_nao_tem_vinculo_nenhum_recebe_inexistente  (linha 53)
      STATUS | assert client.get(tela).status_code == 404
  test_etapa_de_outro_edital_nao_e_alcancavel  (linha 59)
      STATUS | assert resposta.status_code == 404
  test_escopo_institucional_divergente_e_inexistente  (linha 70)
      STATUS | assert client.get(tela).status_code == 404
  test_a_distribuicao_por_post_tambem_e_recusada  (linha 78)
      STATUS | assert resposta.status_code == 404
      STATUS | assert Atribuicao.objects.count() == 0

=== tests/authorization/test_documento_da_mesa.py (7 casos) ===
  test_o_atribuido_abre_a_inscricao_e_o_documento  (linha 58)
      STATUS | assert (         client.get(pagina(edital_com_documentos, etapa_a1, cenario["do_joao"])).status_code == 200     )
      STATUS | assert (         abrir(client, arquivo(edital_com_documentos, etapa_a1, cenario["do_joao"])).status_code         == 200     )
  test_inscricao_de_outro_avaliador_e_inexistente  (linha 72)
      STATUS | assert client.get(pagina(edital_com_documentos, etapa_a1, cenario["da_ana"])).status_code == 404
      STATUS | assert (         abrir(client, arquivo(edital_com_documentos, etapa_a1, cenario["da_ana"])).status_code         == 404     )
  test_alocado_sem_atribuicao_nao_abre_inscricao_alguma  (linha 85)
      STATUS | assert (         client.get(pagina(edital_com_documentos, etapa_a1, cenario["do_joao"])).status_code == 404     )
      STATUS | assert (         abrir(client, arquivo(edital_com_documentos, etapa_a1, cenario["do_joao"])).status_code         == 404     )
  test_remover_a_alocacao_revoga_o_acesso_ao_documento  (linha 113)
      STATUS | assert (         abrir(client, arquivo(edital_com_documentos, etapa_a1, cenario["do_joao"])).status_code         == 200     )
      STATUS | assert (         client.get(pagina(edital_com_documentos, etapa_a1, cenario["do_joao"])).status_code == 404     )
      STATUS | assert (         abrir(client, arquivo(edital_com_documentos, etapa_a1, cenario["do_joao"])).status_code         == 404     )
  test_escopo_divergente_e_inexistente  (linha 140)
      STATUS | assert (         client.get(pagina(edital_com_documentos, etapa_a1, cenario["do_joao"])).status_code == 404     )
  test_quem_gere_a_comissao_nao_alcanca_a_mesa_de_outro  (linha 150)
      STATUS | assert (         client.get(pagina(edital_com_documentos, etapa_a1, cenario["do_joao"])).status_code == 404     )
  test_etapa_de_outro_edital_nao_alcanca_a_inscricao  (linha 161)
      STATUS | assert resposta.status_code == 404

=== tests/authorization/test_eixos_de_identidade.py (2 casos) ===
  test_sessao_de_candidato_nao_alcanca_as_rotas_da_comissao  (linha 43)
      STATUS | assert resposta.status_code in (302, 404), f"{rota} devolveu {resposta.status_code}"
             | assert "identificar" in resposta["Location"]
  test_membro_da_comissao_nao_ganha_ownership_sobre_inscricao  (linha 56)
      STATUS | assert e_titular(inscricao, IdentidadeDoMembro()) is False

=== tests/authorization/test_finalizacao.py (5 casos) ===
  test_final_acts_deny_by_default  (linha 27)
      STATUS | assert response.status_code == 403
             | assert response.json()["code"] == "forbidden"
             | assert Edital.objects.get(pk=edital_publicado.pk).status == Edital.Status.PUBLICADO
  test_final_acts_do_not_cross_institutional_scope  (linha 46)
      STATUS | assert response.status_code == 404
             | assert Edital.objects.get(pk=edital_publicado.pk).status == Edital.Status.PUBLICADO
  test_final_act_audits_actor_reason_and_state_transition  (linha 65)
             | assert registro.actor_subject == "gestor"
             | assert registro.permission == "edital:encerrar"
             | assert registro.previous_state == Edital.Status.PUBLICADO
             | assert registro.new_state == Edital.Status.ENCERRADO
             | assert registro.previous_revision == edital_publicado.revision
      STATUS | assert registro.new_revision == edital_publicado.revision + 1
             | assert registro.reason == "Etapas concluídas"
  test_finalization_preserves_publications_and_history  (linha 85)
             | assert depois == antes
             | assert any(item["kind"] == "PUBLICACAO" for item in historico["items"])
  test_finalized_process_blocks_new_changes_to_its_editais  (linha 106)
             | assert ProcessoSeletivo.objects.get(pk=processo.pk).status == ProcessoSeletivo.Status.CANCELADO
      STATUS | assert bloqueado.status_code == 409
             | assert bloqueado.json()["code"] == "invalid_state"
             | assert AtoAdministrativo.objects.filter(aggregate_id=edital.id).exists()

=== tests/authorization/test_foundation.py (4 casos) ===
  test_anonymous_is_denied  (linha 6)
      STATUS | assert response.status_code == 401
             | assert response["Content-Type"].startswith("application/problem+json")
  test_missing_permission_is_denied  (linha 19)
      STATUS | assert response.status_code == 403
  test_idempotency_replays_and_rejects_changed_payload  (linha 32)
      STATUS | assert first.status_code == 201
      STATUS | assert replay.status_code == 201
             | assert replay.json()["id"] == first.json()["id"]
      STATUS | assert conflict.status_code == 409
  test_activation_requires_if_match  (linha 53)
      STATUS | assert response.status_code == 428

=== tests/authorization/test_gestao_da_comissao.py (6 casos) ===
  test_o_presidente_gere_sem_possuir_a_permissao_sistemica  (linha 23)
      STATUS | assert status == 201 and membro.identity_subject == "ana"
  test_quem_possui_a_permissao_gere_sem_ser_membro  (linha 32)
             | assert not MembroComissao.objects.filter(identity_subject="carlos").exists()
  test_membro_comum_nao_gere  (linha 41)
      STATUS | assert recusa.value.status == 404
  test_presidente_de_outro_processo_nao_gere_este  (linha 48)
      STATUS | assert recusa.value.status == 404
  test_escopo_alheio_responde_como_inexistente  (linha 58)
      STATUS | assert recusa.value.status == 404
  test_membro_de_outro_processo_nao_e_alcancavel_pelo_identificador  (linha 68)
      STATUS | assert recusa.value.status == 404

=== tests/authorization/test_idor_area.py (6 casos) ===
  test_a_inscricao_de_outro_responde_404  (linha 57)
      STATUS | assert client.get(reverse("portal:inscricao", args=[do_joao.id])).status_code == 404
  test_o_documento_de_outro_responde_404  (linha 62)
      STATUS | assert resposta.status_code == 404
  test_baixar_o_documento_de_outro_tambem_responde_404  (linha 70)
      STATUS | assert client.get(f"{endereco}?baixar=1").status_code == 404
  test_o_comprovante_de_outro_responde_404  (linha 76)
      STATUS | assert client.get(reverse(rota, args=[do_joao.id])).status_code == 404, rota
  test_a_recusa_e_indistinguivel_da_inexistente  (linha 89)
      STATUS | assert alheia.status_code == inexistente.status_code == 404
             | assert _sem_csrf(alheia.content) == _sem_csrf(inexistente.content)
  test_sem_sessao_nada_e_alcancavel  (linha 100)
      STATUS | assert client.get(reverse(rota, args=args)).status_code == 404, rota

=== tests/authorization/test_impedimento_superveniente.py (3 casos) ===
  test_a_pessoa_impedida_nao_alcanca_a_inscricao_que_fundamentou_o_resultado  (linha 55)
      STATUS | assert client.get(url).status_code == 404
  test_a_mesa_da_pessoa_impedida_fica_vazia  (linha 70)
      STATUS | assert resposta.status_code == 200
             | assert impedido_depois["inscricao"].protocolo not in resposta.content.decode()
  test_o_resultado_permanece_e_a_consulta_declara_a_contestacao  (linha 81)
      STATUS | assert resposta.status_code == 200
             | assert "Origem contestada depois da consolidação" in corpo
      STATUS | assert ResultadoEtapa.objects.filter(inscricao=impedido_depois["inscricao"]).count() == 1

=== tests/authorization/test_inscricao_alheia.py (3 casos) ===
  test_a_inscricao_alheia_responde_404  (linha 34)
      STATUS | assert client.get(reverse("portal:inscricao", args=[de_joao.id])).status_code == 404
  test_a_recusa_e_indistinguivel_da_inexistente  (linha 39)
      STATUS | assert alheia.status_code == inexistente.status_code == 404
  test_a_inscricao_alheia_nao_aparece_na_lista  (linha 48)
             | assert str(de_joao.id) not in corpo

=== tests/authorization/test_julgamento_de_recurso.py (13 casos) ===
  test_quem_tem_a_capacidade_julga  (linha 96)
             | assert juizo.admitido
             | assert juizo.decidido_por == JULGADORA
  test_sem_a_capacidade_e_403  (linha 104)
             | assert recusa.value.code == "forbidden"
      STATUS | assert recusa.value.status == 403
             | assert not JuizoDeAdmissibilidade.objects.exists()
  test_presidir_a_comissao_nao_concede_julgamento  (linha 113)
             | assert recusa.value.code == "forbidden"
  test_a_lista_nao_e_alcancavel_sem_a_capacidade  (linha 127)
      STATUS | assert resposta.status_code == 403
  test_a_peca_nao_e_alcancavel_sem_a_capacidade  (linha 136)
      STATUS | assert resposta.status_code == 403
  test_o_papel_julgador_alcanca_a_lista  (linha 144)
      STATUS | assert resposta.status_code == 200
             | assert "REC-2026-US30001" in resposta.content.decode()
  test_quem_concluiu_a_avaliacao_fonte_e_recusado  (linha 159)
             | assert recusa.value.code == BARRADO
      STATUS | assert recusa.value.status == 403
             | assert "Avaliação" in recusa.value.detail
  test_quem_consolidou_o_resultado_e_recusado  (linha 171)
             | assert recusa.value.code == BARRADO
             | assert "consolidou" in recusa.value.detail
  test_quem_emitiu_o_ato_atacado_e_recusado  (linha 182)
             | assert recusa.value.code == BARRADO
             | assert "emitiu" in recusa.value.detail
  test_quem_publicou_e_recusado  (linha 193)
             | assert recusa.value.code == BARRADO
             | assert "publicação" in recusa.value.detail
  test_o_impedimento_declarado_da_012_tambem_recusa  (linha 203)
             | assert recusa.value.code == BARRADO
             | assert "impedimento declarado" in recusa.value.detail
  test_o_impedimento_e_nomeado_na_tela_antes_de_qualquer_botao  (linha 222)
             | assert "Você não pode julgar este recurso" in corpo
             | assert "consolidou" in corpo
             | assert "Não admitir" not in corpo, "o botão não é oferecido a quem está impedido"
  test_sem_impedimento_a_tela_oferece_a_apreciacao  (linha 233)
             | assert "Você não pode julgar este recurso" not in corpo
             | assert "Não admitir" in corpo

=== tests/authorization/test_listagem_em_lote.py (5 casos) ===
  test_a_mesa_chama_o_guard_no_maximo_uma_vez  (linha 35)
      STATUS | assert len(linhas) == 12
      STATUS | assert guard.call_count == 0, "a Mesa deve usar a forma em lote, e não o guard individual"
  test_a_mesa_nao_cresce_em_chamadas_com_o_numero_de_linhas  (linha 51)
      STATUS | assert guard.call_count == 0
  test_as_duas_formas_nunca_divergem  (linha 65)
             | assert em_lote == uma_a_uma, subject
  test_a_organizacao_do_trabalho_tambem_nao_usa_o_guard  (linha 84)
      STATUS | assert guard.call_count == 0
  test_o_guard_individual_continua_valendo_na_rota_de_uma_inscricao  (linha 100)
      STATUS | assert (         pode_avaliar_inscricao(joao, cenario["edital"], cenario["etapa"], com_trabalho[0].id)         is not None     )
      STATUS | assert (         pode_avaliar_inscricao(ana, cenario["edital"], cenario["etapa"], com_trabalho[0].id) is None     )

=== tests/authorization/test_mesa.py (6 casos) ===
  test_quem_tem_alocacao_e_atribuicao_ve_a_mesa  (linha 47)
      STATUS | assert joao_com_trabalho["inscricoes"][0].protocolo in corpo
  test_alocado_sem_atribuicao_alcanca_a_mesa_vazia  (linha 55)
      STATUS | assert client.get(mesa).status_code == 200
  test_sem_alocacao_a_etapa_e_inexistente  (linha 65)
      STATUS | assert client.get(mesa).status_code == 404
  test_perder_a_alocacao_revoga_o_acesso  (linha 72)
      STATUS | assert client.get(mesa).status_code == 200
      STATUS | assert client.get(mesa).status_code == 404
      STATUS | assert Atribuicao.objects.filter(ativo=True).count() == ativas_antes
  test_devolver_a_alocacao_restaura_as_mesmas_atribuicoes  (linha 96)
      STATUS | assert client.get(mesa).status_code == 404
             | assert inscricao.protocolo in corpo
  test_escopo_divergente_e_inexistente  (linha 129)
      STATUS | assert client.get(mesa).status_code == 404

=== tests/authorization/test_mesa_por_post.py (11 casos) ===
  test_gravar_avaliacao_alheia_e_recusado  (linha 80)
      STATUS | assert resposta.status_code == 404
             | assert not Avaliacao.objects.filter(identity_subject=subject).exists()
  test_concluir_avaliacao_alheia_e_recusado  (linha 93)
      STATUS | assert resposta.status_code == 404
      STATUS | assert Avaliacao.objects.count() == 0
      STATUS | assert ConclusaoAvaliacao.objects.count() == 0
  test_o_atribuido_nao_alcanca_a_inscricao_que_nao_recebeu  (linha 107)
      STATUS | assert resposta.status_code == 404
             | assert not Avaliacao.objects.filter(inscricao_id=cenario["livre"].id).exists()
  test_o_mesmo_corpo_e_aceito_de_quem_tem_a_atribuicao  (linha 117)
      STATUS | assert resposta.status_code == 302
      STATUS | assert Avaliacao.objects.filter(identity_subject="joao").count() == 1
  test_concluir_com_o_mesmo_corpo_e_aceito_de_quem_tem_a_atribuicao  (linha 131)
      STATUS | assert resposta.status_code == 302
             | assert Avaliacao.objects.get(identity_subject="joao").estado == Avaliacao.Estado.CONCLUIDA
  test_remover_atribuicao_por_post_e_recusado  (linha 158)
      STATUS | assert resposta.status_code == 404
      STATUS | assert Atribuicao.objects.get(pk=atribuicao.pk).ativo is True
  test_registrar_impedimento_por_post_e_recusado  (linha 175)
      STATUS | assert resposta.status_code == 404
             | assert not Impedimento.objects.exists()
      STATUS | assert Atribuicao.objects.filter(ativo=True).count() == 1
  test_a_tela_de_impedimentos_nao_e_alcancavel  (linha 199)
      STATUS | assert client.get(rota("interface:impedimentos", cenario)).status_code == 404
  test_reabrir_avaliacao_por_post_e_recusado  (linha 208)
      STATUS | assert resposta.status_code == 404
             | assert Avaliacao.objects.get(pk=avaliacao.pk).estado == Avaliacao.Estado.CONCLUIDA
  test_a_etapa_de_outro_edital_nao_e_alcancavel_nem_por_post  (linha 233)
      STATUS | assert resposta.status_code == 404
      STATUS | assert Avaliacao.objects.count() == 0
  test_sem_sessao_nenhum_post_grava  (linha 251)
      STATUS | assert resposta.status_code == 302
             | assert resposta["Location"] == reverse("interface:identificar")
      STATUS | assert Avaliacao.objects.count() == 0

=== tests/authorization/test_processos.py (1 casos) ===
  test_cross_scope_process_is_not_revealed  (linha 6)
      STATUS | assert response.status_code == 404

=== tests/authorization/test_progressao.py (4 casos) ===
  test_a_mesa_da_etapa_seguinte_nao_lista_a_eliminada  (linha 51)
             | assert com_eliminada["habilitada"].id in listadas
             | assert com_eliminada["eliminada"].id not in listadas
      STATUS | assert contagens["total"] == 1
  test_a_proxima_pendente_nao_oferece_a_eliminada  (linha 64)
             | assert seguinte is None
  test_o_identificador_da_eliminada_nao_alcanca_a_inscricao  (linha 76)
      STATUS | assert client.get(reverse(rota, args=args)).status_code == 404
      STATUS | assert client.get(reverse(rota, args=args)).status_code == 200
  test_a_inscricao_habilitada_continua_alcancavel  (linha 90)
      STATUS | assert client.get(url).status_code == 200

=== tests/authorization/test_publicacao.py (1 casos) ===
  test_one_actor_cannot_prepare_homologate_and_publish  (linha 9)
      STATUS | assert (         api_client.put(             f"/api/v1/admin/editais/{edital.id}/rascunho",             complete_draft(),             format="json",             **{**actor, "HTTP_IF_MATCH": '"1"'},         ).status_code         == 200     )
      STATUS | assert (         api_client.post(             f"/api/v1/admin/editais/{edital.id}/submissoes",             format="json",             **{**actor, "HTTP_IF_MATCH": '"2"'},         ).status_code         == 200     )
      STATUS | assert (         api_client.post(             f"/api/v1/admin/editais/{edital.id}/homologacoes",             {"reason": "Conferido"},             format="json",             **{**actor, "HTTP_IF_MATCH": '"3"'},         ).status_code         == 200     )
      STATUS | assert denied.status_code == 403

=== tests/authorization/test_publicacao_de_resultado.py (7 casos) ===
  test_quem_tem_a_capacidade_abre_a_previa  (linha 54)
      STATUS | assert client.get(_previa(cenario)).status_code == 200
  test_sem_a_capacidade_e_403_na_previa_e_no_ato  (linha 70)
      STATUS | assert client.get(_previa(cenario)).status_code == 403
      STATUS | assert client.post(_confirmar(cenario), {}).status_code == 403
  test_o_presidente_que_emitiu_nao_publica_nem_por_post  (linha 79)
      STATUS | assert resposta.status_code == 403
             | assert not PublicacaoResultado.objects.exists()
  test_escopo_institucional_alheio_e_404  (linha 97)
      STATUS | assert client.get(_previa(cenario)).status_code == 404
      STATUS | assert client.get(_historico(cenario)).status_code == 404
  test_o_historico_e_de_dois_e_publicar_e_de_um  (linha 105)
      STATUS | assert resposta.status_code == 200
      STATUS | assert client.get(_previa(cenario)).status_code == 403
  test_uma_candidata_nao_alcanca_a_situacao_de_outra  (linha 114)
      STATUS | assert resposta.status_code == 404
  test_o_protocolo_publicado_nao_resolve_a_inscricao_sem_autenticacao  (linha 132)
             | assert titular.protocolo in bytes(publicacao.conteudo_publico).decode(), (         "o teste precisa de um protocolo realmente publicado para valer"     )
             | assert com_protocolo == [], (         f"rota pública recebe protocolo como parâmetro: {com_protocolo} — ele identifica, e "         "identificar não é autorizar"     )
             | assert titular.nome not in corpo, f"{nome} devolveu o nome a partir do protocolo publicado"
             | assert titular.email not in corpo
             | assert str(titular.id) not in corpo

=== tests/authorization/test_reaproveitamento.py (5 casos) ===
  test_quem_nao_elabora_nao_copia  (linha 63)
             | assert recusa.value.code in ("forbidden", "permission_denied")
  test_origem_inexistente_fora_do_escopo_e_inelegivel_respondem_igual  (linha 74)
      STATUS | assert len(set(recusas)) == 1, recusas
      STATUS | assert recusas[0][1] == 404
  test_a_fronteira_tem_dois_lados  (linha 101)
             | assert list(origens_elegiveis(elaborador)) == [origem]
             | assert list(origens_elegiveis(elaborador)) == [origem]
      STATUS | assert copiado.perfis.count() == 1
  test_o_destino_de_outro_escopo_nao_e_alcancavel  (linha 117)
      STATUS | assert recusa.value.status == 404
  test_origem_que_nao_e_uuid_e_recusa_de_dominio_e_nao_defeito  (linha 127)
      STATUS | assert recusa.value.status == 404

=== tests/authorization/test_recurso_do_candidato.py (8 casos) ===
  test_a_titular_le_o_proprio_recurso  (linha 58)
      STATUS | assert resposta.status_code == 200
             | assert "REC-2026-AUTH0001" in resposta.content.decode()
  test_o_recurso_alheio_responde_404  (linha 72)
      STATUS | assert resposta.status_code == 404
  test_a_recusa_e_indistinguivel_da_inexistente  (linha 80)
      STATUS | assert alheio.status_code == inexistente.status_code == 404
             | assert "REC-2026-AUTH0001" not in alheio.content.decode()
  test_sem_sessao_nenhuma_o_recurso_nao_abre  (linha 92)
      STATUS | assert resposta.status_code in (302, 404), resposta.status_code
             | assert "REC-2026-AUTH0001" not in resposta.content.decode()
  test_o_protocolo_nao_confere_acesso  (linha 100)
      STATUS | assert resposta.status_code == 404
  test_interpor_na_inscricao_alheia_responde_404  (linha 116)
      STATUS | assert resposta.status_code == 404
  test_interpor_por_post_na_inscricao_alheia_tambem_responde_404  (linha 127)
      STATUS | assert resposta.status_code == 404
      STATUS | assert peca_de_outra_pessoa["dona"].recursos.count() == 1
             | assert alvo.inscricao_id == peca_de_outra_pessoa["dona"].id
  test_recurso_inexistente_responde_404  (linha 146)
      STATUS | assert client.get(reverse("portal:recurso", args=[uuid.uuid4()])).status_code == 404

=== tests/authorization/test_requisito_alheio.py (3 casos) ===
  test_requisito_de_outro_perfil_e_recusado  (linha 29)
      STATUS | assert resposta.status_code == 404
      STATUS | assert DocumentoSubmetido.objects.count() == 0
  test_requisito_de_modalidade_nao_escolhida_e_recusado  (linha 42)
      STATUS | assert resposta.status_code == 404
      STATUS | assert DocumentoSubmetido.objects.count() == 0
  test_requisito_inexistente_e_recusado  (linha 53)
      STATUS | assert resposta.status_code == 404
      STATUS | assert DocumentoSubmetido.objects.count() == 0

=== tests/authorization/test_retificacao_de_anexo.py (3 casos) ===
  test_elaborar_a_substituicao_exige_a_capacidade_de_elaborar  (linha 54)
      STATUS | assert recusa.status_code == 403
  test_cada_ato_da_retificacao_exige_a_sua_propria_capacidade  (linha 81)
      STATUS | assert recusa.status_code == 403, f"{etapa} aceitou quem tem {outras} e não tem {capacidade}"
  test_cancelar_a_retificacao_do_anexo_exige_a_capacidade_de_cancelar  (linha 102)
      STATUS | assert recusa.status_code == 403

=== tests/authorization/test_retificacoes.py (1 casos) ===
  test_retification_requires_explicit_permission  (linha 10)
      STATUS | assert response.status_code == 403

=== tests/authorization/test_rotacao_de_sessao.py (2 casos) ===
  test_o_identificador_de_sessao_muda_ao_entrar  (linha 30)
      STATUS | assert resposta.status_code == 302
             | assert client.session.session_key != antes, "a sessão conhecida continuaria valendo"
  test_a_sessao_anterior_nao_autentica_depois  (linha 42)
             | assert not Session.objects.filter(session_key=antes).exists()

=== tests/authorization/test_sessao_candidata.py (3 casos) ===
  test_a_gestao_nao_reconhece_a_sessao_do_candidato  (linha 28)
      STATUS | assert resposta.status_code == 302
             | assert reverse("interface:identificar") in resposta["Location"]
  test_as_duas_chaves_de_sessao_nao_se_misturam  (linha 35)
             | assert identidade_do_candidato.CHAVE_SESSAO in client.session
             | assert "interface_identidade" not in client.session
  test_o_candidato_entra_no_portal  (linha 40)
      STATUS | assert client.get(reverse("portal:inscricoes")).status_code == 200

=== tests/authorization/test_titularidade.py (6 casos) ===
  test_a_titular_alcanca_a_propria_inscricao  (linha 41)
      STATUS | assert resposta.status_code == 200
  test_outra_identidade_nao_alcanca_a_inscricao_alheia  (linha 51)
      STATUS | assert resposta.status_code == 404
             | assert MARIA.nome not in resposta.content.decode()
  test_sem_identidade_a_inscricao_nao_e_alcancavel  (linha 63)
      STATUS | assert resposta.status_code == 404
  test_ator_institucional_nao_alcanca_a_inscricao_pelo_portal  (linha 72)
      STATUS | assert resposta.status_code == 404
  test_outra_identidade_nao_grava_na_inscricao_alheia  (linha 88)
      STATUS | assert resposta.status_code == 404
             | assert inscricao_de_maria.telefone == ""
  test_o_ator_do_candidato_nao_tem_permissao_nenhuma  (linha 102)
             | assert ator.permissions == frozenset()
      STATUS | assert recusa.value.status == 403

=== tests/authorization/test_titularidade_preservada.py (3 casos) ===
  test_nenhum_desfecho_troca_o_titular  (linha 74)
             | assert titulares() == antes
  test_reconciliar_torna_a_inscricao_visivel_sem_mudar_de_dono  (linha 81)
             | assert "Você ainda não possui inscrições" not in corpo
             | assert titulares() == antes
  test_a_retomada_tambem_nao_troca_o_titular  (linha 91)
             | assert titulares() == antes

=== tests/authorization/test_valores_congelados.py (3 casos) ===
  test_o_valor_congelado_existe_e_pertence_a_quem_o_informou  (linha 72)
             | assert valor.valor_data.isoformat() == "1990-05-20"
             | assert valor.inscricao.identity_subject == MARIA.subject
  test_outro_candidato_nao_alcanca_a_inscricao_alheia  (linha 80)
      STATUS | assert resposta.status_code == 404
             | assert "1990-05-20" not in resposta.content.decode()
  test_quem_nao_se_identificou_nao_alcanca_nada  (linha 90)
      STATUS | assert resposta.status_code in (302, 404)
             | assert "1990-05-20" not in str(resposta.get("Location", ""))
```
