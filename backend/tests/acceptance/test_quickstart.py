"""T094 — verificações do quickstart que ainda não tinham cobertura comportamental.

Cada teste corresponde a um passo textual de quickstart.md. Os demais passos já eram
exercitados pelas suítes de US1 a US7 e estão mapeados em validation-report.md.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.editais.models.cronograma import Cronograma, EventoCronograma
from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.publicacoes.domain.consolidation import consolidate
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from processo_seletivo.shared.canonical import canonical_sha256
from tests.fixtures.edital import actor_headers, caminho_perfil, complete_draft
from tests.fixtures.publicacao import SIGNATORY, create_retification, publish_original, retify

VACANCIES = caminho_perfil("immediateVacancies")
TITLE = "/title"


def replace(path, value):
    return [{"targetPath": path, "operation": "REPLACE", "newValue": value}]


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_quickstart_s1_invalid_payload_leaves_no_partial_process(api_client, manager_headers):
    """S1: repetir com dado inválido e confirmar rejeição sem Processo parcial."""
    resposta = api_client.post(
        "/api/v1/admin/processos",
        {"institutionalCode": "PS-INVALIDO", "title": "Sem Edital"},
        format="json",
        **manager_headers,
    )
    assert resposta.status_code == 422
    assert resposta.json()["code"] == "invalid_payload"
    assert not ProcessoSeletivo.objects.exists()
    assert not Edital.objects.exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_quickstart_s2_editing_the_second_edital_does_not_touch_the_first(
    api_client, manager_headers, process_payload
):
    """S2: alterar somente o segundo Edital; estado, revisão e Cronograma do primeiro não mudam."""
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    processo_id = criado.json()["id"]
    api_client.post(
        f"/api/v1/admin/processos/{processo_id}/editais",
        {"number": "02", "year": 2026, "title": "Segundo"},
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "quickstart-s2-000001"},
    )
    primeiro, segundo = Edital.objects.order_by("number")
    antes = (primeiro.status, primeiro.revision)

    resposta = api_client.put(
        f"/api/v1/admin/editais/{segundo.id}/rascunho",
        complete_draft(),
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key="quickstart-s2-000002"),
            "HTTP_IF_MATCH": '"1"',
        },
    )
    assert resposta.status_code == 200

    primeiro.refresh_from_db()
    assert (primeiro.status, primeiro.revision) == antes
    assert not Cronograma.objects.filter(edital=primeiro).exists()
    assert Cronograma.objects.filter(edital=segundo).exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_quickstart_s3_draft_cannot_reuse_identifiers_from_another_edital(
    api_client, manager_headers, process_payload
):
    """S3: Evento ou Perfil já pertencente a outro Edital é rejeitado, sem estrutura parcial."""
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    api_client.post(
        f"/api/v1/admin/processos/{criado.json()['id']}/editais",
        {"number": "02", "year": 2026, "title": "Segundo"},
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "quickstart-s3-000001"},
    )
    primeiro, segundo = Edital.objects.order_by("number")
    preparador = actor_headers("preparador", ["edital:elaborar"], key="quickstart-s3-000002")

    assert (
        api_client.put(
            f"/api/v1/admin/editais/{primeiro.id}/rascunho",
            complete_draft(),
            format="json",
            **{**preparador, "HTTP_IF_MATCH": '"1"'},
        ).status_code
        == 200
    )

    # O mesmo rascunho reusa os identificadores já vinculados ao primeiro Edital.
    resposta = api_client.put(
        f"/api/v1/admin/editais/{segundo.id}/rascunho",
        complete_draft(),
        format="json",
        **{**preparador, "HTTP_IF_MATCH": '"1"'},
    )
    assert resposta.status_code == 409, resposta.status_code
    assert resposta.json()["code"] == "identifier_belongs_to_another_edital"
    assert not EventoCronograma.objects.filter(cronograma__edital=segundo).exists()
    assert EventoCronograma.objects.filter(cronograma__edital=primeiro).count() == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_quickstart_s4_revoked_homologation_returns_the_edital_to_review(
    api_client, manager_headers, process_payload
):
    """S4: revogar homologação antes da Publicação devolve o Edital para revisão."""
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()
    preparador = actor_headers("preparador", ["edital:elaborar", "edital:submeter"])
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        complete_draft(),
        format="json",
        **{**preparador, "HTTP_IF_MATCH": '"1"'},
    )
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/submissoes",
        format="json",
        **{**preparador, "HTTP_IF_MATCH": '"2"'},
    )
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **{**actor_headers("homologador", ["edital:homologar"]), "HTTP_IF_MATCH": '"3"'},
    )
    assert Edital.objects.get(pk=edital.pk).status == Edital.Status.HOMOLOGADO

    revogada = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/revogacoes-homologacao",
        {"reason": "Erro identificado na revisão"},
        format="json",
        **{
            **actor_headers("homologador", ["edital:homologar"], key="quickstart-s4-000001"),
            "HTTP_IF_MATCH": '"4"',
        },
    )
    assert revogada.status_code == 200
    assert revogada.json()["status"] == "EM_REVISAO"

    # Publicar após a revogação é recusado: não há homologação vigente.
    recusada = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/publicacoes",
        {"signatory": SIGNATORY},
        format="json",
        **{
            **actor_headers("publicador", ["edital:publicar"], key="quickstart-s4-000002"),
            "HTTP_IF_MATCH": '"5"',
        },
    )
    assert recusada.status_code == 409
    assert not Publicacao.objects.filter(edital=edital).exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_quickstart_s6_immediate_retification_takes_effect_on_publication(
    api_client, manager_headers, process_payload
):
    """S6: sem effectiveAt declarado, a vigência é o próprio instante da Publicação."""
    edital = publish_original(api_client, manager_headers, process_payload)
    retificacao = retify(api_client, edital, replace(VACANCIES, 5))
    publicacao = retificacao.publication

    assert publicacao.effective_at == publicacao.published_at
    consolidada = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert consolidada.valid_from == publicacao.published_at
    assert consolidada.content["profiles"][0]["immediateVacancies"] == 5

    original = VersaoConsolidada.objects.filter(edital=edital).earliest("materialized_at")
    assert original.content["profiles"][0]["immediateVacancies"] == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_quickstart_s7_retroactive_effective_date_is_rejected(
    api_client, manager_headers, process_payload
):
    """S7: effectiveAt anterior à Publicação é rejeitado e não produz efeito retroativo."""
    edital = publish_original(api_client, manager_headers, process_payload)
    passado = (timezone.now() - timedelta(days=1)).isoformat()
    retificacao = create_retification(
        api_client, edital, replace(VACANCIES, 5), effective_at=passado
    )
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao.id}/submissoes",
        format="json",
        **{
            **actor_headers("retificador", ["retificacao:submeter"], key="quickstart-s7-000001"),
            "HTTP_IF_MATCH": '"1"',
        },
    )
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao.id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **{
            **actor_headers("homologador-r", ["retificacao:homologar"], key="quickstart-s7-000002"),
            "HTTP_IF_MATCH": '"2"',
        },
    )
    recusada = api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao.id}/publicacoes",
        {"signatory": SIGNATORY},
        format="json",
        **{
            **actor_headers("publicador-r", ["retificacao:publicar"], key="quickstart-s7-000003"),
            "HTTP_IF_MATCH": '"3"',
        },
    )
    assert recusada.status_code == 422
    assert recusada.json()["code"] == "invalid_effective_at"
    assert Retificacao.objects.get(pk=retificacao.pk).status == Retificacao.Status.HOMOLOGADA
    assert Publicacao.objects.filter(edital=edital).count() == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_quickstart_s9_same_effective_time_without_conflict_accumulates(
    api_client, manager_headers, process_payload
):
    """S9: mesma vigência em caminhos independentes compõe um único snapshot com ambas."""
    edital = publish_original(api_client, manager_headers, process_payload)
    vigencia = (timezone.now() + timedelta(days=7)).isoformat()
    retify(api_client, edital, replace(VACANCIES, 42), effective_at=vigencia, suffix="a")
    retify(
        api_client, edital, replace(TITLE, "Título retificado"), effective_at=vigencia, suffix="b"
    )

    na_fronteira = api_client.get(
        f"/api/v1/public/editais/{edital.id}/versao-vigente", {"em": vigencia}
    ).json()
    assert na_fronteira["content"]["profiles"][0]["immediateVacancies"] == 42
    assert na_fronteira["content"]["title"] == "Título retificado"

    # A ordem física dos atos não pode alterar o resultado nem o hash.
    original = VersaoConsolidada.objects.filter(edital=edital).earliest("materialized_at")
    atos = [
        {
            "effectiveAt": item.publication.effective_at,
            "publicationOrder": item.publication.publication_order,
            "publicationId": str(item.publication_id),
            "changes": [
                {
                    "targetPath": alteracao.target_path,
                    "operation": alteracao.operation,
                    "newValue": alteracao.new_value,
                }
                for alteracao in item.alteracoes.all()
            ],
        }
        for item in Retificacao.objects.filter(
            edital=edital, status=Retificacao.Status.PUBLICADA
        ).select_related("publication")
    ]
    direto, _ = consolidate(original.content, atos)
    invertido, _ = consolidate(original.content, list(reversed(atos)))
    assert canonical_sha256(direto) == canonical_sha256(invertido)
    assert canonical_sha256(direto) == na_fronteira["contentHash"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_quickstart_s10_same_effective_time_with_conflict_is_decided_by_publication_order(
    api_client, manager_headers, process_payload
):
    """S10: no conflito vence a maior publicationOrder; o não conflitante continua acumulado."""
    edital = publish_original(api_client, manager_headers, process_payload)
    vigencia = (timezone.now() + timedelta(days=7)).isoformat()
    retify(
        api_client,
        edital,
        replace(VACANCIES, 10) + replace(TITLE, "Da primeira"),
        effective_at=vigencia,
        suffix="a",
    )
    segunda = retify(api_client, edital, replace(VACANCIES, 20), effective_at=vigencia, suffix="b")

    conteudo = api_client.get(
        f"/api/v1/public/editais/{edital.id}/versao-vigente", {"em": vigencia}
    ).json()
    assert conteudo["content"]["profiles"][0]["immediateVacancies"] == 20
    assert conteudo["content"]["title"] == "Da primeira"
    assert {
        "targetPath": VACANCIES,
        "publicationId": str(segunda.publication_id),
    } in conteudo["provenance"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.acceptance
def test_quickstart_s11_recomputed_temporal_function_matches_the_materialized_snapshot(
    api_client, manager_headers, process_payload
):
    """S11: recomputar a função temporal e comparar o hash ao snapshot materializado."""
    edital = publish_original(api_client, manager_headers, process_payload)
    for indice in range(1, 4):
        retify(api_client, edital, replace(VACANCIES, 100 + indice), suffix=f"r{indice}")

    original = VersaoConsolidada.objects.filter(edital=edital).earliest("materialized_at")
    materializada = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    atos = [
        {
            "effectiveAt": item.publication.effective_at,
            "publicationOrder": item.publication.publication_order,
            "publicationId": str(item.publication_id),
            "changes": [
                {
                    "targetPath": alteracao.target_path,
                    "operation": alteracao.operation,
                    "newValue": alteracao.new_value,
                }
                for alteracao in item.alteracoes.all()
            ],
        }
        for item in Retificacao.objects.filter(
            edital=edital, status=Retificacao.Status.PUBLICADA
        ).select_related("publication")
    ]
    recomputada, _ = consolidate(original.content, atos)
    assert canonical_sha256(recomputada) == materializada.content_hash
    assert recomputada == materializada.content


# --------------- as jornadas da revisão 012–013 que não são a E2E (quickstart)


@pytest.mark.acceptance
@pytest.mark.django_db
def test_j1_o_edital_publica_como_a_etapa_e_concluida(gestor, api_client, manager_headers):
    """Jornada 1: o snapshot e o documento dizem que aquela Etapa não pontua."""
    from tests.fixtures.resultado import montar_etapa_de_leitura_unica

    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=2900, codigo="2900", decisoria=True
    )
    conteudo = cenario["edital"].versoes_consolidadas.latest("materialized_at").content
    etapa = next(e for e in conteudo["stages"] if e["id"] == str(cenario["primeira"]))

    assert conteudo["schemaVersion"] == 7
    assert etapa["forma"] == "DECISORIA"
    assert etapa["minimumScore"] is None and etapa["maximumScore"] is None
    assert (etapa["rotuloFavoravel"], etapa["rotuloDesfavoravel"]) == ("Deferido", "Indeferido")


@pytest.mark.acceptance
@pytest.mark.django_db
def test_j4_a_etapa_decisoria_sem_carater_eliminatorio_nao_e_consolidavel():
    """Jornada 4: o Edital não publicou o efeito, e o sistema não o inventa (013, FR-047)."""
    from processo_seletivo.resultados.domain.regra import REGRA_INSUFICIENTE, impedimento_da_regra

    decisoria = {
        "id": "00000000-0000-0000-0000-0000000000c1",
        "forma": "DECISORIA",
        "rotuloFavoravel": "Deferido",
        "rotuloDesfavoravel": "Indeferido",
        "eliminatory": False,
        "evaluationsPerRegistration": 1,
    }

    codigo, frase = impedimento_da_regra(decisoria)

    assert codigo == REGRA_INSUFICIENTE
    assert "decisória" in frase and "desfavorável" in frase
    # E o simétrico, que passa a funcionar: eliminatória, decisória e sem nota mínima consolida.
    assert impedimento_da_regra({**decisoria, "eliminatory": True}) is None
