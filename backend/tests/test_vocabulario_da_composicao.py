"""Todo termo do vocabulário interno se define no primeiro uso da tela (030, FR-424, SC-141).

**Irmão de `test_vocabulario_do_corte.py` e `test_vocabulario_da_ocupacao.py`**, com a mesma
mecânica e o sinal invertido: aqueles afirmam a **ausência** de uma palavra que atravessaria uma
fronteira de domínio; este afirma a **presença** de uma definição onde a palavra aparece.

**Por que o sinal inverte.** Recorte, geração e faixa são termos deste domínio, e são precisos — o
problema nunca foi a palavra, foi encontrá-la pela primeira vez numa tela que a usa como se fosse
sabida. A auditoria mediu o custo disso: a prosa do sistema é abundante e precisa, e ainda assim o
primeiro contato é caro, porque a explicação está noutro lugar que não o ponto da decisão.

**A regra verificável, e ela é estreita de propósito**: a primeira ocorrência do termo no texto
visível da tela está dentro de um `<dfn>`, e o que vem logo depois é uma definição — uma frase com
cópula, e não uma repetição do termo. Não se verifica se a definição é boa: isso é leitura humana,
e é o que a revisão de código vê. O que se verifica é que ela existe, e que está no primeiro uso.

**Comentário não é afirmação**, como nos irmãos: a varredura lê o template sem `{% comment %}` —
e, aqui, também sem as tags e variáveis do Django, que não chegam a olho nenhum. Sem isso, um
`{% if acao == "faixa" %}` contaria como uso do termo, e a tela seria cobrada por uma palavra que
ela não escreve.

**A contagem veio de varredura, e não de memória.** A primeira escrita destas tarefas nomeava três
telas — as que se lembra de cabeça. São dez.
"""

import re
import unicodedata
from pathlib import Path

import pytest

TEMPLATES = Path(__file__).resolve().parents[1] / "processo_seletivo/interface/templates/interface"

#: As onze telas que usam os termos em texto visível. Literal, e não descoberto por varredura: uma
#: lista calculada passaria a ignorar a tela que deixasse de usar o termo — e o que interessa é
#: que a tela que o usa o defina, não que a lista se conserte sozinha.
TELAS = (
    "compor_classificacao.html",
    "compor_perfis.html",
    "corte.html",
    "corte_historico.html",
    "ordenacao.html",
    "ocupacao.html",
    "ocupacao_historico.html",
    "sorteio.html",
    "convocacao.html",
    "convocacao_historico.html",
    # A tela da exportação de matrículas (031). **Entra na lista no mesmo commit em que nasce**: a
    # lista é literal e não `glob`, por decisão escrita acima, e sem esta linha a tela escaparia da
    # regra em silêncio — ninguém veria falha nenhuma.
    "matriculas.html",
)

#: O termo e o que o casa, singular e plural. Sem acento no padrão porque a comparação normaliza —
#: `geração` e `geracao` são a mesma palavra para quem lê, e duas grafias no padrão só produziriam
#: uma delas esquecida.
TERMOS = {
    "recorte": r"\brecorte",
    "geração": r"\bgerac",
    "faixa": r"\bfaixa",
}

