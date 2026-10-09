"""O número que quem elabora digita no texto do Edital, e as remissões que o texto faz (065).

O texto das seções textuais é transcrito do Word do setor (a E10 = B da `DP-20`), e os Editais do
Cefor numeram todo subitem — "4.1", "4.2" — para que o próprio Edital, a comissão e o candidato
possam citá-los. O número da seção, porém, é calculado (`054`, FR-985), e quando a seção do catálogo
sai com outro número que a do original o documento oficial passa a imprimir subitens fora da sua
seção e remissões que apontam para outro lugar. É o ED-01 da auditoria de 08/10/2026.

Aqui mora só o **reconhecimento**, sem banco e sem Django: quem decide o que é conflito, cruzando
com a numeração do documento, é a validação. Três leituras:

- o número de subitem no começo de um parágrafo (FR-1199);
- o título de seção do original colado como parágrafo (FR-1201);
- as remissões internas de um texto (FR-1204).

**A forma é estreita de propósito.** O conflito de numeração impede a submissão (D-001), e um falso
positivo aqui trava um Edital certo. Por isso o número de subitem exige dois a quatro grupos de **um
ou dois** algarismos: é o que, sozinho, já exclui datas, números de lei, valores, CEP e números de
processo, porque nenhum deles cabe nessa forma sem um grupo de três ou quatro algarismos, uma barra
ou uma vírgula logo depois. O que ainda sobra — o decimal seguido de unidade, "7.5 pontos" — cai
pela lista de unidades. O erro dessa lista fica do lado de não acusar: um subitem legítimo que
comece por "Horas" deixa de ser lido, e o que se perde é um aviso, e não uma submissão (research,
D-010).
"""

import re
from dataclasses import dataclass

# Espaços e marcadores de lista no começo do parágrafo: o "• 4.1" de uma lista colada ainda é o
# subitem 4.1.
_MARCADORES_INICIAIS = re.compile(r"^[\s•·\-–—*]*")

# O número de subitem e o que vem depois dele. O casamento é o guloso, e não é refeito:
# "13.146/2015" vira "13.14" seguido de "6/2015", e é a recusa do que vem depois que o descarta —
# não há segunda tentativa de achar um corte que caiba.
_NUMERO_DE_SUBITEM = re.compile(r"^(?P<numero>\d{1,2}(?:\.\d{1,2}){1,3})(?P<depois>.*)\Z", re.S)

# O que pode separar o número do texto: espaço; ponto ou parêntese seguidos de espaço ou do fim;
# travessão, meia-risca ou hífen entre espaços.
_SEPARADOR = re.compile(r"^(?:[.)]?(?:\s+|\Z)|\s*[–—-]\s+)")

# A primeira palavra que faz do número uma medida, e não um subitem: "7.5 pontos", "10.5 horas".
UNIDADES = frozenset(
    {
        "ponto",
        "pontos",
        "pts",
        "pt",
        "hora",
        "horas",
        "h",
        "minuto",
        "minutos",
        "min",
        "dia",
        "dias",
        "semana",
        "semanas",
        "mês",
        "mes",
        "meses",
        "ano",
        "anos",
        # Multiplicadores e grandezas (revisão do PR, 09/10/2026): "1.2 mil candidatos", "3.5
        # vezes o valor", "1.5 salário mínimo". Decimal com ponto é raro em português, mas aparece
        # no texto colado, e cada um destes impedia a submissão de um Edital certo.
        "mil",
        "milhão",
        "milhões",
        "vez",
        "vezes",
        "salário",
        "salários",
    }
)

# O parêntese logo depois do número — "6.0 (seis) pontos" — é a grafia por extenso, e a unidade é a
# palavra seguinte a ele.
_EXTENSO_ENTRE_PARENTESES = re.compile(r"^\([^)]*\)\s*")

