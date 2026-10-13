"""O despacho sob concorrência, e a interrupção no meio do envio (066, US5, `R-002`, `FR-1273`).

**Transacional, e com threads de verdade**, porque o que se prova mora no banco: a trava consultiva
global, a trava do aviso que a interrupção e o início da tentativa disputam, e o `UNIQUE` que é a
última porta. Nada disso é observável dentro de uma transação que vai ser desfeita.

**A sobreposição é provocada, e não esperada.** O servidor simulado chama, de dentro do envio, a
segunda execução ou a interrupção, numa thread com conexão própria — e o caso fica determinístico,
sem `sleep`.
"""

import threading

import pytest
from django.core import mail
from django.db import IntegrityError, connection, transaction
from django.utils import timezone

from processo_seletivo.avisos.application.despacho import despachar
from processo_seletivo.avisos.application.interromper import interromper
from processo_seletivo.avisos.models import Aviso, InterrupcaoDoAviso, TentativaDeEnvio
from tests.fixtures import correio
from tests.fixtures.avisos import PUBLICADORA, avisar_resultado
from tests.fixtures.divulgacao import montar_ato_publicavel, publicar_o_ato

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="as travas consultivas são do PostgreSQL"
)


@pytest.fixture
def avisado(gestor, api_client, manager_headers, process_payload):
    cenario = montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        pontuacoes=("90.0000", "80.0000", "70.0000"),
    )
    publicacao = publicar_o_ato(cenario)
    return Aviso.objects.get(pk=avisar_resultado(cenario["edital"], publicacao.marco_id)["aviso"])


def _noutra_thread(funcao):
    """Roda `funcao` numa thread com conexão própria, e devolve o que ela devolveu ou levantou."""
    saida = {}

    def alvo():
        try:
            saida["valor"] = funcao()
        except Exception as erro:  # noqa: BLE001 — o caso inspeciona o que a corrida produziu
            saida["erro"] = erro
        finally:
            connection.close()

    thread = threading.Thread(target=alvo)
    thread.start()
    thread.join()
    return saida


@postgresql_only
def test_duas_execucoes_ao_mesmo_tempo_uma_sai_pela_trava(avisado, settings):
    segunda = {}

    def durante_o_envio(_mensagens):
        if not segunda:
            segunda.update(_noutra_thread(despachar))

    correio.usar(settings, ao_enviar=durante_o_envio)

    primeira = despachar()

    assert segunda["valor"].ocupado, "a segunda execução encontrou a trava e saiu"
    assert primeira.tentadas == 3
    assert TentativaDeEnvio.objects.count() == 3
    assert len(mail.outbox) == 3, "ninguém recebeu duas vezes"


@postgresql_only
def test_a_mesma_tentativa_duas_vezes_e_barrada_pelo_banco(avisado):
    destinatario = avisado.destinatarios.first()
    TentativaDeEnvio.objects.create(destinatario=destinatario, numero=1, iniciada_em=timezone.now())

    with pytest.raises(IntegrityError), transaction.atomic():
        TentativaDeEnvio.objects.create(
            destinatario=destinatario, numero=1, iniciada_em=timezone.now()
        )


def test_aviso_interrompido_nao_tenta_os_pendentes(avisado, settings):
    correio.usar(settings)
    interromper(
        actor=PUBLICADORA,
        aviso_id=avisado.id,
        motivo="Modelo errado.",
        idempotency_key="interromper-antes",
        correlation_id="teste-066",
    )

    resumo = despachar()

    assert resumo.tentadas == 0
    assert mail.outbox == []


@postgresql_only
def test_interromper_no_meio_da_execucao_impede_a_tentativa_seguinte(avisado, settings):
    """A interrupção conferida antes de **cada** tentativa, e não só no início da execução."""
    enviadas = []

    def durante_o_envio(mensagens):
        enviadas.extend(mensagens)
        if len(enviadas) == 2:
            saida = _noutra_thread(
                lambda: interromper(
                    actor=PUBLICADORA,
                    aviso_id=avisado.id,
                    motivo="Engano percebido no meio do envio.",
                    idempotency_key="interromper-no-meio",
                    correlation_id="teste-066",
                )
            )
            assert "erro" not in saida, saida.get("erro")

    correio.usar(settings, ao_enviar=durante_o_envio)

    resumo = despachar()

    assert InterrupcaoDoAviso.objects.filter(aviso=avisado).exists()
    assert resumo.tentadas == 2, "a terceira não começou depois da interrupção"
    assert TentativaDeEnvio.objects.count() == 2
    assert len(mail.outbox) == 2
