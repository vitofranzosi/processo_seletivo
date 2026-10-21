"""A prévia reserva o espaço do fecho, e pagina o corpo como o publicado (096, D-012, FR-2418).

**O defeito era da `069`, e a `096` o acordou.** Desde a `069` a última seção vai num bloco com o
fecho do ato (FR-1391): quando os dois não cabem na página, saltam juntos. A prévia não tem fecho —
não é ato, não tem autoridade (FR-035) —, e a última seção ficava onde estava. No cenário B, a seção
15 terminava a uma linha do pé da página 15; a nota "CR: cadastro de reserva." empurrou o documento
uma linha, e só no publicado a seção saltou para a 16 com o fecho. O sumário da prévia dizia "15",
o do publicado "16", e o guardião da `008` (FR-042) reprovou.

**A reserva é do espaço efetivamente necessário**, por decisão do usuário em 21/10/2026: o fecho é
composto de verdade, com a autoridade prevista, e cada linha dele passa à prévia com a mesma altura
e o mesmo `junto`; só o texto muda. Um aviso curto no lugar dele trocaria um acaso por outro.
"""

import pytest

from processo_seletivo.publicacoes.infrastructure import pdf
from tests.contract.test_documento_publicado import AUTORIDADE as AUTORIDADE_DO_CONTRATO
from tests.contract.test_documento_publicado import MARCA_DE_PREVIA, corpo_normativo, paginas_de
from tests.unit.publicacoes.cenarios_da_auditoria import (
    AUTORIDADES,
    DATA_DO_ATO,
    UNIDADE,
    congelado,
    levado_ao_catalogo_novo,
    variante_de_b,
)
from tests.unit.publicacoes.test_pdf import texto_de

CONTEUDOS_DE_B = {
    "B plana": lambda: congelado("B")["content"],
    "B por perguntas": lambda: levado_ao_catalogo_novo(congelado("B")["content"]),
    "B variante": variante_de_b,
}
# Três fechos de alturas diferentes: só o cargo (o B da auditoria), nome, cargo e ato de nomeação (o
# A), e o do contrato. O salto do B plano só acontece com os dois mais altos — medido em 21/10.
PREVISTAS = {
    "só o cargo": AUTORIDADES["B"],
    "nome, cargo e ato": AUTORIDADES["A"],
    "a do contrato": AUTORIDADE_DO_CONTRATO,
}


def _publicado(conteudo, autoridade):
    return pdf.render_edital_pdf(
        conteudo,
        congelado("B")["hash"],
        pdf.MODO_PUBLICADO,
        unidade=UNIDADE,
        autoridade=autoridade,
        data_do_ato=DATA_DO_ATO,
    )


def _previa(conteudo, previstos):
    return pdf.render_edital_pdf(
        conteudo, "", pdf.MODO_PREVIA, unidade=UNIDADE, fechos_previstos=previstos
    )


def _corpo_por_pagina(documento):
    return [corpo_normativo(pagina, MARCA_DE_PREVIA) for pagina in paginas_de(documento)]


def _sumario(documento):
    """As linhas do sumário — título e página —, que são onde a diferença aparecia primeiro."""
    corpo = [linha for pagina in _corpo_por_pagina(documento) for linha in pagina]
    inicio = corpo.index("SUMÁRIO") if "SUMÁRIO" in corpo else 0
    return corpo[inicio : inicio + 60]


# ---------------------------------------------------------------------------
# A regressão do cenário B (SC-904)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("prevista", sorted(PREVISTAS))
@pytest.mark.parametrize("caso", sorted(CONTEUDOS_DE_B))
def test_no_cenario_b_a_previa_pagina_o_corpo_como_o_publicado(caso, prevista):
    """FR-2418: página a página, o corpo normativo é o mesmo — e o número de páginas também."""
    conteudo, autoridade = CONTEUDOS_DE_B[caso](), PREVISTAS[prevista]
    publicado = _corpo_por_pagina(_publicado(conteudo, autoridade))
    previa = _corpo_por_pagina(_previa(conteudo, (autoridade,)))

    assert len(previa) == len(publicado), "a prévia tem de ter as páginas do publicado"
    for numero, (uma, outra) in enumerate(zip(previa, publicado, strict=True), 1):
        assert uma == outra, f"o corpo normativo da página {numero} difere entre prévia e publicado"


@pytest.mark.parametrize("prevista", sorted(PREVISTAS))
@pytest.mark.parametrize("caso", sorted(CONTEUDOS_DE_B))
def test_no_cenario_b_o_sumario_da_previa_diz_as_paginas_do_publicado(caso, prevista):
    conteudo, autoridade = CONTEUDOS_DE_B[caso](), PREVISTAS[prevista]

    assert _sumario(_previa(conteudo, (autoridade,))) == _sumario(_publicado(conteudo, autoridade))


