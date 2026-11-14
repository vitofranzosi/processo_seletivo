"""A página "Assistente do Edital", pela entrada institucional (170, contracts/tela.md).

A Administradora institucional entra pelo provedor simulado da `106`, como entraria pelo SSO; a
demonstração e os papéis de unidade são recusados. Os casos percorrem o que só a tela prova: a
configuração dita sem segredo e sem chamar o modelo, a confirmação com a consequência e o motivo, e
a recusa de produção com os doze requisitos.
"""

import pytest
from django.urls import reverse

from processo_seletivo.duvidas.application import habilitacao
from processo_seletivo.duvidas.domain.habilitacao import PAGINA_PUBLICA, PILOTO
from processo_seletivo.duvidas.models import HabilitacaoDoAssistente
from processo_seletivo.seguranca.acessos import (
    ADMINISTRADOR_DE_ACESSOS,
    ADMINISTRADOR_INSTITUCIONAL,
    ESCOPO_INSTITUCIONAL,
)
from tests.fixtures import provedor_simulado
from tests.fixtures.corpus import publicar_do_corpus
from tests.fixtures.inferencia import configuracao_completa  # noqa: F401
from tests.interface.conftest import identificar
from tests.seguranca.apoio import entrar, pessoa, vincular

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

PAGINA = reverse("interface:administracao-do-assistente")
CREDENCIAL = "sk-or-credencial-que-nao-pode-aparecer"


def _piloto(ato):
    return reverse("interface:administracao-do-assistente-piloto", args=[ato])


def _edital(edital, ato):
    return reverse("interface:administracao-do-assistente-edital", args=[edital.id, ato])


@pytest.fixture(autouse=True)
def _sem_atalhos(settings, sem_rede):
    settings.ASSISTENTE_PILOTO = False
    settings.ASSISTENTE_NA_PAGINA_DO_EDITAL = False


@pytest.fixture
def em_producao(monkeypatch):
    """Produção para a regra do assistente só. `AMBIENTE_DE_PRODUCAO` ligado na suíte mudaria
    também a entrada institucional; a leitura da configuração está provada nos testes da aplicação
    (`tests/integration/duvidas/test_habilitacao.py`) e do `production.py`."""
    monkeypatch.setattr(habilitacao, "em_producao", lambda: True)


@pytest.fixture
def provedor(settings):
    provedor_simulado.limpar()
    settings.GESTAO_PROVEDOR_INSTITUCIONAL = provedor_simulado.CAMINHO
    yield provedor_simulado
    provedor_simulado.limpar()


@pytest.fixture
def administradora(client, provedor):
    """A Administradora institucional, com a sessão institucional aberta neste cliente."""
    vincular(
        pessoa("ines", nome="Inês Institucional"), ESCOPO_INSTITUCIONAL, ADMINISTRADOR_INSTITUCIONAL
    )
    assert entrar(client, "ines", nome="Inês Institucional").status_code == 302
    return client


@pytest.fixture
def edital_91(api_client):
    edital, _ = publicar_do_corpus(api_client, "91", chave="administracao91")
    return edital


def _texto(resposta):
    return resposta.content.decode()


# --- Quem chega --------------------------------------------------------------------------------


def test_a_demonstracao_e_recusada_e_nao_ve_o_item(client, settings):
    """FR-7511: o seletor continua, e não alcança a página."""
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    identificar(client, "ana.gestora", ["gestor", "participante-piloto-assistente"])

    barra = _texto(client.get(reverse("interface:lista")))

    assert PAGINA not in barra
    assert client.get(PAGINA).status_code == 403


def test_o_administrador_de_acessos_da_unidade_e_recusado(client, provedor):
    """FR-7511, SC-2454: papel de unidade não vê o item, nem grava por envio montado à mão."""
    vincular(pessoa("bia"), "cefor", ADMINISTRADOR_DE_ACESSOS)
    entrar(client, "bia")

    assert PAGINA not in _texto(client.get(reverse("interface:lista")))
    assert client.get(PAGINA).status_code == 403
    assert client.post(_piloto("habilitar"), {"motivo": "x"}).status_code == 403
    assert not HabilitacaoDoAssistente.objects.exists()


def test_a_administradora_ve_o_item_ao_lado_de_unidades(administradora):
    barra = _texto(administradora.get(PAGINA))

    assert reverse("interface:unidades") in barra
    assert PAGINA in barra


# --- A configuração ------------------------------------------------------------------------------


def test_sem_servico_a_pagina_diz_o_que_falta_e_nao_oferece_habilitar(administradora):
    """FR-7501, FR-7502, UX-810, SC-2450."""
    pagina = _texto(administradora.get(PAGINA))

    assert "Configuração incompleta" in pagina
    assert "O serviço do modelo não está configurado." in pagina
    assert _piloto("habilitar") not in pagina


