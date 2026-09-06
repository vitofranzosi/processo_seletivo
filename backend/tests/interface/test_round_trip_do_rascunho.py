"""O rascunho atravessa o assistente sem perder o que a etapa atual não edita (E2E17-001).

`replace_draft` substitui o rascunho inteiro: o que não for reenviado é apagado. O assistente
reenvia, a cada gravação, as coleções que a etapa não edita — e é por isso que **cada campo
omitido do serializador de reenvio é um campo que morre na etapa seguinte**, em silêncio, sem
recusa e sem aviso.

A auditoria exploratória da 017 encontrou o caso concreto: quem marca o Evento do período de
inscrições e segue o assistente na ordem natural publica um Edital que anuncia prazo de inscrição
e não recebe nenhuma. Estes testes cobrem a **classe** do defeito e não só aquela marca: para cada
coleção, o estado persistido é comparado campo a campo com o que o contrato de entrada declara e o
que `draft.py` reconstrói.

Dois caminhos, e os dois precisam valer:

- gravar uma etapa **posterior** não pode perder o que a anterior gravou — é o reenvio do estado
  persistido (`*_persistidos`);
- gravar de novo a etapa **dona da coleção** não pode perder o que aquela tela não oferece — é a
  leitura do formulário, que conhece só os campos que desenha.
"""

from datetime import UTC
from zoneinfo import ZoneInfo

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils.dateparse import parse_datetime

from processo_seletivo.editais.models.cronograma import EventoCronograma
from processo_seletivo.editais.models.perfis import PerfilVaga
from processo_seletivo.processos.models import Edital
from tests.fixtures.edital import actor_headers
from tests.interface.conftest import identificar

ZONA = ZoneInfo(settings.TIME_ZONE)

PERFIL = "aaaaaaaa-0000-4000-8000-0000000017a1"
MODALIDADE = "aaaaaaaa-0000-4000-8000-0000000017a2"
INSCRICOES = "aaaaaaaa-0000-4000-8000-0000000017b1"
RESULTADO = "aaaaaaaa-0000-4000-8000-0000000017b2"

# O Evento do período, como a instituição o descreve. Cada chave é um campo do contrato
# operacional que precisa atravessar o assistente inteiro.
EVENTO_DO_PERIODO = {
    "id": INSCRICOES,
    "type": "Inscrições",
    "description": "Período de inscrições",
    "startAt": "2026-10-01T09:00:00-03:00",
    "endAt": "2026-10-20T23:59:00-03:00",
    "order": 1,
    "status": "EM_ANDAMENTO",
    "isRegistrationPeriod": True,
}

EVENTO_DO_RESULTADO = {
    "id": RESULTADO,
    "type": "Resultado",
    "description": "Divulgação do resultado preliminar",
    "startAt": "2026-11-10T09:00:00-03:00",
    "endAt": None,
    "order": 2,
    "status": "PLANEJADO",
    "isRegistrationPeriod": False,
}

PERFIL_COMPLETO = {
    "id": PERFIL,
    "code": "TEC-LAB",
    "name": "Técnico de Laboratório",
    "description": "Apoio técnico aos laboratórios.",
    "requirements": ["Curso técnico em Informática"],
    "immediateVacancies": 2,
    "reserveType": "LIMITED",
    "reserveLimit": 5,
    "locality": "Campus Vitória",
    "duties": "Manutenção dos laboratórios.",
    "workload": "40h semanais",
    "compensation": "R$ 4.500,00",
    # Os dois objetos normativos que o contrato declara, que `draft.py` reconstrói e que o
    # conteúdo publicado carrega — e que nenhuma tela do assistente oferece.
    "classificationInformation": {"criterio": "Maior pontuação na prova prática."},
    "callInformation": {"prazo": "Cinco dias úteis a contar da convocação."},
    "competitionModalities": [
        {"id": MODALIDADE, "code": "AC", "name": "Ampla concorrência"},
    ],
}


def _rascunho():
    return {
        "profiles": [PERFIL_COMPLETO],
        "schedule": [EVENTO_DO_PERIODO, EVENTO_DO_RESULTADO],
    }


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    """Um rascunho gravado pelo canal que aceita o contrato inteiro, para depois atravessá-lo."""
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    resposta = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        _rascunho(),
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key="round-trip-0001"),
            "HTTP_IF_MATCH": '"1"',
        },
    )
    assert resposta.status_code == 200, resposta.content
    edital.refresh_from_db()
    return edital


def _etapa(edital, nome):
    return reverse("interface:compor-etapa", args=[edital.id, nome])


