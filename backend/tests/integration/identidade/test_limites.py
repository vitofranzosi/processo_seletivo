"""Os limites por endereço e por origem — e o teto global que deliberadamente não existe."""

from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.identidade.application import desafio as servico
from processo_seletivo.identidade.models import DesafioDeAcesso

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ENTRAR = DesafioDeAcesso.Finalidade.ENTRAR


def pedir(endereco, origem="203.0.113.7"):
    return servico.solicitar(email_canonico=endereco, finalidade=ENTRAR, origem=origem)


def afastar_no_tempo(segundos=120):
    """Passa a espera entre envios sem esperar de verdade."""
    DesafioDeAcesso.objects.update(criado_em=timezone.now() - timedelta(seconds=segundos))


def test_ha_espera_entre_dois_envios_para_o_mesmo_endereco():
    _, primeiro = pedir("maria@exemplo.test")
    _, segundo = pedir("maria@exemplo.test")
    assert primeiro and not segundo, "o segundo pedido imediato não gera código"


def test_o_teto_por_endereco_para_de_gerar_codigo():
    for _ in range(servico.LIMITE_POR_ENDERECO):
        _, codigo = pedir("maria@exemplo.test")
        assert codigo
        afastar_no_tempo()
    _, alem = pedir("maria@exemplo.test")
    assert not alem


def test_o_teto_por_origem_alcanca_enderecos_distintos():
    """Quem varre endereços de uma origem só é contido, mesmo sem repetir endereço."""
    for indice in range(servico.LIMITE_POR_ORIGEM):
        _, codigo = pedir(f"pessoa{indice}@exemplo.test", origem="198.51.100.9")
        assert codigo
    _, alem = pedir("outra@exemplo.test", origem="198.51.100.9")
    assert not alem


def test_origens_distintas_nao_dividem_o_mesmo_teto():
    for indice in range(servico.LIMITE_POR_ORIGEM):
        pedir(f"pessoa{indice}@exemplo.test", origem="198.51.100.9")
    _, de_outra = pedir("alguem@exemplo.test", origem="203.0.113.7")
    assert de_outra, "o teto de uma origem não pode recusar quem vem de outra"


def test_nao_existe_teto_global():
    """Um teto global converteria abuso distribuído em indisponibilidade para todos (FR-030).

    E converteria no dia em que ela mais custa: o último do prazo de inscrições.
    """
    for indice in range(servico.LIMITE_POR_ORIGEM + 5):
        _, codigo = pedir(f"pessoa{indice}@exemplo.test", origem=f"192.0.2.{indice}")
        assert codigo, "origens distintas continuam sendo atendidas"
