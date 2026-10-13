"""O catálogo fechado: o que se oferece, com que parâmetros, e o que se recusa (070, T008)."""

import pytest

from processo_seletivo.duvidas.domain import catalogo
from tests.fixtures.corpus import conteudo

TODAS = [pergunta.codigo for pergunta in catalogo.PERGUNTAS]


@pytest.mark.parametrize(
    ("nome", "publicacao", "esperadas"),
    [
        # 01/2026: dois Perfis por pontuação, sem sorteio.
        ("01", 3, [codigo for codigo in TODAS if codigo != "P-09"]),
        # 91/2026: quatro polos por sorteio.
        ("91", 2, TODAS),
        # 92/2026: dezoito Perfis pela prova de títulos.
        ("92", 2, [codigo for codigo in TODAS if codigo != "P-09"]),
    ],
)
def test_as_perguntas_oferecidas_dependem_do_conteudo(nome, publicacao, esperadas):
    oferecidas = [pergunta.codigo for pergunta in catalogo.oferecidas(conteudo(nome, publicacao))]
    assert oferecidas == esperadas


def test_um_perfil_so_nao_oferece_a_pergunta_de_mais_de_um_perfil():
    unico = dict(conteudo("01", 3))
    unico["profiles"] = unico["profiles"][:1]
    assert "P-06" not in [pergunta.codigo for pergunta in catalogo.oferecidas(unico)]


def test_as_listas_da_p05_sao_sem_modalidade_mais_as_do_perfil():
    perfil = conteudo("91", 2)["profiles"][0]
    assert [codigo for codigo, _ in catalogo.opcoes_de_modalidade(perfil)] == [
        catalogo.SEM_MODALIDADE,
        "AC",
        "PcD",
        "PPI",
    ]


def test_pergunta_que_nao_se_aplica_e_recusada_com_motivo():
    with pytest.raises(catalogo.ParametroRecusado, match="não se aplica"):
        catalogo.resolver(catalogo.POR_CODIGO["P-09"], conteudo("01", 3), perfil="DOC-INFO")


def test_perfil_que_nao_existe_na_versao_vigente_e_recusado():
    with pytest.raises(catalogo.ParametroRecusado, match="não existe"):
        catalogo.resolver(catalogo.POR_CODIGO["P-03"], conteudo("91", 2), perfil="XYZ")


def test_modalidade_que_nao_existe_no_perfil_e_recusada():
    with pytest.raises(catalogo.ParametroRecusado, match="modalidade"):
        catalogo.resolver(
            catalogo.POR_CODIGO["P-05"], conteudo("91", 2), perfil="INF-BJN", modalidade="PTT"
        )


def test_modalidade_de_outro_perfil_e_recusada():
    """A `PPP` existe no 01/2026, mas só no `DOC-INFO`: no `TEC-LAB` ela não é lista de concorrência
    (`FR-1418`). O caso acima usa um código que nenhum Perfil do 91/2026 tem."""
    with pytest.raises(catalogo.ParametroRecusado, match="não existe no Perfil TEC-LAB"):
        catalogo.resolver(
            catalogo.POR_CODIGO["P-05"], conteudo("01", 1), perfil="TEC-LAB", modalidade="PPP"
        )


def test_pergunta_com_perfil_exige_o_perfil():
    with pytest.raises(catalogo.ParametroRecusado, match="Perfil"):
        catalogo.resolver(catalogo.POR_CODIGO["P-03"], conteudo("91", 2))


def test_o_catalogo_nao_tem_pergunta_de_texto_livre():
    """`FR-1419`: nenhum parâmetro recebe texto que não venha de uma lista do próprio Edital."""
    for pergunta in catalogo.PERGUNTAS:
        assert set(pergunta.parametros) <= {catalogo.PERFIL, catalogo.MODALIDADE}
