"""A zona temporal institucional — declarada uma vez, e onde o domínio pode importá-la.

Ela vivia duas vezes, as duas em `interface/` (T-008). Enquanto só a interface formatava datas,
isso era duplicação inofensiva; a contagem de prazo recursal é **domínio**, e domínio não importa
de `interface` — a dependência apontaria para o lado errado, e a próxima regra de calendário teria
de escolher entre repetir a constante uma terceira vez ou inverter a arquitetura.

**Por que uma zona fixa, e não `settings.TIME_ZONE`.** As duas coincidem hoje, e é justamente por
isso que o valor está aqui: a zona da instituição é fato do domínio — os prazos de um Edital do
Cefor correm em Vitória, qualquer que seja o servidor — e amarrá-la à configuração faria uma
mudança de infraestrutura alterar, em silêncio, o dia em que um recurso vence.
"""

from zoneinfo import ZoneInfo

ZONA = ZoneInfo("America/Sao_Paulo")

__all__ = ["ZONA"]
