"""As fontes da peça do kit de divulgação: métrica e subconjunto por fonte livre (119, D-005).

**Cada família da comunicação traz as suas fontes**, e a peça mede com a fonte que vai desenhar —
a regra da `111` (`D-009`), agora por fonte. O texto continua normalizado pela `grafia`, e o
repertório que a peça admite é o dela: o WinAnsi. Cada fonte do kit cobre esse repertório inteiro, e
o teste confere; um caractere que a fonte não desenhe recusa a peça nomeando o caractere e a fonte
(FR-3823, EC-13), em vez de o rasterizador completar com outra fonte.

**A leitura é a do Edital, e o Edital não muda.** O TrueType é lido pelas funções de
`publicacoes/infrastructure/fonte.py`, sem tocar aquele módulo: a métrica e o subconjunto dele
servem ao ato publicado, que é o documento oficial, e ampliá-los para o kit arriscaria o compositor
do PDF.
O que este módulo acrescenta é a medida por ponto Unicode — e não por byte do WinAnsi — e o registro
de várias fontes, cada uma com o arquivo, o peso e o resumo que `kit_ativos/fontes/ORIGEM.md`
registra.

**A Edital Sans é a primeira**, lida no lugar onde o Edital a guarda, para que a peça Institucional
continue a medir exatamente o que media. As fontes das famílias da comunicação entram em
`kit_ativos/fontes/`, com o registro de origem.
"""

import base64
import hashlib
import struct
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from processo_seletivo.publicacoes.domain import grafia
from processo_seletivo.publicacoes.infrastructure import fonte

PASTA = Path(__file__).resolve().parent / "kit_ativos" / "fontes"

# Um caractere fora da fonte mede como o glifo mais largo, pela regra do Edital: erra quebrando
# cedo, e nunca estourando a margem. Na peça ele já foi recusado antes de chegar aqui.
LARGURA_DESCONHECIDA = fonte.LARGURA_DESCONHECIDA


@dataclass(frozen=True)
class FonteDoKit:
    chave: str
    #: O nome que o SVG declara em `font-family` e no `@font-face`.
    familia: str
    peso: int
    caminho: Path
    sha256: str
    #: Os caracteres do repertório que a fonte de origem não desenha, conferidos pela suíte. Não se
    #: desenha glifo pelo projeto: a peça que os pedir é recusada nomeando-os (FR-3823, EC-13).
    sem_grafia: str = ""

    @property
    def arquivo(self):
        return self.caminho.name


@dataclass(frozen=True)
class Medidas:
    """O que a composição lê de uma fonte: as larguras e a altura das linhas, em milésimos de em."""

    dados: bytes
    larguras: dict
    ascendente: int
    descendente: int


def _edital_sans(chave, recurso, peso):
    arquivo = fonte.ARQUIVOS[recurso]
    return FonteDoKit(chave, "Edital Sans", peso, fonte.PASTA / arquivo, fonte.SHA256[arquivo])


def _do_kit(chave, familia, peso, arquivo, sha256, sem_grafia=""):
    return FonteDoKit(chave, familia, peso, PASTA / arquivo, sha256, sem_grafia)


FONTES = {
    item.chave: item
    for item in (
        _edital_sans("edital-sans-regular", fonte.REGULAR, 400),
        _edital_sans("edital-sans-negrito", fonte.NEGRITO, 700),
        # A Pós Lato Sensu (119, incremento 2): subconjuntos WinAnsi da Poppins, OFL sem nome
        # reservado, gerados por `scripts/gerar_subconjunto_do_kit.py`.
        _do_kit(
            "poppins-regular",
            "Poppins",
            400,
            "Poppins-Regular.ttf",
            "1a28e1d7124696a93c1e5894aff6dc0ca74c72c71777ed8fb8c747c2a657a3aa",
        ),
        _do_kit(
            "poppins-seminegrito",
            "Poppins",
            600,
            "Poppins-SemiBold.ttf",
            "fefe0b3d545ead98fb66a28b5f23fc9b570d5eeb025c11fe3ae0252531892a7e",
        ),
        _do_kit(
            "poppins-negrito",
            "Poppins",
            700,
            "Poppins-Bold.ttf",
            "7422528506b3264a11d167a0de0e757a322ded7c08f4fca6df4a7d43d02951f5",
        ),
        # A UAB/bolsista (119, incremento 3c): a Anton, OFL sem nome reservado, no mesmo roteiro.
        _do_kit(
            "anton-regular",
            "Anton",
            400,
            "Anton-Regular.ttf",
            "a7ad74685f149ccc513aaa57de7cfbeeba676d57b4328be0240ca139b85ba76d",
        ),
        # A FIC (119, incremento 3a): subconjuntos WinAnsi de três famílias OFL sem nome
        # reservado, do mesmo `google/fonts` e pelo mesmo roteiro.
        _do_kit(
            "archivo-black",
            "Archivo Black",
            400,
            "ArchivoBlack-Regular.ttf",
            "24efaface31f64b28d2e34a09753230ef00181f1fe1188bf1e15c9522b426e8a",
        ),
        _do_kit(
            "barlow-semi-condensed-medio",
            "Barlow Semi Condensed",
            500,
            "BarlowSemiCondensed-Medium.ttf",
            "feeb1c5417579e1b9e5b2e5f8a0bfc6a7e9f84fac02b947a9354890285c21cac",
        ),
        _do_kit(
            "barlow-semi-condensed-negrito",
            "Barlow Semi Condensed",
            700,
            "BarlowSemiCondensed-Bold.ttf",
            "6e904ce4579c543817016f540d27bb8bfbf706d7aac8d1eccaedd5721dca0cda",
        ),
        _do_kit(
            "space-mono-negrito",
            "Space Mono",
            700,
            "SpaceMono-Bold.ttf",
            "81c793fc957300ca0521c18f7ebd2ca3f751c373182ceafcfc63cd171c1447d5",
        ),
        # A Aperfeiçoamento (119, incremento 3d): instâncias estáticas das variáveis do Google
        # Fonts, no peso dos arquivos da comunicação, e o mesmo subconjunto WinAnsi.
        _do_kit(
            "unbounded-regular",
            "Unbounded",
            400,
            "Unbounded-Regular.ttf",
            "94c048a78a9b3ff3023dd970d1ca93c5c9918c32acd3c2f1948b2d41bfc3aba2",
            # O micro (U+00B5) não está na Unbounded de origem, em nenhum peso.
            sem_grafia="µ",
        ),
        _do_kit(
            "lexend-extranegrito",
            "Lexend",
            800,
            "Lexend-ExtraBold.ttf",
            "64c5421403046c7f6f61db724c6d897a5369c303a466de5ad84f7a7d2e518268",
        ),
    )
}


