"""O cadastro de reserva no documento: uma resposta só para "quantos podem ser chamados" (162).

C1 a C4 de `specs/162-limite-da-reserva-pelo-corte/contracts/documento.md`, frase por frase, e os
quatro exemplos de aceitação. O exemplo que motivou a feature — Perfil só de reserva limitado em 6,
com corte fixo de 10 e continuação — imprimia três números diferentes; ele não é mais publicável
(FR-6933), e o par coerente que o substitui diz um só (SC-2302).
"""

import pytest

from processo_seletivo.publicacoes.infrastructure import pdf
from processo_seletivo.publicacoes.infrastructure.pdf import REDACAO_1, REDACAO_2

from ..editais.test_cadastro_de_reserva import (
    ETAPA_DA_ENTREVISTA,
    marco,
    perfil,
    regra,
    tres_listas,
)

ETAPAS = {ETAPA_DA_ENTREVISTA: {"id": ETAPA_DA_ENTREVISTA, "name": "Entrevista"}}


def corte(montado, *, com_reservadas=False):
    """A unidade do corte do primeiro marco, como o documento a imprime."""
    return pdf.frases_do_corte(
        montado["classificationMilestones"][0],
        ETAPAS,
        sem_cadastro=False,
        com_reservadas=com_reservadas,
        perfil=montado,
    )


# --- C1: a frase do cadastro (FR-6941, FR-6938) -------------------------------------------------


def test_c1_limitado_sem_modalidade():
    montado = perfil(marcos=[marco(corte=regra(excedente=3))])
    assert pdf.frase_do_cadastro(montado) == (
        "cadastro de reserva de até 3 (três) pessoas classificadas por Perfil"
    )


def test_c1_singular():
    montado = perfil(marcos=[marco(corte=regra(excedente=1))])
    assert pdf.frase_do_cadastro(montado) == (
        "cadastro de reserva de até 1 (uma) pessoa classificada por Perfil"
    )


def test_c1_mesmo_numero_em_cada_lista():
    modalidades, quadro = tres_listas()
    montado = perfil(
        vagas=4, quadro=quadro, modalidades=modalidades, marcos=[marco(corte=regra(excedente=2))]
    )
    assert pdf.frase_do_cadastro(montado) == (
        "cadastro de reserva de até 2 (duas) pessoas classificadas em cada lista de concorrência"
    )


def test_c1_numeros_diferentes_por_lista():
    modalidades, quadro = tres_listas()
    montado = perfil(
        vagas=4, quadro=quadro, modalidades=modalidades, marcos=[marco(corte=regra(alvo=3))]
    )
    assert pdf.frase_do_cadastro(montado) == (
        "cadastro de reserva de até 1 (uma) pessoa classificada na ampla concorrência, 2 (duas) na "
        "lista Pessoas com deficiência e 2 (duas) na lista Pretos, pardos e indígenas"
    )


def test_c1_empate_que_admite_excedente():
    montado = perfil(marcos=[marco(corte=regra(excedente=3, empate="ADMITS_SURPLUS"))])
    assert pdf.frase_do_cadastro(montado) == (
        "cadastro de reserva de até 3 (três) pessoas classificadas por Perfil, além das pessoas "
        "empatadas na "
        "última posição"
    )


def test_c1_limitado_sem_corte_nao_inventa_numero():
    assert pdf.frase_do_cadastro(perfil(marcos=[marco()])) == ""


def test_c1_sem_mudanca_para_nao_ha_e_ilimitado():
    assert pdf.frase_do_cadastro(perfil(especie="NONE")) == "não há cadastro de reserva"
    assert pdf.frase_do_cadastro(perfil(especie="UNLIMITED")) == (
        "cadastro de reserva sem limite de pessoas classificadas"
    )


def test_c1_o_legado_imprime_o_que_publicou():
    """FR-6944: o número digitado, mesmo com um corte que daria outro."""
    montado = perfil(limite=6, marcos=[marco(corte=regra(excedente=3))])
    assert pdf.frase_do_cadastro(montado) == (
        "cadastro de reserva de até 6 (seis) pessoas classificadas por Perfil"
    )


