"""O barema pela API do rascunho, na Retificação e no reaproveitamento (146, T003, T006, T012).

O Edital é publicado pelo caminho real, e a Retificação pelo da API — que é o mesmo que a tela da
Retificação percorre depois de traduzir o formulário em alterações. A tela tem os próprios testes em
`tests/interface/test_barema_na_retificacao.py`.
"""

import copy

import pytest

from processo_seletivo.editais.application.reaproveitamento import reaproveitar_edital
from processo_seletivo.editais.models.etapas import CriterioAvaliacao, EtapaAvaliacao
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.selectors import effective_version
from tests.conftest import ator_institucional
from tests.fixtures.edital import actor_headers, complete_draft
from tests.fixtures.papel_de_producao import como_producao  # noqa: F401
from tests.fixtures.publicacao import create_retification, publish_original, retify

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ETAPA = "aaaaaaaa-0000-4000-8000-000000014670"
DECISORIA = "aaaaaaaa-0000-4000-8000-000000014671"
TITULOS = "aaaaaaaa-0000-4000-8000-000000014672"
DO_PERFIL = "aaaaaaaa-0000-4000-8000-000000014673"
DOUTORADO = "aaaaaaaa-0000-4000-8000-000000014674"
MESTRADO = "aaaaaaaa-0000-4000-8000-000000014675"
NOVO = "aaaaaaaa-0000-4000-8000-000000014676"


def criterio(identificador=DOUTORADO, **campos):
    return {
        "id": identificador,
        "name": "Diploma de Doutorado",
        "description": "",
        "maximumScore": "20.0000",
        "pointsPerUnit": "20.0000",
        "unitLabel": "diploma",
        "documentRequirementId": TITULOS,
        **campos,
    }


def rascunho(criterios=None, seed=0):
    criterios = (
        [
            criterio(),
            criterio(
                MESTRADO,
                name="Diploma de Mestrado",
                maximumScore="15.0000",
                pointsPerUnit="15.0000",
            ),
        ]
        if criterios is None
        else criterios
    )
    draft = complete_draft(seed)
    draft["stages"] = [
        {
            "id": ETAPA,
            "name": "Prova de Títulos",
            "order": 1,
            "classificatory": True,
            "maximumScore": "35.0000",
            "criteria": criterios,
        }
    ]
    draft["documentRequirements"] = [
        {
            "id": TITULOS,
            "key": "titulos",
            "name": "Títulos acadêmicos",
            "required": False,
            "order": 1,
        },
        {
            "id": DO_PERFIL,
            "key": "do-perfil",
            "name": "Declaração do Perfil",
            "required": False,
            "order": 2,
            "profileId": draft["profiles"][0]["id"],
        },
    ]
    return draft


def barema(edital):
    return [
        (str(c.id), c.nome, str(c.maxima), c.unidade)
        for c in CriterioAvaliacao.objects.filter(etapa__edital=edital).order_by("ordem")
    ]


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    return Edital.objects.get()


def put(api_client, edital, draft, key="barema-api-0001"):
    edital.refresh_from_db()
    return api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        draft,
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key=key),
            "HTTP_IF_MATCH": f'"{edital.revision}"',
        },
    )


# --- a API do rascunho (FR-5213) ------------------------------------------------------------------


def test_a_api_grava_o_barema_na_ordem_do_envio(api_client, edital):
    resposta = put(api_client, edital, rascunho())

    assert resposta.status_code == 200, resposta.content
    assert barema(edital) == [
        (DOUTORADO, "Diploma de Doutorado", "20.0000", "diploma"),
        (MESTRADO, "Diploma de Mestrado", "15.0000", "diploma"),
    ]


def test_etapa_sem_a_chave_e_gravada_sem_criterios(api_client, edital):
    """FR-5213: a ausência é a lista vazia — e regravar sem a chave tira o barema que havia."""
    assert put(api_client, edital, rascunho()).status_code == 200
    draft = rascunho()
    del draft["stages"][0]["criteria"]
    draft["stages"][0]["maximumScore"] = "35.0000"

    resposta = put(api_client, edital, draft, key="barema-api-0002")

    assert resposta.status_code == 200, resposta.content
    assert barema(edital) == []
    assert EtapaAvaliacao.objects.filter(edital=edital).count() == 1


