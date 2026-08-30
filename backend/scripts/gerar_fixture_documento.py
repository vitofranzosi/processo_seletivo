"""Regenera os bytes de referência do documento publicado.

A fixture existe para provar que uma mudança no renderizador **não** alterou o documento oficial.
Rodar isto refaz a evidência: só é legítimo na mesma tarefa que muda a composição de propósito, com
o diff dos bytes revisado. Fazê-lo para calar um teste que falhou apaga exatamente o que a fixture
guarda.

    uv run python scripts/gerar_fixture_documento.py
"""

import json
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

# O renderizador converte instantes para a zona institucional, e para isso precisa das settings.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")

import django  # noqa: E402

django.setup()

from processo_seletivo.publicacoes.infrastructure.pdf import render_edital_pdf  # noqa: E402
from processo_seletivo.shared.canonical import canonical_sha256  # noqa: E402

FIXTURES = RAIZ / "tests" / "contract" / "fixtures"


def main():
    snapshot = json.loads((FIXTURES / "snapshot_publicado.json").read_text(encoding="utf-8"))
    destino = FIXTURES / "documento_publicado_v1.pdf"
    destino.write_bytes(render_edital_pdf(snapshot, canonical_sha256(snapshot)))
    print(f"{destino.relative_to(RAIZ)}: {destino.stat().st_size} bytes")


if __name__ == "__main__":
    main()
