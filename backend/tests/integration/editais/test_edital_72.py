"""O Edital 72/2026 não seria publicado hoje (102, SC-955).

**O cronograma do servidor, deslocado para o futuro.** Em 29/10/2026 o sorteio do 72 foi recusado:
inscrições até 28/10 às 9h, extração da Loteria Federal declarada para 28/10 às 20h05, e a relação
congelada às 11h20 do mesmo dia. A forma do cronograma é a que importa — fim das inscrições e
extração no mesmo dia —, e as datas vão para daqui a um mês porque a publicação também recusa Edital
com inscrições já encerradas (FR-346 da `028`), que seria outra recusa sobre outro defeito.

Pelo caminho real: rascunho, submissão e publicação pela API. A conferência não chama a Caixa: lê o
que o Edital declara.
"""

import copy
from datetime import datetime, time, timedelta

import pytest
from django.utils import timezone

from processo_seletivo.processos.models import Edital
from processo_seletivo.shared.tempo import ZONA
from tests.fixtures.edital import DRAW_METHOD, actor_headers, complete_draft
from tests.fixtures.publicacao import levar_a_publicacao

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

#: O corpo da recusa de submissão traz a mensagem dos impeditivos, e não o código deles.
FRASE = "o sorteio será sempre recusado"


def _dia_do_certame():
    return timezone.localdate(timezone.now(), ZONA) + timedelta(days=30)


def _rascunho(*, dias_entre_fim_e_extracao):
    dia = _dia_do_certame()
    fim = datetime.combine(dia, time(9, 0), tzinfo=ZONA)
    extracao = datetime.combine(dia + timedelta(days=dias_entre_fim_e_extracao), time(20, 5))
    rascunho = complete_draft()
    rascunho["schedule"][0].update(
        {
            "startAt": (fim - timedelta(days=20)).isoformat(),
            "endAt": fim.isoformat(),
            "isRegistrationPeriod": True,
        }
    )
    metodo = copy.deepcopy(DRAW_METHOD)
    metodo.update(
        {
            "source": "Loteria Federal",
            "occurrence": "6113",
            "occurrenceAt": extracao.replace(tzinfo=ZONA).isoformat(),
        }
    )
    rascunho["profiles"][0]["classificationMilestones"][0]["drawMethod"] = metodo
    return rascunho


@pytest.fixture
def em_elaboracao(api_client, manager_headers, process_payload):
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert criado.status_code == 201, criado.content
    return Edital.objects.get(processo_id=criado.json()["id"])


def test_com_a_extracao_no_dia_do_fim_das_inscricoes_a_submissao_e_recusada(
    api_client, em_elaboracao
):
    preparador = actor_headers("preparador", ["edital:elaborar", "edital:submeter"])
    gravado = api_client.put(
        f"/api/v1/admin/editais/{em_elaboracao.id}/rascunho",
        _rascunho(dias_entre_fim_e_extracao=0),
        format="json",
        **{**preparador, "HTTP_IF_MATCH": f'"{em_elaboracao.revision}"'},
    )
    assert gravado.status_code < 400, gravado.content
    em_elaboracao.refresh_from_db()

    submetido = api_client.post(
        f"/api/v1/admin/editais/{em_elaboracao.id}/submissoes",
        format="json",
        **{**preparador, "HTTP_IF_MATCH": f'"{em_elaboracao.revision}"'},
    )

    assert submetido.status_code == 422, submetido.content
    assert FRASE in submetido.content.decode("utf-8")
    em_elaboracao.refresh_from_db()
    assert em_elaboracao.status != "PUBLICADO"


def test_com_a_extracao_no_dia_seguinte_o_edital_publica(api_client, em_elaboracao):
    publicado = levar_a_publicacao(
        api_client, em_elaboracao, draft=_rascunho(dias_entre_fim_e_extracao=1)
    )

    assert publicado.status == "PUBLICADO"
