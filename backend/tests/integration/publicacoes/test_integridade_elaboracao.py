"""A recusa na elaboração: quem compõe descobre antes de submeter (US2 da 005).

Não muda o que é impedido — a US1 já impede —, muda quando. Sem isto, o erro só aparece depois de a
submissão e a homologação terem consumido o tempo de outras pessoas.
"""

import pytest

from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.edital import actor_headers
from tests.fixtures.publicacao import create_retification, publish_original, publish_retification
from tests.fixtures.snapshot import PERFIL, perfil_mutilado
from tests.fixtures.snapshot import rascunho_publicavel as rascunho

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

P1, P2, P3 = PERFIL["A"], PERFIL["B"], PERFIL["C"]


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload, draft=rascunho())


@pytest.fixture
def base(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def elaborar(api_client, edital, base, changes, *, suffix="a"):
    """Cria a Retificação sem exigir 201: estes cenários existem para ser recusados."""
    return api_client.post(
        f"/api/v1/admin/editais/{edital.id}/retificacoes",
        {"baseSnapshotId": str(base.id), "justification": "Ajuste", "changes": changes},
        format="json",
        **actor_headers("retificador", ["retificacao:elaborar"], key=f"integridade-{suffix}-0001"),
    )


REMOVER_NOME = [{"targetPath": f"/profiles/id={P2}/name", "operation": "REMOVE"}]


def test_a_criacao_recusa_o_replace_parcial(api_client, edital, base):
    """SC-001 no primeiro momento."""
    recusa = elaborar(
        api_client,
        edital,
        base,
        [
            {
                "targetPath": f"/profiles/id={P3}",
                "operation": "REPLACE",
                "newValue": perfil_mutilado(P3),
            }
        ],
    )

    assert recusa.status_code == 422, recusa.content
    assert recusa.data["code"] == "blocking_findings"
    assert not Retificacao.objects.filter(edital=edital).exists(), "o ato não chega a existir"


def test_a_criacao_recusa_o_remove_de_campo_obrigatorio(api_client, edital, base):
    recusa = elaborar(api_client, edital, base, REMOVER_NOME)

    assert recusa.status_code == 422, recusa.content
    assert recusa.data["code"] == "blocking_findings"
    assert not Retificacao.objects.filter(edital=edital).exists()


def test_a_atualizacao_do_rascunho_recusa_o_mesmo(api_client, edital, base):
    """A mesma verificação nos dois pontos de elaboração (FR-002)."""
    retificacao = create_retification(
        api_client,
        edital,
        [{"targetPath": f"/profiles/id={P1}/name", "operation": "REPLACE", "newValue": "Ajuste"}],
        base=base,
        suffix="a",
    )

    recusa = api_client.put(
        f"/api/v1/admin/retificacoes/{retificacao.id}/rascunho",
        {"justification": "Ajuste", "changes": REMOVER_NOME},
        format="json",
        **{
            **actor_headers("retificador", ["retificacao:elaborar"], key="integridade-r-0001"),
            "HTTP_IF_MATCH": f'"{retificacao.revision}"',
        },
    )

    assert recusa.status_code == 422, recusa.content
    assert recusa.data["code"] == "blocking_findings"
    retificacao.refresh_from_db()
    assert retificacao.alteracoes.get().target_path == f"/profiles/id={P1}/name", (
        "o rascunho anterior permanece intacto"
    )


@pytest.mark.parametrize(
    ("descricao", "change", "trecho"),
    [
        ("campo ausente", REMOVER_NOME[0], "não está presente"),
        (
            "tipo diferente",
            {"targetPath": f"/profiles/id={P2}/name", "operation": "REPLACE", "newValue": []},
            "deveria ser texto",
        ),
        (
            "nulo indevido",
            {"targetPath": f"/profiles/id={P2}/locality", "operation": "REPLACE", "newValue": None},
            "não admite valor nulo",
        ),
        (
            "fora da restrição",
            {
                "targetPath": f"/profiles/id={P2}/immediateVacancies",
                "operation": "REPLACE",
                "newValue": -3,
            },
            "não admite valor menor",
        ),
        (
            "formato inválido",
            {
                "targetPath": "/schedule/id=00000000-0000-0000-0000-000000000521/startAt",
                "operation": "REPLACE",
                "newValue": "ontem",
            },
            "não satisfaz o formato",
        ),
    ],
)
def test_a_recusa_diz_onde_e_o_que(api_client, edital, base, descricao, change, trecho):
    """FR-011 e SC-003: sem o quê, quem recebe sabe onde e não sabe o que corrigir."""
    recusa = elaborar(api_client, edital, base, [change])

    assert recusa.status_code == 422, f"{descricao}: {recusa.content}"
    assert change["targetPath"] in recusa.data["detail"], "o caminho nomeia a entidade"
    assert trecho in recusa.data["detail"], "a mensagem diz qual violação ocorreu"


def test_corrigir_e_reenviar_e_aceito_sem_etapa_nova(api_client, edital, base):
    """FR-014: a recusa não cria burocracia — o mesmo endpoint aceita o conteúdo corrigido."""
    assert elaborar(api_client, edital, base, REMOVER_NOME).status_code == 422

    aceita = elaborar(
        api_client,
        edital,
        base,
        [
            {
                "targetPath": f"/profiles/id={P2}/name",
                "operation": "REPLACE",
                "newValue": "Corrigido",
            }
        ],
        suffix="b",
    )

    assert aceita.status_code == 201, aceita.content
    publicada = publish_retification(
        api_client, Retificacao.objects.get(pk=aceita.data["id"]), suffix="b"
    )
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert vigente.content["profiles"][1]["name"] == "Corrigido"
    assert publicada.status == Retificacao.Status.PUBLICADA


def test_a_precondicao_de_conteudo_prevalece_quando_ambas_valem(api_client, edital, base):
    """A causa serve melhor que a consequência.

    Outra pessoa publicou no intervalo, e o ato desta chegaria malformado. Dizer "o conteúdo
    anterior não corresponde" aponta o que fazer — refazer sobre a versão atual; dizer "está
    incompleto" descreveria a consequência e esconderia a causa.
    """
    publish_retification(
        api_client,
        create_retification(
            api_client,
            edital,
            [
                {
                    "targetPath": f"/profiles/id={P2}/name",
                    "operation": "REPLACE",
                    "newValue": "Alterado por outra",
                }
            ],
            base=base,
            suffix="z",
        ),
        suffix="z",
    )

    recusa = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/retificacoes",
        {
            "baseSnapshotId": str(base.id),
            "justification": "Ajuste",
            "changes": [
                {
                    "targetPath": f"/profiles/id={P2}/name",
                    "operation": "REMOVE",
                    "expectedPreviousHash": "hash-que-nao-confere-mais",
                }
            ],
        },
        format="json",
        **actor_headers("retificador", ["retificacao:elaborar"], key="integridade-p-0001"),
    )

    assert recusa.status_code == 409, recusa.content
    assert recusa.data["code"] == "expected_hash_mismatch"
