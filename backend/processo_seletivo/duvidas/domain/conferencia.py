"""A conferência da saída do modelo, antes de qualquer coisa ser mostrada (071, `R-005`, `FR-1487`).

**O que ela prova.** Que cada fonte citada foi entregue naquela chamada; que a citação literal é
idêntica a um trecho do Edital; que toda data, hora, número e contato afirmados estão numa fonte que
o próprio trecho cita; que o tipo tem as fontes que exige; que "o Edital não informa" não virou
negativa que nenhuma fonte declara. Recusada, a resposta inteira não aparece (`FR-1488`).

**O que ela não prova** (`D-007`). Que a paráfrase respeita a fonte; que nenhuma condição foi
omitida; que um "não" não virou "sim"; que a fonte certa sustenta a afirmação certa. Isso é a
revisão humana (`FR-1513`), e é por isso que a tela diz que as respostas podem conter erros.

**Estreita de propósito.** Números por extenso passam sem ser vistos; uma normalização estreita
recusa respostas certas. As duas coisas são medidas — a recusa indevida entra no resumo de cada
rodada —, e o ajuste, quando vier, é alteração do `R-005`, e não um afrouxamento silencioso.
"""

from __future__ import annotations

import json
import re
from decimal import Decimal, InvalidOperation

from processo_seletivo.duvidas.domain.canal import contatos
from processo_seletivo.duvidas.domain.estruturas import (
    DETALHE_EM_ANEXO,
    FONTES_DIVERGENTES,
    NAO_INFORMA,
    RESPONDIDA,
    TEXTO,
)
from processo_seletivo.duvidas.domain.estruturas_do_piloto import (
    CITACAO_LITERAL,
    CITACAO_NAO_LITERAL,
    FONTE_INEXISTENTE,
    FORMA,
    NATUREZAS_DE_TRECHO,
    NEGATIVA_NAO_DECLARADA,
    TIPO_SEM_FONTE,
    TIPOS,
    VALOR_SEM_FONTE,
    Conferencia,
    Motivo,
    SaidaDoModelo,
    Trecho,
)
from processo_seletivo.shared.texto import dobrar

MESES = {
    "janeiro": 1,
    "fevereiro": 2,
    "marco": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12,
}
DATA_NUMERICA = re.compile(r"(?<!\d)(\d{1,2})/(\d{1,2})/(\d{4})(?!\d)")
DATA_POR_EXTENSO = re.compile(
    r"(?<!\d)(\d{1,2})º?\s+de\s+(" + "|".join(MESES) + r")(?:\s+de\s+(\d{4}))?", re.IGNORECASE
)
HORA = re.compile(r"(?<!\d)(\d{1,2})\s*(?:h|:)\s*(\d{2})?(?:min)?(?![\w])|(?<!\d)(\d{1,2})\s+horas")
NUMERO = re.compile(r"(?<![\w.,])\d+(?:[.,]\d+)*(?:\s*%|[ºª])?")
#: O identificador de fonte que o modelo escreva no texto ("conforme F12") não é valor a conferir.
IDENTIFICADOR_DE_FONTE = re.compile(r"\bF\d+\b")
ASPAS = "\"'“”‘’«» "

#: Negativas que "O Edital não informa" não pode afirmar sem fonte (`FR-1422` da `070`). Lista
#: fechada e pequena: o falso negativo passa à revisão humana; o falso positivo recusa, e aparece.
NEGATIVAS = (
    r"nao cabe",
    r"nao ha",
    r"nao (?:e|sera|serao) (?:permitid|aceit)\w*",
    r"nao pode\w*",
    r"e vedad\w*",
)


