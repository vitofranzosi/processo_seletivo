"""Mede a origem das palavras impressas: redação livre, valores estruturados e texto fixo do sistema.

Recompõe o PDF de cada edital com o compositor do backend, depois de trocar cada campo de texto livre por
um marcador de uma palavra (`XQaa`…, o mesmo marcador para o mesmo texto, para que os agrupamentos da 064 e
da 068 continuem os mesmos). Ver `auditoria-sistema.md`, §1.1.

Entradas: `editais/<edital>/fonte/pub1-canonico.json`. Não toca banco: só importa o compositor.
Dependências: o ambiente do backend (`cd backend && uv sync`) e `pdftotext`.
Uso, da raiz do repositório:

    cd backend && DJANGO_SETTINGS_MODULE=config.settings.development \
        uv run python manage.py shell < ../docs/libras/ferramentas/origem_do_texto.py

**Depende da versão do compositor:** o resultado de 2026-10-11 é do commit `bbc8e04c`. Com outro código,
o texto fixo pode ser outro.
"""

import itertools
import json
import re
import string
import subprocess
import tempfile
from datetime import date
from pathlib import Path

from django.conf import settings
from processo_seletivo.publicacoes.infrastructure import pdf

RAIZ = Path(settings.BASE_DIR).parent / "docs" / "libras"
LIVRES = {
    "title",
    "description",
    "processoTitle",
    "label",
    "name",
    "instructions",
    "derivation",
    "text",
    "source",
    "occurrence",
    "declarationText",
    "duties",
    "requirements",
    "locality",
    "compensation",
    "workload",
    "foundation",
    "location",
    "type",
    "content",
    "rotuloFavoravel",
    "rotuloDesfavoravel",
}
# Chaves que só são texto livre em alguns contextos: o `type` do critério de desempate, do dado declarado e da
# seção é enumeração; o `title` e o `source` da seção são do catálogo.
NAO_LIVRE = {
    ("type", "tiebreakers"),
    ("type", "declaredFacts"),
    ("type", "sections"),
    ("title", "sections"),
    ("source", "sections"),
}


def marcadores():
    for n in itertools.count(0):
        s, m = "", n
        while True:
            s, m = string.ascii_lowercase[m % 26] + s, m // 26
            if m == 0:
                break
        yield "XQ" + s


GERADOR, MAPA = marcadores(), {}


def marca(valor):
    if valor not in MAPA:
        MAPA[valor] = next(GERADOR)
    return MAPA[valor]


def trocar(x, pai=""):
    if isinstance(x, dict):
        out = {}
        for k, v in x.items():
            if isinstance(v, str) and v.strip() and k in LIVRES and (k, pai) not in NAO_LIVRE:
                out[k] = (
                    "\n".join(marca(p) for p in v.split("\n") if p.strip())
                    if (pai, k) == ("sections", "content")
                    else marca(v)
                )
            elif isinstance(v, list) and k == "requirements":
                out[k] = [marca(i) for i in v]
            else:
                out[k] = trocar(v, k if isinstance(v, list) else pai)
        return out
    if isinstance(x, list):
        return [trocar(i, pai) for i in x]
    return x


UNIDADE = pdf.UnidadeDoAto(
    cabecalho=("Centro de Referência em Formação", "e em Educação a Distância"), local="Vitória (ES)"
)
CARGO = "Diretora-Geral do Centro de Referência em Formação e em Educação a Distância"
AUTORIDADES = {
    "edital-91-2026": pdf.AutoridadeSignataria(
        nome="Fulana de Tal", cargo=CARGO, ato_de_nomeacao="Portaria nº 0000, de 2 de janeiro de 2026 (fictícia)"
    ),
    "edital-92-2026": pdf.AutoridadeSignataria(nome="", cargo=CARGO),
    "edital-01-2026": pdf.AutoridadeSignataria(nome="", cargo="Reitora"),
}
RODAPE = re.compile(r"Verificação [0-9a-f]+….*Página \d+ de \d+")


def texto(conteudo):
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        f.write(
            pdf.render_edital_pdf(
                conteudo,
                "0" * 64,
                pdf.MODO_PUBLICADO,
                unidade=UNIDADE,
                autoridade=AUTORIDADES[slug],
                data_do_ato=date(2026, 10, 11),
            )
        )
        f.flush()
        saida = subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True, text=True).stdout
    return " ".join(linha for linha in saida.splitlines() if not RODAPE.search(linha)).split()


for slug in AUTORIDADES:
    conteudo = json.loads((RAIZ / "editais" / slug / "fonte" / "pub1-canonico.json").read_text(encoding="utf-8"))
    codigos = {p["code"] for p in conteudo["profiles"]}
    for p in conteudo["profiles"]:
        codigos |= {m["code"] for m in p.get("classificationMilestones", [])} | {
            m["code"] for m in p.get("competitionModalities", [])
        }
    original, marcado = texto(conteudo), texto(trocar(conteudo))
    sistema = [w for w in marcado if not re.fullmatch(r"\W*XQ[a-z]+\W*", w)]
    valores = [w for w in sistema if re.search(r"\d", w) or w.strip(",.;:()—") in codigos]
    livre, fixo = len(original) - len(sistema), len(sistema) - len(valores)
    print(
        f"{slug}: palavras={len(original)} | redação livre={livre} ({livre / len(original):.0%}) | "
        f"valores estruturados={len(valores)} ({len(valores) / len(original):.0%}) | "
        f"texto fixo do sistema={fixo} ({fixo / len(original):.0%})"
    )
