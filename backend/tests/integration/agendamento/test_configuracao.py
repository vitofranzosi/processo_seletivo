"""Salvar a configuração (167, T015, FR-7204, FR-7205, FR-7207, FR-7208, FR-7256)."""

from datetime import date, time

import pytest

from processo_seletivo.agendamento.application import configurar, leitura
from processo_seletivo.agendamento.domain import nomes
from processo_seletivo.agendamento.domain.horarios import Banca
from processo_seletivo.agendamento.domain.recusas import ConfiguracaoRecusada
from processo_seletivo.agendamento.models import (
    AgendaDaEtapa,
    BancaDaAgenda,
    JanelaDaAgenda,
)
from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.agenda_da_etapa import MANHA_E_TARDE, SEG, configuracao

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def test_salvar_grava_as_tres_tabelas_e_comeca_na_revisao_1(gestor, edital_a, etapa_a2, inscricoes):
    salva = configurar.salvar(
        actor=gestor,
        edital=edital_a,
        etapa_id=etapa_a2,
        configuracao=configuracao(((SEG, MANHA_E_TARDE),)),
    )

    agenda = AgendaDaEtapa.objects.get(edital=edital_a, etapa_id=etapa_a2)
    assert agenda.revision == 1
    assert agenda.duracao_minutos == 10 and agenda.intervalo_minutos == 5
    assert JanelaDaAgenda.objects.filter(agenda=agenda).count() == 2
    assert list(BancaDaAgenda.objects.filter(agenda=agenda).values_list("nome", flat=True)) == [
        "Banca 1"
    ]
    assert salva.frase.startswith("Configuração salva. A agenda continua em rascunho")


def test_salvar_de_novo_sobe_a_revisao_e_mantem_a_banca(gestor, edital_a, etapa_a2, configurada):
    banca = BancaDaAgenda.objects.get(agenda=configurada)
    renomeada = configuracao(bancas=(Banca(str(banca.id), "Sala 1", "https://x", 1),))

    configurar.salvar(actor=gestor, edital=edital_a, etapa_id=etapa_a2, configuracao=renomeada)

    configurada.refresh_from_db()
    assert configurada.revision == 2
    assert BancaDaAgenda.objects.get(agenda=configurada).pk == banca.pk
    assert BancaDaAgenda.objects.get(agenda=configurada).nome == "Sala 1"


def test_a_configuracao_recusada_nao_grava_nada(gestor, edital_a, etapa_a2, inscricoes):
    invalida = configuracao(((SEG, ((time(12), time(12, 5)),)),), duracao=10)

    with pytest.raises(ConfiguracaoRecusada) as recusa:
        configurar.salvar(actor=gestor, edital=edital_a, etapa_id=etapa_a2, configuracao=invalida)

    assert [p.codigo for p in recusa.value.problemas] == [nomes.JANELA_MENOR_QUE_A_DURACAO]
    assert not AgendaDaEtapa.objects.exists()


def test_o_dia_fora_do_periodo_do_evento_e_recusado(gestor, edital_a, etapa_a1, inscricoes):
    """A primeira Etapa tem Evento em 01/09/2026: 23/11 está fora, e a frase diz o período."""
    with pytest.raises(ConfiguracaoRecusada) as recusa:
        configurar.salvar(
            actor=gestor, edital=edital_a, etapa_id=etapa_a1, configuracao=configuracao()
        )

    assert "em 01/09/2026" in recusa.value.detail
    assert "Retificação" in recusa.value.detail


def test_a_insuficiencia_e_a_lista_aberta_nao_impedem_salvar(
    gestor, edital_a, etapa_a2, inscricoes
):
    """Quatro horários para cinco, com a anterior sem Resultado (FR-7205, FR-7207)."""
    configurar.salvar(actor=gestor, edital=edital_a, etapa_id=etapa_a2, configuracao=configuracao())

    assert AgendaDaEtapa.objects.filter(etapa_id=etapa_a2).exists()


def test_a_etapa_sem_evento_e_aceita_em_qualquer_dia(gestor, edital_a, etapa_a2, inscricoes):
    longe = configuracao(((date(2027, 3, 1), MANHA_E_TARDE),))

    configurar.salvar(actor=gestor, edital=edital_a, etapa_id=etapa_a2, configuracao=longe)

    assert JanelaDaAgenda.objects.filter(dia=date(2027, 3, 1)).count() == 2


def test_a_trilha_registra_sem_o_acesso_da_banca(gestor, edital_a, etapa_a2, configurada):
    registro = RegistroAuditoria.objects.get(operation=leitura.CONFIGURACAO_SALVA)

    assert registro.actor_subject == gestor.subject
    assert registro.new_revision == 1
    assert "sala.exemplo" not in str(registro.detalhe)
    assert registro.detalhe["posterior"]["bancas"] == ["Banca 1"]


def test_sem_a_base_da_comissao_nada_se_grava(edital_a, etapa_a2, inscricoes):
    with pytest.raises(DomainError) as recusa:
        configurar.salvar(
            actor=ator_institucional("estranho"),
            edital=edital_a,
            etapa_id=etapa_a2,
            configuracao=configuracao(),
        )

    assert recusa.value.status == 404
    assert not AgendaDaEtapa.objects.exists()
