"""O canal de atendimento: o do Edital primeiro, o da implantação só na falta (070, `R-011`).

**O sistema acha o canal, e não o escolhe** (`D-005`). O Edital escreve o canal em texto livre, às
vezes em mais de um lugar. Achar é seleção — o parágrafo que fala de dúvida e traz um contato.
Escolher entre dois canais declarados seria interpretar o ato, e o erro mandaria a dúvida para o
lugar errado. Por isso dois canais distintos viram "Fontes divergentes" e ponto para revisão
(`FR-1440`).

**As listas são fechadas e pequenas.** Falso positivo vira ponto para revisão a mais; falso negativo
põe o canal institucional no lugar do do Edital. Os dois aparecem na validação interna, que existe
para isso. "Informações", sozinho, ficou de fora: alcançaria "Informações Gerais sobre o Curso".
"""

from __future__ import annotations

import re

from processo_seletivo.duvidas.domain import leitura
from processo_seletivo.duvidas.domain.estruturas import CANAL_DO_EDITAL, CANAL_INSTITUCIONAL, Canal
from processo_seletivo.shared.texto import dobrar

#: Raízes, comparadas depois de `dobrar()` (sem acento, sem caixa).
TERMOS_DE_DUVIDA = ("duvida", "esclarec", "atendimento", "contato", "informacoes sobre este edital")
#: Palavras que restringem as dúvidas ao canal (`FR-1442`).
TERMOS_DE_EXCLUSIVIDADE = ("exclusivamente", "somente", "unicamente", "apenas")

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
ENDERECO = re.compile(r"(?:https?://|www\.)[^\s,;)]+", re.IGNORECASE)
TELEFONE = re.compile(r"(?<!\d)(?:\(?\d{2}\)?\s?)?\d{4,5}-?\d{4}(?!\d)")


def _normalizar_endereco(valor):
    return valor.rstrip("./").lower()


def contatos(paragrafo: str) -> tuple[str, ...]:
    """Os contatos do parágrafo, normalizados — e-mail, endereço eletrônico, telefone."""
    achados = []
    for email in EMAIL.findall(paragrafo):
        achados.append(email.rstrip(".").lower())
    sem_email = EMAIL.sub(" ", paragrafo)
    for endereco in ENDERECO.findall(sem_email):
        achados.append(_normalizar_endereco(endereco))
    sem_endereco = ENDERECO.sub(" ", sem_email)
    for telefone in TELEFONE.findall(sem_endereco):
        achados.append(re.sub(r"\D", "", telefone))
    vistos = []
    for item in achados:
        if item not in vistos:
            vistos.append(item)
    return tuple(vistos)


def _de_duvida(paragrafo: str) -> bool:
    dobrado = dobrar(paragrafo)
    return any(termo in dobrado for termo in TERMOS_DE_DUVIDA)


def exclusivo(paragrafo: str) -> bool:
    palavras = set(re.findall(r"\w+", dobrar(paragrafo)))
    return any(termo in palavras for termo in TERMOS_DE_EXCLUSIVIDADE)


def canal(conteudo, canal_institucional: str = "") -> Canal:
    """O canal desta versão do Edital, com os parágrafos literais de onde ele saiu."""
    encontrados = []
    paragrafos = []
    exclusividade = False
    for secao in conteudo.get("sections") or []:
        texto = leitura.texto_da_secao(secao)
        for posicao, paragrafo in leitura.paragrafos(texto):
            achados = contatos(paragrafo)
            if not achados or not _de_duvida(paragrafo):
                continue
            paragrafos.append(
                leitura.texto(
                    leitura.onde_secao(secao),
                    leitura.caminho_da_secao(secao),
                    paragrafo,
                    posicao=posicao,
                )
            )
            exclusividade = exclusividade or exclusivo(paragrafo)
            for achado in achados:
                if achado not in encontrados:
                    encontrados.append(achado)
    if encontrados:
        return Canal(CANAL_DO_EDITAL, tuple(encontrados), tuple(paragrafos), exclusividade)
    institucional = (canal_institucional or "").strip()
    return Canal(CANAL_INSTITUCIONAL, (institucional,) if institucional else ())


def em_palavras(canal_encontrado: Canal) -> str:
    """O canal para a explicação que encaminha (`FR-1423`)."""
    if not canal_encontrado.contatos:
        # Sem canal nenhum, não há a quem encaminhar: "procure o atendimento institucional"
        # mandava a um canal que a própria P-11 diz não existir (`FR-1441`, validação de 12/10).
        return ""
    if canal_encontrado.divergente:
        return "um dos canais que o Edital informa, mostrados abaixo"
    if canal_encontrado.origem == CANAL_INSTITUCIONAL:
        return f"o canal institucional ({canal_encontrado.contatos[0]})"
    return f"o canal que o Edital informa ({canal_encontrado.contatos[0]})"
