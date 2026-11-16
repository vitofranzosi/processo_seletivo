import json, sys, os
P = sys.argv[1]
def vera(arq):
    d = json.load(open(f"{P}/saida/{arq}"))
    out = {}
    for j in d["report"]["jobs"]:
        nome = os.path.basename(j["itemDetails"]["name"])
        vr = j.get("validationResult") or []
        if not vr:
            out[nome] = ("erro", j.get("taskException", {}).get("exceptionMessage", "")[:60] if isinstance(j.get("taskException"), dict) else "sem resultado", [])
            continue
        v = vr[0]
        regras = [f"{r['clause']}-{r['testNumber']}" for r in v["details"]["ruleSummaries"]]
        descr = {f"{r['clause']}-{r['testNumber']}": r["description"][:110] for r in v["details"]["ruleSummaries"]}
        out[nome] = ("OK" if v["compliant"] else "FALHA", v["details"]["failedChecks"], regras, descr, j["processingTime"]["difference"])
    return out
a, s, u = vera("a.json"), vera("s.json"), vera("u.json")
c = json.load(open(f"{P}/saida/conversao.json"))
print("| amostra | KB | pág | veraPDF 2b antes | gs s | KB depois | ×tam | veraPDF 2b depois | texto | pix% | assinatura |")
for r in c["resultados"]:
    n = r["amostra"]; d = n.replace(".pdf", ".pdfa.pdf")
    antes = a.get(n, ("?",)); depois = s.get(d, ("—",))
    sig = ""
    if r.get("assinatura_antes"): sig = f"{r['assinatura_antes']} → campos {r.get('assinaturas_pdfa')} {r.get('assinatura_depois','')}"
    print(f"| {n} | {r['bytes']/1024:.0f} | {r.get('paginas')} | {antes[0]} {('('+','.join(antes[2])+')') if len(antes)>2 and antes[2] else ''} | {r['gs_segundos']} | {r.get('bytes_pdfa',0)/1024:.0f} | {r.get('variacao_tamanho')} | {depois[0]} {depois[2] if len(depois)>2 and depois[2] else ''} | {r.get('texto_igual')} {r.get('texto_chars','')} | {r.get('pixels_diferentes_pct_max')} | {sig} |")
print(c["determinismo"])
print("--- regras falhas nos originais do GPS (2b):")
for n in ["I1-edital-gps.pdf","I2-comprovante-gps.pdf","I3-divulgacao-gps.pdf","I4-relatorio-gps.pdf","C8-falso-pdfa.pdf","C1b-textual-fonte-embutida.pdf","C2-digitalizado.pdf"]:
    print(n, a[n][0]); [print("   ", k, v) for k, v in a[n][3].items()]
print("--- 2u:", {k: (v[0], v[2]) for k, v in u.items()})
for k,v in u.items():
    [print("   ", k, kk, vv) for kk, vv in v[3].items()]
print("--- tempo veraPDF ms (depois):", {k: v[4] for k, v in s.items() if len(v) > 4})
