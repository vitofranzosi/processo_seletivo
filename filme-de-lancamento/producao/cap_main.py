"""Recaptura, com o código da main de 18/10 (porta 8092, banco ps_filme_main), das telas que o filme usa."""
import os, capture as K
from capture import *
K.BASE = "http://localhost:8092"
K.OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cap_main"); os.makedirs(K.OUT, exist_ok=True)
E02 = "e84bb828-29fb-4914-a1d6-06ce9e6aa7e4"
D1 = "00000000-0000-0000-0051-0000000000d1"
ANA51 = "4a64c39e-e9de-468f-a477-6de0d28cb69d"
def login_gestao(pg, subject, papeis):
    # a identificação mudou na 075: a demonstração fica numa página própria, com "Opções avançadas"
    K.sair(pg)
    pg.goto(K.BASE + "/gestao/identificar", wait_until="networkidle")
    pg.click("a[href*='demonstracao']"); pg.wait_for_load_state("networkidle")
    pg.evaluate("document.querySelectorAll('details').forEach(d => d.open = true)")
    pg.fill("input[name=subject]", subject)
    for p_ in papeis:
        pg.check(f"form:has(input[name=subject]) input[name=papeis][value='{p_}']")
    pg.click("form:has(input[name=subject]) button[type=submit]")
    pg.wait_for_load_state("networkidle")
    print("login", subject, pg.url, file=sys.stderr)

def lote(pg, ctx, b):
    login_gestao(pg, "joana.avaliadora", [])
    shoot(pg, "g_mesa51_d1", f"/gestao/minhas-etapas/{E51}/{D1}")
    shoot(pg, "av_doc_1", f"/gestao/minhas-etapas/{E51}/{D1}/inscricoes/{ANA51}")
    sair(pg)
    shoot(pg, "pub_portal_depois", "/selecoes/")
    shoot(pg, "p_lista_busca", "/selecoes/?busca=inform%C3%A1tica")
    shoot(pg, "pub_portal_edital02", f"/selecoes/{E02}/")
    shoot(pg, "p_edital01", f"/selecoes/{E01}/")
    shoot(pg, "p_resultado51", f"/selecoes/resultados/{PUB51}/")
    shoot(pg, "p_verificar26", f"/selecoes/sorteio/{SORT}/verificar")
    shoot(pg, "p_ana_acesso_vazio", "/selecoes/acesso")
if __name__ == "__main__":
    run(lote)
