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
from pathlib import Path

import pytest

from processo_seletivo.publicacoes.infrastructure.pdf import render_edital_pdf
from processo_seletivo.shared.canonical import canonical_sha256

FIXTURES = Path(__file__).resolve().parent / "fixtures"
SNAPSHOT = json.loads((FIXTURES / "snapshot_publicado.json").read_text(encoding="utf-8"))
DOCUMENTO = (FIXTURES / "documento_publicado_v1.pdf").read_bytes()

# O hash do próprio snapshot, e não uma constante arbitrária: é o que o ato de publicação passa
# ao renderizador, e é o que aparece na declaração de integridade do documento.
HASH = canonical_sha256(SNAPSHOT)


@pytest.mark.contract
def test_o_documento_publicado_continua_byte_a_byte_o_mesmo():
    assert render_edital_pdf(SNAPSHOT, HASH) == DOCUMENTO
