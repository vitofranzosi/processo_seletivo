"""Vídeos sintéticos para a suíte da verificação por vídeo (166, research T-007).

**Nenhum vídeo real, e nenhuma imagem**: só os contêineres, montados à mão — as caixas do MP4 e os
elementos do WebM que a conferência técnica lê, e um corpo de bytes sem significado no lugar da mídia.
É o suficiente para a assinatura, a duração, o tamanho e o resumo; e a suíte não precisa de
codificador nem de amostra gravada.
"""

import hashlib
import struct


def _caixa(tipo: bytes, corpo: bytes) -> bytes:
    return struct.pack(">I4s", 8 + len(corpo), tipo) + corpo


def mp4(duracao=4.8, *, escala=1000, fragmentado=False, corpo=4096, moov_no_fim=False) -> bytes:
    """Um MP4 mínimo: `ftyp`, `moov` com `mvhd` (e `mvex/mehd`, se fragmentado) e um `mdat`."""
    ftyp = _caixa(b"ftyp", b"isom" + struct.pack(">I", 512) + b"isomiso2avc1mp41")
    unidades = round(duracao * escala)
    mvhd = _caixa(
        b"mvhd",
        b"\x00\x00\x00\x00"
        + struct.pack(">IIII", 0, 0, escala, 0 if fragmentado else unidades)
        + b"\x00" * 80,
    )
    filhos = mvhd
    if fragmentado:
        filhos += _caixa(b"mvex", _caixa(b"mehd", b"\x00\x00\x00\x00" + struct.pack(">I", unidades)))
    moov = _caixa(b"moov", filhos)
    mdat = _caixa(b"mdat", bytes((i * 7) % 251 for i in range(corpo)))
    return ftyp + (mdat + moov if moov_no_fim else moov + mdat)


def _vint_tamanho(n: int) -> bytes:
    return bytes([0x01]) + n.to_bytes(7, "big")


def _elemento(ident: int, corpo: bytes) -> bytes:
    bruto = ident.to_bytes((ident.bit_length() + 7) // 8, "big")
    return bruto + _vint_tamanho(len(corpo)) + corpo


def webm(duracao=4.8, *, com_duracao=True, corpo=4096, tamanho_desconhecido=False) -> bytes:
    """Um WebM mínimo: cabeçalho EBML com `DocType` `webm`, e o segmento com `Info` e um `Cluster`.

    `com_duracao=False` é o WebM do `MediaRecorder` do Chrome, que não grava o elemento `Duration`.
    """
    cabecalho = _elemento(0x1A45DFA3, _elemento(0x4282, b"webm"))
    info = _elemento(0x2AD7B1, (1_000_000).to_bytes(3, "big"))
    if com_duracao:
        info += _elemento(0x4489, struct.pack(">d", duracao * 1000))
    cluster = _elemento(0x1F43B675, bytes((i * 11) % 251 for i in range(corpo)))
    filhos = _elemento(0x1549A966, info) + cluster
    if tamanho_desconhecido:
        segmento = bytes.fromhex("18538067") + b"\x01\xff\xff\xff\xff\xff\xff\xff" + filhos
    else:
        segmento = _elemento(0x18538067, filhos)
    return cabecalho + segmento


def resumo(dados: bytes) -> str:
    return hashlib.sha256(dados).hexdigest()
