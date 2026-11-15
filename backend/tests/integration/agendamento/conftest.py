import pytest

from processo_seletivo.agendamento.application import configurar
from tests.fixtures.agenda_da_etapa import configuracao
from tests.fixtures.comissao import inscrever


@pytest.fixture
def inscricoes(edital_a):
    return inscrever(edital_a, 5)


@pytest.fixture
def configurada(gestor, edital_a, etapa_a2, inscricoes):
    """A agenda da segunda Etapa com quatro horários, para cinco participantes."""
    return configurar.salvar(
        actor=gestor, edital=edital_a, etapa_id=etapa_a2, configuracao=configuracao()
    ).agenda
