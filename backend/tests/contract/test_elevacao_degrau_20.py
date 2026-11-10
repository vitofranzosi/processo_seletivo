"""Edital publicado antes do degrau 20 continua vivo — e a ausência da visibilidade é `true` (144).

Todo Edital publicado antes deste degrau imprimiu todos os Eventos na tabela do Cronograma: a
capacidade de ocultar não existia. `true` é a verdade sobre o acervo, e não um padrão escolhido —
conversão sem invenção, no molde do degrau 11, o outro que mora no Evento (D-001, FR-5105).
"""

import pytest

from processo_seletivo.editais.domain.mutabilidade import CONTRATO, Natureza
from processo_seletivo.publicacoes.domain.changes import apply_changes
from processo_seletivo.publicacoes.domain.elevacao import DEGRAUS_DE_EVENTO, elevar, elevar_evento
from processo_seletivo.shared.canonical import SCHEMA_VERSION

pytestmark = [pytest.mark.contract]

EVENTO = "44444444-4444-4444-4444-444444444444"


def conteudo_na_versao(versao):
    return {
        "schemaVersion": versao,
        "stages": [],
        "profiles": [],
        "attachments": [],
        "documentRequirements": [],
        "maxInscricoesPorCandidato": None,
        "schedule": [
            {
                "id": EVENTO,
                "type": "Avaliação",
                "description": "Avaliação curricular",
                "startAt": "2026-11-20T14:00:00-03:00",
                "endAt": None,
                "order": 1,
                "status": "PLANEJADO",
                "location": "",
                "isRegistrationPeriod": False,
            }
        ],
    }


def test_o_degrau_20_existe_no_nivel_do_evento_e_grafa_a_ausencia_como_exibido():
    assert DEGRAUS_DE_EVENTO[20] == {"shownInPdf": True}
    assert SCHEMA_VERSION >= 20


def test_o_edital_anterior_eleva_com_todo_evento_exibido():
    elevado = elevar(conteudo_na_versao(19))

    evento = elevado["schedule"][0]
    assert elevado["schemaVersion"] == SCHEMA_VERSION
    assert evento["shownInPdf"] is True
    assert evento["description"] == "Avaliação curricular", "nada mais do Evento é tocado"


def test_o_edital_de_antes_do_local_recebe_os_dois_degraus():
    """Do 10 ao 20: o local vazio e a visibilidade verdadeira, cada um pelo seu degrau."""
    anterior = conteudo_na_versao(10)
    del anterior["schedule"][0]["location"]

    evento = elevar(anterior)["schedule"][0]

    assert evento["location"] == ""
    assert evento["shownInPdf"] is True


def test_o_evento_oculto_nao_e_reescrito():
    evento = elevar_evento({"id": EVENTO, "shownInPdf": False}, de=19)

    assert evento["shownInPdf"] is False


def test_a_elevacao_e_idempotente():
    ja_elevado = elevar(conteudo_na_versao(19))

    assert elevar(ja_elevado) is ja_elevado


def test_a_visibilidade_e_retificavel_pela_gramatica_que_ja_existe():
    """FR-5113, P-1: por identidade do Evento, sem gramática nova."""
    assert CONTRATO[("schedule", "shownInPdf")].natureza is Natureza.RETIFICAVEL
    conteudo = elevar(conteudo_na_versao(19))

    resultado, _registro = apply_changes(
        conteudo,
        [
            {
                "targetPath": f"/schedule/id={EVENTO}/shownInPdf",
                "operation": "REPLACE",
                "newValue": False,
            }
        ],
        publication_id="55555555-5555-5555-5555-555555555555",
    )

    assert resultado["schedule"][0]["shownInPdf"] is False
