"""O endereço de um arquivo estático com a versão do conteúdo (089).

`{% load estaticos %}` e `{% estatico 'interface/gestao.css' %}` dão o endereço de `{% static %}`
com `?v=` e os 12 primeiros dígitos do SHA-256 do arquivo. Fora do HTML, a folha fica no cache do
navegador; sem versão no endereço, a folha velha continuaria servida depois de mudar — a `053` mediu
uma correção de JS como se não funcionasse porque o navegador rodava a `shell.js` da véspera.

O resumo é do **conteúdo**, e não da data do arquivo nem da versão do sistema: um `git checkout`
muda a data sem mudar o arquivo, e uma implantação muda a versão sem mudar a folha — nos dois casos
o cache seria descartado sem motivo (D-003 da `089`).

Com `DEBUG`, o resumo é recalculado a cada página: editou a folha no runserver, a próxima página já
a pede por outro endereço. Sem `DEBUG`, é calculado uma vez por processo — a implantação reinicia o
processo, e o endereço muda se, e só se, o arquivo mudou.

Descartado o `ManifestStaticFilesStorage`, que faz o mesmo no nome do arquivo: exige `collectstatic`
para um `STATIC_ROOT`, e o guia de produção serve os diretórios da release sem coletar (lacuna I-3).
"""

import hashlib
from functools import cache

from django import template
from django.conf import settings
from django.contrib.staticfiles import finders
from django.templatetags.static import static

register = template.Library()


def _resumo(caminho):
    arquivo = finders.find(caminho)
    # Arquivo ausente é erro na página, e não `<link>` quebrado em silêncio: uma folha que não
    # carrega deixa a gestão sem estilo, e ninguém vê o 404 do estático.
    if not arquivo:
        raise template.TemplateSyntaxError(f"estático inexistente: {caminho}")
    with open(arquivo, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]


_resumo_do_processo = cache(_resumo)


@register.simple_tag
def estatico(caminho):
    resumo = _resumo(caminho) if settings.DEBUG else _resumo_do_processo(caminho)
    return f"{static(caminho)}?v={resumo}"
