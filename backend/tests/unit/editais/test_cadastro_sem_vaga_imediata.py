"""Quem o documento imprime como `CR` (096, FR-2402, D-005).

O Perfil continua guardando `0` vagas imediatas, e é a composição que decide entre o número e a
sigla. A decisão é deste predicado, e de mais ninguém: as quatro composições que imprimem o número o
leem, para que a tabela de Perfis, a ficha do Perfil único e as duas tabelas da apresentação por
perguntas não discordem sobre o mesmo Perfil.

Não é o `sem_vaga_imediata` da `067`. Aquele responde se o quadro e a reversão saem, e por isso diz
**não** quando não há quadro declarado — o acervo anterior à `025`. Este responde se há oferta de
cadastro sem vaga, e o quadro ausente não muda a resposta.
"""

import pytest

from processo_seletivo.editais.domain import quadro


def _perfil(total=0, linhas=None, reserva="LIMITED"):
    perfil = {"immediateVacancies": total, "reserveType": reserva}
    if linhas is not None:
        perfil["vacancyTable"] = [
            {"modalityId": None if indice == 0 else f"m{indice}", "immediateVacancies": valor}
            for indice, valor in enumerate(linhas)
        ]
    return perfil


@pytest.mark.parametrize(
    "perfil",
    [
        pytest.param(_perfil(reserva="LIMITED"), id="sem quadro, limitado"),
        pytest.param(_perfil(reserva="UNLIMITED"), id="sem quadro, ilimitado"),
        pytest.param(_perfil(linhas=[0, 0, 0, 0], reserva="UNLIMITED"), id="quadro todo em 0"),
        pytest.param(_perfil(linhas=[], reserva="LIMITED"), id="quadro vazio"),
    ],
)
def test_zero_vaga_e_cadastro_declarado_e_cr(perfil):
    assert quadro.cadastro_sem_vaga_imediata(perfil) is True


@pytest.mark.parametrize(
    "perfil",
    [
        # O incoerente: a validação o recusa, e o documento imprime `0` para que o erro se veja,
        # como a `067` faz com o quadro (caso-limite da spec).
        pytest.param(_perfil(linhas=[0, 2]), id="total 0 com linha positiva"),
        pytest.param(_perfil(reserva="NONE"), id="sem cadastro"),
        pytest.param(_perfil(reserva=None), id="cadastro ausente"),
        pytest.param({"immediateVacancies": 0}, id="sem a chave do cadastro"),
        pytest.param(_perfil(reserva="OUTRO"), id="tipo desconhecido"),
        pytest.param(_perfil(total=3), id="com vaga"),
        # `bool` é `int` em Python, e o snapshot é JSON: `False` não é zero declarado.
        pytest.param(_perfil(total=False), id="False"),
        pytest.param(_perfil(total=True), id="True"),
        pytest.param(_perfil(total="0"), id="texto"),
        pytest.param({"reserveType": "LIMITED"}, id="total ausente"),
    ],
)
def test_os_demais_nao_sao_cr(perfil):
    assert quadro.cadastro_sem_vaga_imediata(perfil) is False


@pytest.mark.parametrize("perfil", [None, [], "TP-01", 0])
def test_o_que_nao_e_perfil_nao_e_cr(perfil):
    assert quadro.cadastro_sem_vaga_imediata(perfil) is False


def test_o_acervo_sem_quadro_e_cr_e_para_a_067_continua_sem_vaga_nao():
    """A diferença entre os dois predicados, que é a razão de existirem dois (D-005)."""
    acervo = _perfil(reserva="LIMITED")

    assert quadro.cadastro_sem_vaga_imediata(acervo) is True
    assert quadro.sem_vaga_imediata(acervo) is False
