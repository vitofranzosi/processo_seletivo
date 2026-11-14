"""A entrega mediada do vídeo, com intervalos de bytes (166, FR-7131, research T-005).

Sem `Range`, o `<video>` do Safari não avança nem volta, e o de qualquer navegador baixa o arquivo
inteiro antes de tocar. A entrega **não registra** e **não confere o resumo**: as duas coisas são da
abertura, que acontece uma vez (D-007, T-006). Ela só serve os bytes de um arquivo cujo acesso já foi
decidido.
"""

import os

from django.http import HttpResponse, StreamingHttpResponse

from processo_seletivo.shared.http import marcar_como_privada
from processo_seletivo.verificacao.domain import intervalo

BLOCO = 256 * 1024


def _fatias(caminho, inicio, fim):
    with open(caminho, "rb") as arquivo:
        arquivo.seek(inicio)
        restante = fim - inicio + 1
        while restante > 0:
            bloco = arquivo.read(min(BLOCO, restante))
            if not bloco:
                return
            restante -= len(bloco)
            yield bloco


def _cabecalhos(resposta, formato):
    resposta["Accept-Ranges"] = "bytes"
    resposta["Content-Type"] = formato
    # Assistir, e não baixar: a tela não oferece o botão (FR-7132), e o nome do arquivo não sai.
    resposta["Content-Disposition"] = "inline"
    resposta["X-Content-Type-Options"] = "nosniff"
    return marcar_como_privada(resposta)


def entregar(request, *, caminho, formato):
    """200 com o arquivo inteiro, 206 com o intervalo pedido, ou 416."""
    tamanho = os.path.getsize(caminho)
    try:
        pedido = intervalo.ler(request.headers.get("Range"), tamanho)
    except intervalo.Insatisfazivel:
        resposta = HttpResponse(status=416)
        resposta["Content-Range"] = f"bytes */{tamanho}"
        return _cabecalhos(resposta, formato)
    if pedido is None:
        # O arquivo inteiro pelo mesmo gerador das fatias, e não por `FileResponse`: o gerador fecha o
        # arquivo ao terminar, sem depender de quem fecha a resposta.
        resposta = StreamingHttpResponse(_fatias(caminho, 0, tamanho - 1))
        resposta["Content-Length"] = str(tamanho)
        return _cabecalhos(resposta, formato)
    inicio, fim = pedido
    resposta = StreamingHttpResponse(_fatias(caminho, inicio, fim), status=206)
    resposta["Content-Length"] = str(fim - inicio + 1)
    resposta["Content-Range"] = f"bytes {inicio}-{fim}/{tamanho}"
    return _cabecalhos(resposta, formato)
