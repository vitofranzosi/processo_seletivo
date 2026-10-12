"""Do conteúdo publicado aos cartões de texto e de dado (070, `R-010`, `FR-1431`, `FR-1433`).

**O texto do Edital sai como está.** Sem `strip`, sem normalização, sem corte: o cartão "Texto do
Edital" é a cadeia que o conteúdo publicado guarda naquele caminho, e o teste do `SC-534` compara
uma com a outra. Qualquer tratamento aqui faria o cartão afirmar sobre o Edital um texto que ele
não tem.

**O lugar é dito pelo nome, nunca pelo número impresso.** A numeração do documento é posicional e
muda quando uma Retificação esvazia uma seção (a do 92/2026 renumerou da 7 em diante). O título da
seção, o código do Perfil e o tipo do Evento não mudam com ela.

**Conteúdo de esquema anterior é lido como está** (`FR-1416`): campo ausente é "não declarado", e o
conteúdo publicado não é convertido — a consulta pública faz o mesmo, pela razão de `elevar`.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.utils.dateparse import parse_datetime

from processo_seletivo.duvidas.domain.estruturas import DADO, TEXTO, Referencia
from processo_seletivo.publicacoes.infrastructure import humano
from processo_seletivo.shared.tempo import ZONA

# ---- endereços ------------------------------------------------------------------------------


def caminho_do_perfil(perfil) -> str:
    return f"/profiles/id={perfil['id']}"


def caminho_da_secao(secao) -> str:
    return f"/sections/id={secao['id']}/content"


def caminho_do_evento(evento) -> str:
    return f"/schedule/id={evento['id']}"


def caminho_do_documento(documento) -> str:
    return f"/documentRequirements/id={documento['id']}"


def caminho_da_etapa(etapa) -> str:
    return f"/stages/id={etapa['id']}"


def caminho_do_marco(perfil, marco) -> str:
    return f"{caminho_do_perfil(perfil)}/classificationMilestones/id={marco['id']}"


# ---- onde está, para quem lê ----------------------------------------------------------------


def onde_perfil(perfil) -> str:
    return f"Perfil {perfil.get('code', '')} — {perfil.get('name', '')}"


def onde_secao(secao) -> str:
    return f"Seção “{secao.get('title', '')}”"


def nome_do_evento(evento) -> str:
    """O Evento como o documento o imprime na coluna "Evento": a descrição, e o tipo só sem ela
    (`pdf._cronograma`). Pelo tipo, quem conferia no PDF não achava o nome (validação de 12/10)."""
    return evento.get("description") or evento.get("type") or ""


def onde_evento(evento) -> str:
    return f"Cronograma — evento “{nome_do_evento(evento)}”"


def onde_documento(documento) -> str:
    return f"Documento exigido “{documento.get('name', '')}”"


def onde_etapa(etapa) -> str:
    return f"Etapa “{etapa.get('name', '')}”"


def onde_marco(perfil, marco) -> str:
    return f"{onde_perfil(perfil)} — marco “{marco.get('name') or marco.get('code') or ''}”"


# ---- buscas --------------------------------------------------------------------------------


def por_id(colecao) -> dict:
    return {str(item.get("id")): item for item in colecao or []}


def perfil_por_codigo(conteudo, codigo):
    for perfil in conteudo.get("profiles") or []:
        if perfil.get("code") == codigo:
            return perfil
    return None


def secao_por_chave(conteudo, chave):
    for secao in conteudo.get("sections") or []:
        if secao.get("key") == chave:
            return secao
    return None


def texto_da_secao(secao) -> str:
    """O texto publicado da seção textual, ou `""` — a gerada não tem texto no conteúdo."""
    if not secao or secao.get("type") != "TEXT":
        return ""
    return secao.get("content") or ""


def paragrafos(texto: str):
    """`(posição, linha)` de cada parágrafo não vazio. O conteúdo publicado separa por `\\n`."""
    return [(posicao, linha) for posicao, linha in enumerate(texto.split("\n")) if linha.strip()]


# ---- cartões -------------------------------------------------------------------------------


def texto(localizacao, caminho, valor, *, posicao=None, rotulo=""):
    """Cartão "Texto do Edital", ou `None` quando não há texto: ausente não é texto vazio."""
    if not isinstance(valor, str) or not valor.strip():
        return None
    return Referencia(
        natureza=TEXTO,
        localizacao=localizacao,
        conteudo=valor,
        caminho=caminho,
        posicao=posicao,
        rotulo=rotulo,
    )


def dado(localizacao, caminho, rotulo, conteudo):
    return Referencia(
        natureza=DADO, localizacao=localizacao, conteudo=conteudo, caminho=caminho, rotulo=rotulo
    )


def secao(conteudo, chave):
    """A seção textual inteira, como texto do Edital (`FR-1420`), ou `None` se vazia ou ausente."""
    encontrada = secao_por_chave(conteudo, chave)
    return texto(
        onde_secao(encontrada or {}),
        caminho_da_secao(encontrada or {"id": ""}),
        texto_da_secao(encontrada),
    )


# ---- valores em palavras ------------------------------------------------------------------


def instante_legivel(valor) -> str:
    """O instante na zona institucional, como o Edital o escreve ("05/10/2026, às 14h")."""
    if not valor:
        return "não declarado"
    try:
        momento = valor if isinstance(valor, datetime) else parse_datetime(str(valor))
    except ValueError:
        # Bem formado e inexistente ("2026-02-30T10:00"): `parse_datetime` levanta, em vez de
        # devolver `None`. Dito como está escrito, e não um 500.
        momento = None
    if momento is None:
        return f"“{valor}”"
    if momento.tzinfo is None:
        # Sem deslocamento, `astimezone` usaria a zona da máquina, e não a do Edital.
        momento = momento.replace(tzinfo=ZONA)
    return humano.instante(momento.astimezone(ZONA))


def numero_legivel(valor) -> str:
    if valor is None or valor == "":
        return "não declarado"
    try:
        return humano.decimal(Decimal(str(valor)))
    except (InvalidOperation, ValueError, TypeError):
        return f"“{valor}”"
