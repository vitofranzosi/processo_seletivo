"""Emite o PDF do Edital 61/2026 pela porta do sistema: a view de emissão, com o registro na trilha.

`emitir_demonstracao.py` só compõe o documento; aqui é o `POST` da gestão, numerado e auditado, com
o host que a requisição declara. `HOST=selecao.cefor.ifes.edu.br` dá os links públicos; sem `HOST`,
o host é `localhost`, e o PDF sai sem endereço, dizendo por quê (FR-2603). Rode de `backend/`, com
`SAIDA=<arquivo.pdf>`, `INTERFACE_SELETOR_IDENTIDADE=true` e o host em `DJANGO_ALLOWED_HOSTS`.

Com `HOST`, a requisição é segura, como em produção: lá o TLS termina no nginx, que repassa
`X-Forwarded-Proto: https`, e o Django confia nele (`DJANGO_TRUST_PROXY_SSL_HEADER`). Sem isso o
link sairia `http://`, que é o que um servidor de desenvolvimento sem TLS de fato serve.
"""

import os
from pathlib import Path

from django.test import Client
from django.urls import reverse

from processo_seletivo.processos.models import Edital

host = os.environ.get("HOST")
cliente = Client(HTTP_HOST=host or "localhost")
identificado = cliente.post(
    reverse("interface:identificar"), {"subject": "gustavo.gestor", "papeis": ["gestor"]}
)
assert identificado.status_code == 302, identificado.content[:300]
edital = Edital.objects.get(number="61")
emitido = cliente.post(
    reverse("interface:relatorio-do-edital-pdf", args=[edital.id]), secure=bool(host)
)
assert emitido.status_code == 200, emitido.content[:300]
Path(os.environ["SAIDA"]).write_bytes(emitido.content)
print(emitido["Content-Disposition"], "→", os.environ["SAIDA"])
