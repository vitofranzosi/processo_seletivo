import json, glob, sys, collections, pathlib, re
S = pathlib.Path(sys.argv[1])
vis = []
for f in sorted(glob.glob(str(S / "rastreio-*.json"))): vis += [r for r in json.load(open(f)) if r.get("status") == 200 and "main" in r]
vis = [r for r in vis if "/documentacao" not in r["padrao"]]
G = [r for r in vis if r["padrao"].startswith("/gestao") and "identificar" not in r["padrao"]]; P = [r for r in vis if r["padrao"].startswith("/selecoes")]
def tabela(nome, rs, campo, chave, top=18):
    telas = collections.defaultdict(set); usos = collections.Counter()
    for r in rs:
        for b in r[campo]:
            k = chave(b); telas[k].add(r["padrao"]); usos[k] += b.get("n", 1)
    print(f"\n### {nome}: {len(telas)} assinaturas distintas em {len({r['padrao'] for r in rs})} padrões")
    for k, t in sorted(telas.items(), key=lambda kv: -len(kv[1]))[:top]: print(f"  {len(t):3} telas | {usos[k]:5} usos | {k}")
for nome, rs in (("GESTÃO", G), ("PORTAL", P)):
    print("\n==================", nome, len(rs), "visitas")
    tabela("Botões por (altura, fonte)", rs, "botoes", lambda b: (b["h"], b["fs"]))
    tabela("Botões por classe → altura/fonte/raio/padding", rs, "botoes", lambda b: (b["cls"][:60], b["h"], b["fs"], b["raio"], b["pad"]), 40)
    tabela("Campos por (tag, altura, fonte, raio, padding)", rs, "campos", lambda b: (b["cls"].split(".")[0], b["h"], b["fs"], b["raio"], b["pad"]), 20)
    tabela("Selos/etiquetas", rs, "selos", lambda b: (b["cls"][:50], b["h"], b["fs"], b["raio"], b["pad"], b["fw"]), 40)
    tabela("Avisos", rs, "avisos", lambda b: (b["cls"][:50], b["fs"], b["raio"], b["pad"], b["bg"]), 30)
    tabela("Caixas (raio | padding | fundo | borda)", rs, "caixas", lambda b: b["k"], 30)
    tabela("Tabelas (classe, td padding, td fonte, th fonte, moldura)", rs, "tabelas", lambda b: (b["cls"][:30], b["tdPad"], b["tdFs"], b["thFs"], (b["moldura"] or "")[:25], b["pai"][:30]), 30)
    h1 = collections.Counter((r["h1"][0]["fs"], r["h1"][0]["fw"]) if r["h1"] else None for r in rs); print("\n### h1 (px, peso):", dict(h1))
    print("### h1 fora do main:", sum(1 for r in rs if r["h1"] and not r["h1"][0]["dentroDoMain"]), "| telas com mais de um h1:", len({r["padrao"] for r in rs if len(r["h1"]) > 1}), "| sem h1:", sorted({r["padrao"] for r in rs if not r["h1"]}))
    h2 = collections.Counter(x for r in rs for x in r["h2"]); h3 = collections.Counter(x for r in rs for x in r["h3"]); print("### h2 px:", dict(h2), "| h3 px:", dict(h3))
    fs = collections.Counter(); 
    for r in rs:
        for f, n in r["tamanhosDeFonte"]: fs[f] += n
    tot = sum(fs.values()); print("### tamanhos de fonte por volume de texto:", [(f, f"{100*n/tot:.1f}%") for f, n in fs.most_common(22)], "total distintos:", len(fs))
    cores = collections.Counter()
    for r in rs:
        for c, n in r["coresDeTexto"]: cores[c] += n
    print("### cores de texto:", len(cores), cores.most_common(14))
    print("### contraste baixo:", [(r["padrao"], r["contrasteBaixo"]["n"], r["contrasteBaixo"]["ex"][:3]) for r in {r["padrao"]: r for r in rs if r["contrasteBaixo"]["n"]}.values()])
    print("### sem rótulo:", {r["padrao"]: r["semRotulo"] for r in rs if r["semRotulo"]})
    al = collections.Counter()
    for r in {r["padrao"]: r for r in rs}.values():
        for e in r["alvos"]["ex"]: al[re.sub(r"\d+x\d+", "", e).strip()[:50] + " " + e.split()[-1]] += 1
    print("### alvos < 24px mais comuns:", al.most_common(14))
    prof = collections.Counter(r["profundidadeDeCaixa"] for r in {r["padrao"]: r for r in rs}.values()); print("### profundidade de caixa:", dict(prof))
    nb = {r["padrao"]: r["nBotoesCheios"] for r in rs}; print("### botões cheios por tela:", collections.Counter(nb.values()), "| com 3+:", [k for k, v in nb.items() if v >= 3])
