"""Grava o lote que o veraPDF valida no CI (178, FR-8168, FR-8169).

**Não é guardião, e roda só sob demanda**, como a fotografia do piloto do design system: sem
`PDFA_EXEMPLARES=<pasta>`, o módulo pula inteiro. Com ela, grava na pasta um exemplar de cada tipo e
o `manifesto.json` com o nível que cada um tem de declarar — que é o que
`scripts/conferir_o_verapdf.py` compara com o relatório do validador. O job `pdfa` do
`.github/workflows/backend.yml` faz os três passos; à mão:

```bash
PDFA_EXEMPLARES=$HOME/pdfa uv run python -m pytest tests/pdfa -q
docker run --rm -v $HOME/pdfa:/data verapdf/cli:v1.30.4 --format json /data > $HOME/pdfa/r.json
uv run python scripts/conferir_o_verapdf.py $HOME/pdfa/manifesto.json $HOME/pdfa/r.json
```

A pasta fica fora de `/tmp` no macOS com Colima, que não monta `/tmp` no contêiner.
"""

import json
import os
from pathlib import Path

import pytest

from tests.pdfa.exemplares import EXEMPLARES

PASTA = os.environ.get("PDFA_EXEMPLARES")

pytestmark = pytest.mark.skipif(
    not PASTA, reason="sob demanda: PDFA_EXEMPLARES=<pasta> grava o lote do veraPDF"
)


def test_grava_um_exemplar_de_cada_tipo_e_o_manifesto():
    pasta = Path(PASTA)
    pasta.mkdir(parents=True, exist_ok=True)
    manifesto = {}
    for exemplar in EXEMPLARES:
        (pasta / exemplar.arquivo).write_bytes(exemplar.compor())
        manifesto[exemplar.arquivo] = f"2{exemplar.nivel.lower()}"
    (pasta / "manifesto.json").write_text(json.dumps(manifesto, indent=2, sort_keys=True))
    assert len(manifesto) == 9
