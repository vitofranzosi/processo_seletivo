"""Junta o rastreio e as larguras do instrumento do estudo num telas.csv com as colunas de 14/11.

Duas fases, porque `larguras.py` lê `representantes.json`:
  python montar_telas_csv.py <pasta> representantes   -> escolhe uma visita por padrão
  python montar_telas_csv.py <pasta> csv              -> grava <pasta>/telas.csv
"""
import csv, json, glob, sys, pathlib
S = pathlib.Path(sys.argv[1]); fase = sys.argv[2]
ORDEM = ["paulo_presidente", "treino_presidencia", "complemento", "treino_avaliacao1", "treino_formalizacao", "anonimo"]
def visitas():
    for nome in ORDEM:
        f = S / f"rastreio-{nome}.json"
        if f.exists():
            yield from (r for r in json.load(open(f)) if r.get("status") == 200 and "main" in r)
    for f in sorted(glob.glob(str(S / "rastreio-cand*.json"))):
        yield from (r for r in json.load(open(f)) if r.get("status") == 200 and "main" in r)
rep = {}
for r in visitas():
    if r["padrao"] in rep: continue
    if r["padrao"].startswith("/gestao/identificar"): r = {**r, "ident": "identidade"}
    rep[r["padrao"]] = r
if fase == "representantes":
    # O complemento entrou como treino.presidencia, com todos os papéis: as larguras entram igual.
    sai = {k: {**v, "ident": "treino.presidencia" if v["ident"] == "complemento" else v["ident"]}
           for k, v in rep.items() if not v["ident"].startswith("cand")}
    json.dump(sai, open(S / "representantes.json", "w"), ensure_ascii=False)
    print(len(sai), "representantes da gestão e do público;", len(rep) - len(sai), "do portal autenticado")
    sys.exit()
lg = json.load(open(S / "larguras.json"))
COLS = "tela,identidade,folhas_proprias,h1_px,n_h2,tamanhos_de_fonte,caixas,profundidade_de_caixa,assinaturas_de_botao,campos,tabelas,altura_1440,nos_abaixo_do_contraste,alvos_menores_que_24,transborda_375,transborda_768,metade_direita_1280,metade_direita_1440,metade_direita_1920,terco_direito_1440,terco_direito_1920,cpl_max_1440,cpl_max_1920,margem_esq_1920,margem_dir_1920".split(",")
# As definições das colunas são as do telas.csv de 14/11, conferidas contra ele nas 91 telas cuja
# altura não mudou: a folha própria é toda folha que não seja dos tokens nem a comum da gestão; os
# tamanhos de fonte são os que somam ao menos 1% do texto; a assinatura de botão é (altura, fonte).
COMUNS = ("shared/", "interface/gestao/")
with open(S / "telas.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(COLS)
    for k in sorted(rep):
        r = rep[k]; L = lg.get(k, {}).get("w", {})
        g = lambda larg, campo: (L.get(str(larg)) or {}).get(campo, "")
        folhas = [p.rsplit("/", 1)[-1].removesuffix(".css") for p in r.get("folhas", []) if not p.startswith(COMUNS)]
        fontes = sum(1 for _, n in r["tamanhosDeFonte"] if 100 * n / max(r["chars"], 1) >= 1)
        botoes = len({(b["h"], b["fs"]) for b in r["botoes"]})
        w.writerow([k, r["ident"], " ".join(folhas), r["h1"][0]["fs"] if r["h1"] else "", r["nH2"],
                    fontes, r["nCaixas"], r["profundidadeDeCaixa"], botoes,
                    r["nCampos"], len(r["tabelas"]), r["scrollH"], r["contrasteBaixo"]["n"], r["alvos"]["pequenos"],
                    g(375, "overflowX"), g(768, "overflowX"), g(1280, "metadeDireita"), g(1440, "metadeDireita"),
                    g(1920, "metadeDireita"), g(1440, "tercoDireito"), g(1920, "tercoDireito"),
                    g(1440, "cplMax") or "", g(1920, "cplMax") or "", g(1920, "margemEsq"), g(1920, "margemDir")])
print(len(rep), "telas")
