"""Protocolo de locks Processo→Editais sob concorrência real (PostgreSQL, conexões separadas)."""

import threading
import time

import pytest
from django.db import connection, connections, transaction
from django.db.models import F

from processo_seletivo.processos.models import AtoAdministrativo, Edital, ProcessoSeletivo
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.publicacao import publish_original

GESTOR = frozenset({"processo:encerrar", "processo:cancelar", "edital:encerrar", "edital:cancelar"})

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="locks exigem PostgreSQL"
)


def gestor():
    return Actor("gestor", "cefor", GESTOR)


def cancel(processo, revision, key):
    from processo_seletivo.processos.application.finalizacao import cancel_process

    return cancel_process(
        actor=gestor(),
        processo_id=processo.id,
        expected_revision=revision,
        reason="Cancelamento",
        idempotency_key=key,
        correlation_id="concorrencia",
    )


@pytest.fixture
def edital_publicado(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload)


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@postgresql_only
def test_process_cancellation_waits_for_a_concurrent_edital_transition(
    api_client, edital_publicado
):
    """TOCTOU: o Edital é encerrado por uma transação ainda aberta quando o cancelamento começa.

    Sem o lock nos Editais, o cancelamento leria o estado anterior ao commit e recusaria por
    editais_pendentes. Com o lock, ele espera, enxerga o Edital já final e conclui o ato.
    """
    processo = ProcessoSeletivo.objects.get(pk=edital_publicado.processo_id)
    lock_obtido = threading.Event()
    falhas = []

    def encerrar_segurando_o_lock():
        try:
            with transaction.atomic():
                Edital.objects.select_for_update().get(pk=edital_publicado.id)
                lock_obtido.set()
                # Mantém a transação aberta enquanto o cancelamento tenta avançar.
                time.sleep(0.5)
                Edital.objects.filter(pk=edital_publicado.id).update(
                    status=Edital.Status.ENCERRADO, revision=F("revision") + 1
                )
        except Exception as exc:  # noqa: BLE001 — repassado para o corpo do teste
            falhas.append(exc)
        finally:
            connections.close_all()

    thread = threading.Thread(target=encerrar_segurando_o_lock)
    thread.start()
    assert lock_obtido.wait(timeout=5)

    inicio = time.monotonic()
    processo_cancelado, _ = cancel(processo, processo.revision, "cancelar-key-00000001")
    esperou = time.monotonic() - inicio

    thread.join(timeout=10)
    assert not falhas, falhas
    assert esperou >= 0.2, "o cancelamento não aguardou o lock do Edital"
    assert processo_cancelado.status == ProcessoSeletivo.Status.CANCELADO
    assert Edital.objects.get(pk=edital_publicado.pk).status == Edital.Status.ENCERRADO


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@postgresql_only
def test_cancellation_is_rejected_while_an_edital_is_still_open(api_client, edital_publicado):
    processo = ProcessoSeletivo.objects.get(pk=edital_publicado.processo_id)
    with pytest.raises(DomainError) as exc:
        cancel(processo, processo.revision, "bloqueado-key-0000001")
    assert exc.value.code == "editais_pendentes"
    assert ProcessoSeletivo.objects.get(pk=processo.pk).status == processo.status
    assert not AtoAdministrativo.objects.filter(
        aggregate_id=processo.id, operation="CANCELAR"
    ).exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@postgresql_only
