"""O que foi publicado depois das inscrições, no cartão da vitrine (072, US5, FR-1629 a FR-1636).

O cartão de um Edital com resultado preliminar e prazo de recurso aberto dizia só "Inscrições
encerradas". O prazo para exercer um direito estava na página da seleção, e a vitrine o calava.
Estes testes prendem a ligação — a regra de resumo está em `test_resumo_do_acompanhamento.py` —:
o cartão diz o mesmo que a página, no mesmo instante, e a vitrine não passa a consultar o banco
uma vez por cartão.
"""

import re
from unittest.mock import patch

import pytest
from django.urls import reverse

from tests.fixtures.divulgacao import publicar_o_ato
from tests.fixtures.selecao import publicar_selecao
from tests.portal.test_prazo_recursal_publico import (
    consultas,
    depois_do_prazo,
    fecha_da_interposicao,
    montar,
    na_zona,
    pagina_do_edital,
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def cartao_do(client, edital):
    """O cartão do Edital: do seu `<li class="selecao">` até o próximo, ou até o fim da lista."""
    corpo = client.get(reverse("portal:vitrine")).content.decode()
    endereco = reverse("portal:selecao", args=[edital.id])
    for cartao in corpo.split('<li class="selecao">')[1:]:
        if endereco in cartao:
            return " ".join(re.sub(r"<[^>]+>", " ", cartao).split()), cartao
    raise AssertionError("o Edital não tem cartão na vitrine")


def test_o_cartao_diz_o_resultado_e_o_prazo_que_a_pagina_diz(
    client, gestor, api_client, manager_headers, process_payload
):
    cenario = montar(gestor, api_client, manager_headers, process_payload, seed=91)
    preliminar = publicar_o_ato(cenario, chave="publicar-072-91")
    fecha = na_zona(fecha_da_interposicao(cenario["inscricoes"][0], preliminar))

    texto, _ = cartao_do(client, cenario["edital"])
    pagina = pagina_do_edital(client, cenario)

    publicado = na_zona(preliminar.publicado_em).strftime("%d/%m/%Y")
    assert f"Resultado preliminar publicado em {publicado}." in texto
    assert f"Recurso até {fecha.strftime('%d/%m/%Y')} às {fecha.strftime('%Hh%M')}." in texto
    assert f"recurso até {fecha.strftime('%d/%m/%Y')}" in pagina, "o cartão e a página discordam"
    assert "Ver resultados e prazo de recurso" in texto


def test_prazo_encerrado_sai_do_cartao_e_o_resultado_fica(
    client, gestor, api_client, manager_headers, process_payload
):
    cenario = montar(gestor, api_client, manager_headers, process_payload, seed=92)
    publicar_o_ato(cenario, chave="publicar-072-92")

    with patch("django.utils.timezone.now", return_value=depois_do_prazo()):
        texto, _ = cartao_do(client, cenario["edital"])

    assert "Resultado preliminar publicado em" in texto
    assert "Recurso" not in texto
    assert "Ver resultado" in texto


def test_a_publicacao_sucedida_nao_conta(
    client, gestor, api_client, manager_headers, process_payload
):
    """Só a vigente entra em N, em M e na data — a sucedida continua no endereço dela (047)."""
    cenario = montar(gestor, api_client, manager_headers, process_payload, seed=93)
    publicar_o_ato(cenario, chave="publicar-072-93")
    with patch("django.utils.timezone.now", return_value=depois_do_prazo()):
        definitiva = publicar_o_ato(
            cenario, natureza="DEFINITIVA", chave="publicar-072-93-def", declaracao=""
        )
        texto, _ = cartao_do(client, cenario["edital"])

    publicado = na_zona(definitiva.publicado_em).strftime("%d/%m/%Y")
    assert f"Resultado definitivo publicado em {publicado}." in texto
    assert "resultados publicados" not in texto
    assert "preliminar" not in texto


def test_sem_resultado_o_cartao_nao_diz_nada_sobre_resultado(
    client, api_client, manager_headers, process_payload
):
    edital = publicar_selecao(api_client, manager_headers, process_payload)

    texto, cartao = cartao_do(client, edital)

    assert 'class="acompanhamento"' not in cartao
    assert "esultado" not in texto


def test_a_vitrine_nao_consulta_o_banco_por_cartao(
    client, gestor, api_client, manager_headers, process_payload
):
    """FR-1635 e a premissa do plano: o número de consultas não cresce com o número de cartões.

    O processamento cresce com as publicações lidas — e isso é aceitável; o que não pode é a leitura
    de cada cartão ser uma ida ao banco.
    """
    um = montar(gestor, api_client, manager_headers, process_payload, seed=94)
    publicar_o_ato(um, chave="publicar-072-94")
    com_um = consultas(client, reverse("portal:vitrine"))

    for seed in (95, 96):
        outro = montar(gestor, api_client, manager_headers, process_payload, seed=seed)
        publicar_o_ato(outro, chave=f"publicar-072-{seed}")
    com_tres = consultas(client, reverse("portal:vitrine"))

    assert len(com_tres) == len(com_um), "\n".join(com_tres)
