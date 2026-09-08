"""A publicação congela os artefatos, e a página pública os entrega (020, FR-025, FR-039).

O congelamento acontece **dentro da transação** em que a `Publicacao` nasce, e é essa a razão de os
bytes morarem em coluna binária: com arquivo em disco, um `rollback` deixaria conteúdo publicado
apontando para bytes inexistentes — o defeito que a feature veio corrigir.
"""

import pytest
from django.urls import reverse
from django.utils import timezone

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


def test_a_publicacao_e_recusada_quando_os_bytes_nao_correspondem_ao_resumo(
    api_client, manager_headers, process_payload
):
    """FR-026 — o resumo da versão homologada prova os bytes, e é conferido antes de congelar.

    Sem esta conferência, um artefato alterado entre a homologação e a publicação entraria com o
    resumo antigo: a versão publicada afirmaria um conteúdo e o download entregaria outro, com o
    `ETag` mentindo sobre os dois. É o elo `resumo publicado → bytes` da cadeia da FR-053, e é o
    único que a aplicação precisa fechar sozinha — os demais são estruturais.
    """
    from processo_seletivo.publicacoes.application.publish_edital import congelar_artefatos
    from processo_seletivo.shared.api.problems import DomainError
    from tests.fixtures.anexos import pdf_de_teste

    artefato = ArtefatoAnexo.objects.create(
        bytes=pdf_de_teste("A"),
        tamanho=len(pdf_de_teste("A")),
        document_hash="0" * 64,
        nome_original="anexo.pdf",
        enviado_por="preparador",
        enviado_em=timezone.now(),
    )
    conteudo = {
        "attachments": [
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "label": "ANEXO I — REQUERIMENTO",
                "order": 1,
                "artifactId": str(artefato.id),
                "artifactHash": "0" * 64,
            }
        ]
    }

    with pytest.raises(DomainError) as recusa:
        congelar_artefatos(conteudo, now=timezone.now())

    assert recusa.value.code == "attachment_artifact_missing"
    artefato.refresh_from_db()
    assert artefato.congelado_em is None, "nada é congelado quando a conferência falha"


def test_a_publicacao_e_recusada_quando_o_artefato_nao_existe():
    """A versão citaria bytes que ninguém tem, e o candidato receberia 404 no anexo do Edital."""
    from processo_seletivo.publicacoes.application.publish_edital import congelar_artefatos
    from processo_seletivo.shared.api.problems import DomainError

    conteudo = {
        "attachments": [
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "label": "ANEXO I — REQUERIMENTO",
                "order": 1,
                "artifactId": "22222222-2222-2222-2222-222222222222",
                "artifactHash": "0" * 64,
            }
        ]
    }

    with pytest.raises(DomainError) as recusa:
        congelar_artefatos(conteudo, now=timezone.now())

    assert recusa.value.code == "attachment_artifact_missing"


def test_a_publicacao_e_recusada_quando_o_requisito_aponta_anexo_inexistente(
    api_client, manager_headers, process_payload
):
    """FR-023 — a referência pendurada é impeditiva na publicação, e não só na Retificação.

    É o defeito que a `020` veio corrigir entrando pela porta de trás: um Edital que promete modelo
    e publica sem ele manda o candidato ao mesmo lugar vazio de antes.
    """
    from processo_seletivo.editais.domain.validation import (
        blocking_findings,
        validate_for_publication,
    )

    snapshot = {
        "title": "Edital",
        "profiles": [{"id": "11111111-1111-1111-1111-111111111111"}],
        "schedule": [{"id": "22222222-2222-2222-2222-222222222222"}],
        "attachments": [],
        "documentRequirements": [
            {
                "id": "33333333-3333-3333-3333-333333333333",
                "name": "Requerimento",
                "attachmentId": "44444444-4444-4444-4444-444444444444",
            }
        ],
    }

    codigos = {item.code for item in blocking_findings(validate_for_publication(snapshot))}

    assert "attachment_reference_dangling" in codigos
