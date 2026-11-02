"""A conferência vale no instante do ato, sob as travas (113, FR-3543, SC-1070, R-004).

**O que se prova.** Um recurso gravado por outra transação que confirma antes do encerramento é
visto por ele — porque o encerramento espera a trava do Processo, que é onde recurso, admissão,
julgamento e publicação de resultado já se serializam. Sem a trava do Processo, o encerramento leria
o Edital sem o recurso e concluiria.
"""

import threading
import time

import pytest
from django.db import connection, connections, transaction

from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.recursos.application.julgar import julgar
from processo_seletivo.recursos.models import DecisaoRecurso
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.recursos import admitir, interpor
from tests.fixtures.recursos_us4 import cenario_julgavel, julgador
from tests.integration.processos.test_encerramento_seguro import encerrar

pytestmark = [
    pytest.mark.django_db(transaction=True),
    pytest.mark.integration,
    pytest.mark.skipif(connection.vendor != "postgresql", reason="trava exige PostgreSQL"),
]


@pytest.fixture
def sem_impedimento(gestor, api_client, manager_headers, process_payload):
    """Edital com resultado divulgado e o único recurso já decidido: nada impede encerrar."""
    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=151, codigo="1151"
    )
    julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.INDEFERIDO,
        motivacao="Sem razão.",
        idempotency_key="indeferir-113-151",
    )
    return peca


def recurso_novo(peca, protocolo):
    """Outra inscrição recorre e tem a peça admitida — pela via curta, como as fixtures da `018`."""
    edital = peca["cenario"]["edital"]
    resultado = (
        ResultadoEtapa.vigentes.filter(inscricao__edital=edital)
        .exclude(inscricao=peca["inscricao"])
        .first()
    )
    recurso = interpor(
        inscricao=resultado.inscricao,
        versao=peca["versao"],
        resultado=resultado,
        protocolo=protocolo,
    )
    admitir(recurso)
    return recurso


def test_recurso_confirmado_antes_do_encerramento_o_impede(sem_impedimento):
    peca = sem_impedimento
    edital = peca["cenario"]["edital"]
    trancado = threading.Event()
    falhas = []

    def recorrer_segurando_o_processo():
        try:
            with transaction.atomic():
                ProcessoSeletivo.objects.select_for_update().get(pk=edital.processo_id)
                recurso_novo(peca, "REC-2026-113CONC1")
                trancado.set()
                time.sleep(0.5)
        except Exception as exc:  # noqa: BLE001 — repassado para o corpo do teste
            falhas.append(exc)
        finally:
            connections.close_all()

    linha = threading.Thread(target=recorrer_segurando_o_processo)
    linha.start()
    assert trancado.wait(timeout=10)

    inicio = time.monotonic()
    with pytest.raises(DomainError) as exc:
        encerrar(edital, chave="encerrar-113-concorrente")
    esperou = time.monotonic() - inicio
    linha.join(timeout=10)

    assert not falhas, falhas
    assert esperou >= 0.2, "o encerramento não esperou a trava do Processo"
    assert exc.value.code == "pendencias_impeditivas"
    assert "1 recurso aguarda decisão" in exc.value.detail
    edital.refresh_from_db()
    assert edital.status == Edital.Status.PUBLICADO


def test_encerramento_confirmado_antes_nao_e_desfeito_pelo_que_vem_depois(sem_impedimento):
    """FR-3545: o ato posterior segue as regras de hoje — a admissão continua aceita."""
    peca = sem_impedimento
    edital = peca["cenario"]["edital"]

    encerrar(edital, chave="encerrar-113-antes")
    recurso_novo(peca, "REC-2026-113CONC2")

    edital.refresh_from_db()
    assert edital.status == Edital.Status.ENCERRADO
