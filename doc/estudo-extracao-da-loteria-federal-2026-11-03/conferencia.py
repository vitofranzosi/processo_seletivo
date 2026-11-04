"""POC — a extração declarada já aconteceu? Pergunta feita à Caixa antes de publicar o Edital.

**Prova de conceito, fora do produto.** Só biblioteca padrão, sem Django, sem banco. O lugar desta
regra no sistema está no relatório (`../estudo-extracao-da-loteria-federal-2026-11-03.md`, seção 6).

**O que ela afirma, e o que não afirma.** A Caixa responde, de forma verificável, uma pergunta só:
*qual é o último concurso realizado*. Disso decorre um fato — um número menor ou igual a ele já foi
realizado — e a ausência de outro: um número maior **ainda não foi**, o que não diz quando será. A
API devolve HTTP 500 para qualquer concurso não realizado, o seguinte e o 9999 do mesmo jeito, e
nenhum campo traz a data de um concurso futuro. A data declarada continua sendo declaração de quem
compõe.

**Falha de acesso não vira fato.** Tempo esgotado, rede fora, 5xx no endpoint principal ou corpo de
outra forma são `DESCONHECIDA`: nunca "válida", nunca "realizada".

Uso ao vivo (duas chamadas, no máximo):

    python3 -I conferencia.py 6120 2026-11-22
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from urllib import error, request

ENDERECO_DO_ULTIMO = "https://servicebus2.caixa.gov.br/portaldeloterias/api/federal"
ENDERECO_DO_NUMERO = ENDERECO_DO_ULTIMO + "/{numero}"

REALIZADA = "REALIZADA"
NAO_REALIZADA = "NAO_REALIZADA"
DESCONHECIDA = "DESCONHECIDA"
FORMA_INVALIDA = "FORMA_INVALIDA"

RECUSA, ADVERTENCIA, CONFERIDA = "RECUSA", "ADVERTENCIA", "CONFERIDA"

# Seis dígitos cobrem o 999999; o concurso de hoje tem quatro. Zero à esquerda é aceito pela Caixa
# (`006114` devolve o 6114) e normalizado aqui: `6114` e `006114` não são duas referências.
_FORMA = re.compile(r"^\d{1,6}$")


@dataclass(frozen=True)
class Resposta:
    """O que voltou de uma chamada. `status` é `None` quando a chamada não completou."""

    status: int | None
    corpo: object = None
    falha: str = ""


@dataclass(frozen=True)
class Situacao:
    """O estado do concurso **no instante da consulta**, com o lastro de onde ele saiu."""

    estado: str
    numero: int | None = None
    realizada_em: date | None = None
    ultimo: int | None = None
    ultimo_em: date | None = None
    anunciado_como_proximo: bool = False
    motivo: str = ""


@dataclass(frozen=True)
class Veredito:
    nivel: str
    codigo: str
    mensagem: str


def consultar(url, *, abrir=request.urlopen, limite=10):
    """Uma chamada. Nunca levanta: o 500 da Caixa tem corpo, e o corpo é evidência."""
    try:
        with abrir(url, timeout=limite) as resposta:
            return Resposta(resposta.status, _json(resposta.read()))
    except error.HTTPError as falha:
        return Resposta(falha.code, _json(falha.read() if falha.fp else b""))
    except (error.URLError, TimeoutError, OSError) as falha:
        return Resposta(None, falha=f"{type(falha).__name__}: {falha}")


def _json(bruto):
    try:
        return json.loads(bruto.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None


def _extracao(resposta):
    """`(numero, data)` de uma resposta 200 que traz uma extração inteira — ou `None`.

    Inteira quer dizer: número, data no formato da Caixa e os cinco bilhetes. Uma resposta 200 sem
    os bilhetes não prova realização, pela mesma razão que `loteria_federal._bilhetes_premiados`
    recusa sucedâneo.
    """
    corpo = resposta.corpo
    if resposta.status != 200 or not isinstance(corpo, dict):
        return None
    numero = corpo.get("numero")
    try:
        dia = datetime.strptime(str(corpo.get("dataApuracao") or ""), "%d/%m/%Y").date()
    except ValueError:
        return None
    bilhetes = [b for b in corpo.get("listaDezenas") or [] if str(b).strip()]
    if not isinstance(numero, int) or len(bilhetes) != 5:
        return None
    return numero, dia


def situacao(referencia, *, abrir=request.urlopen):
    """REALIZADA, NAO_REALIZADA, DESCONHECIDA ou FORMA_INVALIDA — no máximo duas chamadas.

    **A decisão sai do endpoint principal**, e não da consulta pelo número: a consulta de um
    concurso futuro devolve 500, igual a um erro do serviço, e não há como separar os dois por ela.
    O último realizado separa. A segunda chamada só acontece quando o número já foi realizado, para
    dar à mensagem a data em que foi.
    """
    texto = str(referencia).strip()
    if not _FORMA.match(texto) or int(texto) == 0:
        return Situacao(
            FORMA_INVALIDA,
            motivo="o concurso da Loteria Federal é um número inteiro, como 6115 — sem dígito "
            "verificador, sem texto e sem ano",
        )
    numero = int(texto)
    principal = consultar(ENDERECO_DO_ULTIMO, abrir=abrir)
    ultima = _extracao(principal)
    if ultima is None:
        return Situacao(DESCONHECIDA, numero=numero, motivo=_motivo(principal))
    ultimo, ultimo_em = ultima
    if numero > ultimo:
        proximo = principal.corpo.get("numeroConcursoProximo")
        return Situacao(
            NAO_REALIZADA,
            numero=numero,
            ultimo=ultimo,
            ultimo_em=ultimo_em,
            anunciado_como_proximo=proximo == numero,
        )
    detalhe = _extracao(consultar(ENDERECO_DO_NUMERO.format(numero=numero), abrir=abrir))
    # Menor ou igual ao último é realizado: a numeração é a sequência das extrações já feitas. A
    # data é o que a segunda chamada acrescenta, e a falta dela não desfaz o fato.
    realizada_em = detalhe[1] if detalhe and detalhe[0] == numero else None
    return Situacao(
        REALIZADA, numero=numero, realizada_em=realizada_em, ultimo=ultimo, ultimo_em=ultimo_em
    )


def _motivo(resposta):
    if resposta.status is None:
        return f"a Caixa não respondeu ao pedido do último concurso ({resposta.falha})"
    return f"a Caixa respondeu HTTP {resposta.status} ao pedido do último concurso, sem a extração"


def _dia(valor):
    return valor.strftime("%d/%m/%Y")


def conferir(estado, *, declarada_em):
    """O veredito para quem compõe ou publica. Pura: recebe a situação já consultada.

    `declarada_em` é o dia de `occurrenceAt`. Ele **não** é conferido contra a Caixa — não há
    contra o que conferir —, e por isso a mensagem de sucesso diz o que foi e o que não foi
    verificado.
    """
    if estado.estado == FORMA_INVALIDA:
        return Veredito(RECUSA, "draw_occurrence_malformed", f"Concurso inválido: {estado.motivo}.")
    if estado.estado == REALIZADA:
        quando = f", em {_dia(estado.realizada_em)}" if estado.realizada_em else ""
        return Veredito(
            RECUSA,
            "draw_occurrence_already_drawn",
            f"O concurso {estado.numero} da Loteria Federal já foi realizado{quando}. A semente "
            "precisa vir de uma extração que ainda não aconteceu quando a relação for congelada. "
            f"O último concurso realizado é o {estado.ultimo}, de {_dia(estado.ultimo_em)}: "
            "declare um concurso posterior a ele, que ocorra depois do fim das inscrições, "
            "conferindo número e data no calendário oficial da Caixa.",
        )
    if estado.estado == DESCONHECIDA:
        return Veredito(
            ADVERTENCIA,
            "draw_occurrence_not_checked",
            f"Não foi possível conferir na Caixa se o concurso {estado.numero} já foi realizado: "
            f"{estado.motivo}. Isso não confirma a extração. Confira no resultado oficial que ele "
            "ainda não foi realizado antes de publicar.",
        )
    dias = (declarada_em - estado.ultimo_em).days
    adiante = estado.numero - estado.ultimo
    anuncio = " (é o próximo anunciado pela Caixa)" if estado.anunciado_como_proximo else ""
    return Veredito(
        CONFERIDA,
        "draw_occurrence_not_drawn_yet",
        f"Concurso {estado.numero}{anuncio}: ainda não realizado. O último realizado é o "
        f"{estado.ultimo}, de {_dia(estado.ultimo_em)}; o declarado está {adiante} concurso(s) "
        f"adiante, e a data declarada, {_dia(declarada_em)}, {dias} dia(s) depois. "
        "A Caixa não publica a data de concursos futuros: confira no calendário oficial que o "
        f"concurso {estado.numero} é o de {_dia(declarada_em)}.",
    )


def conferir_realizacao(*, numero, realizada_em, declarada_em):
    """No dia do sorteio: a Caixa realizou na data que o Edital publicou? Só informa (adiamento,
    antecipação). Quem recusa continua sendo a precedência sobre o congelamento, que já existe."""
    if realizada_em == declarada_em:
        return None
    sentido = "antes" if realizada_em < declarada_em else "depois"
    return (
        f"O Edital declara o concurso {numero} para {_dia(declarada_em)}, e a Caixa o realizou em "
        f"{_dia(realizada_em)}, {abs((declarada_em - realizada_em).days)} dia(s) {sentido}."
    )


if __name__ == "__main__":
    referencia, declarada = sys.argv[1], date.fromisoformat(sys.argv[2])
    estado = situacao(referencia)
    veredito = conferir(estado, declarada_em=declarada)
    print(f"{datetime.now().isoformat(timespec='seconds')} {estado}")
    print(f"{veredito.nivel} {veredito.codigo}\n{veredito.mensagem}")
