"""A fonte da Agenda dos Editais (101): só o cronograma publicado e vigente, do escopo do ator.

Pelo ciclo real — publicação, Retificação, encerramento e cancelamento pelo canal administrativo —,
porque a garantia que importa está na diferença entre a linha de elaboração e a versão vigente: um
teste que montasse a versão à mão provaria a projeção, e não a fonte (`FR-2612`).
"""

import pytest

from processo_seletivo.interface import agenda
from processo_seletivo.processos.application.finalizacao import cancel_edital, close_edital
from processo_seletivo.processos.models import Edital
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.tempo import ZONA
from tests.fixtures.agenda import cronograma, em, publicar
from tests.fixtures.edital import actor_headers, identificador
from tests.fixtures.publicacao import create_retification, publish_retification, retify
from tests.fixtures.selecao import rascunho_de_selecao

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

LEITORA = Actor("leitora.agenda", "cefor", frozenset())
GESTORA = Actor("gestora.agenda", "cefor", frozenset({"edital:encerrar", "edital:cancelar"}))
TODOS = {"visao": "proximos", "janela": "30"}


def marcos_de(leitura):
    return [marco for dia in leitura.dias for marco in dia.marcos]


def dias_da_prova(leitura, seed):
    return [m.dia for m in marcos_de(leitura) if m.evento_id == identificador(511, seed)]


def test_edital_publicado_entra_e_em_elaboracao_nao(api_client, manager_headers, process_payload):
    """`FR-2612`, `SC-949`: o rascunho tem linhas de cronograma na janela, e nada dele aparece."""
    publicado = publicar(api_client, manager_headers, process_payload, 1)

    criado = api_client.post(
        "/api/v1/admin/processos",
        {
            **process_payload,
            "institutionalCode": "PS-AGENDA-RASCUNHO",
            "firstEdital": {**process_payload["firstEdital"], "number": "99"},
        },
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "agenda-101-rascunho"},
    )
    assert criado.status_code == 201, criado.content
    rascunho = Edital.objects.get(processo_id=criado.json()["id"])
    corpo = rascunho_de_selecao(9)
    corpo["schedule"] = cronograma(9)
    gravado = api_client.put(
        f"/api/v1/admin/editais/{rascunho.id}/rascunho",
        corpo,
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key="agenda-101-rascunho-put"),
            "HTTP_IF_MATCH": f'"{rascunho.revision}"',
        },
    )
    assert gravado.status_code < 400, gravado.content
    assert rascunho.cronograma.eventos.exists(), "a premissa: o rascunho tem linhas de cronograma"

    leitura = agenda.ler(LEITORA, TODOS)
    editais = {m.edital.id for m in marcos_de(leitura)}
    assert editais == {str(publicado.id)}
    assert [e.id for e in leitura.opcoes_de_edital] == [str(publicado.id)]


def test_retificacao_vigente_muda_a_data_na_leitura_seguinte(
    api_client, manager_headers, process_payload
):
    """`FR-2613`, `SC-952`: a linha de elaboração fica com a data antiga; a agenda, com a nova."""
    edital = publicar(api_client, manager_headers, process_payload, 2)
    assert dias_da_prova(agenda.ler(LEITORA, TODOS), 2) == [em(3).date()]

    retify(
        api_client,
        edital,
        [
            {
                "targetPath": f"/schedule/id={identificador(511, 2)}/startAt",
                "operation": "REPLACE",
                "newValue": em(6, 14).isoformat(),
            }
        ],
    )

    assert dias_da_prova(agenda.ler(LEITORA, TODOS), 2) == [em(6).date()]
    linha = edital.cronograma.eventos.get(pk=identificador(511, 2))
    assert linha.start_at.astimezone(ZONA).date() == em(3).date(), "a linha não foi reescrita"


