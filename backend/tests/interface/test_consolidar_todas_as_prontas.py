"""Consolidar todas as prontas da Etapa numa confirmação só — e não página a página.

A seleção da listagem é da página, e a página é de 25: com 600 prontas eram 24 atos da presidência
para uma decisão só. A 013 pede o lote confirmado (FR-018) e um envio "sem interação por inscrição"
(SC-002); a página não protegia nada que a conferência não declarasse. O que estes testes fixam é
que o alcance do ato deixou de ser a página, e que nada do que o ato garantia se perdeu no caminho:
a conferência antes, a mesma chave devolvendo o desfecho original, um evento por Resultado, e o
conjunto confirmado sendo o que a tela declarou.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.resultados.application.consolidacao import CONSOLIDAR, NADA_PRONTO
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.resultado import montar_etapa_de_leitura_unica, semear_prontas
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]

PRONTAS = 30  # mais que uma página de 25, para que a página exista e o ato a atravesse


@pytest.fixture
def etapa(gestor, api_client, manager_headers):
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1710, codigo="1710"
    )
    cenario["prontas"] = semear_prontas(cenario, PRONTAS, primeiro=1)
    # Cinco sem avaliação: participam da Etapa e não estão prontas.
    cenario["pendentes"] = inscrever(cenario["edital"], 5, primeiro=100)
    return cenario


def _organizacao(cenario):
    return reverse("interface:distribuicao", args=[cenario["edital"].id, cenario["primeira"]])


def _consolidar(cenario):
    return reverse(
        "interface:consolidar-resultados", args=[cenario["edital"].id, cenario["primeira"]]
    )


def _conferir(client, cenario, chave="todas-1710"):
    return client.post(_consolidar(cenario), {"alcance": "prontas", "chave_idempotencia": chave})


def _declaradas(corpo):
    campo = re.search(r'name="inscricoes" value="([^"]*)"', corpo)
    assert campo, "a confirmação não devolve o conjunto que declarou"
    return campo.group(1).split()


def test_a_tela_oferece_consolidar_todas_as_prontas_com_o_numero(client, seletor_ligado, etapa):
    identificar(client, "maria", ["gestor"])
    corpo = client.get(_organizacao(etapa)).content.decode()

    assert f"Consolidar as {PRONTAS} prontas" in corpo
    assert 'name="alcance" value="prontas"' in corpo


def test_sem_pronta_nenhuma_o_botao_nao_aparece(
    client, seletor_ligado, gestor, api_client, manager_headers
):
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1711, codigo="1711"
    )
    inscrever(cenario["edital"], 3, primeiro=1)
    identificar(client, "maria", ["gestor"])

    corpo = client.get(_organizacao(cenario)).content.decode()

    assert 'name="alcance" value="prontas"' not in corpo


def test_a_conferencia_declara_todas_as_prontas_e_nao_a_pagina(client, seletor_ligado, etapa):
    identificar(client, "maria", ["gestor"])
    resposta = _conferir(client, etapa)

    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert "Confira antes de consolidar" in corpo
    assert f"O que será consolidado — {PRONTAS} inscrições" in corpo
    assert f"{PRONTAS} habilitadas" in corpo
    assert "não só as da página" in " ".join(corpo.split())
    for inscricao in etapa["prontas"]:
        assert inscricao.protocolo in corpo
    for inscricao in etapa["pendentes"]:
        assert inscricao.protocolo not in corpo, "quem não está pronto não entra no alcance"
    assert sorted(_declaradas(corpo)) == sorted(str(i.id) for i in etapa["prontas"])
    # Um campo só, e não um por inscrição: é o que deixa a confirmação passar de mil.
    assert 'name="inscricao_id"' not in corpo
    assert ResultadoEtapa.objects.count() == 0, "conferir não pratica o ato"


def test_uma_confirmacao_consolida_todas_as_prontas(client, seletor_ligado, etapa):
    identificar(client, "maria", ["gestor"])
    corpo = _conferir(client, etapa).content.decode()

    resposta = client.post(
        _consolidar(etapa),
        {
            "confirmar": "1",
            "chave_idempotencia": "todas-1710",
            "inscricoes": " ".join(_declaradas(corpo)),
        },
    )

    assert resposta.status_code == 302
    criados = ResultadoEtapa.objects.filter(edital=etapa["edital"])
    assert criados.count() == PRONTAS
    # A autoria e o instante são os de um ato só (013, FR-025; 015).
    assert set(criados.values_list("consolidado_por", flat=True)) == {"maria"}
    assert criados.values_list("consolidado_em", flat=True).distinct().count() == 1
    # Um evento por Resultado, como no lote de sempre (FR-021).
    assert RegistroAuditoria.objects.filter(operation=CONSOLIDAR).count() == PRONTAS
    destino = client.get(resposta["Location"]).content.decode()
    assert f"<strong>{PRONTAS}</strong> consolidadas" in destino


def test_repetir_a_confirmacao_devolve_o_desfecho_original(client, seletor_ligado, etapa):
    identificar(client, "maria", ["gestor"])
    envio = {
        "confirmar": "1",
        "chave_idempotencia": "todas-1710",
        "inscricoes": " ".join(_declaradas(_conferir(client, etapa).content.decode())),
    }
    client.post(_consolidar(etapa), envio)
    eventos = RegistroAuditoria.objects.filter(operation=CONSOLIDAR).count()

    resposta = client.post(_consolidar(etapa), envio)

    assert ResultadoEtapa.objects.filter(edital=etapa["edital"]).count() == PRONTAS
    assert RegistroAuditoria.objects.filter(operation=CONSOLIDAR).count() == eventos
    destino = client.get(resposta["Location"]).content.decode()
    # O desfecho original, e não "zero consolidadas" sobre um estado que já mudou (FR-020).
    assert f"<strong>{PRONTAS}</strong> consolidadas" in destino


def test_o_ato_consolida_o_conjunto_declarado_e_nao_o_do_instante(
    client, seletor_ligado, etapa, gestor
):
    """Quem ficou pronto entre a conferência e a confirmação não entra sem ser visto."""
    identificar(client, "maria", ["gestor"])
    declaradas = _declaradas(_conferir(client, etapa).content.decode())
    tardia = etapa["pendentes"][0]
    distribuir_para(etapa, gestor, ["joao"], [tardia], chave="tardia-1710")
    concluir_como(etapa, "joao", tardia, pontuacao="75")

    client.post(
        _consolidar(etapa),
        {"confirmar": "1", "chave_idempotencia": "todas-1710", "inscricoes": " ".join(declaradas)},
    )

    assert ResultadoEtapa.objects.filter(edital=etapa["edital"]).count() == PRONTAS
    assert not ResultadoEtapa.objects.filter(inscricao=tardia).exists()


def test_sem_pronta_nenhuma_a_conferencia_volta_com_a_frase(
    client, seletor_ligado, gestor, api_client, manager_headers
):
    cenario = montar_etapa_de_leitura_unica(
        gestor, api_client, manager_headers, seed=1712, codigo="1712"
    )
    inscrever(cenario["edital"], 3, primeiro=1)
    identificar(client, "maria", ["gestor"])

    resposta = _conferir(client, cenario)

    assert resposta.status_code == 302
    assert NADA_PRONTO in client.get(resposta["Location"]).content.decode()