def test_sem_a_reserva_o_cenario_b_volta_a_divergir(monkeypatch):
    """A prova reprova o defeito que existe para pegar: sem a reserva, a última seção não salta."""
    monkeypatch.setattr(pdf, "_reservar_o_fecho", lambda composicao, medir, previstos: None)
    conteudo, autoridade = CONTEUDOS_DE_B["B plana"](), PREVISTAS["a do contrato"]

    previa = _corpo_por_pagina(_previa(conteudo, (autoridade,)))
    publicado = _corpo_por_pagina(_publicado(conteudo, autoridade))

    assert previa != publicado


# ---------------------------------------------------------------------------
# A reserva (FR-2419 a FR-2421)
# ---------------------------------------------------------------------------


def _fecho_real(previsto, conteudo):
    rascunho = pdf.Composicao(metrica=pdf.METRICA_DO_EDITAL)
    pdf._fecho_medido(rascunho, previsto, conteudo, UNIDADE)
    return rascunho.itens


def _reservado(previstos, conteudo):
    composicao = pdf.Composicao(metrica=pdf.METRICA_DO_EDITAL)
    pdf._reservar_o_fecho(
        composicao,
        lambda rascunho, previsto: pdf._fecho_medido(rascunho, previsto, conteudo, UNIDADE),
        previstos,
    )
    return composicao.itens


def _geometria(itens):
    """O que a paginação lê de cada item: tudo, menos o texto — e a régua, que não tem altura."""
    return [
        (item[0], *item[2:]) if item[0] == "texto" else item for item in itens if item[0] != "regua"
    ]


@pytest.mark.parametrize("cenario", ["A", "B"])
def test_a_reserva_tem_a_geometria_do_fecho_real(cenario):
    """FR-2419: a mesma sequência de linhas, alturas, espaços e `junto` — e não um aviso curto."""
    conteudo = congelado(cenario)["content"]
    previsto = AUTORIDADES[cenario]

    assert _geometria(_reservado((previsto,), conteudo)) == _geometria(
        _fecho_real(previsto, conteudo)
    )


def test_nenhuma_linha_da_reserva_e_vazia_onde_o_fecho_tem_texto():
    """A linha `junto` procura a seguinte **com texto**: em branco, a última linha da seção não
    encontraria o fecho, e a decisão de quebra seria outra."""
    conteudo = congelado("A")["content"]
    reais = [i for i in _fecho_real(AUTORIDADES["A"], conteudo) if i[0] == "texto" and i[1]]
    reservadas = [i for i in _reservado((AUTORIDADES["A"],), conteudo) if i[0] == "texto" and i[1]]

    assert len(reservadas) == len(reais)


def test_entre_varias_previstas_reserva_a_mais_alta():
    """FR-2420: a autoridade é escolhida no ato, e a prévia não a conhece."""
    conteudo = congelado("A")["content"]
    baixa, alta = AUTORIDADES["B"], AUTORIDADES["A"]

    assert _geometria(_reservado((baixa, alta), conteudo)) == _geometria(
        _fecho_real(alta, conteudo)
    )
    assert _geometria(_reservado((alta, baixa), conteudo)) == _geometria(
        _fecho_real(alta, conteudo)
    )


def test_sem_prevista_reserva_o_fecho_sem_nome_nem_cargo():
    conteudo = congelado("A")["content"]
    vazio = pdf.AutoridadeSignataria(nome="", cargo="")

    assert _geometria(_reservado((), conteudo)) == _geometria(_fecho_real(vazio, conteudo))


def test_a_previa_nao_imprime_a_autoridade_nem_o_resumo():
    """FR-2421, FR-035 e FR-014: a prevista mede, e não aparece; o resumo não é lido."""
    texto = texto_de(_previa(congelado("A")["content"], (AUTORIDADES["A"],)))

    assert pdf.FECHO_NA_PUBLICACAO in texto
    assert AUTORIDADES["A"].nome not in texto
    assert AUTORIDADES["A"].ato_de_nomeacao not in texto
    assert "Autoridade responsável pelo ato" not in texto
    assert "SHA-256" not in texto
    assert pdf.RESUMO_DE_MEDIDA not in texto


def test_o_publicado_recusa_fecho_previsto():
    with pytest.raises(ValueError, match="não reserva espaço"):
        pdf.render_edital_pdf(
            congelado("A")["content"],
            congelado("A")["hash"],
            pdf.MODO_PUBLICADO,
            unidade=UNIDADE,
            autoridade=AUTORIDADES["A"],
            data_do_ato=pdf.DATA_DE_MEDIDA,
            fechos_previstos=(AUTORIDADES["A"],),
        )
