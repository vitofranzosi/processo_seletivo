"""Inicialização sem migrate, seed ou provisão; falha antes de servir se faltar isolamento."""

import os

from contrato import exigir_selecao, verificar_banco

exigir_selecao()
import django

django.setup()
from django.db import connection

verificar_banco(connection)
connection.close()
os.execvp("python", ["python", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"])
