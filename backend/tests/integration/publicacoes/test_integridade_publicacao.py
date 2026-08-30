"""O portão da Publicação: nenhum Edital malformado passa a vigorar (US1 da 005).

**Por que o ato é gravado direto.** A US2 recusa o ato malformado já na elaboração, então ele não
chega à Publicação pelo caminho normal — e é justamente por isso que este portão não é redundante:
ele alcança a linha que chega por fora da borda, restaurada de backup ou criada por importação. É o
mesmo padrão que a `003` usa para a precondição de conteúdo ausente.
"""

import pytest
from django.utils import timezone

from processo_seletivo.publicacoes.models import DocumentoPublicado, Publicacao
from processo_seletivo.publicacoes.models_retificacao import (
    AlteracaoNormativa,
    Retificacao,
    VersaoConsolidada,
)
from processo_seletivo.shared.canonical import canonical_sha256
from tests.fixtures.edital import actor_headers
from tests.fixtures.publicacao import (
    create_retification,
    publish_original,
    publish_retification,
    try_publish_retification,
)
from tests.fixtures.snapshot import PERFIL
from tests.fixtures.snapshot import rascunho_publicavel as rascunho

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

P1, P2, P3 = PERFIL["A"], PERFIL["B"], PERFIL["C"]


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload, draft=rascunho())


