"""Os conteúdos publicados na auditoria do PDF de 08/10/2026, compostos como a auditoria os compôs.

A `065` prendeu os bytes desses documentos; a `067` os muda de propósito (ED-02, ED-03, ED-12) e
precisa compô-los em vários testes — com o mesmo contexto do ato, para que a diferença entre o PDF
da auditoria e o de agora seja só a da composição.
"""

import copy
import json
from datetime import date

from processo_seletivo.editais.domain import secoes
from processo_seletivo.publicacoes.infrastructure import pdf
from tests.unit.publicacoes.test_itens_do_documento import AUTORIDADES, CONGELADOS, DOCUMENTOS

UNIDADE = pdf.UnidadeDoAto(
    cabecalho=("Centro de Referência em Formação", "e em Educação a Distância"),
    local="Vitória (ES)",
    sigla="Cefor",
)
DATA_DO_ATO = date(2026, 10, 8)


def congelado(cenario):
    """`{"content": …, "hash": …}` do cenário, como a auditoria o gravou."""
    return json.loads((CONGELADOS / f"{cenario}-conteudo-publicado.json").read_text("utf-8"))


def composto(cenario, conteudo=None, *, modo=pdf.MODO_PUBLICADO):
    """O documento do cenário composto agora — com outro conteúdo, se for dado."""
    dados = congelado(cenario)
    kwargs = {"unidade": UNIDADE}
    if modo == pdf.MODO_PUBLICADO:
        kwargs.update(autoridade=AUTORIDADES[cenario], data_do_ato=DATA_DO_ATO)
    return pdf.render_edital_pdf(
        conteudo if conteudo is not None else dados["content"], dados["hash"], modo, **kwargs
    )


def publicado_na_auditoria(cenario):
    """Os bytes que a auditoria gravou — evidência datada, que nenhum teste regrava."""
    return (DOCUMENTOS / f"{cenario}-publicado.pdf").read_bytes()


def levado_ao_catalogo_novo(conteudo):
    """O conteúdo com o título e a ordem das seções do catálogo da `069`, e nada mais mudado (T038).

    É o que um Edital com o mesmo texto e o mesmo dado teria se fosse submetido depois da `069`: o
    snapshot copia o título e a ordem do catálogo na submissão, e as chaves e o texto ficam.
    """
    novo = copy.deepcopy(conteudo)
    for secao in novo["sections"]:
        catalogada = secoes.POR_CHAVE[secao["key"]]
        secao["title"], secao["order"] = catalogada.title, catalogada.order
    novo["sections"].sort(key=lambda secao: secao["order"])
    return novo


def por_perguntas(cenario, conteudo=None, *, modo=pdf.MODO_PUBLICADO):
    """O documento do cenário levado ao catálogo novo: a apresentação por perguntas."""
    dados = congelado(cenario)
    return composto(cenario, levado_ao_catalogo_novo(conteudo or dados["content"]), modo=modo)


def variante_de_b():
    """B no catálogo novo, com os suplentes dos tutores presenciais diferentes (069, R-009).

    O corte difere entre os grupos e o resto é igual: é o caso que exercita a partilha parcial — o
    comum uma vez, a unidade do corte inteira em cada grupo.
    """
    conteudo = levado_ao_catalogo_novo(congelado("B")["content"])
    for perfil in conteudo["profiles"]:
        if perfil["code"].startswith("TP-"):
            perfil["classificationMilestones"][0]["cutRule"]["surplusCount"] = 3
    return conteudo
