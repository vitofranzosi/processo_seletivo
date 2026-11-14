"""O cabeçalho `Range` de um pedido de vídeo (166, FR-7131, T-005).

Sem ele, o `<video>` do Safari não avança nem volta. Um intervalo só: `bytes=a-b`, `bytes=a-` e
`bytes=-n`. Vários intervalos, ou um cabeçalho que não se entende, são ignorados e o arquivo vai
inteiro — é o que a RFC 9110 permite, e o reprodutor nunca os pede.
"""

import re

_UM = re.compile(r"^bytes=(\d*)-(\d*)$")


class Insatisfazivel(ValueError):
    """O intervalo começa além do fim: 416."""


def ler(cabecalho, tamanho) -> tuple[int, int] | None:
    """`(inicio, fim)` inclusivo, ou `None` para o arquivo inteiro."""
    if not cabecalho:
        return None
    casado = _UM.match(cabecalho.strip())
    if not casado:
        return None
    inicio, fim = casado.groups()
    if not inicio and not fim:
        return None
    if not inicio:
        sufixo = int(fim)
        if sufixo == 0:
            raise Insatisfazivel
        return max(tamanho - sufixo, 0), tamanho - 1
    inicio = int(inicio)
    if inicio >= tamanho:
        raise Insatisfazivel
    fim = tamanho - 1 if not fim else min(int(fim), tamanho - 1)
    if fim < inicio:
        return None
    return inicio, fim
