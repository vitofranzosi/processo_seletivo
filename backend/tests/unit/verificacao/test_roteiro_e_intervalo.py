"""O roteiro e as marcas (166, FR-7112, FR-7113), e o cabeçalho `Range` (FR-7131)."""

import pytest

from processo_seletivo.verificacao.domain import intervalo, roteiro


def _marcas(*instantes):
    return [
        {"passo": chave, "instante": instante}
        for chave, instante in zip(roteiro.CHAVES, instantes, strict=True)
    ]


def test_o_roteiro_tem_quatro_passos_e_nao_pede_o_cpf_falado():
    assert roteiro.CHAVES == ("documento", "perfil-esquerdo", "perfil-direito", "frente")
    assert "Não diga o seu CPF" in roteiro.PASSOS[-1].instrucao
    assert "Libras" in roteiro.PASSOS[-1].instrucao


def test_marcas_validas_sao_normalizadas():
    assert roteiro.conferir_marcas(_marcas(0, 1.2345, 2.5, 4), 4.8)[1]["instante"] == 1.234


@pytest.mark.parametrize(
    "marcas",
    [
        _marcas(0, 3, 2, 4),
        _marcas(0, 1, 2, 9),
        _marcas(2, 3, 4, 4.5),
        [{"passo": "documento", "instante": 0}],
        [{"passo": c, "instante": 0} for c in reversed(roteiro.CHAVES)],
        "texto",
    ],
    ids=["decrescente", "alem-da-duracao", "comeca-tarde", "faltam", "fora-de-ordem", "nao-lista"],
)
def test_marcas_invalidas_sao_recusadas(marcas):
    with pytest.raises(roteiro.MarcasInvalidas):
        roteiro.conferir_marcas(marcas, 4.8)


def test_nao_ha_tempo_minimo_por_passo():
    """R-14: os passos podem vir no mesmo instante — o roteiro não cronometra ninguém."""
    assert roteiro.conferir_marcas(_marcas(0, 0, 0, 0), 0.5)


@pytest.mark.parametrize(
    ("cabecalho", "esperado"),
    [
        (None, None),
        ("", None),
        ("bytes=0-", (0, 999)),
        ("bytes=0-1", (0, 1)),
        ("bytes=500-", (500, 999)),
        ("bytes=900-5000", (900, 999)),
        ("bytes=-100", (900, 999)),
        ("bytes=-5000", (0, 999)),
        ("bytes=0-1,5-9", None),
        ("itens=0-1", None),
        ("bytes=9-3", None),
    ],
)
def test_intervalo(cabecalho, esperado):
    assert intervalo.ler(cabecalho, 1000) == esperado


@pytest.mark.parametrize("cabecalho", ["bytes=1000-", "bytes=5000-6000", "bytes=-0"])
def test_intervalo_insatisfazivel(cabecalho):
    with pytest.raises(intervalo.Insatisfazivel):
        intervalo.ler(cabecalho, 1000)
