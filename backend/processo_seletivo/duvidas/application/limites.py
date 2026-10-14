"""Os limites do piloto: o teto global e o limite da conversa (071, US4).

**O teto global é o que impede inferências lentas de esgotar os processos que servem as páginas
públicas** (`FR-1506`, `D-008`). Com cinco processos síncronos, no máximo dois ficam presos numa
chamada; os outros continuam livres. São travas consultivas do PostgreSQL, como as do despacho de
avisos: atravessam processos, não pedem tabela nem serviço, e um processo que morre no meio solta a
trava junto com a conexão. Sem vaga, a pergunta é recusada na hora — sem fila, que é o que o `D-008`
descartou.

**O gasto no serviço externo não é contado aqui** (`FR-1507`, emendado em 14/10). O OpenRouter é só
do desenvolvimento, e a produção não o aceita; quem limita o gasto é o limite da própria credencial,
que o serviço aplica mesmo quando a aplicação erra a conta. Esgotado, ele recusa com 402, e a
recusa vira `ORCAMENTO_ESGOTADO` no adaptador.
"""

from __future__ import annotations

import hashlib
from contextlib import contextmanager

from django.conf import settings
from django.db import connection

from processo_seletivo.duvidas.domain.estruturas_do_piloto import LIMITE_DE_USO
from processo_seletivo.duvidas.models import TrocaDoPiloto


def _chave_da_vaga(indice: int) -> int:
    digest = hashlib.sha256(f"assistente:vaga:{indice}".encode()).digest()
    return int.from_bytes(digest[:8], "big") >> 1


@contextmanager
def vaga_do_assistente():
    """Uma das `ASSISTENTE_TETO_SIMULTANEO` vagas, ou `None` quando todas estão ocupadas.

    Fora do PostgreSQL não há teto, e é honesto que não haja: é o ambiente da suíte em SQLite, onde
    nada roda em paralelo.
    """
    if connection.vendor != "postgresql":
        yield True
        return
    obtida = None
    with connection.cursor() as cursor:
        for indice in range(max(int(settings.ASSISTENTE_TETO_SIMULTANEO), 0)):
            chave = _chave_da_vaga(indice)
            cursor.execute("SELECT pg_try_advisory_lock(%s)", [chave])
            if cursor.fetchone()[0]:
                obtida = chave
                break
    try:
        yield obtida
    finally:
        if obtida is not None:
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_unlock(%s)", [obtida])


def recusa_antes_da_chamada(*, conversa) -> str | None:
    """`LIMITE_DE_USO` quando a conversa chegou ao número máximo de turnos, ou `None`."""
    feitas = TrocaDoPiloto.objects.filter(conversa=conversa).count()
    if feitas >= settings.ASSISTENTE_TURNOS_POR_CONVERSA:
        return LIMITE_DE_USO
    return None
