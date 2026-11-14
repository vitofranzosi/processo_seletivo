"""A conferência técnica do contêiner do vídeo: assinatura e duração (166, FR-7120, T-003).

**É a única verificação automática que o sistema faz sobre o vídeo** (R-19, FR-7150): o contêiner,
o tamanho, a duração e o resumo. A leitura percorre caixas (MP4) e elementos (WebM) de topo, e nunca
decodifica imagem nem som — não há biblioteca de mídia, e não haverá: um decodificador é o primeiro
passo de qualquer análise que esta spec proíbe.

**A duração pode faltar.** O `MediaRecorder` do Chrome grava WebM sem o elemento `Duration`, e o MP4
fragmentado pode declarar zero no `mvhd`. Nesses casos quem decide é a duração medida pelo aparelho,
conferida contra o teto; quando o contêiner a declara, é ela que vale.
"""

import struct
from dataclasses import dataclass

MP4 = "video/mp4"
WEBM = "video/webm"
FORMATOS = (MP4, WEBM)
EXTENSAO = {MP4: "mp4", WEBM: "webm"}

_EBML = b"\x1a\x45\xdf\xa3"
_SEGMENTO = 0x18538067
_INFO = 0x1549A966
_ESCALA = 0x2AD7B1
_DURACAO = 0x4489
_DOCTYPE = 0x4282
_CLUSTER = 0x1F43B675
# Leitura de contêiner, e não de conteúdo: um cabeçalho EBML ou uma caixa `moov` maiores que isto
# não são de um vídeo de três minutos gravado no navegador.
_LIMITE_DE_CABECALHO = 4 * 1024 * 1024


@dataclass(frozen=True)
class Conteiner:
    formato: str
    duracao: float | None


class ConteinerInvalido(ValueError):
    pass


def formato_da_assinatura(cabeca: bytes) -> str | None:
    """O formato pela assinatura dos primeiros bytes, ou `None`. A extensão não conta."""
    if len(cabeca) >= 12 and cabeca[4:8] == b"ftyp":
        return MP4
    if cabeca[:4] == _EBML and b"webm" in cabeca[:64]:
        return WEBM
    return None


def ler(arquivo) -> Conteiner:
    """O formato e a duração do arquivo binário; `ConteinerInvalido` se não for vídeo."""
    arquivo.seek(0)
    formato = formato_da_assinatura(arquivo.read(64))
    if formato is None:
        raise ConteinerInvalido("o arquivo não é um vídeo MP4 nem WebM")
    arquivo.seek(0)
    try:
        duracao = _duracao_mp4(arquivo) if formato == MP4 else _duracao_webm(arquivo)
    except (struct.error, EOFError) as erro:
        raise ConteinerInvalido("o contêiner do vídeo está truncado") from erro
    return Conteiner(formato, duracao)


# --- MP4 -------------------------------------------------------------------------------------


def _caixas(arquivo, inicio, fim):
    """As caixas entre `inicio` e `fim`: `(tipo, inicio_do_corpo, fim_da_caixa)`."""
    posicao = inicio
    while fim is None or posicao + 8 <= fim:
        arquivo.seek(posicao)
        cabeca = arquivo.read(8)
        if len(cabeca) < 8:
            return
        tamanho, tipo = struct.unpack(">I4s", cabeca)
        corpo = posicao + 8
        if tamanho == 1:
            (tamanho,) = struct.unpack(">Q", _exato(arquivo, 8))
            corpo += 8
        elif tamanho == 0:
            arquivo.seek(0, 2)
            tamanho = arquivo.tell() - posicao
        if tamanho < corpo - posicao:
            raise ConteinerInvalido("caixa do MP4 com tamanho impossível")
        yield tipo, corpo, posicao + tamanho
        posicao += tamanho


