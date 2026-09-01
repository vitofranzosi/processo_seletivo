"""O protocolo que o candidato leva embora.

Três exigências, e cada uma exclui uma solução óbvia (FR-062):

- **único**, o que o banco garante, e não este módulo;
- **legível**, porque ele é ditado ao telefone, copiado à mão e lido em voz alta — daí o alfabeto
  sem os pares que se confundem nessas três situações: `0`/`O`, `1`/`I`/`L`;
- **opaco**, sem sequência: um `INS-2026-000042` diria a quem o recebe quantas inscrições existem
  e em que ordem chegaram, e produzir a sequência exigiria serializar inscrições concorrentes para
  gerar um número que ninguém precisa que seja ordenado.
"""

import secrets

ALFABETO = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"
COMPRIMENTO = 8
PREFIXO = "INS"


def gerar(ano: int) -> str:
    """`INS-2026-K7M4Q2PX`. O ano é o do envio, e não o do Edital.

    O ano do envio é o que localiza o ato no tempo para quem atende a pessoa depois — um Edital
    de 2026 recebe inscrição em 2026, mas um retificado pode receber em 2027, e o protocolo tem de
    dizer quando a inscrição aconteceu.
    """
    sorteio = "".join(secrets.choice(ALFABETO) for _ in range(COMPRIMENTO))
    return f"{PREFIXO}-{ano}-{sorteio}"
