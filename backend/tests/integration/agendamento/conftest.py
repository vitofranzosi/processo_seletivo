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


@pytest.fixture
def publicada(gestor, edital_a, etapa_a2, inscricoes):
    """A agenda da segunda Etapa completa e publicada no GPS: as cinco pessoas com horário."""
    from tests.fixtures.agenda_da_etapa import montar_completa, publicar_agenda

    montar_completa(gestor, edital_a, etapa_a2)
    return publicar_agenda(gestor, edital_a, etapa_a2)
