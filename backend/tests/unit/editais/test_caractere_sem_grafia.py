"""Caractere sem grafia — caractere que o documento oficial não imprime impede a publicação.

O renderizador trocava o caractere por `?` em silêncio, e nenhuma validação o via. A Constituição
(Princípio II) pede que o PDF corresponda exatamente à versão homologada, e que a divergência entre
os dois impeça a publicação. O que `grafia` normaliza sem mudar o significado não é achado; o que
sobra é impeditivo, nos dois atos, com o lugar e o caractere nomeados.

A cobertura de **todos** os campos impressos é conferida em `test_pdf_grafia.py`, contra o próprio
renderizador. Aqui fica o comportamento da regra.
"""

import pytest

from processo_seletivo.editais.domain.validation import (
    ATO_DE_PUBLICACAO,
    ATO_DE_RETIFICACAO,
    CARACTERE_SEM_GRAFIA,
    Severity,
    validate_for_publication,
)
from tests.fixtures.snapshot import PERFIL, conteudo_normativo


def _achados(conteudo, ato=ATO_DE_PUBLICACAO):
    return [
        item
        for item in validate_for_publication(conteudo, ato=ato)
        if item.code == CARACTERE_SEM_GRAFIA
    ]


def _com_atribuicoes(texto):
    conteudo = conteudo_normativo()
    conteudo["profiles"][0]["duties"] = texto
    return conteudo


@pytest.mark.parametrize("ato", [ATO_DE_PUBLICACAO, ATO_DE_RETIFICACAO])
def test_caractere_sem_grafia_impede_nos_dois_atos(ato):
    """Na Retificação também: ela recompõe o documento inteiro, e o `?` sairia nele."""
    (achado,) = _achados(_com_atribuicoes("Experiência ≥ 2 anos."), ato=ato)

    assert achado.severity == Severity.BLOCKING_ERROR
    assert achado.path == f"/profiles/id={PERFIL['A']}/duties"


def test_a_mensagem_diz_o_campo_o_perfil_e_o_caractere():
    conteudo = _com_atribuicoes("Experiência ≥ 2 anos.")
    nome = conteudo["profiles"][0]["name"]

    (achado,) = _achados(conteudo)

    assert achado.message == (
        f"Nas atribuições do Perfil «{nome}», há «≥» (U+2265) — caractere que o documento oficial "
        "não imprime. Reescreva o trecho sem ele."
    )


def test_varios_caracteres_no_mesmo_campo_sao_um_achado_so():
    (achado,) = _achados(_com_atribuicoes("≥ 2 anos → ≤ 5 anos ≥"))

    assert "«≥» (U+2265), «→» (U+2192) e «≤» (U+2264)" in achado.message
    assert achado.message.endswith(
        "caracteres que o documento oficial não imprime. Reescreva o trecho sem eles."
    )


def test_o_que_a_lista_normaliza_nao_e_achado():
    """As atribuições do Edital 90/2026, como foram coladas do Word."""
    assert _achados(_com_atribuicoes("●\u200b Conhecer o curso;\n\uf0b7 Mediar.")) == []


def test_o_marcador_vazado_e_achado():
    """Decisão de 08/10: normalizá-lo apagaria o nível da lista."""
    (achado,) = _achados(_com_atribuicoes("◦ Subitem"))
    assert "«◦» (U+25E6)" in achado.message


def test_o_invisivel_que_sobra_e_nomeado_pelo_codigo():
    (achado,) = _achados(_com_atribuicoes("Planejar\x07 aulas."))
    assert "há (U+0007) —" in achado.message


@pytest.mark.parametrize(
    ("alterar", "caminho", "lugar"),
    [
        (lambda c: c.update(title="Edital ≥"), "title", "No título do Edital"),
        (
            lambda c: c["profiles"][0]["requirements"].append("Experiência ≥ 2 anos"),
            None,
            "requisito do Perfil",
        ),
        (
            lambda c: c["schedule"][0].update(location="Sala → 2"),
            None,
            "No local do Evento",
        ),
    ],
)
def test_cada_lugar_e_nomeado(alterar, caminho, lugar):
    conteudo = conteudo_normativo()
    alterar(conteudo)

    (achado,) = _achados(conteudo)

    assert lugar in achado.message
    if caminho is not None:
        assert achado.path == caminho


def test_o_requisito_e_nomeado_pela_posicao():
    conteudo = conteudo_normativo()
    conteudo["profiles"][0]["requirements"] = ["Diploma", "Experiência ≥ 2 anos"]

    (achado,) = _achados(conteudo)

    assert achado.path == f"/profiles/id={PERFIL['A']}/requirements/1"
    assert achado.message.startswith("No 2º requisito do Perfil")


def test_campo_que_o_documento_nao_imprime_nao_e_recusado():
    """Decisão de 08/10: a descrição da Modalidade só aparece na web, que é UTF-8."""
    conteudo = conteudo_normativo()
    conteudo["profiles"][0]["competitionModalities"][0]["description"] = "Renda ≤ 1,5 salário"

    assert _achados(conteudo) == []
