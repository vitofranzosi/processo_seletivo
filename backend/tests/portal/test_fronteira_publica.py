"""A fronteira entre o divulgado e o individual, afirmada dos dois lados (FR-017, T-010, T-013).

**São duas afirmações, e nenhuma basta sozinha.**

A primeira é sobre o **HTML renderizado**: nada de quem está apenas em `SituacaoDivulgada` aparece
na página pública. É o que a pessoa de fato vê.

A segunda é sobre a **consulta emitida**: a view não alcança aquela tabela. Sem ela, o primeiro
teste continuaria passando com uma view que carrega o dado individual e um template que se lembra de
não o imprimir — e a fronteira passaria a depender de ninguém mexer no template. Com ela, não há o
que imprimir.
"""

import re

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.divulgacao.models import SituacaoDivulgada
from tests.fixtures.divulgacao import montar_ato_publicavel, publicar_o_ato

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def publicada(gestor, api_client, manager_headers, process_payload):
    """Duas classificadas e **duas** consideradas sem posição — a fronteira precisa de gente."""
    cenario = montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=63,
        codigo="0763",
        pontuacoes=("90.0000", "70.0000", None, None),
        primeiro=1101,
    )
    return cenario, publicar_o_ato(cenario, chave="publicar-0763")


def test_ninguem_de_situacao_divulgada_aparece_no_html(client, publicada):
    """A primeira metade: o que a pessoa vê."""
    _, publicacao = publicada
    sem_posicao = SituacaoDivulgada.objects.filter(
        publicacao=publicacao, situacao=SituacaoDivulgada.Situacao.SEM_POSICAO
    ).select_related("inscricao")
    assert sem_posicao.count() == 2, "o cenário precisa de gente do lado de cá da fronteira"

    corpo = client.get(reverse("portal:resultado", args=[publicacao.id])).content.decode()
    renderizado = re.search(r"<main[^>]*>(.*)</main>", corpo, re.DOTALL).group(1)

    for linha in sem_posicao:
        assert linha.inscricao.nome not in renderizado
        assert linha.inscricao.protocolo not in renderizado
        assert str(linha.inscricao_id) not in renderizado
        if linha.motivo:
            assert linha.motivo not in renderizado


def test_a_view_nao_emite_consulta_a_situacao_divulgada(client, publicada):
    """A segunda metade, e a que sustenta a primeira contra o tempo.

    A fronteira é a **ausência da consulta**, e não um filtro na renderização: trocar "o template
    não imprime isto" por "a view não tem como buscar isto" é o que T-010 comprou ao separar as
    projeções em tabelas distintas.
    """
    _, publicacao = publicada

    with CaptureQueriesContext(connection) as consultas:
        client.get(reverse("portal:resultado", args=[publicacao.id]))

    tocaram = [
        item["sql"]
        for item in consultas.captured_queries
        if "divulgacao_situacaodivulgada" in item["sql"]
    ]
    assert tocaram == [], f"a página pública consultou a tabela do individual: {tocaram}"


def test_o_documento_publico_tambem_nao_alcanca_o_individual(client, publicada):
    """O documento sai dos mesmos bytes, e por isso herda a mesma fronteira (FR-064)."""
    _, publicacao = publicada

    with CaptureQueriesContext(connection) as consultas:
        resposta = client.get(reverse("portal:resultado-documento", args=[publicacao.id]))

    assert resposta.status_code == 200
    assert not any(
        "divulgacao_situacaodivulgada" in item["sql"] for item in consultas.captured_queries
    )
    sem_posicao = SituacaoDivulgada.objects.filter(
        publicacao=publicacao, situacao=SituacaoDivulgada.Situacao.SEM_POSICAO
    ).select_related("inscricao")
    for linha in sem_posicao:
        assert linha.inscricao.nome.encode() not in resposta.content


def test_o_individual_existe_e_e_alcancavel_por_quem_tem_direito(client, publicada):
    """A contraprova: a fronteira separa, e não apaga.

    Sem isto, uma view que simplesmente não gravasse `SituacaoDivulgada` passaria nos dois testes
    acima — e a US3 inteira deixaria de existir sem que nada acusasse.
    """
    from tests.fixtures.divulgacao import entrar_como_titular

    cenario, publicacao = publicada
    sem_posicao = SituacaoDivulgada.objects.filter(
        publicacao=publicacao, situacao=SituacaoDivulgada.Situacao.SEM_POSICAO
    ).select_related("inscricao")[0]

    entrar_como_titular(client, sem_posicao.inscricao)
    corpo = client.get(
        reverse("portal:acompanhamento", args=[sem_posicao.inscricao_id])
    ).content.decode()

    assert "Você não foi classificado" in corpo
    assert cenario["edital"] is not None
