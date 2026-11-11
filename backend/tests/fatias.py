"""A suíte em fatias, para o CI rodar cada uma num runner próprio: `-p tests.fatias --fatia=K/N`.

**Por que fatiar, se já há quatro workers.** O runner tem quatro vCPUs, e o PostgreSQL do serviço
divide o mesmo disco com eles: mais workers no mesmo runner quase não rendem
(`doc/estudo-paralelizacao-da-suite.md`). Outro runner traz outro disco e outro PostgreSQL, e o
repositório é público, de modo que o runner a mais não custa.

**Por hash do nodeid, e não por ordem de coleta nem por arquivo.** Simulado sobre os tempos de
11/11/2026, o hash deixa a fatia mais cara 3% acima da média com três fatias; o hash do arquivo, 7%.
E a fatia de um caso não muda quando entra caso novo — a ordem de coleta mudaria a de todos os
seguintes. O caso cai inteiro numa fatia, e o `worksteal` já reparte um mesmo módulo entre workers:
fatiar por caso não separa nada que o paralelismo de hoje mantenha junto.

Sem `--fatia`, não faz nada. Fora do CI, ninguém precisa dele.
"""

import zlib

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--fatia",
        default=None,
        metavar="K/N",
        help="roda só os casos da fatia K de N (1 ≤ K ≤ N), pelo hash do nodeid",
    )


def pytest_collection_modifyitems(config, items):
    fatia = config.getoption("fatia")
    if not fatia:
        return
    try:
        k, n = (int(parte) for parte in fatia.split("/"))
    except ValueError:
        raise pytest.UsageError(f"--fatia espera K/N, e recebeu {fatia!r}") from None
    if not 1 <= k <= n:
        raise pytest.UsageError(f"--fatia {fatia}: K vai de 1 a N")
    manter, fora = [], []
    for item in items:
        (manter if zlib.crc32(item.nodeid.encode()) % n == k - 1 else fora).append(item)
    if fora:
        config.hook.pytest_deselected(items=fora)
    items[:] = manter
