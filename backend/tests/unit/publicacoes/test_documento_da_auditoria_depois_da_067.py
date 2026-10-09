"""O que a `067` mudou nos documentos da auditoria — e só isso (SC-502, D-010).

Atualizar uma fixture de bytes é apagar a evidência que ela guardava, a menos que outra coisa diga o
que mudou. É esta: o texto do PDF que a auditoria de 08/10/2026 gravou, transformado **só** pelas
mudanças pretendidas — a frase de recurso que passa a nomear o resultado (ED-02), as linhas de
arredondamento e de empate sob sorteio que saem (ED-03), os quadros zerados e as reversões dos
Perfis sem vaga imediata que saem (ED-12) —, tem de ser igual ao texto do documento composto agora.

O que **não** é diferença de conteúdo é neutralizado antes da comparação, e só isto: o rodapé de
cada página (a paginação muda, e o B perde oito páginas), o cabeçalho de tabela repetido quando a
tabela atravessa a quebra, e o número das "Tabela N" (as seguintes avançam sem lacuna).
"""

import re

import pytest

from tests.unit.publicacoes.cenarios_da_auditoria import composto, publicado_na_auditoria
from tests.unit.publicacoes.test_pdf import texto_de

RODAPE = re.compile(r" ?Edital \d+/\d+ · Verificação [0-9a-f]+… Página \d+ de \d+")
CABECALHOS = (
    "Nº Evento Início Término Onde",
    "Modalidade Percentual Fundamento normativo",
    "Lista de concorrência Vagas imediatas",
    "Código Perfil Vagas imediatas Cadastro reserva",
)


def _corrido(documento):
    texto = re.sub(r"\s+", " ", texto_de(documento))
    texto = RODAPE.sub("", texto)
    texto = re.sub(r"Tabela \d+ —", "Tabela N —", texto)
    for cabecalho in CABECALHOS:
        texto = texto.replace(f" {cabecalho} ", " ")
    return texto


def _recurso(nome, dias, extenso):
    de_antes = (
        f"Recurso: Caberá recurso no prazo de {dias} ({extenso}) dias corridos, contados da "
        "divulgação do resultado."
    )
    agora = (
        f"Recurso: Caberá recurso contra o resultado de “{nome}”, no prazo de {dias} ({extenso}) "
        "dias corridos, contados da divulgação desse resultado."
    )
    return de_antes, agora


def _substituir(texto, de_antes, agora, quantas):
    assert texto.count(de_antes) == quantas, (de_antes, texto.count(de_antes))
    return texto.replace(de_antes, agora)


def test_a_diferenca_do_cenario_a_e_so_a_pretendida():
    antes = _corrido(publicado_na_auditoria("A"))
    agora = _corrido(composto("A"))

    esperado = _substituir(antes, *_recurso("Classificação por sorteio eletrônico", 2, "dois"), 4)
    esperado = _substituir(esperado, " Arredondamento: 2 casas decimais, meio para cima", "", 4)
    esperado = _substituir(
        esperado,
        " Empate no corte: Havendo empate na última posição, essa quantidade não é excedida.",
        "",
        4,
    )
    assert esperado == agora


def test_a_diferenca_do_cenario_b_e_so_a_pretendida():
    antes = _corrido(publicado_na_auditoria("B"))
    agora = _corrido(composto("B"))

    esperado = _substituir(
        antes, *_recurso("Classificação final pela prova de títulos", 3, "três"), 18
    )
    # Os 16 Perfis de tutor presencial: o quadro de zeros e a reversão logo abaixo dele.
    quadro_zerado = re.compile(
        r" Tabela N — Quadro de vagas — (TP-\d+) Ampla concorrência 0 (?:[^0-9]+? 0 ){3}"
        r"Na hipótese do não preenchimento total das vagas reservadas, o quantitativo não "
        r"preenchido será destinado à respectiva ampla concorrência\."
    )
    retirados = quadro_zerado.findall(esperado)
    assert retirados == [f"TP-{n:02d}" for n in range(1, 17)]
    esperado = quadro_zerado.sub("", esperado)
    # O arredondamento e o empate do B ficam: o marco dele ordena por pontuação.
    assert esperado.count("Arredondamento: 2 casas decimais, meio para cima") == 18
    assert esperado == agora


@pytest.mark.parametrize("cenario", ["A", "B"])
def test_o_documento_de_agora_nao_tem_a_frase_sem_objeto(cenario):
    assert "contados da divulgação do resultado" not in _corrido(composto(cenario))
