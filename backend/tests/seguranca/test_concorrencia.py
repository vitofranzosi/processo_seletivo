"""A primeira administração institucional é exclusiva também sob concorrência (revisão do #345).

**A falha era de corrida, e a suíte serial não a via.** A primeira versão trancava só a pessoa de
destino: duas execuções do comando para pessoas diferentes trancavam linhas diferentes, viam as duas
que não havia administrador e gravavam dois vínculos sem `--adicional` (FR-3029).

O teste põe uma barreira **depois** da trava e antes da consulta. Sem a trava global, as duas
execuções chegam juntas à barreira, consultam juntas e gravam as duas. Com ela, a segunda espera a
trava, a barreira da primeira vence o prazo e ela grava sozinha; a segunda entra depois, vê a
primeira e recusa.
"""

import threading

import pytest
from django.db import connection, connections

from processo_seletivo.seguranca import acessos as catalogo
from processo_seletivo.seguranca.application import acessos
from processo_seletivo.seguranca.models import Vinculo
from processo_seletivo.shared.api.problems import DomainError
from tests.seguranca.apoio import AGORA, pessoa

postgresql_only = pytest.mark.skipif(
    connection.vendor != "postgresql", reason="a trava de transação é do PostgreSQL"
)


def _duas_ao_mesmo_tempo(monkeypatch, *, adicional):
    primeira, segunda = pessoa("reitoria-a"), pessoa("reitoria-b")
    barreira = threading.Barrier(2, timeout=2)
    original = acessos.vigentes

    def vigentes_depois_da_barreira():
        try:
            barreira.wait()
        except threading.BrokenBarrierError:
            pass
        return original()

    monkeypatch.setattr(acessos, "vigentes", vigentes_depois_da_barreira)
    resultados = {}

    def conceder(alguem):
        try:
            acessos.conceder_administracao_institucional(
                pessoa=alguem, motivo="Portaria 100", adicional=adicional, now=AGORA
            )
            resultados[alguem.username] = "concedida"
        except DomainError as recusa:
            resultados[alguem.username] = recusa.code
        finally:
            connections.close_all()

    linhas = [threading.Thread(target=conceder, args=(alguem,)) for alguem in (primeira, segunda)]
    for linha in linhas:
        linha.start()
    for linha in linhas:
        linha.join(timeout=30)
    return sorted(resultados.values())


@pytest.mark.django_db(transaction=True)
@postgresql_only
def test_duas_primeiras_administracoes_simultaneas_gravam_uma_so(monkeypatch):
    resultados = _duas_ao_mesmo_tempo(monkeypatch, adicional=False)

    assert resultados == [acessos.ADMINISTRACAO_JA_CONCEDIDA, "concedida"]
    assert Vinculo.objects.filter(papel=catalogo.ADMINISTRADOR_INSTITUCIONAL).count() == 1


@pytest.mark.django_db(transaction=True)
@postgresql_only
def test_com_adicional_explicito_as_duas_simultaneas_valem(monkeypatch):
    acessos.conceder_administracao_institucional(
        pessoa=pessoa("reitoria-0"), motivo="Portaria 99", adicional=False, now=AGORA
    )

    resultados = _duas_ao_mesmo_tempo(monkeypatch, adicional=True)

    assert resultados == ["concedida", "concedida"]
    assert Vinculo.objects.filter(papel=catalogo.ADMINISTRADOR_INSTITUCIONAL).count() == 3
