"""As falhas do serviço, o teto global e o limite da conversa (071, US4).

Em todo cenário, no máximo uma chamada por pergunta, e nenhuma quando a recusa vem antes
(`FR-1501`, `FR-1505` a `FR-1507`, `SC-548`). O gasto no serviço externo é limitado pela credencial,
e não pela aplicação (`FR-1507`, emendado em 14/10): o 402 dele é o `ORCAMENTO_ESGOTADO`. O teto
se prova com as duas vagas presas por outra conexão, como dois processos do servidor estariam —
por isso o caso é transacional.
"""

import threading
import uuid

import pytest
from django.db import connection
from django.utils import timezone

from processo_seletivo.duvidas.application import limites
from processo_seletivo.duvidas.application.perguntar import perguntar
from processo_seletivo.duvidas.domain.estruturas_do_piloto import (
    AVALIACAO,
    INDISPONIVEL,
    LIMITE_DE_USO,
    LIMITE_DO_SERVICO,
    MODELO_DIFERENTE,
    ORCAMENTO_ESGOTADO,
    PERGUNTA_RECUSADA,
    RESPONDIDA_E_CONFERIDA,
    RESPOSTA_MALFORMADA,
    TELA,
    TEMPO_ESGOTADO,
)
from processo_seletivo.duvidas.infrastructure.inferencia import NAO_CONFIGURADO, FalhaDoServico
from tests.fixtures.corpus import publicar_do_corpus
from tests.fixtures.inferencia import devolucao, saida
from tests.fixtures.inferencia_corpus import fonte

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def edital_91(api_client):
    edital, _ = publicar_do_corpus(api_client, "91", chave="teto91")
    return edital


@pytest.fixture
def externo(settings):
    """O OpenRouter configurado, por cima do serviço que a porta falsa ligou."""

    def configurar():
        settings.ASSISTENTE_SERVICO = "openrouter"

    return configurar


def _vagas(mensagens):
    total = fonte(mensagens, lugar="INF-BJN", rotulo="Vagas imediatas")
    return devolucao(saida("RESPONDIDA", ("dado", "São 45 vagas.", [total["id"]])))


def _perguntar(edital, *, conversa=None, texto="Quantas vagas tem o polo de BJN?", origem=TELA):
    return perguntar(
        edital_id=edital.id,
        conversa=conversa or str(uuid.uuid4()),
        pergunta=texto,
        instante=timezone.now(),
        origem=origem,
    )


@pytest.mark.parametrize(
    ("codigo", "estado"),
    [
        (INDISPONIVEL, INDISPONIVEL),
        (TEMPO_ESGOTADO, TEMPO_ESGOTADO),
        (LIMITE_DO_SERVICO, LIMITE_DO_SERVICO),
        (ORCAMENTO_ESGOTADO, ORCAMENTO_ESGOTADO),
        (RESPOSTA_MALFORMADA, RESPOSTA_MALFORMADA),
        (NAO_CONFIGURADO, INDISPONIVEL),
    ],
)
def test_cada_falha_e_um_estado_e_uma_chamada(
    edital_91, porta_falsa, contador_falso, codigo, estado
):
    contador_falso()
    porta = porta_falsa(FalhaDoServico(codigo, "motivo"))

    troca = _perguntar(edital_91)

    assert troca.estado == estado
    assert troca.chamou_o_servico is True
    assert len(porta.chamadas) == 1
    assert not troca.trechos


def test_outro_modelo_respondeu(edital_91, porta_falsa, contador_falso):
    """`FR-1499`: descartada como falha de integração, com o modelo que respondeu gravado."""
    contador_falso()

    def responder(mensagens):
        return devolucao(_vagas(mensagens).texto, modelo="provedor/outro-modelo")

    porta_falsa(responder)
    troca = _perguntar(edital_91)

    assert troca.estado == MODELO_DIFERENTE
    assert troca.modelo_que_respondeu == "provedor/outro-modelo"
    assert not troca.trechos


def test_sem_vaga_no_teto_nao_ha_chamada(edital_91, porta_falsa, contador_falso, settings):
    """As duas vagas presas por outra conexão: a terceira pergunta é recusada, sem fila."""
    contador_falso()
    settings.ASSISTENTE_TETO_SIMULTANEO = 2
    porta = porta_falsa()
    presas, soltar = threading.Event(), threading.Event()

    def ocupar():
        with connection.cursor() as cursor:
            for indice in range(2):
                cursor.execute("SELECT pg_advisory_lock(%s)", [limites._chave_da_vaga(indice)])
        presas.set()
        soltar.wait(10)
        connection.close()

    linha = threading.Thread(target=ocupar)
    linha.start()
    try:
        assert presas.wait(10)
        troca = _perguntar(edital_91)
    finally:
        soltar.set()
        linha.join()

    assert troca.estado == LIMITE_DE_USO
    assert troca.chamou_o_servico is False
    assert porta.chamadas == []


def test_a_vaga_e_solta_depois_da_chamada(edital_91, porta_falsa, contador_falso, settings):
    contador_falso()
    settings.ASSISTENTE_TETO_SIMULTANEO = 1
    porta_falsa(_vagas, _vagas)

    assert _perguntar(edital_91).estado == RESPONDIDA_E_CONFERIDA
    assert _perguntar(edital_91).estado == RESPONDIDA_E_CONFERIDA


def test_o_limite_da_conversa(edital_91, porta_falsa, contador_falso, settings):
    contador_falso()
    settings.ASSISTENTE_TURNOS_POR_CONVERSA = 1
    porta = porta_falsa(_vagas)
    conversa = str(uuid.uuid4())

    _perguntar(edital_91, conversa=conversa)
    segunda = _perguntar(edital_91, conversa=conversa)

    assert segunda.estado == LIMITE_DE_USO
    assert len(porta.chamadas) == 1


def test_a_aplicacao_nao_conta_chamadas_externas(edital_91, porta_falsa, contador_falso, externo):
    """O limite é o da credencial: a aplicação não recusa por contagem, na tela nem na avaliação."""
    contador_falso()
    porta = porta_falsa(_vagas, _vagas, _vagas)
    externo()

    assert _perguntar(edital_91).estado == RESPONDIDA_E_CONFERIDA
    assert _perguntar(edital_91).estado == RESPONDIDA_E_CONFERIDA
    assert _perguntar(edital_91, origem=AVALIACAO).estado == RESPONDIDA_E_CONFERIDA
    assert len(porta.chamadas) == 3


def test_cb11_dado_pessoal_nao_sai_para_o_servico_externo(
    edital_91, porta_falsa, contador_falso, externo
):
    contador_falso()
    porta = porta_falsa()
    externo()

    troca = _perguntar(edital_91, texto="Meu CPF é 123.456.789-09, fui aprovado?")

    assert troca.estado == PERGUNTA_RECUSADA
    assert troca.pergunta == "Meu CPF é [CPF], fui aprovado?"
    assert porta.chamadas == []


def test_no_servico_local_o_dado_pessoal_e_mascarado_e_sai(edital_91, porta_falsa, contador_falso):
    contador_falso()
    porta = porta_falsa(_vagas)

    _perguntar(edital_91, texto="Escrevo de maria@exemplo.test: quantas vagas em BJN?")

    enviada = porta.chamadas[0]["mensagens"][-1]["content"]
    assert enviada == "Escrevo de [e-mail]: quantas vagas em BJN?"