# --- C2: a célula -------------------------------------------------------------------------------


def test_c2_as_tres_formas():
    assert pdf._reserva(perfil(marcos=[marco(corte=regra(excedente=3))]), redacao=REDACAO_2) == (
        "até 3 (três) classificados"
    )
    modalidades, quadro = tres_listas()
    mesma = perfil(
        vagas=4, quadro=quadro, modalidades=modalidades, marcos=[marco(corte=regra(excedente=2))]
    )
    assert pdf._reserva(mesma, redacao=REDACAO_2) == "até 2 (dois) classificados por lista"
    diferentes = perfil(
        vagas=4, quadro=quadro, modalidades=modalidades, marcos=[marco(corte=regra(alvo=3))]
    )
    assert (
        pdf._reserva(diferentes, redacao=REDACAO_2) == "até 1 (um) AC, 2 (dois) PcD, 2 (dois) PPI"
    )


def test_c2_redacao_1():
    assert pdf._reserva(perfil(marcos=[marco(corte=regra(excedente=3))]), redacao=REDACAO_1) == (
        "limitado em 3"
    )
    assert pdf._reserva(perfil(limite=6), redacao=REDACAO_1) == "limitado em 6"


# --- C3: a abertura do Perfil só de reserva (FR-6943, SC-2299) ----------------------------------


def test_c3_limitado():
    montado = perfil(vagas=0, marcos=[marco(corte=regra(alvo=4, excedente=2))])
    unidade = corte(montado)
    assert (
        unidade[0] == "Compõem o cadastro de reserva as 6 (seis) primeiras pessoas classificadas."
    )
    assert not any("suplente" in frase for frase in unidade)


def test_c3_limitado_com_um_so():
    montado = perfil(vagas=0, marcos=[marco(corte=regra(alvo=1))])
    assert (
        corte(montado)[0] == "Compõe o cadastro de reserva a 1 (uma) primeira pessoa classificada."
    )


def test_c3_de_cada_lista():
    modalidades, quadro = tres_listas()
    for linha in quadro:
        linha["immediateVacancies"] = 0
    montado = perfil(
        vagas=0, quadro=quadro, modalidades=modalidades, marcos=[marco(corte=regra(alvo=2))]
    )
    assert corte(montado, com_reservadas=True)[0] == (
        "Compõem o cadastro de reserva as 2 (duas) primeiras pessoas classificadas de cada lista "
        "de "
        "concorrência."
    )


def test_c3_ilimitado_com_alcance():
    montado = perfil(
        especie="UNLIMITED",
        vagas=0,
        marcos=[marco(corte=regra(alvo=10, continuacao="ALLOWED", empate="ADMITS_SURPLUS"))],
    )
    unidade = corte(montado)
    assert unidade[0] == (
        "Compõem o cadastro de reserva todas as pessoas classificadas, sem limite. São chamadas "
        "primeiro "
        "as 10 (dez) primeiras."
    )
    assert (
        unidade[-1]
        == "Depois, poderão ser chamadas outras pessoas, além dessas, seguindo a mesma ordem."
    )


def test_c3_ilimitado_sem_alcance():
    montado = perfil(
        especie="UNLIMITED", vagas=0, marcos=[marco(corte=regra(continuacao="ALLOWED"))]
    )
    assert (
        corte(montado)[0]
        == "Compõem o cadastro de reserva todas as pessoas classificadas, sem limite."
    )


def test_c3_com_etapa_governada():
    montado = perfil(vagas=0, marcos=[marco(corte=regra(alvo=6, governada=ETAPA_DA_ENTREVISTA))])
    assert corte(montado)[0] == (
        "Compõem o cadastro de reserva as 6 (seis) primeiras pessoas classificadas. Elas "
        "participam da "
        "Etapa “Entrevista”."
    )


