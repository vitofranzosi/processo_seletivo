"""O que faz de um PDF composto pelo GPS um arquivo PDF/A-2 (178).

O estudo de 16/11/2026 (`doc/estudo-pdf-a-preservacao-documental-2026-11-16.md`, §4.2) mediu o que
os documentos do GPS descumprem na ISO 19005-2, e era só o que o **arquivo** declara — nenhuma regra
sobre o que a página desenha:

- o identificador do arquivo no trailer (6.1.3), aqui derivado do próprio conteúdo;
- os metadados XMP no catálogo, com a parte e o nível (6.6.2), e coerentes com o `/Info` (6.6.3);
- a condição de saída com um perfil ICC, para o `DeviceRGB` e o `DeviceGray` que as páginas usam
  (6.2.4.3);
- a marca de imprimível nas anotações (6.3.2).

A quinta, a fonte embutida, é de `fonte.py`, e o Edital já a cumpria desde a `069`.

**Sem biblioteca, e por isso sem dependência nova.** A prova de conceito acrescentou esses objetos
com o pikepdf; aqui eles são escritos pelo escritor próprio, como todo o resto do arquivo. A
conversão de PDF pronto foi descartada pelo estudo: o Ghostscript produziu PDF/A "válido" a
partir de arquivo ilegível.

**Determinístico, como todo PDF do GPS.** Sem data, sem produtor, sem identificador sorteado: o
mesmo conteúdo dá os mesmos bytes (a FR-063a da `009`; o SC-523 da `069`). O identificador do
arquivo é um resumo do corpo, e não um número aleatório — o que a norma permite, e o que mantém a
promessa.

**Quem valida é o veraPDF, no CI** (`.github/workflows/backend.yml`, job `pdfa`), sobre um exemplar
de cada tipo (`tests/pdfa/`). Produção não ganha Java.
"""

import hashlib
import re
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from xml.sax.saxutils import escape

PASTA = Path(__file__).resolve().parent / "cor"
PERFIL = "sRGB2014.icc"
# O resumo que `cor/ORIGEM.md` registra e o teste confere.
SHA256_DO_PERFIL = "384b832de3412066743b52a75ee906b6fb9fb8d9e09e936fc2c43223815c6e0a"
# O nome da condição de saída no registro do ICC — o que o perfil descreve.
CONDICAO_DE_SAIDA = "sRGB IEC61966-2.1"

PARTE = 2
# U: o texto se extrai em Unicode, e é o que pega a perda de acento que o B deixa passar (D-006).
# A: além disso, a estrutura lógica — só os relatórios, que já são marcados (FR-8151).
NIVEL_U = "U"
NIVEL_A = "A"
NIVEIS = (NIVEL_U, NIVEL_A)

# `/F 4` é o bit "Print" das anotações: a ISO 19005-2 exige que toda anotação o tenha, e o leitor
# que o encontra desligado pode omitir o link na impressão. Sem ele, a conversão da prova de
# conceito descartou os 18 links do Edital.
ANOTACAO_IMPRIMIVEL = "/F 4"


@cache
def perfil() -> bytes:
    """Os bytes do perfil versionado, lidos uma vez por processo."""
    return (PASTA / PERFIL).read_bytes()


def conferir():
    """O perfil é o que `ORIGEM.md` registra? O resumo dele, se não for; `None`, se for."""
    resumo = hashlib.sha256((PASTA / PERFIL).read_bytes()).hexdigest()
    return None if resumo == SHA256_DO_PERFIL else resumo


@dataclass(frozen=True)
class Descricao:
    """O título e o autor que o arquivo declara — no `/Info` e nos metadados, o mesmo texto."""

    titulo: str | None = None
    autor: str | None = None


# O que o XML 1.0 não admite: os controles C0 fora de tabulação e quebras, os substitutos e os dois
# não caracteres do fim do plano básico. Um deles nos metadados os torna mal-formados, e o arquivo
# deixaria de ser PDF/A sem que nada acusasse.
_FORA_DO_XML = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff\ufffe\uffff]")


def descricao(titulo=None, autor=None) -> Descricao:
    """A descrição do arquivo, saneada **uma vez** para os dois lugares que a declaram (FR-8153).

    Tira o que o XML não admite e trata texto vazio como ausente: um relatório de unidade sem nome
    não declara autor vazio, e não declara autor nenhum. O `/Info` (`pdf._informacao`) e o XMP leem
    o resultado daqui, e por isso concordam por construção.
    """

    def limpo(valor):
        if valor is None:
            return None
        valor = _FORA_DO_XML.sub("", str(valor)).strip()
        return valor or None

    return Descricao(titulo=limpo(titulo), autor=limpo(autor))


