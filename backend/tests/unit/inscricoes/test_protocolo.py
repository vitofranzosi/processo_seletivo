"""O protocolo que o candidato leva embora (US5 da 009, FR-062)."""

import re

import pytest

from processo_seletivo.inscricoes.domain.protocolo import ALFABETO, COMPRIMENTO, gerar

FORMA = re.compile(r"^INS-(\d{4})-([" + ALFABETO + r"]{" + str(COMPRIMENTO) + r"})$")


def test_a_forma_e_a_declarada():
    assert FORMA.match(gerar(2026))


def test_o_ano_e_o_informado():
    assert gerar(2027).startswith("INS-2027-")


@pytest.mark.parametrize("ambiguo", ["0", "O", "1", "I", "L"])
def test_o_alfabeto_nao_tem_caractere_que_se_confunde(ambiguo):
    """Ele é ditado ao telefone, copiado à mão e lido em voz alta."""
    assert ambiguo not in ALFABETO


def test_nao_e_sequencial():
    """Sequência diria quantas inscrições existem e em que ordem chegaram."""
    sorteios = {gerar(2026) for _ in range(200)}

    assert len(sorteios) > 190, "duzentos sorteios não podem colidir em massa"


def test_o_espaco_de_sorteio_e_grande_o_bastante_para_a_escala_prevista():
    """Milhares de inscrições por seleção contra 31^8 combinações."""
    assert len(ALFABETO) ** COMPRIMENTO > 10**11
