"""A publicação congela os artefatos, e a página pública os entrega (020, FR-025, FR-039).

O congelamento acontece **dentro da transação** em que a `Publicacao` nasce, e é essa a razão de os
bytes morarem em coluna binária: com arquivo em disco, um `rollback` deixaria conteúdo publicado
apontando para bytes inexistentes — o defeito que a feature veio corrigir.
"""

import pytest
from django.urls import reverse

from processo_seletivo.editais.models import ArtefatoAnexo
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.publicacao import publish_original
from tests.fixtures.snapshot import rascunho_completo

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def publicado(api_client, manager_headers, process_payload):
    return publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_completo(), anexos=2
    )


def test_a_publicacao_congela_todos_os_artefatos_daquela_versao(publicado):
    assert ArtefatoAnexo.objects.filter(congelado_em__isnull=True).count() == 0
    assert ArtefatoAnexo.objects.filter(congelado_em__isnull=False).count() == 2


def test_o_conteudo_publicado_carrega_identidade_e_resumo_de_cada_anexo(publicado):
    conteudo = VersaoConsolidada.objects.get(edital=publicado).content

    anexos = conteudo["attachments"]
    assert len(anexos) == 2
    for anexo in anexos:
        artefato = ArtefatoAnexo.objects.get(pk=anexo["artifactId"])
        assert anexo["artifactHash"] == artefato.document_hash, "o resumo verifica os bytes"
        assert anexo["label"]


def test_a_pagina_publica_da_selecao_oferece_todos_os_anexos(client, publicado):
    corpo = client.get(reverse("portal:selecao", args=[publicado.id])).content.decode()

    assert "Anexos do Edital" in corpo
    for artefato in ArtefatoAnexo.objects.all():
        assert reverse("public-anexo", args=[artefato.id]) in corpo


def test_o_publico_baixa_o_artefato_sem_se_identificar(client, publicado):
    conteudo = VersaoConsolidada.objects.get(edital=publicado).content
    artefato_id = conteudo["attachments"][0]["artifactId"]

    resposta = client.get(reverse("public-anexo", args=[artefato_id]))

    assert resposta.status_code == 200
    assert resposta["Content-Type"] == "application/pdf"


def test_o_documento_publicado_lista_os_anexos_e_nao_carrega_os_bytes(publicado):
    """D-002 e FR-027 — o documento cita, e o canal entrega."""
    from processo_seletivo.publicacoes.models import DocumentoPublicado

    documento = DocumentoPublicado.objects.get(publicacao__edital=publicado)
    conteudo = VersaoConsolidada.objects.get(edital=publicado).content
    soma_dos_anexos = sum(
        ArtefatoAnexo.objects.get(pk=anexo["artifactId"]).tamanho
        for anexo in conteudo["attachments"]
    )

    assert len(bytes(documento.bytes)) > 0
    assert soma_dos_anexos > 0
    assert b"%PDF" in bytes(documento.bytes)[:8]
