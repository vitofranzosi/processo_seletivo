"""O Edital em si continua sendo o documento — e a página leva a ele (FR-014).

A vitrine e o detalhe derivam do conteúdo publicado, mas o que tem valor normativo é o PDF
assinado. A página não o substitui; ela o alcança.
"""

import pytest
from django.urls import reverse

from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.selecao import publicar_selecao


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_detalhe_leva_ao_documento_publicado(
    client, api_client, manager_headers, process_payload
):
    edital = publicar_selecao(api_client, manager_headers, process_payload)
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    endereco = reverse("public-document", args=[vigente.source_publication_id])

    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()

    assert endereco in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_documento_apontado_e_alcancavel_sem_identificacao(
    client, api_client, manager_headers, process_payload
):
    edital = publicar_selecao(api_client, manager_headers, process_payload)
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")

    resposta = client.get(reverse("public-document", args=[vigente.source_publication_id]))

    assert resposta.status_code == 200
    assert resposta.headers["Content-Type"] == "application/pdf"
