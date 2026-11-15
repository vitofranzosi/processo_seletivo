"""A montagem: agendar, mudar, liberar, e o preenchimento com prévia (167, T024, US2).

FR-7212 a FR-7216; o cenário 9 da US2 (a configuração que remove um horário devolve a pessoa).
"""

from datetime import time, timedelta

import pytest

from processo_seletivo.agendamento.application import configurar, leitura, montar
from processo_seletivo.agendamento.domain import nomes
from processo_seletivo.agendamento.domain.horarios import Banca
from processo_seletivo.agendamento.models import Agendamento, BancaDaAgenda
from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.agenda_da_etapa import SEG, TER, UMA_HORA, configuracao, eliminar_na_primeira
from tests.fixtures.comissao import inscrever

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def _horarios(edital, etapa):
    agenda = leitura.agenda_da_etapa(edital, etapa)
    return leitura.montagem(edital, etapa, agenda).horarios


def _agendar(gestor, edital, etapa, inscricao, horario, **extra):
    return montar.agendar(
        actor=gestor,
        edital=edital,
        etapa_id=etapa,
        inscricao_id=inscricao.id,
        banca_id=horario.banca_id,
        inicio=horario.inicio,
        **extra,
    )


def test_agendar_a_mao_grava_origem_autor_e_instante(
    gestor, edital_a, etapa_a2, inscricoes, configurada
):
    horario = _horarios(edital_a, etapa_a2)[1]

    frase = _agendar(gestor, edital_a, etapa_a2, inscricoes[0], horario)

    agendamento = Agendamento.objects.get()
    assert agendamento.origem == nomes.MANUAL
    assert agendamento.feito_por == gestor.subject
    assert agendamento.inicio == horario.inicio and agendamento.fim == horario.fim
    assert frase == "Candidata 1 agendada em Seg., 23/11, 08:15, Banca 1."
    registro = RegistroAuditoria.objects.get(operation=montar.AGENDAMENTO)
    assert registro.detalhe["gesto"] == "agendar"
    assert registro.detalhe["posterior"]["protocolo"] == inscricoes[0].protocolo


def test_mudar_de_horario_inclusive_de_dia(gestor, edital_a, etapa_a2, inscricoes, configurada):
    configurar.salvar(
        actor=gestor,
        edital=edital_a,
        etapa_id=etapa_a2,
        configuracao=configuracao(
            ((SEG, UMA_HORA), (TER, UMA_HORA)),
            bancas=(Banca(str(BancaDaAgenda.objects.get().pk), "Banca 1", "https://x", 1),),
        ),
    )
    horarios = _horarios(edital_a, etapa_a2)
    _agendar(gestor, edital_a, etapa_a2, inscricoes[0], horarios[0])

    frase = _agendar(gestor, edital_a, etapa_a2, inscricoes[0], horarios[-1], mudanca=True)

    assert Agendamento.objects.get().inicio == horarios[-1].inicio
    assert frase == "Candidata 1 passou de Seg., 23/11, 08:00 para Ter., 24/11, 08:45."


def test_do_horario_livre_quem_ja_tem_horario_e_recusado(
    gestor, edital_a, etapa_a2, inscricoes, configurada
):
    horarios = _horarios(edital_a, etapa_a2)
    _agendar(gestor, edital_a, etapa_a2, inscricoes[0], horarios[0])

    with pytest.raises(DomainError) as recusa:
        _agendar(gestor, edital_a, etapa_a2, inscricoes[0], horarios[1])

    assert recusa.value.code == nomes.PESSOA_JA_AGENDADA
    assert "já tem horário, em Seg., 23/11, 08:00" in recusa.value.detail


def test_horario_ocupado_por_outra_pessoa_e_recusado(
    gestor, edital_a, etapa_a2, inscricoes, configurada
):
    horario = _horarios(edital_a, etapa_a2)[0]
    _agendar(gestor, edital_a, etapa_a2, inscricoes[0], horario)

    with pytest.raises(DomainError) as recusa:
        _agendar(gestor, edital_a, etapa_a2, inscricoes[1], horario)

    assert recusa.value.code == nomes.HORARIO_OCUPADO
    assert recusa.value.status == 409


