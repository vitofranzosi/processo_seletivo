"""A duração do vídeo por extenso, no comprovante do candidato (174, FR-7883).

O comprovante dizia "72.3 segundos": ponto decimal, que o português lê como milhar, e nenhuma
conversão para minutos. O `gravacao.js` tem a mesma conta, em `duracaoPorExtenso`, para a revisão
antes do envio; os dois testes usam os mesmos casos.
"""

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def duracao_por_extenso(segundos) -> str:
    """*"1 min 12 s"*, *"45 s"*, *"3 min"*; vazio quando não há número."""
    try:
        total = int(Decimal(str(segundos)).quantize(Decimal(1), rounding=ROUND_HALF_UP))
    except (InvalidOperation, ValueError, TypeError):
        return ""
    total = max(total, 0)
    minutos, resto = divmod(total, 60)
    if not minutos:
        return f"{resto} s"
    return f"{minutos} min {resto} s" if resto else f"{minutos} min"
