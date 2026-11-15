"""Segunda passada: o mesmo registro, mais o número «A ocupar» de cada recorte apurado."""

import re

import registro_da_ocupacao as r
from registro_da_ocupacao import pytest_configure  # noqa: F401

A_OCUPAR = re.compile(r"<li><strong>(\d+)</strong>A ocupar</li>")
_original = r._estados


def _estados(html):
    pagina, blocos = _original(html)
    for bloco, secao in zip(blocos, html.split(r.CORTE)[1:]):
        achado = A_OCUPAR.search(secao.split("</section>")[0])
        if achado:
            bloco.append("a_ocupar_zero" if achado.group(1) == "0" else "a_ocupar_positivo")
            bloco.sort()
    return pagina, blocos


r._estados = _estados
r.SECAO["a_ocupar_zero"] = "\x00"
r.SECAO["a_ocupar_positivo"] = "\x00"