def test_evento_acrescentado_por_retificacao_aparece(api_client, manager_headers, process_payload):
    """`FR-2613`: o Evento novo não tem linha de cronograma nenhuma."""
    edital = publicar(api_client, manager_headers, process_payload, 3)
    novo = identificador(519, 3)
    retify(
        api_client,
        edital,
        [
            {
                "targetPath": "/schedule/-",
                "operation": "ADD",
                "newValue": {
                    "id": novo,
                    "type": "Entrevista",
                    "description": "Entrevistas",
                    "startAt": em(5, 10).isoformat(),
                    "endAt": None,
                    "order": 3,
                    "status": "PLANEJADO",
                    "location": "",
                    "isRegistrationPeriod": False,
                },
            }
        ],
    )
    assert not edital.cronograma.eventos.filter(pk=novo).exists()
    acrescentado = [m for m in marcos_de(agenda.ler(LEITORA, TODOS)) if m.evento_id == novo]
    assert [(m.nome, m.dia) for m in acrescentado] == [("Entrevistas", em(5).date())]


def test_retificacao_de_vigencia_futura_e_anunciada_e_nao_aplicada(
    api_client, manager_headers, process_payload
):
    """`FR-2614`, `D-008`, `SC-952`: antes da vigência, a data antiga e o aviso; depois, a nova."""
    edital = publicar(api_client, manager_headers, process_payload, 4)
    vigencia = em(4, 0)
    retificacao = create_retification(
        api_client,
        edital,
        [
            {
                "targetPath": f"/schedule/id={identificador(511, 4)}/startAt",
                "operation": "REPLACE",
                "newValue": em(8, 14).isoformat(),
            }
        ],
        effective_at=vigencia.isoformat(),
    )
    publish_retification(api_client, retificacao)

    antes = agenda.ler(LEITORA, TODOS)
    assert dias_da_prova(antes, 4) == [em(3).date()]
    assert [(a.edital.id, a.vigora_em.astimezone(ZONA).date()) for a in antes.avisos] == [
        (str(edital.id), vigencia.date())
    ]

    depois = agenda.ler(LEITORA, TODOS, agora=em(5, 12))
    assert dias_da_prova(depois, 4) == [em(8).date()]
    assert depois.avisos == ()


def test_edital_cancelado_some_e_encerrado_so_mostra_o_que_passou(
    api_client, manager_headers, process_payload
):
    """`FR-2615`, `D-009`."""
    cancelado = publicar(api_client, manager_headers, process_payload, 5)
    encerrado = publicar(api_client, manager_headers, process_payload, 6)
    for finalizar, edital, chave in (
        (cancel_edital, cancelado, "cancelar-agenda"),
        (close_edital, encerrado, "encerrar-agenda"),
    ):
        finalizar(
            actor=GESTORA,
            edital_id=edital.id,
            expected_revision=Edital.objects.get(pk=edital.pk).revision,
            reason="Finalização do teste da agenda.",
            idempotency_key=chave,
            correlation_id="101-agenda",
        )

    hoje = agenda.ler(LEITORA, TODOS)
    assert {m.edital.id for m in marcos_de(hoje)} == set()

    # Daqui a cinco dias a prova do encerrado já passou, e o período de inscrições ainda corre.
    adiante = agenda.ler(LEITORA, {"visao": "mes", "mes": em(3).strftime("%Y-%m")}, agora=em(5, 12))
    do_encerrado = {
        (m.evento_id, m.tipo)
        for semana in adiante.semanas
        for dia in semana
        for m in dia.nomeados
        if m.edital.id == str(encerrado.id)
    }
    assert do_encerrado == {(identificador(511, 6), agenda.PONTUAL)}
    assert all(m.edital.id != str(cancelado.id) for m in marcos_de(adiante))


def test_edital_de_outro_escopo_nao_aparece_nem_pelo_filtro(
    api_client, manager_headers, process_payload
):
    """`FR-2610`, `SC-949`: ignorado sem distinção — nem recusa, nem página vazia de propósito."""
    do_cefor = publicar(api_client, manager_headers, process_payload, 7)
    da_serra = publicar(api_client, manager_headers, process_payload, 8)
    Edital.objects.filter(pk=da_serra.pk).update(institution_scope="serra")

    leitura = agenda.ler(LEITORA, {**TODOS, "edital": str(da_serra.id)})
    assert leitura.filtros.edital is None, "o identificador alheio é ignorado"
    assert {m.edital.id for m in marcos_de(leitura)} == {str(do_cefor.id)}

    serra = agenda.ler(Actor("leitora.serra", "serra", frozenset()), TODOS)
    assert {m.edital.id for m in marcos_de(serra)} == {str(da_serra.id)}
