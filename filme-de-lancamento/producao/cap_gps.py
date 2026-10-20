"""Recaptura da gestão com o visual novo (main de 18/10: barra lateral GPS) para a abertura e as miniaturas
do clímax. Captura só a janela (1440 × 810 ou 850, escala 2), como o recorte que o filme já usava; grava
<nome>_gps.png em cap/, sem tocar nas capturas antigas, que outras cenas ainda leem com caixas medidas."""
import os, sys, capture as K
from capture import *
import cap_main as _cm  # reaproveita o login da página de demonstração nova
K.BASE = "http://localhost:8092"
K.OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cap")
login = _cm.login_gestao
D1 = "00000000-0000-0000-0051-0000000000d1"
ANA51 = "4a64c39e-e9de-468f-a477-6de0d28cb69d"
REC = "/gestao/recursos/9463940e-896c-4852-98c0-ccc1a1d7c67a"
def lote(pg, ctx, b):
    pg.set_viewport_size({"width": 1440, "height": 810})
    login(pg, "gustavo.gestor", ["gestor", "publicador", "auditor", "elaborador", "exportador"])
    shoot(pg, "g_visao_gps", "/gestao/visao-geral", full=False,
          sel={"barra": ".barra-lateral", "titulo": "main h1", "sub": "main p.sub", "filtros": "form.filtros-da-visao",
               "kpi": "ul.consolidado > li", "tabela": "table.tabela-da-visao", "topo": "header.topo"})
    pg.set_viewport_size({"width": 1440, "height": 850})
    shoot(pg, "g_comissao_gps", f"/gestao/processos/{P}/comissao", full=False)
    shoot(pg, "g_convocacao51_gps", f"/gestao/editais/{E51}/marcos/{M51}/convocacao", full=False)
    login(pg, "joana.avaliadora", [])
    shoot(pg, "g_mesa51_d1_gps", f"/gestao/minhas-etapas/{E51}/{D1}", full=False)
    shoot(pg, "g_avaliacao_docs_gps", f"/gestao/minhas-etapas/{E51}/{D1}/inscricoes/{ANA51}", full=False)
    login(pg, "marta.julgadora", ["julgador"])
    shoot(pg, "g_recurso_gps", REC, full=False)
run(lote)
