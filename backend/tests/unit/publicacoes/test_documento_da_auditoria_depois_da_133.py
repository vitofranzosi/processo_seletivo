"""O que a `133` mudou nos documentos do cenário B — e só isso (FR-4553, R-008).

Os bytes esperados do B passam a ser os que a `133` grava em
`specs/133-jornada-sem-ato-errado/demonstracao/`, e os da `096` ficam onde estão, como evidência
dela. O que mudou é preso aqui: o texto da `133` é o da `096` com o complemento "de cada lista de
concorrência" no corte de alvo fixo — o B tem Perfis com Modalidades reservadas e corte fixo —, e
nada mais. O complemento não muda a regra: o motor sempre aplicou o alvo fixo em cada lista (CV-10
do estudo de 07/11/2026).

O que **não** é conteúdo é neutralizado antes da comparação: o rodapé de cada página, as quebras de
linha (o complemento reflui o parágrafo) e o número de página das entradas do sumário.
"""

import re

import pytest

from tests.unit.publicacoes.test_itens_do_documento import RAIZ
from tests.unit.publicacoes.test_pdf import texto_de

DEMONSTRACAO_096 = RAIZ / "specs" / "096-cadastro-de-reserva-como-cr" / "demonstracao"
DEMONSTRACAO_133 = RAIZ / "specs" / "133-jornada-sem-ato-errado" / "demonstracao"
DOCUMENTOS = ("B-plana", "B-publicado", "B-variante")
COMPLEMENTO = " de cada lista de concorrência"

RODAPE = re.compile(r"^Edital \d+/\d+ · Verificação [0-9a-f]+…$|^Página \d+ de \d+$")
PAGINA_DO_SUMARIO = re.compile(r"(\. \. \.)\s*\d+")


def _corrido(documento):
    linhas = [linha.strip() for linha in texto_de(documento).splitlines()]
    texto = " ".join(linha for linha in linhas if linha and not RODAPE.match(linha))
    texto = re.sub(r"\s+", " ", texto)
    return PAGINA_DO_SUMARIO.sub(r"\1 <página>", texto)


@pytest.mark.parametrize("nome", DOCUMENTOS)
def test_a_diferenca_para_a_096_e_so_o_complemento_de_cada_lista(nome):
    antes = _corrido((DEMONSTRACAO_096 / f"{nome}-096.pdf").read_bytes())
    depois = _corrido((DEMONSTRACAO_133 / f"{nome}-133.pdf").read_bytes())

    assert COMPLEMENTO in depois
    assert COMPLEMENTO not in antes
    assert depois.replace(COMPLEMENTO, "") == antes
