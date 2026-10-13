"""O acervo publicado antes da `069` não muda (FR-1393, FR-1394, SC-523; premissa da spec).

Três garantias, cada uma no ponto em que a `069` poderia rompê-la:

- **o documento publicado é servido com os bytes gravados na publicação**, e não recomposto: um
  Edital publicado com o compositor anterior continua dizendo o que publicou;
- **o hash do conteúdo já homologado não muda**: a `069` não toca o snapshot que já existe;
- **o Edital homologado antes da troca do catálogo é recusado na publicação**, com
  `homologated_revision_changed`, e nada é publicado — o snapshot que a publicação compõe agora
  leva os títulos e a ordem do catálogo vigente, e diverge do homologado. É o custo que a spec
  registra: devolvê-lo à elaboração, e submetê-lo e homologá-lo de novo, já com a redação nova.
"""

import hashlib

import pytest
from django.urls import reverse

from processo_seletivo.editais.domain import secoes, validation
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application import publish_edital as publicacao
from processo_seletivo.publicacoes.models import DocumentoPublicado, Publicacao
from processo_seletivo.shared.canonical import canonical_sha256
from tests.fixtures.edital import actor_headers, complete_draft
from tests.fixtures.publicacao import SIGNATORY, publish_original
from tests.integration.publicacoes.test_topologia_do_acervo import CATALOGO_ANTERIOR

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

# O que o compositor de antes produziria. A `069` não pode regenerá-lo nem servi-lo diferente.
BYTES_DO_COMPOSITOR_ANTERIOR = b"%PDF-1.4\n% composto antes da 069\n%%EOF\n"


def test_o_documento_publicado_antes_e_servido_com_os_bytes_gravados(
    client, api_client, manager_headers, process_payload, monkeypatch
):
    with monkeypatch.context() as antes:
        antes.setattr(secoes, "CATALOGO", CATALOGO_ANTERIOR)
        antes.setattr(validation, "CATALOGO", CATALOGO_ANTERIOR)
        antes.setattr(
            publicacao, "render_edital_pdf", lambda *args, **kwargs: BYTES_DO_COMPOSITOR_ANTERIOR
        )
        edital = publish_original(api_client, manager_headers, process_payload)
    publicado = Publicacao.objects.get(edital=edital)

    resposta = client.get(reverse("public-document", args=[publicado.id]))

    assert resposta.status_code == 200
    assert resposta.content == BYTES_DO_COMPOSITOR_ANTERIOR
    documento = DocumentoPublicado.objects.get(publicacao=publicado)
    assert documento.document_hash == hashlib.sha256(BYTES_DO_COMPOSITOR_ANTERIOR).hexdigest()


def test_o_hash_do_conteudo_homologado_antes_nao_muda(
    api_client, manager_headers, process_payload, monkeypatch
):
    """O hash gravado na revisão é o do conteúdo dela, recalculado hoje (SC-523)."""
    with monkeypatch.context() as antes:
        antes.setattr(secoes, "CATALOGO", CATALOGO_ANTERIOR)
        antes.setattr(validation, "CATALOGO", CATALOGO_ANTERIOR)
        edital = publish_original(api_client, manager_headers, process_payload)
    revisao = edital.revisoes.order_by("-submitted_at").first()

    assert canonical_sha256(revisao.content) == revisao.content_hash
    assert Publicacao.objects.get(edital=edital).content_hash == revisao.content_hash


def test_o_homologado_antes_da_troca_e_recusado_na_publicacao(
    api_client, manager_headers, process_payload, monkeypatch
):
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert criado.status_code == 201, criado.content
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    preparador = actor_headers(
        "preparador", ["edital:elaborar", "edital:submeter"], key="acervo-da-069-chave-0001"
    )
    with monkeypatch.context() as antes:
        antes.setattr(secoes, "CATALOGO", CATALOGO_ANTERIOR)
        antes.setattr(validation, "CATALOGO", CATALOGO_ANTERIOR)
        gravado = api_client.put(
            f"/api/v1/admin/editais/{edital.id}/rascunho",
            complete_draft(),
            format="json",
            **{**preparador, "HTTP_IF_MATCH": f'"{edital.revision}"'},
        )
        assert gravado.status_code < 400, gravado.content
        edital.refresh_from_db()
        submetido = api_client.post(
            f"/api/v1/admin/editais/{edital.id}/submissoes",
            format="json",
            **{**preparador, "HTTP_IF_MATCH": f'"{edital.revision}"'},
        )
        assert submetido.status_code < 400, submetido.content
        edital.refresh_from_db()
        homologado = api_client.post(
            f"/api/v1/admin/editais/{edital.id}/homologacoes",
            {"reason": "OK"},
            format="json",
            **{
                **actor_headers(
                    "homologador", ["edital:homologar"], key="acervo-da-069-chave-0001"
                ),
                "HTTP_IF_MATCH": f'"{edital.revision}"',
            },
        )
        assert homologado.status_code < 400, homologado.content
    edital.refresh_from_db()

    publicado = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/publicacoes",
        {"signatory": SIGNATORY},
        format="json",
        **{
            **actor_headers("publicador", ["edital:publicar"], key="acervo-da-069-chave-0001"),
            "HTTP_IF_MATCH": f'"{edital.revision}"',
        },
    )

    assert publicado.status_code == 409, publicado.content
    assert publicado.json()["code"] == "homologated_revision_changed"
    assert not Publicacao.objects.filter(edital=edital).exists()
