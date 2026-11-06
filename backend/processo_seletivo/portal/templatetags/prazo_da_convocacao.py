"""O prazo da convocação nos templates do portal, pela função única (121, FR-3873, FR-3875).

Os dados do ato, a lista e o acompanhamento escreviam a data e a hora do prazo com o filtro `date`,
ao lado da data — a mesma conta feita de novo em cada template. A FR-3873 pede uma função só para o
portal e o e-mail: estes filtros a chamam, e uma mudança de formato ou de fuso nela alcança todas as
telas do candidato de uma vez.
"""

from django import template

from processo_seletivo.portal import obrigacoes

register = template.Library()


@register.filter
def data_e_hora_do_prazo(instante):
    """*"12/11/2026, às 17h00"*, ou vazio sem instante."""
    return obrigacoes.data_e_hora(instante) if instante else ""


@register.filter
def ate_o_prazo(vencimento):
    """*"até 12/11/2026, às 17h00"*, ou vazio sem vencimento (FR-3747 da `118`)."""
    return obrigacoes.ate(vencimento)
