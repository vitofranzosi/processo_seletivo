"""A fonte que o Edital embute, lida dos arquivos versionados (069, D-002, R-005, R-007).

O Edital deixa de declarar a Helvetica sem arquivo — que cada leitor substitui pela que tem, e o
poppler desenhava o negrito como regular (ED-14 da auditoria) — e passa a embutir a **Edital Sans**,
Regular e Bold: o subconjunto WinAnsi da Liberation Sans 2.1.5, sob a SIL OFL 1.1, gerado por
`backend/scripts/gerar_subconjunto_da_fonte.py`. A origem, os resumos e a razão do nome estão em
`fontes/ORIGEM.md`.

**Sem dependência nova.** O `fontTools` só existe no roteiro que gera o subconjunto; aqui, o
TrueType é lido pela própria gramática — o diretório de tabelas, `head`, `hhea`, `hmtx`, `cmap`,
`OS/2` e `post` —, que é tudo o que a composição e o descritor da fonte precisam.

**Duas coisas, e só o Edital as usa** (FR-1383): a métrica, com as larguras da própria fonte
(FR-1381), e os objetos do PDF que a embutem. O comprovante e a divulgação continuam com a
Helvetica de `pdf.py`.
"""

import hashlib
import struct
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from processo_seletivo.publicacoes.domain import grafia

PASTA = Path(__file__).resolve().parent / "fontes"

# Os nomes de recurso são os de `pdf.py` (`REGULAR`, `NEGRITO`): as páginas continuam a desenhar com
# `/F1` e `/F2`, e só o objeto para onde eles apontam muda. Repetidos aqui, e não importados, porque
# `pdf.py` importa este módulo.
REGULAR, NEGRITO = "F1", "F2"
ARQUIVOS = {REGULAR: "EditalSans-Regular.ttf", NEGRITO: "EditalSans-Bold.ttf"}
# Os resumos dos arquivos versionados, que `ORIGEM.md` registra e o teste confere.
SHA256 = {
    "EditalSans-Regular.ttf": "62b13299f160417649de8979ee1b72f5c276af2db2c3e9933d5e9054b4aa71e4",
    "EditalSans-Bold.ttf": "465a6122bcd959c9a9a4f392cc67ecec886d28397019e4ef9d6cff6fd832508c",
    "EditalSans-Regular.ttf.zlib": (
        "0e5bb7cb264840f34216a022b72c4f6dc90423803eebe5a002b19ae5f6c0a469"
    ),
    "EditalSans-Bold.ttf.zlib": "0c64e1441ce1315d27d47ebe11c717e00b5d7a3ab0740dc472328148cb4afd5b",
}
# O prefixo de subconjunto que o PDF pede antes do nome da fonte embutida em parte: seis maiúsculas
# e "+". Fixo, e não sorteado, porque o documento tem de sair com os mesmos bytes.
PREFIXO = {REGULAR: "EDITAA", NEGRITO: "EDITAB"}
# O traço vertical dominante, que o descritor pede e o TrueType não guarda: os valores usuais para
# um sem-serifa regular e negrito.
HASTE = {REGULAR: 80, NEGRITO: 140}

# Um caractere fora do WinAnsi mede como o glifo mais largo, pela regra da Helvetica de `pdf.py`:
# erra quebrando cedo, e nunca estourando a margem. Na publicação ele já foi recusado (`grafia`).
LARGURA_DESCONHECIDA = 1000


def _codigos_winansi():
    """`{byte: caractere}` do espaço ao 255, para os bytes que o `cp1252` define."""
    codigos = {}
    for byte in range(32, 256):
        try:
            codigos[byte] = bytes([byte]).decode("cp1252")
        except UnicodeDecodeError:
            continue
    return codigos


WINANSI = _codigos_winansi()


@dataclass(frozen=True)
class FonteTrueType:
    """O que a composição e o descritor do PDF leem de um TrueType."""

    nome: str
    dados: bytes
    comprimido: bytes
    # Largura de cada byte WinAnsi, em milésimos de em.
    larguras: dict
    caixa: tuple
    ascendente: int
    descendente: int
    altura_das_maiusculas: int
    angulo_italico: float


