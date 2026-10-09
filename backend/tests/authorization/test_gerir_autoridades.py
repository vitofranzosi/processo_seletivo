"""Quem mantém as autoridades da unidade (060, D-005, FR-1122).

O Gestor da própria unidade, por permissão **própria**: destacá-la para outro papel, se o Ifes pedir
gestão centralizada, custa uma linha no mapa de papéis e nenhuma mudança no modelo.
"""

from processo_seletivo.interface import identidade
from processo_seletivo.unidades.domain import nomes


def test_a_grafia_da_permissao_e_a_mesma_nos_dois_lugares():
    """`identidade.py` a escreve literalmente, e não a importa de quem a consome — como a 040."""
    assert nomes.GERIR == "autoridade:gerir"
    assert nomes.GERIR in identidade.PAPEIS["gestor"][1]


def test_nenhum_outro_papel_mantem_autoridades():
    """Negar por padrão. Publicar, em especial, não concede manter quem assina (FR-1122)."""
    outros = [
        papel
        for papel, (_, permissoes) in identidade.PAPEIS.items()
        if papel != "gestor" and nomes.GERIR in permissoes
    ]
    assert outros == []


def test_manter_autoridades_nao_concede_publicar():
    """FR-1122, o outro sentido: quem cadastra não ganha, por cadastrar, o poder de publicar."""
    permissoes_de_quem_so_mantem = {nomes.GERIR}
    assert not permissoes_de_quem_so_mantem & {
        "edital:publicar",
        "retificacao:publicar",
        "resultado:publicar",
    }
    assert "edital:publicar" not in identidade.PAPEIS["gestor"][1]
