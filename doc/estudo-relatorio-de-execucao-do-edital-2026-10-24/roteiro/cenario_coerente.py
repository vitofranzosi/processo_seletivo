"""O cenário coerente do relatório do Edital, num banco próprio e migrado.

Desde a implementação (099) o cenário mora numa fonte só, a fixture dos testes
(`backend/tests/fixtures/relatorio.py`); este roteiro só a chama, para a demonstração e para as
maquetes. Rode de `backend/`, num banco vazio:

    FINAL=pendente ESCALA=1 uv run python manage.py shell < ../doc/.../roteiro/cenario_coerente.py

`FINAL`: `pendente` (o da maquete v2), `sem-pendencia`, `aberto` ou `cancelado`.
"""

import io
import os
from contextlib import redirect_stdout

from tests.fixtures.relatorio import montar_cenario

with redirect_stdout(io.StringIO()):
    cenario = montar_cenario(
        escala=int(os.environ.get("ESCALA", "1")), final=os.environ.get("FINAL", "pendente")
    )
print("pronto:", cenario.edital, cenario.edital.status, len(cenario.inscricoes), "inscrições")
