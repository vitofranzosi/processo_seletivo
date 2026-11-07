"""runserver da demonstração da 130 com o relógio no instante de referência do cenário do relatório."""
import os
import sys

sys.path.insert(0, os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
import django

django.setup()
from django.core.management import call_command

from tests.fixtures.relatorio import REFERENCIA, em

with em(REFERENCIA):
    call_command("runserver", sys.argv[1], use_reloader=False)