def ler(saida_bruta: str):
    """A saída na forma do contrato, ou `None` — o motivo `FORMA` (saida-do-modelo.md §2)."""
    try:
        objeto = json.loads(saida_bruta)
    except (TypeError, ValueError):
        return None
    if not isinstance(objeto, dict) or set(objeto) != {"tipo", "trechos"}:
        return None
    tipo, trechos = objeto["tipo"], objeto["trechos"]
    if tipo not in TIPOS or not isinstance(trechos, list) or not 1 <= len(trechos) <= 12:
        return None
    lidos = []
    for trecho in trechos:
        if not isinstance(trecho, dict) or set(trecho) != {"natureza", "texto", "fontes"}:
            return None
        natureza, texto, fontes = trecho["natureza"], trecho["texto"], trecho["fontes"]
        if natureza not in NATUREZAS_DE_TRECHO:
            return None
        if not isinstance(texto, str) or not 1 <= len(texto) <= 1200:
            return None
        if not isinstance(fontes, list) or len(fontes) > 8:
            return None
        if not all(isinstance(fonte, str) and re.fullmatch(r"F\d+", fonte) for fonte in fontes):
            return None
        lidos.append(Trecho(natureza, texto, tuple(fontes)))
    return SaidaDoModelo(tipo, tuple(lidos))


def conferir(saida_bruta: str, fontes, *, permitidos=()) -> Conferencia:
    """Aprova ou recusa, com todos os motivos encontrados (`FR-1487`).

    `permitidos`: valores que o modelo recebeu fora das fontes, no cabeçalho delas — o número e o
    ano do Edital.
    """
    saida = ler(saida_bruta)
    if saida is None:
        return Conferencia((Motivo(FORMA),))
    por_id = {fonte.id: fonte for fonte in fontes}
    motivos = []
    for posicao, trecho in enumerate(saida.trechos):
        citadas = []
        for identificador in trecho.fontes:
            if identificador not in por_id:
                motivos.append(Motivo(FONTE_INEXISTENTE, posicao, identificador))
            else:
                citadas.append(por_id[identificador])
        if trecho.natureza == CITACAO_LITERAL and not _literal(trecho.texto, citadas):
            motivos.append(Motivo(CITACAO_NAO_LITERAL, posicao, trecho.texto[:80]))
        for valor in _sem_fonte(trecho.texto, citadas, permitidos):
            motivos.append(Motivo(VALOR_SEM_FONTE, posicao, valor))
    motivos.extend(_coerencia_do_tipo(saida, por_id))
    return Conferencia(tuple(motivos), saida)


# ---- as regras -------------------------------------------------------------------------------


def _literal(texto, citadas) -> bool:
    """Sem as aspas das pontas, subcadeia **exata** de uma fonte de texto do Edital citada."""
    trecho = texto.strip(ASPAS)
    return bool(trecho) and any(
        fonte.natureza == TEXTO and trecho in fonte.conteudo for fonte in citadas
    )


def _sem_fonte(texto, citadas, permitidos):
    """Os valores do trecho que nenhuma fonte citada por ele traz."""
    disponivel = _valores(" ".join(_pesquisavel(fonte) for fonte in citadas), lado_da_fonte=True)
    disponivel |= _valores(" ".join(str(item) for item in permitidos), lado_da_fonte=True)
    faltando = []
    for valor in _valores(texto):
        if valor in disponivel:
            continue
        # Data sem ano casa com a mesma data em qualquer ano das fontes.
        if valor[0] == "data" and valor[3] is None:
            if any(item[0] == "data" and item[1:3] == valor[1:3] for item in disponivel):
                continue
        faltando.append(_legivel(valor))
    return faltando


