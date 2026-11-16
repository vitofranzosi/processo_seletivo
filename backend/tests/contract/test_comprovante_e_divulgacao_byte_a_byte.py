"""O comprovante de inscrição e o documento de divulgação, byte a byte (069, FR-1383; 178, FR-8166).

**As fixtures `_v1` foram compostas pela `main` de 12/10/2026 (`a79ce463`), antes de qualquer
mudança no escritor**, e não se regeneram. A `069` deu ao Edital fonte embutida, métrica própria,
marcadores e outro arquivo; os outros dois documentos que passam pelo mesmo escritor
(`render_documento`) ficaram como estavam (R-005, SC-522).

**A `178` emendou a FR-1383.** A família da divulgação e o comprovante novo passam a PDF/A-2u, com a
Edital Sans embutida e medida — as fixtures `_v2`, compostas pela `178` em 16/11/2026 e validadas no
veraPDF 1.30.4. A `_v1` do comprovante continua valendo, e para sempre: é o comprovante da inscrição
enviada antes da `178` (D-002, FR-8164), que sai do escritor antigo, congelado. A `_v1` da
divulgação fica como evidência do "antes", e o texto dela é o da `_v2`, palavra a palavra (SC-2824).

**Por que bytes, e não texto.** O comprovante se regenera a cada download, e a página dele promete
ao candidato o SHA-256 do arquivo (`portal/templates/portal/comprovante.html`, FR-063a da `009`):
um byte diferente é um resumo que deixa de conferir na segunda emissão.

**Quando um destes casos falhar**, a pergunta não é como regenerar a fixture: é por que o
comprovante ou a divulgação mudaram. Se a mudança for deliberada, ela é de outra feature, que decide
a regeneração e diz o que acontece com os resumos já emitidos — e a `_v1` do comprovante não se
regenera nunca.

Os conteúdos (`comprovante_v1.json`, `divulgacao_v1.json`) são sintéticos e passam pelos caminhos
que a composição tem: acentos e "í", "ª", "º" que a métrica da Helvetica subestima, pares
rótulo-valor, moldura, uma lista de 45 posições que atravessa três páginas com o cabeçalho repetido,
empate compartilhado, retificação por recurso e a seção do sorteio.
"""

import json
from pathlib import Path

import pytest

from processo_seletivo.divulgacao.infrastructure.documento import render_resultado_pdf
from processo_seletivo.inscricoes.infrastructure.comprovante_pdf import render_comprovante_pdf
from tests.interface.test_fluxo import texto_de_pdf_bytes

FIXTURES = Path(__file__).parent / "fixtures"

pytestmark = pytest.mark.contract


def _conteudo(nome):
    return json.loads((FIXTURES / f"{nome}.json").read_text("utf-8"))


def _fixture(nome):
    return (FIXTURES / f"{nome}.pdf").read_bytes()


def test_o_comprovante_da_inscricao_enviada_antes_da_178_sai_com_os_bytes_de_sempre():
    """SC-2823: o escritor antigo, congelado, dá os bytes de 12/10: o resumo confere."""
    assert render_comprovante_pdf(_conteudo("comprovante_v1"), pdfa=False) == _fixture(
        "comprovante_v1"
    )


def test_o_comprovante_novo_sai_com_os_bytes_da_178():
    assert render_comprovante_pdf(_conteudo("comprovante_v1")) == _fixture("comprovante_v2")


def test_o_documento_de_divulgacao_sai_com_os_bytes_da_178():
    assert render_resultado_pdf(_conteudo("divulgacao_v1")) == _fixture("divulgacao_v2")


@pytest.mark.parametrize("nome", ["comprovante", "divulgacao"])
def test_o_texto_da_178_e_o_de_antes_palavra_a_palavra(nome):
    """SC-2824: a fonte embutida move a quebra de linha, e não muda uma palavra (FR-8160)."""
    antes = texto_de_pdf_bytes(_fixture(f"{nome}_v1")).split()
    depois = texto_de_pdf_bytes(_fixture(f"{nome}_v2")).split()

    assert depois == antes


def test_o_comprovante_antigo_continua_com_a_helvetica_nao_embutida():
    """O que a `_v1` prende, dito em claro: sem fonte embutida, sem PDF/A, sem título."""
    documento = render_comprovante_pdf(_conteudo("comprovante_v1"), pdfa=False)

    assert b"/BaseFont /Helvetica " in documento
    assert b"/FontFile2" not in documento
    assert b"/Metadata" not in documento
    assert b"/Outlines" not in documento
    assert b"/Info" not in documento


def test_os_novos_embutem_a_fonte_e_nao_declaram_a_helvetica():
    for documento in (_fixture("comprovante_v2"), _fixture("divulgacao_v2")):
        assert b"/BaseFont /Helvetica" not in documento
        assert documento.count(b"/FontFile2") == 2
        assert b"<pdfaid:part>2</pdfaid:part>" in documento
        # Continuam sem navegação: a `178` não acrescenta título, marcador nem link (FR-8153).
        assert b"/Outlines" not in documento
        # O `/Info` do trailer; o `/Info` da condição de saída é o nome do perfil de cor.
        assert b"/Info" not in documento.rsplit(b"trailer", 1)[1]
