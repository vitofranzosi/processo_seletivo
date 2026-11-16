"""O que a `178` mudou nos documentos — o arquivo, e nenhuma página (FR-8159, FR-8160).

O "antes" são documentos gravados antes desta feature, e o "depois", os que ela gravou em
`specs/178-documentos-em-pdfa/demonstracao/`:

- os do cenário da auditoria, A e B, que a `069` e a `133` gravaram e a `178` regravou;
- o documento publicado do contrato (`tests/contract/fixtures/documento_publicado_v1.pdf` e `_v2`);
- um exemplar de cada tipo da FR-8150 (`tests/pdfa/exemplares.py`), composto pela `main` em
  `619a4ae0` (`demonstracao/antes/`) e pela `178` (`demonstracao/exemplares/`).

**No Edital, na Retificação e nos relatórios, a prova é byte a byte por página** (SC-2822): o que
cada `/Contents` desenha é idêntico, e os links, os marcadores e os elementos da estrutura são os
mesmos em número (SC-2827). **Na família da divulgação e no comprovante, é o texto** (SC-2824): a
fonte embutida tem outras larguras em "í", "ª", "º", e a linha pode quebrar noutro ponto — mas não
muda uma palavra.

Todos comparam arquivos gravados, e não composições de agora: são evidência do que a `178` fez, e
não mudam quando outra feature mudar a composição. Que a composição de agora ainda é conforme é de
`test_conformidade_pdfa.py`.
"""

import re

import pytest

from tests.interface.test_fluxo import texto_de_pdf_bytes
from tests.pdfa import leitura
from tests.unit.publicacoes.test_itens_do_documento import RAIZ

ESPECIFICACOES = RAIZ / "specs"
DEMONSTRACAO = ESPECIFICACOES / "178-documentos-em-pdfa" / "demonstracao"
CONTRATO = RAIZ / "backend" / "tests" / "contract" / "fixtures"

# (antes, depois) dos documentos cuja página não pode mudar.
MESMA_PAGINA = {
    "A-plana": (
        ESPECIFICACOES / "069-edital-linguagem-simples" / "demonstracao" / "A-plana-069.pdf",
        DEMONSTRACAO / "A-plana-178.pdf",
    ),
    "A-publicado": (
        ESPECIFICACOES / "069-edital-linguagem-simples" / "demonstracao" / "A-publicado-069.pdf",
        DEMONSTRACAO / "A-publicado-178.pdf",
    ),
    **{
        nome: (
            ESPECIFICACOES / "133-jornada-sem-ato-errado" / "demonstracao" / f"{nome}-133.pdf",
            DEMONSTRACAO / f"{nome}-178.pdf",
        )
        for nome in ("B-plana", "B-publicado", "B-variante")
    },
    "contrato": (
        CONTRATO / "documento_publicado_v1.pdf",
        CONTRATO / "documento_publicado_v2.pdf",
    ),
    **{
        nome: (DEMONSTRACAO / "antes" / f"{nome}.pdf", DEMONSTRACAO / "exemplares" / f"{nome}.pdf")
        for nome in ("edital", "retificacao", "relatorio-do-edital", "relatorio-consolidado")
    },
}

# Os que embutem a fonte agora, e cuja linha pode quebrar noutro ponto.
MESMO_TEXTO = ("comprovante", "resultado", "inscricoes", "convocados", "agenda")


def _par(antes, depois):
    return antes.read_bytes(), depois.read_bytes()


@pytest.mark.parametrize("nome", sorted(MESMA_PAGINA))
def test_nenhuma_pagina_muda(nome):
    """SC-2822: cada página desenha os mesmos bytes."""
    antes, depois = _par(*MESMA_PAGINA[nome])
    assert leitura.fluxos_das_paginas(depois) == leitura.fluxos_das_paginas(antes)


@pytest.mark.parametrize("nome", sorted(MESMA_PAGINA))
def test_links_marcadores_e_estrutura_ficam(nome):
    """SC-2827: o que a conversão da prova de conceito destruiu, aqui continua — e imprimível."""
    antes, depois = _par(*MESMA_PAGINA[nome])
    for marca in (b"/Subtype /Link", b"/Type /Outlines", b"/Parent", b"/Type /StructElem"):
        assert leitura.contagem(depois, marca) == leitura.contagem(antes, marca), marca
    assert all(b"/F 4 " in anotacao for anotacao in leitura.anotacoes(depois))
    # O catálogo é o de antes, com as duas entradas da conformidade e nada mais: idioma, título na
    # janela, marcadores e marcação continuam como estavam.
    sem_a_conformidade = re.sub(
        rb" /Metadata \d+ 0 R /OutputIntents \[.*\]", b"", leitura.catalogo(depois)
    )
    assert sem_a_conformidade == leitura.catalogo(antes)


@pytest.mark.parametrize("nome", MESMO_TEXTO)
def test_o_texto_e_o_mesmo_palavra_a_palavra(nome):
    """SC-2824, FR-8160."""
    antes, depois = _par(
        DEMONSTRACAO / "antes" / f"{nome}.pdf", DEMONSTRACAO / "exemplares" / f"{nome}.pdf"
    )
    assert texto_de_pdf_bytes(depois).split() == texto_de_pdf_bytes(antes).split()
    assert len(leitura.paginas(depois)) == len(leitura.paginas(antes))


@pytest.mark.parametrize(
    "depois",
    [par[1] for par in MESMA_PAGINA.values()]
    + [DEMONSTRACAO / "exemplares" / f"{nome}.pdf" for nome in MESMO_TEXTO],
    ids=lambda caminho: caminho.name,
)
def test_so_o_depois_declara_pdfa(depois):
    assert b"<pdfaid:part>2</pdfaid:part>" in depois.read_bytes()


@pytest.mark.parametrize(
    "antes",
    [par[0] for par in MESMA_PAGINA.values()]
    + [DEMONSTRACAO / "antes" / f"{nome}.pdf" for nome in MESMO_TEXTO],
    ids=lambda caminho: caminho.name,
)
def test_o_antes_nao_declarava(antes):
    assert b"pdfaid" not in antes.read_bytes()
