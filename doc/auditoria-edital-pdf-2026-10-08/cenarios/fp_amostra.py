"""Exploratório: falsos positivos da 065 sobre o texto dos Editais reais (não versiona texto)."""
import re, sys, glob, collections
sys.path.insert(0, "/Users/saymoncastro/Projetos/processo_seletivo/.claude/worktrees/auditoria-edital-pdf-d33731/backend")
from processo_seletivo.editais.domain.numeracao_digitada import numero_de_subitem, titulo_transcrito, remissoes
from processo_seletivo.publicacoes.domain import grafia
TITULO = re.compile(r"^\s*(\d{1,2})\s*[.\-–]\s+(?=[^a-zà-ÿ]*$)\S.{3,}$")
total = collections.Counter(); exemplos = collections.defaultdict(list)
for arq in sorted(glob.glob(sys.argv[1] + "/r*.txt")):
    secao = None; c = collections.Counter()
    for linha in open(arq, encoding="utf-8", errors="replace"):
        l = grafia.normalizar(linha.rstrip("\n")).strip()
        if not l: continue
        m = TITULO.match(l)
        if m: secao = int(m[1]); c["titulos"] += 1; continue
        sub = numero_de_subitem(l)
        if sub:
            c["subitens"] += 1
            if secao is not None and sub.primeiro != secao:
                c["acusados"] += 1
                forma = re.sub(r"\d", "9", sub.texto) + " após seção " + ("N" if secao else "?")
                exemplos[arq.split("/")[-1]].append((secao, sub.texto, re.sub(r"[A-Za-zÀ-ÿ]", "x", l[len(sub.texto):len(sub.texto)+25])))
        c["remissoes"] += len(remissoes(l))
    total.update(c)
    print(arq.split("/")[-1], dict(c))
print("TOTAL", dict(total))
for arq, lista in exemplos.items():
    print(arq, lista[:6])
