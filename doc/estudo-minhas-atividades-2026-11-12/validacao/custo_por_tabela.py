"""Leitura só: onde estão as consultas de `andamento.do_edital`, por tabela (estudo minhas atividades, rodada 2).

Roda dentro de `manage.py shell`. Para cada identidade, soma as consultas dos Editais publicados das
comissões da pessoa e agrupa pela primeira tabela do FROM. Mede também quanto custa decidir, antes
de derivar, em quais Editais a pessoa pode ter algo seu: o recorte barato.
"""

import re
import time
from collections import Counter

from django.db import connection
from django.test.utils import CaptureQueriesContext

from processo_seletivo.comissoes.models import MembroComissao
from processo_seletivo.interface import andamento, atos_retificacao, providencias
from processo_seletivo.interface.identidade import permissoes_de
from processo_seletivo.processos.models import Edital
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.unidades.models import Unidade

escopo = Unidade.objects.get().codigo
TABELA = re.compile(r'FROM "([a-z_0-9]+)"')

for subject in ("treino.presidencia", "treino.avaliacao1"):
    ator = Actor(subject, escopo, permissoes_de(()))
    with CaptureQueriesContext(connection) as recorte:
        processos = set(
            MembroComissao.objects.filter(identity_subject=subject, ativo=True).values_list(
                "processo_id", flat=True
            )
        )
        editais = list(
            Edital.objects.filter(processo_id__in=processos, status__in=("PUBLICADO", "ENCERRADO"))
            .exclude(processo__status__in=("ENCERRADO", "CANCELADO"))
            .select_related("processo")
        )
    print(f"\n{subject}: recorte barato = {len(recorte.captured_queries)} consultas, {len(editais)} Editais")

    por_tabela, por_edital, suas = Counter(), [], 0
    t0 = time.perf_counter()
    with CaptureQueriesContext(connection) as cq:
        for edital in editais:
            antes = len(cq.captured_queries)
            em_curso = atos_retificacao.em_curso(edital, ator)
            dados = andamento.do_edital(edital, ator, em_curso=em_curso)
            por_edital.append(len(cq.captured_queries) - antes)
            if dados:
                suas += sum(1 for i in dados.nivel_1.itens if i.grupo == providencias.SUA)
    dt = time.perf_counter() - t0
    for q in cq.captured_queries:
        m = TABELA.search(q["sql"])
        por_tabela[m.group(1) if m else q["sql"][:30]] += 1
    print(f"  {len(cq.captured_queries)} consultas em {dt:.2f}s; por Edital: min {min(por_edital)}, "
          f"max {max(por_edital)}; itens seus: {suas}")
    for tabela, n in por_tabela.most_common(12):
        print(f"    {n:5}  {tabela}")
