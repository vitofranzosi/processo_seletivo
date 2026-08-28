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
