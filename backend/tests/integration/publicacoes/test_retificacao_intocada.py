"""O pipeline de Retificação se comporta como antes para conteúdo na versão vigente (FR-100).

A `012` tocou **quatro** módulos do fluxo — a leitura do conteúdo-base, a reaplicação dos atos, a
projeção que o autor compõe e a semântica da precondição —, e a última alcança toda Retificação, e
não só as de base anterior. FR-061 protege conteúdo, versão, hash e documento; este arquivo protege
o **comportamento**.

O que ele afirma: para Edital inteiramente na versão vigente, precondição, detecção de conflito,
consolidação, efeito prático e materialização produzem o mesmo resultado de sempre.
"""

import pytest

from processo_seletivo.publicacoes.domain.conflicts import HASH_MISMATCH, content_conflicts
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.shared.canonical import SCHEMA_VERSION, canonical_sha256
from tests.fixtures.comissao import ETAPA_A1, rascunho_com_etapas
from tests.fixtures.edital import caminho_perfil, identificador
from tests.fixtures.publicacao import (
    create_retification,
    publish_original,
    publish_retification,
    try_publish_retification,
)

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ALTERACAO = [{"targetPath": caminho_perfil("name"), "operation": "REPLACE", "newValue": "Outro"}]
ETAPA_A1_ID = identificador(ETAPA_A1, 0)


@pytest.fixture
def publicado(api_client, manager_headers, process_payload):
    """Publicado **agora**, portanto na versão canônica vigente — sem elevação envolvida."""
    return publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_com_etapas()
    )


def vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def test_o_conteudo_ja_nasce_na_versao_vigente(publicado):
    """A precondição de tudo o mais: aqui a elevação não tem o que fazer."""
    assert vigente(publicado).content["schemaVersion"] == SCHEMA_VERSION


def test_retificar_continua_funcionando_ponta_a_ponta(api_client, publicado):
    antes = vigente(publicado).id

    publish_retification(api_client, create_retification(api_client, publicado, ALTERACAO))

    nova = vigente(publicado)
    assert nova.id != antes
    assert nova.content["schemaVersion"] == SCHEMA_VERSION
    assert nova.content["profiles"][0]["name"] == "Outro"


def test_a_precondicao_por_hash_continua_recusando_conteudo_obsoleto(api_client, publicado):
    """FR-036 inteira: hash de conteúdo diferente não passa, e a mensagem é a de sempre."""
    resposta = api_client.post(
        f"/api/v1/admin/editais/{publicado.id}/retificacoes",
        {
            "baseSnapshotId": str(vigente(publicado).id),
            "justification": "Precondição obsoleta",
            "changes": [
                {
                    "targetPath": caminho_perfil("name"),
                    "operation": "REPLACE",
                    "newValue": "Outro",
                    "expectedPreviousHash": canonical_sha256("valor que nunca esteve lá"),
                }
            ],
        },
        format="json",
        **_retificador("hash"),
    )

    assert resposta.status_code == 409
    assert resposta.json()["code"] == "expected_hash_mismatch"


def test_a_equivalencia_de_grafias_nao_alcanca_conteudo_vigente(publicado):
    """A exceção de T-017 vale onde a elevação alcança — e **só** ali.

    Numa Etapa já na forma nova com máxima declarada, existe uma grafia só: o hash da forma
    reduzida não é candidato, e a precondição recusa como recusaria antes desta feature.
    """
    conteudo = vigente(publicado).content
    etapa = next(e for e in conteudo["stages"] if e["id"] == ETAPA_A1_ID)
    reduzida = {
        chave: valor
        for chave, valor in etapa.items()
        if chave not in ("evaluationsPerRegistration", "maximumScore")
    }
    declarada = {**etapa, "maximumScore": "100.0000"}
    atual = {**conteudo, "stages": [declarada]}

    conflitos = content_conflicts(
        atual,
        [
            {
                "targetPath": f"/stages/id={ETAPA_A1_ID}",
                "operation": "REPLACE",
                "newValue": {**declarada, "name": "Outro"},
                "expectedPreviousHash": canonical_sha256(reduzida),
            }
        ],
    )

    assert HASH_MISMATCH in conflitos


def test_o_efeito_pratico_continua_sendo_exigido(api_client, publicado):
    """Uma Retificação que não muda nada continua sendo recusada (FR-026 da 004)."""
    atual = vigente(publicado).content["profiles"][0]["name"]

    resposta = api_client.post(
        f"/api/v1/admin/editais/{publicado.id}/retificacoes",
        {
            "baseSnapshotId": str(vigente(publicado).id),
            "justification": "Sem efeito",
            "changes": [
                {"targetPath": caminho_perfil("name"), "operation": "REPLACE", "newValue": atual}
            ],
        },
        format="json",
        **_retificador("efeito"),
    )

    assert resposta.status_code == 422
    assert resposta.json()["code"] == "no_effective_change"


def test_a_consolidacao_compoe_duas_retificacoes_como_antes(api_client, publicado):
    """A reaplicação dos atos, que é onde a elevação passou a entrar."""
    publish_retification(
        api_client, create_retification(api_client, publicado, ALTERACAO, suffix="a"), suffix="a"
    )
    segunda = [
        {
            "targetPath": caminho_perfil("locality"),
            "operation": "REPLACE",
            "newValue": "Outra cidade",
        }
    ]
    publish_retification(
        api_client, create_retification(api_client, publicado, segunda, suffix="b"), suffix="b"
    )

    conteudo = vigente(publicado).content
    assert conteudo["profiles"][0]["name"] == "Outro"
    assert conteudo["profiles"][0]["locality"] == "Outra cidade"


def test_a_publicacao_original_permanece_intocada(api_client, publicado):
    """FR-061 e FR-100 juntos: nem o conteúdo nem o comportamento mudaram."""
    original = publicado.publicacoes.get()
    hash_antes, versao_antes = original.content_hash, original.canonical_schema_version

    publish_retification(api_client, create_retification(api_client, publicado, ALTERACAO))

    original.refresh_from_db()
    assert original.content_hash == hash_antes
    assert original.canonical_schema_version == versao_antes


def test_alteracao_inaplicavel_continua_sendo_recusada(api_client, publicado):
    """Remover o que já não existe: a recusa da 004, inalterada."""
    retificacao = create_retification(
        api_client,
        publicado,
        [{"targetPath": f"/stages/id={ETAPA_A1_ID}", "operation": "REMOVE"}],
        suffix="a",
    )
    publish_retification(api_client, retificacao, suffix="a")

    resposta = api_client.post(
        f"/api/v1/admin/editais/{publicado.id}/retificacoes",
        {
            "baseSnapshotId": str(vigente(publicado).id),
            "justification": "Remover de novo",
            "changes": [{"targetPath": f"/stages/id={ETAPA_A1_ID}", "operation": "REMOVE"}],
        },
        format="json",
        **_retificador("remove"),
    )

    assert resposta.status_code == 409


def test_uma_retificacao_homologada_publica_normalmente(api_client, publicado):
    """O percurso inteiro, sem elevação em jogo — que é o caso comum daqui para a frente."""
    resposta = try_publish_retification(
        api_client, create_retification(api_client, publicado, ALTERACAO, suffix="c"), suffix="c"
    )

    assert resposta.status_code == 201, resposta.content


def _retificador(sufixo="0001"):
    """A chave de idempotência precisa ter 16 caracteres ou mais — o contrato da 001 já exige."""
    from tests.fixtures.edital import actor_headers

    return actor_headers(
        "retificador", ["retificacao:elaborar"], key=f"retificacao-intocada-{sufixo}"
    )
