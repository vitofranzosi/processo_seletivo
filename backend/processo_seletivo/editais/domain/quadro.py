"""A quantidade que o percentual de uma Modalidade produz no quadro de vagas (051, FR-932, FR-933).

**O operador fazia a conta e o sistema a conferia.** A validação já calcula o piso e o teto do
percentual sobre as vagas imediatas (`validation._divergencia_do_percentual`) e avisa quando a linha
sai da faixa — mas não dizia o número, e quem compunha abria a calculadora. Aqui a mesma conta vira
**sugestão**, e o que decide entre o piso e o teto é o arredondamento que a Modalidade declara.

**Sugestão, e não derivação.** A quantidade continua sendo do Perfil e declarada por quem compõe; a
validação continua aceitando a faixa inteira, como sempre aceitou. Nada aqui grava valor: a tela
mostra, e o gesto *"Preencher pelo percentual"* põe a sugestão nas linhas vazias do formulário, que
só existem depois de *Salvar*.

**O arredondamento é o `rounding` da regra normativa**, que existia no esquema sem consumidor (ordem
de 27/09, passo 1) e continua não retificável: ele é parâmetro da cota, e muda por versionamento.
A forma lida é uma lista fechada; o que a API tiver gravado fora dela é preservado e não sugere
nada.
"""

import math
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

PARA_CIMA = "PARA_CIMA"
MEIO_PARA_CIMA = "MEIO_PARA_CIMA"
PARA_BAIXO = "PARA_BAIXO"

#: As três regras, com as palavras que a composição e a Revisão mostram. A ordem é a da lista.
ARREDONDAMENTOS = {
    PARA_CIMA: "a fração vira vaga",
    MEIO_PARA_CIMA: "fração de meio ou mais vira vaga",
    PARA_BAIXO: "a fração é desprezada",
}


def modo_declarado(rounding):
    """O modo que a regra declara, se for da lista fechada; `""` quando não declara, `None` fora.

    Três respostas, e não duas: *não declarado* e *declarado fora da lista* se dizem de jeitos
    diferentes na tela, e o segundo precisa ser preservado ao gravar.
    """
    if not rounding:
        return ""
    if (
        isinstance(rounding, dict)
        and set(rounding) == {"mode"}
        and rounding["mode"] in ARREDONDAMENTOS
    ):
        return rounding["mode"]
    return None


def em_palavras(rounding):
    modo = modo_declarado(rounding)
    if modo is None:
        return "declarado fora da lista"
    return ARREDONDAMENTOS.get(modo, "não declarado")


@dataclass(frozen=True)
class Sugestao:
    #: A quantidade sugerida; `None` quando piso e teto diferem e nada decide entre eles.
    valor: int | None
    piso: int
    teto: int
    #: A conta à vista: *"25% de 7 = 1,75"*.
    conta: str


def _formatar(numero: Decimal) -> str:
    texto = format(numero.normalize(), "f")
    return texto.replace(".", ",")


def sugestao(*, percentual, vagas_imediatas, rounding=None):
    """A sugestão para a linha de uma Modalidade, ou `None` quando não há o que calcular."""
    try:
        taxa = Decimal(str(percentual))
    except (InvalidOperation, TypeError, ValueError):
        return None
    if not isinstance(vagas_imediatas, int) or isinstance(vagas_imediatas, bool):
        return None
    if taxa <= 0 or vagas_imediatas < 0:
        return None
    esperado = Decimal(vagas_imediatas) * taxa / Decimal(100)
    piso, teto = math.floor(esperado), math.ceil(esperado)
    conta = f"{_formatar(taxa)}% de {vagas_imediatas} = {_formatar(esperado)}"
    modo = modo_declarado(rounding)
    if piso == teto:
        valor = piso
    elif modo == PARA_CIMA:
        valor = teto
    elif modo == PARA_BAIXO:
        valor = piso
    elif modo == MEIO_PARA_CIMA:
        valor = teto if esperado - piso >= Decimal("0.5") else piso
    else:
        valor = None
    return Sugestao(valor=valor, piso=piso, teto=teto, conta=conta)
