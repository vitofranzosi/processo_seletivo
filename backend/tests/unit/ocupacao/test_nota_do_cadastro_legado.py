"""A nota do cadastro legado na ocupação e na convocação (162, T035, FR-6947, FR-6949).

O Perfil publicado antes da `162` com número digitado continua dizendo o número; quem conduz lê, na
tela, que o sistema não o aplica e quem o corte alcança.
"""

import pytest

from processo_seletivo.ocupacao.application.selectors import nota_do_cadastro_legado

from ..editais.test_cadastro_de_reserva import marco, perfil, regra, tres_listas


def conteudo(*perfis):
    return {"profiles": list(perfis)}


def test_sem_continuacao_diz_o_alcance():
    legado = perfil(limite=6, marcos=[marco(corte=regra(excedente=3))])
    assert nota_do_cadastro_legado(conteudo(legado), "p1") == (
        "O Edital publicou cadastro de reserva limitado em 6. O sistema não aplica esse número: a "
        "convocação alcança quem o corte alcança — até 3 classificados além das vagas."
    )


def test_com_continuacao_diz_que_a_faixa_cresce():
    legado = perfil(limite=6, marcos=[marco(corte=regra(excedente=3, continuacao="ALLOWED"))])
    assert nota_do_cadastro_legado(conteudo(legado), "p1") == (
        "O Edital publicou cadastro de reserva limitado em 6. O sistema não aplica esse número: a "
        "convocação alcança quem o corte alcança, e a faixa cresce pela faixa seguinte do corte, "
        "na ordem."
    )


def test_sem_corte():
    legado = perfil(limite=6, marcos=[marco()])
    assert nota_do_cadastro_legado(conteudo(legado), "p1") == (
        "O Edital publicou cadastro de reserva limitado em 6. O sistema não aplica esse número, e "
        "nenhum marco que convoca deste Perfil declara corte."
    )


def test_por_lista():
    modalidades, quadro = tres_listas()
    legado = perfil(
        limite=6,
        vagas=4,
        quadro=quadro,
        modalidades=modalidades,
        marcos=[marco(corte=regra(alvo=3))],
    )
    assert nota_do_cadastro_legado(conteudo(legado), "p1").endswith(
        "— até 1 na ampla concorrência, 2 na lista Pessoas com deficiência e 2 na lista Pretos, "
        "pardos e indígenas, além das vagas."
    )


def test_a_nota_sai_mesmo_quando_os_numeros_coincidem():
    """FR-6949: o sistema continua não aplicando o número publicado, ainda que ele bata."""
    legado = perfil(limite=3, marcos=[marco(corte=regra(excedente=3))])
    assert nota_do_cadastro_legado(conteudo(legado), "p1").startswith(
        "O Edital publicou cadastro de reserva limitado em 3."
    )


@pytest.mark.parametrize(
    "montado",
    [
        perfil(marcos=[marco(corte=regra(excedente=3))]),
        perfil(especie="UNLIMITED", marcos=[marco(corte=regra(continuacao="ALLOWED"))]),
        perfil(especie="NONE"),
    ],
    ids=["limitado-derivado", "ilimitado", "nao-ha"],
)
def test_sem_nota_fora_do_legado(montado):
    assert nota_do_cadastro_legado(conteudo(montado), "p1") is None


def test_perfil_ausente():
    assert nota_do_cadastro_legado(conteudo(), "p1") is None
