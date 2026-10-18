"""A divisão da folha comum não perdeu, não mudou e não duplicou regra nenhuma (091, FR-2090, FR-2094).

    equivalencia.py            (de qualquer lugar)

Compara as unidades — regra ou bloco `@media`, com os comentários que a precedem — do `gestao.css` de
antes da divisão (guardado ao lado, `gestao-antes-da-divisao.css`) com as dos sete arquivos de
`interface/gestao/`: o mesmo multiconjunto de regras, byte a byte, e o mesmo de comentários. Dentro de
cada arquivo, a ordem relativa é a de antes. A ordem **entre** arquivos é do `ordem.py`.

E a varredura de duplicadas (FR-2093, SC-816): nas folhas que uma mesma página carrega — a comum,
mais a de cada tela e a de cada grupo —, nenhum par de regras com o mesmo seletor, as mesmas
declarações e a mesma mídia.
"""

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from areas import AREAS  # noqa: E402
from unidades import ler  # noqa: E402

AQUI = Path(__file__).parent
ESTATICOS = AQUI.parents[2] / "backend/processo_seletivo/interface/static/interface"
BASES = AQUI.parents[2] / "backend/processo_seletivo/interface/templates/interface"

antes, _ = ler((AQUI / "gestao-antes-da-divisao.css").read_text())
depois = []
for area in AREAS:
    unidades, _ = ler((ESTATICOS / "gestao" / f"{area}.css").read_text(), origem=area)
    posicoes = [next(k for k, u in enumerate(antes) if u.regra == d.regra) for d in unidades]
    assert posicoes == sorted(posicoes), f"{area}: a ordem relativa de antes mudou dentro do arquivo"
    depois += unidades

regras_antes, regras_depois = Counter(u.regra for u in antes), Counter(u.regra for u in depois)
assert regras_antes == regras_depois, (regras_antes - regras_depois, regras_depois - regras_antes)


def comentarios(unidades):
    return Counter(c for u in unidades for c in u.comentarios.split("/*")[1:])


# Os comentários de antes estão todos depois; depois há também os cabeçalhos dos arquivos novos. O
# de topo da 089 ganhou um parágrafo sobre a divisão: vale se o texto de antes está inteiro no começo.
faltando = comentarios(antes) - comentarios(depois)
estendidos = [
    c for c in faltando
    if any(d.startswith(c.removesuffix("*/\n").rstrip()) for d in comentarios(depois))
]
assert set(faltando) == set(estendidos), [c[:80] for c in set(faltando) - set(estendidos)]
print(f"EQUIVALENTE: {sum(regras_antes.values())} regras e {sum(comentarios(antes).values())} comentários,"
      f" nos {len(AREAS)} arquivos; {len(estendidos)} estendido(s) com a nota da 091")

# ---- duplicadas, página a página -----------------------------------------------------------------

comum = depois
de_tela = {}
for arquivo in sorted([*ESTATICOS.glob("telas/*.css"), *ESTATICOS.glob("grupos/*.css")]):
    de_tela[f"{arquivo.parent.name}/{arquivo.name}"], _ = ler(arquivo.read_text())

# O que cada modelo carrega além da comum (a página de acesso não carrega a comum).
import re  # noqa: E402

pares = []
for modelo in sorted(BASES.glob("*.html")):
    citadas = re.findall(r"""\{%\s*estatico\s+'interface/((?:telas|grupos)/[^']+)'""", modelo.read_text())
    if not citadas:
        continue
    acesso = "grupos/acesso.css" in citadas
    juntas = ([] if acesso else comum) + [u for c in citadas for u in de_tela[c]]
    contagem = Counter(u.normalizada for u in juntas)
    pares += [(modelo.name, regra[:70]) for regra, n in contagem.items() if n > 1]
contagem_comum = Counter(u.normalizada for u in comum)
pares += [("folha comum", regra[:70]) for regra, n in contagem_comum.items() if n > 1]
print("duplicadas no que uma página carrega:", len(pares), pares[:5])
sys.exit(1 if pares else 0)
