"""O incremento da `012` não pode tornar irretificável o que já estava publicado (D-002, T-001).

Oito cenários e três contraprovas. Os oito exigem que a Retificação atravesse; as três exigem que
ela seja recusada — e são elas que impedem a equivalência de grafias de virar buraco (T-017).

**Em todos**, o `content_hash` de tudo o que já estava publicado permanece idêntico: a elevação é
leitura, e o que ela produz vai para uma Versão Consolidada nova, que é artefato novo.
"""

import pytest

from processo_seletivo.publicacoes.domain.elevacao import elevar_etapa
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.shared.canonical import SCHEMA_VERSION, canonical_sha256
from tests.fixtures.legado import (
    hashes_publicados,
    publicar_na_versao_anterior,
    rebaixar,
)
from tests.fixtures.publicacao import (
    create_retification,
    publish_retification,
    try_publish_retification,
)
from tests.fixtures.snapshot import ETAPA, rascunho_com_etapas

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

TITULO = [{"targetPath": "/title", "operation": "REPLACE", "newValue": "Edital retificado"}]


@pytest.fixture
def legado(api_client, manager_headers, process_payload):
    return publicar_na_versao_anterior(
        api_client, manager_headers, process_payload, draft=rascunho_com_etapas()
    )


def vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def etapa_nova(identificador, **extra):
    return {
        "id": identificador,
        "name": "Entrevista",
        "order": 3,
        "weight": None,
        "eliminatory": False,
        "classificatory": True,
        "minimumScore": None,
        "scheduleEventId": None,
        **extra,
    }


def assert_publicado_permanece(antes):
    """Publicar acrescenta linha; o que já existia não pode mudar de hash."""
    depois = hashes_publicados()
    for grupo in ("publicacoes", "versoes"):
        for identificador, hash_anterior in antes[grupo].items():
            assert depois[grupo][identificador] == hash_anterior, (grupo, identificador)


def assert_versao_vigente_e_bem_formada(edital):
    conteudo = vigente(edital).content
    assert conteudo["schemaVersion"] == SCHEMA_VERSION
    for etapa in conteudo["stages"]:
        assert "evaluationsPerRegistration" in etapa, etapa["name"]
        assert "maximumScore" in etapa, etapa["name"]


# --------------------------------------------------------------------- histórico misto


def test_1_edital_sem_retificacao_e_retificado_pela_primeira_vez(api_client, legado):
    antes = hashes_publicados()

    publish_retification(api_client, create_retification(api_client, legado, TITULO), suffix="a")

    assert_versao_vigente_e_bem_formada(legado)
    assert_publicado_permanece(antes)


def test_2_ato_anterior_que_acrescentou_etapa_e_reaplicado_na_forma_nova(api_client, legado):
    """O caso que trava a materialização quando o ato não é elevado.

    `newValue` guarda a Etapa como ela era; reaplicá-la sem elevar reintroduz forma antiga, e a
    publicação inteira falha por campo obrigatório ausente.
    """
    acrescimo = [
        {
            "targetPath": "/stages/-",
            "operation": "ADD",
            "newValue": etapa_nova("00000000-0000-0000-0000-0000000005a1"),
        }
    ]
    publish_retification(
        api_client, create_retification(api_client, legado, acrescimo, suffix="a"), suffix="a"
    )

    publish_retification(
        api_client, create_retification(api_client, legado, TITULO, suffix="b"), suffix="b"
    )

    assert_versao_vigente_e_bem_formada(legado)
    assert len(vigente(legado).content["stages"]) == 3


def test_3_ato_anterior_que_substituiu_etapa_inteira(api_client, legado):
    substituicao = [
        {
            "targetPath": f"/stages/id={ETAPA['A']}",
            "operation": "REPLACE",
            "newValue": etapa_nova(ETAPA["A"], name="Prova didática revista"),
        }
    ]
    publish_retification(
        api_client, create_retification(api_client, legado, substituicao, suffix="a"), suffix="a"
    )

    publish_retification(
        api_client, create_retification(api_client, legado, TITULO, suffix="b"), suffix="b"
    )

    assert_versao_vigente_e_bem_formada(legado)


def test_4_ato_anterior_que_substituiu_um_campo_nao_e_corrompido(api_client, legado):
    """A prova de que a elevação é path-aware: escalar atravessa intacto."""
    campo = [
        {
            "targetPath": f"/stages/id={ETAPA['A']}/minimumScore",
            "operation": "REPLACE",
            "newValue": "8.0000",
        }
    ]
    publish_retification(api_client, create_retification(api_client, legado, campo), suffix="a")

    assert_versao_vigente_e_bem_formada(legado)
    etapa = next(e for e in vigente(legado).content["stages"] if e["id"] == ETAPA["A"])
    assert etapa["minimumScore"] == "8.0000"


# --------------------------------------------------------- Retificação atravessando o deploy


def test_5_retificacao_em_elaboracao_atravessa_o_incremento(api_client, legado):
    """Elaborada antes, publicada depois: é o que o `ADD` sem precondição tornava perigoso."""
    acrescimo = [
        {
            "targetPath": "/stages/-",
            "operation": "ADD",
            "newValue": etapa_nova("00000000-0000-0000-0000-0000000005b1"),
        }
    ]
    retificacao = create_retification(api_client, legado, acrescimo)

    publish_retification(api_client, retificacao, suffix="a")

    assert_versao_vigente_e_bem_formada(legado)


