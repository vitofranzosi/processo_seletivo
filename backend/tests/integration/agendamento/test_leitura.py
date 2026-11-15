"""O que a agenda lê: a participação da prontidão, e nada guardado ao lado (167, T013).

FR-7210: quem precisa de horário é quem `participacao_detalhada` põe na Etapa, a cada leitura.
FR-7217: quem tem horário e saiu aparece, com o motivo. FR-7200: a agenda não toca o Edital.
"""

import pytest

from processo_seletivo.agendamento.application import leitura, montar
from processo_seletivo.agendamento.domain.horarios import derivar
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.resultados.application.prontidao import participacao_detalhada
from tests.fixtures.agenda_da_etapa import eliminar_na_primeira

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def test_a_participacao_e_a_da_prontidao(edital_a, etapa_a2, inscricoes):
    esperada = participacao_detalhada(edital=edital_a, etapa_id=etapa_a2)[0]

    assert leitura.participacao(edital_a, etapa_a2).participantes == {str(i) for i in esperada}
    assert len(esperada) == 5


def test_a_lista_esta_aberta_enquanto_a_anterior_nao_tem_resultado(
    edital_a, etapa_a1, etapa_a2, inscricoes
):
    """US1, cenário 7: a primeira Etapa não tem anterior; a segunda espera a primeira."""
    assert leitura.participacao(edital_a, etapa_a2).lista_aberta is True
    assert leitura.participacao(edital_a, etapa_a1).lista_aberta is False


def test_quem_sai_por_eliminacao_aparece_em_nao_participa_mais(
    gestor, edital_a, etapa_a1, etapa_a2, inscricoes, configurada
):
    alvo = inscricoes[0]
    horario = derivar(leitura.configuracao_da_agenda(leitura.agenda_da_etapa(edital_a, etapa_a2)))[
        0
    ]
    montar.agendar(
        actor=gestor,
        edital=edital_a,
        etapa_id=etapa_a2,
        inscricao_id=alvo.id,
        banca_id=horario.banca_id,
        inicio=horario.inicio,
    )

    eliminar_na_primeira(gestor, edital_a, etapa_a1, [alvo])

    agenda = leitura.agenda_da_etapa(edital_a, etapa_a2)
    resultado = leitura.montagem(edital_a, etapa_a2, agenda)
    [(agendamento, motivo)] = resultado.nao_participam
    assert agendamento.inscricao_id == alvo.id
    assert motivo == leitura.ELIMINADA


def test_a_agenda_nao_altera_o_edital_nem_o_cronograma(gestor, edital_a, etapa_a2, inscricoes):
    """FR-7200: operacional — nenhuma versão nova, nenhuma revisão do Edital, nenhum Evento."""
    from processo_seletivo.agendamento.application import configurar
    from processo_seletivo.editais.models import EventoCronograma
    from tests.fixtures.agenda_da_etapa import configuracao

    antes = (
        edital_a.revision,
        VersaoConsolidada.objects.filter(edital=edital_a).count(),
        list(EventoCronograma.objects.order_by("id").values()),
    )

    configurar.salvar(actor=gestor, edital=edital_a, etapa_id=etapa_a2, configuracao=configuracao())
    previa = montar.previa_do_preenchimento(actor=gestor, edital=edital_a, etapa_id=etapa_a2)
    montar.aplicar_preenchimento(
        actor=gestor, edital=edital_a, etapa_id=etapa_a2, assinatura=previa.assinatura
    )

    edital_a.refresh_from_db()
    assert (
        edital_a.revision,
        VersaoConsolidada.objects.filter(edital=edital_a).count(),
        list(EventoCronograma.objects.order_by("id").values()),
    ) == antes


def test_a_etapa_sem_evento_nao_tem_periodo(edital_a, etapa_a2):
    from processo_seletivo.comissoes.domain.etapas import etapa_vigente

    assert leitura.periodo_da_etapa(edital_a, etapa_vigente(edital_a, etapa_a2)) is None


def test_o_periodo_e_o_do_evento_vigente(edital_a, etapa_a1):
    """A primeira Etapa aponta o Evento da fixture, que só tem início: um dia só."""
    from datetime import date

    from processo_seletivo.comissoes.domain.etapas import etapa_vigente

    periodo = leitura.periodo_da_etapa(edital_a, etapa_vigente(edital_a, etapa_a1))

    assert periodo == (date(2026, 9, 1), date(2026, 9, 1))
