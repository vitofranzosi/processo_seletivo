"""A gravação do rascunho normaliza os zeros e recusa a forma errada (116, US5, FR-3623, FR-3624).

Pelos dois canais: o `PUT /rascunho` da API e o comando que a tela chama direto
(`replace_draft`). E sem consultar a Caixa: a gravação não é ato (D-007).
"""

import copy

import pytest

from processo_seletivo.editais.application.draft import replace_draft
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.edital import DRAW_METHOD, actor_headers, complete_draft

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

CORRECAO = "informe só o número do concurso, como 6106 — sem dígito verificador, texto ou ano"


@pytest.fixture
def em_elaboracao(api_client, manager_headers, process_payload):
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert criado.status_code == 201, criado.content
    return Edital.objects.get(processo_id=criado.json()["id"])


def _rascunho(ocorrencia, fonte="Loteria Federal", *, comum=False):
    rascunho = complete_draft()
    metodo = copy.deepcopy(DRAW_METHOD)
    metodo.update({"source": fonte, "occurrence": ocorrencia})
    if comum:
        rascunho["profiles"][0]["classificationMilestones"][0].pop("drawMethod", None)
        rascunho["drawMethod"] = metodo
    else:
        rascunho["profiles"][0]["classificationMilestones"][0]["drawMethod"] = metodo
    return rascunho


def _put(api_client, edital, rascunho):
    preparador = actor_headers("preparador", ["edital:elaborar"])
    return api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        rascunho,
        format="json",
        **{**preparador, "HTTP_IF_MATCH": f'"{edital.revision}"'},
    )


def _ocorrencia_gravada(edital):
    edital.refresh_from_db()
    snapshot = edital_snapshot(edital)
    metodo = (
        snapshot["profiles"][0]["classificationMilestones"][0].get("drawMethod")
        or snapshot["drawMethod"]
    )
    return metodo["occurrence"]


def test_zeros_a_esquerda_sao_gravados_sem_eles(api_client, em_elaboracao, caixa):
    resposta = _put(api_client, em_elaboracao, _rascunho("006114"))
    assert resposta.status_code < 400, resposta.content
    assert _ocorrencia_gravada(em_elaboracao) == "6114"
    assert caixa.chamadas == 0, "a gravação do rascunho não consulta a Caixa (D-007)"


def test_zeros_a_esquerda_do_metodo_comum(api_client, em_elaboracao):
    resposta = _put(api_client, em_elaboracao, _rascunho("0006116", comum=True))
    assert resposta.status_code < 400, resposta.content
    assert _ocorrencia_gravada(em_elaboracao) == "6116"


@pytest.mark.parametrize("grafia", ["6106-9", "Concurso 6115"])
def test_a_forma_errada_e_recusada_pela_api_e_nada_e_gravado(api_client, em_elaboracao, grafia):
    revisao = em_elaboracao.revision
    resposta = _put(api_client, em_elaboracao, _rascunho(grafia))
    assert resposta.status_code == 422, resposta.content
    assert CORRECAO in resposta.content.decode("utf-8")
    em_elaboracao.refresh_from_db()
    assert em_elaboracao.revision == revisao


def test_a_forma_errada_e_recusada_pelo_comando_da_tela(em_elaboracao):
    rascunho = _rascunho("6106-9")
    with pytest.raises(DomainError) as recusa:
        replace_draft(
            actor=Actor("preparador", "cefor", frozenset({"edital:elaborar"})),
            edital_id=em_elaboracao.id,
            expected_revision=em_elaboracao.revision,
            profiles=rascunho["profiles"],
            schedule=rascunho["schedule"],
            correlation_id="teste-116",
        )
    assert recusa.value.status == 422
    assert CORRECAO in recusa.value.detail


def test_a_demonstracao_grava_como_gravava(api_client, em_elaboracao):
    resposta = _put(api_client, em_elaboracao, _rascunho("Concurso 5900", "Fonte de demonstração"))
    assert resposta.status_code < 400, resposta.content
    assert _ocorrencia_gravada(em_elaboracao) == "Concurso 5900"