def repertorio():
    """Os caracteres que a `grafia` deixa chegar à peça: o WinAnsi imprimível."""
    return tuple(c for c in fonte.WINANSI.values() if grafia.representavel(c))


@cache
def medidas(chave):
    """A fonte do kit lida uma vez por processo, com as larguras dos caracteres do repertório."""
    dados = FONTES[chave].caminho.read_bytes()
    # As funções privadas do leitor do Edital, e não uma cópia delas: duas leituras do mesmo
    # TrueType divergiriam na primeira tabela que uma delas corrigisse.
    tabelas = fonte._tabelas(dados)
    (unidades,) = struct.unpack(">H", tabelas["head"][18:20])
    (quantas,) = struct.unpack(">H", tabelas["hhea"][34:36])
    avancos = [
        struct.unpack(">H", tabelas["hmtx"][4 * indice : 4 * indice + 2])[0]
        for indice in range(quantas)
    ]
    glifos = fonte._glifos_por_ponto(tabelas["cmap"])

    def em_milesimos(valor):
        return round(valor * 1000 / unidades)

    larguras = {}
    for caractere in repertorio():
        glifo = glifos.get(ord(caractere))
        if glifo is not None:
            larguras[caractere] = em_milesimos(avancos[min(glifo, quantas - 1)])
    ascendente, descendente = struct.unpack(">hh", tabelas["OS/2"][68:72])
    return Medidas(dados, larguras, em_milesimos(ascendente), em_milesimos(descendente))


class Metrica:
    """A largura de um texto numa fonte do kit. `fonte` é a chave em `FONTES`.

    Tem a forma da métrica do Edital, porque é a quebra do Edital que a usa (`pdf.quebrar`).
    """

    def largura(self, texto, tamanho, fonte):
        larguras = medidas(fonte).larguras
        total = sum(
            larguras.get(caractere, LARGURA_DESCONHECIDA)
            for caractere in grafia.normalizar(str(texto))
        )
        return total * tamanho / 1000


METRICA = Metrica()


def sem_glifo(texto, chave):
    """Os caracteres do texto que a fonte não desenha, na ordem, sem repetir (FR-3823)."""
    larguras = medidas(chave).larguras
    faltam = []
    for caractere in grafia.normalizar(str(texto)):
        if caractere not in larguras and caractere not in faltam:
            faltam.append(caractere)
    return faltam


def arquivos(chaves):
    """Os caminhos das fontes, para o rasterizador, sem repetir e na ordem pedida."""
    return tuple(dict.fromkeys(str(FONTES[chave].caminho) for chave in chaves))


def resumos(chaves):
    """`{arquivo: sha256}` das fontes, na ordem pedida, para o manifesto."""
    return {FONTES[chave].arquivo: FONTES[chave].sha256 for chave in dict.fromkeys(chaves)}


def font_face(chaves):
    """O `@font-face` de cada fonte em `data:`, na ordem pedida, para o SVG exportado."""
    regras = []
    for chave in dict.fromkeys(chaves):
        item = FONTES[chave]
        dados = base64.b64encode(medidas(chave).dados).decode("ascii")
        regras.append(
            f'@font-face{{font-family:"{item.familia}";font-weight:{item.peso};'
            f'src:url(data:font/ttf;base64,{dados}) format("truetype")}}'
        )
    return "".join(regras)


def conferir():
    """Os arquivos são os registrados? `{arquivo: resumo}` dos que não são."""
    divergentes = {}
    for item in FONTES.values():
        resumo = hashlib.sha256(item.caminho.read_bytes()).hexdigest()
        if resumo != item.sha256:
            divergentes[item.arquivo] = resumo
    return divergentes
