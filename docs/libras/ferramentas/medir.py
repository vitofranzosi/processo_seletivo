"""Métricas do catálogo atual (versão 3), ao lado das versões 1 e 2.

A versão 1 vem de `referencia/catalogo-v1.json`; a 2, dos valores publicados em `viabilidade.md` na rodada 2
(a parte que depende só dos simulados se recalcula aqui, e tem de dar o mesmo número). Os editais reais
(28/2026 e 59/2026) se medem à parte: contra os simulados e um contra o outro, nunca somados aos simulados
num total só, porque a natureza do texto é outra.

Uso, da raiz do repositório:  python3 docs/libras/ferramentas/medir.py
Imprime tabelas em Markdown; não grava nada.
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

from corpus import EDITAIS, REAIS, SIMULADOS, carregar, palavras, unidades_da_linha  # noqa: E402
from ids import IDS, V3  # noqa: E402
from unidades import FAMILIAS, U  # noqa: E402

V1 = json.loads((AQUI / "referencia" / "catalogo-v1.json").read_text(encoding="utf-8"))["metricas"]
# Publicados na rodada 2 (viabilidade.md, §2.3). A classificação mudou na rodada 3 para 21 unidades, e por isso
# estes não se recalculam: ficam como registro.
V2_CLS = {
    "EXATA": (17, 581),
    "PARAMETRIZÁVEL": (46, 3510),
    "SEMELHANTE": (8, 318),
    "INÉDITA": (70, 1329),
    "ESPECIALIZADA": (1, 45),
}
linhas, _, ocorr, situacoes = carregar()
eds = list(EDITAIS)


def quase(t):
    """Texto de comparação sem caixa e sem pontuação: diferença só de vírgula, crase escrita ou inicial maiúscula."""
    return " ".join(re.sub(r"[^\w\s]", " ", t.lower()).split())


# Ocorrências: as linhas com unidade, sem o rodapé; cada unidade de uma linha conta uma ocorrência.
occ = defaultdict(list)
for e in eds:
    for o in linhas[e]:
        for k in unidades_da_linha(o):
            if k != "rodape":
                occ[k].append((e, o))
ativas = [k for k in IDS if U[k].get("status") != "desdobrada"]


def em_editais(k, grupo):
    return {e for e, _ in occ[k] if e in grupo}


print("## Unidades e ocorrências\n")
print("| Medida | Versão 1 | Versão 2 | Versão 3 |\n|---|---|---|---|")
print(f"| Identificadores | 126 | 154 | {len(IDS)} |")
print(f"| Unidades ativas | 126 | 142 | {len(ativas)} |")
print(f"| Ocorrências (sem rodapé) | {V1['ocorrencias']} | 377 | {sum(len(v) for v in occ.values())} |")
novas = {
    e: len({k for o in linhas[e] for k in unidades_da_linha(o) if situacoes[(o["id"], k)] == "INÉDITA"}) for e in eds
}
print("| Unidades novas por edital | 72 · 49 · 4 | 72 · 62 · 7 | " + " · ".join(str(novas[e]) for e in eds) + " |")
ned = Counter(len({e for e, _ in v}) for v in occ.values())
print(
    "| Unidades em 1 · 2 · 3 · 4 · 5 editais | 69 · 31 · 24 | 92 · 26 · 22 | "
    + " · ".join(str(ned[n]) for n in range(1, 6))
    + " |"
)
print(f"\nUnidades novas da rodada 3: {len(V3)}. Ordem: " + " → ".join(EDITAIS[e]["curto"] for e in eds) + ".")


def medir_palavras(e, contra):
    """Palavras de `e` cuja unidade recorre nos editais `contra`, com texto idêntico, e com texto quase idêntico."""
    tot = rec = idn = qse = 0
    for o in linhas[e]:
        k = o["unidade"]
        if k == "rodape":
            continue
        p = palavras(o["texto"])
        tot += p
        if not k:
            continue
        outros = [x for ee, x in occ[k] if ee in contra and ee != e]
        rec += p if outros else 0
        idn += p if any(x["comparavel"] == o["comparavel"] for x in outros) else 0
        qse += p if any(quase(x["comparavel"]) == quase(o["comparavel"]) for x in outros) else 0
    return tot, rec, idn, qse


print("\n## Palavras: simulados entre si (reproduz a versão 2)\n")
print("Uma linha com duas unidades conta as palavras uma vez, pela unidade principal; a regra embutida não soma.\n")
print("| Edital | Palavras | Unidade recorre em outro simulado | Texto idêntico em outro simulado |\n|---|---|---|---|")
ts = rs = ids_ = 0
for e in SIMULADOS:
    tot, rec, idn, _ = medir_palavras(e, SIMULADOS)
    ts, rs, ids_ = ts + tot, rs + rec, ids_ + idn
    print(f"| {EDITAIS[e]['curto']} | {tot} | {rec / tot:.0%} | {idn / tot:.0%} |")
print(f"| **Simulados** | **{ts}** | **{rs / ts:.0%}** | **{ids_ / ts:.0%}** |")

print("\n## Palavras: editais reais contra o corpus simulado inteiro\n")
print(
    "Conjunto comparado: **todas** as linhas dos três simulados — o texto que o sistema gera **e** o texto livre que a "
    "auditoria do PDF redigiu para simular o gestor. A comparação é feita **dentro da unidade** atribuída pelo "
    "catálogo: uma linha real conta como idêntica se alguma linha simulada **da mesma unidade** tiver o mesmo texto "
    "normalizado. Denominador: as palavras do edital real (cabeçalho em imagem incluído, transcrito). Mede "
    "coincidência literal em português; não mede equivalência de sentido nem reaproveitamento de tradução.\n"
)
print("| Edital | Palavras | Mesma unidade num simulado | Linha idêntica num simulado (mesma unidade) |")
print("|---|---|---|---|")
for e in REAIS:
    tot, rec_s, idn_s, _ = medir_palavras(e, SIMULADOS)
    print(f"| {EDITAIS[e]['curto']} | {tot} | {rec_s / tot:.0%} | {idn_s / tot:.0%} |")


def frases(texto):
    """Frases normalizadas (sem caixa e sem pontuação), cortadas em ponto, ponto e vírgula e dois-pontos."""
    return [q for q in (quase(f) for f in re.split(r"(?<=[.;:])\s+", texto)) if len(q.split()) >= 4]


# As frases que o sistema gera: as linhas dos simulados cuja unidade principal tem origem C pura (“frase escrita
# pelo sistema a partir de regra”, auditoria do PDF de 08/10, §3.2). As de origem mista (C+D, C+B+D, D+C) ficam
# fora, porque carregam texto livre; as de origem A (cabeçalho, numeração, rótulos) também, porque não são frase.
GERADAS = [o for e in SIMULADOS for o in linhas[e] if o["unidade"] and U[o["unidade"]]["ori"] == "C"]
FRASES_GERADAS = {f for o in GERADAS for f in frases(o["texto"])}
LINHAS_GERADAS = {o["comparavel"] for o in GERADAS}
UNID_GERADAS = {o["unidade"] for o in GERADAS}
print("\n## Palavras: editais reais contra as frases que o sistema gera\n")
print(
    f"Conjunto comparado: as **{len(GERADAS)} linhas** dos simulados cuja unidade tem origem **C pura** "
    f"({sum(palavras(o['texto']) for o in GERADAS)} palavras, {len(FRASES_GERADAS)} frases de quatro palavras ou mais, "
    f"{len(UNID_GERADAS)} unidades). Comparação **sem** restrição de unidade. Denominador: as palavras do edital real. "
    "*Frase idêntica*: a frase real, sem caixa e sem pontuação, é uma das frases do conjunto. *Mesma função*: a linha "
    "real foi atribuída a uma das unidades do conjunto — o que diz que o edital trata da mesma coisa, e não que diga o "
    "mesmo.\n"
)
print(
    "| Edital | Palavras | Em linha idêntica a uma linha gerada | Em frase idêntica a uma frase gerada | Em linha com a mesma função de uma frase gerada |"
)
print("|---|---|---|---|---|")
for e in REAIS:
    tot = lin = fra = fun = 0
    for o in linhas[e]:
        p = palavras(o["texto"])
        tot += p
        lin += p if o["comparavel"] in LINHAS_GERADAS else 0
        fun += p if set(unidades_da_linha(o)) & UNID_GERADAS else 0
        fra += sum(len(f.split()) for f in frases(o["texto"]) if f in FRASES_GERADAS)
    print(f"| {EDITAIS[e]['curto']} | {tot} | {lin / tot:.1%} | {fra / tot:.1%} | {fun / tot:.1%} ({fun} palavras) |")
cobertas = {k for e in REAIS for o in linhas[e] for k in unidades_da_linha(o)} & UNID_GERADAS
print(
    f"\nDas {len(UNID_GERADAS)} unidades do conjunto, {len(cobertas)} aparecem em algum edital real; nenhuma frase do "
    "conjunto aparece literalmente: "
    + str(sum(1 for e in REAIS for o in linhas[e] for f in frases(o["texto"]) if f in FRASES_GERADAS))
    + " frases reais coincidem. As duas que aparecem: "
    + ", ".join(sorted(f"{IDS[k]} ({U[k]['t']})" for k in cobertas))
    + ". **Limite:** “mesma função” depende da atribuição do catálogo, que cria unidade nova quando muda destinatário, "
    "condição ou consequência; cláusulas reais que tratam do mesmo assunto com outra regra, ou com mais conteúdo, ficam "
    "fora. A comparação de sentido por situação está em `comparacao-focalizada/`."
)

print("\n## Palavras: editais reais entre si\n")
print(
    "Conjunto comparado: o outro edital real, dentro da mesma unidade. *Quase idêntico* ignora caixa e pontuação. "
    "Mede coincidência literal; não mede equivalência de sentido.\n"
)
print("| Edital | Palavras | Mesma unidade no outro real | Idêntico ao outro real | Quase idêntico ao outro real |")
print("|---|---|---|---|---|")
for e in REAIS:
    tot, rec_r, idn_r, qse_r = medir_palavras(e, REAIS)
    print(f"| {EDITAIS[e]['curto']} | {tot} | {rec_r / tot:.0%} | {idn_r / tot:.0%} | {qse_r / tot:.0%} |")

print("\n## Texto idêntico entre os dois editais reais, por família\n")
print(
    "| Família | Unidades nos dois | Com texto idêntico | Palavras do 59/2026 com texto idêntico ao 28/2026 |\n|---|---|---|---|"
)
e28, e59 = REAIS
fam_pal, fam_tot = Counter(), Counter()
for o in linhas[e59]:
    k = o["unidade"]
    if not k:
        continue
    p = palavras(o["texto"])
    fam_tot[U[k]["fam"]] += p
    if any(x["comparavel"] == o["comparavel"] for ee, x in occ[k] if ee == e28):
        fam_pal[U[k]["fam"]] += p
for fam in FAMILIAS:
    nos_dois = [k for k in ativas if U[k]["fam"] == fam and em_editais(k, REAIS) == set(REAIS)]
    if not nos_dois:
        continue
    iguais = [
        k
        for k in nos_dois
        if {o["comparavel"] for e, o in occ[k] if e == e28} & {o["comparavel"] for e, o in occ[k] if e == e59}
    ]
    print(f"| {fam} | {len(nos_dois)} | {len(iguais)} | {fam_pal[fam]} de {fam_tot[fam]} |")

print("\n## Palavras por classificação da unidade principal\n")
print(
    "| Classificação | Unidades ativas (v3 · v2) | Palavras v3, simulados | Palavras v3, reais | Palavras v2 | Palavras v1 |"
)
print("|---|---|---|---|---|---|")
pc_s, pc_r = Counter(), Counter()
for e in eds:
    for o in linhas[e]:
        if o["unidade"] and o["unidade"] != "rodape":
            (pc_r if e in REAIS else pc_s)[U[o["unidade"]]["cls"]] += palavras(o["texto"])
tot_s, tot_r = sum(pc_s.values()), sum(pc_r.values())
nc = Counter(U[k]["cls"] for k in ativas)
for c in ["EXATA", "PARAMETRIZÁVEL", "SEMELHANTE", "INÉDITA", "ESPECIALIZADA"]:
    print(
        f"| {c} | {nc[c]} · {V2_CLS[c][0]} | {pc_s[c]} ({pc_s[c] / tot_s:.0%}) | {pc_r[c]} ({pc_r[c] / tot_r:.0%}) | "
        f"{V2_CLS[c][1]} | {V1['palavras_por_classificacao'][c]} |"
    )
so_c = sum(palavras(o["texto"]) for e in SIMULADOS for o in linhas[e] if o["unidade"] and U[o["unidade"]]["ori"] == "C")
print(f"\nFrases escritas pelo sistema (origem C pura), nos simulados: {so_c} palavras ({so_c / ts:.0%}).")
reclass = [k for k in IDS if k not in V3 and any("rodada 3" in h and "→" in h for h in U[k].get("hist") or [])]
print(f"Unidades anteriores reclassificadas na rodada 3: {len(reclass)}.")
