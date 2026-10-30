"""A sessão institucional tem prazo: duração máxima e inatividade (107, US5).

O relógio é o de `seguranca.relogio`, fixado pelo caso: os limites se verificam no instante exato,
sem `sleep`. Os valores são os padrões fora de produção — 8 horas e 30 minutos, os que o usuário
decidiu em 30/10 (P4 da spec).
"""

from datetime import timedelta

import pytest
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.interface import identidade
from processo_seletivo.seguranca import relogio
from tests.interface.conftest import identificar
from tests.seguranca.apoio import AGORA, entrar, pessoa, vincular

pytestmark = pytest.mark.django_db

LISTA = reverse("interface:lista")


class Relogio:
    def __init__(self):
        self.instante = AGORA

    def avancar(self, **duracao):
        self.instante += timedelta(**duracao)

    def __call__(self):
        return self.instante


@pytest.fixture
def agora(monkeypatch):
    marcador = Relogio()
    monkeypatch.setattr(relogio, "agora", marcador)
    return marcador


@pytest.fixture
def ana(client, provedor, agora):
    alguem = pessoa("ana", nome="Ana")
    vincular(alguem, "cefor", "elaborador")
    entrar(client, "ana", nome="Ana")
    return alguem


def _vale(client):
    return client.get(LISTA).status_code == 200


def test_a_sessao_vale_ate_o_limite_de_inatividade_e_cai_nele(client, ana, agora):
    agora.avancar(minutes=29, seconds=59)
    assert _vale(client)

    agora.avancar(minutes=29, seconds=59)
    assert _vale(client), "a ação anterior renovou a atividade"

    agora.avancar(minutes=30)
    resposta = client.get(LISTA)
    assert resposta.status_code == 302
    assert resposta["Location"].startswith(reverse("interface:identificar"))


def test_o_termino_por_inatividade_vai_a_trilha_e_a_pagina_de_acesso_diz_por_que(
    client, ana, agora
):
    agora.avancar(minutes=31)
    client.get(LISTA)

    saida = RegistroAuditoria.objects.get(operation="SAIDA")
    assert saida.actor_subject == ana.username
    assert saida.detalhe["motivo"] == identidade.INATIVIDADE
    pagina = client.get(reverse("interface:identificar")).content.decode()
    assert "Sua sessão terminou por inatividade" in pagina
    assert (
        "Sua sessão terminou por inatividade"
        not in client.get(reverse("interface:identificar")).content.decode()
    ), "o aviso é dito uma vez"


def test_a_atividade_constante_nao_passa_da_duracao_maxima(client, ana, agora):
    for _ in range(23):
        agora.avancar(minutes=20)
        assert _vale(client)
    # 23 × 20 min = 7 h 40 min; mais 20 chega às 8 h exatas, e no limite já não vale.
    agora.avancar(minutes=20)
    assert not _vale(client)
    assert RegistroAuditoria.objects.get(operation="SAIDA").detalhe["motivo"] == (
        identidade.DURACAO_MAXIMA
    )
    pagina = client.get(reverse("interface:identificar")).content.decode()
    assert "atingiu a duração máxima" in pagina


def test_a_troca_de_unidade_nao_renova_a_duracao(client, provedor, agora, campus_a):
    alguem = pessoa("ana", nome="Ana")
    vincular(alguem, "cefor", "elaborador")
    vincular(alguem, "campus-a", "elaborador")
    entrar(client, "ana", nome="Ana")
    for _ in range(23):
        agora.avancar(minutes=20)
        client.post(reverse("interface:unidade-ativa"), {"unidade": "cefor"})
    agora.avancar(minutes=20)

    assert not _vale(client)


def test_a_requisicao_automatica_nao_conta_como_atividade(client, ana, agora):
    agora.avancar(minutes=20)
    assert client.get(LISTA, headers={identidade.CABECALHO_AUTOMATICA: "1"}).status_code == 200
    agora.avancar(minutes=10)

    assert not _vale(client), "a automática valeu, mas não renovou: 30 min desde a entrada"


def test_requisicao_fora_da_gestao_nao_conta_como_atividade(client, ana, agora):
    agora.avancar(minutes=20)
    client.get(reverse("portal:inscricoes"))
    agora.avancar(minutes=10)

    assert not _vale(client)


def test_sessao_sem_os_instantes_vence(client, ana):
    sessao = client.session
    del sessao[identidade.CHAVE_PRAZO]
    sessao.save()

    assert not _vale(client)


def test_os_limites_vem_da_configuracao(client, ana, agora, settings):
    settings.GESTAO_SESSAO_INATIVIDADE_MINUTOS = 5
    agora.avancar(minutes=4, seconds=59)
    assert _vale(client)
    agora.avancar(minutes=5)

    assert not _vale(client)


def test_a_demonstracao_nao_tem_prazo(client, seletor_ligado, agora):
    identificar(client, "gustavo.gestor", ["gestor"])
    agora.avancar(hours=9)

    assert _vale(client)


def test_o_portal_do_candidato_nao_e_alcancado(client, agora):
    """Sem sessão institucional, o prazo não lê nem apaga a identidade do portal (`FR-3126`).

    No mesmo navegador **com** sessão institucional, o término dela apaga a sessão inteira, e com
    ela a do portal — o `logout()` do framework. Está registrado na spec, em §Achados.
    """
    from processo_seletivo.portal.identidade import CHAVE_SESSAO as CHAVE_DO_PORTAL

    sessao = client.session
    sessao[CHAVE_DO_PORTAL] = "registro-do-candidato"
    sessao.save()
    agora.avancar(hours=9)
    client.get(LISTA)

    assert client.session.get(CHAVE_DO_PORTAL) == "registro-do-candidato"
