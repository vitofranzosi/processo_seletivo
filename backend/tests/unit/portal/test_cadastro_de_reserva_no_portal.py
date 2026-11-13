"""O número do cadastro no portal e no assistente, pela regra única (162, FR-6945, FR-6946).

O portal diz ao candidato quantos o cadastro comporta, e o assistente responde a mesma pergunta; os
dois leem `cadastro_de_reserva`, e o Perfil publicado antes da `162` continua dizendo o número que
publicou.
"""

from types import SimpleNamespace

import pytest

from processo_seletivo.duvidas.domain import respostas
from processo_seletivo.portal import situacao, views
from tests.unit.editais.test_cadastro_de_reserva import marco, perfil, regra, tres_listas


def _so_reserva(**extra):
    return perfil(vagas=0, **extra)


# --- A oferta (`_oferta`) ------------------------------------------------------------------------


def test_a_oferta_diz_o_numero_do_corte():
    montado = _so_reserva(marcos=[marco(corte=regra(alvo=6))])
    assert (
        views._oferta(0, "LIMITED", montado)["detalhe"]
        == "até 6 classificados, para convocação futura"
    )


def test_a_oferta_com_o_mesmo_numero_em_cada_lista():
    modalidades, quadro = tres_listas()
    for linha in quadro:
        linha["immediateVacancies"] = 0
    montado = _so_reserva(
        quadro=quadro, modalidades=modalidades, marcos=[marco(corte=regra(alvo=2))]
    )
    assert views._oferta(0, "LIMITED", montado)["detalhe"] == (
        "até 2 classificados em cada lista de concorrência, para convocação futura"
    )


def test_a_oferta_do_legado_diz_o_que_publicou():
    montado = _so_reserva(limite=6, marcos=[marco(corte=regra(alvo=3))])
    assert (
        views._oferta(0, "LIMITED", montado)["detalhe"]
        == "até 6 classificados, para convocação futura"
    )


# --- O acompanhamento (`frase_da_reserva`) -------------------------------------------------------


def test_a_frase_do_acompanhamento_diz_o_numero_do_corte():
    montado = perfil(marcos=[marco(corte=regra(excedente=3))])
    assert situacao.frase_da_reserva(montado) == (
        "O Edital prevê cadastro reserva de até 3 pessoas para este Perfil."
    )


def test_a_frase_do_acompanhamento_por_lista():
    modalidades, quadro = tres_listas()
    montado = perfil(
        vagas=4, quadro=quadro, modalidades=modalidades, marcos=[marco(corte=regra(alvo=3))]
    )
    assert situacao.frase_da_reserva(montado) == (
        "O Edital prevê cadastro reserva de até 1 pessoas na ampla concorrência, 2 na lista "
        "Pessoas com deficiência e 2 na lista Pretos, pardos e indígenas deste Perfil."
    )


def test_a_frase_do_acompanhamento_do_legado():
    montado = perfil(limite=9, marcos=[marco(corte=regra(excedente=3))])
    assert situacao.frase_da_reserva(montado) == (
        "O Edital prevê cadastro reserva de até 9 pessoas para este Perfil."
    )


# --- O assistente (FR-6946) ----------------------------------------------------------------------


def _cartao_do_limite(montado):
    contexto = SimpleNamespace(
        conteudo={"profiles": [montado]}, instante=None, desfecho=None, pagina_publica=None
    )
    pergunta = SimpleNamespace(acompanha=())
    rascunho = respostas._p03(contexto, SimpleNamespace(perfil=montado), pergunta, None)
    referencias = getattr(rascunho, "referencias", None) or getattr(rascunho, "cartoes", [])
    return [ref for ref in referencias if ref.rotulo == "Limite do cadastro de reserva"]


@pytest.mark.parametrize(
    ("montado", "conteudo", "caminho"),
    [
        (
            perfil(marcos=[marco(corte=regra(excedente=3))]),
            "até 3",
            "/profiles/id=p1/classificationMilestones/id=m1/cutRule/surplusCount",
        ),
        (
            perfil(limite=6, marcos=[marco(corte=regra(excedente=3))]),
            "6",
            "/profiles/id=p1/reserveLimit",
        ),
    ],
    ids=["derivado", "legado"],
)
def test_o_assistente_diz_o_numero_e_cita_de_onde_ele_vem(montado, conteudo, caminho):
    (cartao,) = _cartao_do_limite(montado)
    assert (cartao.conteudo, cartao.caminho) == (conteudo, caminho)


def test_a_explicacao_do_assistente_diz_o_numero_sem_o_ate():
    montado = perfil(marcos=[marco(corte=regra(excedente=3))])
    contexto = SimpleNamespace(
        conteudo={"profiles": [montado]}, instante=None, desfecho=None, pagina_publica=None
    )
    pergunta = SimpleNamespace(acompanha=())
    rascunho = respostas._p03(contexto, SimpleNamespace(perfil=montado), pergunta, None)
    assert "O cadastro de reserva é limitado a 3." in rascunho.explicacao