def test_concurrent_cancellations_produce_exactly_one_act(api_client, edital_publicado):
    """Duas tentativas simultâneas: uma vence pelo CAS, a outra é rejeitada."""
    from processo_seletivo.processos.application.finalizacao import close_edital

    close_edital(
        actor=gestor(),
        edital_id=edital_publicado.id,
        expected_revision=edital_publicado.revision,
        reason="Etapas concluídas",
        idempotency_key="preparo-key-000000001",
        correlation_id="concorrencia",
    )
    processo = ProcessoSeletivo.objects.get(pk=edital_publicado.processo_id)
    resultados = []
    barreira = threading.Barrier(2, timeout=10)

    def tentar(indice):
        try:
            barreira.wait()
            with transaction.atomic():
                resultados.append(
                    cancel(processo, processo.revision, f"corrida-key-0000000{indice}")[0].status
                )
        except Exception as exc:  # noqa: BLE001 — a perdedora deve falhar de forma controlada
            resultados.append(exc)
        finally:
            connections.close_all()

    threads = [threading.Thread(target=tentar, args=(indice,)) for indice in (1, 2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=15)

    vencedoras = [item for item in resultados if item == ProcessoSeletivo.Status.CANCELADO]
    assert len(vencedoras) == 1, resultados
    assert (
        AtoAdministrativo.objects.filter(aggregate_id=processo.id, operation="CANCELAR").count()
        == 1
    )
    assert ProcessoSeletivo.objects.get(pk=processo.pk).status == ProcessoSeletivo.Status.CANCELADO


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@postgresql_only
def test_final_states_never_return_to_a_previous_one_in_the_database(api_client, edital_publicado):
    from processo_seletivo.processos.application.finalizacao import cancel_edital, close_edital

    encerrado, _ = close_edital(
        actor=gestor(),
        edital_id=edital_publicado.id,
        expected_revision=edital_publicado.revision,
        reason="Etapas concluídas",
        idempotency_key="final-key-0000000001",
        correlation_id="concorrencia",
    )
    with pytest.raises(DomainError, match="estado final"):
        cancel_edital(
            actor=gestor(),
            edital_id=edital_publicado.id,
            expected_revision=encerrado.revision,
            reason="Tentativa posterior",
            idempotency_key="final-key-0000000002",
            correlation_id="concorrencia",
        )
    assert Edital.objects.get(pk=edital_publicado.pk).status == Edital.Status.ENCERRADO


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@postgresql_only
def test_edital_creation_loses_to_a_concurrent_process_closure(api_client, edital_publicado):
    """FR-012 da 003: criar Edital e encerrar o Processo decidem coisas incompatíveis.

    Sem `select_for_update` no Processo, a criação lê `ATIVO`, o encerramento faz commit no
    intervalo e o `INSERT` conclui: nasce um Edital dentro de um Processo já encerrado. Com o
    bloqueio, a criação espera, enxerga o estado final e é recusada.
    """
    from processo_seletivo.processos.application.commands import add_edital

    processo = ProcessoSeletivo.objects.get(pk=edital_publicado.processo_id)
    ProcessoSeletivo.objects.filter(pk=processo.pk).update(status=ProcessoSeletivo.Status.ATIVO)
    lock_obtido = threading.Event()
    resultado = {}

    def encerrar_segurando_o_lock():
        try:
            with transaction.atomic():
                ProcessoSeletivo.objects.select_for_update().get(pk=processo.pk)
                lock_obtido.set()
                time.sleep(0.5)
                ProcessoSeletivo.objects.filter(pk=processo.pk).update(
                    status=ProcessoSeletivo.Status.ENCERRADO, revision=F("revision") + 1
                )
        finally:
            connections.close_all()

    encerramento = threading.Thread(target=encerrar_segurando_o_lock)
    encerramento.start()
    assert lock_obtido.wait(timeout=5)

    try:
        add_edital(
            actor=Actor("gestor", "cefor", frozenset({"edital:criar"})),
            processo_id=processo.id,
            data={"number": "99", "year": 2026, "title": "Depois do fim"},
            idempotency_key="concorrencia-edital-1",
            correlation_id="concorrencia",
        )
        resultado["criado"] = True
    except DomainError as exc:
        resultado["code"] = exc.code
    finally:
        encerramento.join(timeout=5)

    assert resultado.get("criado") is None
    assert resultado["code"] == "invalid_state"
    assert Edital.objects.filter(processo=processo).count() == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
@postgresql_only
def test_process_cancellation_waits_for_a_concurrent_edital_creation(api_client, edital_publicado):
    """A recíproca da corrida: quem cria primeiro segura o Processo e o cancelamento espera.

    Sem o lock, o cancelamento leria a lista de Editais antes do `INSERT` concorrente, não veria
    pendência e cancelaria — deixando um Edital em elaboração dentro de Processo cancelado. Com
    ele, o cancelamento espera, enxerga o Edital recém-criado e recusa por `editais_pendentes`.
    """
    from processo_seletivo.processos.application.commands import add_edital

    processo = ProcessoSeletivo.objects.get(pk=edital_publicado.processo_id)
    ProcessoSeletivo.objects.filter(pk=processo.pk).update(status=ProcessoSeletivo.Status.ATIVO)
    # O Edital que já existe precisa estar final: assim a única pendência possível é a que a
    # transação concorrente cria, e é ela que o teste está medindo.
    Edital.objects.filter(pk=edital_publicado.pk).update(status=Edital.Status.ENCERRADO)
    criado = threading.Event()
    falhas = []

    def criar_segurando_o_lock():
        try:
            with transaction.atomic():
                add_edital(
                    actor=Actor("gestor", "cefor", frozenset({"edital:criar"})),
                    processo_id=processo.id,
                    data={"number": "02", "year": 2026, "title": "Segundo Edital"},
                    idempotency_key="concorrencia-edital-2",
                    correlation_id="concorrencia",
                )
                criado.set()
                # Mantém a transação aberta enquanto o cancelamento tenta avançar.
                time.sleep(0.5)
        except Exception as exc:  # noqa: BLE001 — reportado ao thread principal
            falhas.append(exc)
            criado.set()
        finally:
            connections.close_all()

    criacao = threading.Thread(target=criar_segurando_o_lock)
    criacao.start()
    assert criado.wait(timeout=5)

    processo.refresh_from_db()
    with pytest.raises(DomainError) as recusa:
        cancel(processo, processo.revision, "concorrencia-cancelamento")
    criacao.join(timeout=5)

    assert not falhas
    assert recusa.value.code == "editais_pendentes"
    assert "02/2026" in recusa.value.detail
    assert ProcessoSeletivo.objects.get(pk=processo.pk).status == ProcessoSeletivo.Status.ATIVO
    assert Edital.objects.filter(processo=processo).count() == 2
