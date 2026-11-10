"""runserver do estudo do Centro de Controle do Edital (2026-11-09).

Serve a gestão inteira, como está, **mais** as rotas do protótipo em `/gestao/prototipo-centro/`.
Nada disto entra no código de produção: as configurações, as rotas, os templates e a folha do
protótipo moram nesta pasta, e o servidor os acrescenta em tempo de execução.

    cd backend && DB_NAME=ps_cc_centro DB_USER=$USER DB_RUNTIME_USER=$USER \
        INTERFACE_SELETOR_IDENTIDADE=true \
        uv run python ../doc/estudo-centro-de-controle-2026-11-09/prototipo/servidor.py 8150

O banco é o dos cenários de treinamento (134), carregado à parte — ver `../README.md`.
"""

import os
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, os.getcwd())
sys.path.insert(0, str(AQUI))
os.environ["DJANGO_SETTINGS_MODULE"] = "configuracao_do_prototipo"

import django  # noqa: E402

django.setup()
from django.core.management import call_command  # noqa: E402

porta = sys.argv[1] if len(sys.argv) > 1 else "8150"
call_command("runserver", porta)
