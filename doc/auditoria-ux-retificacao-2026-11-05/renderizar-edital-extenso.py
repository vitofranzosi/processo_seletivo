"""A tela Retificar sobre o Edital 01/2026 ampliado (cenário E da auditoria de 05/11/2026).

Só lê: troca `conteudo_base` em memória e grava o HTML. Rode por `manage.py shell <`.
"""

import copy
import json
import re
import uuid

from django.test import Client

import processo_seletivo.interface.views as V

original = V.conteudo_base
N_PERFIS, N_EVENTOS = 4, 11


def ids_em(no, acc):
    if isinstance(no, dict):
        if isinstance(no.get("id"), str):
            acc.add(no["id"])
        for v in no.values():
            ids_em(v, acc)
    elif isinstance(no, list):
        for v in no:
            ids_em(v, acc)
    return acc


def ampliado(base):
    c = copy.deepcopy(original(base))
    modelo = c["profiles"][0]
    for i in range(N_PERFIS - 1):
        texto = json.dumps(modelo)
        for velho in ids_em(modelo, set()):
            texto = texto.replace(velho, str(uuid.uuid4()))
        novo = json.loads(texto)
        novo["code"] = f"CURSO-{i + 2}"
        novo["name"] = f"Curso de Aperfeiçoamento {i + 2}"
        c["profiles"].insert(1 + i, novo)
    ev = c["schedule"][-1]
    for j in range(len(c["schedule"]), N_EVENTOS):
        e = copy.deepcopy(ev)
        e["id"] = str(uuid.uuid4())
        e["order"] = j + 1
        e["description"] = f"Evento sintético {j + 1}"
        e["type"] = f"Evento {j + 1}"
        c["schedule"].append(e)
    return c


V.conteudo_base = ampliado
cli = Client()
cli.post("/gestao/identificar", {"identidade_sugerida": "ana.elaboradora", "papeis": "elaborador"})
r = cli.get("/gestao/editais/0b0173ac-9992-4e27-aad0-50e19c459f37/retificar")
html = r.content.decode().replace("<head>", '<head><base href="http://localhost:8135/">', 1)
open("/tmp/ux-retificacao/extenso.html", "w").write(html)
print(
    "status",
    r.status_code,
    "perfis",
    N_PERFIS,
    "eventos",
    N_EVENTOS,
    "cartoes",
    html.count("data-linha "),
    "campos",
    len(re.findall(r'name="campo:', html)),
)