# **Intervalos de hora e de data no começo do parágrafo** (FR-1199, emendado na revisão do PR em
# 09/10/2026). "8.30 às 12.00 – atendimento" e "10.10 a 20.10 – período de recurso" têm a forma de
# subitem no primeiro número, e cada um impedia a submissão com a orientação de "corrigir a
# numeração", que não faz sentido. **Reconhece-se a expressão inteira**, e não o número seguido de
# "a" ou "às": "1.1 a 1.3 aplicam-se…" continua subitem, e um conflito de verdade continua
# impeditivo.
#
# - **Horas**: as duas pontas com minutos de dois algarismos (00 a 59) e hora até 23, ligadas por
#   "às" — o conectivo de hora. Com "a", "8.10 a 8.12" é intervalo de subitens, e continua lido
#   assim.
# - **Datas**: as duas pontas como dia (1 a 31) e mês de dois algarismos (01 a 12), ligadas por "a"
#   ou "até", com o ano opcional na segunda, e **dias diferentes**. Um intervalo de subitens fica
#   numa seção só e repete o primeiro grupo; "10.10 a 10.12" é ambíguo — de 10/10 a 10/12, ou dos
#   itens 10.10 a 10.12 —, e continua subitem. O erro aceito fica desse lado porque o subitem é a
#   leitura natural de um parágrafo do Edital, e a data, a exceção.
_FIM_DA_EXPRESSAO = r"(?=[.,;:)]?(?:\s|\Z)|\s*[–—-]\s)"
_INTERVALO_DE_HORAS = re.compile(
    r"^(?P<h1>\d{1,2})\.(?P<m1>\d{2})\s+(?:às|as)\s+(?P<h2>\d{1,2})\.(?P<m2>\d{2})h?"
    + _FIM_DA_EXPRESSAO,
    re.I,
)
_INTERVALO_DE_DATAS = re.compile(
    r"^(?P<d1>\d{1,2})\.(?P<m1>\d{2})\s+(?:a|até)\s+(?P<d2>\d{1,2})\.(?P<m2>\d{2})"
    r"(?:[./]\d{2}(?:\d{2})?)?" + _FIM_DA_EXPRESSAO,
    re.I,
)


def _intervalo_de_horas_ou_datas(texto: str) -> bool:
    if casado := _INTERVALO_DE_HORAS.match(texto):
        horas = (int(casado["h1"]), int(casado["h2"]))
        minutos = (int(casado["m1"]), int(casado["m2"]))
        if all(hora <= 23 for hora in horas) and all(minuto <= 59 for minuto in minutos):
            return True
    if casado := _INTERVALO_DE_DATAS.match(texto):
        dias = (int(casado["d1"]), int(casado["d2"]))
        meses = (int(casado["m1"]), int(casado["m2"]))
        if all(1 <= dia <= 31 for dia in dias) and all(1 <= mes <= 12 for mes in meses):
            return dias[0] != dias[1]
    return False


@dataclass(frozen=True)
class NumeroDeSubitem:
    """O número como foi digitado ("04.1"), o primeiro grupo como inteiro (4) e o texto depois."""

    texto: str
    primeiro: int
    resto: str


def _sem_marcadores(paragrafo: str) -> str:
    return _MARCADORES_INICIAIS.sub("", str(paragrafo or ""))


def numero_de_subitem(paragrafo: str) -> NumeroDeSubitem | None:
    """O número de subitem com que o parágrafo começa, ou `None` (FR-1199)."""
    texto = _sem_marcadores(paragrafo)
    casado = _NUMERO_DE_SUBITEM.match(texto)
    if casado is None or _intervalo_de_horas_ou_datas(texto):
        return None
    depois = casado["depois"]
    separador = _SEPARADOR.match(depois)
    if depois and separador is None:
        return None
    resto = depois[separador.end() :].strip() if separador else ""
    primeira = _EXTENSO_ENTRE_PARENTESES.sub("", resto).split(maxsplit=1)
    if primeira and primeira[0].strip(".,;:").casefold() in UNIDADES:
        return None
    return NumeroDeSubitem(
        texto=casado["numero"], primeiro=int(casado["numero"].split(".")[0]), resto=resto
    )


# O título da seção do original, colado como primeiro parágrafo: "11. DA CONVOCAÇÃO". Um grupo só,
# ponto ou traço, e o resto em caixa alta. É **suspeita**, e não conflito: "11." sozinho também pode
# abrir uma lista (FR-1201).
_TITULO = re.compile(r"^(?P<numero>\d{1,2})\s*[.\-–—]\s+(?P<resto>\S.*)\Z", re.S)
_LETRAS_DE_UM_TITULO = 3


