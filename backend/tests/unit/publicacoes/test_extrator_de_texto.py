"""Os extratores de texto dos testes leem o que os documentos desenham (069, R-006).

**Um extrator que devolve vazio aprova todo "não contém".** Os três extratores da suíte —
`texto_de` de `test_pdf.py`, o de `contract/test_documento_publicado.py` e `texto_de_pdf_bytes` de
`interface/test_fluxo.py` — leem só os fluxos de página de dicionário exatamente `<< /Length N >>`.
A `069` muda o arquivo do Edital: fonte embutida num fluxo compactado, marcadores, anotações. Se uma
dessas mudanças fizesse os fluxos de página saírem noutra forma, os extratores devolveriam texto
vazio, e as centenas de asserções negativas da suíte — "o documento não diz «recorte»", "não imprime
o UUID" — passariam sem testar nada.

Este guarda falha antes: cada extrator, sobre cada documento que a suíte lê, devolve texto não vazio
com uma frase conhecida.
"""

import json
from pathlib import Path

import pytest

from processo_seletivo.divulgacao.infrastructure.documento import render_resultado_pdf
from processo_seletivo.inscricoes.infrastructure.comprovante_pdf import render_comprovante_pdf
from processo_seletivo.publicacoes.infrastructure.pdf import MODO_PREVIA, MODO_PUBLICADO
from tests.contract import test_documento_publicado as contrato
from tests.interface.test_fluxo import texto_de_pdf_bytes
from tests.unit.publicacoes import test_pdf

FIXTURES = Path(__file__).resolve().parents[2] / "contract" / "fixtures"

EXTRATORES = {
    "test_pdf.texto_de": test_pdf.texto_de,
    "test_documento_publicado.texto_de": contrato.texto_de,
    "test_fluxo.texto_de_pdf_bytes": texto_de_pdf_bytes,
}


def _snapshot():
    return json.loads((FIXTURES / "snapshot_publicado.json").read_text("utf-8"))


def _documentos():
    """Cada documento que a suíte extrai, e uma frase que ele certamente desenha."""
    return {
        "edital publicado": (contrato.documento(_snapshot(), modo=MODO_PUBLICADO), "SHA-256"),
        "prévia do edital": (contrato.documento(_snapshot(), modo=MODO_PREVIA), "PRÉVIA"),
        "comprovante": (
            render_comprovante_pdf(
                json.loads((FIXTURES / "comprovante_v1.json").read_text("utf-8"))
            ),
            "COMPROVANTE DE INSCRIÇÃO",
        ),
        "divulgação": (
            render_resultado_pdf(json.loads((FIXTURES / "divulgacao_v1.json").read_text("utf-8"))),
            "SHA-256 do conteúdo divulgado",
        ),
    }


@pytest.mark.parametrize("extrator", sorted(EXTRATORES))
@pytest.mark.parametrize(
    "documento", ["edital publicado", "prévia do edital", "comprovante", "divulgação"]
)
def test_o_extrator_le_o_texto_desenhado(extrator, documento):
    pdf, frase = _documentos()[documento]
    texto = EXTRATORES[extrator](pdf)

    assert texto.strip(), f"{extrator} devolveu texto vazio para {documento}"
    assert frase in texto
    # Mais de uma página de texto, e não só o rodapé: o rodapé sai em todas as páginas e passaria
    # por "não vazio" mesmo com o corpo ilegível.
    assert len(texto.splitlines()) > 10