def test_horario_que_nao_deriva_da_configuracao_e_recusado(
    gestor, edital_a, etapa_a2, inscricoes, configurada
):
    horario = _horarios(edital_a, etapa_a2)[0]

    with pytest.raises(DomainError) as recusa:
        montar.agendar(
            actor=gestor,
            edital=edital_a,
            etapa_id=etapa_a2,
            inscricao_id=inscricoes[0].id,
            banca_id=horario.banca_id,
            inicio=horario.inicio + timedelta(minutes=3),
        )

    assert recusa.value.code == nomes.HORARIO_INEXISTENTE


def test_liberar_devolve_a_pessoa_para_sem_horario(
    gestor, edital_a, etapa_a2, inscricoes, configurada
):
    _agendar(gestor, edital_a, etapa_a2, inscricoes[0], _horarios(edital_a, etapa_a2)[0])

    frase = montar.liberar(
        actor=gestor, edital=edital_a, etapa_id=etapa_a2, inscricao_id=inscricoes[0].id
    )

    assert not Agendamento.objects.exists()
    assert frase == 'Horário liberado. Candidata 1 voltou para "Sem horário".'
    agenda = leitura.agenda_da_etapa(edital_a, etapa_a2)
    sem = [p.inscricao_id for p in leitura.montagem(edital_a, etapa_a2, agenda).sem_horario]
    assert str(inscricoes[0].id) in sem


def test_agendar_quem_nao_participa_e_recusado_com_o_motivo(
    gestor, edital_a, etapa_a1, etapa_a2, inscricoes, configurada
):
    eliminar_na_primeira(gestor, edital_a, etapa_a1, [inscricoes[0]])

    with pytest.raises(DomainError) as recusa:
        _agendar(gestor, edital_a, etapa_a2, inscricoes[0], _horarios(edital_a, etapa_a2)[0])

    assert recusa.value.code == nomes.PESSOA_NAO_PARTICIPA
    assert recusa.value.detail == (
        "Candidata 1 não participa desta Etapa: foi eliminada numa Etapa anterior."
    )


def test_a_previa_nao_grava_e_a_aplicacao_grava_como_automatica(
    gestor, edital_a, etapa_a2, inscricoes, configurada
):
    previa = montar.previa_do_preenchimento(actor=gestor, edital=edital_a, etapa_id=etapa_a2)

    assert previa.proposta.frase == "4 pessoas recebem horário. 1 continua sem horário."
    assert not Agendamento.objects.exists()

    frase = montar.aplicar_preenchimento(
        actor=gestor, edital=edital_a, etapa_id=etapa_a2, assinatura=previa.assinatura
    )

    assert frase == "4 pessoas receberam horário."
    assert set(Agendamento.objects.values_list("origem", flat=True)) == {nomes.AUTOMATICA}
    assert set(Agendamento.objects.values_list("feito_por", flat=True)) == {gestor.subject}
    assert RegistroAuditoria.objects.filter(operation=montar.PREENCHIMENTO_APLICADO).count() == 1


def test_quem_foi_agendado_a_mao_nao_muda_no_preenchimento(
    gestor, edital_a, etapa_a2, inscricoes, configurada
):
    """O teste independente da US2: agendar à mão antes de preencher mantém a pessoa ali."""
    horarios = _horarios(edital_a, etapa_a2)
    _agendar(gestor, edital_a, etapa_a2, inscricoes[4], horarios[2])
    previa = montar.previa_do_preenchimento(actor=gestor, edital=edital_a, etapa_id=etapa_a2)

    montar.aplicar_preenchimento(
        actor=gestor, edital=edital_a, etapa_id=etapa_a2, assinatura=previa.assinatura
    )

    manual = Agendamento.objects.get(inscricao=inscricoes[4])
    assert manual.inicio == horarios[2].inicio and manual.origem == nomes.MANUAL
    # SC-2392: ninguém com dois horários, nenhum horário com duas pessoas.
    assert Agendamento.objects.count() == 4
    assert len(set(Agendamento.objects.values_list("banca_id", "inicio"))) == 4


