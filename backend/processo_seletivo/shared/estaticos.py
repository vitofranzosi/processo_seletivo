"""O endereço de um arquivo estático com a versão do conteúdo (089).

`{% load estaticos %}` e `{% estatico 'interface/gestao/base.css' %}` dão o endereço de
`{% static %}` com `?v=` e os 12 primeiros dígitos do SHA-256 do arquivo. Fora do HTML, a folha
fica no cache do navegador; sem versão no endereço, a folha velha continuaria servida depois de
mudar — a `053` mediu uma correção de JS como se não funcionasse porque o navegador rodava a
`shell.js` da véspera.

O resumo é do **conteúdo**, e não da data do arquivo nem da versão do sistema: um `git checkout`
muda a data sem mudar o arquivo, e uma implantação muda a versão sem mudar a folha — nos dois casos
o cache seria descartado sem motivo (D-003 da `089`).

O resumo é memorizado pelo arquivo, pela data e pelo tamanho: a página só relê a folha quando
ela mudou. No runserver, editou a folha, a próxima página já a pede por outro endereço, sem
reiniciar; em produção, a folha da implantação nova ganha endereço novo, e as páginas não leem o
arquivo a cada pedido — custa um `stat`.

Descartado o `ManifestStaticFilesStorage`, que faz o mesmo no nome do arquivo: exige `collectstatic`
para um `STATIC_ROOT`, e o guia de produção serve os diretórios da release sem coletar (lacuna I-3).
"""

import hashlib
import os
import re
from functools import cache
from pathlib import Path

from django import template
from django.conf import settings
from django.contrib.staticfiles import finders
from django.core import checks
from django.core.exceptions import ImproperlyConfigured
from django.template.utils import get_app_template_dirs
from django.templatetags.static import static
from django.utils.html import format_html_join

register = template.Library()

# A folha comum da gestão, na ordem da cascata — a ordem em que `{% folhas_da_gestao %}` escreve os
# `<link>`. Uma lista só para a base e para a verificação de sistema (091, D-002): um `@import` num
# arquivo de entrada daria um `<link>` só, mas o navegador só acharia os importados depois de
# baixá-lo, e o endereço deles não levaria a versão do conteúdo.
FOLHAS_DA_GESTAO = tuple(
    f"interface/gestao/{area}.css"
    for area in (
        "base",
        "moldura",
        "impressao",
        "componentes",
        "formularios",
        "tabelas",
        "telas",
    )
)

# As folhas que as bases carregam por esta tag, além das de tela. A verificação de sistema abaixo
# confere cada uma, e também toda folha que um modelo cita pela tag (`folhas_citadas`).
FOLHAS = ("shared/tokens.css", *FOLHAS_DA_GESTAO, "shared/erro.css")


@cache
def _resumo_do_arquivo(arquivo, data, tamanho):
    # `data` e `tamanho` só entram na chave: mudou o arquivo, muda a chave, e ele é relido.
    with open(arquivo, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]


def _resumo(caminho):
    arquivo = finders.find(caminho)
    # Arquivo ausente é erro na página, e não `<link>` quebrado em silêncio: uma folha que não
    # carrega deixa a gestão sem estilo, e ninguém vê o 404 do estático. A verificação de sistema
    # pega o mesmo defeito antes, no `check` e no `migrate` da implantação.
    if not arquivo:
        raise ImproperlyConfigured(f"estático inexistente: {caminho}")
    estado = os.stat(arquivo)
    return _resumo_do_arquivo(arquivo, estado.st_mtime_ns, estado.st_size)


@register.simple_tag
def estatico(caminho):
    return f"{static(caminho)}?v={_resumo(caminho)}"


@register.simple_tag
def folhas_da_gestao():
    """Um `<link>` por arquivo da folha comum, na ordem de `FOLHAS_DA_GESTAO` (091)."""
    return format_html_join(
        "\n", '<link rel="stylesheet" href="{}">', ((estatico(c),) for c in FOLHAS_DA_GESTAO)
    )


# `{% estatico 'caminho' %}` no texto de um modelo.
_CITACAO = re.compile(r"""\{%\s*estatico\s+['"]([^'"]+)['"]\s*%\}""")


def folhas_citadas():
    """Todo caminho que algum modelo do projeto pede pela tag `estatico`, com o modelo que pede.

    Desde a 091 cada tela carrega o próprio arquivo, e são duas dúzias de `<link>` espalhados por
    modelos: um nome errado em um deles viraria 500 só naquela tela, achado por quem a abrisse. A
    verificação de sistema lê o texto dos modelos — os de `TEMPLATES.DIRS` e os dos apps — e confere
    cada caminho antes de o serviço atender alguém.
    """
    diretorios = [Path(d) for config in settings.TEMPLATES for d in config.get("DIRS", [])]
    diretorios += [Path(d) for d in get_app_template_dirs("templates")]
    citadas = {}
    for diretorio in diretorios:
        for modelo in sorted(diretorio.rglob("*.html")):
            for caminho in _CITACAO.findall(modelo.read_text(encoding="utf-8")):
                citadas.setdefault(caminho, modelo)
    return citadas


@checks.register(checks.Tags.staticfiles)
def verificar_folhas(app_configs=None, **kwargs):
    """Toda folha que as bases carregam tem de ser achada pelos *finders* — antes de atender alguém.

    Sem isto, uma implantação sem `shared/static/` subiria, passaria no `/health`, e todo pedido das
    quatro bases viraria 500, a página de erro inclusive, porque ela também carrega os tokens.
    """
    exigidas = dict.fromkeys(FOLHAS, None) | folhas_citadas()
    return [
        checks.Error(
            f"A folha {caminho} não é achada pelos finders de estáticos"
            + (f" (citada em {modelo.name})." if modelo else "."),
            hint="Confira STATICFILES_DIRS e os diretórios static/ dos apps (089, 091).",
            id="estaticos.E001",
        )
        for caminho, modelo in exigidas.items()
        if not finders.find(caminho)
    ]
