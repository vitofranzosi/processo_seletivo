"""Um Edital publicado **antes** do incremento canônico da `012`.

Simular a versão anterior é a única forma de exercitar a elevação, e ela não pode ser simulada por
`UPDATE`: `VersaoConsolidada` e `Publicacao` são append-only por trigger desde a `002`, e reescrever
uma linha publicada é exatamente o que a decisão D-002 promete nunca fazer. O caminho é montar a
Publicação como ela **teria sido** — conteúdo sem as duas propriedades, `schemaVersion` anterior — e
inseri-la, que é operação que a trigger admite.

O Edital atravessa o rascunho e a submissão pela API, de modo que a `RevisaoEdital` seja real: é
por `source_publication__revisao__isnull=False` que a consolidação encontra a versão original.
"""

import hashlib

from django.utils import timezone

from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.domain.elevacao import DEGRAUS
from processo_seletivo.publicacoes.models import DocumentoPublicado, Publicacao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.shared.canonical import canonical_bytes, canonical_sha256
from tests.fixtures.edital import actor_headers, complete_draft
from tests.fixtures.publicacao import SIGNATORY

VERSAO_ANTERIOR = 4
# O que rebaixar tira: **tudo** o que os degraus acima da versão alvo escrevem, derivado da própria
# elevação. A lista literal aqui já ficou desatualizada uma vez — com o segundo incremento, ela
# deixava `forma` num conteúdo carimbado como 4, que é uma grafia que nunca existiu — e derivá-la
# é o que impede a terceira vez.
PROPRIEDADES_DO_INCREMENTO = tuple(
    chave
    for versao, degrau in sorted(DEGRAUS.items())
    if versao > VERSAO_ANTERIOR
    for chave in degrau
)


def rebaixar(conteudo):
    """O conteúdo como ele era antes do incremento: sem as duas chaves, na versão anterior."""
    return {
        **conteudo,
        "schemaVersion": VERSAO_ANTERIOR,
        "stages": [
            {
                chave: valor
                for chave, valor in etapa.items()
                if chave not in PROPRIEDADES_DO_INCREMENTO
            }
            for etapa in conteudo.get("stages", [])
        ],
    }


def publicar_na_versao_anterior(api_client, manager_headers, process_payload, *, draft=None):
    """Cria Processo e Edital e os publica com conteúdo da versão canônica anterior."""
    from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot
    from processo_seletivo.publicacoes.models import RevisaoEdital

    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert criado.status_code == 201, criado.content
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
    revisao = RevisaoEdital.objects.filter(edital=edital).latest("submitted_at")
    conteudo = rebaixar(edital_snapshot(edital))
    agora = timezone.now()
    publicacao = Publicacao.objects.create(
        edital=edital,
        revisao=revisao,
        publication_order=edital.next_publication_order,
        published_at=agora,
        effective_at=agora,
        content_hash=canonical_sha256(conteudo),
        canonical_content=canonical_bytes(conteudo),
        canonical_schema_version=VERSAO_ANTERIOR,
        published_by="publicador",
        signatory_id=SIGNATORY["authorityId"],
        signatory_name=SIGNATORY["name"],
        signatory_role=SIGNATORY["role"],
    )
    DocumentoPublicado.objects.create(
        publicacao=publicacao,
        bytes=b"documento da publicacao original",
        document_hash=hashlib.sha256(b"documento da publicacao original").hexdigest(),
    )
    VersaoConsolidada.objects.create(
        edital=edital,
        valid_from=agora,
        materialized_at=agora,
        source_publication=publicacao,
        content=conteudo,
        canonical_content=canonical_bytes(conteudo),
        content_hash=canonical_sha256(conteudo),
        applied_publications=[str(publicacao.id)],
    )
    Edital.objects.filter(pk=edital.pk).update(
        status=Edital.Status.PUBLICADO,
        next_publication_order=edital.next_publication_order + 1,
        revision=edital.revision + 1,
    )
    return Edital.objects.get(pk=edital.pk)


def hashes_publicados():
    """Os hashes de tudo que já está publicado, para afirmar depois que nada mudou."""
    return {
        "publicacoes": dict(Publicacao.objects.values_list("id", "content_hash")),
        "versoes": dict(VersaoConsolidada.objects.values_list("id", "content_hash")),
    }
