import pytest

from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models import Publicacao
from tests.fixtures.edital import actor_headers, complete_draft


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_us4_complete_publication_flow(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()
    preparer = actor_headers("preparador", ["edital:elaborar", "edital:submeter"])
    homologator = actor_headers("homologador", ["edital:homologar"])
    publisher = actor_headers("publicador", ["edital:publicar"])
    assert (
        api_client.put(
            f"/api/v1/admin/editais/{edital.id}/rascunho",
            complete_draft(),
            format="json",
            **{**preparer, "HTTP_IF_MATCH": '"1"'},
        ).status_code
        == 200
    )
    assert (
        api_client.post(
            f"/api/v1/admin/editais/{edital.id}/submissoes",
            format="json",
            **{**preparer, "HTTP_IF_MATCH": '"2"'},
        ).status_code
        == 200
    )
    assert (
        api_client.post(
            f"/api/v1/admin/editais/{edital.id}/homologacoes",
            {"reason": "Aprovado"},
            format="json",
            **{**homologator, "HTTP_IF_MATCH": '"3"'},
        ).status_code
        == 200
    )
    published = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/publicacoes",
        {
            "signatory": {
                "authorityId": "00000000-0000-0000-0000-000000000496",
                "name": "Diretora",
                "role": "Diretora-Geral",
            }
        },
        format="json",
        **{**publisher, "HTTP_IF_MATCH": '"4"'},
    )
    assert published.status_code == 201
    assert Edital.objects.get().status == Edital.Status.PUBLICADO
    publication = Publicacao.objects.get()
    assert published.json()["contentHash"] == publication.content_hash
    assert published["Location"].endswith(str(publication.id))


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_us4_published_document_matches_the_homologated_content(
    api_client, manager_headers, process_payload
):
    """US4 cenário 4 e FR-023: o documento servido reproduz a versão homologada."""
    from processo_seletivo.publicacoes.models import DocumentoPublicado, RevisaoEdital
    from tests.fixtures.publicacao import publish_original
    from tests.unit.publicacoes.test_pdf import texto_de

    edital = publish_original(api_client, manager_headers, process_payload)
    publicacao = Publicacao.objects.get(edital=edital)
    revisao = RevisaoEdital.objects.get(edital=edital)

    resposta = api_client.get(f"/api/v1/public/publicacoes/{publicacao.id}/documento")
    assert resposta.status_code == 200
    assert resposta["Content-Type"] == "application/pdf"

    documento = DocumentoPublicado.objects.get(publicacao=publicacao)
    servido = b"".join(resposta.streaming_content) if resposta.streaming else resposta.content
    assert servido == bytes(documento.bytes), "os bytes servidos são os preservados"

    texto = texto_de(servido)
    for perfil in revisao.content["profiles"]:
        assert perfil["code"] in texto, perfil["code"]
        assert perfil["name"] in texto
        # **Forma atualizada pela `008`/US2**: a identificação do Perfil virou quadro, e rótulo e
        # valor passaram a ser células distintas. O que esta aceitação guarda é que o número de
        # vagas do conteúdo homologado chega ao documento — e continua chegando.
        assert "Vagas imediatas" in texto
        assert str(perfil["immediateVacancies"]) in texto
    for evento in revisao.content["schedule"]:
        assert evento["description"] in texto, evento["description"]
    assert revisao.content_hash in texto, "o documento carrega o hash da versão homologada"
    assert publicacao.content_hash == revisao.content_hash
