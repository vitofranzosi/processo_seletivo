"""056 — o polish do assistente de composição.

As medidas de tela — 80 px de stepper, o h2 de Perfis em y ≤ 440, a página do Conteúdo — estão em
`specs/056-polish-assistente-de-composicao/verificacao.md`, tiradas na página renderizada. O que
fica aqui é o que as produz: a regra na folha e a marcação no template. Nada disso muda
comportamento, e por isso nenhum outro teste perceberia se voltasse ao que era.
"""

import re
from pathlib import Path

import pytest
from django.urls import reverse

from tests.interface.test_acessibilidade import FONTE, sem_prosa
from tests.interface.test_conteudo_da_054 import composto  # noqa: F401

RAIZ = Path(__file__).resolve().parents[2] / "processo_seletivo"
GESTAO = RAIZ / "interface/templates/interface"
FOLHA = sem_prosa(FONTE)


def regra(seletor, folha=FOLHA):
    """O corpo da regra cujo seletor é exatamente `seletor`, sem espaços, ou `None`."""
    achado = re.search(rf"(?:^|[}}\n])[ \t]*{re.escape(seletor)}\{{([^}}]*)\}}", folha)
    return achado.group(1).replace("\n", "").replace(" ", "") if achado else None


# --- F1 — o stepper numa linha (FR-1020 a FR-1022) ---------------------------------------------


def test_o_stepper_e_grade_de_colunas_iguais():
    """`flex:1 1 160px` com quebra fazia 7 + 2, com as duas últimas esticadas a 613 px.

    A grade quebra em colunas do mesmo tamanho em todas as linhas (FR-1021), e a 1280 px cabe as
    nove numa só (FR-1020): 7,5 rem por coluna, contra 131 px disponíveis.
    """
    corpo = regra(".assistente")
    assert corpo and "display:grid" in corpo
    assert "repeat(auto-fit,minmax(7.5rem,1fr))" in corpo
    assert "flex-wrap" not in corpo
    assert "flex:" not in (regra(".assistente li") or ""), "a base de 160 px volta a quebrar 7 + 2"


def test_a_situacao_da_etapa_continua_em_texto():
    """FR-1022: a situação é escrita, e não só cor. Sai a caixa-alta, e não a palavra."""
    compor = (GESTAO / "compor_base.html").read_text()
    assert '<span class="estado">etapa atual</span>' in compor
    assert '<span class="estado">{{ passo.rotulo_estado }}</span>' in compor
    assert 'aria-current="step"' in compor
    assert "text-transform" not in (regra(".assistente .estado") or "")
    # A marca vazada da etapa pronta para revisar continua: a distinção não pode ser só de cor.
    assert "border:2px" in (regra(".assistente .a-pronta .numero") or "")


# --- F3 — o Conteúdo do Edital (FR-1029 a FR-1032) ---------------------------------------------


@pytest.fixture
def conteudo(client, composto):  # noqa: F811
    """A etapa com três seções escritas e as demais vazias."""
    return client.get(
        reverse("interface:compor-etapa", args=[composto.id, "conteudo"])
    ).content.decode()


def _secao(html, chave):
    achado = re.search(rf'<fieldset[^>]*data-secao="{chave}".*?</fieldset>', html, re.S)
    assert achado, chave
    return achado.group(0)


@pytest.mark.django_db
@pytest.mark.integration
def test_a_secao_vazia_nasce_com_duas_linhas_e_a_escrita_com_cinco(conteudo):
    """FR-1030: a vazia do tamanho da preenchida era a maior parte dos 4.876 px da página."""
    assert re.search(r'name="secao-certificado" rows="2"', _secao(conteudo, "certificado"))
    assert re.search(r'name="secao-publico-alvo" rows="5"', _secao(conteudo, "publico-alvo"))


@pytest.mark.django_db
@pytest.mark.integration
def test_a_marca_de_secao_vazia_continua_no_nome_do_campo(conteudo):
    """FR-1031 e D-008: muda o desenho, e não o texto — ela fecha o nome acessível do campo."""
    secao = _secao(conteudo, "certificado")
    assert "(vazia — não sai no documento)</span></legend>" in secao
    assert 'aria-labelledby="titulo-certificado"' in secao
    regras = (GESTAO / "compor_conteudo.html").read_text()
    assert ".secao>legend [data-estado-texto]{text-transform:none" in regras


@pytest.mark.django_db
@pytest.mark.integration
def test_a_secao_gerada_nao_tem_caixa_e_o_caminho_fica_na_frase(conteudo):
    """FR-1032: sem moldura de campo, e o link no fim da frase, e não num parágrafo só dele."""
    secao = _secao(conteudo, "cronograma")
    assert "Não há texto a redigir: alterar aquele conteúdo altera esta seção." in secao
    paragrafo = re.search(r'<p class="ajuda">(.*?)</p>', secao, re.S).group(1)
    assert "Ir para Cronograma</a>" in paragrafo
    regras = (GESTAO / "compor_conteudo.html").read_text()
    assert "fieldset.secao.gerada{border:0;" in regras
    assert "fieldset.secao{max-width:calc(var(--leitura)" in regras
