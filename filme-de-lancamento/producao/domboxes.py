"""Mede, no DOM real, as caixas dos blocos de cada tela capturada (px da captura, escala 2)."""
import json, os
from capture import *
from playwright.sync_api import sync_playwright

JS = """() => {
  const out = [];
  const main = document.querySelector('main') || document.body;
  const sel = 'a,label,input,select,textarea,strong,span,h1,h2,h3,section,table,thead,tbody tr,form,fieldset,dl,ul,ol,li,p,nav,aside,article,details,summary,a.botao,button,.cartao,[class*=contador],[class*=indicador],[class*=numero],div';
  for (const e of main.querySelectorAll(sel)) {
    const r = e.getBoundingClientRect();
    if (r.width < 20 || r.height < 12) continue;
    const cls = (e.className && typeof e.className === 'string') ? e.className.split(' ').slice(0,2).join('.') : '';
    const t = (e.innerText || '').trim().replace(/\\s+/g, ' ').slice(0, 60);
    out.push([e.tagName.toLowerCase() + (cls ? '.' + cls : ''), t,
              Math.round(r.left*2), Math.round((r.top + scrollY)*2), Math.round(r.width*2), Math.round(r.height*2)]);
  }
  return {h: document.documentElement.scrollHeight*2, els: out};
}"""

PAGES = {
  "gustavo": (["gestor", "publicador", "auditor", "elaborador", "exportador"], {
      "g_edital01": f"/gestao/editais/{E01}/",
      "g_marco51": f"/gestao/editais/{E51}/marcos/{M51}",
      "g_corte51": f"/gestao/editais/{E51}/marcos/{M51}/corte",
      "g_ocupacao51": f"/gestao/editais/{E51}/marcos/{M51}/ocupacao",
      "g_convocacao51": f"/gestao/editais/{E51}/marcos/{M51}/convocacao",
      "g_matriculas51_prev": f"/gestao/editais/{E51}/matriculas?populacao=CONVOCACAO%3A{M51}",
      "g_auditoria51": f"/gestao/editais/{E51}/auditoria",
      "g_visao_v2": "/gestao/visao-geral",
      "g_supervisao": f"/gestao/processos/{P}/supervisao",
      "g_autoridades": "/gestao/autoridades",
      "g_retificacao": f"/gestao/retificacoes/{RET}/",
  }),
  "paulo.presidente": ([], {
      "g_distrib51_d1": f"/gestao/editais/{E51}/distribuicao/00000000-0000-0000-0051-0000000000d1",
      "g_result_etapa51_d1": f"/gestao/editais/{E51}/distribuicao/00000000-0000-0000-0051-0000000000d1/resultados",
  }),
  "joana.avaliadora": ([], {
      "g_mesa51_d1": f"/gestao/minhas-etapas/{E51}/00000000-0000-0000-0051-0000000000d1",
      "g_avaliacao_docs": f"/gestao/minhas-etapas/{E51}/00000000-0000-0000-0051-0000000000d1/inscricoes/4a64c39e-e9de-468f-a477-6de0d28cb69d",
  }),
  "carla.publicadora": (["publicador", "gestor"], {
      "g_aviso_novo": f"/gestao/editais/{E51}/marcos/{M51}/avisos/novo",
      "g_avisos51": f"/gestao/editais/{E51}/avisos",
  }),
  "marta.julgadora": (["julgador"], {
      "g_recurso": "/gestao/recursos/9463940e-896c-4852-98c0-ccc1a1d7c67a",
  }),
  "ana.elaboradora": (["elaborador"], {
      f"c02_{s}": f"/gestao/editais/e84bb828-29fb-4914-a1d6-06ce9e6aa7e4/compor/{s}"
      for s in ["identificacao", "perfis", "cronograma", "etapas", "classificacao", "inscricao", "anexos", "revisao"]
  }),
  None: ([], {
      "p_lista": "/selecoes/", "p_edital01": f"/selecoes/{E01}/", "p_edital51": f"/selecoes/{E51}/",
      "p_resultado51": f"/selecoes/resultados/{PUB51}/", "p_verificar26": f"/selecoes/sorteio/{SORT}/verificar",
  }),
}

if __name__ == "__main__":
    res = {}
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        for who, (papeis, pages) in PAGES.items():
            ctx = b.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2, locale="pt-BR")
            pg = ctx.new_page()
            if who: login_gestao(pg, who, papeis)
            for name, url in pages.items():
                pg.goto(BASE + url, wait_until="networkidle")
                res[name] = pg.evaluate(JS)
            ctx.close()
        for name, url, st in [("p_ana_acomp51", "/selecoes/inscricoes/4a64c39e-e9de-468f-a477-6de0d28cb69d/acompanhamento", "state_ana.json"),
                              ("p_ana_conv51", "/selecoes/inscricoes/4a64c39e-e9de-468f-a477-6de0d28cb69d/convocacao", "state_ana.json"),
                              ("p_insc01_11_comprovante", "/selecoes/inscricoes/41937c90-dd8f-4f8c-9eda-b5b6d2424b31/comprovante", "state_ana.json"),
                              ("p_elisa_recorrer_ok", "/selecoes/recursos/9463940e-896c-4852-98c0-ccc1a1d7c67a", "state_elisa.json")]:
            ctx = b.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2, locale="pt-BR", storage_state=st)
            pg = ctx.new_page(); pg.goto(BASE + url, wait_until="networkidle")
            res[name] = pg.evaluate(JS); res[name]["url"] = pg.url
            ctx.close()
        b.close()
    from PIL import Image
    for n, r in res.items():
        try: hcap = Image.open(f"cap/{n}.png").size[1]
        except Exception: hcap = None
        print(f"{n:28} dom {r['h']:5}  cap {hcap}  {'OK' if hcap == r['h'] else 'DIFERE'}  {r.get('url','')}")
    json.dump(res, open("dom.json", "w"), ensure_ascii=False)