def _outro_edital(api_client, manager_headers, chave):
    criado = api_client.post(
        "/api/v1/admin/processos",
        {
            "institutionalCode": f"PS-2027-{chave}",
            "title": "Outro Processo Seletivo",
            "firstEdital": {"number": "47", "year": 2027, "title": "Outro Edital"},
        },
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"outro-edital-{chave}-0001"},
    )
    assert criado.status_code == 201, criado.content
    return Edital.objects.get(processo_id=criado.json()["id"])


def test_criterio_de_outro_edital_e_recusado(api_client, manager_headers, edital):
    """A identidade do critério não muda de ficha: a do outro Edital é recusada com 409."""
    assert put(api_client, edital, rascunho()).status_code == 200
    outro = _outro_edital(api_client, manager_headers, "146")
    # Perfis e Eventos de outra semente: o que colide é só o barema.
    draft = rascunho(seed=1)
    draft["stages"][0]["id"] = "aaaaaaaa-0000-4000-8000-000000014679"

    resposta = put(api_client, outro, draft, key="barema-api-0003")

    assert resposta.status_code == 409, resposta.content
    assert resposta.json()["code"] == "identifier_belongs_to_another_edital"
    assert resposta.json()["detail"].endswith(f"{DOUTORADO}, {MESTRADO}")


@pytest.mark.parametrize(
    ("ajuste", "frase"),
    [
        (
            {
                "forma": "DECISORIA",
                "maximumScore": None,
                "rotuloFavoravel": "Apto",
                "rotuloDesfavoravel": "Inapto",
            },
            "concluída com decisão, sem nota",
        ),
        ({"maximumScore": "100.0000"}, "a soma das máximas dos critérios do barema, 35"),
    ],
    ids=["decisoria", "soma"],
)
def test_a_api_recusa_o_barema_incoerente(api_client, edital, ajuste, frase):
    draft = rascunho()
    draft["stages"][0].update(ajuste)

    resposta = put(api_client, edital, draft)

    assert resposta.status_code == 422, resposta.content
    assert resposta.json()["code"] == "invalid_stages"
    assert frase in resposta.json()["detail"]
    assert barema(edital) == []


def test_a_api_recusa_o_documento_restrito_a_um_perfil(api_client, edital):
    draft = rascunho()
    draft["stages"][0]["criteria"][0]["documentRequirementId"] = DO_PERFIL

    resposta = put(api_client, edital, draft)

    assert resposta.status_code == 422, resposta.content
    assert "não é pedido a toda inscrição" in resposta.json()["detail"]


# --- publicar e retificar (FR-5208, FR-5210) ------------------------------------------------------


@pytest.fixture
def publicado(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload, draft=rascunho())


def vigente(edital):
    return effective_version(edital_id=edital.id).content["stages"][0]


def test_a_retificacao_acrescenta_criterio_e_altera_a_maxima_no_mesmo_ato(api_client, publicado):
    retify(
        api_client,
        publicado,
        [
            {
                "targetPath": f"/stages/id={ETAPA}/criteria/-",
                "operation": "ADD",
                "newValue": criterio(
                    NOVO,
                    name="Especialização",
                    description="Na área da Educação.",
                    maximumScore="10.0000",
                    pointsPerUnit="5.0000",
                    unitLabel="certificado",
                ),
            },
            {
                "targetPath": f"/stages/id={ETAPA}/maximumScore",
                "operation": "REPLACE",
                "newValue": "45.0000",
            },
        ],
    )

    etapa = vigente(publicado)
    assert etapa["maximumScore"] == "45.0000"
    assert [c["name"] for c in etapa["criteria"]] == [
        "Diploma de Doutorado",
        "Diploma de Mestrado",
        "Especialização",
    ]


def test_a_retificacao_altera_cada_campo_de_um_criterio(api_client, publicado):
    retify(
        api_client,
        publicado,
        [
            {
                "targetPath": f"/stages/id={ETAPA}/criteria/id={MESTRADO}/{campo}",
                "operation": "REPLACE",
                "newValue": valor,
            }
            for campo, valor in (
                ("name", "Mestrado acadêmico"),
                ("description", "Reconhecido pela Capes."),
                ("unitLabel", "título"),
                ("documentRequirementId", None),
            )
        ],
    )

    mestrado = vigente(publicado)["criteria"][1]
    assert mestrado["name"] == "Mestrado acadêmico"
    assert mestrado["description"] == "Reconhecido pela Capes."
    assert mestrado["unitLabel"] == "título"
    assert mestrado["documentRequirementId"] is None