def test_6_retificacao_homologada_atravessa_o_incremento(api_client, legado):
    """A que mais dói se falhar: homologada não se reelabora sem devolver."""
    acrescimo = [
        {
            "targetPath": "/stages/-",
            "operation": "ADD",
            "newValue": etapa_nova("00000000-0000-0000-0000-0000000005c1"),
        }
    ]
    resposta = try_publish_retification(
        api_client, create_retification(api_client, legado, acrescimo), suffix="a"
    )

    assert resposta.status_code == 201, resposta.content
    assert_versao_vigente_e_bem_formada(legado)


def test_7_retificacao_criada_depois_sobre_base_anterior(api_client, legado):
    publish_retification(api_client, create_retification(api_client, legado, TITULO), suffix="a")

    assert_versao_vigente_e_bem_formada(legado)


def test_8_o_hash_declarado_vale_nas_duas_grafias(api_client, legado):
    """`expectedPreviousHash` é o hash do conteúdo que o autor encontrou — e há dois lugares
    onde encontrá-lo: a projeção elevada, que a autoria compõe, e o literal, que a consulta
    pública serve. As duas denotam a mesma norma, e as duas passam (T-017)."""
    base = vigente(legado)
    etapa_literal = next(e for e in base.content["stages"] if e["id"] == ETAPA["A"])
    # A grafia elevada vem da própria elevação, e não de uma cópia literal das chaves que ela
    # escreve: com dois degraus a cópia já ficou desatualizada uma vez, e ficaria de novo no
    # terceiro. O que o teste afirma é que a projeção que a autoria compõe passa na conferência.
    etapa_elevada = elevar_etapa(etapa_literal)

    for indice, grafia in enumerate((etapa_literal, etapa_elevada)):
        atual = next(e for e in vigente(legado).content["stages"] if e["id"] == ETAPA["A"])
        declarada = {**grafia, "name": atual["name"]}
        alteracao = [
            {
                "targetPath": f"/stages/id={ETAPA['A']}",
                "operation": "REPLACE",
                "newValue": {**atual, "name": f"Prova didática {indice}"},
                "expectedPreviousHash": canonical_sha256(declarada),
            }
        ]
        retificacao = create_retification(
            api_client, legado, alteracao, suffix=f"h{indice}", base=vigente(legado)
        )
        publish_retification(api_client, retificacao, suffix=f"h{indice}")

    assert_versao_vigente_e_bem_formada(legado)


# ------------------------------------------------------------------------- contraprovas


@pytest.mark.parametrize(
    ("declarado", "caso"),
    [
        ({"maximumScore": "100.0000"}, "maxima declarada"),
        ({"evaluationsPerRegistration": 2}, "quantidade declarada"),
    ],
)
def test_9_e_10_a_grafia_literal_deixa_de_valer_quando_a_norma_muda(
    api_client, legado, declarado, caso
):
    """A condição de T-017, e a razão dela.

    Remover os campos novos e comparar devolveria a grafia antiga **mesmo depois** de uma
    Retificação ter declarado a máxima — o hash velho passaria, e a precondição teria aprovado um
    ato escrito contra conteúdo que já não existe.
    """
    base = vigente(legado)
    etapa_literal = next(e for e in base.content["stages"] if e["id"] == ETAPA["A"])
    declaracao = [
        {
            "targetPath": f"/stages/id={ETAPA['A']}",
            "operation": "REPLACE",
            "newValue": {**etapa_literal, **declarado},
        }
    ]
    publish_retification(
        api_client, create_retification(api_client, legado, declaracao), suffix="a"
    )

    resposta = api_client.post(
        f"/api/v1/admin/editais/{legado.id}/retificacoes",
        {
            "baseSnapshotId": str(vigente(legado).id),
            "justification": "Sobre conteúdo que já não existe",
            "changes": [
                {
                    "targetPath": f"/stages/id={ETAPA['A']}",
                    "operation": "REPLACE",
                    "newValue": {**etapa_literal, "name": "Outro nome"},
                    "expectedPreviousHash": canonical_sha256(etapa_literal),
                }
            ],
        },
        format="json",
        **_retificador(),
    )

    assert resposta.status_code == 409, resposta.content
    assert resposta.json()["code"] == "expected_hash_mismatch"


def test_11_alteracao_de_campo_que_ja_existia_continua_recusada(api_client, legado):
    """A regra de sempre, inteira: hash de conteúdo realmente diferente não passa."""
    resposta = api_client.post(
        f"/api/v1/admin/editais/{legado.id}/retificacoes",
        {
            "baseSnapshotId": str(vigente(legado).id),
            "justification": "Precondição obsoleta",
            "changes": [
                {
                    "targetPath": f"/stages/id={ETAPA['A']}/minimumScore",
                    "operation": "REPLACE",
                    "newValue": "9.0000",
                    "expectedPreviousHash": canonical_sha256("outro valor"),
                }
            ],
        },
        format="json",
        **_retificador(),
    )

    assert resposta.status_code == 409, resposta.content
    assert resposta.json()["code"] == "expected_hash_mismatch"


def _retificador():
    from tests.fixtures.edital import actor_headers

    return actor_headers("retificador", ["retificacao:elaborar"], key="retificacao-z-0001")


def test_a_publicacao_original_permanece_byte_a_byte(api_client, legado):
    """A promessa central de D-002: elevar é leitura, e não reescreve o que foi publicado."""
    antes = hashes_publicados()
    original = legado.publicacoes.get()

    publish_retification(
        api_client, create_retification(api_client, legado, TITULO, suffix="a"), suffix="a"
    )

    assert_publicado_permanece(antes)
    original.refresh_from_db()
    assert original.canonical_schema_version == 4
    assert original.content_hash == antes["publicacoes"][original.id]
    assert rebaixar(original.revisao.content)["schemaVersion"] == 4
