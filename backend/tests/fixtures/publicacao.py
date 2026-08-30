"""Fluxos completos de Publicação e Retificação reutilizados pelos testes de US4 a US6."""

from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.edital import actor_headers, complete_draft

SIGNATORY = {
    "authorityId": "00000000-0000-0000-0000-000000000601",
    "name": "Diretora",
    "role": "Diretora-Geral",
}


def publish_original(api_client, manager_headers, process_payload, *, draft=None):
    """Cria Processo e primeiro Edital e o leva até a primeira Publicação."""
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert criado.status_code == 201, criado.content
    # Escopado ao Processo: o helper precisa servir a testes com mais de um Edital.
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    preparer = actor_headers("preparador", ["edital:elaborar", "edital:submeter"])
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        draft or complete_draft(),
        format="json",
        **{**preparer, "HTTP_IF_MATCH": '"1"'},
    )
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/submissoes",
        format="json",
        **{**preparer, "HTTP_IF_MATCH": '"2"'},
    )
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **{**actor_headers("homologador", ["edital:homologar"]), "HTTP_IF_MATCH": '"3"'},
    )
    published = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/publicacoes",
        {"signatory": SIGNATORY},
        format="json",
        **{**actor_headers("publicador", ["edital:publicar"]), "HTTP_IF_MATCH": '"4"'},
    )
    assert published.status_code == 201, published.content
    return Edital.objects.get(pk=edital.pk)


def create_retification(api_client, edital, changes, *, effective_at=None, suffix="a"):
    base = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    payload = {
        "baseSnapshotId": str(base.id),
        "justification": f"Retificação {suffix}",
        "changes": changes,
    }
    if effective_at is not None:
        payload["effectiveAt"] = effective_at
    created = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/retificacoes",
        payload,
        format="json",
        **actor_headers("retificador", ["retificacao:elaborar"], key=f"retificacao-{suffix}-0001"),
    )
    assert created.status_code == 201, created.content
    return Retificacao.objects.get(pk=created.json()["id"])


def publish_retification(api_client, retificacao, *, suffix="a"):
    """Submete, homologa e publica uma Retificação já criada."""
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao.id}/submissoes",
        format="json",
        **{
            **actor_headers(
                "retificador", ["retificacao:submeter"], key=f"retificacao-{suffix}-0002"
            ),
            "HTTP_IF_MATCH": '"1"',
        },
    )
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao.id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **{
            **actor_headers(
                "homologador-r", ["retificacao:homologar"], key=f"retificacao-{suffix}-0003"
            ),
            "HTTP_IF_MATCH": '"2"',
        },
    )
    published = api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao.id}/publicacoes",
        {"signatory": SIGNATORY},
        format="json",
        **{
            **actor_headers(
                "publicador-r", ["retificacao:publicar"], key=f"retificacao-{suffix}-0004"
            ),
            "HTTP_IF_MATCH": '"3"',
        },
    )
    assert published.status_code == 201, published.content
    retificacao.refresh_from_db()
    return retificacao


def retify(api_client, edital, changes, *, effective_at=None, suffix="a"):
    """Cria e publica uma Retificação em um passo."""
    retificacao = create_retification(
        api_client, edital, changes, effective_at=effective_at, suffix=suffix
    )
    return publish_retification(api_client, retificacao, suffix=suffix)
