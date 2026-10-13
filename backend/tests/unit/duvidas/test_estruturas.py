"""As estruturas da resposta: a forma serializada e as portas que elas guardam (070, T005)."""

from datetime import UTC, datetime

import pytest

from processo_seletivo.duvidas.domain.estruturas import (
    DADO,
    EXPLICACAO,
    ORIGINAL,
    RESPONDIDA,
    TEXTO,
    AtoPublicado,
    Referencia,
    Resposta,
    VersaoConsultada,
)

DIA = datetime(2026, 10, 11, tzinfo=UTC)
ATO = AtoPublicado("pub-1", ORIGINAL, 1, DIA, DIA, "/documento")
VERSAO = VersaoConsultada("v1", "abcdef123456", DIA, DIA)
EXPLICA = Referencia(EXPLICACAO, "Explicação", "texto")


def resposta(*referencias):
    return Resposta("P-01", (), DIA, VERSAO, RESPONDIDA, EXPLICA, tuple(referencias))


def test_a_ordem_das_chaves_e_fixa():
    dados = resposta(Referencia(DADO, "lugar", "1", "/x", origens=(ATO,))).como_dict()
    assert list(dados) == [
        "pergunta",
        "parametros",
        "instante",
        "versao",
        "mudanca",
        "tipo",
        "avisos",
        "explicacao",
        "referencias",
        "situacao",
    ]
    assert list(dados["referencias"][0]) == [
        "natureza",
        "localizacao",
        "caminho",
        "posicao",
        "rotulo",
        "conteudo",
        "origens",
        "futuro",
        "links",
    ]


def test_a_explicacao_nao_tem_ato_de_origem():
    with pytest.raises(ValueError, match="explicação"):
        Referencia(EXPLICACAO, "Explicação", "texto", origens=(ATO,))


@pytest.mark.parametrize("natureza", [TEXTO, DADO])
def test_texto_e_dado_sem_origem_nao_saem_na_resposta(natureza):
    with pytest.raises(ValueError, match="sem ato de origem"):
        resposta(Referencia(natureza, "lugar", "conteúdo", "/x"))


def test_natureza_desconhecida_e_recusada():
    with pytest.raises(ValueError, match="natureza"):
        Referencia("CITACAO", "lugar", "conteúdo")
