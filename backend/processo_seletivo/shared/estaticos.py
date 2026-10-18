"""O endereço de um arquivo estático com a versão do conteúdo (089).

`{% load estaticos %}` e `{% estatico 'interface/gestao.css' %}` dão o endereço de `{% static %}`
com `?v=` e os 12 primeiros dígitos do SHA-256 do arquivo. Fora do HTML, a folha fica no cache do
navegador; sem versão no endereço, a folha velha continuaria servida depois de mudar — a `053` mediu
uma correção de JS como se não funcionasse porque o navegador rodava a `shell.js` da véspera.

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
from functools import cache

from django import template
from django.contrib.staticfiles import finders
from django.core import checks
from django.core.exceptions import ImproperlyConfigured
from django.templatetags.static import static

register = template.Library()

# As folhas que as bases carregam por esta tag. A verificação de sistema abaixo confere cada uma.
FOLHAS = ("shared/tokens.css", "interface/gestao.css")


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


@checks.register(checks.Tags.staticfiles)
def verificar_folhas(app_configs=None, **kwargs):
    """Toda folha que as bases carregam tem de ser achada pelos *finders* — antes de atender alguém.

    Sem isto, uma implantação sem `shared/static/` subiria, passaria no `/health`, e todo pedido das
    quatro bases viraria 500, a página de erro inclusive, porque ela também carrega os tokens.
    """
    return [
        checks.Error(
            f"A folha {caminho} não é achada pelos finders de estáticos.",
            hint="Confira STATICFILES_DIRS e os diretórios static/ dos apps (089).",
            id="estaticos.E001",
        )
        for caminho in FOLHAS
        if not finders.find(caminho)
    ]
