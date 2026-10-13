"""Os itens que o documento imprime, ditos pela mesma regra que o compõe (065, D-004, FR-1205).

A conferência das remissões precisa saber quais números o documento imprime — seções, subseções de
Perfis e de Etapas, subseções comuns de atribuições, tabelas. Reescrever essa contagem na validação
seria a segunda regra de numeração que a `054` (FR-985) existe para não ter. Por isso a função mora
no compositor, e este guardião compõe o documento **de verdade** e compara: mudar a composição sem
mudar a função reprova aqui.
"""

import json
import re
from pathlib import Path

import pytest

from processo_seletivo.editais.domain import secoes
from processo_seletivo.publicacoes.infrastructure import apresentacao, pdf

RAIZ = Path(__file__).resolve().parents[4]
CONGELADOS = RAIZ / "doc" / "auditoria-edital-pdf-2026-10-08" / "snapshots"


def _congelado(nome):
    return json.loads((CONGELADOS / nome).read_text(encoding="utf-8"))["content"]


def _secoes(*, catalogo=secoes.CATALOGO_DA_054, **redigidas):
    """Pelo catálogo da `054` por padrão — a apresentação plana; os casos "por perguntas" pedem o da
    `069` (R-003), e o guardião compara as duas com a composição de verdade."""
    return [
        {
            "id": f"00000000-0000-0000-0000-{secao.order:012d}",
            "key": secao.key,
            "title": secao.title,
            "order": secao.order,
            "type": secao.type,
            **(
                {"source": secao.source}
                if secao.gerada
                else {"content": redigidas.get(secao.key.replace("-", "_"), "")}
            ),
        }
        for secao in catalogo
    ]


def _perfil(codigo, *, quadro=True, modalidades=True, atribuicoes=""):
    modalidade = {"id": f"m-{codigo}", "code": "AC", "name": "Ampla concorrência"}
    return {
        "id": f"p-{codigo}",
        "code": codigo,
        "name": f"Perfil {codigo}",
        "immediateVacancies": 1,
        "reserveType": "NONE",
        "reserveLimit": None,
        "locality": "Vitória",
        "duties": atribuicoes,
        "requirements": [],
        "competitionModalities": [modalidade] if modalidades else [],
        "vacancyTable": (
            [{"id": f"l-{codigo}", "modalityId": None, "immediateVacancies": 1}] if quadro else []
        ),
        "classificationMilestones": [],
    }


EVENTO = {
    "id": "e-1",
    "type": "Inscrições",
    "description": "Período de inscrições",
    "startAt": "2026-10-13T09:00:00-03:00",
    "endAt": "2026-10-30T23:59:00-03:00",
    "order": 1,
    "location": "",
}


def _etapa(ordem):
    return {"id": f"s-{ordem}", "name": f"Etapa {ordem}", "order": ordem}


def _sintetico(
    perfis, *, etapas=(), eventos=(EVENTO,), catalogo=secoes.CATALOGO_DA_054, **redigidas
):
    return {
        "number": "1",
        "year": 2026,
        "title": "Edital",
        "sections": _secoes(catalogo=catalogo, **redigidas),
        "profiles": list(perfis),
        "schedule": list(eventos),
        "stages": list(etapas),
        "documentRequirements": [],
        "attachments": [],
    }


CASOS = {
    "cenario A da auditoria": lambda: _congelado("A-conteudo-publicado.json"),
    "cenario B da auditoria": lambda: _congelado("B-conteudo-publicado.json"),
    "um Perfil só": lambda: _sintetico([_perfil("P1")]),
    "Perfil sem quadro": lambda: _sintetico([_perfil("P1"), _perfil("P2", quadro=False)]),
    "Perfil sem modalidade": lambda: _sintetico(
        [_perfil("P1"), _perfil("P2", modalidades=False, quadro=False)]
    ),
    "sem Etapa e sem Cronograma": lambda: _sintetico([_perfil("P1"), _perfil("P2")], eventos=()),
    "com Etapas": lambda: _sintetico([_perfil("P1")], etapas=[_etapa(1), _etapa(2), _etapa(3)]),
    "atribuições comuns": lambda: _sintetico(
        [
            _perfil("TP-01", atribuicoes="Mediar.\nAcompanhar."),
            _perfil("TP-02", atribuicoes="Mediar.\nAcompanhar."),
            _perfil("TD-01", atribuicoes="Corrigir."),
            _perfil("TD-02", atribuicoes="Corrigir."),
            _perfil("CO-01", atribuicoes="Coordenar."),
        ],
        etapas=[_etapa(1)],
        inscricao="A inscrição é gratuita.",
    ),
    "seções textuais intercaladas": lambda: _sintetico(
        [_perfil("P1"), _perfil("P2")],
        etapas=[_etapa(1)],
        apresentacao="A Diretora torna público.",
        publico_alvo="Graduados.",
        recursos="Cabe recurso.",
    ),
}


