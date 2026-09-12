"""A população das medições de escala, parametrizável pelo ambiente.

O padrão é **mil** — o número que a `013`, a `015` e a `014` mediram, e para o qual os tetos de
relógio destes testes foram calibrados. Nada muda sem `PERF_ESCALA` no ambiente.

**Por que a variável existe.** A amostra de Editais reais passou a conter um certame de 2719 vagas
num recorte só, acima de tudo o que já se mediu aqui — ver
`doc/avaliacao-de-capacidade-editais-2026-09-12.md`. Medir num tamanho novo não pode exigir editar
teste: editar para medir e reverter depois é como uma medição vira diferença não commitada que
ninguém reproduz.

**Os tetos de relógio não escalam junto, e é deliberado.** Eles são promessa de produto no tamanho
declarado; multiplicá-los pela escala afirmaria linearidade que ninguém mediu. Acima do padrão, a
falha de um teto é informação — é o tamanho em que a promessa deixa de valer —, e não defeito do
teste.

**Os testes que dizem "mil" no nome dizem a verdade no padrão**, que é o tamanho pelo qual eles
respondem e o único que o CI roda. Renomeá-los para algo genérico apagaria do nome a promessa que
cada um carrega — a `SC-002` promete **mil** inscrições num envio, e é isso que o nome afirma.
"""

import os

PADRAO = 1000


def escala() -> int:
    """Quantos participantes as medições de escala usam nesta execução."""
    bruto = os.getenv("PERF_ESCALA", "").strip()
    if not bruto:
        return PADRAO
    valor = int(bruto)
    if valor < 10:
        raise ValueError(f"PERF_ESCALA precisa ser ao menos 10; veio {valor}.")
    return valor
