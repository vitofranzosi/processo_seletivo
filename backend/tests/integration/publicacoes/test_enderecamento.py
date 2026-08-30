"""Endereçamento por chave estável, de ponta a ponta (US1 da 004).

O que a `003` conseguia era recusar: quando a lista mudava de forma, a Retificação precisava ser
refeita mesmo que ninguém tivesse tocado no Perfil dela. Aqui se verifica o que passou a ser
possível — duas pessoas em Perfis diferentes publicam ambas — e o que continua sendo recusado, e
por qual código.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.publicacoes.models_retificacao import (
    AlteracaoNormativa,
    Retificacao,
    VersaoConsolidada,
)
from tests.fixtures.publicacao import (
    create_retification,
    publish_original,
    publish_retification,
    try_publish_retification,
)
from tests.fixtures.snapshot import PERFIL, colecoes_nao_declaradas, elementos_sem_chave
from tests.fixtures.snapshot import rascunho_publicavel as rascunho

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

P1, P2, P3 = PERFIL["A"], PERFIL["B"], PERFIL["C"]


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload, draft=rascunho())


@pytest.fixture
def base(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def elaborar(api_client, edital, changes, *, base=None, suffix="a"):
    """Cria a Retificação sem exigir 201: alguns cenários existem para ser recusados."""
    from tests.fixtures.edital import actor_headers

    base = base or VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    return api_client.post(
        f"/api/v1/admin/editais/{edital.id}/retificacoes",
        {
            "baseSnapshotId": str(base.id),
            "justification": f"Retificação {suffix}",
            "changes": changes,
        },
        format="json",
        **actor_headers("retificador", ["retificacao:elaborar"], key=f"retificacao-{suffix}-0001"),
    )


def renomear(identificador, nome):
    return [
        {
            "targetPath": f"/profiles/id={identificador}/name",
            "operation": "REPLACE",
            "newValue": nome,
        }
    ]


def remover(identificador):
    return [{"targetPath": f"/profiles/id={identificador}", "operation": "REMOVE"}]


# --- SC-001: o ganho ------------------------------------------------------------------------


def test_two_people_on_different_profiles_both_publish(api_client, edital, base):
    """SC-001. Na `003`, a segunda seria recusada sem ninguém ter tocado no Perfil dela."""
    renomeia_o_segundo = create_retification(
        api_client, edital, renomear(P2, "Perfil B renomeado"), base=base, suffix="a"
    )
    remove_o_primeiro = create_retification(api_client, edital, remover(P1), base=base, suffix="b")

    publish_retification(api_client, remove_o_primeiro, suffix="b")
    publish_retification(api_client, renomeia_o_segundo, suffix="a")

    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert [perfil["id"] for perfil in vigente.content["profiles"]] == [P2, P3]
    assert vigente.content["profiles"][0]["name"] == "Perfil B renomeado"


def test_two_acts_on_the_same_field_still_collide_by_hash(api_client, edital, base):
    """FR-014: a precondição por hash não saiu junto com a âncora — e é ela que recusa aqui."""
    primeira = create_retification(api_client, edital, renomear(P2, "Por A"), base=base, suffix="a")
    segunda = create_retification(api_client, edital, renomear(P2, "Por B"), base=base, suffix="b")
    publish_retification(api_client, primeira, suffix="a")

    recusa = try_publish_retification(api_client, segunda, suffix="b")

    assert recusa.status_code == 409, recusa.content
    assert recusa.data["code"] == "expected_hash_mismatch"
    assert f"/profiles/id={P2}/name" in recusa.data["detail"]


# --- SC-002 e SC-003: os dois momentos ------------------------------------------------------


def test_a_positional_path_is_refused_when_the_act_is_elaborated(api_client, edital):
    """SC-002: a recusa acontece na elaboração — o ato instável não chega a existir."""
    recusa = elaborar(
        api_client,
        edital,
        [{"targetPath": "/profiles/0/name", "operation": "REPLACE", "newValue": "X"}],
    )

    assert recusa.status_code == 422, recusa.content
    assert recusa.data["code"] == "positional_addressing_refused"
    assert "/profiles/0/name" in recusa.data["detail"]
    assert not Retificacao.objects.filter(edital=edital).exists()


def test_a_key_that_does_not_exist_is_refused_when_the_act_is_elaborated(api_client, edital):
    ausente = "00000000-0000-0000-0000-0000000005ff"
    recusa = elaborar(api_client, edital, renomear(ausente, "X"))

    assert recusa.status_code == 409, recusa.content
    assert recusa.data["code"] == "target_key_not_found"
    assert ausente in recusa.data["detail"]


def test_a_key_removed_in_the_meantime_is_refused_when_the_act_is_published(
    api_client, edital, base
):
    """SC-003: o segundo momento pergunta outra coisa.

    Na elaboração: existe no que eu vi? Na Publicação: ainda existe quando meu ato passa a valer?
    """
    renomeia_o_segundo = create_retification(
        api_client, edital, renomear(P2, "Renomeado"), base=base, suffix="a"
    )
    remove_o_segundo = create_retification(api_client, edital, remover(P2), base=base, suffix="b")
    publish_retification(api_client, remove_o_segundo, suffix="b")

    recusa = try_publish_retification(api_client, renomeia_o_segundo, suffix="a")

    assert recusa.status_code == 409, recusa.content
    assert recusa.data["code"] == "target_key_not_found"
    assert P2 in recusa.data["detail"]


# --- FR-011: a coleção atômica --------------------------------------------------------------


def test_requirements_is_replaced_whole(api_client, edital):
    caminho = f"/profiles/id={P1}/requirements"
    retificacao = create_retification(
        api_client,
        edital,
        [{"targetPath": caminho, "operation": "REPLACE", "newValue": ["Único requisito"]}],
        suffix="a",
    )
    publish_retification(api_client, retificacao, suffix="a")

    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert vigente.content["profiles"][0]["requirements"] == ["Único requisito"]


def test_requirements_may_be_emptied(api_client, edital):
    caminho = f"/profiles/id={P1}/requirements"
    retificacao = create_retification(
        api_client,
        edital,
        [{"targetPath": caminho, "operation": "REPLACE", "newValue": []}],
        suffix="a",
    )
    publish_retification(api_client, retificacao, suffix="a")

    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert vigente.content["profiles"][0]["requirements"] == []


def test_requirements_is_never_addressed_item_by_item(api_client, edital):
    recusa = elaborar(
        api_client,
        edital,
        [
            {
                "targetPath": f"/profiles/id={P1}/requirements/1",
                "operation": "REPLACE",
                "newValue": "z",
            }
        ],
    )

    assert recusa.status_code == 422, recusa.content
    assert recusa.data["code"] == "invalid_change"
    assert "substitua a lista inteira" in recusa.data["detail"]


# --- FR-009: chave repetida -----------------------------------------------------------------


def test_adding_a_profile_whose_key_already_exists_is_refused(api_client, edital, base):
    clone = {**base.content["profiles"][0], "code": "CLONE"}
    recusa = elaborar(
        api_client, edital, [{"targetPath": "/profiles/-", "operation": "ADD", "newValue": clone}]
    )

    assert recusa.status_code == 409, recusa.content
    assert recusa.data["code"] == "duplicate_key_in_collection"
    assert f"/profiles/id={P1}" in recusa.data["detail"]


def test_the_same_identifier_in_two_different_collections_is_irrelevant(api_client, edital, base):
    """A resolução é escopada à coleção do caminho: unicidade global não é pressuposta."""
    novo = {**base.content["profiles"][0], "id": base.content["schedule"][0]["id"], "code": "PX"}
    criada = elaborar(
        api_client, edital, [{"targetPath": "/profiles/-", "operation": "ADD", "newValue": novo}]
    )

    assert criada.status_code == 201, criada.content


# --- FR-004, FR-005: aninhamento -------------------------------------------------------------


def test_a_nested_modality_is_reached_by_the_composed_path(api_client, edital, base):
    # A Modalidade nasce com identificador do servidor: quem o conhece é o snapshot publicado.
    modalidade = base.content["profiles"][0]["competitionModalities"][1]["id"]
    caminho = f"/profiles/id={P1}/competitionModalities/id={modalidade}/description"
    retificacao = create_retification(
        api_client,
        edital,
        [{"targetPath": caminho, "operation": "REPLACE", "newValue": "Nova descrição"}],
        suffix="a",
    )
    publish_retification(api_client, retificacao, suffix="a")

    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    modalidade = vigente.content["profiles"][0]["competitionModalities"][1]
    assert modalidade["description"] == "Nova descrição"


# --- FR-012: o guarda das coleções, contra um snapshot publicado -----------------------------


def test_the_declared_collections_hold_for_a_really_published_snapshot(base):
    """FR-012 verificada onde importa: no conteúdo que o sistema efetivamente materializou."""
    assert colecoes_nao_declaradas(base.content) == []
    assert elementos_sem_chave(base.content) == []


# --- FR-018: o caminho publicado identifica a entidade ---------------------------------------


def test_a_published_path_names_the_entity_without_consulting_the_current_version(
    api_client, edital
):
    retificacao = create_retification(api_client, edital, renomear(P3, "Renomeado"), suffix="a")
    publish_retification(api_client, retificacao, suffix="a")

    alteracao = AlteracaoNormativa.objects.get(retificacao=retificacao)
    assert alteracao.target_path == f"/profiles/id={P3}/name"
    assert P3 in alteracao.target_path, (
        "a auditoria de um ato publicado não deve depender de consultar a versão vigente"
    )


# --- Erros de forma: recusa de borda e recusa de domínio -------------------------------------


def test_a_relative_path_is_refused_at_the_border(api_client, edital):
    """A única regra de forma que independe do contêiner, e por isso pode viver no serializer.

    Vira recusa de requisição inválida — `invalid_payload` —, e não erro de domínio: o caminho
    nem chega a ser interpretado.
    """
    recusa = elaborar(api_client, edital, [{"targetPath": "profiles", "operation": "REMOVE"}])

    assert recusa.status_code == 422, recusa.content
    assert recusa.data["code"] == "invalid_payload"
    assert "absoluto" in str(recusa.data)


def test_a_malformed_selector_over_a_list_is_an_invalid_change(api_client, edital):
    """`id=` em lista exige UUID. Em objeto, seria nome de chave — por isso a borda não decide."""
    recusa = elaborar(
        api_client,
        edital,
        [{"targetPath": "/profiles/id=nao-e-uuid/name", "operation": "REPLACE", "newValue": "X"}],
    )

    assert recusa.status_code == 422, recusa.content
    assert recusa.data["code"] == "invalid_change"
    assert "UUID" in recusa.data["detail"]


def test_a_path_that_does_not_exist_at_all_is_an_invalid_change(api_client, edital):
    recusa = elaborar(
        api_client, edital, [{"targetPath": "/inexistente", "operation": "REPLACE", "newValue": 1}]
    )

    assert recusa.status_code == 422, recusa.content
    assert recusa.data["code"] == "invalid_change"
    assert "Caminho inexistente" in recusa.data["detail"]


def test_two_acts_that_only_collide_at_a_later_boundary_are_refused_on_composition(
    api_client, edital, base
):
    """FR-009 no momento da Publicação, e não na elaboração.

    Cada ato acrescenta o mesmo Perfil, e cada um é válido sozinho contra a base que declarou.
    O de vigência futura publica primeiro; quando o de vigência imediata publica, o conteúdo
    vigente no início da **sua** vigência ainda não tem o Perfil do outro — a verificação da
    elaboração não vê nada. A colisão só existe na versão materializada para a fronteira
    posterior, que é onde a composição a encontra.
    """
    clone = {**base.content["profiles"][0], "id": "00000000-0000-0000-0000-0000000005ee"}
    daqui_a_um_mes = (timezone.now() + timedelta(days=30)).isoformat()
    futura = create_retification(
        api_client,
        edital,
        [{"targetPath": "/profiles/-", "operation": "ADD", "newValue": clone}],
        base=base,
        effective_at=daqui_a_um_mes,
        suffix="a",
    )
    imediata = create_retification(
        api_client,
        edital,
        [{"targetPath": "/profiles/-", "operation": "ADD", "newValue": clone}],
        base=base,
        suffix="b",
    )
    publish_retification(api_client, futura, suffix="a")

    recusa = try_publish_retification(api_client, imediata, suffix="b")

    assert recusa.status_code == 409, recusa.content
    assert recusa.data["code"] == "duplicate_key_in_collection"
    assert "/profiles/id=00000000-0000-0000-0000-0000000005ee" in recusa.data["detail"]


# --- O que não pode entrar numa coleção com chave -------------------------------------------


def test_appending_an_entity_without_a_key_is_refused_at_elaboration(api_client, edital):
    """Sem `id`, o Perfil entraria no conteúdo normativo sem poder ser endereçado nunca mais."""
    recusa = elaborar(
        api_client,
        edital,
        [
            {
                "targetPath": "/profiles/-",
                "operation": "ADD",
                "newValue": {"code": "SEM", "name": "Sem identificador"},
            }
        ],
    )

    assert recusa.status_code == 422, recusa.content
    assert recusa.data["code"] == "invalid_change"
    assert "UUID" in recusa.data["detail"]


def test_a_key_that_is_not_text_is_refused_and_not_an_internal_error(api_client, edital):
    """Antes disto, `id` de lista chegava à verificação de unicidade e virava 500."""
    recusa = elaborar(
        api_client,
        edital,
        [{"targetPath": "/profiles/-", "operation": "ADD", "newValue": {"id": ["a"], "code": "X"}}],
    )

    assert recusa.status_code == 422, recusa.content
    assert recusa.data["code"] == "invalid_change"


def test_adding_at_a_specific_position_is_refused(api_client, edital):
    """FR-006: acréscimo é ao fim. O seletor resolveria a posição de um Perfil existente."""
    recusa = elaborar(
        api_client,
        edital,
        [
            {
                "targetPath": f"/profiles/id={P2}",
                "operation": "ADD",
                "newValue": {"id": "00000000-0000-0000-0000-0000000005ff", "code": "PX"},
            }
        ],
    )

    assert recusa.status_code == 422, recusa.content
    assert recusa.data["code"] == "invalid_change"
    assert "token `-`" in recusa.data["detail"]


def test_replacing_an_entity_under_the_same_key_is_refused_at_elaboration(api_client, edital, base):
    """FR-009: a coleção terminaria íntegra, mas o ato trocaria uma entidade por outra."""
    substituto = {**base.content["profiles"][1], "name": "Substituto"}
    recusa = elaborar(
        api_client,
        edital,
        [
            {"targetPath": "/profiles/-", "operation": "ADD", "newValue": substituto},
            {"targetPath": f"/profiles/id={P2}", "operation": "REMOVE"},
        ],
    )

    assert recusa.status_code == 409, recusa.content
    assert recusa.data["code"] == "duplicate_key_in_collection"
    assert f"/profiles/id={P2}" in recusa.data["detail"]


def test_removing_and_recreating_under_the_same_key_still_publishes(api_client, edital, base):
    """A recíproca: apagar e recriar é ato declarado, e continua sendo admitido."""
    recriado = {**base.content["profiles"][1], "name": "Recriado"}
    retificacao = create_retification(
        api_client,
        edital,
        [
            {"targetPath": f"/profiles/id={P2}", "operation": "REMOVE"},
            {"targetPath": "/profiles/-", "operation": "ADD", "newValue": recriado},
        ],
        suffix="a",
    )
    publish_retification(api_client, retificacao, suffix="a")

    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert [p["id"] for p in vigente.content["profiles"]] == [P1, P3, P2]
    assert vigente.content["profiles"][-1]["name"] == "Recriado"


# --- A identidade pelas outras portas -------------------------------------------------------


@pytest.mark.parametrize(
    ("descricao", "change"),
    [
        (
            "substituir o Perfil inteiro trocando o id",
            {
                "targetPath": f"/profiles/id={P1}",
                "operation": "REPLACE",
                "newValue": {"id": "00000000-0000-0000-0000-0000000005ff", "code": "OUTRO"},
            },
        ),
        (
            "editar o campo id",
            {
                "targetPath": f"/profiles/id={P1}/id",
                "operation": "REPLACE",
                "newValue": "00000000-0000-0000-0000-0000000005ff",
            },
        ),
        ("apagar o campo id", {"targetPath": f"/profiles/id={P1}/id", "operation": "REMOVE"}),
        (
            "trocar a coleção inteira por itens sem id",
            {"targetPath": "/profiles", "operation": "REPLACE", "newValue": [{"code": "A"}]},
        ),
        (
            "trocar a coleção por um objeto",
            {"targetPath": "/profiles", "operation": "REPLACE", "newValue": {"a": 1}},
        ),
    ],
)
def test_identity_cannot_be_forged_through_any_door(api_client, edital, descricao, change):
    """O `ADD` era só uma das portas.

    Vigiar a operação alcançava uma; vigiar o estado resultante alcança todas.
    """
    recusa = elaborar(api_client, edital, [change])

    assert recusa.status_code == 422, f"{descricao}: {recusa.content}"
    assert recusa.data["code"] == "invalid_change"


def test_replacing_a_whole_profile_keeping_its_identity_publishes(api_client, edital, base):
    """A recíproca: reescrever o Perfil inteiro é ato legítimo, desde que ele continue sendo ele."""
    reescrito = {**base.content["profiles"][0], "name": "Reescrito por inteiro"}
    retificacao = create_retification(
        api_client,
        edital,
        [{"targetPath": f"/profiles/id={P1}", "operation": "REPLACE", "newValue": reescrito}],
        suffix="a",
    )
    publish_retification(api_client, retificacao, suffix="a")

    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert vigente.content["profiles"][0]["id"] == P1
    assert vigente.content["profiles"][0]["name"] == "Reescrito por inteiro"
