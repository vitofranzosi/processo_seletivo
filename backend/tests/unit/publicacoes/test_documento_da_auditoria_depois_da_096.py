"""O que a `096` mudou nos documentos do cenário B — e só isso (SC-900, D-009).

Atualizar os bytes esperados é apagar a evidência que eles guardavam, a menos que outra coisa diga o
que mudou. É esta: o texto dos PDFs que a `069` gravou, e o dos que a `096` grava, diferem **só** em
dezesseis células de vagas dos tutores presenciais, que passam de `0` a `CR`, e numa nota "CR:
cadastro de reserva." depois da tabela que as tem. Os PDFs da `069` ficam onde estão, como evidência
dela, e não são regravados.

O que **não** é diferença de conteúdo é neutralizado antes da comparação, e só isto: o rodapé de
cada página, o cabeçalho de tabela repetido quando a tabela atravessa a quebra, e o número de página
das entradas do sumário — a nota é uma linha a mais, e no B plano três seções começam uma página
adiante.
"""

import difflib
import re

import pytest

from tests.unit.publicacoes.test_itens_do_documento import RAIZ
from tests.unit.publicacoes.test_pdf import texto_de

DEMONSTRACAO_069 = RAIZ / "specs" / "069-edital-linguagem-simples" / "demonstracao"
DEMONSTRACAO_096 = RAIZ / "specs" / "096-cadastro-de-reserva-como-cr" / "demonstracao"
DOCUMENTOS = ("B-plana", "B-publicado", "B-variante")
NOTA = "CR: cadastro de reserva."
TUTORES_PRESENCIAIS = 16

RODAPE = re.compile(r"^Edital \d+/\d+ · Verificação [0-9a-f]+…$|^Página \d+ de \d+$")
# A entrada do sumário termina na linha de pontos, e a página vem na linha seguinte.
ENTRADA_DO_SUMARIO = re.compile(r"\. \. \.$")
CABECALHOS_REPETIDOS = (("Nº", "Evento", "Quando", "Onde"),)


def da_069(nome):
    return (DEMONSTRACAO_069 / f"{nome}-069.pdf").read_bytes()


def da_096(nome):
    return (DEMONSTRACAO_096 / f"{nome}-096.pdf").read_bytes()


def _linhas(documento):
    linhas = [linha.strip() for linha in texto_de(documento).splitlines()]
    linhas = [linha for linha in linhas if linha and not RODAPE.match(linha)]
    neutras = []
    for indice, linha in enumerate(linhas):
        if indice and ENTRADA_DO_SUMARIO.search(linhas[indice - 1]) and linha.isdigit():
            neutras.append("<página>")
        else:
            neutras.append(linha)
    for cabecalho in CABECALHOS_REPETIDOS:
        tamanho, sem = len(cabecalho), []
        indice = 0
        while indice < len(neutras):
            if tuple(neutras[indice : indice + tamanho]) == cabecalho:
                indice += tamanho
                continue
            sem.append(neutras[indice])
            indice += 1
        neutras = sem
    return neutras


def _diferencas(nome):
    antes, depois = _linhas(da_069(nome)), _linhas(da_096(nome))
    casamento = difflib.SequenceMatcher(None, antes, depois, autojunk=False)
    return depois, [
        (tag, antes[i1:i2], depois[j1:j2], j1)
        for tag, i1, i2, j1, j2 in casamento.get_opcodes()
        if tag != "equal"
    ]


@pytest.mark.parametrize("nome", DOCUMENTOS)
def test_a_diferenca_para_a_069_e_so_a_sigla_e_a_nota(nome):
    _, diferencas = _diferencas(nome)

    trocas = [d for d in diferencas if d[:3] == ("replace", ["0"], ["CR"])]
    notas = [d for d in diferencas if d[:3] == ("insert", [], [NOTA])]
    outras = [d for d in diferencas if d not in trocas and d not in notas]

    assert len(trocas) == TUTORES_PRESENCIAIS
    assert len(notas) == 1
    assert not outras, f"diferença que a 096 não pretendia: {outras[:3]}"


@pytest.mark.parametrize("nome", DOCUMENTOS)
def test_cada_cr_e_de_um_tutor_presencial_e_a_nota_vem_depois_deles(nome):
    depois, diferencas = _diferencas(nome)
    posicoes = [j for tag, _, novas, j in diferencas if novas == ["CR"]]
    (nota,) = [j for tag, _, novas, j in diferencas if novas == [NOTA]]

    for posicao in posicoes:
        # A linha do Perfil começa pelo código; a célula de vagas vem poucas linhas depois.
        contexto = depois[max(posicao - 6, 0) : posicao]
        assert any(linha.startswith("TP-") for linha in contexto), contexto
    assert nota > max(posicoes)
