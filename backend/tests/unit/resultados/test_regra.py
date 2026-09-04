"""A tabela-verdade da V1, sem banco.

Quatro linhas, e duas delas são impedimento — a Etapa não pode ser consolidada. Sem elas escritas
aqui, a decisão de "o que fazer quando o Edital diz eliminatória e não diz mínima" cairia em quem
implementa, que é como uma invariante não declarada entra por uma expressão regular.
"""

from decimal import Decimal

import pytest

from processo_seletivo.avaliacoes.domain.formas import Forma, Sentido
from processo_seletivo.resultados.application.prontidao import Conclusao
from processo_seletivo.resultados.domain.regra import (
    ELIMINADA,
    HABILITADA,
    REGRA_DE_COMBINACAO_AUSENTE,
    REGRA_INSUFICIENTE,
    consequencia,
    impedimento_da_regra,
)


def pontuada(valor):
    """A conclusão pontuada que `consequencia` recebe — a assinatura passou a levar a conclusão."""
    return Conclusao(
        avaliacao_id=None, forma=Forma.PONTUADA, pontuacao=valor, sentido="", conteudo=None
    )


def decisoria(sentido):
    return Conclusao(
        avaliacao_id=None, forma=Forma.DECISORIA, pontuacao=None, sentido=sentido, conteudo=None
    )


def etapa(**kwargs):
    base = {"id": "e1", "order": 0, "eliminatory": False, "classificatory": False}
    base.update(kwargs)
    return base


def test_leitura_unica_e_eliminatoria_com_minima_tem_regra():
    assert impedimento_da_regra(etapa(eliminatory=True, minimumScore="60.0000")) is None


def test_mais_de_uma_avaliacao_impede_a_etapa_inteira():
    codigo, frase = impedimento_da_regra(etapa(evaluationsPerRegistration=2))
    assert codigo == REGRA_DE_COMBINACAO_AUSENTE
    # A frase nomeia a quantidade publicada: "não dá para consolidar" sem dizer quantas são deixa
    # a presidência sem a ação seguinte.
    assert "2 avaliações" in frase


def test_eliminatoria_sem_nota_minima_nao_tem_regra_suficiente():
    codigo, _ = impedimento_da_regra(etapa(eliminatory=True))
    assert codigo == REGRA_INSUFICIENTE


def test_etapa_nao_eliminatoria_dispensa_nota_minima():
    assert impedimento_da_regra(etapa(eliminatory=False)) is None


@pytest.mark.parametrize(
    ("pontuacao", "esperada"),
    [(Decimal("75.0000"), HABILITADA), (Decimal("55.0000"), ELIMINADA)],
)
def test_eliminatoria_compara_com_a_minima(pontuacao, esperada):
    resultado, _ = consequencia(
        etapa(eliminatory=True, minimumScore="60.0000"), pontuada(pontuacao)
    )
    assert resultado == esperada


def test_nota_exatamente_igual_a_minima_habilita():
    """O caso em que o arredondamento binário decidiria a vida de alguém."""
    resultado, _ = consequencia(
        etapa(eliminatory=True, minimumScore="60.0000"), pontuada(Decimal("60.0000"))
    )
    assert resultado == HABILITADA


def test_a_eliminacao_carrega_a_causa_com_os_dois_numeros():
    _, motivo = consequencia(
        etapa(eliminatory=True, minimumScore="60.0000"), pontuada(Decimal("55.0000"))
    )
    assert "55,0000" in motivo and "60,0000" in motivo


def test_etapa_nao_eliminatoria_habilita_mesmo_abaixo_da_minima_publicada():
    """Nota mínima sem caráter eliminatório não elimina: sem o caráter, ela não é critério."""
    resultado, motivo = consequencia(
        etapa(eliminatory=False, minimumScore="60.0000"), pontuada(Decimal("10.0000"))
    )
    assert resultado == HABILITADA
    assert "não tem caráter eliminatório" in motivo


def test_peso_e_carater_classificatorio_nao_alteram_a_consequencia():
    """Os dois pertencem à composição entre Etapas, que esta feature recusa."""
    com_peso = etapa(eliminatory=True, minimumScore="60.0000", weight="3.0000", classificatory=True)
    sem_peso = etapa(eliminatory=True, minimumScore="60.0000")
    assert consequencia(com_peso, pontuada(Decimal("70.0000"))) == consequencia(
        sem_peso, pontuada(Decimal("70.0000"))
    )


# ---------------------------------------------------------- a forma decisória (013, D-008)


def decisoria_etapa(**extra):
    return etapa(
        forma="DECISORIA", rotuloFavoravel="Deferido", rotuloDesfavoravel="Indeferido", **extra
    )


def test_decisoria_eliminatoria_sem_nota_minima_nao_cai_em_regra_insuficiente():
    """A configuração real dos Editais 35 e 57 — e, até esta revisão, recusada (013, FR-048)."""
    assert impedimento_da_regra(decisoria_etapa(eliminatory=True)) is None


def test_pontuada_eliminatoria_sem_nota_minima_continua_caindo():
    """A recusa não sumiu: ela passou a valer só onde há nota para faltar."""
    codigo, frase = impedimento_da_regra(etapa(eliminatory=True))

    assert codigo == REGRA_INSUFICIENTE
    assert "não publicou nota mínima" in frase


def test_decisoria_nao_eliminatoria_e_impedida_e_a_frase_diz_por_que():
    """O Edital não publicou o que o desfavorável produz, e o sistema não infere (013, FR-047)."""
    codigo, frase = impedimento_da_regra(decisoria_etapa(eliminatory=False))

    assert codigo == REGRA_INSUFICIENTE
    assert "não publicou o efeito da decisão desfavorável" in frase


def test_o_sentido_vira_consequencia_na_etapa_eliminatoria():
    eliminada, causa = consequencia(
        decisoria_etapa(eliminatory=True), decisoria(Sentido.DESFAVORAVEL)
    )
    habilitada, _ = consequencia(decisoria_etapa(eliminatory=True), decisoria(Sentido.FAVORAVEL))

    assert eliminada == ELIMINADA and habilitada == HABILITADA
    # O rótulo publicado, e nunca o enum: quem lê o Resultado tem direito ao vocabulário do Edital.
    assert "Indeferido" in causa and "DESFAVORAVEL" not in causa


def test_a_forma_decisoria_nao_le_nota_minima():
    """Publicá-la ali seria regra fictícia; o que decide é o sentido (012, FR-121)."""
    com_minima = decisoria_etapa(eliminatory=True, minimumScore="60.0000")

    assert consequencia(com_minima, decisoria(Sentido.FAVORAVEL))[0] == HABILITADA
