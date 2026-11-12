"""Leitura só: para cada identidade, as providências 'suas' em todos os Editais (estudo minhas atividades).

Roda dentro de `manage.py shell`. Não grava nada.
"""

import time
from collections import Counter

from django.db import connection, reset_queries
from django.test.utils import CaptureQueriesContext

from processo_seletivo.interface import andamento, atos_retificacao, providencias, trabalho
from processo_seletivo.interface.identidade import permissoes_de
from processo_seletivo.processos.models import Edital
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.unidades.models import Unidade

unidade = Unidade.objects.get()
escopo = getattr(unidade, "codigo", None) or getattr(unidade, "sigla", None) or str(unidade.pk)


def ator(subject, papeis=()):
    try:
        return Actor(subject, escopo, permissoes_de(papeis))
    except Exception as erro:  # noqa: BLE001
        print("falha ao montar ator", subject, erro)
        raise


IDENTIDADES = [
    ("treino.presidencia", ()),
    ("treino.avaliacao1", ()),
    ("treino.avaliacao2", ()),
    ("estudo.publicador", ("publicador",)),
    ("estudo.julgador", ("julgador",)),
]

editais = list(
    Edital.objects.select_related("processo").order_by("processo__institutional_code", "year", "number")
)
print("Editais:", [(e.processo.institutional_code, f"{e.number}/{e.year}", e.status) for e in editais])

for subject, papeis in IDENTIDADES:
    a = ator(subject, papeis)
    print("\n" + "=" * 100)
    print("IDENTIDADE", subject, papeis)
    total_suas = Counter()
    t0 = time.perf_counter()
    with CaptureQueriesContext(connection) as cq:
        for edital in editais:
            try:
                em_curso = atos_retificacao.em_curso(edital, a)
            except Exception as erro:  # noqa: BLE001
                em_curso = None
                print("  em_curso falhou", erro)
            dados = andamento.do_edital(edital, a, em_curso=em_curso)
            if dados is None:
                continue
            nivel = dados.nivel_1
            suas = [i for i in nivel.itens if i.grupo == providencias.SUA]
            outras = [i for i in nivel.itens if i.grupo != providencias.SUA]
            if not nivel.itens:
                continue
            print(f"\n  {edital.processo.institutional_code} Edital {edital.number}/{edital.year} [{edital.status}]"
                  f"  suas={len(suas)} outras={len(outras)}")
            for i in nivel.itens:
                p = getattr(i, "providencia", i)
                total_suas[i.grupo] += 1
                ate = getattr(p, "ate", None)
                print(
                    f"    [{i.grupo:9}] {getattr(p,'situacao',''):9} {getattr(p,'natureza',''):11}"
                    f" | {getattr(p,'ato','')[:70]} | onde={getattr(p,'onde','')[:40]}"
                    f" | resp={getattr(p,'responsavel','')} | ate={ate:%d/%m %H:%M}" if ate else
                    f"    [{i.grupo:9}] {getattr(p,'situacao',''):9} {getattr(p,'natureza',''):11}"
                    f" | {getattr(p,'ato','')[:70]} | onde={getattr(p,'onde','')[:40]}"
                    f" | resp={getattr(p,'responsavel','')}"
                )
    dt = time.perf_counter() - t0
    print(f"\n  RESUMO {subject}: {dict(total_suas)}; {len(cq.captured_queries)} consultas; {dt:.2f}s"
          f" para {len(editais)} Editais")

    # A faixa da 104, para comparação.
    try:
        objetos = trabalho.do_ator(a, editais)
        print(f"  FAIXA 104 ({len(objetos)}):")
        for o in objetos:
            print(f"    {o.natureza:12} {o.titulo[:40]:40} | {o.ato[:50]} | {o.situacao}")
    except Exception as erro:  # noqa: BLE001
        print("  faixa 104 falhou:", repr(erro))
