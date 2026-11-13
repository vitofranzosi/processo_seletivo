"""O cadastro de reserva nas telas da gestão (162, T010, T036).

A Etapa Perfis já tem os testes do bloco da opção limitada em `test_campos_que_a_escolha_governa`;
aqui ficam a nota e o resumo do cartão calculados do corte salvo, a linha da Revisão e a nota do
legado nas duas telas da condução.
"""

from pathlib import Path

import pytest

from processo_seletivo.interface import revisao
from processo_seletivo.interface.forms import cadastro_para_o_cartao
from tests.unit.editais.test_cadastro_de_reserva import marco, perfil, regra, tres_listas

TEMPLATES = Path(revisao.__file__).parent / "templates" / "interface"


# --- A Etapa Perfis (FR-6932, UX-725) -----------------------------------------------------------


def test_a_nota_sem_corte_nao_tem_numero():
    assert cadastro_para_o_cartao(perfil(marcos=[marco()])) == {
        "frase": "",
        "listas": [],
        "resumo": "limitado",
    }


def test_a_nota_com_numero_unico():
    nota = cadastro_para_o_cartao(perfil(marcos=[marco(corte=regra(excedente=3))]))
    assert nota == {
        "frase": "O número vem do corte do marco “Classificação final”: até 3 classificados.",
        "listas": [],
        "resumo": "limitado: até 3",
    }


def test_a_nota_por_lista():
    modalidades, quadro = tres_listas()
    nota = cadastro_para_o_cartao(
        perfil(vagas=4, quadro=quadro, modalidades=modalidades, marcos=[marco(corte=regra(alvo=3))])
    )
    assert nota["frase"] == "O número vem do corte do marco “Classificação final”:"
    assert nota["listas"] == [
        "Ampla concorrência: até 1",
        "Pessoas com deficiência: até 2",
        "Pretos, pardos e indígenas: até 2",
    ]


def test_a_nota_ignora_o_numero_digitado_e_a_especie_marcada():
    """Calculada sobre o corte salvo: quem troca para limitado lê o número na hora."""
    nota = cadastro_para_o_cartao(
        perfil(especie="NONE", limite=6, marcos=[marco(corte=regra(excedente=3))])
    )
    assert nota["resumo"] == "limitado: até 3"


def test_o_cartao_nao_tem_mais_o_campo_do_numero():
    cartao = (TEMPLATES / "_perfil.html").read_text()
    assert "-reserveLimit" not in cartao
    assert 'id="cadastro-perfil-{{ indice }}"' in cartao
    assert 'aria-describedby="cadastro-perfil-{{ indice }}"' in cartao


# --- A Revisão (FR-6930) ------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("montado", "esperado"),
    [
        (perfil(marcos=[marco(corte=regra(excedente=3))]), "Limitado: até 3"),
        (perfil(limite=6, marcos=[marco(corte=regra(excedente=3))]), "Limitado em 6"),
        (perfil(marcos=[marco()]), "Limitado, sem corte no marco que convoca"),
        (perfil(especie="UNLIMITED"), "Sem limite"),
    ],
)
def test_a_revisao_diz_o_cadastro_pela_regra_unica(montado, esperado):
    linhas = revisao._perfil(montado, {"profiles": [montado], "stages": []})["linhas"]
    (cadastro,) = [linha for linha in linhas if getattr(linha, "rotulo", "") == "Cadastro Reserva"]
    assert cadastro.valor == esperado


# --- A nota do legado na condução (FR-6947, UX-727) ----------------------------------------------


@pytest.mark.parametrize("tela", ["ocupacao.html", "convocacao.html"])
def test_a_nota_do_legado_e_nota_e_nao_alerta(tela):
    corpo = (TEMPLATES / tela).read_text()
    assert '{% if nota_do_cadastro %}<p class="nota">{{ nota_do_cadastro }}</p>{% endif %}' in corpo
