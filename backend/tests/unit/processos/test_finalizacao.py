"""US7 — política de desfecho. Encerrado e Cancelado são finais e nunca sinônimos."""

from types import SimpleNamespace

import pytest

from processo_seletivo.processos.domain import finalizacao
from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.shared.api.problems import DomainError


def processo(status):
    return SimpleNamespace(status=status)


def edital(status, number="01", year=2026):
    return SimpleNamespace(status=status, number=number, year=year)


@pytest.mark.parametrize(
    "status",
    [
        ProcessoSeletivo.Status.EM_ELABORACAO,
        ProcessoSeletivo.Status.ENCERRADO,
        ProcessoSeletivo.Status.CANCELADO,
    ],
)
def test_only_an_active_process_can_be_closed(status):
    with pytest.raises(DomainError) as exc:
        finalizacao.ensure_processo_can_be_closed(processo(status))
    assert exc.value.status == 409
    finalizacao.ensure_processo_can_be_closed(processo(ProcessoSeletivo.Status.ATIVO))


@pytest.mark.parametrize(
    "status", [ProcessoSeletivo.Status.EM_ELABORACAO, ProcessoSeletivo.Status.ATIVO]
)
def test_process_can_be_cancelled_before_a_final_state(status):
    finalizacao.ensure_processo_can_be_cancelled(processo(status), [])


@pytest.mark.parametrize(
    "status", [ProcessoSeletivo.Status.ENCERRADO, ProcessoSeletivo.Status.CANCELADO]
)
def test_final_process_states_never_return_to_a_previous_one(status):
    for act in (
        finalizacao.ensure_processo_can_be_closed,
        lambda item: finalizacao.ensure_processo_can_be_cancelled(item, []),
    ):
        with pytest.raises(DomainError, match="estado final"):
            act(processo(status))


def test_cancelling_a_process_is_blocked_and_names_the_pending_editais():
    """FR-034: o cancelamento não propaga; cada Edital precisa de ato próprio."""
    pendentes = [edital(Edital.Status.PUBLICADO, "02", 2026), edital(Edital.Status.EM_REVISAO)]
    with pytest.raises(DomainError) as exc:
        finalizacao.ensure_processo_can_be_cancelled(
            processo(ProcessoSeletivo.Status.ATIVO), pendentes
        )
    assert exc.value.code == "editais_pendentes"
    assert exc.value.status == 409
    assert "02/2026" in exc.value.detail and "01/2026" in exc.value.detail


def test_only_a_published_edital_reaches_regular_conclusion():
    """FR-006: Encerrado é a conclusão regular, posterior à Publicação."""
    finalizacao.ensure_edital_can_be_closed(edital(Edital.Status.PUBLICADO))
    for status in (
        Edital.Status.EM_ELABORACAO,
        Edital.Status.EM_REVISAO,
        Edital.Status.HOMOLOGADO,
    ):
        with pytest.raises(DomainError, match="publicado"):
            finalizacao.ensure_edital_can_be_closed(edital(status))


def test_edital_may_be_cancelled_at_any_point_before_regular_conclusion():
    for status in (
        Edital.Status.EM_ELABORACAO,
        Edital.Status.EM_REVISAO,
        Edital.Status.HOMOLOGADO,
        Edital.Status.PUBLICADO,
    ):
        finalizacao.ensure_edital_can_be_cancelled(edital(status))


@pytest.mark.parametrize("status", [Edital.Status.ENCERRADO, Edital.Status.CANCELADO])
def test_closed_and_cancelled_editais_are_both_final(status):
    with pytest.raises(DomainError, match="estado final"):
        finalizacao.ensure_edital_can_be_closed(edital(status))
    with pytest.raises(DomainError, match="estado final"):
        finalizacao.ensure_edital_can_be_cancelled(edital(status))


def test_cancelled_edital_is_not_presented_as_regular_conclusion():
    """Cancelado interrompe antes da conclusão; não vira Encerrado por outro caminho."""
    assert Edital.Status.CANCELADO in finalizacao.EDITAL_FINAL
    assert Edital.Status.CANCELADO not in finalizacao.EDITAL_ENCERRAVEL
    assert Edital.Status.ENCERRADO not in finalizacao.EDITAL_CANCELAVEL


@pytest.mark.parametrize(
    "status", [ProcessoSeletivo.Status.ENCERRADO, ProcessoSeletivo.Status.CANCELADO]
)
def test_final_process_rejects_further_changes_to_its_editais(status):
    """FR-035: desfecho impede novas transições incompatíveis."""
    with pytest.raises(DomainError, match="estado final"):
        finalizacao.ensure_processo_accepts_changes(processo(status))


@pytest.mark.parametrize(
    "status", [ProcessoSeletivo.Status.EM_ELABORACAO, ProcessoSeletivo.Status.ATIVO]
)
def test_process_in_course_keeps_accepting_changes(status):
    finalizacao.ensure_processo_accepts_changes(processo(status))
