"""Os passos que os testes da exportação repetem (117): verificar, baixar, abrir o ZIP, estragar
um arquivo e contar quantos arquivos se leram."""

import csv
import hashlib
import io
import re
import zipfile
from pathlib import Path

from django.urls import reverse

from processo_seletivo.formalizacao.application import conjunto, definir, exportar
from tests.fixtures.formalizacao import servido


def verificar(client, edital, **dados):
    dados = dados or {"alcance": "todos"}
    return client.post(reverse("interface:formalizacao-verificar", args=[edital.id]), dados)


def comprovante_da(resposta):
    achado = re.search(r'name="comprovante" value="([^"]+)"', resposta.content.decode())
    return achado.group(1) if achado else None


def baixar(client, edital, comprovante):
    return client.post(
        reverse("interface:formalizacao-baixar", args=[edital.id]), {"comprovante": comprovante}
    )


def exportar_pessoa(client, edital, inscricao):
    return client.post(
        reverse("interface:formalizacao-exportar-pessoa", args=[edital.id, inscricao.id])
    )


def abrir_zip(resposta):
    return zipfile.ZipFile(io.BytesIO(servido(resposta)))


def manifesto(pacote):
    texto = pacote.read("manifesto.csv").decode("utf-8")
    assert texto.startswith("﻿")
    linhas = list(csv.reader(io.StringIO(texto[1:])))
    vazia = linhas.index([])
    return dict(linhas[:vazia]), linhas[vazia + 1], linhas[vazia + 2 :]


def pastas(pacote):
    return sorted({nome.split("/")[0] for nome in pacote.namelist() if "/" in nome})


def sha(conteudo):
    return hashlib.sha256(conteudo).hexdigest()


def documentos_de(edital, inscricao):
    pessoas = conjunto.aptos(
        edital,
        definicao=definir.vigente(edital),
        inscricoes=[inscricao.id],
        com_exportacoes=False,
    )
    return pessoas[0].incluiveis


def apagar(documento):
    Path(documento.fonte.arquivo.path).unlink()


def adulterar(documento, extra=b"!"):
    with open(documento.fonte.arquivo.path, "ab") as arquivo:
        arquivo.write(extra)


def guardar(documento):
    return Path(documento.fonte.arquivo.path).read_bytes()


def restaurar(documento, conteudo):
    Path(documento.fonte.arquivo.path).write_bytes(conteudo)


def contar_leituras(monkeypatch):
    """Quantas pessoas a exportação leu: a prova de que uma recusa veio antes de ler."""
    lidas = []
    original = exportar._ler_pessoa

    def ler(pessoa, pacote, falhas):
        lidas.append(pessoa.inscricao_id)
        return original(pessoa, pacote, falhas)

    monkeypatch.setattr(exportar, "_ler_pessoa", ler)
    return lidas
