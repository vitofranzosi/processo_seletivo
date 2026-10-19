"""O tamanho da resposta HTML de telas do portal, para o R-005 da 092 (FR-2144, SC-825).

    pesar_portal.py <rotas.json>      (de backend/ da árvore a medir, com o ambiente do inventário)

Pede pelo cliente de teste do Django, com a sessão da candidata aberta como no `capturar_portal.py`,
uma tela de cada forma de endereço da lista de rotas, e imprime o tamanho do corpo e a contagem de
`style=`. Rodado na árvore de antes e na de depois, sobre cópias do mesmo banco.
"""

import json
import os
import re
import sys
from importlib import import_module

sys.path.insert(0, os.getcwd())

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402
from django.test import Client  # noqa: E402

from processo_seletivo.identidade.models import CandidateIdentity  # noqa: E402
from processo_seletivo.portal.identidade import CHAVE_SESSAO  # noqa: E402

settings.ALLOWED_HOSTS = [*settings.ALLOWED_HOSTS, "testserver"]
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")

vistas = set()
for rota in json.load(open(sys.argv[1])):
    forma = UUID.sub("{id}", rota["caminho"])
    if rota["quem"] == "inventario.piloto" or forma in vistas:
        continue
    vistas.add(forma)
    cliente = Client()
    if rota["quem"]:
        registro = CandidateIdentity.objects.get(credenciais__email_como_informado=rota["quem"])
        sessao = import_module(settings.SESSION_ENGINE).SessionStore()
        sessao[CHAVE_SESSAO] = str(registro.pk)
        sessao.save()
        cliente.cookies[settings.SESSION_COOKIE_NAME] = sessao.session_key
    corpo = cliente.get(rota["caminho"]).content
    print(f"{len(corpo):>7} {corpo.count(b'style='):>2}  {forma}")