def test_a_assinatura_velha_e_recusada_com_a_previa_nova(
    gestor, edital_a, etapa_a2, inscricoes, configurada
):
    velha = montar.previa_do_preenchimento(actor=gestor, edital=edital_a, etapa_id=etapa_a2)
    _agendar(gestor, edital_a, etapa_a2, inscricoes[0], _horarios(edital_a, etapa_a2)[0])

    with pytest.raises(montar.MudouDesdeAPrevia) as recusa:
        montar.aplicar_preenchimento(
            actor=gestor, edital=edital_a, etapa_id=etapa_a2, assinatura=velha.assinatura
        )

    assert recusa.value.recusa.code == nomes.AGENDA_MUDOU_DESDE_A_PREVIA
    assert recusa.value.previa.assinatura != velha.assinatura
    assert Agendamento.objects.count() == 1


def test_so_a_participacao_mudar_tambem_invalida_a_previa(
    gestor, edital_a, etapa_a2, inscricoes, configurada
):
    """T-010: uma inscrição nova não sobe a `revision`, mas muda os pares propostos."""
    velha = montar.previa_do_preenchimento(actor=gestor, edital=edital_a, etapa_id=etapa_a2)
    inscrever(edital_a, 1, primeiro=0)

    with pytest.raises(montar.MudouDesdeAPrevia):
        montar.aplicar_preenchimento(
            actor=gestor, edital=edital_a, etapa_id=etapa_a2, assinatura=velha.assinatura
        )


def test_a_configuracao_que_remove_o_horario_devolve_e_diz_quem(
    gestor, edital_a, etapa_a2, inscricoes, configurada
):
    """US2, cenário 9 e FR-7208."""
    horarios = _horarios(edital_a, etapa_a2)
    _agendar(gestor, edital_a, etapa_a2, inscricoes[0], horarios[3])
    _agendar(gestor, edital_a, etapa_a2, inscricoes[1], horarios[0])
    banca = BancaDaAgenda.objects.get()
    menor = configuracao(
        ((SEG, ((time(8), time(8, 30)),)),),
        bancas=(Banca(str(banca.pk), "Banca 1", "https://x", 1),),
    )

    salva = configurar.salvar(actor=gestor, edital=edital_a, etapa_id=etapa_a2, configuracao=menor)

    assert salva.devolvidos == ["Candidata 1"]
    assert "voltou" in salva.frase and "Candidata 1" in salva.frase
    assert list(Agendamento.objects.values_list("inscricao_id", flat=True)) == [inscricoes[1].id]
    agenda = leitura.agenda_da_etapa(edital_a, etapa_a2)
    frase = leitura.devolvidos_pela_ultima_configuracao(
        agenda, leitura.montagem(edital_a, etapa_a2, agenda)
    )
    assert frase.startswith('1 pessoa voltou para "Sem horário" porque a configuração de ')
    assert frase.endswith("removeu o horário dela: Candidata 1.")


def test_cada_inscricao_e_uma_linha_de_quem_precisa_de_horario(
    gestor, edital_a, etapa_a2, configurada
):
    """Edge Cases: a participação é por inscrição, e a tela não as junta."""
    duas = inscrever(edital_a, 2, primeiro=90)
    agenda = leitura.agenda_da_etapa(edital_a, etapa_a2)

    sem = [p.inscricao_id for p in leitura.montagem(edital_a, etapa_a2, agenda).sem_horario]

    assert {str(i.id) for i in duas} <= set(sem)
    assert len(sem) == len(set(sem)) == 7
