"""O número como o campo numérico o aceita — uma regra só para todas as telas."""

from decimal import Decimal


def no_campo(valor):
    """O número sem zeros à direita, no formato que o campo numérico aceita (058, FR-1078).

    As colunas guardam quatro casas, e a leitura devolve `25.0000` onde se escreveu `25`. Com ponto
    — o `value` de um campo numérico é sempre com ponto; quem o mostra com vírgula é o navegador.
    Nada é arredondado: é o mesmo número, e o que "Salvar rascunho" grava não muda (D-005).
    Saiu de `interface/forms.py` para a ficha do barema (146) usar a mesma, e não uma cópia.
    """
    return "" if valor in (None, "") else format(Decimal(str(valor)).normalize(), "f")
