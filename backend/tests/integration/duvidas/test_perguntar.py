"""Uma pergunta ao piloto de ponta a ponta, com a porta falsa (071, `R-011`, US1).

O Edital é o 91/2026 do corpus, publicado e retificado pelo fluxo real. A porta falsa lê as fontes
que recebeu e cita pelo identificador, como o modelo faria; a contagem é o contador falso.
"""

import pytest
from django.utils import timezone

from processo_seletivo.duvidas.application.consultar import SemVersaoVigente
from processo_seletivo.duvidas.application.perguntar import perguntar
from processo_seletivo.duvidas.domain.estruturas_do_piloto import (
    CITACAO_NAO_LITERAL,
    FONTE_INEXISTENTE,
    NAO_PASSOU_NA_CONFERENCIA,
    RESPONDIDA_E_CONFERIDA,
    SEM_TOKENIZER,
    TELA,
    VALOR_SEM_FONTE,
)
from processo_seletivo.duvidas.models import TrocaDoPiloto
from tests.fixtures.corpus import publicar_do_corpus
from tests.fixtures.inferencia import devolucao, saida
from tests.fixtures.inferencia_corpus import fonte

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

RECURSOS = "Não serão aceitos recursos enviados por e-mail ou fora do prazo."
CONVERSA = "2b1c6f1e-0071-4000-8000-000000000001"


@pytest.fixture
def edital_91(api_client):
    edital, _ = publicar_do_corpus(api_client, "91", chave="piloto91")
    return edital


def _perguntar(edital, texto="Quantas vagas tem o polo de Bom Jesus do Norte?"):
    return perguntar(
        edital_id=edital.id,
        conversa=CONVERSA,
        pergunta=texto,
        instante=timezone.now(),
        origem=TELA,
    )


def _vagas_de_bjn(mensagens):
    total = fonte(mensagens, lugar="INF-BJN", rotulo="Vagas imediatas")
    ampla = fonte(mensagens, lugar="INF-BJN", rotulo="Vagas da ampla concorrência")
    return devolucao(
        saida(
            "RESPONDIDA",
            ("dado", "O polo de Bom Jesus do Norte tem 45 vagas.", [total["id"]]),
            ("dado", "Dessas, 33 são de ampla concorrência.", [ampla["id"]]),
        )
    )


def test_a_resposta_conferida_e_gravada_com_as_fontes(edital_91, porta_falsa, contador_falso):
    """US1, cenário 1: 45 e 33, e a fonte das 45 leva ao documento da Retificação."""
    contador_falso()
    porta = porta_falsa(_vagas_de_bjn)

    troca = _perguntar(edital_91)

    assert len(porta.chamadas) == 1
    assert troca.estado == RESPONDIDA_E_CONFERIDA
    assert troca.tipo == "RESPONDIDA"
    assert [trecho["texto"] for trecho in troca.trechos][0].endswith("45 vagas.")
    vagas = next(item for item in troca.fontes_citadas if item["rotulo"] == "Vagas imediatas")
    assert vagas["conteudo"] == "45"
    assert vagas["origens"][-1]["ato"] == "RETIFICACAO"
    assert vagas["origens"][-1]["documento"]
    assert troca.impressao_das_fontes and troca.versao


def test_a_citacao_literal_de_dos_recursos_e_aprovada(edital_91, porta_falsa, contador_falso):
    """US1, cenário 2."""
    contador_falso()

    def responder(mensagens):
        recursos = fonte(mensagens, lugar="Dos Recursos")
        return devolucao(saida("RESPONDIDA", ("citacao", f"“{RECURSOS}”", [recursos["id"]])))

    porta_falsa(responder)

    assert _perguntar(edital_91, "O que diz o Edital sobre recurso por e-mail?").estado == (
        RESPONDIDA_E_CONFERIDA
    )


