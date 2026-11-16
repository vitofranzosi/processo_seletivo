import sys, django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
django.setup()
from processo_seletivo.publicacoes.infrastructure import pdf
from tests.unit.publicacoes import cenarios_da_auditoria as c
destino = sys.argv[1]
open(f"{destino}/I1-edital-gps.pdf", "wb").write(c.composto("A", redacao=pdf.REDACAO_VIGENTE))
