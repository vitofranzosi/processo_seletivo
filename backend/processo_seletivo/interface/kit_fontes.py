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


FONTES = {
    item.chave: item
    for item in (
        _edital_sans("edital-sans-regular", fonte.REGULAR, 400),
        _edital_sans("edital-sans-negrito", fonte.NEGRITO, 700),
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