@pytest.mark.usefixtures("configuracao_completa")
def test_completa_a_pagina_nao_afirma_disponibilidade_e_nao_mostra_a_credencial(
    administradora,
    settings,
    porta_falsa,
):
    """FR-7500, FR-7502, SC-2450: a credencial só como presença, e nenhuma chamada ao serviço."""
    porta = porta_falsa()
    settings.ASSISTENTE_CREDENCIAL = CREDENCIAL

    pagina = _texto(administradora.get(PAGINA))

    assert "Configuração completa." in pagina
    assert "verificar_servico_de_inferencia" in pagina
    assert "presente" in pagina
    assert CREDENCIAL not in pagina
    assert porta.chamadas == []
    assert _piloto("habilitar") in pagina


# --- O piloto ------------------------------------------------------------------------------------


@pytest.mark.usefixtures("configuracao_completa")
def test_habilitar_o_piloto_pela_tela_com_motivo(administradora):  # noqa: F811
    """FR-7514, FR-7528, UX-812: a consequência antes do motivo; sem motivo, recusa sem gravar."""
    confirmacao = _texto(administradora.get(_piloto("habilitar")))
    assert "Participante do piloto passa a ver o assistente" in confirmacao
    assert "sessões acompanhadas" in confirmacao

    sem_motivo = administradora.post(_piloto("habilitar"), {"motivo": "  "})
    assert sem_motivo.status_code == 422
    assert not HabilitacaoDoAssistente.objects.exists()

    feito = administradora.post(_piloto("habilitar"), {"motivo": "Sessão de teste de 14/11"})
    assert feito.status_code == 302
    pagina = _texto(administradora.get(feito.url))
    assert "Assistente habilitado." in pagina
    assert "Inês Institucional" in pagina and "Sessão de teste de 14/11" in pagina
    assert habilitacao.piloto_atende() is True


@pytest.mark.usefixtures("configuracao_completa")
def test_o_estado_mudado_recusa_a_confirmacao(administradora):  # noqa: F811
    """FR-7530, FR-7531: o pedido montado à mão para o que já está habilitado não grava."""
    administradora.post(_piloto("habilitar"), {"motivo": "Primeiro"})

    resposta = administradora.post(_piloto("habilitar"), {"motivo": "Segundo"})

    assert resposta.status_code == 409
    assert "já está habilitado" in _texto(resposta)
    assert HabilitacaoDoAssistente.objects.count() == 1


def test_ato_desconhecido_e_pagina_inexistente(administradora):
    assert administradora.get(_piloto("apagar")).status_code == 404


# --- A página pública ----------------------------------------------------------------------------


@pytest.mark.usefixtures("configuracao_completa")
def test_habilitar_e_desabilitar_um_edital_pela_tela(administradora, edital_91):
    """FR-7517, FR-7520, SC-2451 (passos 2 e 5)."""
    pagina = _texto(administradora.get(PAGINA))
    assert f"{edital_91.number}/{edital_91.year}" in pagina
    assert _edital(edital_91, "habilitar") in pagina
    assert "Qualquer visitante da página pública deste Edital" in _texto(
        administradora.get(_edital(edital_91, "habilitar"))
    )

    administradora.post(_edital(edital_91, "habilitar"), {"motivo": "Teste com visitante"})
    assert habilitacao.pagina_publica_atende(edital_91.id) is True
    assert "Nenhuma pergunta nova chega ao modelo" in _texto(
        administradora.get(_edital(edital_91, "desabilitar"))
    )

    administradora.post(_edital(edital_91, "desabilitar"), {"motivo": "Fim do teste"})
    assert habilitacao.pagina_publica_atende(edital_91.id) is False
    historico = list(
        HabilitacaoDoAssistente.objects.filter(frente=PAGINA_PUBLICA).values_list(
            "habilitada", flat=True
        )
    )
    assert sorted(historico) == [False, True]


@pytest.mark.usefixtures("configuracao_completa")
def test_em_producao_a_tela_recusa_nomeando_os_requisitos(administradora, edital_91, em_producao):
    """FR-7518, UX-811, SC-2453: a página não oferece, e a confirmação lista RA-1 a RA-12."""
    pagina = _texto(administradora.get(PAGINA))
    assert _edital(edital_91, "habilitar") not in pagina
    assert "Em produção, a página pública não abre" in pagina

    resposta = administradora.post(_edital(edital_91, "habilitar"), {"motivo": "x"})
    assert resposta.status_code == 409
    for numero in range(1, 13):
        assert f"<strong>RA-{numero}</strong>" in _texto(resposta)
    assert "Confirmar a habilitação" not in _texto(resposta)
    assert not HabilitacaoDoAssistente.objects.exists()


@pytest.mark.usefixtures("configuracao_completa")
def test_o_piloto_se_habilita_pela_tela_tambem_em_producao(administradora, em_producao):
    """Q-1: em produção, só a página pública fecha; o piloto continua habilitável."""
    assert administradora.post(_piloto("habilitar"), {"motivo": "Sessão"}).status_code == 302
    assert HabilitacaoDoAssistente.objects.get().frente == PILOTO
