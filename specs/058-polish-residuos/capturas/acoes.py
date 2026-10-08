"""Os destinos de ação por papel, nas telas que a 058 toca (D-010; a D-017 da 057).

Roda no `manage.py shell` contra o banco da medição:

    DB_NAME=ps_058_polish DB_USER=$USER DB_RUNTIME_USER=$USER INTERFACE_SELETOR_IDENTIDADE=true \
      uv run python manage.py shell < ../specs/058-polish-residuos/capturas/acoes.py

e grava `ACOES_SAIDA` (o caminho vem do ambiente). `ACOES_057`, opcional, aponta para o
`acoes-antes.json` da 057: as telas de lá entram como sementes, porque nem todas se alcançam pela
Lista. A lista de telas é descoberta a partir da Lista
e dos Processos, seguindo só os links das telas tocadas — e é a mesma para as duas identidades.
"""

import json
import os
import re
from html.parser import HTMLParser

from django.conf import settings
from django.test import Client

from processo_seletivo.processos.models import Edital
from processo_seletivo.interface import identidade

settings.ALLOWED_HOSTS = [*settings.ALLOWED_HOSTS, "testserver"]

# As telas tocadas (e as que o parcial das terminais alcança): só GET de leitura.
TOCADAS = re.compile(
    r"^/gestao/("
    r"$|processos/[0-9a-f-]+/$"
    r"|editais/[0-9a-f-]+/$"
    r"|editais/[0-9a-f-]+/matriculas$"
    r"|editais/[0-9a-f-]+/recursos$"
    r"|recursos/[0-9a-f-]+$"
    r"|editais/[0-9a-f-]+/distribuicao/[0-9a-f-]+(/resultados)?$"
    r"|editais/[0-9a-f-]+/marcos/[0-9a-f-]+(/conducao|/corte|/ocupacao|/ocupacao/historico|/sorteio)?$"
    r"|editais/[0-9a-f-]+/compor/(etapas|revisao|perfis)$"
    r")"
)


class Destinos(HTMLParser):
    """`href`, `action`, `hx-post`, `formaction` e `name=value` de dentro do `main`."""

    def __init__(self, pagina):
        super().__init__()
        self.pagina, self.no_main, self.achados = pagina, 0, set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "main":
            self.no_main += 1
        if not self.no_main:
            return
        if tag == "a" and a.get("href"):
            self.achados.add(f"href {a['href']}")
        if tag == "form":
            self.achados.add(f"action {a.get('action') or self.pagina}")
        if a.get("hx-post"):
            self.achados.add(f"hx-post {a['hx-post']}")
        if tag == "button" or (tag == "input" and a.get("type") == "submit"):
            if a.get("formaction"):
                self.achados.add(f"formaction {a['formaction']}")
            if a.get("name"):
                # A chave de idempotência nasce nova a cada render (é o que a torna chave), e
                # compará-la acusaria diferença em toda tela com formulário, com ou sem a feature.
                valor = "<chave>" if a["name"] == "chave_idempotencia" else a.get("value", "")
                self.achados.add(f"botao {a['name']}={valor}")

    def handle_endtag(self, tag):
        if tag == "main":
            self.no_main -= 1


def entrar(subject, papeis):
    cliente = Client()
    resposta = cliente.post("/gestao/identificar", {"subject": subject, "papeis": papeis})
    assert resposta.status_code == 302, resposta.status_code
    return cliente


def destinos(cliente, url):
    resposta = cliente.get(url)
    if resposta.status_code != 200:
        return [f"status {resposta.status_code}"]
    leitor = Destinos(url)
    leitor.feed(resposta.content.decode())
    return sorted(leitor.achados)


def descobrir(cliente):
    sementes = ["/gestao/"] + [f"/gestao/editais/{e.id}/compor/etapas" for e in Edital.objects.all()]
    # As telas que a 057 mediu, no mesmo banco de origem: as que nenhum link da Lista alcança.
    if os.environ.get("ACOES_057"):
        sementes += json.load(open(os.environ["ACOES_057"]))["ana.gestora"]
    vistas, fila = [], list(sementes)
    while fila:
        url = fila.pop(0)
        if url in vistas or not TOCADAS.match(url):
            continue
        vistas.append(url)
        for item in destinos(cliente, url):
            if item.startswith("href "):
                alvo = item[5:].split("#")[0]
                if TOCADAS.match(alvo) and alvo not in vistas:
                    fila.append(alvo)
    return vistas


ana = entrar("ana.gestora", list(identidade.PAPEIS))
telas = descobrir(ana)
saida = {}
for nome, cliente in (("ana.gestora", ana), ("joana.avaliadora", entrar("joana.avaliadora", []))):
    saida[nome] = {url: destinos(cliente, url) for url in telas}
with open(os.environ["ACOES_SAIDA"], "w") as arquivo:
    json.dump(saida, arquivo, indent=1, ensure_ascii=False)
print(len(telas), "telas;", sum(len(v) for v in saida["ana.gestora"].values()), "destinos (ana)")