def _tabelas(dados):
    (quantas,) = struct.unpack(">H", dados[4:6])
    tabelas = {}
    for indice in range(quantas):
        etiqueta, _, inicio, tamanho = struct.unpack(
            ">4sIII", dados[12 + 16 * indice : 28 + 16 * indice]
        )
        tabelas[etiqueta.decode("latin-1")] = dados[inicio : inicio + tamanho]
    return tabelas


def _glifos_por_ponto(cmap):
    """O mapa Unicode → glifo do subformato 4 da plataforma Windows (3, 1)."""
    (_, quantas) = struct.unpack(">HH", cmap[:4])
    for indice in range(quantas):
        plataforma, codificacao, inicio = struct.unpack(
            ">HHI", cmap[4 + 8 * indice : 12 + 8 * indice]
        )
        if (plataforma, codificacao) == (3, 1):
            break
    else:
        raise ValueError("TrueType sem o mapa Unicode do Windows (3, 1).")
    tabela = cmap[inicio:]
    (formato, _, _, segmentos_x2) = struct.unpack(">HHHH", tabela[:8])
    if formato != 4:
        raise ValueError(f"Mapa Unicode em formato {formato}, e não 4.")
    segmentos = segmentos_x2 // 2
    finais = struct.unpack(f">{segmentos}H", tabela[14 : 14 + segmentos_x2])
    base = 16 + segmentos_x2
    iniciais = struct.unpack(f">{segmentos}H", tabela[base : base + segmentos_x2])
    deltas = struct.unpack(f">{segmentos}h", tabela[base + segmentos_x2 : base + 2 * segmentos_x2])
    # `endCode`, o `reservedPad`, `startCode`, `idDelta` e então `idRangeOffset`.
    deslocamentos_em = base + 2 * segmentos_x2
    deslocamentos = struct.unpack(
        f">{segmentos}H", tabela[deslocamentos_em : deslocamentos_em + segmentos_x2]
    )
    mapa = {}
    for segmento in range(segmentos):
        for ponto in range(iniciais[segmento], finais[segmento] + 1):
            if ponto == 0xFFFF:
                continue
            if deslocamentos[segmento] == 0:
                glifo = (ponto + deltas[segmento]) & 0xFFFF
            else:
                endereco = (
                    deslocamentos_em
                    + 2 * segmento
                    + deslocamentos[segmento]
                    + 2 * (ponto - iniciais[segmento])
                )
                (glifo,) = struct.unpack(">H", tabela[endereco : endereco + 2])
                if glifo:
                    glifo = (glifo + deltas[segmento]) & 0xFFFF
            if glifo:
                mapa[ponto] = glifo
    return mapa


def ler(arquivo):
    """O TrueType versionado, com as larguras dos bytes WinAnsi e os dados do descritor."""
    dados = (PASTA / arquivo).read_bytes()
    comprimido = (PASTA / f"{arquivo}.zlib").read_bytes()
    tabelas = _tabelas(dados)
    (unidades,) = struct.unpack(">H", tabelas["head"][18:20])
    caixa = struct.unpack(">4h", tabelas["head"][36:44])
    (metricas,) = struct.unpack(">H", tabelas["hhea"][34:36])
    avancos = [
        struct.unpack(">H", tabelas["hmtx"][4 * indice : 4 * indice + 2])[0]
        for indice in range(metricas)
    ]
    glifos = _glifos_por_ponto(tabelas["cmap"])

    def em_milesimos(valor):
        return round(valor * 1000 / unidades)

    larguras = {}
    for byte, caractere in WINANSI.items():
        glifo = glifos.get(ord(caractere))
        if glifo is None:
            continue
        larguras[byte] = em_milesimos(avancos[min(glifo, metricas - 1)])
    os2 = tabelas["OS/2"]
    ascendente, descendente = struct.unpack(">hh", os2[68:72])
    (versao,) = struct.unpack(">H", os2[:2])
    maiusculas = struct.unpack(">h", os2[88:90])[0] if versao >= 2 else 700
    (angulo,) = struct.unpack(">i", tabelas["post"][4:8])
    return FonteTrueType(
        nome=arquivo.removesuffix(".ttf"),
        dados=dados,
        comprimido=comprimido,
        larguras=larguras,
        caixa=tuple(em_milesimos(valor) for valor in caixa),
        ascendente=em_milesimos(ascendente),
        descendente=em_milesimos(descendente),
        altura_das_maiusculas=em_milesimos(maiusculas),
        angulo_italico=angulo / 65536,
    )


