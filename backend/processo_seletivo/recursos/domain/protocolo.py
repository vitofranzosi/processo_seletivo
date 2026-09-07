"""O protocolo do recurso — `REC-2026-K7M4Q2PX`.

**O alfabeto é importado, e não copiado.** Ele existe por três razões que valem igual aqui e na
Inscrição: o protocolo é ditado ao telefone, copiado à mão e lido em voz alta, e por isso não tem
`0`/`O` nem `1`/`I`/`L`. Duplicar a constante criaria dois alfabetos que podem divergir — e o
segundo divergiria em silêncio, porque nada compara os dois (T-012).

O que muda é o prefixo, e ele é o que distingue os dois atos para quem os recebe: `INS` é o que a
pessoa enviou, `REC` é o que ela contestou.

**Único é garantia do banco**, e não deste módulo: `unique=True` na coluna é quem responde sob
concorrência. Aqui só se sorteia.
"""

import secrets

from processo_seletivo.inscricoes.domain.protocolo import ALFABETO, COMPRIMENTO

PREFIXO = "REC"


def gerar(ano: int) -> str:
    """O ano é o da interposição — é ele que localiza o ato no tempo para quem atende depois."""
    sorteio = "".join(secrets.choice(ALFABETO) for _ in range(COMPRIMENTO))
    return f"{PREFIXO}-{ano}-{sorteio}"
