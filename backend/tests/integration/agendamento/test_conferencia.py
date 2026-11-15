"""A conferência antes de publicar (167, T043, FR-7220 a FR-7222, SC-2393, US3 cenários 1 a 4).

A conferência não grava, não envia e não reserva; cada impedimento é nomeado e leva ao lugar de
corrigir; a Etapa sem Evento só avisa; e a agenda completa não tem impedimento nenhum.
"""

import pytest

from processo_seletivo.agendamento.application import conferir, configurar, leitura, montar
from processo_seletivo.agendamento.domain import nomes
from processo_seletivo.agendamento.domain.horarios import Banca
from processo_seletivo.agendamento.models import AgendaDaEtapa, Agendamento, AtoDaAgenda
from processo_seletivo.auditoria.models import IdempotencyRecord, RegistroAuditoria
from tests.fixtures.agenda_da_etapa import (
    DUAS_HORAS,
    SEG,
    configuracao,
    eliminar_na_primeira,
    montar_completa,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def _conferencia(gestor, edital, etapa):
    return conferir.conferencia(actor=gestor, edital=edital, etapa_id=etapa)


def _codigos(conferencia):
    return [impedimento.codigo for impedimento in conferencia.impedimentos]


def _contagem():
    return (
        AgendaDaEtapa.objects.values_list("revision", flat=True).first(),
        Agendamento.objects.count(),
        AtoDaAgenda.objects.count(),
        RegistroAuditoria.objects.count(),
        IdempotencyRecord.objects.count(),
    )


def test_a_conferencia_nao_grava_nem_reserva_nada(gestor, edital_a, etapa_a2, inscricoes):
    montar_completa(gestor, edital_a, etapa_a2)
    antes = _contagem()

    for _ in range(2):
        conferencia = _conferencia(gestor, edital_a, etapa_a2)

    assert _contagem() == antes
    assert conferencia.pode_publicar


def test_a_agenda_completa_mostra_fatos_previa_mensagem_e_autoridades(
    gestor, edital_a, etapa_a2, inscricoes
):
    """US3, cenário 4: nada impede, e a tela tem tudo o que a FR-7222 enumera."""
    montar_completa(gestor, edital_a, etapa_a2)

    conferencia = _conferencia(gestor, edital_a, etapa_a2)

    assert conferencia.impedimentos == []
    fatos = dict(conferencia.fatos)
    assert list(fatos) == [
        "Etapa",
        "Período no cronograma",
        "Dias da agenda",
        "Atendimento",
        "Pessoas",
    ]
    assert fatos["Pessoas"].startswith("5 de 5 com horário")
    assert "Segunda-feira, 23/11/2026" in fatos["Dias da agenda"]
    horarios = [h for dia in conferencia.conteudo["dias"] for h in dia["horarios"]]
    assert len(horarios) == 5
    assert conferencia.mensagem_de_exemplo["assunto"].startswith("Seu horário: ")
    # A mensagem é a única peça que leva a sala, e leva a de uma pessoa só (FR-7229).
    assert "Sala virtual: https://sala.exemplo/1" in conferencia.mensagem_de_exemplo["corpo"]
    assert "https://sala.exemplo/1" not in str(conferencia.conteudo)
    assert conferencia.autoridades
    assert [linha.pronta for linha in conferencia.prontidao] == [True, None, True, None]


def test_pessoas_sem_horario_impedem_com_a_lista(
    gestor, edital_a, etapa_a2, inscricoes, configurada
):
    """US3, cenário 1: quatro horários para cinco pessoas, ninguém agendado."""
    conferencia = _conferencia(gestor, edital_a, etapa_a2)

    impedimento = conferencia.impedimentos[0]
    assert impedimento.codigo == nomes.PARTICIPANTES_SEM_HORARIO
    assert impedimento.frase.startswith("5 pessoas estão sem horário.")
    assert "Volte à montagem e agende essas pessoas." in impedimento.frase
    assert impedimento.caminho == "montar"
    assert len(impedimento.pessoas) == 5
    assert "Candidata 1 (INS-" in impedimento.pessoas[0]
    assert not conferencia.pode_publicar


def test_agendada_que_nao_participa_mais_impede_e_e_nomeada(
    gestor, edital_a, etapa_a1, etapa_a2, inscricoes
):
    """US3, cenário 2: a Ocorrência na primeira Etapa elimina quem já tinha horário."""
    montar_completa(gestor, edital_a, etapa_a2)
    eliminar_na_primeira(gestor, edital_a, etapa_a1, inscricoes[:1])

    conferencia = _conferencia(gestor, edital_a, etapa_a2)

    assert nomes.AGENDADOS_QUE_NAO_PARTICIPAM in _codigos(conferencia)
    impedimento = next(
        i for i in conferencia.impedimentos if i.codigo == nomes.AGENDADOS_QUE_NAO_PARTICIPAM
    )
    assert impedimento.frase.startswith(f"Candidata 1 ({inscricoes[0].protocolo}) tem horário")
    assert "Volte à montagem e libere o horário." in impedimento.frase


def test_banca_sem_endereco_impede_e_nomeia_a_banca(gestor, edital_a, etapa_a2, inscricoes):
    """US3, cenário 3."""
    bancas = (
        Banca("nova-1", "Banca 1", "https://sala.exemplo/1", 1),
        Banca("nova-2", "Banca 2", "", 2),
    )
    montar_completa(
        gestor, edital_a, etapa_a2, config=configuracao(dias=((SEG, DUAS_HORAS),), bancas=bancas)
    )

    conferencia = _conferencia(gestor, edital_a, etapa_a2)

    assert _codigos(conferencia) == [nomes.BANCA_SEM_LOCAL]
    impedimento = conferencia.impedimentos[0]
    assert impedimento.frase.startswith("Banca 2 sem endereço da sala.")
    assert impedimento.caminho == "configurar"
    assert conferencia.prontidao[2].pronta is False


def test_a_configuracao_e_relida_contra_o_evento(
    gestor, edital_a, etapa_a2, inscricoes, monkeypatch
):
    """O Evento retificado depois da configuração: o dia fora do período vira impedimento."""
    montar_completa(gestor, edital_a, etapa_a2)
    # O Evento passou a ser só 25/11, e a agenda tem 23/11.
    vigente = SEG.replace(day=25)
    monkeypatch.setattr(
        conferir, "etapa_e_periodo", lambda edital, etapa_id: ({"name": "E"}, (vigente, vigente))
    )

    conferencia = _conferencia(gestor, edital_a, etapa_a2)

    assert _codigos(conferencia) == [nomes.CONFIGURACAO_INVALIDA]
    assert "está fora do período da Etapa" in conferencia.impedimentos[0].frase
    assert conferencia.prontidao[1].pronta is False


def test_sem_autoridade_vigente_impede(gestor, edital_a, etapa_a2, inscricoes, monkeypatch):
    """A autoridade da suíte já assinou atos, e a usada não se reescreve: a vigência some aqui."""
    montar_completa(gestor, edital_a, etapa_a2)
    monkeypatch.setattr(conferir.unidades, "autoridades_vigentes", lambda codigo, data: [])

    conferencia = _conferencia(gestor, edital_a, etapa_a2)

    assert _codigos(conferencia) == [nomes.SEM_AUTORIDADE_VIGENTE]
    assert 'tela "Unidades"' in conferencia.impedimentos[0].frase
    assert conferencia.prontidao[3].pronta is False


def test_a_etapa_sem_evento_so_avisa(gestor, edital_a, etapa_a2, inscricoes):
    """Edge Cases: a Etapa A2 não tem Evento; a conferência avisa, e não impede."""
    montar_completa(gestor, edital_a, etapa_a2)

    conferencia = _conferencia(gestor, edital_a, etapa_a2)

    assert conferencia.periodo is None
    assert conferencia.avisos == [
        "Esta Etapa não tem período publicado no cronograma; os dias não foram conferidos contra "
        "ele."
    ]
    assert conferencia.pode_publicar


def test_a_assinatura_muda_com_a_agenda_e_com_a_participacao(
    gestor, edital_a, etapa_a1, etapa_a2, inscricoes
):
    """T-010: a assinatura vê o agendamento e também a participação que muda sem tocar a agenda."""
    montar_completa(gestor, edital_a, etapa_a2)
    primeira = _conferencia(gestor, edital_a, etapa_a2).assinatura
    assert _conferencia(gestor, edital_a, etapa_a2).assinatura == primeira

    eliminar_na_primeira(gestor, edital_a, etapa_a1, inscricoes[:1])
    segunda = _conferencia(gestor, edital_a, etapa_a2).assinatura
    assert segunda != primeira

    montar.liberar(actor=gestor, edital=edital_a, etapa_id=etapa_a2, inscricao_id=inscricoes[0].id)
    assert _conferencia(gestor, edital_a, etapa_a2).assinatura not in {primeira, segunda}


def test_sem_agenda_a_conferencia_recusa(gestor, edital_a, etapa_a2, inscricoes):
    from processo_seletivo.shared.api.problems import DomainError

    with pytest.raises(DomainError) as recusa:
        _conferencia(gestor, edital_a, etapa_a2)
    assert recusa.value.code == nomes.SEM_CONFIGURACAO
    assert leitura.agenda_da_etapa(edital_a, etapa_a2) is None
    assert configurar  # o módulo da configuração continua o caminho de quem não tem agenda
