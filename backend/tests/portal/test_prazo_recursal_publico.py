"""Quem chega ao resultado sabe até quando pode recorrer (047, US4, `FR-769` a `FR-771`).

O RC-48 da auditoria de consolidação: a página pública do resultado não dizia o prazo recursal, e
só quem se identificava o via, no acompanhamento. O prazo agora é dito ao público, e é **o mesmo**
que a interposição aplica: as duas superfícies leem `janela_da_publicacao_divulgada` (`SC-284`).
"""

import re
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.processos.application.finalizacao import close_edital
from processo_seletivo.processos.models import Edital
from processo_seletivo.recursos.application.interpor import objetos_recorriveis
from processo_seletivo.seguranca.domain import Actor
from tests.fixtures.divulgacao import emitir, montar_marco, pontuar, publicar_o_ato

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

JANELA = {"admits": True, "durationDays": 5, "unit": "DIAS_CORRIDOS"}


def montar(gestor, api_client, manager_headers, process_payload, *, seed, janela=JANELA):
    cenario = montar_marco(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=seed,
        codigo=f"08{seed}",
        janela_recursal=janela,
    )
    cenario["inscricoes"] = pontuar(
        cenario, gestor, ["90.0000", "70.0000"], primeiro=900 + 2 * seed, sufixo=str(seed)
    )
    cenario["ato"] = emitir(cenario, gestor, chave=f"emitir-047-{seed}")
    return cenario


def pagina_do_resultado(client, publicacao):
    """Só o `<main>`, como `test_resultado_publico.py` lê: a folha de estilo vai em toda página, e
    uma palavra num comentário de CSS não é a página dizendo alguma coisa."""
    corpo = client.get(reverse("portal:resultado", args=[publicacao.id])).content.decode()
    return re.search(r"<main[^>]*>(.*)</main>", corpo, re.DOTALL).group(1)


def pagina_do_edital(client, cenario):
    return client.get(reverse("portal:selecao", args=[cenario["edital"].id])).content.decode()


def na_zona(instante):
    return timezone.localtime(instante)


def depois_do_prazo():
    return timezone.now() + timedelta(days=10)


def fecha_da_interposicao(inscricao, publicacao):
    """A data que a interposição aplica àquela publicação, como o acompanhamento a mostra."""
    for item in objetos_recorriveis(inscricao):
        if item["tipo"] == "publicacao" and item["id"] == publicacao.id:
            return item["fecha_em"]
    raise AssertionError("a publicação não está entre os objetos recorríveis da inscrição")


def test_prazo_aberto_na_pagina_do_resultado_e_na_lista_do_edital(
    client, gestor, api_client, manager_headers, process_payload
):
    cenario = montar(gestor, api_client, manager_headers, process_payload, seed=71)
    preliminar = publicar_o_ato(cenario, chave="publicar-047-71")
    fecha = fecha_da_interposicao(cenario["inscricoes"][0], preliminar)

    corpo = pagina_do_resultado(client, preliminar)
    assert "Prazo de recurso aberto" in corpo
    assert na_zona(preliminar.publicado_em).strftime("%d/%m/%Y") in corpo
    assert na_zona(fecha).strftime("%d/%m/%Y") in corpo, (
        "a página diz outra data que a interposição"
    )

    lista = pagina_do_edital(client, cenario)
    trecho = re.search(r'<ul class="resultados-divulgados">.*?</ul>', lista, flags=re.S).group(0)
    assert f"recurso até {na_zona(fecha).strftime('%d/%m/%Y')}" in trecho


def test_prazo_encerrado_diz_quando_e_some_da_lista(
    client, gestor, api_client, manager_headers, process_payload
):
    cenario = montar(gestor, api_client, manager_headers, process_payload, seed=72)
    preliminar = publicar_o_ato(cenario, chave="publicar-047-72")

    with patch("django.utils.timezone.now", return_value=depois_do_prazo()):
        corpo = pagina_do_resultado(client, preliminar)
        lista = pagina_do_edital(client, cenario)

    assert "Prazo de recurso encerrado em" in corpo
    assert "Prazo de recurso aberto" not in corpo
    assert "recurso até" not in lista


def test_a_definitiva_do_mesmo_ato_diz_o_prazo_da_primeira_publicacao(
    client, gestor, api_client, manager_headers, process_payload
):
    """A âncora é a primeira publicação do ato (018): republicar não abre prazo novo.

    A definitiva com o prazo aberto é recusada pela 018, e por isso ela é publicada com o relógio
    depois do prazo.
    """
    cenario = montar(gestor, api_client, manager_headers, process_payload, seed=73)
    preliminar = publicar_o_ato(cenario, chave="publicar-047-73")
    fecha_da_preliminar = fecha_da_interposicao(cenario["inscricoes"][0], preliminar)

    with patch("django.utils.timezone.now", return_value=depois_do_prazo()):
        definitiva = publicar_o_ato(
            cenario, natureza="DEFINITIVA", chave="publicar-047-73-def", declaracao=""
        )
        corpo = pagina_do_resultado(client, definitiva)

    assert "Prazo de recurso encerrado em" in corpo
    assert na_zona(fecha_da_preliminar).strftime("%d/%m/%Y") in corpo


def test_sem_janela_declarada_nada_se_diz_sobre_recurso(
    client, gestor, api_client, manager_headers, process_payload
):
    cenario = montar(gestor, api_client, manager_headers, process_payload, seed=74, janela=None)
    preliminar = publicar_o_ato(cenario, chave="publicar-047-74")

    assert "recurso" not in pagina_do_resultado(client, preliminar).lower()


