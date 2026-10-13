"""O comprovante de inscrição e o documento de divulgação não mudam um byte com a `069` (FR-1383).

**As fixtures foram compostas pela `main` de 12/10/2026 (`a79ce463`), antes de qualquer mudança no
escritor**, e não se regeneram nesta feature. A `069` dá ao Edital fonte embutida, métrica própria,
marcadores e outro arquivo; os outros dois documentos que passam pelo mesmo escritor
(`render_documento`) ficam como estavam (R-005, SC-522).

**Por que bytes, e não texto.** O comprovante se regenera a cada download, e a página dele promete
ao candidato o SHA-256 do arquivo (`portal/templates/portal/comprovante.html`, FR-063a da `009`):
um byte diferente é um resumo que deixa de conferir na segunda emissão. Até aqui nenhum dos dois
tinha fixture — só o determinismo no mesmo processo, que uma mudança de escritor não acusaria.

**Quando um destes casos falhar**, a pergunta não é como regenerar a fixture: é por que o
comprovante ou a divulgação mudaram. Se a mudança for deliberada, ela é de outra feature, que
decide a regeneração e diz o que acontece com os resumos já emitidos.

Os conteúdos (`comprovante_v1.json`, `divulgacao_v1.json`) são sintéticos e passam pelos caminhos
que a composição tem: acentos e "í", "ª", "º" que a métrica de hoje subestima, pares rótulo-valor,
moldura, uma lista de 45 posições que atravessa três páginas com o cabeçalho repetido, empate
compartilhado, retificação por recurso e a seção do sorteio.
"""

import json
from pathlib import Path

import pytest

from processo_seletivo.divulgacao.infrastructure.documento import render_resultado_pdf
from processo_seletivo.inscricoes.infrastructure.comprovante_pdf import render_comprovante_pdf

FIXTURES = Path(__file__).parent / "fixtures"

pytestmark = pytest.mark.contract


def _conteudo(nome):
    return json.loads((FIXTURES / f"{nome}.json").read_text("utf-8"))


def test_o_comprovante_sai_com_os_bytes_da_main():
    """SC-522: o mesmo comprovante, emitido antes e depois da `069`, tem os mesmos bytes."""
    esperado = (FIXTURES / "comprovante_v1.pdf").read_bytes()

    assert render_comprovante_pdf(_conteudo("comprovante_v1")) == esperado


def test_o_documento_de_divulgacao_sai_com_os_bytes_da_main():
    """SC-522: o mesmo resultado divulgado, antes e depois da `069`, tem os mesmos bytes."""
    esperado = (FIXTURES / "divulgacao_v1.pdf").read_bytes()

    assert render_resultado_pdf(_conteudo("divulgacao_v1")) == esperado


def test_os_dois_continuam_com_a_helvetica_nao_embutida():
    """O que a fixture prende, dito em claro: sem fonte embutida, sem marcador, sem título.

    Se os bytes conferem, isto também confere; o caso existe para que a falha, quando vier, diga de
    saída qual das mudanças do Edital vazou para os outros documentos.
    """
    for documento in (
        render_comprovante_pdf(_conteudo("comprovante_v1")),
        render_resultado_pdf(_conteudo("divulgacao_v1")),
    ):
        assert b"/BaseFont /Helvetica " in documento
        assert b"/FontFile2" not in documento
        assert b"/Outlines" not in documento
        assert b"/Info" not in documento
