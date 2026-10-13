"""Exploratório (não é implementação): confirma o ED-01 no snapshot publicado do cenário B."""
import json, re, sys, os
sys.path.insert(0, "/Users/saymoncastro/Projetos/processo_seletivo/.claude/worktrees/auditoria-edital-pdf-d33731/backend")
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.development"
import django; django.setup()
from processo_seletivo.publicacoes.infrastructure import pdf
snap = json.load(open(sys.argv[1]))["content"]
numeros = pdf.numeracao(snap)
# rótulos de subseções geradas que o documento imprime (para checar remissões)
gerados = set()
for secao, corpo in pdf._materializaveis(snap):
    n = numeros.get(secao["key"])
    if secao.get("source") == "profiles":
        k = len(snap["profiles"]); grupos = pdf.grupos_de_atribuicoes(snap["profiles"])
        gerados |= {f"{n}.{i}" for i in range(1, k + len(grupos) + 1)}
    if secao.get("source") == "stages":
        gerados |= {f"{n}.{i}" for i in range(1, len(snap.get("stages") or []) + 1)}
PREFIXO = re.compile(r"^(\d{1,2})\.(\d{1,2})(?:\.\d{1,2})*\s")
REMISSAO = re.compile(r"\b(?:sub)?ite(?:m|ns)\s+(\d{1,2}(?:\.\d{1,2})+)", re.I)
digitados = {}
for secao in sorted(snap["sections"], key=lambda s: s["order"]):
    if secao.get("type") != "TEXT": continue
    n = numeros.get(secao["key"])
    for i, par in enumerate(pdf._paragrafos(secao.get("content", "")), 1):
        m = PREFIXO.match(par)
        if m:
            digitados[m.group(0).strip()] = (secao["title"], n)
            estado = "OK" if n is not None and int(m.group(1)) == n else "CONFLITO"
            print(f"[{estado}] seção «{secao['title']}» impressa como {n}; parágrafo {i} começa por {m.group(0).strip()}")
        for r in REMISSAO.finditer(par):
            alvo = r.group(1)
            onde = []
            if alvo in gerados: onde.append("subseção gerada do documento")
            if alvo in digitados: onde.append(f"subitem digitado na seção «{digitados[alvo][0]}» (impressa {digitados[alvo][1]})")
            print(f"   REMISSÃO em «{secao['title']}» ({n}), parágrafo {i}: «{r.group(0)}» → {onde or ['nenhum item com esse número no documento']}")
