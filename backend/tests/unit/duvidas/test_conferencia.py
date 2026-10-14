"""A conferência da saída do modelo, sobre saídas fabricadas (071, `R-005`, `FR-1487`, `SC-546`).

Cada caso é um defeito que o modelo comete, e a conferência precisa recusá-lo inteiro — ou uma saída
certa, que ela precisa deixar passar. As recusas indevidas também são defeito: são medidas na
avaliação, e as que se conhecem estão aqui.
"""

import pytest

from processo_seletivo.duvidas.domain.conferencia import conferir
from processo_seletivo.duvidas.domain.estruturas import DADO, TEXTO
from processo_seletivo.duvidas.domain.estruturas_do_piloto import (
    CALCULADA,
    CITACAO_NAO_LITERAL,
    FONTE_INEXISTENTE,
    FORMA,
    NEGATIVA_NAO_DECLARADA,
    TIPO_SEM_FONTE,
    VALOR_SEM_FONTE,
    Fonte,
)
from tests.fixtures.inferencia import saida

RECURSOS = "Não serão aceitos recursos enviados por e-mail ou fora do prazo."
FONTES = (
    Fonte("F1", TEXTO, "Seção “Dos Recursos”, 2º parágrafo", RECURSOS),
    Fonte("F2", DADO, "Perfil INF-BJN — Especialização", "45", rotulo="Vagas imediatas"),
    Fonte("F3", DADO, "Perfil INF-BJN — Especialização", "33", rotulo="Ampla concorrência"),
    Fonte(
        "F4",
        DADO,
        "Cronograma — evento “Período de inscrições”",
        "04/11/2026, às 23h59",
        rotulo="Término",
    ),
    Fonte(
        "F5",
        TEXTO,
        "Seção “Disposições Preliminares”, 2º parágrafo",
        "As dúvidas serão esclarecidas exclusivamente pelo e-mail "
        "selecao.demo@exemplo.ifes.edu.br.",
    ),
    Fonte("F6", DADO, "Modalidade PPI", "25.0000", rotulo="Percentual"),
    Fonte("F7", DADO, "Anexos", "ANEXO II — MODELO DE LAUDO MÉDICO", anexo=True),
    Fonte("F8", CALCULADA, "Situação de calendário", "Situação em 20/10/2026, às 12h: abertas."),
)


def _motivos(texto, **opcoes):
    return [motivo.regra for motivo in conferir(texto, FONTES, **opcoes).motivos]


@pytest.mark.parametrize(
    ("texto", "regra"),
    [
        ("isto não é JSON", FORMA),
        ('{"tipo": "RESPONDIDA"}', FORMA),
        (saida("INVENTADO", ("dado", "45 vagas.", ["F2"])), FORMA),
        (saida("RESPONDIDA", ("opiniao", "45 vagas.", ["F2"])), FORMA),
        (saida("RESPONDIDA", ("dado", "45 vagas.", ["F99"])), FONTE_INEXISTENTE),
        # Um ponto a mais, e já não é o que o Edital diz.
        (
            saida(
                "RESPONDIDA", ("citacao", "Não serão aceitos recursos enviados por e-mail.", ["F1"])
            ),
            CITACAO_NAO_LITERAL,
        ),
        # Citação que é texto do Edital, mas citando um dado: não é citação literal.
        (saida("RESPONDIDA", ("citacao", "45", ["F2"])), CITACAO_NAO_LITERAL),
        # A soma que nenhuma fonte traz (`CB-12`).
        (saida("RESPONDIDA", ("dado", "São 180 vagas no total.", ["F2", "F3"])), VALOR_SEM_FONTE),
        # A data certa, citando a fonte errada: o valor tem de estar na fonte do próprio trecho.
        (saida("RESPONDIDA", ("dado", "Até 04/11/2026.", ["F2"])), VALOR_SEM_FONTE),
        (saida("RESPONDIDA", ("dado", "Até 05/11/2026.", ["F4"])), VALOR_SEM_FONTE),
        (
            saida("RESPONDIDA", ("dado", "Escreva para outro@exemplo.test.", ["F5"])),
            VALOR_SEM_FONTE,
        ),
        # A contagem de dias (`CB-13`) e a explicação sem fonte com número.
        (saida("RESPONDIDA", ("explicacao", "Faltam 15 dias.", ["F8"])), VALOR_SEM_FONTE),
        (saida("RESPONDIDA", ("explicacao", "São 45 vagas.", [])), VALOR_SEM_FONTE),
    ],
)
def test_cada_defeito_recusa(texto, regra):
    assert regra in _motivos(texto)


