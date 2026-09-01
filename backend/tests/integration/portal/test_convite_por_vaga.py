"""O convite por vaga, e a retomada (US1 e US3 da 009, FR-016, FR-029).

O convite é o que liga a página pública à jornada: quem chega pela vaga já começa com o Perfil
escolhido, e não é levado a escolhê-lo de novo. Quem volta encontra `Continuar inscrição` — a
mesma inscrição, e não uma segunda.
"""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.edital import identificador
from tests.fixtures.selecao import publicar_selecao, rascunho_de_selecao

PERFIL_DOCENTE = identificador(401, 0)


@pytest.fixture
def provedor_ligado():
    """Não liga mais nada: a identificação por declaração deixou de existir na 010.

    A *fixture* sobrevive porque os testes abaixo a pedem, e removê-la seria reescrever o que eles
    afirmam sobre a jornada — que continua valendo.
    """


def _publicar(api_client, manager_headers, process_payload, *, aberto=True):
    agora = timezone.now()
    inicio = agora - timedelta(days=1) if aberto else agora + timedelta(days=5)
    rascunho = rascunho_de_selecao()
    rascunho["schedule"][0]["startAt"] = inicio.isoformat()
    rascunho["schedule"][0]["endAt"] = (inicio + timedelta(days=10)).isoformat()
    rascunho["schedule"][0]["isRegistrationPeriod"] = True
    return publicar_selecao(api_client, manager_headers, process_payload, rascunho=rascunho)


def _identificar(client):
    from tests.fixtures.candidato import MARIA, identificar

    identificar(client, MARIA)


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_com_o_periodo_aberto_cada_perfil_convida(
    client, provedor_ligado, api_client, manager_headers, process_payload
):
    edital = _publicar(api_client, manager_headers, process_payload)

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    assert "Inscrever-se nesta vaga" in corpo
    assert reverse("portal:inscrever", args=[edital.id, PERFIL_DOCENTE]) in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_fora_do_periodo_nao_ha_convite(
    client, provedor_ligado, api_client, manager_headers, process_payload
):
    edital = _publicar(api_client, manager_headers, process_payload, aberto=False)

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    assert "Inscrever-se nesta vaga" not in corpo
    assert "Inscrições começam em" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_convite_leva_a_inscricao_com_aquele_perfil(
    client, provedor_ligado, api_client, manager_headers, process_payload
):
    """SC-003: quem chegou pelo convite de um Perfil não escolhe Perfil nenhum."""
    edital = _publicar(api_client, manager_headers, process_payload)
    _identificar(client)

    resposta = client.post(reverse("portal:inscrever", args=[edital.id, PERFIL_DOCENTE]))

    inscricao = Inscricao.objects.get()
    assert resposta["Location"] == reverse("portal:inscricao", args=[inscricao.id])
    assert str(inscricao.profile_id) == PERFIL_DOCENTE
    corpo = client.get(resposta["Location"]).content.decode()
    assert "Professor de Informática" in corpo
    assert "<select" not in corpo.split("Seus dados")[0], "nenhuma escolha de Perfil é oferecida"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_sem_identidade_o_convite_leva_a_identificacao_e_volta(
    client, provedor_ligado, api_client, manager_headers, process_payload
):
    edital = _publicar(api_client, manager_headers, process_payload)
    vaga = reverse("portal:inscrever", args=[edital.id, PERFIL_DOCENTE])

    resposta = client.post(vaga)

    assert resposta["Location"] == f"{reverse('portal:acesso')}?destino={vaga}"
    assert Inscricao.objects.count() == 0, "sem identidade, nada é criado"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_quem_ja_comecou_encontra_continuar_inscricao(
    client, provedor_ligado, api_client, manager_headers, process_payload
):
    edital = _publicar(api_client, manager_headers, process_payload)
    _identificar(client)
    client.post(reverse("portal:inscrever", args=[edital.id, PERFIL_DOCENTE]))

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    assert "Continuar inscrição" in corpo
    assert corpo.count("Inscrever-se nesta vaga") == 1, "só o outro Perfil ainda convida"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_pagina_publica_nao_revela_inscricao_de_terceiro(
    client, provedor_ligado, api_client, manager_headers, process_payload
):
    """Sem identidade a consulta nem acontece: a página pública continua pública."""
    edital = _publicar(api_client, manager_headers, process_payload)
    _identificar(client)
    client.post(reverse("portal:inscrever", args=[edital.id, PERFIL_DOCENTE]))
    client.post(reverse("portal:sair"))

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    assert "Continuar inscrição" not in corpo
