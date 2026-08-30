"""Os bytes do documento publicado, congelados antes de o renderizador ganhar um modo.

Esta fixture prova **uma** coisa: que a introdução do modo de prévia não alterou o documento
oficial. Ela não descreve o conteúdo do PDF — para isso existe `tests/unit/publicacoes/test_pdf.py`,
que afirma o que precisa aparecer. Aqui o que se afirma é a ausência de mudança, e por isso a
comparação é byte a byte: qualquer coisa que altere a composição do documento publicado faz este
teste falhar, inclusive uma alteração que os testes de conteúdo não notariam.

**Regenerar a fixture só é legítimo na mesma tarefa que mudar a composição de propósito**, com o
diff revisado. Regenerá-la para fazer um teste passar é apagar a única evidência que ela guarda.

O snapshot fica versionado ao lado dos bytes: sem ele a fixture seria um arquivo binário que
ninguém consegue reproduzir, e a comparação viraria fé.
"""

import json
import re
from pathlib import Path

import pytest

from processo_seletivo.publicacoes.infrastructure.pdf import (
    MARCA_DE_PREVIA,
    MODO_PREVIA,
    MODO_PUBLICADO,
    render_edital_pdf,
)
from processo_seletivo.shared.canonical import canonical_sha256

FIXTURES = Path(__file__).resolve().parent / "fixtures"
SNAPSHOT = json.loads((FIXTURES / "snapshot_publicado.json").read_text(encoding="utf-8"))
DOCUMENTO = (FIXTURES / "documento_publicado_v1.pdf").read_bytes()

# O hash do próprio snapshot, e não uma constante arbitrária: é o que o ato de publicação passa
# ao renderizador, e é o que aparece na declaração de integridade do documento.
HASH = canonical_sha256(SNAPSHOT)

PAGINA = re.compile(rb"/Type /Page /Parent")
TEXTO_PDF = re.compile(rb"\((.*?)\) Tj", re.DOTALL)


def texto_de(pdf: bytes) -> str:
    return "\n".join(
        parte.replace(b"\\(", b"(").replace(b"\\)", b")").decode("cp1252")
        for parte in TEXTO_PDF.findall(pdf)
    )


@pytest.mark.contract
def test_o_documento_publicado_continua_byte_a_byte_o_mesmo():
    assert render_edital_pdf(SNAPSHOT, HASH) == DOCUMENTO


@pytest.mark.contract
def test_o_modo_publicado_explicito_e_o_mesmo_do_padrao():
    """Nomear o modo não pode mudar o documento oficial."""
    assert render_edital_pdf(SNAPSHOT, HASH, modo=MODO_PUBLICADO) == DOCUMENTO


@pytest.mark.contract
def test_a_previa_nao_carrega_nenhuma_afirmacao_de_integridade():
    """FR-014: o que não pode sair de uma prévia é a afirmação, não o desenho.

    O hash é passado vazio pela view, mas o teste passa o hash **de verdade** justamente para
    provar que o modo o ignora: se a garantia dependesse de o chamador lembrar de esvaziá-lo, ela
    estaria com quem não a tem.
    """
    texto = texto_de(render_edital_pdf(SNAPSHOT, HASH, modo=MODO_PREVIA))

    assert HASH not in texto
    assert HASH[:16] not in texto
    assert "INTEGRIDADE" not in texto
    assert "deriva integralmente da versão homologada" not in texto
    assert "SHA-256" not in texto


@pytest.mark.contract
def test_a_previa_se_identifica_em_todas_as_paginas():
    muitos = {
        **SNAPSHOT,
        "profiles": [
            {**SNAPSHOT["profiles"][0], "code": f"P{indice:02d}", "id": str(indice)}
            for indice in range(1, 26)
        ],
    }
    pdf = render_edital_pdf(muitos, HASH, modo=MODO_PREVIA)
    paginas = len(PAGINA.findall(pdf))
    assert paginas >= 3, paginas

    texto = texto_de(pdf)
    assert texto.count(MARCA_DE_PREVIA) >= paginas, "a marca precisa estar em todas as páginas"


@pytest.mark.contract
def test_a_previa_traz_o_mesmo_conteudo_normativo_do_publicado():
    """FR-013: o que muda é a moldura, não o Edital."""
    publicado = texto_de(render_edital_pdf(SNAPSHOT, HASH))
    previa = texto_de(render_edital_pdf(SNAPSHOT, HASH, modo=MODO_PREVIA))

    for esperado in ("DOC-INFO", "Professor de Informática", "PPP", "Lei 12.990/2014", "20.0000"):
        assert esperado in publicado and esperado in previa, esperado


@pytest.mark.contract
def test_modo_desconhecido_e_recusado_em_vez_de_cair_no_publicado():
    """Errar o nome do modo não pode produzir, em silêncio, um documento com cara de publicado."""
    with pytest.raises(ValueError):
        render_edital_pdf(SNAPSHOT, HASH, modo="PREVIEW_")
