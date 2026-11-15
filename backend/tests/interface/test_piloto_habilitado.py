"""O piloto da gestão ligado pelo ato, sem o atalho `ASSISTENTE_PILOTO` (170).

Prende o lado da gestão do percurso:
- sem ato, a negativa de sempre; com ato, quem tem o papel conversa (FR-7508, FR-7515);
- desabilitado, a pergunta seguinte recebe a negativa e não chega ao modelo (FR-7524);
- habilitado de novo, conversa nova (FR-7525);
- a página do Edital diz se a página pública dele está aberta ao assistente (FR-7522).
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.duvidas.application import habilitacao
from processo_seletivo.duvidas.domain.habilitacao import HABILITAR, PAGINA_PUBLICA, PILOTO
from processo_seletivo.seguranca.acessos import ESCOPO_INSTITUCIONAL
from processo_seletivo.seguranca.domain import Actor
from tests.fixtures.corpus import publicar_do_corpus
from tests.fixtures.inferencia import configuracao_completa, devolucao, saida  # noqa: F401
from tests.fixtures.inferencia_corpus import fonte
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

PARTICIPANTE = ["gestor", "participante-piloto-assistente"]
ADMINISTRADORA = Actor("pessoa-administradora", ESCOPO_INSTITUCIONAL, frozenset({HABILITAR}))


@pytest.fixture(autouse=True)
def _ambiente(seletor_ligado, sem_rede, settings, configuracao_completa):  # noqa: F811
    """O seletor, nenhuma rede, e nenhum atalho: o percurso é o da interface (FR-7508)."""
    settings.ASSISTENTE_PILOTO = False
    settings.ASSISTENTE_NA_PAGINA_DO_EDITAL = False


@pytest.fixture
def edital_91(api_client):
    edital, _ = publicar_do_corpus(api_client, "91", chave="pilotohabilitado91")
    return edital


def _url(edital):
    return reverse("interface:assistente", args=[edital.id])


def _texto(resposta):
    return re.sub(r"\s+", " ", resposta.content.decode())


def _vagas(mensagens):
    total = fonte(mensagens, lugar="INF-BJN", rotulo="Vagas imediatas")
    return devolucao(saida("RESPONDIDA", ("dado", "São 45 vagas.", [total["id"]])))


def test_sem_ato_a_negativa_e_com_ato_quem_tem_o_papel_conversa(
    client, edital_91, porta_falsa, contador_falso
):
    """FR-7508, FR-7515, SC-2451 (passo 3)."""
    contador_falso()
    porta = porta_falsa(_vagas)
    identificar(client, "pessoa", PARTICIPANTE)
    assert client.get(_url(edital_91)).status_code == 404

    habilitacao.habilitar(ADMINISTRADORA, frente=PILOTO, motivo="Sessão acompanhada")

    detalhe = _texto(client.get(reverse("interface:detalhe", args=[edital_91.id])))
    assert "Conversar com o assistente (piloto)" in detalhe
    assert client.post(_url(edital_91), {"pergunta": "Quantas vagas?"}).status_code == 302
    assert len(porta.chamadas) == 1


def test_desabilitado_a_pergunta_seguinte_recebe_a_negativa(
    client, edital_91, porta_falsa, contador_falso
):
    """FR-7524: a negativa da FR-1464 da 071, e nada chega ao modelo."""
    contador_falso()
    porta = porta_falsa(_vagas)
    identificar(client, "pessoa", PARTICIPANTE)
    habilitacao.habilitar(ADMINISTRADORA, frente=PILOTO, motivo="Abrir")
    client.post(_url(edital_91), {"pergunta": "Quantas vagas?"})
    habilitacao.desabilitar(ADMINISTRADORA, frente=PILOTO, motivo="Fechar")

    assert client.post(_url(edital_91), {"pergunta": "E as reservadas?"}).status_code == 404
    detalhe = _texto(client.get(reverse("interface:detalhe", args=[edital_91.id])))
    assert "Conversar com o assistente (piloto)" not in detalhe
    assert len(porta.chamadas) == 1


def test_habilitado_de_novo_a_conversa_recomeca(client, edital_91, porta_falsa, contador_falso):
    """FR-7525: o histórico de antes da desabilitação não volta ao modelo."""
    contador_falso()
    porta = porta_falsa(_vagas, _vagas)
    identificar(client, "pessoa", PARTICIPANTE)
    habilitacao.habilitar(ADMINISTRADORA, frente=PILOTO, motivo="Abrir")
    client.post(_url(edital_91), {"pergunta": "Quantas vagas?"})
    habilitacao.desabilitar(ADMINISTRADORA, frente=PILOTO, motivo="Fechar")
    habilitacao.habilitar(ADMINISTRADORA, frente=PILOTO, motivo="Abrir de novo")

    client.post(_url(edital_91), {"pergunta": "E as reservadas?"})

    segunda = porta.chamadas[1]["mensagens"]
    assert not any(m["content"] == "Quantas vagas?" for m in segunda)


def test_a_pagina_do_edital_diz_se_a_pagina_publica_esta_aberta(client, edital_91, settings):
    """FR-7522, UX-814; e, em produção, a linha não aparece (FR-7519)."""
    identificar(client, "pessoa", ["gestor"])
    detalhe = reverse("interface:detalhe", args=[edital_91.id])
    assert "Assistente na página pública: não aberto." in _texto(client.get(detalhe))

    habilitacao.habilitar(
        ADMINISTRADORA, frente=PAGINA_PUBLICA, edital_id=edital_91.id, motivo="Teste"
    )
    assert "Assistente na página pública: <strong>aberto</strong> desde" in _texto(
        client.get(detalhe)
    )

    settings.AMBIENTE_DE_PRODUCAO = True
    assert "Assistente na página pública" not in _texto(client.get(detalhe))