@pytest.mark.parametrize(
    ("fabricar", "regra"),
    [
        (lambda m: saida("RESPONDIDA", ("dado", "São 45 vagas.", ["F9999"])), FONTE_INEXISTENTE),
        (
            lambda m: saida(
                "RESPONDIDA",
                (
                    "citacao",
                    "Não serão aceitos recursos enviados por e-mail.",
                    [fonte(m, lugar="Dos Recursos")["id"]],
                ),
            ),
            CITACAO_NAO_LITERAL,
        ),
        (
            lambda m: saida(
                "RESPONDIDA",
                (
                    "dado",
                    "São 46 vagas.",
                    [fonte(m, lugar="INF-BJN", rotulo="Vagas imediatas")["id"]],
                ),
            ),
            VALOR_SEM_FONTE,
        ),
    ],
)
def test_a_saida_invalida_nao_vira_resposta(
    edital_91, porta_falsa, contador_falso, fabricar, regra
):
    """US1, cenário 3: gravada como recusa, com o motivo, e com uma chamada só."""
    contador_falso()
    porta = porta_falsa(lambda mensagens: devolucao(fabricar(mensagens)))

    troca = _perguntar(edital_91)

    assert len(porta.chamadas) == 1
    assert troca.estado == NAO_PASSOU_NA_CONFERENCIA
    assert regra in [motivo["regra"] for motivo in troca.conferencia]


def test_o_raciocinio_nao_vai_a_troca(edital_91, porta_falsa, contador_falso):
    """`FR-1492`: o raciocínio do modelo não é gravado, em campo nenhum."""
    contador_falso()

    def responder(mensagens):
        resposta = _vagas_de_bjn(mensagens)
        return devolucao(resposta.texto, raciocinio="PENSAMENTO-QUE-NAO-SE-GRAVA")

    porta_falsa(responder)
    troca = _perguntar(edital_91)

    gravada = TrocaDoPiloto.objects.filter(pk=troca.pk).values()[0]
    assert "PENSAMENTO-QUE-NAO-SE-GRAVA" not in repr(gravada)


def test_a_troca_nao_guarda_quem_perguntou(edital_91, porta_falsa, contador_falso):
    """`FR-1509`: nenhuma coluna identifica o participante."""
    contador_falso()
    porta_falsa(_vagas_de_bjn)
    _perguntar(edital_91)

    colunas = {campo.name for campo in TrocaDoPiloto._meta.get_fields()}
    assert not colunas & {"ator", "subject", "usuario", "sessao", "papel", "origem_ip"}


def test_a_pergunta_e_gravada_mascarada(edital_91, porta_falsa, contador_falso):
    contador_falso()
    porta = porta_falsa(_vagas_de_bjn)

    troca = _perguntar(edital_91, "Meu CPF é 123.456.789-09: quantas vagas há em BJN?")

    assert troca.pergunta == "Meu CPF é [CPF]: quantas vagas há em BJN?"
    assert "123.456.789-09" not in porta.chamadas[0]["mensagens"][-1]["content"]


def test_sem_tokenizer_nao_ha_chamada(edital_91, porta_falsa, settings):
    """`FR-1479`: sem medir, não há como garantir que nada foi cortado."""
    settings.ASSISTENTE_TOKENIZER = ""
    porta = porta_falsa()

    troca = _perguntar(edital_91)

    assert troca.estado == SEM_TOKENIZER
    assert porta.chamadas == []
    assert troca.chamou_o_servico is False


def test_edital_sem_publicacao_nao_tem_conversa(porta_falsa, contador_falso, api_client):
    from processo_seletivo.processos.models import Edital
    from tests.fixtures.edital import actor_headers

    criado = api_client.post(
        "/api/v1/admin/processos",
        {
            "institutionalCode": "PS-071-SEM-PUBLICACAO",
            "title": "Processo sem publicação",
            "firstEdital": {"number": "71", "year": 2026, "title": "Edital em elaboração"},
        },
        format="json",
        **actor_headers(
            "gestor-a", ["processo:criar", "edital:criar"], key="piloto-sem-publicacao-0001"
        ),
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    porta = porta_falsa()

    with pytest.raises(SemVersaoVigente):
        _perguntar(edital)
    assert porta.chamadas == []
    assert not TrocaDoPiloto.objects.filter(edital=edital).exists()