_COMENTARIO = re.compile(r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}", re.S)
#: O `<title>` da página, que o navegador põe na aba e a tela não desenha. Fora da varredura: a
#: FR-424 fala do primeiro uso **na tela**, e um título de aba não tem onde caber uma definição —
#: exigi-la ali produziria a definição no lugar em que ela menos serve.
_TITULO = re.compile(r"\{%\s*block\s+titulo\s*%\}.*?\{%\s*endblock\s*%\}", re.S)
_TAG_DO_DJANGO = re.compile(r"\{%.*?%\}|\{\{.*?\}\}", re.S)
_DFN = re.compile(r"<dfn\b[^>]*>(.*?)</dfn>", re.S | re.I)
_MARCACAO = re.compile(r"<[^>]+>", re.S)
#: O `{% include %}` de um parcial. A varredura **desce nele**, e a razão custou uma leitura vazia:
#: a ajuda da etapa de Classificação saiu de `compor_classificacao.html` para um arquivo próprio, e
#: com ela saíram as definições — a varredura passou a não achar termo nenhum naquela tela e a
#: pular os três casos dela, aprovando calada. O que a FR-424 promete é sobre a **tela**, e a tela
#: é o que o navegador monta.
_INCLUDE = re.compile(r'\{%\s*include\s+"interface/([^"]+)"[^%]*%\}')
#: A cópula que separa definir de repetir: `é`, `são`, `chama-se`.
#:
#: **Com acento, e sobre o texto original.** A comparação do termo normaliza acento de propósito —
#: `geração` e `geracao` são a mesma palavra para quem lê —, mas aqui a normalização destruiria a
#: verificação: sem acento, `é` vira `e`, e a conjunção mais comum do português passaria por
#: cópula. Qualquer frase seguinte satisfaria a asserção, e o guardião aprovaria vazio.
_COPULA = re.compile(r"\b(é|são|chama-se)\b")

ABRE, FECHA = "«", "»"


def _sem_acento(texto):
    return "".join(
        letra
        for letra in unicodedata.normalize("NFD", texto)
        if unicodedata.category(letra) != "Mn"
    ).lower()


def _montada(caminho, vistos=None):
    """A fonte da tela com os parciais dela no lugar, **na ordem em que a página os monta**.

    A ordem é o que importa: o bloco de ajuda da Classificação é incluído antes do laço que desenha
    os cartões, e por isso a definição precede o uso. Trocar a ordem aqui inverteria a resposta.

    `vistos` guarda contra recursão: um parcial que se incluísse de volta travaria a varredura.
    """
    vistos = set() if vistos is None else vistos
    if caminho.name in vistos:
        return ""
    vistos.add(caminho.name)
    return _INCLUDE.sub(
        lambda achado: _montada(TEMPLATES / achado.group(1), vistos), caminho.read_text()
    )


def visivel(caminho):
    """O texto que a tela de fato mostra, com as definições marcadas por «…»."""
    bruto = _TITULO.sub(" ", _COMENTARIO.sub(" ", _montada(caminho)))
    bruto = _DFN.sub(lambda achado: f"{ABRE}{achado.group(1)}{FECHA}", bruto)
    bruto = _TAG_DO_DJANGO.sub(" ", bruto)
    return _MARCACAO.sub(" ", bruto)


def _definicoes(texto):
    """Os trechos `«…»` e onde cada um começa e termina."""
    return [
        (achado.start(), achado.end()) for achado in re.finditer(f"{ABRE}[^{FECHA}]*{FECHA}", texto)
    ]


CASOS = [(tela, termo) for tela in TELAS for termo in TERMOS]


@pytest.mark.parametrize(("tela", "termo"), CASOS, ids=lambda item: item)
def test_o_termo_usado_pela_tela_se_define_no_primeiro_uso(tela, termo):
    texto = visivel(TEMPLATES / tela)
    sem_acento = _sem_acento(texto)
    primeira = re.search(TERMOS[termo], sem_acento)
    if primeira is None:
        pytest.skip(f"{tela} não usa «{termo}» em texto visível")

    dentro_de_definicao = any(
        inicio <= primeira.start() < fim for inicio, fim in _definicoes(texto)
    )
    assert dentro_de_definicao, (
        f"{tela} usa «{termo}» pela primeira vez sem defini-lo: "
        f"…{texto[max(0, primeira.start() - 60) : primeira.start() + 90].strip()}…"
    )

    _, fim = next(
        (par for par in _definicoes(texto) if par[0] <= primeira.start() < par[1]),
    )
    seguinte = texto[fim : fim + 120]
    assert _COPULA.search(seguinte), (
        f"{tela} marca «{termo}» como definição e não define: o que vem depois é "
        f"«{texto[fim : fim + 90].strip()}»"
    )
