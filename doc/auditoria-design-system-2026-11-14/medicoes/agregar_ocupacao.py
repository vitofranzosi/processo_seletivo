"""Agrega o registro: por estado, quantos testes o desenham, e exemplos."""

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import registro_da_ocupacao as r  # noqa: E402

pasta = Path(sys.argv[1])
linhas = [json.loads(x) for arq in pasta.glob("*.jsonl") for x in arq.read_text().splitlines()]
por_tela = defaultdict(set)
pagina = defaultdict(set)
secao = defaultdict(set)
combos = defaultdict(set)
for linha in linhas:
    por_tela[linha["tela"]].add(linha["teste"])
    if linha["tela"] != "interface/ocupacao.html":
        if linha.get("erro"):
            por_tela[linha["tela"] + " (com recusa)"].add(linha["teste"])
        continue
    pode = any(any(m.startswith("form_") for m in b) for b in linha["recortes"])
    pagina["quem_pode_emitir" if pode else "quem_so_le"].add(linha["teste"])
    pagina[f"recortes={len(linha['recortes'])}"].add(linha["teste"])
    for nome in linha["pagina"]:
        pagina[nome].add(linha["teste"])
    for bloco in linha["recortes"]:
        combos[tuple(bloco)].add(linha["teste"])
        for nome in bloco:
            secao[nome].add(linha["teste"])


def mostra(titulo, nomes, onde):
    print(f"\n## {titulo}")
    for nome in nomes:
        testes = sorted(onde.get(nome, ()))
        arquivos = sorted({t.split("::")[0] for t in testes})
        print(f"{len(testes):5d}  {nome}  [{len(arquivos)} arq.]  {'; '.join(arquivos[:3])}")


print(f"desenhos: {len(linhas)}")
for tela, testes in sorted(por_tela.items()):
    print(f"{len(testes):5d} testes  {tela}  [{len({t.split('::')[0] for t in testes})} arq.]")
extras = sorted(k for k in pagina if k not in r.CABECA)
mostra("Página", list(r.CABECA) + extras, pagina)
mostra("Recorte", list(r.SECAO) + ["declaracao_na_lista", "frase_da_vaga", "vigente"], secao)
print(f"\n## Combinações distintas por recorte: {len(combos)}")
if "--combos" in sys.argv:
    for combo, testes in sorted(combos.items(), key=lambda kv: -len(kv[1])):
        print(f"{len(testes):5d}  {', '.join(combo) or '(vazio)'}")
if "--testes" in sys.argv:
    print("\n## Arquivos que desenham a Ocupação")
    arqs = defaultdict(int)
    for t in por_tela["interface/ocupacao.html"]:
        arqs[t.split("::")[0]] += 1
    for a, n in sorted(arqs.items(), key=lambda kv: -kv[1]):
        print(f"{n:5d}  {a}")