def test_a_retificacao_que_quebra_a_soma_e_recusada(api_client, publicado):
    """FR-5210: a igualdade vale também no conteúdo consolidado."""
    corpo = create_retification(
        api_client,
        publicado,
        [
            {
                "targetPath": f"/stages/id={ETAPA}/criteria/id={MESTRADO}/maximumScore",
                "operation": "REPLACE",
                "newValue": "20.0000",
            }
        ],
        esperar=422,
    )

    assert "a soma das máximas dos critérios do barema, 40" in corpo["detail"]
    assert vigente(publicado)["maximumScore"] == "35.0000"


def test_a_retificacao_que_restringe_o_documento_ligado_e_recusada(api_client, publicado):
    """SC-1634: a restrição chega pela Retificação do próprio documento, depois do vínculo."""
    perfil = effective_version(edital_id=publicado.id).content["profiles"][0]["id"]
    corpo = create_retification(
        api_client,
        publicado,
        [
            {
                "targetPath": f"/documentRequirements/id={TITULOS}/profileId",
                "operation": "REPLACE",
                "newValue": perfil,
            }
        ],
        esperar=422,
    )

    assert "não é pedido a toda inscrição" in corpo["detail"]


def test_a_retificacao_remove_um_criterio_com_a_maxima(api_client, publicado):
    retify(
        api_client,
        publicado,
        [
            {"targetPath": f"/stages/id={ETAPA}/criteria/id={MESTRADO}", "operation": "REMOVE"},
            {
                "targetPath": f"/stages/id={ETAPA}/maximumScore",
                "operation": "REPLACE",
                "newValue": "20.0000",
            },
        ],
    )

    assert [c["id"] for c in vigente(publicado)["criteria"]] == [DOUTORADO]


# --- o reaproveitamento (FR-5212, SC-1625) --------------------------------------------------------


def test_reaproveitar_copia_o_barema_com_identidades_novas_e_o_documento_remapeado(
    api_client,
    manager_headers,
    publicado,
    como_producao,  # noqa: F811
):
    criado = api_client.post(
        "/api/v1/admin/processos",
        {
            "institutionalCode": "PS-2027-146",
            "title": "Processo Seletivo 2027",
            "firstEdital": {"number": "46", "year": 2027, "title": "Edital reaproveitado"},
        },
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "destino-146-0001"},
    )
    assert criado.status_code == 201, criado.content
    destino = Edital.objects.get(processo_id=criado.json()["id"])

    with como_producao():
        reaproveitar_edital(
            actor=ator_institucional("preparadora", "edital:elaborar"),
            edital_id=destino.id,
            origem_id=publicado.id,
            expected_revision=destino.revision,
            idempotency_key="reaproveitar-146-0001",
            correlation_id="correlacao-146",
        )

    copiados = list(CriterioAvaliacao.objects.filter(etapa__edital=destino).order_by("ordem"))
    assert [c.nome for c in copiados] == ["Diploma de Doutorado", "Diploma de Mestrado"]
    assert {str(c.id) for c in copiados}.isdisjoint({DOUTORADO, MESTRADO})
    titulos_do_destino = destino.documentos_exigidos.get(key="titulos")
    assert {c.documento for c in copiados} == {titulos_do_destino.id}
    assert str(titulos_do_destino.id) != TITULOS
    assert EtapaAvaliacao.objects.get(edital=destino).maximum_score == 35


def test_o_conteudo_reaproveitado_passa_pelo_remapeamento_sem_referencia_solta():
    """A lista fechada de identidades do remapeamento inclui o critério e o documento dele."""
    from processo_seletivo.editais.domain.reaproveitamento import mapa_de_identidades, remapear

    conteudo = copy.deepcopy(rascunho())
    mapa = mapa_de_identidades(conteudo)
    novo = remapear(conteudo, mapa)

    criterios = novo["stages"][0]["criteria"]
    assert {c["id"] for c in criterios} == {mapa[DOUTORADO], mapa[MESTRADO]}
    assert {c["documentRequirementId"] for c in criterios} == {mapa[TITULOS]}