def xmp(nivel, descricao=None) -> bytes:
    """Os metadados XMP: a parte e o nível, e o título e o autor da descrição, se houver.

    **Só o que o `/Info` declara**, e com o mesmo texto: a norma cobra que as duas descrições
    concordem, e a mais segura das concordâncias é não dizer nos metadados nada que o `/Info` não
    diga. Sem data de criação, de modificação, nem produtor — o arquivo continua determinístico.
    """
    if nivel not in NIVEIS:
        raise ValueError(f"Nível de PDF/A desconhecido: {nivel!r}.")
    descricao = descricao or Descricao()
    partes = []
    if descricao.titulo is not None:
        partes.append(
            "<dc:title><rdf:Alt>"
            f'<rdf:li xml:lang="x-default">{escape(descricao.titulo)}</rdf:li>'
            "</rdf:Alt></dc:title>"
        )
    if descricao.autor is not None:
        partes.append(
            f"<dc:creator><rdf:Seq><rdf:li>{escape(descricao.autor)}</rdf:li></rdf:Seq></dc:creator>"
        )
    descricao_dc = (
        '<rdf:Description rdf:about="" xmlns:dc="http://purl.org/dc/elements/1.1/">'
        + "".join(partes)
        + "</rdf:Description>"
        if partes
        else ""
    )
    texto = (
        '<?xpacket begin="\ufeff" id="W5M0MpCehiHzreSzNTczkc9d"?>\n'
        '<x:xmpmeta xmlns:x="adobe:ns:meta/">'
        '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
        '<rdf:Description rdf:about="" xmlns:pdfaid="http://www.aiim.org/pdfa/ns/id/">'
        f"<pdfaid:part>{PARTE}</pdfaid:part>"
        f"<pdfaid:conformance>{nivel}</pdfaid:conformance>"
        "</rdf:Description>"
        f"{descricao_dc}"
        "</rdf:RDF></x:xmpmeta>\n"
        '<?xpacket end="r"?>'
    )
    return texto.encode("utf-8")


def objetos(primeiro, *, nivel, descricao=None):
    """Os dois objetos da conformidade, numerados a partir de `primeiro`, e o que o catálogo cita.

    Devolve `(objetos, entradas)`: o perfil ICC e os metadados, e o trecho do catálogo que aponta
    para eles — `/Metadata` e `/OutputIntents`. Quem os acrescenta ao arquivo é
    `pdf._arquivo_em_pdfa`, e só ele.

    **Nenhum dos dois é `<< /Length N >>`**, como o arquivo da fonte (`fonte.objetos`): os
    extratores de texto dos testes leem só esse formato como conteúdo de página. E nenhum é
    comprimido: a norma proíbe filtro no fluxo dos metadados, e o perfil tem 3 KB.
    """
    icc = perfil()
    metadados = xmp(nivel, descricao)
    saida = [
        f"<< /N 3 /Length {len(icc)} >>\nstream\n".encode() + icc + b"\nendstream",
        f"<< /Type /Metadata /Subtype /XML /Length {len(metadados)} >>\nstream\n".encode()
        + metadados
        + b"\nendstream",
    ]
    entradas = (
        f"/Metadata {primeiro + 1} 0 R /OutputIntents [<< /Type /OutputIntent /S /GTS_PDFA1 "
        f"/OutputConditionIdentifier ({CONDICAO_DE_SAIDA}) /RegistryName (http://www.color.org) "
        f"/Info ({CONDICAO_DE_SAIDA}) /DestOutputProfile {primeiro} 0 R >>]"
    )
    return saida, entradas


def identificador(corpo: bytes) -> str:
    """O `/ID` do trailer, derivado do corpo do arquivo: o mesmo conteúdo, o mesmo identificador.

    Os dois elementos iguais, como a norma pede de um arquivo que nunca foi atualizado. Os 16 bytes
    são os primeiros do SHA-256 do corpo — o tamanho que os leitores esperam.
    """
    resumo = hashlib.sha256(corpo).hexdigest()[:32].upper()
    return f"/ID [<{resumo}> <{resumo}>]"
