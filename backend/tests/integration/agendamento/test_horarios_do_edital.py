"""O horário de cada inscrição, das duas fontes, em consultas fixas (179, FR-8201, research T-002).

Antes da publicação, o horário é o da montagem; depois, o vigente publicado — e nunca os dois para a
mesma agenda. A remarcação traz o vigente novo com a marca; o cancelamento tira a pessoa.
"""

from datetime import date

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from processo_seletivo.agendamento.application import atos_individuais, leitura
from processo_seletivo.agendamento.application.leitura import (
    MONTAGEM,
    PUBLICADO,
    horarios_do_edital,
)
from tests.fixtures.agenda_da_etapa import eliminar_na_primeira
from tests.fixtures.avaliacoes_com_agenda import agenda
from tests.fixtures.comissao import inscrever

pytestmark = [pytest.mark.django_db]

# O Evento da primeira Etapa do Processo A é em 01/09/2026, e a configuração recusa dia fora dele.
DIA_DA_A1 = date(2026, 9, 1)


def test_sem_agenda_nao_ha_horario(edital_a):
    assert horarios_do_edital(edital_a) == {}


def test_antes_da_publicacao_a_fonte_e_a_montagem(gestor, edital_a, etapa_a2):
    pessoas = inscrever(edital_a, 4)
    agenda(gestor, edital_a, etapa_a2, publicar=False)
    horarios = horarios_do_edital(edital_a)
    assert {i for (_, i) in horarios} == {p.id for p in pessoas}
    assert {h.fonte for h in horarios.values()} == {MONTAGEM}
    assert horarios_do_edital(edital_a, so_publicados=True) == {}


def test_depois_da_publicacao_a_fonte_e_o_publicado(gestor, edital_a, etapa_a2):
    pessoas = inscrever(edital_a, 4)
    agenda(gestor, edital_a, etapa_a2, quantas_bancas=2)
    horarios = horarios_do_edital(edital_a)
    assert {h.fonte for h in horarios.values()} == {PUBLICADO}
    assert horarios == horarios_do_edital(edital_a, so_publicados=True)
    um = horarios[(str(etapa_a2), pessoas[0].id)]
    assert um.banca_nome in {"Banca 01", "Banca 02"}
    assert um.inicio < um.fim
    assert um.remarcado_em is None


def test_a_remarcacao_traz_o_vigente_e_o_cancelamento_tira(gestor, edital_a, etapa_a1, etapa_a2):
    pessoas = inscrever(edital_a, 3)
    agenda(gestor, edital_a, etapa_a2)
    agenda_ = leitura.agenda_da_etapa(edital_a, etapa_a2)
    montagem = leitura.montagem(edital_a, etapa_a2, agenda_)
    livre = montagem.livres[-1]
    atos_individuais.remarcar(
        actor=gestor,
        edital=edital_a,
        etapa_id=etapa_a2,
        inscricao_id=pessoas[0].id,
        inicio=livre.inicio,
        banca_id=livre.banca_id,
        motivo="falha de conexão",
        idempotency_key="remarcar-179",
    )
    remarcado = horarios_do_edital(edital_a)[(str(etapa_a2), pessoas[0].id)]
    assert remarcado.inicio == livre.inicio
    assert remarcado.remarcado_em is not None
    eliminar_na_primeira(gestor, edital_a, etapa_a1, [pessoas[1]])
    atos_individuais.cancelar(
        actor=gestor,
        edital=edital_a,
        etapa_id=etapa_a2,
        inscricao_id=pessoas[1].id,
        motivo="desistiu",
        idempotency_key="cancelar-179",
    )
    assert (str(etapa_a2), pessoas[1].id) not in horarios_do_edital(edital_a)


def test_duas_agendas_do_mesmo_edital(gestor, edital_a, etapa_a1, etapa_a2):
    pessoas = inscrever(edital_a, 2)
    agenda(gestor, edital_a, etapa_a2)
    agenda(gestor, edital_a, etapa_a1, dias=(DIA_DA_A1,), publicar=False)
    horarios = horarios_do_edital(edital_a)
    assert horarios[(str(etapa_a2), pessoas[0].id)].fonte == PUBLICADO
    assert horarios[(str(etapa_a1), pessoas[0].id)].fonte == MONTAGEM


@pytest.mark.parametrize("quantas", [3, 8])
def test_consultas_fixas(gestor, edital_a, etapa_a1, etapa_a2, quantas):
    inscrever(edital_a, quantas)
    agenda(gestor, edital_a, etapa_a2)
    agenda(gestor, edital_a, etapa_a1, dias=(DIA_DA_A1,), publicar=False)
    with CaptureQueriesContext(connection) as consultas:
        horarios_do_edital(edital_a)
    assert len(consultas) == 4, [c["sql"][:120] for c in consultas]
