"""O peso das respostas HTML da gestão, em bytes (089).

    pesar.py [saida.json]

Roda com o ambiente do backend, no banco do inventário, como o `capturar.py`. Pede cada tela pelo
cliente de teste do Django, com a identidade do inventário, e imprime o tamanho do corpo e o dos
`<style>` que ele carrega. As folhas externas não entram na conta da página: o navegador as baixa uma
vez e as guarda, e é essa a diferença que a 089 mede.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.getcwd())

import django  # noqa: E402

django.setup()

from django.test import Client  # noqa: E402

E51 = "af86be76-27f3-4e6a-b621-2b0771c323b2"
ETAPA = "00000000-0000-0000-0051-0000000000d1"
TELAS = [
    ("distribuicao", f"/gestao/editais/{E51}/distribuicao/{ETAPA}", "paulo.presidente", []),
    ("lista", "/gestao/", "gustavo.gestor", ["gestor"]),
    ("minhas-etapas", "/gestao/minhas-etapas", "joana.avaliadora", []),
]

linhas = []
for nome, caminho, quem, papeis in TELAS:
    c = Client(HTTP_HOST="localhost")
    c.post("/gestao/identificar", {"identidade_sugerida": quem, "papeis": papeis})
    r = c.get(caminho)
    assert r.status_code == 200, (nome, r.status_code)
    corpo = r.content
    estilo = sum(len(m) for m in re.findall(rb"<style>(.*?)</style>", corpo, re.S))
    links = re.findall(rb'<link rel="stylesheet" href="([^"]+)"', corpo)
    linhas.append({"tela": nome, "bytes": len(corpo), "style": estilo,
                   "folhas": [l.decode() for l in links]})
    print(f"{nome:15} {len(corpo):>8} bytes  <style> {estilo:>7}  folhas {len(links)}")

if len(sys.argv) > 1:
    with open(sys.argv[1], "w") as f:
        json.dump(linhas, f, ensure_ascii=False, indent=1)
