"""Anexos: pelo vínculo do documento e pela citação do rótulo (070, `R-012`, `FR-1430`).

O sistema nunca lê o que há dentro de um anexo (`editais/models/anexos.py`). A resposta, por isso,
só pode **levar** ao anexo, e dizer que o detalhe está lá — nunca afirmar o que ele contém. A
pontuação da prova de títulos do 92/2026 está no Anexo IV, e nenhum número dela está no conteúdo
publicado.

A citação é comparada ao **começo do rótulo** ("ANEXO IV — FICHA…"), que é como o Edital rotula. Um
"anexo" sem identificador não é citação.
"""

from __future__ import annotations

import re

from processo_seletivo.shared.texto import dobrar

#: Algarismo romano **válido**, e não qualquer palavra feita das letras dele: "anexo civil" não é
#: citação (revisão de 12/10).
ROMANO = r"(?=[ivxlcdm])m{0,3}(?:cm|cd|d?c{0,3})(?:xc|xl|l?x{0,3})(?:ix|iv|v?i{0,3})"
IDENTIFICADOR = rf"(?:{ROMANO}|\d+)\b"
#: O anexo **de outra norma** não é do Edital: "Anexo I do Decreto nº 9.508/2018".
DE_OUTRA_NORMA = (
    r"(?!\s*,?\s*d[oa]s?\s+(?:decreto|lei|portaria|resolu[cç][aã]o|instru[cç][aã]o|"
    r"regulamento|norma))"
)
CITACAO = re.compile(
    rf"\banexos?\s+({IDENTIFICADOR}(?:\s*(?:,|\be\b)\s*{IDENTIFICADOR})*){DE_OUTRA_NORMA}",
    re.IGNORECASE,
)
SEPARADOR = re.compile(r"\s*(?:,|\be\b)\s*", re.IGNORECASE)


def _normalizado(identificador: str) -> str:
    """Dobrado, e o número sem zero à esquerda: "Anexo 04" é o "Anexo 4"."""
    identificador = dobrar(identificador.strip())
    return str(int(identificador)) if identificador.isdigit() else identificador


def identificador_do_rotulo(rotulo: str) -> str | None:
    achado = CITACAO.match((rotulo or "").strip())
    return _normalizado(SEPARADOR.split(achado.group(1))[0]) if achado else None


def citados(texto: str) -> tuple[str, ...]:
    """Os identificadores citados no texto, dobrados e sem repetição, na ordem em que aparecem.

    "Anexos III e IV" cita os dois.
    """
    vistos = []
    for achado in CITACAO.finditer(texto or ""):
        for parte in SEPARADOR.split(achado.group(1)):
            identificador = _normalizado(parte)
            if identificador and identificador not in vistos:
                vistos.append(identificador)
    return tuple(vistos)


def por_identificador(conteudo) -> dict:
    """`identificador citado` → anexo publicado."""
    resultado = {}
    for anexo in conteudo.get("attachments") or []:
        identificador = identificador_do_rotulo(anexo.get("label", ""))
        if identificador is not None:
            resultado.setdefault(identificador, anexo)
    return resultado


def resolver(textos, conteudo):
    """`(anexos encontrados, identificadores sem anexo)` para os textos dados."""
    publicados = por_identificador(conteudo)
    encontrados, inexistentes = [], []
    for texto in textos:
        for identificador in citados(texto):
            anexo = publicados.get(identificador)
            if anexo is None:
                if identificador not in inexistentes:
                    inexistentes.append(identificador)
            elif anexo not in encontrados:
                encontrados.append(anexo)
    return tuple(encontrados), tuple(inexistentes)


def textos_do_conteudo(conteudo):
    """Todo texto livre do conteúdo em que um anexo pode ser citado (para os pontos de revisão)."""
    textos = []
    for secao in conteudo.get("sections") or []:
        textos.append(secao.get("content") or "")
    for etapa in conteudo.get("stages") or []:
        textos.append(etapa.get("name") or "")
    for documento in conteudo.get("documentRequirements") or []:
        textos.append(documento.get("instructions") or "")
    for evento in conteudo.get("schedule") or []:
        textos.append(evento.get("description") or "")
    for perfil in conteudo.get("profiles") or []:
        textos.extend(perfil.get("requirements") or [])
        textos.append(perfil.get("duties") or "")
        textos.append(perfil.get("description") or "")
    return textos
