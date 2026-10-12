"""A métrica com que a composição mede o texto passa a ser parâmetro (069, R-005, T005).

O Edital vai embutir a fonte e medir pelas larguras dela; o comprovante e a divulgação continuam
com a Helvetica de hoje, byte a byte (FR-1383). As duas coisas só convivem se a medida for da
**composição**, e não de uma função global: `Composicao()` sem métrica mede como sempre mediu, e
`Composicao(metrica=…)` mede pela que recebe — na quebra (`escrever`), na justificação, na posição
de linha centralizada ou à direita, nas colunas e nas células das tabelas.
"""

import pytest

from processo_seletivo.publicacoes.infrastructure import pdf
from tests.unit.publicacoes.cenarios_da_auditoria import congelado


class _Larga(pdf.Metrica):
    """Uma métrica que mede todo caractere como 1000 — o dobro de quase tudo na Helvetica."""

    def largura(self, texto, tamanho, fonte=pdf.REGULAR):
        return len(str(texto)) * tamanho


def test_sem_metrica_a_composicao_mede_pela_helvetica_de_hoje():
    composicao = pdf.Composicao()

    assert composicao.metrica is pdf.HELVETICA
    assert pdf.HELVETICA.largura("M", 1000) == 833
    assert pdf.HELVETICA.largura("i", 1000) == 222
    assert pdf.HELVETICA.largura(" ", 1000) == 278
    # A função de módulo continua a mesma medida: os testes de largura e o comprovante a leem.
    for texto in ("Edital nº 91/2026 — Informações", "ÍNDICE ª º", "—"):
        for fonte in (pdf.REGULAR, pdf.NEGRITO):
            assert pdf.HELVETICA.largura(texto, 10.5, fonte) == pdf.largura(texto, 10.5, fonte)


def test_a_quebra_de_linha_segue_a_metrica_da_composicao():
    texto = "palavra " * 40
    helvetica, larga = pdf.Composicao(), pdf.Composicao(metrica=_Larga())

    helvetica.escrever(texto)
    larga.escrever(texto)

    # Com cada caractere medindo o dobro, cabem menos palavras por linha, e o parágrafo tem mais
    # linhas — a quebra mediu pela métrica da composição, e não pela global.
    assert len(larga.itens) > len(helvetica.itens)
    util = pdf.LARGURA - 2 * pdf.MARGEM
    for item in larga.itens:
        assert _Larga().largura(item[1], item[3]) <= util + 0.01


def test_a_posicao_e_a_justificacao_seguem_a_metrica_da_composicao():
    larga = pdf.Composicao(metrica=_Larga())
    larga.escrever("Centro", alinhamento=pdf.CENTRO)
    larga.escrever("Direita", alinhamento=pdf.DIREITA)
    # Palavras de uma letra: muitos espaços, e a folga de cada um fica abaixo do teto da
    # justificação, que não estica espaço além de 35% do corpo.
    larga.escrever("a " * 80, justificar=True)

    (linhas, _), *_ = larga.paginar()
    util = pdf.LARGURA - 2 * pdf.MARGEM
    centro, direita, justificada = linhas[0], linhas[1], linhas[2]
    tamanho = pdf.CORPO_TEXTO

    assert centro[3] == pytest.approx(pdf.MARGEM + (util - 6 * tamanho) / 2)
    assert direita[3] == pytest.approx(pdf.MARGEM + util - 7 * tamanho)
    # A folga distribuída pelos espaços é a que falta à linha **pela métrica larga** para alcançar a
    # margem — pela Helvetica, ela seria outra.
    espacos = justificada[0].count(" ")
    folga = util - _Larga().largura(justificada[0], tamanho)
    assert justificada[5] == pytest.approx(folga / espacos)
    pela_helvetica = (util - pdf.HELVETICA.largura(justificada[0], tamanho)) / espacos
    assert justificada[5] != pytest.approx(pela_helvetica)


def test_as_colunas_e_as_celulas_seguem_a_metrica_da_composicao():
    helvetica, larga = pdf.Composicao(), pdf.Composicao(metrica=_Larga())
    for composicao in (helvetica, larga):
        pdf._tabela(
            composicao, ["Código", "Localidade"], [["TP-01", "Aracruz"], ["TP-02", "Serra"]]
        )

    bordas = [item[1] for item in helvetica.itens if item[0] == "abre_tabela"][0]
    bordas_largas = [item[1] for item in larga.itens if item[0] == "abre_tabela"][0]
    assert bordas != bordas_largas


@pytest.mark.parametrize("cenario", ["A", "B"])
def test_a_metrica_padrao_explicita_compoe_os_mesmos_itens(cenario):
    """Nomear a Helvetica não muda nada: a composição dos cenários da auditoria é a mesma."""
    snapshot = pdf._grafado(congelado(cenario)["content"], previa=False)
    padrao, explicita = pdf.Composicao(), pdf.Composicao(metrica=pdf.HELVETICA)

    pdf._secoes(padrao, snapshot)
    pdf._secoes(explicita, snapshot)

    assert padrao.itens == explicita.itens
    assert padrao.paginar() == explicita.paginar()