def _coerencia_do_tipo(saida: SaidaDoModelo, por_id):
    citadas = [por_id[fonte] for fonte in saida.citadas() if fonte in por_id]
    motivos = []
    if saida.tipo == RESPONDIDA and not citadas:
        motivos.append(Motivo(TIPO_SEM_FONTE, None, RESPONDIDA))
    if saida.tipo == FONTES_DIVERGENTES and len(citadas) < 2:
        motivos.append(Motivo(TIPO_SEM_FONTE, None, FONTES_DIVERGENTES))
    if saida.tipo == DETALHE_EM_ANEXO and not any(fonte.anexo for fonte in citadas):
        motivos.append(Motivo(TIPO_SEM_FONTE, None, DETALHE_EM_ANEXO))
    if saida.tipo == NAO_INFORMA:
        declaradas = dobrar(" ".join(fonte.conteudo for fonte in citadas))
        for trecho_posicao, trecho in enumerate(saida.trechos):
            dobrado = dobrar(trecho.texto)
            for negativa in NEGATIVAS:
                achada = re.search(rf"\b{negativa}\b", dobrado)
                if achada and not re.search(rf"\b{negativa}\b", declaradas):
                    motivos.append(Motivo(NEGATIVA_NAO_DECLARADA, trecho_posicao, achada.group()))
    return motivos


# ---- a extração dos valores -------------------------------------------------------------------


def _pesquisavel(fonte) -> str:
    """O que o modelo viu da fonte: o lugar, o rótulo e o conteúdo."""
    return f"{fonte.lugar} {fonte.rotulo} {fonte.conteudo}"


def _valores(texto: str, *, lado_da_fonte=False) -> set:
    """`("data", d, m, a)`, `("hora", h, min)`, `("contato", c)` e `("numero", Decimal)`.

    Do lado da fonte, os componentes de datas e horas também valem como números: "dia 5" se
    sustenta numa fonte que diz "05/11/2026".
    """
    valores = set()
    texto = IDENTIFICADOR_DE_FONTE.sub(" ", texto)
    for contato in contatos(texto):
        valores.add(("contato", contato))
    restante = _sem_contatos(texto)

    for dia, mes, ano in DATA_NUMERICA.findall(restante):
        valores.add(("data", int(dia), int(mes), int(ano)))
        if lado_da_fonte:
            valores.update(("numero", Decimal(item)) for item in (dia, mes, ano))
    restante = DATA_NUMERICA.sub(" ", restante)
    for dia, mes, ano in DATA_POR_EXTENSO.findall(restante):
        valores.add(("data", int(dia), MESES[dobrar(mes)], int(ano) if ano else None))
        if lado_da_fonte:
            valores.update(("numero", Decimal(item)) for item in (dia, ano) if item)
    restante = DATA_POR_EXTENSO.sub(" ", restante)
    for hora, minuto, so_hora in HORA.findall(restante):
        h = int(hora or so_hora)
        if h > 23:
            continue
        valores.add(("hora", h, int(minuto or 0)))
        if lado_da_fonte:
            valores.update(("numero", Decimal(item)) for item in (hora or so_hora, minuto) if item)
    restante = HORA.sub(" ", restante)
    for bruto in NUMERO.findall(restante):
        numero = _numero(bruto)
        if numero is not None:
            valores.add(("numero", numero))
    return valores


def _sem_contatos(texto):
    from processo_seletivo.duvidas.domain.canal import EMAIL, ENDERECO, TELEFONE

    return TELEFONE.sub(" ", ENDERECO.sub(" ", EMAIL.sub(" ", texto)))


def _numero(bruto: str):
    """ "25%", "25,0", "25.0000", "1.200", "5º" → o mesmo `Decimal` que a fonte escreve."""
    limpo = bruto.rstrip("%ºª ").strip()
    if "," in limpo:
        limpo = limpo.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(?:\.\d{3})+", limpo):
        limpo = limpo.replace(".", "")
    try:
        return Decimal(limpo).normalize()
    except InvalidOperation:
        return None


def _legivel(valor) -> str:
    if valor[0] == "data":
        return f"{valor[1]:02d}/{valor[2]:02d}" + (f"/{valor[3]}" if valor[3] else "")
    if valor[0] == "hora":
        return f"{valor[1]}h{valor[2]:02d}"
    if valor[0] == "numero":
        # `normalize()` escreve 150 como "1.5E+2": o motivo da recusa é para quem lê o relatório.
        return format(valor[1], "f")
    return str(valor[1])
