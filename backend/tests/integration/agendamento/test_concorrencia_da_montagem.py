"""As duas unicidades sob operações simultâneas (167, T025, FR-7211, SC-2392, US2 cenário 8).

**Transacional, com duas conexões de verdade**, porque o que se prova mora no banco: a trava da
agenda, que serializa os gestos, e o `UNIQUE`, que é a última guarda. A sobreposição é provocada: a
conexão principal segura a trava e grava; a outra espera nela, e quando entra encontra o horário
ocupado ou a agenda mudada.
"""

import threading
import time

import pytest
from django.db import IntegrityError, connection, transaction
from django.utils import timezone

from processo_seletivo.agendamento.application import leitura, montar
from processo_seletivo.agendamento.domain import nomes
from processo_seletivo.agendamento.models import AgendaDaEtapa, Agendamento

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="a trava da linha é do PostgreSQL"
)


def _em_espera_na_trava(saida, alvo):
    """Roda `alvo` noutra conexão e espera até ela estar parada na trava da agenda."""

    def corpo():
        try:
            saida["valor"] = alvo()
        except Exception as erro:  # noqa: BLE001 — o caso inspeciona o que a corrida produziu
            saida["erro"] = erro
        finally:
            connection.close()

    thread = threading.Thread(target=corpo)
    thread.start()
    limite = time.monotonic() + 10
    while time.monotonic() < limite:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT count(*) FROM pg_stat_activity "
                "WHERE wait_event_type = 'Lock' AND datname = current_database()"
            )
            if cursor.fetchone()[0]:
                break
        time.sleep(0.02)
    return thread


def _horario(edital, etapa, indice=0):
    agenda = leitura.agenda_da_etapa(edital, etapa)
    return leitura.montagem(edital, etapa, agenda).horarios[indice]


def _gravar_por_fora(agenda, inscricao, horario):
    Agendamento.objects.create(
        agenda=agenda,
        inscricao=inscricao,
        banca_id=horario.banca_id,
        inicio=horario.inicio,
        fim=horario.fim,
        origem=nomes.MANUAL,
        feito_por="outra-sessao",
        feito_em=timezone.now(),
    )
    AgendaDaEtapa.objects.filter(pk=agenda.pk).update(revision=agenda.revision + 1)


@postgresql_only
def test_dois_agendamentos_no_mesmo_horario_um_ocupa(
    gestor, edital_a, etapa_a2, inscricoes, configurada
):
    horario = _horario(edital_a, etapa_a2)
    saida = {}
    with transaction.atomic():
        agenda = AgendaDaEtapa.objects.select_for_update().get(pk=configurada.pk)
        thread = _em_espera_na_trava(
            saida,
            lambda: montar.agendar(
                actor=gestor,
                edital=edital_a,
                etapa_id=etapa_a2,
                inscricao_id=inscricoes[1].id,
                banca_id=horario.banca_id,
                inicio=horario.inicio,
            ),
        )
        _gravar_por_fora(agenda, inscricoes[0], horario)
    thread.join()

    assert saida["erro"].code == nomes.HORARIO_OCUPADO
    assert "acabou de ser ocupado" in saida["erro"].detail
    assert list(Agendamento.objects.values_list("inscricao_id", flat=True)) == [inscricoes[0].id]


@postgresql_only
def test_a_mesma_pessoa_em_dois_horarios_um_vale(
    gestor, edital_a, etapa_a2, inscricoes, configurada
):
    saida = {}
    segundo = _horario(edital_a, etapa_a2, 1)
    with transaction.atomic():
        agenda = AgendaDaEtapa.objects.select_for_update().get(pk=configurada.pk)
        thread = _em_espera_na_trava(
            saida,
            lambda: montar.agendar(
                actor=gestor,
                edital=edital_a,
                etapa_id=etapa_a2,
                inscricao_id=inscricoes[0].id,
                banca_id=segundo.banca_id,
                inicio=segundo.inicio,
            ),
        )
        _gravar_por_fora(agenda, inscricoes[0], _horario(edital_a, etapa_a2, 0))
    thread.join()

    assert saida["erro"].code == nomes.PESSOA_JA_AGENDADA
    assert Agendamento.objects.filter(inscricao=inscricoes[0]).count() == 1


@postgresql_only
def test_preenchimento_simultaneo_a_um_agendamento_a_mao(
    gestor, edital_a, etapa_a2, inscricoes, configurada
):
    previa = montar.previa_do_preenchimento(actor=gestor, edital=edital_a, etapa_id=etapa_a2)
    saida = {}
    with transaction.atomic():
        agenda = AgendaDaEtapa.objects.select_for_update().get(pk=configurada.pk)
        thread = _em_espera_na_trava(
            saida,
            lambda: montar.aplicar_preenchimento(
                actor=gestor, edital=edital_a, etapa_id=etapa_a2, assinatura=previa.assinatura
            ),
        )
        _gravar_por_fora(agenda, inscricoes[4], _horario(edital_a, etapa_a2, 0))
    thread.join()

    assert isinstance(saida["erro"], montar.MudouDesdeAPrevia)
    pares = list(Agendamento.objects.values_list("inscricao_id", "banca_id", "inicio"))
    assert len({p[0] for p in pares}) == len({p[1:] for p in pares}) == len(pares) == 1


@postgresql_only
def test_o_banco_recusa_duas_pessoas_no_mesmo_horario(edital_a, etapa_a2, inscricoes, configurada):
    """A última guarda (T-009): mesmo por fora dos comandos, o `UNIQUE` recusa."""
    horario = _horario(edital_a, etapa_a2)
    _gravar_por_fora(configurada, inscricoes[0], horario)

    with pytest.raises(IntegrityError, match="uq_agendamento_horario"), transaction.atomic():
        _gravar_por_fora(configurada, inscricoes[1], horario)