@cache
def fontes():
    """As duas fontes do Edital, lidas uma vez por processo."""
    return {recurso: ler(arquivo) for recurso, arquivo in ARQUIVOS.items()}


def conferir():
    """Os arquivos são os que `ORIGEM.md` registra? `{arquivo: resumo}` dos que não são."""
    divergentes = {}
    for arquivo, esperado in SHA256.items():
        resumo = hashlib.sha256((PASTA / arquivo).read_bytes()).hexdigest()
        if resumo != esperado:
            divergentes[arquivo] = resumo
    return divergentes


class MetricaEmbutida:
    """A métrica do Edital: as larguras da fonte que o arquivo embute (FR-1381).

    **Mede o que vai ser desenhado**, como a da Helvetica: o texto passa por `grafia` antes, para
    que um espaço de largura zero colado do Word não ocupe largura. Corrige, por construção, os
    caracteres que a tabela da Helvetica subestimava — "í", "ì", "î", "ï" e, no negrito, "ª" e
    "º" —, e com eles a linha justificada que passava da margem.
    """

    def largura(self, texto, tamanho, fonte=REGULAR):
        larguras = fontes()[NEGRITO if fonte == NEGRITO else REGULAR].larguras
        total = 0
        for caractere in grafia.normalizar(str(texto)):
            try:
                byte = caractere.encode("cp1252")[0]
            except (UnicodeEncodeError, IndexError):
                total += LARGURA_DESCONHECIDA
                continue
            total += larguras.get(byte, LARGURA_DESCONHECIDA)
        return total * tamanho / 1000


METRICA = MetricaEmbutida()


def objetos(primeiro):
    """Os objetos das duas fontes, numerados a partir de `primeiro`: `(objetos, {recurso: id})`.

    Por fonte, três: o dicionário `/TrueType` com as larguras do WinAnsi, o descritor, e o arquivo
    comprimido (`/FontFile2`, com `/Length1` — o tamanho descomprimido). **O dicionário do arquivo
    não é `<< /Length N >>`**, e é de propósito: os extratores de texto dos testes leem só esse
    formato, e o arquivo da fonte não é página (R-006).
    """
    saida, ids = [], {}
    numero = primeiro
    for recurso in (REGULAR, NEGRITO):
        fonte = fontes()[recurso]
        nome = f"{PREFIXO[recurso]}+{fonte.nome}"
        larguras = " ".join(str(fonte.larguras.get(byte, 0)) for byte in range(32, 256))
        ids[recurso] = numero
        saida.append(
            f"<< /Type /Font /Subtype /TrueType /BaseFont /{nome} /FirstChar 32 /LastChar 255 "
            f"/Widths [{larguras}] /Encoding /WinAnsiEncoding "
            f"/FontDescriptor {numero + 1} 0 R >>".encode()
        )
        caixa = " ".join(str(valor) for valor in fonte.caixa)
        saida.append(
            f"<< /Type /FontDescriptor /FontName /{nome} /Flags 32 /FontBBox [{caixa}] "
            f"/ItalicAngle {fonte.angulo_italico:g} /Ascent {fonte.ascendente} "
            f"/Descent {fonte.descendente} /CapHeight {fonte.altura_das_maiusculas} "
            f"/StemV {HASTE[recurso]} /MissingWidth {LARGURA_DESCONHECIDA} "
            f"/FontFile2 {numero + 2} 0 R >>".encode()
        )
        saida.append(
            f"<< /Filter /FlateDecode /Length1 {len(fonte.dados)} "
            f"/Length {len(fonte.comprimido)} >>\nstream\n".encode()
            + fonte.comprimido
            + b"\nendstream"
        )
        numero += 3
    return saida, ids
