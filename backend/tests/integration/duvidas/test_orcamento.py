"""O orçamento de contexto, sem corte silencioso (071, US5, `FR-1479` a `FR-1483`, `SC-547`).

A contagem é substituída por uma regra fixa — uma base e um tanto por par do histórico —, para que
cada cenário caia exatamente onde o caso quer. Em todos, nenhuma fonte é cortada: o número de fontes
nas mensagens é sempre o de `fontes_completas`.
"""

import uuid

import pytest
from django.utils import timezone

from processo_seletivo.duvidas.application.consultar import contexto
from processo_seletivo.duvidas.application.perguntar import perguntar
from processo_seletivo.duvidas.domain.estruturas_do_piloto import (
    EXCEDE_O_CONTEXTO,
    INCOMPLETA,
    POSSIVEL_CORTE,
    RESPONDIDA_E_CONFERIDA,
    TELA,
)
from processo_seletivo.duvidas.domain.fontes import fontes_completas
from processo_seletivo.duvidas.infrastructure import tokens
from tests.fixtures.corpus import publicar_do_corpus
from tests.fixtures.inferencia import devolucao, saida
from tests.fixtures.inferencia_corpus import fonte, fontes_recebidas

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

BASE, POR_PAR = 1000, 500


@pytest.fixture
def edital_91(api_client):
    edital, _ = publicar_do_corpus(api_client, "91", chave="orcamento91")
    return edital


@pytest.fixture
def contagem_fixa(monkeypatch, settings):
    """`BASE` mais `POR_PAR` por resposta do histórico; o orçamento cabe `pares` pares."""

    def configurar(pares):
        def contar(mensagens):
            return BASE + POR_PAR * sum(1 for m in mensagens if m["role"] == "assistant")

        monkeypatch.setattr(tokens, "contar", contar)
        settings.ASSISTENTE_SAIDA_MAXIMA_TOKENS = 0
        # O orçamento é o contexto menos a margem de 5%: este contexto deixa caber `pares` pares.
        alvo = BASE + POR_PAR * pares + 1
        settings.ASSISTENTE_CONTEXTO_TOKENS = int(alvo / 0.95) + 1

    return configurar


def _vagas(mensagens, *, tokens_de_entrada=None, termino="stop"):
    total = fonte(mensagens, lugar="INF-BJN", rotulo="Vagas imediatas")
    return devolucao(
        saida("RESPONDIDA", ("dado", "São 45 vagas.", [total["id"]])),
        tokens_de_entrada=tokens_de_entrada,
        termino=termino,
    )


def _perguntar(edital, conversa, texto="Quantas vagas tem o polo de BJN?"):
    return perguntar(
        edital_id=edital.id,
        conversa=conversa,
        pergunta=texto,
        instante=timezone.now(),
        origem=TELA,
    )


def _todas_as_fontes(edital, mensagens):
    esperadas = fontes_completas(contexto(edital_id=edital.id, instante=timezone.now()))
    return len(fontes_recebidas(mensagens)) == len(esperadas)


def test_o_historico_mais_antigo_sai_primeiro(edital_91, porta_falsa, contagem_fixa):
    contagem_fixa(pares=1)
    porta = porta_falsa(_vagas, _vagas, _vagas)
    conversa = str(uuid.uuid4())

    _perguntar(edital_91, conversa)
    segunda = _perguntar(edital_91, conversa)
    terceira = _perguntar(edital_91, conversa)

    enviadas = porta.chamadas[2]["mensagens"]
    assert [m["role"] for m in enviadas].count("assistant") == 1
    assert terceira.historico_desde == segunda.ordem
    assert terceira.estado == RESPONDIDA_E_CONFERIDA
    assert _todas_as_fontes(edital_91, enviadas)


def test_sem_caber_nem_sem_historico_nao_ha_chamada(
    edital_91, porta_falsa, contagem_fixa, settings
):
    contagem_fixa(pares=0)
    settings.ASSISTENTE_CONTEXTO_TOKENS = 500
    porta = porta_falsa()

    troca = _perguntar(edital_91, str(uuid.uuid4()))

    assert troca.estado == EXCEDE_O_CONTEXTO
    assert troca.chamou_o_servico is False
    assert porta.chamadas == []


def test_o_servico_que_leu_menos_acusa_corte(edital_91, porta_falsa, contagem_fixa):
    contagem_fixa(pares=1)
    porta = porta_falsa(lambda m: _vagas(m, tokens_de_entrada=BASE // 2))

    troca = _perguntar(edital_91, str(uuid.uuid4()))

    assert troca.estado == POSSIVEL_CORTE
    assert not troca.trechos
    assert _todas_as_fontes(edital_91, porta.chamadas[0]["mensagens"])


def test_dentro_da_tolerancia_nao_acusa(edital_91, porta_falsa, contagem_fixa):
    contagem_fixa(pares=1)
    porta_falsa(lambda m: _vagas(m, tokens_de_entrada=int(BASE * 0.99)))

    assert _perguntar(edital_91, str(uuid.uuid4())).estado == RESPONDIDA_E_CONFERIDA


def test_ler_mais_que_o_medido_nao_descarta(edital_91, porta_falsa, contagem_fixa):
    """Acima do medido é acréscimo por mensagem subestimado: vai ao log, e a resposta segue."""
    contagem_fixa(pares=1)
    porta_falsa(lambda m: _vagas(m, tokens_de_entrada=BASE * 2))

    assert _perguntar(edital_91, str(uuid.uuid4())).estado == RESPONDIDA_E_CONFERIDA


def test_a_resposta_encerrada_por_limite_e_incompleta(edital_91, porta_falsa, contagem_fixa):
    contagem_fixa(pares=1)
    porta_falsa(lambda m: _vagas(m, termino="length"))

    troca = _perguntar(edital_91, str(uuid.uuid4()))

    assert troca.estado == INCOMPLETA
    assert not troca.trechos
