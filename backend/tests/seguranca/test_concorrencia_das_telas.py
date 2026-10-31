"""Concessões e revogações simultâneas pela tela (107, casos-limite da spec).

As duas pela mesma camada que a tela chama — `conceder` e `revogar` da `106` —, cada uma numa
conexão própria, com uma barreira **depois** da trava da pessoa. Se a trava faltasse, as duas
chegariam juntas à barreira, consultariam juntas e gravariam as duas; com ela, a segunda espera, a
barreira da primeira vence o prazo, e a segunda encontra o que a primeira gravou.
"""

import threading

import pytest
from django.db import connection, connections

from processo_seletivo.seguranca import acessos as catalogo
from processo_seletivo.seguranca.application import acessos
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.seguranca.models import RevogacaoDeVinculo, Vinculo
from processo_seletivo.shared.api.problems import DomainError
from tests.seguranca.apoio import AGORA, pessoa, vincular

pytestmark = [
    pytest.mark.django_db(transaction=True),
    pytest.mark.skipif(connection.vendor != "postgresql", reason="trava de linha do PostgreSQL"),
]


def _administradores():
    atores = []
    for nome in ("admin-a", "admin-b"):
        alguem = pessoa(nome)
        vincular(alguem, "cefor", catalogo.ADMINISTRADOR_DE_ACESSOS)
        atores.append(Actor(alguem.username, "cefor", frozenset({catalogo.GERIR})))
    return atores


def _ao_mesmo_tempo(monkeypatch, atos):
    barreira = threading.Barrier(len(atos), timeout=2)
    original = acessos.vigentes

    def vigentes_depois_da_barreira():
        try:
            barreira.wait()
        except threading.BrokenBarrierError:
            pass
        return original()

    monkeypatch.setattr(acessos, "vigentes", vigentes_depois_da_barreira)
    resultados = []

    def executar(ato):
        try:
            ato()
            resultados.append("gravado")
        except DomainError as recusa:
            resultados.append(recusa.code)
        finally:
            connections.close_all()

    linhas = [threading.Thread(target=executar, args=(ato,)) for ato in atos]
    for linha in linhas:
        linha.start()
    for linha in linhas:
        linha.join(timeout=30)
    return sorted(resultados)


def test_duas_concessoes_do_mesmo_papel_gravam_uma(monkeypatch):
    primeiro, segundo = _administradores()
    bea = pessoa("bea")

    def conceder(ator):
        return lambda: acessos.conceder(
            ator, pessoa=bea, escopo="cefor", papel="elaborador", motivo="Memorando", now=AGORA
        )

    resultados = _ao_mesmo_tempo(monkeypatch, [conceder(primeiro), conceder(segundo)])

    assert resultados == ["gravado", acessos.VINCULO_JA_VIGENTE]
    assert Vinculo.objects.filter(pessoa=bea, papel="elaborador").count() == 1


def test_duas_revogacoes_do_mesmo_vinculo_gravam_uma(monkeypatch):
    primeiro, segundo = _administradores()
    vinculo = vincular(pessoa("bea"), "cefor", "elaborador")
    # A revogação não consulta `vigentes`; a barreira fica na conferência de já revogado.
    original = RevogacaoDeVinculo.objects.filter
    barreira = threading.Barrier(2, timeout=2)

    def filtro_depois_da_barreira(*args, **kwargs):
        try:
            barreira.wait()
        except threading.BrokenBarrierError:
            pass
        return original(*args, **kwargs)

    monkeypatch.setattr(RevogacaoDeVinculo.objects, "filter", filtro_depois_da_barreira)

    def revogar(ator):
        return lambda: acessos.revogar(ator, vinculo=vinculo, motivo="Saiu", now=AGORA)

    resultados = _ao_mesmo_tempo(monkeypatch, [revogar(primeiro), revogar(segundo)])

    assert resultados == ["gravado", acessos.VINCULO_JA_REVOGADO]
    assert RevogacaoDeVinculo.objects.count() == 1


def _institucional():
    from processo_seletivo.seguranca.acessos import ADMINISTRAR, ESCOPO_INSTITUCIONAL

    atores = []
    for nome in ("rita", "rosa"):
        alguem = pessoa(nome)
        atores.append(Actor(alguem.username, ESCOPO_INSTITUCIONAL, frozenset({ADMINISTRAR})))
    return atores


def _barreira_em_suspensao_aberta(monkeypatch):
    from processo_seletivo.seguranca.application import suspensao

    barreira = threading.Barrier(2, timeout=2)
    original = suspensao.suspensao_aberta

    def depois_da_barreira(pessoa_id):
        try:
            barreira.wait()
        except threading.BrokenBarrierError:
            pass
        return original(pessoa_id)

    monkeypatch.setattr(suspensao, "suspensao_aberta", depois_da_barreira)
    return suspensao


def _duas(atos):
    resultados = []

    def executar(ato):
        try:
            ato()
            resultados.append("gravado")
        except DomainError as recusa:
            resultados.append(recusa.code)
        finally:
            connections.close_all()

    linhas = [threading.Thread(target=executar, args=(ato,)) for ato in atos]
    for linha in linhas:
        linha.start()
    for linha in linhas:
        linha.join(timeout=30)
    return sorted(resultados)


def test_duas_suspensoes_simultaneas_gravam_uma(monkeypatch):
    from processo_seletivo.seguranca.models import SuspensaoDePessoa

    primeira, segunda = _institucional()
    ana = pessoa("ana")
    suspensao = _barreira_em_suspensao_aberta(monkeypatch)

    def suspender(ator):
        return lambda: suspensao.suspender(ator, pessoa=ana, motivo="Processo", now=AGORA)

    assert _duas([suspender(primeira), suspender(segunda)]) == ["gravado", suspensao.JA_SUSPENSA]
    assert SuspensaoDePessoa.objects.count() == 1


def test_duas_reativacoes_simultaneas_gravam_uma(monkeypatch):
    from processo_seletivo.seguranca.application import suspensao as servico
    from processo_seletivo.seguranca.models import ReativacaoDePessoa

    primeira, segunda = _institucional()
    ana = pessoa("ana")
    servico.suspender(primeira, pessoa=ana, motivo="Processo", now=AGORA)
    suspensao = _barreira_em_suspensao_aberta(monkeypatch)

    def reativar(ator):
        return lambda: suspensao.reativar(ator, pessoa=ana, motivo="Fim", now=AGORA)

    assert _duas([reativar(primeira), reativar(segunda)]) == ["gravado", suspensao.NAO_SUSPENSA]
    assert ReativacaoDePessoa.objects.count() == 1
