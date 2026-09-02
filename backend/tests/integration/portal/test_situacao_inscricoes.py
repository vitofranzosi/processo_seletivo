"""A situação das inscrições vem do Evento designado — e de mais nada (US1, FR-015, FR-017).

Antes da `009`, saber se um Edital recebia inscrição significava ler o Cronograma e interpretar
texto. A designação é dado publicado, e é isso que torna a situação uma leitura em vez de um
palpite sobre o que alguém digitou em `type`.
"""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.selecao import publicar_selecao, rascunho_de_selecao


def _publicar_com_periodo(api_client, manager_headers, process_payload, *, inicio, fim):
    rascunho = rascunho_de_selecao()
    rascunho["schedule"][0]["startAt"] = inicio.isoformat()
    rascunho["schedule"][0]["endAt"] = None if fim is None else fim.isoformat()
    rascunho["schedule"][0]["isRegistrationPeriod"] = True
    return publicar_selecao(api_client, manager_headers, process_payload, rascunho=rascunho)


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_inscricoes_abertas_dizem_ate_quando(client, api_client, manager_headers, process_payload):
    agora = timezone.now()
    edital = _publicar_com_periodo(
        api_client,
        manager_headers,
        process_payload,
        inicio=agora - timedelta(days=1),
        fim=agora + timedelta(days=10),
    )

    for endereco in (reverse("portal:vitrine"), reverse("portal:selecao", args=[edital.id])):
        texto = " ".join(client.get(endereco).content.decode().split())
        assert "Inscrições abertas desde" in texto, endereco
        assert "até" in texto, endereco
        assert "Faltam 9 dias." in texto, "uma data sozinha não diz se dá tempo"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_inscricoes_futuras_dizem_quando_comecam(
    client, api_client, manager_headers, process_payload
):
    agora = timezone.now()
    edital = _publicar_com_periodo(
        api_client,
        manager_headers,
        process_payload,
        inicio=agora + timedelta(days=5),
        fim=agora + timedelta(days=20),
    )

    for endereco in (reverse("portal:vitrine"), reverse("portal:selecao", args=[edital.id])):
        corpo = client.get(endereco).content.decode()
        assert "Inscrições começam em" in corpo, endereco


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_encerrada_continua_consultavel(client, api_client, manager_headers, process_payload):
    """FR-017: a página não desaparece quando o prazo passa — ela muda o que diz."""
    agora = timezone.now()
    edital = _publicar_com_periodo(
        api_client,
        manager_headers,
        process_payload,
        inicio=agora - timedelta(days=30),
        fim=agora - timedelta(days=1),
    )

    resposta = client.get(reverse("portal:selecao", args=[edital.id]))

    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert "Inscrições encerradas em" in corpo
    assert "Professor de Informática" in corpo, "a seleção continua legível depois do prazo"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_sem_evento_designado_a_pagina_nao_fala_de_prazo(
    client, api_client, manager_headers, process_payload
):
    """Ausência de designação não é um quarto estado: é um Edital que não recebe inscrição aqui."""
    edital = publicar_selecao(api_client, manager_headers, process_payload)

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    assert "Inscrições" not in corpo.split("<main")[1]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_situacao_vem_da_marca_e_nao_do_texto_do_evento(
    api_client, manager_headers, process_payload
):
    """O Evento chamado "Inscrições" **sem** a marca não designa período nenhum (FR-002)."""
    edital = publicar_selecao(api_client, manager_headers, process_payload)
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")

    designados = [
        evento for evento in vigente.content["schedule"] if evento.get("isRegistrationPeriod")
    ]

    assert [evento["description"] for evento in vigente.content["schedule"]] == [
        "Período de inscrições"
    ], "o Evento se chama assim, e ainda assim"
    assert designados == [], "não designa período: a marca é que designa"
