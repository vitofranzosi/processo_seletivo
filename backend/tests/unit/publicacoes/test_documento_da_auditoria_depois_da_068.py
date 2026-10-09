"""O que a `068` mudou nos documentos da auditoria — e só isso (ED-04, ED-11; SC-510 a SC-514).

O "antes" é o documento que a `067` gravou (`specs/067-…/demonstracao/`), que era a `main` antes
desta feature; o "agora", o que o compositor faz hoje com o mesmo conteúdo e o mesmo contexto do
ato. A equivalência **dentro** da seção de Perfis — cada Perfil com toda a regra que tinha — é
provada por `test_equivalencia_da_consolidacao.py`. Aqui se prende o resto:

- **fora** da seção de Perfis, o texto é o mesmo, palavra por palavra — salvo o número das
  "Tabela N", que a tabela única desloca;
- o que se repetia sai **uma** vez (SC-512);
- as páginas caem até a meta da spec (SC-510, SC-511), e o espaço liberado não vira branco no pé
  das páginas (SC-514).
"""

import re

import pytest

from processo_seletivo.publicacoes.infrastructure.pdf import RODAPE as MARGEM_DE_BAIXO
from tests.unit.publicacoes.cenarios_da_auditoria import composto
from tests.unit.publicacoes.test_documento_da_auditoria_depois_da_067 import (
    CABECALHOS,
    RODAPE,
    da_067,
)
from tests.unit.publicacoes.test_pdf import alturas_por_pagina, paginas_de, texto_de

SECOES = {
    "A": ("5. PERFIS DE VAGA", "6. DA INSCRIÇÃO"),
    "B": ("3. PERFIS DE VAGA", "4. DA INSCRIÇÃO"),
}


def _corrido(documento):
    texto = re.sub(r"\s+", " ", texto_de(documento))
    texto = RODAPE.sub("", texto)
    texto = re.sub(r"Tabela \d+ —", "Tabela N —", texto)
    for cabecalho in CABECALHOS:
        texto = texto.replace(f" {cabecalho} ", " ")
    return texto


def _fora_da_secao_de_perfis(documento, cenario):
    inicio, fim = SECOES[cenario]
    texto = _corrido(documento)
    return texto[: texto.index(inicio)] + texto[texto.index(fim) :]


@pytest.mark.parametrize("cenario", ["A", "B"])
def test_fora_da_secao_de_perfis_o_texto_e_o_mesmo(cenario):
    assert _fora_da_secao_de_perfis(composto(cenario), cenario) == _fora_da_secao_de_perfis(
        da_067(cenario), cenario
    )


def _ocorrencias(documento, trecho):
    return " ".join(texto_de(documento).split()).count(trecho)


@pytest.mark.parametrize(
    ("cenario", "trecho", "antes"),
    [
        ("A", "SORTEIO — Classificação por sorteio eletrônico", 4),
        ("A", "Algoritmo: IFES-SORTEIO-SHA256-v1", 4),
        ("A", "Se faltar: Não havendo extração na data prevista", 4),
        ("A", "Havendo ausência de candidatos aprovados na reserva de vagas", 4),
        ("A", "A convocação dos classificados será feita por publicação", 4),
        ("A", "PPI — Pretos, pardos e indígenas", 4),
        ("A", "Acesso a computador com conexão à internet", 4),
        ("B", "FINAL — Classificação final pela prova de títulos", 18),
        ("B", "Critérios de desempate:", 18),
        ("B", "Na hipótese do não preenchimento total das vagas reservadas", 2),
        ("B", "A convocação dos classificados será feita por mensagem individual", 18),
        ("B", "PTT — Pessoas transgênero e travestis", 18),
        ("B", "Residir no município do polo ou em município limítrofe", 16),
    ],
)
def test_o_que_se_repetia_sai_uma_vez(cenario, trecho, antes):
    """SC-512: o texto dos marcos, o método, as frases, as modalidades e os requisitos, uma vez."""
    assert _ocorrencias(da_067(cenario), trecho) == antes
    assert _ocorrencias(composto(cenario), trecho) == 1


def _paginas_da_secao(documento, cenario):
    """`(primeira, última)` — da página do título da seção à do título da seguinte."""
    inicio, fim = SECOES[cenario]
    paginas = paginas_de(documento)
    primeira = next(n for n, pagina in enumerate(paginas, 1) if inicio in pagina)
    ultima = next(n for n, pagina in enumerate(paginas, 1) if fim in pagina)
    return primeira, ultima


@pytest.mark.parametrize(
    ("cenario", "total_antes", "secao_antes", "total_meta", "secao_meta"),
    [("A", 9, 5, 7, 3), ("B", 36, 30, 18, 12)],
)
def test_as_paginas_caem_ate_a_meta(cenario, total_antes, secao_antes, total_meta, secao_meta):
    """SC-510 e SC-511, sobre o conteúdo congelado; o fluxo real está em `verificacao.md`."""
    antes, agora = da_067(cenario), composto(cenario)
    primeira, ultima = _paginas_da_secao(antes, cenario)
    assert (len(paginas_de(antes)), ultima - primeira + 1) == (total_antes, secao_antes)
    primeira, ultima = _paginas_da_secao(agora, cenario)
    assert len(paginas_de(agora)) <= total_meta
    assert ultima - primeira + 1 <= secao_meta


def _branco_no_pe(documento, cenario):
    """A soma, em pontos, do branco entre a última linha e o rodapé nas páginas da seção.

    A última página da seção fica de fora: ela é dividida com a seção seguinte, e o branco dela é
    o de lá.
    """
    primeira, ultima = _paginas_da_secao(documento, cenario)
    total = 0.0
    for ys in alturas_por_pagina(documento)[primeira - 1 : ultima - 1]:
        corpo = [y for y in ys if y > MARGEM_DE_BAIXO]
        total += min(corpo) - (MARGEM_DE_BAIXO + 24)
    return total


@pytest.mark.parametrize("cenario", ["A", "B"])
def test_o_espaco_liberado_nao_vira_branco(cenario):
    """SC-514: a soma do branco no pé das páginas da seção de Perfis cai."""
    assert _branco_no_pe(composto(cenario), cenario) < _branco_no_pe(da_067(cenario), cenario)