def titulo_transcrito(paragrafo: str) -> int | None:
    """O número de um parágrafo que tem a forma de título de seção transcrito, ou `None`."""
    casado = _TITULO.match(_sem_marcadores(paragrafo))
    if casado is None:
        return None
    letras = [caractere for caractere in casado["resto"] if caractere.isalpha()]
    if len(letras) < _LETRAS_DE_UM_TITULO or any(not letra.isupper() for letra in letras):
        return None
    return int(casado["numero"])


# --- as remissões (FR-1204) -------------------------------------------------------------------

# O número da remissão não pode ser **prefixo** de outro número: sem o `\.\d` no fim, "item
# 10.1.1.1.1" virava a remissão a "10.1.1.1" e "item 4.123" a "4" — remissões a outro item, que o
# texto não fez (revisão do PR, 09/10/2026). Acima de quatro níveis, a remissão é ignorada inteira.
_NUMERO = r"\d{1,2}(?:\.\d{1,2}){0,3}(?![\d/]|\.\d)"
_LISTA = rf"{_NUMERO}(?:(?:\s*,\s*|\s+(?:e|ou|a)\s+){_NUMERO})*"
_REMISSAO_A_ITEM = re.compile(
    rf"(?i:\b(?P<palavra>(?:sub)?ite(?:m|ns))\b)\s+(?:n[º°o.]\s*)?(?P<lista>{_LISTA})"
)
_REMISSAO_A_QUADRO = re.compile(
    r"(?i:\b(?P<palavra>tabela|tabelas|quadro|quadros)\b)\s+(?P<lista>\d{1,3})(?![\d/.]\d)"
)
_NUMERO_DA_LISTA = re.compile(r"\d{1,3}(?:\.\d{1,2}){0,3}")

# A designação de outro ato, ou de um Anexo, logo depois do número: a remissão não é deste
# documento. "Do edital" sem número continua interna — o 28/2026 escreve "item 5.4 do edital" para
# citar a si mesmo.
_OUTRO_ATO = re.compile(
    r"(?i)\b(?:d[oa]s?|n[oa]s?|pel[oa]s?)\s+(?:edital\s+n|resolu|portaria|lei\b|decreto|art\b|"
    r"art\.|artigo|instru[cç][aã]o\s+normativa|anexo|nota\s+t[eé]cnica)"
)
# Até onde a designação ainda governa a remissão: oito palavras, sem atravessar ponto final. Ponto
# final é o ponto seguido de espaço e maiúscula, ou do fim — "art. 3º" e "nº. 28" não encerram a
# frase.
_PALAVRAS_DA_DESIGNACAO = 8
_FIM_DE_FRASE = re.compile(r"\.(?=\s+[A-ZÀ-Ý]|\s*\Z)|[;!?]")


@dataclass(frozen=True)
class Remissao:
    """Uma remissão interna: como está no texto, os números que ela cita e a espécie do alvo."""

    literal: str
    numeros: tuple[str, ...]
    especie: str
    inicio: int


def _de_outro_ato(depois: str) -> bool:
    fim = _FIM_DE_FRASE.search(depois)
    trecho = depois[: fim.start()] if fim else depois
    janela = " ".join(trecho.split()[:_PALAVRAS_DA_DESIGNACAO])
    return bool(_OUTRO_ATO.search(janela))


def remissoes(texto: str) -> list[Remissao]:
    """As remissões internas de `texto`, na ordem em que aparecem (FR-1204)."""
    texto = str(texto or "")
    achadas = []
    for padrao in (_REMISSAO_A_ITEM, _REMISSAO_A_QUADRO):
        for casado in padrao.finditer(texto):
            if _de_outro_ato(texto[casado.end() :]):
                continue
            numeros = tuple(_NUMERO_DA_LISTA.findall(casado["lista"]))
            palavra = casado["palavra"].casefold()
            if palavra.startswith("tabela"):
                especie = "tabela"
            elif palavra.startswith("quadro"):
                especie = "quadro"
            else:
                especie = "subitem" if any("." in numero for numero in numeros) else "secao"
            achadas.append(
                Remissao(
                    literal=texto[casado.start() : casado.end()],
                    numeros=numeros,
                    especie=especie,
                    inicio=casado.start(),
                )
            )
    return sorted(achadas, key=lambda remissao: remissao.inicio)
