"""Renderiza um snapshot com o pdf.py de um commit antigo (código extraído por git archive)."""
import json, sys, os
from datetime import date
raiz, snap, saida = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, raiz)
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.development"
import django
django.setup()
from processo_seletivo.publicacoes.infrastructure import pdf
dados = json.load(open(snap))
kw = {}
import inspect
params = inspect.signature(pdf.render_edital_pdf).parameters
autoridade = pdf.AutoridadeSignataria(nome="Fulana de Tal", cargo="Diretora-Geral do Centro de Referência em Formação e em Educação a Distância", **({"ato_de_nomeacao": "Portaria nº 0000, de 2 de janeiro de 2026 (fictícia)"} if "ato_de_nomeacao" in pdf.AutoridadeSignataria.__dataclass_fields__ else {}))
kw["autoridade"] = autoridade
if "unidade" in params:
    kw["unidade"] = pdf.UnidadeDoAto(cabecalho=("Centro de Referência em Formação", "e em Educação a Distância"), local="Vitória (ES)")
if "data_do_ato" in params:
    kw["data_do_ato"] = date(2026, 10, 8)
open(saida, "wb").write(pdf.render_edital_pdf(dados["content"], dados["hash"], **kw))
print(saida, inspect.getsourcefile(pdf))
