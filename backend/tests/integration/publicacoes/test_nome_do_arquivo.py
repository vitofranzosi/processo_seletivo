"""O nome do arquivo no download do Edital (069, FR-1387, R-012).

O documento publicado chega ao candidato como `edital-«n»-«ano».pdf`; o de uma Retificação, como
`edital-«n»-«ano»-retificado-«AAAA-MM-DD».pdf`, com a data da publicação no fuso institucional. A
prévia mantém o nome de hoje. Sem nome, o navegador salvava o arquivo pelo identificador da URL.
"""

from datetime import UTC, datetime
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest
from django.urls import reverse

from processo_seletivo.publicacoes.api.views import nome_do_documento
from processo_seletivo.publicacoes.models import Publicacao
from tests.fixtures.publicacao import publish_original, retify

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

FUSO = ZoneInfo("America/Sao_Paulo")


def _disposicao(client, publicacao):
    resposta = client.get(reverse("public-document", args=[publicacao.id]))
    assert resposta.status_code == 200
    return resposta["Content-Disposition"]


def test_o_publicado_se_chama_pelo_numero_e_o_ano(
    client, api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    publicacao = Publicacao.objects.get(edital=edital)
    numero = edital.number.replace("/", "-")
    assert _disposicao(client, publicacao) == (
        f'inline; filename="edital-{numero}-{edital.year}.pdf"'
    )


def test_o_da_retificacao_leva_a_data_da_publicacao(
    client, api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    retify(
        api_client,
        edital,
        [{"operation": "REPLACE", "targetPath": "/description", "newValue": "Nova."}],
        suffix="nome-069",
    )
    publicacao = Publicacao.objects.filter(edital=edital).latest("publication_order")
    dia = publicacao.published_at.astimezone(FUSO).date()
    numero = edital.number.replace("/", "-")
    assert _disposicao(client, publicacao) == (
        f'inline; filename="edital-{numero}-{edital.year}-retificado-{dia.isoformat()}.pdf"'
    )


def test_a_data_e_a_do_fuso_institucional_e_nao_a_de_utc():
    """Às 02h30 UTC ainda é o dia anterior em Vitória: é ele que o nome diz."""
    publicacao = SimpleNamespace(
        edital=SimpleNamespace(number="07", year=2026),
        publication_order=2,
        published_at=datetime(2026, 11, 3, 2, 30, tzinfo=UTC),
    )
    assert nome_do_documento(publicacao) == "edital-07-2026-retificado-2026-11-02.pdf"
    publicacao.publication_order = 1
    assert nome_do_documento(publicacao) == "edital-07-2026.pdf"


def test_numero_incomum_nao_quebra_o_cabecalho():
    """Número em texto livre: aspas e espaço viram hífen, e o não ASCII vai em `filename*`."""
    from django.utils.http import content_disposition_header

    publicacao = SimpleNamespace(
        edital=SimpleNamespace(number='07 "A"', year=2026), publication_order=1, published_at=None
    )
    assert nome_do_documento(publicacao) == "edital-07-A-2026.pdf"
    publicacao.edital.number = "nº 07"
    cabecalho = content_disposition_header(
        as_attachment=False, filename=nome_do_documento(publicacao)
    )
    assert cabecalho == "inline; filename*=utf-8''edital-n%C2%BA-07-2026.pdf"
