"""Apoio comum às telas: identidade e o seletor que substitui a autenticação institucional."""

import pytest
from django.urls import reverse


def identificar(client, subject, papeis):
    resposta = client.post(reverse("interface:identificar"), {"subject": subject, "papeis": papeis})
    assert resposta.status_code == 302, resposta.content
    return resposta


@pytest.fixture
def seletor_ligado(settings):
    settings.INTERFACE_SELETOR_IDENTIDADE = True


def compor_rascunho(client, edital, perfis=None, eventos=None):
    """Percorre o assistente: Perfis e Cronograma são etapas distintas, salvas em separado."""
    from django.urls import reverse

    if perfis is not None:
        resposta = client.post(
            reverse("interface:compor-etapa", args=[edital.id, "perfis"]), perfis
        )
        assert resposta.status_code == 302, resposta.content
    if eventos is not None:
        edital.refresh_from_db()
        resposta = client.post(
            reverse("interface:compor-etapa", args=[edital.id, "cronograma"]), eventos
        )
        assert resposta.status_code == 302, resposta.content
    return edital
