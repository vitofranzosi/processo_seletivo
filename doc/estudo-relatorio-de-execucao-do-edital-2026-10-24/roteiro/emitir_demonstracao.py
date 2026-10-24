"""Emite o PDF do relatório do Edital 61/2026 do banco corrente, no instante da maquete v2.

Somente leitura: não grava o evento de emissão, porque não é emissão — é a demonstração do
documento. Rode de `backend/` com `SAIDA=<arquivo.pdf>`.
"""

import os
from pathlib import Path

from processo_seletivo.interface import relatorio_do_edital, relatorio_pdf
from processo_seletivo.processos.models import Edital
from tests.fixtures.relatorio import REFERENCIA

BASE = os.environ.get("ENDERECO", "http://localhost:8099")


class Enderecos:
    def __init__(self, edital):
        self.edital = edital

    def selecao(self):
        return f"{BASE}/selecoes/{self.edital.id}/"

    def resultado(self, publicacao_id):
        return f"{BASE}/selecoes/resultados/{publicacao_id}/"


edital = Edital.objects.select_related("processo").get(number="61")
relatorio = relatorio_do_edital.ler(edital, agora=REFERENCIA, enderecos=Enderecos(edital))
Path(os.environ["SAIDA"]).write_bytes(relatorio_pdf.compor(relatorio, emissao=1))
print(relatorio.especie, "→", os.environ["SAIDA"])
