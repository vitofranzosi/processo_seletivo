"""Dois atos sobre o mesmo horário ou a mesma pessoa (167, T074, FR-7247, US5 cenário 7).

**Transacional, com duas conexões de verdade**, como a concorrência da montagem: a conexão
principal segura a trava da agenda e grava por fora o que a outra sessão gravaria; o ato da outra
conexão espera na trava e, quando entra, encontra o horário ocupado ou a pessoa já remarcada.
"""

import pytest
from django.db import connection, transaction
from django.utils import timezone

from processo_seletivo.agendamento.application import atos_individuais, leitura
from processo_seletivo.agendamento.domain import nomes
from processo_seletivo.agendamento.models import AgendaDaEtapa, Agendamento, AtoDaAgenda
from processo_seletivo.shared.api.problems import DomainError
from tests.integration.agendamento.test_concorrencia_da_montagem import _em_espera_na_trava

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="a trava da linha é do PostgreSQL"
)


def _livres(edital, etapa):
    agenda = leitura.agenda_da_etapa(edital, etapa)
    return leitura.montagem(edital, etapa, agenda).livres


def _ocupar_por_fora(agenda, inscricao, horario):
    Agendamento.objects.filter(agenda=agenda, inscricao=inscricao).update(
        banca_id=horario.banca_id,
        inicio=horario.inicio,
        fim=horario.fim,
        feito_por="outra-sessao",
        feito_em=timezone.now(),
    )


def _remarcar(gestor, edital, etapa, inscricao, horario, chave):
    return atos_individuais.remarcar(
        actor=gestor,
        edital=edital,
        etapa_id=etapa,
        inscricao_id=inscricao.id,
        banca_id=horario.banca_id,
        inicio=horario.inicio,
        motivo="falha de conexão comprovada",
        idempotency_key=chave,
    )


@postgresql_only
def test_duas_remarcacoes_para_o_mesmo_horario_so_a_primeira_vale(
    gestor, edital_a, etapa_a2, inscricoes, publicada
):
    alvo = _livres(edital_a, etapa_a2)[0]
    saida = {}
    with transaction.atomic():
        agenda = AgendaDaEtapa.objects.select_for_update().get(pk=publicada.agenda_id)
        thread = _em_espera_na_trava(
            saida,
            lambda: _remarcar(gestor, edital_a, etapa_a2, inscricoes[1], alvo, "segunda"),
        )
        _ocupar_por_fora(agenda, inscricoes[0], alvo)
    thread.join()

    assert saida["erro"].code == nomes.HORARIO_OCUPADO
    assert "acabou de ser ocupado" in saida["erro"].detail
    assert not AtoDaAgenda.objects.filter(especie=nomes.REMARCACAO).exists()


@postgresql_only
def test_a_segunda_remarcacao_da_mesma_pessoa_ve_o_horario_ja_trocado(
    gestor, edital_a, etapa_a2, inscricoes, publicada
):
    livres = _livres(edital_a, etapa_a2)
    primeiro = _remarcar(gestor, edital_a, etapa_a2, inscricoes[0], livres[0], "primeira")
    # A tela da outra sessão ainda oferecia o mesmo horário: a pessoa já está nele.
    with pytest.raises(DomainError) as recusa:
        _remarcar(gestor, edital_a, etapa_a2, inscricoes[0], livres[0], "segunda")
    assert recusa.value.code == nomes.MESMO_HORARIO
    vigente = atos_individuais.vigente_da_inscricao(publicada.agenda, inscricoes[0].id)
    assert vigente.ato_id == primeiro.id
