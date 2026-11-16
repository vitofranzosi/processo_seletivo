"""Dois lotes ao mesmo tempo não põem a mesma pessoa em dois lugares (179, FR-8205, SC-2840).

**Transacional, com duas conexões de verdade**, como a concorrência da montagem da `167`: o que se
prova é a trava do Processo, que o `comando_de_comissao` toma antes de tudo (research T-006). A
conexão principal segura a trava e grava a primeira Atribuição, como um lote que chegou antes; a
outra espera nela, e quando entra lê os compromissos já com a primeira — e recusa a linha.
"""

import threading
import time

import pytest
from django.db import connection, transaction
from django.utils import timezone

from processo_seletivo.avaliacoes.models import Atribuicao
from processo_seletivo.processos.models import ProcessoSeletivo
from tests.fixtures.avaliacoes_com_agenda import agenda, atribuir, comissao, por_sessao
from tests.fixtures.comissao import inscrever

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="a trava da linha é do PostgreSQL"
)


def _em_espera_na_trava(saida, alvo):
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


@postgresql_only
def test_o_segundo_lote_le_o_primeiro_e_recusa_a_linha(gestor, edital_a, etapa_a2):
    inscrever(edital_a, 4)
    agenda(gestor, edital_a, etapa_a2, quantas_bancas=2)
    membros = comissao(gestor, edital_a, etapa_a2, ["ana"])
    banca1, banca2 = (v for _, v in sorted(por_sessao(edital_a, etapa_a2).items()))
    saida = {}
    with transaction.atomic():
        ProcessoSeletivo.objects.select_for_update().get(pk=edital_a.processo_id)
        thread = _em_espera_na_trava(
            saida,
            lambda: atribuir(
                gestor, edital_a, etapa_a2, [membros["ana"]], banca2[:1], chave="segundo"
            ),
        )
        # O "primeiro lote": a mesma pessoa, no mesmo horário, na outra banca.
        Atribuicao.objects.create(
            membro=membros["ana"],
            edital=edital_a,
            etapa_id=etapa_a2,
            inscricao=banca1[0],
            criado_em=timezone.now(),
            criado_por=gestor.subject,
        )
    thread.join(timeout=20)
    assert "erro" not in saida, saida.get("erro")
    assert saida["valor"]["feitas"] == 0
    assert saida["valor"]["recusadas"] == 1
    assert "já tem entrevista" in saida["valor"]["motivos"][0]["motivo"]
    assert Atribuicao.objects.filter(membro=membros["ana"], ativo=True).count() == 1
