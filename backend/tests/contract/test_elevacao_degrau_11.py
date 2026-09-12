"""Edital publicado antes do degrau 11 continua vivo — e a ausência do local **significa** algo.

Vazio diz "este Evento não declarou onde acontece", e não "acontece em lugar nenhum". A frase é
verdadeira sobre todo Edital publicado antes deste degrau: nenhum publicou o local em campo
estruturado, ainda que muitos o dissessem em prosa. Conversão sem invenção, portanto (021, D-008).

**String, e não `None`**, pela convenção do próprio Evento: `type` e `description` são strings, e
uma terceira grafia para texto ausente faria a versão canônica admitir mais de uma forma.
"""

import pytest

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
                "type": "Sorteio público",
                "description": "Sorteio dos habilitados",
                "startAt": "2026-11-20T14:00:00-03:00",
                "endAt": None,
                "order": 1,
                "status": "PLANEJADO",
                "isRegistrationPeriod": False,
            }
        ],
    }


def test_o_degrau_11_existe_no_nivel_do_evento_e_grafa_a_ausencia_como_vazio():
    assert DEGRAUS_DE_EVENTO[11] == {"location": ""}
    assert SCHEMA_VERSION >= 11


def test_o_edital_anterior_eleva_sem_inventar_local():
    elevado = elevar(conteudo_na_versao(10))

    evento = elevado["schedule"][0]
    assert elevado["schemaVersion"] == SCHEMA_VERSION
    assert evento["location"] == ""
    assert evento["type"] == "Sorteio público", "nada mais do Evento é tocado"


def test_o_evento_que_ja_declara_local_nao_e_reescrito():
    evento = elevar_evento({"id": EVENTO, "location": "Auditório do Cefor"}, de=10)

    assert evento["location"] == "Auditório do Cefor"


def test_a_elevacao_e_idempotente():
    ja_elevado = elevar(conteudo_na_versao(10))

    assert elevar(ja_elevado) is ja_elevado


def test_a_retificacao_alcanca_o_local_pela_gramatica_que_ja_existe():
    """FR-060: por identidade do Evento, e sem gramática nova."""
    conteudo = elevar(conteudo_na_versao(10))

    resultado, _registro = apply_changes(
        conteudo,
        [
            {
                "targetPath": f"/schedule/id={EVENTO}/location",
                "operation": "REPLACE",
                "newValue": "Auditório do Cefor e canal institucional no YouTube",
            }
        ],
        publication_id="55555555-5555-5555-5555-555555555555",
    )

    assert resultado["schedule"][0]["location"] == (
        "Auditório do Cefor e canal institucional no YouTube"
    )
    assert resultado["schedule"][0]["type"] == "Sorteio público"


def test_o_local_nao_e_validado_como_endereco_eletronico():
    """FR-061: *"Página da chamada pública"* não é URL, e recusá-lo obrigaria a mentir."""
    from processo_seletivo.editais.api.serializers import EventSerializer

    campo = EventSerializer().fields["location"]

    assert campo.allow_blank is True
    assert not any("URL" in type(v).__name__ for v in campo.validators)
