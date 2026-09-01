"""A origem que conta o limite não pode ser escolhida por quem é contado (FR-030).

`X-Forwarded-For` é escrito pelo cliente. Lê-lo sem um proxy que o sobrescreva tornava o limite por
origem decorativo: quem varre endereços mandava um valor diferente a cada requisição, cada uma
parecia vir de outro lugar, e o teto nunca era alcançado — sobrava só o limite por endereço, que
não contém quem varre endereços distintos.
"""

import pytest
from django.urls import reverse

from processo_seletivo.identidade.application import desafio as servico
from processo_seletivo.identidade.models import DesafioDeAcesso

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def pedir(client, indice, **cabecalhos):
    return client.post(
        reverse("portal:acesso"), {"email": f"pessoa{indice}@exemplo.test"}, **cabecalhos
    )


def test_o_cabecalho_forjado_nao_muda_a_origem_por_padrao(client):
    for indice in range(servico.LIMITE_POR_ORIGEM + 3):
        pedir(client, indice, HTTP_X_FORWARDED_FOR=f"203.0.113.{indice}")

    assert DesafioDeAcesso.objects.count() == servico.LIMITE_POR_ORIGEM, (
        "trocar o cabeçalho a cada requisição não pode multiplicar o teto"
    )


def test_as_origens_gravadas_sao_todas_a_mesma(client):
    for indice in range(3):
        pedir(client, indice, HTTP_X_FORWARDED_FOR=f"203.0.113.{indice}")

    assert len(set(DesafioDeAcesso.objects.values_list("origem_hash", flat=True))) == 1


def test_atras_de_proxy_declarado_o_cabecalho_volta_a_valer(client, settings):
    """Quem implanta declara o que é verdade na sua topologia."""
    settings.PORTAL_ATRAS_DE_PROXY = True

    for indice in range(3):
        pedir(client, indice, HTTP_X_FORWARDED_FOR=f"203.0.113.{indice}")

    assert len(set(DesafioDeAcesso.objects.values_list("origem_hash", flat=True))) == 3