def test_com_admits_false_nada_se_diz_sobre_recurso(
    client, gestor, api_client, manager_headers, process_payload
):
    cenario = montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=75,
        janela={"admits": False},
    )
    preliminar = publicar_o_ato(cenario, chave="publicar-047-75")

    assert "recurso" not in pagina_do_resultado(client, preliminar).lower()


def test_a_sucedida_nao_diz_prazo(client, gestor, api_client, manager_headers, process_payload):
    cenario = montar(gestor, api_client, manager_headers, process_payload, seed=76)
    preliminar = publicar_o_ato(cenario, chave="publicar-047-76")
    with patch("django.utils.timezone.now", return_value=depois_do_prazo()):
        publicar_o_ato(cenario, natureza="DEFINITIVA", chave="publicar-047-76-def", declaracao="")

    corpo = pagina_do_resultado(client, preliminar)

    assert "Este resultado foi sucedido" in corpo
    assert "Prazo de recurso" not in corpo


def test_edital_encerrado_com_prazo_em_curso_continua_dizendo_o_prazo(
    client, gestor, api_client, manager_headers, process_payload
):
    """Caso-limite da 047: o desfecho não apaga a norma aplicada a ato já publicado."""
    cenario = montar(gestor, api_client, manager_headers, process_payload, seed=77)
    preliminar = publicar_o_ato(cenario, chave="publicar-047-77")
    edital = Edital.objects.get(pk=cenario["edital"].id)
    close_edital(
        actor=Actor("gestora.prazo", "cefor", frozenset({"edital:encerrar"})),
        edital_id=edital.id,
        expected_revision=edital.revision,
        reason="Encerramento com prazo em curso.",
        idempotency_key="encerrar-047-77",
        correlation_id="047-prazo",
    )
    fecha = fecha_da_interposicao(cenario["inscricoes"][0], preliminar)

    corpo = pagina_do_resultado(client, preliminar)

    assert "Prazo de recurso aberto" in corpo
    assert na_zona(fecha).strftime("%d/%m/%Y") in corpo


def test_nenhuma_acao_de_recorrer_em_caso_algum(
    client, gestor, api_client, manager_headers, process_payload
):
    """`FR-771`, e a `FR-055` da `017` na parte que continua: a página diz o prazo, e só."""
    cenario = montar(gestor, api_client, manager_headers, process_payload, seed=78)
    preliminar = publicar_o_ato(cenario, chave="publicar-047-78")

    corpo = pagina_do_resultado(client, preliminar)

    assert "<form" not in corpo
    assert "recorrer" not in re.sub(r"recorre pela", "", corpo.lower())


# --- O custo da cadeia (revisão do #193) -------------------------------------------------------


def consultas(client, url):
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    with CaptureQueriesContext(connection) as capturadas:
        assert client.get(url).status_code == 200
    return [item["sql"] for item in capturadas.captured_queries]


def as_publicacoes(sqls):
    return [sql for sql in sqls if 'FROM "divulgacao_publicacaoresultado"' in sql]


def test_a_lista_do_edital_nao_consulta_a_cadeia_degrau_por_degrau(
    client, gestor, api_client, manager_headers, process_payload
):
    """O prazo da lista sobe a cadeia até a primeira publicação do ato; a cadeia já está carregada.

    Com uma publicação ou com duas na mesma cadeia, a página do Edital lê as publicações do mesmo
    jeito: o que cresce é o resultado, e não o número de idas ao banco.
    """
    curta = montar(gestor, api_client, manager_headers, process_payload, seed=79)
    publicar_o_ato(curta, chave="publicar-047-79")

    longa = montar(gestor, api_client, manager_headers, process_payload, seed=80)
    publicar_o_ato(longa, chave="publicar-047-80")
    with patch("django.utils.timezone.now", return_value=depois_do_prazo()):
        publicar_o_ato(longa, natureza="DEFINITIVA", chave="publicar-047-80-def", declaracao="")

    com_uma = as_publicacoes(
        consultas(client, reverse("portal:selecao", args=[curta["edital"].id]))
    )
    com_duas = as_publicacoes(
        consultas(client, reverse("portal:selecao", args=[longa["edital"].id]))
    )

    assert len(com_duas) == len(com_uma), com_duas


def test_a_pagina_do_resultado_sobe_a_cadeia_uma_vez(
    client, gestor, api_client, manager_headers, process_payload
):
    """A âncora do prazo e a lista das anteriores sobem a mesma cadeia; a segunda não reconsulta."""
    cenario = montar(gestor, api_client, manager_headers, process_payload, seed=85)
    preliminar = publicar_o_ato(cenario, chave="publicar-047-85")
    so_uma = as_publicacoes(consultas(client, reverse("portal:resultado", args=[preliminar.id])))
    with patch("django.utils.timezone.now", return_value=depois_do_prazo()):
        definitiva = publicar_o_ato(
            cenario, natureza="DEFINITIVA", chave="publicar-047-85-def", declaracao=""
        )

    com_anterior = as_publicacoes(
        consultas(client, reverse("portal:resultado", args=[definitiva.id]))
    )

    # Um degrau a mais custa, no máximo, a leitura da publicação anterior — uma vez.
    assert len(com_anterior) <= len(so_uma) + 1, com_anterior
