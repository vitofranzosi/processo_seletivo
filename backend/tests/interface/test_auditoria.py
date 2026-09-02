"""Tela de trilha de auditoria (US6 da 002).

Verifica o que a trilha promete a quem responde questionamento: cada ato com ator, instante,
transição e motivo — e o que ela não pode virar, que é via alternativa de leitura do conteúdo.
"""

import pytest
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.processos.models import Edital
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload)


@pytest.mark.django_db
@pytest.mark.integration
def test_trilha_mostra_cada_ato_com_ator_instante_e_transicao(client, seletor_ligado, edital):
    identificar(client, "auditor", ["auditor"])
    corpo = client.get(reverse("interface:auditoria", args=[edital.id])).content.decode()

    assert "Publicação" in corpo
    assert "Homologação" in corpo
    assert "Submissão para revisão" in corpo
    assert "preparador" in corpo and "homologador" in corpo and "publicador" in corpo
    assert "Em revisão → Homologado" in corpo, "a transição de estado precisa ser legível"


@pytest.mark.django_db
@pytest.mark.integration
def test_trilha_mostra_o_motivo_registrado_no_ato(client, seletor_ligado, edital):
    identificar(client, "auditor", ["auditor"])
    corpo = client.get(reverse("interface:auditoria", args=[edital.id])).content.decode()
    assert "OK" in corpo, "o motivo da homologação foi registrado e aparece"


@pytest.mark.django_db
@pytest.mark.integration
def test_trilha_reune_o_edital_e_suas_retificacoes(client, seletor_ligado, api_client, edital):
    """Atos de Retificação são auditados sob o id dela; a trilha do Edital precisa dos dois."""
    from tests.fixtures.publicacao import retify

    retify(
        api_client,
        edital,
        [{"targetPath": "/title", "operation": "REPLACE", "newValue": "Retificado"}],
    )
    identificar(client, "auditor", ["auditor"])
    corpo = client.get(
        reverse("interface:auditoria", args=[edital.id]), {"limit": 100}
    ).content.decode()
    assert corpo.count("Retificação</span>") >= 3, "criar, submeter, homologar e publicar"
    assert "Edital</span>" in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_trilha_exige_permissao_propria(client, seletor_ligado, edital):
    """FR-019: consultar a auditoria é permissão distinta de conduzir o Edital."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    assert client.get(reverse("interface:auditoria", args=[edital.id])).status_code == 403

    corpo = client.get(reverse("interface:detalhe", args=[edital.id])).content.decode()
    assert "trilha de auditoria" not in corpo, "nem é oferecida a quem não pode"


@pytest.mark.django_db
@pytest.mark.integration
def test_trilha_nao_expoe_conteudo_normativo_nem_chave_de_idempotencia(
    client, seletor_ligado, edital
):
    """A trilha não pode virar via alternativa de leitura dos agregados."""
    assert RegistroAuditoria.objects.exclude(idempotency_key="").exists()
    identificar(client, "auditor", ["auditor"])
    corpo = client.get(
        reverse("interface:auditoria", args=[edital.id]), {"limit": 100}
    ).content.decode()

    for chave in RegistroAuditoria.objects.values_list("idempotency_key", flat=True):
        if chave:
            assert chave not in corpo
    assert "immediateVacancies" not in corpo, "conteúdo do Edital não vaza pela auditoria"


@pytest.mark.django_db
@pytest.mark.integration
def test_trilha_nao_cruza_escopo_institucional(client, seletor_ligado, edital):
    identificar(client, "auditor", ["auditor"])
    sessao = client.session
    sessao["interface_identidade"] = {
        "subject": "auditor",
        "escopo": "outra-instituicao",
        "papeis": ["auditor"],
    }
    sessao.save()
    assert client.get(reverse("interface:auditoria", args=[edital.id])).status_code == 404


@pytest.mark.django_db
@pytest.mark.integration
def test_trilha_pagina_do_mais_recente_para_o_mais_antigo(client, seletor_ligado, edital):
    identificar(client, "auditor", ["auditor"])
    primeira = client.get(reverse("interface:auditoria", args=[edital.id]), {"limit": 2})
    assert len(primeira.context["registros"]) == 2
    assert primeira.context["proximo_cursor"], "há mais atos a mostrar"

    instantes = [r["quando"] for r in primeira.context["registros"]]
    assert instantes == sorted(instantes, reverse=True)

    segunda = client.get(
        reverse("interface:auditoria", args=[edital.id]),
        {"limit": 100, "cursor": primeira.context["proximo_cursor"]},
    )
    ids_primeira = {r["quando"] for r in primeira.context["registros"]}
    ids_segunda = {r["quando"] for r in segunda.context["registros"]}
    assert not ids_primeira & ids_segunda, "a página seguinte não repete o que já foi mostrado"


@pytest.mark.django_db
@pytest.mark.integration
def test_edital_sem_atos_registrados_explica_em_vez_de_mostrar_tela_vazia(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    novo = Edital.objects.get()
    identificar(client, "auditor", ["auditor"])
    corpo = client.get(reverse("interface:auditoria", args=[novo.id])).content.decode()
    assert "Nenhum ato registrado" in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_recusa_do_dominio_vira_pagina_e_nao_erro_de_servidor(client, seletor_ligado, edital):
    """O handler do DRF não alcança views comuns; sem isto, uma recusa viraria 500."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.get(reverse("interface:auditoria", args=[edital.id]))

    assert resposta.status_code == 403
    corpo = resposta.content.decode()
    assert "Você não tem permissão para isto" in corpo
    assert "Nenhuma alteração foi feita" in corpo
    assert "Traceback" not in corpo, "detalhe interno não pode chegar à tela"


@pytest.mark.django_db
@pytest.mark.integration
def test_situacao_feminina_da_retificacao_e_traduzida(client, seletor_ligado, api_client, edital):
    """A trilha mostrava 'Em revisão → HOMOLOGADA', misturando texto e código cru."""
    from tests.fixtures.publicacao import retify

    retify(
        api_client,
        edital,
        [{"targetPath": "/title", "operation": "REPLACE", "newValue": "Retificado"}],
    )
    identificar(client, "auditor", ["auditor"])
    corpo = client.get(
        reverse("interface:auditoria", args=[edital.id]), {"limit": 100}
    ).content.decode()
    assert "Homologada" in corpo
    assert "HOMOLOGADA" not in corpo
    assert "PUBLICADA" not in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_a_tela_traduz_a_base_de_autorizacao(
    client, seletor_ligado, gestor, processo_a, comissao_de_a
):
    """L7: `comissao:gerir` é codename — quem lê a trilha precisa da frase."""
    from django.urls import reverse

    identificar(client, "auditora", ["auditor"])

    corpo = client.get(
        reverse("interface:auditoria-comissao", args=[processo_a.id])
    ).content.decode()

    assert "permissão de gerir comissões" in corpo
    assert "comissao:gerir" not in corpo