def _instante(valor):
    """O instante, e não a grafia dele: o mesmo momento em UTC.

    O contrato admite qualquer deslocamento explícito e a persistência devolve UTC. Comparar
    texto faria o teste falhar por notação e passar por acaso — é o instante que precisa
    sobreviver ao round-trip, não o fuso em que alguém o escreveu.
    """
    if valor is None:
        return None
    momento = parse_datetime(valor) if isinstance(valor, str) else valor
    return momento.astimezone(UTC)


def _eventos_como_o_contrato_os_declara(edital):
    """O Cronograma persistido, no vocabulário do contrato de entrada.

    Comparar a coleção inteira — e não campo a campo escolhido a dedo — é o que faz este teste
    falhar quando um campo novo entrar no contrato e o serializador de reenvio esquecer dele.
    """
    return [
        {
            "id": str(evento.id),
            "type": evento.type,
            "description": evento.description,
            "startAt": _instante(evento.start_at),
            "endAt": _instante(evento.end_at),
            "order": evento.order,
            "status": evento.status,
            "isRegistrationPeriod": evento.is_registration_period,
        }
        for evento in EventoCronograma.objects.filter(cronograma__edital=edital).order_by("order")
    ]


def _esperado():
    """O mesmo Cronograma que entrou — todos os campos, e não só a marca."""
    return [
        {
            **evento,
            "startAt": _instante(evento["startAt"]),
            "endAt": _instante(evento["endAt"]),
        }
        for evento in (EVENTO_DO_PERIODO, EVENTO_DO_RESULTADO)
    ]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_gravar_a_etapa_seguinte_preserva_o_cronograma_inteiro(client, seletor_ligado, edital):
    """A jornada real: marcar o período, seguir o assistente, e o período continuar marcado.

    `inscricao` é seguida de `conteudo` na ordem do assistente, e é obrigatório atravessá-la para
    chegar à Revisão. Era ali que a marca morria.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = client.post(
        _etapa(edital, "inscricao"),
        {"periodo-inscricoes": INSCRICOES},
    )
    assert resposta.status_code == 302, resposta.content

    edital.refresh_from_db()
    resposta = client.post(_etapa(edital, "conteudo"), {"secao-recursos": "Três dias úteis."})
    assert resposta.status_code == 302, resposta.content

    assert _eventos_como_o_contrato_os_declara(edital) == _esperado()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_regravar_o_cronograma_preserva_o_que_a_tela_nao_oferece(client, seletor_ligado, edital):
    """Corrigir uma data depois de designar o período não pode desdesignar o período.

    A tela do Cronograma não oferece a marca — ela é decisão da etapa `Inscrição` — nem o estado
    do Evento. O que a tela não oferece, ela não pode apagar.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = client.post(_etapa(edital, "inscricao"), {"periodo-inscricoes": INSCRICOES})
    assert resposta.status_code == 302, resposta.content

    edital.refresh_from_db()
    resposta = client.post(
        _etapa(edital, "cronograma"),
        {
            "evento-0-id": INSCRICOES,
            "evento-0-type": "Inscrições",
            "evento-0-description": "Período de inscrições",
            "evento-0-startAt": "2026-10-01T09:00",
            # A correção: o término passa para o dia 21.
            "evento-0-endAt": "2026-10-21T23:59",
            "evento-0-order": "1",
            "evento-1-id": RESULTADO,
            "evento-1-type": "Resultado",
            "evento-1-description": "Divulgação do resultado preliminar",
            "evento-1-startAt": "2026-11-10T09:00",
            "evento-1-endAt": "",
            "evento-1-order": "2",
        },
    )
    assert resposta.status_code == 302, resposta.content

    periodo = EventoCronograma.objects.get(pk=INSCRICOES)
    assert periodo.end_at.astimezone(ZONA).day == 21, "a correção que a tela oferece vale"
    assert periodo.is_registration_period is True, "a marca que a tela não oferece sobrevive"
    assert periodo.status == "EM_ANDAMENTO", "o estado que a tela não oferece sobrevive"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_gravar_outra_etapa_preserva_o_conteudo_normativo_do_perfil(client, seletor_ligado, edital):
    """Os dois objetos normativos do Perfil que nenhuma tela desenha, e que o contrato declara."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = client.post(_etapa(edital, "conteudo"), {"secao-recursos": "Três dias úteis."})
    assert resposta.status_code == 302, resposta.content

    perfil = PerfilVaga.objects.get(edital=edital)
    assert perfil.classification_information == PERFIL_COMPLETO["classificationInformation"]
    assert perfil.call_information == PERFIL_COMPLETO["callInformation"]