def levado_ao_catalogo_novo(conteudo):
    # Adiado: `cenarios_da_auditoria` importa deste módulo.
    from tests.unit.publicacoes.cenarios_da_auditoria import levado_ao_catalogo_novo as levar

    return levar(conteudo)


# Os mesmos casos na apresentação por perguntas (069, R-003): seções reunidas, subseções N.k
# textuais e geradas, e as Etapas como subseções da seleção.
POR_PERGUNTAS = {
    "por perguntas: cenario A": lambda: levado_ao_catalogo_novo(
        _congelado("A-conteudo-publicado.json")
    ),
    "por perguntas: cenario B": lambda: levado_ao_catalogo_novo(
        _congelado("B-conteudo-publicado.json")
    ),
    "por perguntas: um Perfil só": lambda: _sintetico(
        [_perfil("P1")], catalogo=secoes.CATALOGO_DA_069
    ),
    "por perguntas: com Etapas": lambda: _sintetico(
        [_perfil("P1")], etapas=[_etapa(1), _etapa(2)], catalogo=secoes.CATALOGO_DA_069
    ),
    "por perguntas: seções textuais reunidas": lambda: _sintetico(
        [_perfil("P1", atribuicoes="Mediar."), _perfil("P2", atribuicoes="Corrigir.")],
        etapas=[_etapa(1)],
        catalogo=secoes.CATALOGO_DA_069,
        apresentacao="A Diretora torna público.",
        publico_alvo="Graduados.",
        requisitos_gerais="Ter disponibilidade.",
        inscricao="A inscrição é gratuita.",
        atendimento_pcd="Atendimento especializado.",
        classificacao="A seleção tem uma etapa.",
        verificacao_autodeclaracao="A comissão verifica.",
        matricula="A matrícula é presencial.",
        acesso_ao_curso="O curso é a distância.",
        recursos="Cabe recurso.",
    ),
}
CASOS.update(POR_PERGUNTAS)


def _colhidos(snapshot):
    """Os números que a composição de verdade escreve: seções, subseções e legendas de tabela.

    Pela apresentação do snapshot (069): a plana pelo `_secoes`, a por perguntas pelo compositor
    dela. O sumário fica de fora, porque não é negrito: os títulos colhidos são os do corpo.
    """
    composicao = pdf.Composicao()
    grafado = pdf._grafado(snapshot, previa=False)
    if pdf.por_perguntas(grafado):
        apresentacao.compor(composicao, grafado)
    else:
        pdf._secoes(composicao, grafado)
    secoes_, subsecoes, tabelas = set(), set(), []
    for item in composicao.itens:
        if item[0] != "texto" or item[2] != pdf.NEGRITO or not item[1]:
            continue
        texto = item[1]
        if encontrado := re.match(r"^(\d+)\. \S", texto):
            secoes_.add(encontrado[1])
        if encontrado := re.match(r"^(\d+\.\d+) ", texto):
            subsecoes.add(encontrado[1])
        if encontrado := re.match(r"^Tabela (\d+) — ", texto):
            tabelas.append(int(encontrado[1]))
    return secoes_, subsecoes, tabelas


@pytest.mark.parametrize("caso", sorted(CASOS))
def test_os_itens_sao_os_que_a_composicao_escreve(caso):
    snapshot = CASOS[caso]()
    secoes_, subsecoes, tabelas = _colhidos(snapshot)
    itens = pdf.itens_do_documento(snapshot)

    assert {item.numero for item in itens if item.natureza == "secao"} == secoes_
    assert {item.numero for item in itens if item.natureza != "secao"} == subsecoes
    assert tabelas == list(range(1, len(tabelas) + 1)), "as legendas são contíguas"
    assert pdf.tabelas_do_documento(snapshot) == len(tabelas)