@pytest.mark.parametrize("especie", ["LIMITED", "UNLIMITED"])
def test_c3_nunca_abre_por_seguem_ou_passam(especie):
    continuacao = "ALLOWED" if especie == "UNLIMITED" else "NONE"
    for governada in ("NONE", ETAPA_DA_ENTREVISTA):
        montado = perfil(
            especie=especie,
            vagas=0,
            marcos=[marco(corte=regra(alvo=5, continuacao=continuacao, governada=governada))],
        )
        abertura = corte(montado)[0]
        assert not abertura.startswith(("Seguem no processo", "Passam para", "Segue", "Passa"))


def test_c3_so_no_marco_que_convoca():
    """O marco intermediário de um Perfil só de reserva continua dizendo quem vai à Etapa."""
    intermediario = marco(
        "m1",
        nome="Classificação para a entrevista",
        corte=regra(alvo=10, governada=ETAPA_DA_ENTREVISTA),
    )
    final = marco("m2", etapas=(ETAPA_DA_ENTREVISTA,), corte=regra(alvo=6))
    montado = perfil(vagas=0, marcos=[intermediario, final])
    assert corte(montado)[0].startswith("Passam para a Etapa “Entrevista” as 10 (dez) primeiras")


# --- C4: suplentes e cadastro (FR-6942) ----------------------------------------------------------


def test_c4_perfil_com_cadastro_e_vagas():
    montado = perfil(marcos=[marco(corte=regra(excedente=3))])
    assert pdf.SUPLENTES_DO_CADASTRO_3 in corte(montado)
    assert pdf.SUPLENTES_DO_CADASTRO_3 == (
        "As pessoas suplentes formam o cadastro de reserva deste Perfil e são chamadas, na ordem, "
        "para as "
        "vagas que não forem preenchidas pelas primeiras pessoas classificadas."
    )


def test_c4_perfil_sem_cadastro_explica_mesmo_com_outro_perfil_com_cadastro():
    """`sem_cadastro=False` é o Edital com cadastro em outro Perfil: o deste não tem, e explica."""
    montado = perfil(especie="NONE", marcos=[marco(corte=regra(excedente=3))])
    assert pdf.SUPLENTES_SEM_CADASTRO_3 in corte(montado)


# --- Os exemplos de aceitação (contrato) ---------------------------------------------------------


def test_exemplo_1():
    montado = perfil(marcos=[marco(corte=regra(excedente=3))])
    unidade = corte(montado)
    assert unidade[0] == (
        "Seguem no processo as primeiras pessoas classificadas de cada lista de concorrência, em "
        "número "
        "igual ao das vagas dessa lista, mais 3 (três) pessoas suplentes."
    )
    assert pdf.SUPLENTES_DO_CADASTRO_3 in unidade
    assert pdf.frase_do_cadastro(montado).startswith("cadastro de reserva de até 3 (três)")


def test_exemplo_2():
    montado = perfil(vagas=0, marcos=[marco(corte=regra(alvo=4, excedente=2))])
    assert (
        corte(montado)[0]
        == "Compõem o cadastro de reserva as 6 (seis) primeiras pessoas classificadas."
    )
    assert pdf._reserva(montado, redacao=REDACAO_2) == "até 6 (seis) classificados"


def test_exemplo_4():
    modalidades, quadro = tres_listas()
    montado = perfil(
        vagas=4, quadro=quadro, modalidades=modalidades, marcos=[marco(corte=regra(alvo=3))]
    )
    assert pdf._reserva(montado, redacao=REDACAO_2) == "até 1 (um) AC, 2 (dois) PcD, 2 (dois) PPI"


# --- SC-2302: um número só ----------------------------------------------------------------------


def test_um_numero_so_no_perfil_do_seed_demo():
    from processo_seletivo.processos.management.commands import seed_demo

    for montado in seed_demo.perfis("00"):
        if montado.get("reserveType") != "LIMITED":
            continue
        assert montado.get("reserveLimit") is None
        frase = pdf.frase_do_cadastro(montado)
        unidade = pdf.frases_do_corte(
            montado["classificationMilestones"][0],
            {},
            sem_cadastro=False,
            perfil=montado,
        )
        assert frase == (
            "cadastro de reserva de até 2 (duas) pessoas classificadas em cada lista de "
            "concorrência"
        )
        assert not any("poderão ser chamadas outras" in item for item in unidade)