def _duracao_mp4(arquivo):
    for tipo, corpo, fim in _caixas(arquivo, 0, None):
        if tipo != b"moov":
            continue
        if fim - corpo > _LIMITE_DE_CABECALHO:
            raise ConteinerInvalido("caixa moov grande demais")
        escala, duracao, fragmentos = None, None, None
        for filho, corpo_filho, fim_filho in _caixas(arquivo, corpo, fim):
            if filho == b"mvhd":
                escala, duracao = _mvhd(arquivo, corpo_filho)
            elif filho == b"mvex":
                fragmentos = _mehd(arquivo, corpo_filho, fim_filho)
        # O MP4 fragmentado do `MediaRecorder` declara zero no `mvhd` e a duração no `mehd`, que se
        # lê na escala do `mvhd`.
        unidades = duracao or fragmentos
        if not escala or not unidades:
            return None
        return unidades / escala
    raise ConteinerInvalido("o MP4 não tem a caixa moov")


def _mvhd(arquivo, corpo):
    """`(escala, duração em unidades)` da caixa `mvhd`, versões 0 e 1."""
    arquivo.seek(corpo)
    versao = _exato(arquivo, 4)[0]
    if versao == 1:
        _exato(arquivo, 16)
        return struct.unpack(">IQ", _exato(arquivo, 12))
    _exato(arquivo, 8)
    return struct.unpack(">II", _exato(arquivo, 8))


def _mehd(arquivo, corpo, fim):
    for tipo, corpo_filho, _ in _caixas(arquivo, corpo, fim):
        if tipo != b"mehd":
            continue
        arquivo.seek(corpo_filho)
        versao = _exato(arquivo, 4)[0]
        if versao == 1:
            return struct.unpack(">Q", _exato(arquivo, 8))[0]
        return struct.unpack(">I", _exato(arquivo, 4))[0]
    return None


# --- WebM ------------------------------------------------------------------------------------


def _vint(arquivo, *, manter_marca):
    primeiro = _exato(arquivo, 1)[0]
    if primeiro == 0:
        raise ConteinerInvalido("número EBML inválido")
    comprimento = 1
    mascara = 0x80
    while not primeiro & mascara:
        mascara >>= 1
        comprimento += 1
    valor = primeiro if manter_marca else primeiro & (mascara - 1)
    resto = _exato(arquivo, comprimento - 1)
    desconhecido = not manter_marca and valor == mascara - 1
    for byte in resto:
        valor = (valor << 8) | byte
        desconhecido = desconhecido and byte == 0xFF
    return valor, comprimento, desconhecido


def _elementos(arquivo, inicio, fim):
    posicao = inicio
    while fim is None or posicao < fim:
        arquivo.seek(posicao)
        try:
            ident, n_id, _ = _vint(arquivo, manter_marca=True)
        except EOFError:
            return
        tamanho, n_tam, desconhecido = _vint(arquivo, manter_marca=False)
        corpo = posicao + n_id + n_tam
        yield ident, corpo, None if desconhecido else tamanho
        if desconhecido:
            return
        posicao = corpo + tamanho


def _duracao_webm(arquivo):
    for ident, corpo, tamanho in _elementos(arquivo, 0, None):
        if ident == 0x1A45DFA3:
            continue
        if ident != _SEGMENTO:
            continue
        fim = None if tamanho is None else corpo + tamanho
        for filho, corpo_filho, tamanho_filho in _elementos(arquivo, corpo, fim):
            if filho == _CLUSTER:
                return None
            if filho == _INFO and tamanho_filho is not None:
                if tamanho_filho > _LIMITE_DE_CABECALHO:
                    raise ConteinerInvalido("elemento Info grande demais")
                return _info(arquivo, corpo_filho, corpo_filho + tamanho_filho)
            if tamanho_filho is None:
                return None
        return None
    raise ConteinerInvalido("o WebM não tem o segmento")


def _info(arquivo, inicio, fim):
    escala, duracao = 1_000_000, None
    for ident, corpo, tamanho in _elementos(arquivo, inicio, fim):
        arquivo.seek(corpo)
        dados = _exato(arquivo, tamanho)
        if ident == _ESCALA:
            escala = int.from_bytes(dados, "big") or escala
        elif ident == _DURACAO:
            if tamanho == 4:
                (duracao,) = struct.unpack(">f", dados)
            elif tamanho == 8:
                (duracao,) = struct.unpack(">d", dados)
    if not duracao or duracao <= 0:
        return None
    return duracao * escala / 1e9


def _exato(arquivo, n):
    dados = arquivo.read(n)
    if len(dados) != n:
        raise EOFError
    return dados
