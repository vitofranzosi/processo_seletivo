"""runserver do estudo da classificação, com o relógio da aplicação posto no dia da fase.

O certame demonstrativo acontece entre novembro de 2026 e janeiro de 2027, e cada fase só existe
no dia certo: a inscrição só abre no período, o recurso só cabe na janela, a convocação vence. O
relógio é o mesmo truque de `tests/fixtures/relatorio.em` — `timezone.now` deslocado para o
instante pedido, andando a partir dali.

    RELOGIO=2026-12-09T10:00 uv run python ../doc/estudo-classificacao-demonstrativa-2026-11-07/reproducao/servidor.py 8140

Sem `RELOGIO`, o relógio é o real.
"""

import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
import django  # noqa: E402

django.setup()
from django.core.management import call_command  # noqa: E402

from tests.fixtures.relatorio import em  # noqa: E402

relogio = os.environ.get("RELOGIO")
porta = sys.argv[1] if len(sys.argv) > 1 else "8140"
if relogio:
    instante = datetime.fromisoformat(relogio).replace(tzinfo=ZoneInfo("America/Sao_Paulo"))
    with em(instante):
        call_command("runserver", porta, use_reloader=False)
else:
    call_command("runserver", porta, use_reloader=False)