@pytest.fixture
def base(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def ato_homologado_malformado(api_client, edital, base, alteracao, *, suffix="a"):
    """Uma Retificação homologada cuja alteração nunca passou pela elaboração.

    Nasce de um ato legítimo — que a elaboração aceita —, e a Alteração é reescrita direto no banco
    para o que se quer testar. É a linha que chega por fora da borda.
    """
    retificacao = create_retification(
        api_client,
        edital,
        [{"targetPath": f"/profiles/id={P1}/name", "operation": "REPLACE", "newValue": "Ajuste"}],
        base=base,
        suffix=suffix,
    )
    AlteracaoNormativa.objects.filter(retificacao=retificacao).update(
        target_path=alteracao["targetPath"],
        operation=alteracao["operation"],
        new_value=alteracao.get("newValue"),
        expected_previous_hash=alteracao.get("expectedPreviousHash", ""),
    )
    return retificacao


def precondicao(base, caminho):
    """O hash que a alteração reescrita precisa declarar para não ser recusada antes do portão."""
    from processo_seletivo.publicacoes.domain.conflicts import previous_hash

    return previous_hash(base.content, caminho)


def test_replace_parcial_de_perfil_e_recusado_na_publicacao(api_client, edital, base):
    """SC-001, e o rollback junto: recusar não pode deixar efeito parcial (FR-012)."""
    caminho = f"/profiles/id={P3}"
    mutilado = {
        "id": P3,
        "code": "MUTILADO",
        "name": "Sem o resto",
        "immediateVacancies": 1,
        "reserveType": "NONE",
    }
    ato = ato_homologado_malformado(
        api_client,
        edital,
        base,
        {
            "targetPath": caminho,
            "operation": "REPLACE",
            "newValue": mutilado,
            "expectedPreviousHash": precondicao(base, caminho),
        },
    )
    vigente_antes = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")

    recusa = try_publish_retification(api_client, ato, suffix="a")

    assert recusa.status_code == 422, recusa.content
    assert recusa.data["code"] == "blocking_findings"
    assert f"/profiles/id={P3}/requirements" in recusa.data["detail"]
    assert Publicacao.objects.filter(edital=edital).count() == 1
    assert DocumentoPublicado.objects.count() == 1
    assert VersaoConsolidada.objects.filter(edital=edital).count() == 1
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert canonical_sha256(vigente.content) == canonical_sha256(vigente_antes.content)


def test_remove_de_campo_obrigatorio_e_recusado_na_publicacao(api_client, edital, base):
    """SC-002."""
    caminho = f"/profiles/id={P2}/name"
    ato = ato_homologado_malformado(
        api_client,
        edital,
        base,
        {
            "targetPath": caminho,
            "operation": "REMOVE",
            "expectedPreviousHash": precondicao(base, caminho),
        },
    )

    recusa = try_publish_retification(api_client, ato, suffix="a")

    assert recusa.status_code == 422, recusa.content
    assert recusa.data["code"] == "blocking_findings"
    assert caminho in recusa.data["detail"]
    assert VersaoConsolidada.objects.filter(edital=edital).count() == 1


def test_a_fronteira_posterior_recusa_o_ato_inteiro(api_client, edital, base):
    """FR-003 e SC-005: verificar só a primeira fronteira deixaria a seguinte vigorar malformada.

    **A primeira fronteira do ato é válida.** É isso que torna o teste discriminante: uma
    implementação que verificasse apenas a versão que passa a vigorar de imediato publicaria este
    ato, e o Edital ficaria sem nenhum Perfil a partir da fronteira seguinte — sem que ninguém
    publicasse nada naquele dia.

    O arranjo: uma Retificação de vigência futura, já publicada, remove o Perfil A. O ato sob teste
    remove B e C, e vigora de imediato. Na fronteira de hoje sobra A, e o conteúdo é íntegro; na
    fronteira futura a composição aplica as duas e não sobra Perfil nenhum.

    O achado aqui é de raiz — "ao menos um Perfil" — e não por entidade, e isso não é acaso: a
    consolidação aplica os atos em ordem de vigência, de modo que o ato sob teste é sempre aplicado
    **antes** do futuro. Uma malformação de entidade que só aparecesse na fronteira posterior teria
    de ser introduzida pelo ato futuro, que já passou pela mesma verificação ao ser publicado.
    """
    daqui_a_um_mes = (timezone.now() + timezone.timedelta(days=30)).isoformat()
    futura = create_retification(
        api_client,
        edital,
        [{"targetPath": f"/profiles/id={P1}", "operation": "REMOVE"}],
        base=base,
        effective_at=daqui_a_um_mes,
        suffix="z",
    )
    publish_retification(api_client, futura, suffix="z")
    fronteiras_antes = VersaoConsolidada.objects.filter(edital=edital).count()
    vigente = VersaoConsolidada.objects.filter(edital=edital).order_by("valid_from").first()
    assert [p["id"] for p in vigente.content["profiles"]] == [P1, P2, P3]

    remove_os_outros_dois = create_retification(
        api_client,
        edital,
        [
            {"targetPath": f"/profiles/id={P2}", "operation": "REMOVE"},
            {"targetPath": f"/profiles/id={P3}", "operation": "REMOVE"},
        ],
        base=vigente,
        suffix="a",
    )

    recusa = try_publish_retification(api_client, remove_os_outros_dois, suffix="a")

    assert recusa.status_code == 422, recusa.content
    assert recusa.data["code"] == "blocking_findings"
    assert "Perfil" in recusa.data["detail"]
    assert "passaria a vigorar em" in recusa.data["detail"], "a recusa nomeia a fronteira"
    assert VersaoConsolidada.objects.filter(edital=edital).count() == fronteiras_antes


def test_o_mesmo_ato_publica_quando_nao_ha_fronteira_posterior(api_client, edital, base):
    """A recíproca, e a segunda metade da prova.

    Sem a Retificação de vigência futura, remover B e C deixa o Edital com um Perfil e é ato
    legítimo. O que recusa no teste anterior é a fronteira posterior, e não a remoção em si.
    """
    retificacao = create_retification(
        api_client,
        edital,
        [
            {"targetPath": f"/profiles/id={P2}", "operation": "REMOVE"},
            {"targetPath": f"/profiles/id={P3}", "operation": "REMOVE"},
        ],
        base=base,
        suffix="a",
    )

    publish_retification(api_client, retificacao, suffix="a")

    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert [p["id"] for p in vigente.content["profiles"]] == [P1]


def test_uma_retificacao_bem_formada_continua_publicando(api_client, edital, base):
    """FR-014, FR-015 e SC-004: o risco de uma verificação nova é recusar o legítimo."""
    novo = {
        **base.content["profiles"][0],
        "id": "00000000-0000-0000-0000-0000000005ff",
        "code": "PX",
        "description": "",
        "requirements": [],
        "reserveLimit": None,
        "classificationInformation": {},
        "competitionModalities": [],
    }
    retificacao = create_retification(
        api_client,
        edital,
        [
            {"targetPath": f"/profiles/id={P1}/name", "operation": "REPLACE", "newValue": "Novo"},
            {"targetPath": "/profiles/-", "operation": "ADD", "newValue": novo},
            {"targetPath": f"/profiles/id={P3}", "operation": "REMOVE"},
        ],
        base=base,
        suffix="a",
    )

    publish_retification(api_client, retificacao, suffix="a")

    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert [p["id"] for p in vigente.content["profiles"]] == [P1, P2, novo["id"]]
    assert vigente.content["profiles"][0]["name"] == "Novo"


def test_o_ato_recusado_permanece_homologado_e_pode_ser_devolvido(api_client, edital, base):
    """Recusar não descarta o ato: quem o preparou precisa poder corrigi-lo."""
    caminho = f"/profiles/id={P2}/name"
    ato = ato_homologado_malformado(
        api_client,
        edital,
        base,
        {
            "targetPath": caminho,
            "operation": "REMOVE",
            "expectedPreviousHash": precondicao(base, caminho),
        },
    )

    try_publish_retification(api_client, ato, suffix="a")

    ato.refresh_from_db()
    assert ato.status == Retificacao.Status.HOMOLOGADA
    devolvida = api_client.post(
        f"/api/v1/admin/retificacoes/{ato.id}/devolucoes",
        {"reason": "Conteúdo incompleto."},
        format="json",
        **{
            **actor_headers(
                "homologador-r", ["retificacao:homologar"], key="integridade-devolucao-0001"
            ),
            "HTTP_IF_MATCH": f'"{ato.revision}"',
        },
    )
    assert devolvida.status_code == 200, devolvida.content
