"""Fatia o texto de um PDF (`pdftotext -layout`) em trechos consecutivos, por âncoras ordenadas.

Cada âncora é o começo literal de um trecho, procurado a partir do fim do anterior, com espaços em branco
tratados como equivalentes. Os rodapés de página saem do fluxo antes do corte. A função confere que a
concatenação dos trechos reproduz o texto inteiro: é isso que garante a cobertura integral.
"""

import re
import subprocess

RODAPE = re.compile(r"^\s*Edital \S+ · Verificação [0-9a-f]+…\s+Página (\d+) de (\d+)\s*$")


def paginas(pdf):
    saida = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout
    return saida.split("\f")


def fluxo(pdf):
    """O texto corrido sem rodapés, a página de cada caractere e os rodapés encontrados."""
    pedacos, pags, rodapes = [], [], []
    for n, pagina in enumerate(paginas(pdf), 1):
        for linha in pagina.splitlines():
            if RODAPE.match(linha):
                rodapes.append((n, linha.strip()))
            elif linha.strip():
                s = linha.rstrip() + "\n"
                pedacos.append(s)
                pags.extend([n] * len(s))
    return "".join(pedacos), pags, rodapes


def _padrao(ancora):
    return re.compile(r"\s+".join(re.escape(p) for p in ancora.split()))


def fatiar(pdf, linhas):
    texto, pags, rodapes = fluxo(pdf)
    pos, inicios, faltas = 0, [], []
    for i, linha in enumerate(linhas):
        achado = _padrao(linha["ancora"]).search(texto, pos)
        if not achado:
            faltas.append((i, linha["ancora"], texto[pos : pos + 200]))
            inicios.append(None)
            continue
        if i == 0 and texto[: achado.start()].strip():
            faltas.append((i, "TEXTO ANTES DA PRIMEIRA ÂNCORA", texto[: achado.start()]))
        inicios.append(achado.start())
        pos = achado.end()
    if faltas:
        for falta in faltas:
            print("FALTA:", falta)
        raise SystemExit(1)
    out = []
    for i, linha in enumerate(linhas):
        a = inicios[i]
        b = inicios[i + 1] if i + 1 < len(linhas) else len(texto)
        bruto = texto[a:b]
        out.append(
            dict(
                linha,
                bruto=bruto.rstrip("\n"),
                texto=" ".join(bruto.split()),
                pag_ini=pags[a],
                pag_fim=pags[max(a, b - 2)],
            )
        )
    juntos = "".join(o["bruto"] for o in out)
    assert re.sub(r"\s", "", juntos) == re.sub(r"\s", "", texto), "cobertura incompleta"
    return out, rodapes