def test_cada_item_tem_natureza_e_descricao():
    itens = pdf.itens_do_documento(CASOS["atribuições comuns"]())
    naturezas = {item.natureza for item in itens}
    assert naturezas == {"secao", "perfil", "atribuicoes_comuns", "etapa"}
    perfil = next(item for item in itens if item.natureza == "perfil")
    assert perfil.descricao == "TP-01 — Perfil TP-01"
    etapa = next(item for item in itens if item.natureza == "etapa")
    assert etapa.descricao == "Etapa 1"
    comum = next(item for item in itens if item.natureza == "atribuicoes_comuns")
    assert "TP-01" in comum.descricao and "TP-02" in comum.descricao


def test_secao_que_nao_sai_nao_tem_item():
    snapshot = _sintetico([_perfil("P1")], etapas=())
    numeros = pdf.numeracao(snapshot)
    assert numeros["etapas"] is None
    assert not [item for item in pdf.itens_do_documento(snapshot) if item.natureza == "etapa"]


def test_a_funcao_nao_muda_o_snapshot():
    snapshot = CASOS["cenario B da auditoria"]()
    antes = json.dumps(snapshot, sort_keys=True)
    pdf.itens_do_documento(snapshot)
    pdf.tabelas_do_documento(snapshot)
    assert json.dumps(snapshot, sort_keys=True) == antes


# --- o documento não muda (FR-1219, SC-466, D-014) --------------------------------------------
#
# **Até a `067`, que o muda de propósito** (ED-02, ED-03, ED-12). Os PDFs da auditoria continuam
# onde estão, e não são regravados: são evidência de uma auditoria datada, e regravá-los apagaria
# o que ela viu. O que mudou entre a auditoria e a `067` é preso, trecho a trecho, por
# `test_documento_da_auditoria_depois_da_067.py` (D-010 dela), contra os PDFs que ela gravou.
#
# **E depois a `068`**, que o muda de novo, de propósito (ED-04, ED-11): os bytes esperados passam
# a ser os de `specs/068-…/demonstracao/`; os da `067` ficam como evidência dela, e o que a `068`
# mudou é preso por `test_documento_da_auditoria_depois_da_068.py` e, Perfil a Perfil, por
# `test_equivalencia_da_consolidacao.py`.
#
# **E depois a `069`**, que muda a redação, a fonte, a hierarquia e a navegação: os bytes esperados
# passam a ser os de `specs/069-…/demonstracao/`, e os da `068` ficam como evidência dela. O que a
# `069` mudou é preso por `test_documento_da_auditoria_depois_da_069.py`.

DOCUMENTOS = RAIZ / "doc" / "auditoria-edital-pdf-2026-10-08" / "pdf"
ESPERADOS = RAIZ / "specs" / "069-edital-linguagem-simples" / "demonstracao"
CARGO = "Diretora-Geral do Centro de Referência em Formação e em Educação a Distância"
# O contexto do ato com que cada cenário foi publicado na auditoria de 08/10/2026: A com nome e ato
# de nomeação fictícios, B só com o cargo, como o registro inicial do Cefor está hoje.
AUTORIDADES = {
    "A": pdf.AutoridadeSignataria(
        nome="Fulana de Tal",
        cargo=CARGO,
        ato_de_nomeacao="Portaria nº 0000, de 2 de janeiro de 2026 (fictícia)",
    ),
    "B": pdf.AutoridadeSignataria(nome="", cargo=CARGO),
}


@pytest.mark.parametrize("cenario", ["A", "B"])
def test_o_documento_da_auditoria_sai_com_os_bytes_esperados_depois_da_069(cenario):
    from datetime import date

    congelado = json.loads(
        (CONGELADOS / f"{cenario}-conteudo-publicado.json").read_text(encoding="utf-8")
    )
    documento = pdf.render_edital_pdf(
        congelado["content"],
        congelado["hash"],
        unidade=pdf.UnidadeDoAto(
            cabecalho=("Centro de Referência em Formação", "e em Educação a Distância"),
            local="Vitória (ES)",
            # A sigla da Unidade, que o anúncio em caixa alta preserva (069, FR-1377).
            sigla="Cefor",
        ),
        autoridade=AUTORIDADES[cenario],
        data_do_ato=date(2026, 10, 8),
    )
    assert documento == (ESPERADOS / f"{cenario}-plana-069.pdf").read_bytes()
