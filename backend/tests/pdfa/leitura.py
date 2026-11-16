"""O que os testes da `178` leem de um PDF do GPS, sem biblioteca.

Basta a gramática que o escritor próprio escreve: objetos numerados um a um, sem fluxo de objetos,
sem tabela de referências comprimida, sem atualização incremental. Um PDF de fora não passaria por
aqui — e nem precisa.
"""

import re

OBJETO = re.compile(rb"(\d+) 0 obj\n(.*?)\nendobj\n", re.DOTALL)


def objetos(documento):
    return {int(numero): corpo for numero, corpo in OBJETO.findall(documento)}


def referencia(corpo, chave):
    casado = re.search(rb"/" + chave + rb" (\d+) 0 R", corpo)
    return int(casado[1]) if casado else None


def fluxo(corpo):
    """Os bytes entre `stream` e `endstream` de um objeto."""
    return corpo.split(b"\nstream\n", 1)[1].rsplit(b"\nendstream", 1)[0]


def catalogo(documento):
    trailer = documento.rsplit(b"trailer", 1)[1]
    return objetos(documento)[referencia(trailer, b"Root")]


def paginas(documento):
    """Os objetos `/Page`, na ordem do `/Kids`."""
    todos = objetos(documento)
    raiz = todos[referencia(catalogo(documento), b"Pages")]
    kids = raiz.split(b"/Kids [", 1)[1].split(b"]", 1)[0]
    return [todos[int(numero)] for numero in re.findall(rb"(\d+) 0 R", kids)]


def fluxos_das_paginas(documento):
    """O que cada página desenha: os bytes do `/Contents` de cada uma, na ordem."""
    todos = objetos(documento)
    return [fluxo(todos[referencia(pagina, b"Contents")]) for pagina in paginas(documento)]


def anotacoes(documento):
    return [corpo for corpo in objetos(documento).values() if corpo.startswith(b"<< /Type /Annot")]


def contagem(documento, marca):
    return sum(1 for corpo in objetos(documento).values() if marca in corpo)


def cadeia(corpo, chave):
    """Uma cadeia de texto do dicionário: `<FEFF…>` em UTF-16BE, ou `( … )` literal."""
    casado = re.search(rb"/" + chave + rb" (<FEFF[0-9A-F]*>|\((?:\\.|[^\\)])*\))", corpo)
    if casado is None:
        return None
    valor = casado[1]
    if valor.startswith(b"<FEFF"):
        return bytes.fromhex(valor[5:-1].decode()).decode("utf-16-be")
    return valor[1:-1].replace(b"\\(", b"(").replace(b"\\)", b")").replace(b"\\\\", b"\\").decode()