@pytest.mark.parametrize(
    "texto",
    [
        saida(
            "RESPONDIDA", ("dado", "O polo tem 45 vagas, 33 de ampla concorrência.", ["F2", "F3"])
        ),
        saida("RESPONDIDA", ("citacao", f"“{RECURSOS}”", ["F1"])),
        saida("RESPONDIDA", ("citacao", "Não serão aceitos recursos enviados por e-mail", ["F1"])),
        # A data por extenso casa com a numérica, e a hora em qualquer grafia.
        saida("RESPONDIDA", ("dado", "Até 4 de novembro de 2026, às 23:59.", ["F4"])),
        saida("RESPONDIDA", ("dado", "Até 4 de novembro, às 23h59.", ["F4"])),
        saida("RESPONDIDA", ("dado", "A reserva é de 25% das vagas.", ["F6"])),
        saida(
            "RESPONDIDA",
            ("dado", "Escreva para selecao.demo@exemplo.ifes.edu.br (F5).", ["F5"]),
        ),
        saida("OUTRA_SELECAO", ("explicacao", "Respondo só sobre o Edital 91/2026.", [])),
    ],
)
def test_saidas_certas_passam(texto):
    assert _motivos(texto, permitidos=("91", "2026")) == []


def test_a_conferencia_devolve_a_saida_lida():
    conferencia = conferir(saida("RESPONDIDA", ("dado", "45 vagas.", ["F2"])), FONTES)

    assert conferencia.aprovada
    assert conferencia.saida.citadas() == ("F2",)


@pytest.mark.parametrize(
    ("texto", "regra"),
    [
        (saida("RESPONDIDA", ("explicacao", "O Edital trata disso.", [])), TIPO_SEM_FONTE),
        (saida("FONTES_DIVERGENTES", ("explicacao", "Há duas leituras.", ["F1"])), TIPO_SEM_FONTE),
        (saida("DETALHE_EM_ANEXO", ("explicacao", "Está num anexo.", ["F1"])), TIPO_SEM_FONTE),
        (
            saida("NAO_INFORMA", ("explicacao", "Não cabe recurso desse resultado.", [])),
            NEGATIVA_NAO_DECLARADA,
        ),
    ],
)
def test_o_tipo_exige_as_fontes_que_ele_supoe(texto, regra):
    assert regra in _motivos(texto)


def test_negativa_declarada_numa_fonte_citada_passa():
    """ "Não serão aceitos" está no Edital: dizê-lo não é transformar silêncio em proibição."""
    texto = saida("NAO_INFORMA", ("explicacao", "Recursos por e-mail não serão aceitos.", ["F1"]))

    assert NEGATIVA_NAO_DECLARADA not in _motivos(texto)


def test_divergencia_com_duas_fontes_e_anexo_com_fonte_de_anexo_passam():
    assert _motivos(saida("FONTES_DIVERGENTES", ("explicacao", "Há duas.", ["F1", "F5"]))) == []
    assert _motivos(saida("DETALHE_EM_ANEXO", ("explicacao", "Ver o Anexo II.", ["F7"]))) == []


def test_o_valor_recusado_e_legivel():
    """Achado na verificação pelo navegador, em 12/10: `150` aparecia como `1.5E+2`."""
    conferencia = conferir(saida("RESPONDIDA", ("dado", "Custa R$ 150,00.", ["F2"])), FONTES)

    assert [motivo.valor for motivo in conferencia.motivos] == ["150"]
