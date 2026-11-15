"""A página pública aberta pelo ato, sem a chave da `074` (170).

Prende o percurso do visitante sem login, com as duas chaves de demonstração desligadas:
- o Edital habilitado oferece o painel, e o outro não (FR-7508, FR-7520);
- desabilitado no meio da conversa, a pergunta seguinte recebe o aviso e não chega ao modelo
  (FR-7524, UX-813);
- habilitado de novo, a conversa recomeça sem o histórico de antes (FR-7525, SC-2456);
- em produção, nem o ato gravado abre o painel (FR-7519, SC-2453).
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.duvidas.application import habilitacao
from processo_seletivo.duvidas.domain.habilitacao import HABILITAR, PAGINA_PUBLICA
from processo_seletivo.duvidas.models import TrocaDoPiloto
from processo_seletivo.seguranca.acessos import ESCOPO_INSTITUCIONAL
from processo_seletivo.seguranca.domain import Actor
from tests.fixtures.corpus import publicar_do_corpus
from tests.fixtures.inferencia import configuracao_completa, devolucao, saida  # noqa: F401
from tests.fixtures.inferencia_corpus import fonte

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ADMINISTRADORA = Actor("pessoa-administradora", ESCOPO_INSTITUCIONAL, frozenset({HABILITAR}))
ENVIOS = ("perguntar", "sugestao", "nova")


@pytest.fixture(autouse=True)
def _ambiente(sem_rede, settings, configuracao_completa):  # noqa: F811
    """Nenhum caso alcança a rede, e nenhum atalho está ligado: o percurso é o da interface."""
    settings.ASSISTENTE_PILOTO = False
    settings.ASSISTENTE_NA_PAGINA_DO_EDITAL = False


@pytest.fixture
def edital_91(api_client):
    edital, _ = publicar_do_corpus(api_client, "91", chave="habilitado91")
    return edital


@pytest.fixture
def edital_92(api_client):
    edital, _ = publicar_do_corpus(api_client, "92", chave="habilitado92")
    return edital


def _abrir(edital, motivo="Teste"):
    habilitacao.habilitar(ADMINISTRADORA, frente=PAGINA_PUBLICA, edital_id=edital.id, motivo=motivo)


def _fechar(edital, motivo="Fim do teste"):
    habilitacao.desabilitar(
        ADMINISTRADORA, frente=PAGINA_PUBLICA, edital_id=edital.id, motivo=motivo
    )


def _pagina(edital):
    return reverse("portal:selecao", args=[edital.id])


def _envio(edital, nome):
    return reverse(f"portal:assistente-{nome}", args=[edital.id])


def _painel(resposta):
    corpo = re.sub(r"\s+", " ", resposta.content.decode())
    encontrado = re.search(r'<dialog id="pd-painel".*?</dialog>', corpo)
    return encontrado.group(0) if encontrado else ""


def _vagas(mensagens):
    total = fonte(mensagens, lugar="INF-BJN", rotulo="Vagas imediatas")
    return devolucao(saida("RESPONDIDA", ("dado", "São 45 vagas.", [total["id"]])))


def test_o_edital_habilitado_oferece_o_painel_e_o_outro_nao(
    client, edital_91, edital_92, porta_falsa, contador_falso
):
    """FR-7508, FR-7520, SC-2451 (passo 4): o visitante sem login conversa no 91, e o 92 continua
    sem o assistente, com as rotas dele respondendo 404."""
    contador_falso()
    porta = porta_falsa(_vagas)
    _abrir(edital_91)

    assert _painel(client.get(_pagina(edital_91) + "?painel=1"))
    resposta = client.post(_envio(edital_91, "perguntar"), {"pergunta": "Quantas vagas?"})
    assert resposta.status_code == 302
    assert len(porta.chamadas) == 1
    assert "São 45 vagas." in _painel(client.get(_pagina(edital_91) + "?painel=1"))

    assert "pd-painel" not in client.get(_pagina(edital_92) + "?painel=1").content.decode()
    for nome in ENVIOS:
        assert client.post(_envio(edital_92, nome), {"pergunta": "x"}).status_code == 404
    assert len(porta.chamadas) == 1


def test_desabilitado_no_meio_da_conversa_a_pergunta_seguinte_nao_chega_ao_modelo(
    client, edital_91, porta_falsa, contador_falso
):
    """FR-7524, UX-813, SC-2451 (passo 5): o aviso de encerrado, e nenhuma chamada."""
    contador_falso()
    porta = porta_falsa(_vagas)
    _abrir(edital_91)
    client.post(_envio(edital_91, "perguntar"), {"pergunta": "Quantas vagas?"})
    _fechar(edital_91)

    resposta = client.post(_envio(edital_91, "perguntar"), {"pergunta": "E as reservadas?"})

    assert resposta.status_code == 302
    assert resposta.url == _pagina(edital_91) + "?assistente=encerrado"
    pagina = client.get(resposta.url).content.decode()
    assert "O assistente desta seleção foi encerrado." in pagina
    assert "pd-painel" not in pagina
    assert len(porta.chamadas) == 1
    assert TrocaDoPiloto.objects.count() == 1


def test_quem_nunca_conversou_recebe_404_e_o_aviso_forjado_nao_aparece_com_o_painel(
    client, edital_91
):
    """R-9: sem conversa na sessão, a rota não se revela; e o parâmetro forjado não mente."""
    assert client.post(_envio(edital_91, "perguntar"), {"pergunta": "x"}).status_code == 404

    _abrir(edital_91)
    pagina = client.get(_pagina(edital_91) + "?assistente=encerrado").content.decode()
    assert "foi encerrado" not in pagina


def test_habilitado_de_novo_a_conversa_recomeca_sem_o_historico(
    client, edital_91, porta_falsa, contador_falso
):
    """FR-7525, SC-2456: a primeira chamada depois de reabilitar leva zero trocas anteriores."""
    contador_falso()
    porta = porta_falsa(_vagas, _vagas)
    _abrir(edital_91)
    client.post(_envio(edital_91, "perguntar"), {"pergunta": "Quantas vagas?"})
    _fechar(edital_91)
    _abrir(edital_91, motivo="Outra sessão de teste")

    client.post(_envio(edital_91, "perguntar"), {"pergunta": "E as reservadas?"})

    primeira, segunda = (chamada["mensagens"] for chamada in porta.chamadas)
    assert any(m["content"] == "Quantas vagas?" for m in primeira)
    assert not any(m["content"] == "Quantas vagas?" for m in segunda)
    assert segunda[-1]["content"] == "E as reservadas?"
    assert TrocaDoPiloto.objects.values("conversa").distinct().count() == 2


def test_em_producao_o_ato_gravado_nao_abre_a_pagina(client, edital_91, porta_falsa, settings):
    """FR-7519, SC-2453: o banco de testes levado à produção, com uma conversa em curso."""
    porta = porta_falsa()
    _abrir(edital_91)
    client.post(_envio(edital_91, "sugestao"), {"sugestao": "P-05", "perfil": "INF-BJN"})
    settings.AMBIENTE_DE_PRODUCAO = True

    assert "pd-painel" not in client.get(_pagina(edital_91) + "?painel=1").content.decode()
    for nome in ENVIOS:
        assert client.post(_envio(edital_91, nome), {"pergunta": "x"}).status_code == 404
    assert porta.chamadas == []
