"""A metade da FR-006 que faltava: antes da Publicação, a revisão devolve o Edital à elaboração.

**Por que existe.** A FR-006 declara as duas voltas anteriores à Publicação — "a revisão PODE
devolver o Edital a Em elaboração e a homologação PODE ser revogada para Em revisão". A segunda
foi implementada na `001`; a primeira nunca, e a matriz de rastreabilidade marcou a FR-006 como
coberta citando três testes que só falam de Encerrado e Cancelado. Uma auditoria de percurso
encontrou o buraco pelo lado de quem opera: quem revisa e discorda não tinha ato nenhum, e as
duas saídas restantes eram cancelar — estado final, que queima o número no escopo — ou homologar
o que se recusa, para retificar depois.

O que estes testes cobram é a volta **inteira**: o estado muda, o formulário volta a aceitar, o
que foi submetido continua registrado, e a próxima submissão não colide com a anterior.
"""

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models import RevisaoEdital
from tests.fixtures.edital import actor_headers, complete_draft

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ELABORADOR = ["edital:elaborar", "edital:submeter"]
HOMOLOGADOR = ["edital:homologar"]


def submetido(api_client, manager_headers, process_payload):
    """Um Edital em revisão, pelo mesmo caminho que a interface percorre."""
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()
    elaborador = actor_headers("preparador", ELABORADOR)
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        complete_draft(),
        format="json",
        **{**elaborador, "HTTP_IF_MATCH": '"1"'},
    )
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/submissoes",
        format="json",
        **{**elaborador, "HTTP_IF_MATCH": '"2"'},
    )
    edital.refresh_from_db()
    assert edital.status == Edital.Status.EM_REVISAO
    return edital


def devolver(
    api_client, edital, *, revisao, motivo="O Cronograma não confere com a portaria.", **extra
):
    return api_client.post(
        f"/api/v1/admin/editais/{edital.id}/devolucoes",
        {"reason": motivo},
        format="json",
        **actor_headers("homologador", HOMOLOGADOR, if_match=revisao, **extra),
    )


def test_a_revisao_devolve_o_edital_para_elaboracao(api_client, manager_headers, process_payload):
    edital = submetido(api_client, manager_headers, process_payload)

    resposta = devolver(api_client, edital, revisao=3)

    assert resposta.status_code == 200
    edital.refresh_from_db()
    assert edital.status == Edital.Status.EM_ELABORACAO


def test_devolvido_o_edital_volta_a_aceitar_o_formulario(
    api_client, manager_headers, process_payload
):
    """A prova de que a volta é real: sem isto, devolver seria só trocar um rótulo.

    `replace_draft` recusa qualquer Edital fora de elaboração, e é essa recusa — não o estado
    exibido — que dizia a quem revisava que não havia caminho de volta.
    """
    edital = submetido(api_client, manager_headers, process_payload)
    devolver(api_client, edital, revisao=3)

    resposta = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        complete_draft(),
        format="json",
        **{
            **actor_headers("preparador", ELABORADOR, key="reedicao-apos-devolver"),
            "HTTP_IF_MATCH": '"4"',
        },
    )

    assert resposta.status_code == 200


def test_a_revisao_submetida_sobrevive_a_devolucao(api_client, manager_headers, process_payload):
    """Devolver não apaga o que foi submetido: aquilo aconteceu, e continua verdadeiro."""
    edital = submetido(api_client, manager_headers, process_payload)

    devolver(api_client, edital, revisao=3)

    assert RevisaoEdital.objects.filter(edital=edital).count() == 1


def test_a_ressubmissao_nao_colide_com_a_revisao_devolvida(
    api_client, manager_headers, process_payload
):
    """`(edital, edital_revision)` é único, e a devolução é que abre espaço para a próxima.

    A transição incrementa a revisão do Edital, então a submissão seguinte grava sob outro
    número. Sem isso, devolver produziria um Edital que não pode ser submetido de novo — beco
    pior que o que ela veio resolver.
    """
    edital = submetido(api_client, manager_headers, process_payload)
    devolver(api_client, edital, revisao=3)

    resposta = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/submissoes",
        format="json",
        **{
            **actor_headers("preparador", ELABORADOR, key="ressubmissao-apos-devolver"),
            "HTTP_IF_MATCH": '"4"',
        },
    )

    assert resposta.status_code == 200
    edital.refresh_from_db()
    assert edital.status == Edital.Status.EM_REVISAO
    assert RevisaoEdital.objects.filter(edital=edital).count() == 2


def test_a_devolucao_exige_motivo(api_client, manager_headers, process_payload):
    """O motivo é o que a devolução entrega a quem vai corrigir — sem ele, ela é recusa muda."""
    edital = submetido(api_client, manager_headers, process_payload)

    resposta = devolver(api_client, edital, revisao=3, motivo="   ")

    assert resposta.status_code == 422
    edital.refresh_from_db()
    assert edital.status == Edital.Status.EM_REVISAO


def test_quem_elabora_nao_devolve(api_client, manager_headers, process_payload):
    """Devolver desfaz a revisão de outra pessoa: é ato de quem homologa, como a revogação."""
    edital = submetido(api_client, manager_headers, process_payload)

    resposta = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/devolucoes",
        {"reason": "Quero editar de novo."},
        format="json",
        **actor_headers("preparador", ELABORADOR, if_match=3),
    )

    assert resposta.status_code == 403
    edital.refresh_from_db()
    assert edital.status == Edital.Status.EM_REVISAO


def test_o_edital_homologado_nao_e_devolvido(api_client, manager_headers, process_payload):
    """Homologado tem volta própria — revogar a homologação —, e são atos distintos."""
    edital = submetido(api_client, manager_headers, process_payload)
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/homologacoes",
        {"reason": "Conferido"},
        format="json",
        **actor_headers("homologador", HOMOLOGADOR, if_match=3, key="homologacao-do-edital"),
    )

    resposta = devolver(api_client, edital, revisao=4, key="devolucao-apos-homologar")

    assert resposta.status_code == 409
    edital.refresh_from_db()
    assert edital.status == Edital.Status.HOMOLOGADO


def test_confirmar_duas_vezes_devolve_uma_vez_so(api_client, manager_headers, process_payload):
    edital = submetido(api_client, manager_headers, process_payload)

    primeira = devolver(api_client, edital, revisao=3)
    repetida = devolver(api_client, edital, revisao=3)

    assert primeira.status_code == repetida.status_code == 200
    edital.refresh_from_db()
    assert edital.revision == 4


def test_a_trilha_registra_a_devolucao_com_autoria_e_motivo(
    api_client, manager_headers, process_payload
):
    edital = submetido(api_client, manager_headers, process_payload)

    devolver(api_client, edital, revisao=3, motivo="Faltou o Anexo II.")

    registro = RegistroAuditoria.objects.get(operation="DEVOLVER", aggregate_id=edital.id)
    assert registro.actor_subject == "homologador"
    assert registro.permission == "edital:homologar"
    assert registro.reason == "Faltou o Anexo II."
    assert registro.previous_state == Edital.Status.EM_REVISAO
    assert registro.new_state == Edital.Status.EM_ELABORACAO
