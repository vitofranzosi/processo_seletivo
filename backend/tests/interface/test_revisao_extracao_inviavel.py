"""A extração inviável aparece na revisão, e leva à etapa em que o método se declara (102, FR-2654).

**Nenhuma tela nova.** O achado entra na mesma lista de pendências que a revisão da composição já
mostra, e a tradução de caminho para etapa é a que já existe: o método do marco e o comum do Edital
se resolvem na Classificação. O teste fixa isso, porque um caminho sem destino aparece como
"não corrigível" — o sistema apontaria o defeito e diria que não há onde corrigi-lo.
"""

import copy
from datetime import datetime, time, timedelta

import pytest
from django.utils import timezone

from processo_seletivo.interface.views import _pendencias
from processo_seletivo.processos.models import Edital
from processo_seletivo.shared.tempo import ZONA
from tests.fixtures.edital import DRAW_METHOD, actor_headers, complete_draft

pytestmark = [pytest.mark.django_db]

CODIGO = "draw_occurrence_not_after_registration"


def _rascunho(*, comum):
    dia = timezone.localdate(timezone.now(), ZONA) + timedelta(days=30)
    fim = datetime.combine(dia, time(9, 0), tzinfo=ZONA)
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
            "occurrenceAt": datetime.combine(dia, time(20, 5), tzinfo=ZONA).isoformat(),
        }
    )
    marco = rascunho["profiles"][0]["classificationMilestones"][0]
    if comum:
        marco.pop("drawMethod")
        rascunho["drawMethod"] = metodo
    else:
        marco["drawMethod"] = metodo
    return rascunho


def _gravado(api_client, manager_headers, process_payload, rascunho):
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert criado.status_code == 201, criado.content
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    gravado = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        rascunho,
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"]),
            "HTTP_IF_MATCH": f'"{edital.revision}"',
        },
    )
    assert gravado.status_code < 400, gravado.content
    return Edital.objects.get(pk=edital.pk)


@pytest.mark.parametrize("comum", [False, True], ids=["do-marco", "comum"])
def test_a_pendencia_leva_a_classificacao_e_e_corrigivel(
    api_client, manager_headers, process_payload, comum
):
    edital = _gravado(api_client, manager_headers, process_payload, _rascunho(comum=comum))

    (pendencia,) = [p for p in _pendencias(edital) if p["codigo"] == CODIGO]

    assert pendencia["severidade"] == "erro"
    assert pendencia["etapa"] == "classificacao"
    assert pendencia["corrigivel"] is True
    assert "o sorteio será sempre recusado" in pendencia["mensagem"]
