"""Formatação humana — e o único lugar onde ela acontece.

**A fronteira que este módulo existe para tornar verificável.** A forma canônica do conteúdo
publicado carrega decimais com quatro casas e ponto (`"20.0000"`), porque é dela que saem o hash, a
reprodutibilidade e o endereçamento da Retificação. Quem lê o Edital não quer `20.0000%`. As duas
coisas são verdadeiras ao mesmo tempo, e a única maneira de manter as duas é converter **na
materialização**, nunca antes (FR-001).

Espalhar a conversão pelo compositor a tornaria convenção; num módulo nomeado ela é regra, com teste
próprio e visível em diff. A revisão da spec mostrou que essa fronteira é fácil de atravessar por
descuido — este arquivo é a resposta barata a isso.

**Sem locale.** Nada aqui depende de `LC_ALL`, de `django.utils.formats` ou de qualquer estado
global do processo: o mesmo conteúdo publicado tem de produzir o mesmo documento em qualquer
máquina, e um documento normativo que muda de forma conforme o ambiente que o gerou não é
reproduzível.
"""

from decimal import Decimal, InvalidOperation


def decimal(valor) -> str:
    """A forma canônica de quatro casas, escrita em português do Brasil (FR-003).

    `"20.0000"` → `"20"`; `"12.5000"` → `"12,5"`; `"7.2500"` → `"7,25"`; `"0.5000"` → `"0,5"`.

    Zeros à direita são descartados porque não são informação: a quarta casa existe na forma
    canônica para que duas gravações semanticamente iguais produzam o mesmo hash, não para afirmar
    precisão que o dado não tem. Um percentual de vinte por cento escrito `20,0000%` num Edital
    sugere uma exatidão que ninguém mediu.

    Ausência devolve string vazia. Os chamadores já decidem se compõem a linha — a decisão de
    imprimir ou omitir é deles, e continua sendo (`if etapa.get("weight") is not None`).
    """
    if valor is None:
        return ""
    texto = str(valor).strip()
    if not texto:
        return ""
    try:
        # `format(..., "f")` em vez de `normalize()`: normalizar `Decimal("20.0000")` produz
        # `2E+1`, e a notação científica num Edital seria pior do que o problema original.
        texto = format(Decimal(texto), "f")
    except InvalidOperation:
        # Valor que não é decimal não é convertido nem descartado em silêncio: sai como está, e
        # quem lê o documento vê o dado real em vez de um campo vazio inexplicável.
        return str(valor)
    if "." in texto:
        texto = texto.rstrip("0").rstrip(".")
    return texto.replace(".", ",")


def instante(momento) -> str:
    """Data e hora como um Edital as escreve — não como um banco as armazena.

    `05/10/2026 14:00` é registro; `05/10/2026, às 14h` é ato administrativo. A hora cheia perde
    os minutos porque num Edital ela não os tem: um prazo que termina "às 23h59" se escreve assim,
    e um que começa "às 14h" não vira "às 14h00".
    """
    if momento is None:
        return ""
    data = momento.strftime("%d/%m/%Y")
    if momento.hour == 0 and momento.minute == 0:
        return data
    hora = f"{momento.hour}h" + (f"{momento.minute:02d}" if momento.minute else "")
    return f"{data}, às {hora}"
