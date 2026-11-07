"""Sonda do estudo de convergência: imprime o andamento (127) do Edital 900 num instante.

Uso, de backend/:  uv run python <esta>/sonda.py andamento 2026-12-09T10:00 [subject]
                   uv run python <esta>/sonda.py apurar-m1 2027-01-06T12:00   (só em cópia descartável!)
"""

import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

REPRO = os.path.abspath("../doc/estudo-classificacao-demonstrativa-2026-11-07/reproducao")
sys.argv_original = list(sys.argv)
sys.argv = [sys.argv[0]]
sys.path.insert(0, REPRO)
import reproduzir as R  # noqa: E402  (faz o django.setup)

sys.argv = sys.argv_original
from tests.fixtures.relatorio import em  # noqa: E402

cmd, quando = sys.argv[1], datetime.fromisoformat(sys.argv[2]).replace(
    tzinfo=ZoneInfo("America/Sao_Paulo")
)
subject = sys.argv[3] if len(sys.argv) > 3 else "demo.presidente"


def andamento():
    from processo_seletivo.interface import andamento as A

    ator = R.ator(subject, *(["resultado:publicar"] if "publicador" in subject else []))
    with em(quando):
        a = A.do_edital(R.edital(), ator)
    if a is None:
        print("sem andamento")
        return
    print("== nível 1 (providências)")
    for p in a.providencias:
        cel = p.celula if hasattr(p, "celula") else p
        print("  ", getattr(p, "onde", ""), "|", cel.situacao, "|", cel.ato, "|", cel.razao, "| resp:", cel.responsavel, "| sua:", getattr(p, "sua", ""))
    for perfil in a.perfis:
        listas = perfil.listas
        print("== matriz", [r for _, r in listas])
        for ponto in perfil.pontos:
            linha = []
            for lista, _ in listas:
                c = ponto.celula(lista)
                linha.append(f"{c.rotulo}{(':' + c.ato) if c and c.ato else ''}" if c else "·")
            print(f"  {ponto.grupo[:40]:40} {ponto.titulo:12}", " | ".join(linha))
    for lista_id in R.LISTAS:
        for marco in (R.M1, R.M2):
            desta, outras, _ = A.da_lista(a, marco, lista_id, preferir=a.e_sua)
            print("próximo nesta lista", "M1" if marco == R.M1 else "M2", lista_id and "res" or "ampla", "→", desta and (desta.situacao, desta.ato or desta.rotulo, desta.razao))


def apurar_m1():
    from processo_seletivo.ocupacao.application.emissao import emitir_apuracao

    ed = R.edital()
    with em(quando):
        try:
            r = emitir_apuracao(
                actor=R.PRESIDENCIA,
                processo_id=ed.processo_id,
                edital_id=ed.id,
                perfil_id=R.PERFIL_ID,
                marco_id=R.M1,
                lista_id=None,
                idempotency_key="sonda-apurar-m1",
                correlation_id="sonda",
                motivo="sonda: a providência do cartão",
            )
            print("ACEITA:", r)
        except Exception as e:  # noqa: BLE001
            print("RECUSADA:", type(e).__name__, getattr(e, "detail", e))


{"andamento": andamento, "apurar-m1": apurar_m1}[cmd]()
