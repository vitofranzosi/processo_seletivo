"""A folha do portal em arquivo é o `<style>` de antes, mais o que a 092 declara (FR-2131).

    equivalencia.py <commit-de-antes>

Lê o `<style>` do `portal/base.html` no commit de antes (`git show`) e o `portal/portal.css` da árvore
de trabalho, e desfaz no arquivo, uma a uma, as mudanças que a pesquisa lista (R-002): o comentário
de cabeçalho, o bloco das classes de percentual e as sete grafias que a varredura de sintaxe vazada
acusaria. O que sobra tem de ser **igual, byte a byte**, ao `<style>` de antes — mesmas regras, mesma
ordem, mesmos comentários. Cada desfazer tem de casar exatamente uma vez: uma mudança que não está lá,
ou que está duas vezes, reprova.

Roda de qualquer lugar da worktree; sai com código 1 se reprovar.
"""

import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
BASE = "backend/processo_seletivo/portal/templates/portal/base.html"
ARQUIVO = RAIZ / "backend/processo_seletivo/portal/static/portal/portal.css"

antes = subprocess.check_output(["git", "-C", str(RAIZ), "show", f"{sys.argv[1]}:{BASE}"], text=True)
antes = antes[antes.index("<style>\n") + len("<style>\n") : antes.index("</style>\n")]
depois = ARQUIVO.read_text()

# As sete grafias (R-002): a de depois → a de antes.
GRAFIAS = [
    ("  max-width:100%;}\n.consulta .acoes", "  max-width:100%}\n.consulta .acoes"),
    (".vagas-numero .reserva{flex-basis:100%;}", ".vagas-numero .reserva{flex-basis:100%}"),
    ("line-height:1.3;flex-basis:100%;}", "line-height:1.3;flex-basis:100%}"),
    (".reserva-primeiro>span{flex-basis:100%;}", ".reserva-primeiro>span{flex-basis:100%}"),
    ("font-weight:600;width:100%;}", "font-weight:600;width:100%}"),
    ("align-items:end}\n}", "align-items:end}}"),
    ("  .lateral-vaga .principal{width:100%;}", "  .lateral-vaga .principal{width:100%}"),
]

falhas = []


def desfazer(texto, de, para, nome):
    if texto.count(de) != 1:
        falhas.append(f"{nome}: casou {texto.count(de)} vezes")
        return texto
    return texto.replace(de, para)


# O cabeçalho: o primeiro comentário do arquivo, e só ele.
cabecalho = re.match(r"/\*.*?\*/\n", depois, re.S)
depois = depois[cabecalho.end() :] if cabecalho else (falhas.append("sem cabeçalho") or depois)

# As classes de percentual: o comentário que as explica e as onze linhas de 0 a 100.
linhas = "\n".join(
    " ".join(f".largura-{v}{{width:{v}%;}}" for v in range(d, min(d + 10, 101)))
    for d in range(0, 101, 10)
)
bloco = re.search(r"/\* A largura preenchida da barra \(092\)\..*?\*/\n" + re.escape(linhas) + "\n", depois, re.S)
if bloco:
    depois = depois[: bloco.start()] + depois[bloco.end() :]
else:
    falhas.append("sem o bloco das classes de percentual")

for de, para in GRAFIAS:
    depois = desfazer(depois, de, para, f"grafia {para.strip()[:40]!r}")

if depois != antes:
    falhas.append("o resto difere do <style> de antes")
    for i, (a, b) in enumerate(zip(antes.splitlines(), depois.splitlines(), strict=False), 1):
        if a != b:
            falhas.append(f"  primeira linha diferente, {i}: {a!r} | {b!r}")
            break

regras = len(re.findall(r"\{", re.sub(r"/\*.*?\*/", "", antes, flags=re.S)))
comentarios = len(re.findall(r"/\*", antes))
if falhas:
    print("REPROVA", *falhas, sep="\n")
    sys.exit(1)
print(
    f"EQUIVALENTE: o <style> de {sys.argv[1]} ({len(antes)} bytes, {regras} chaves de abertura, "
    f"{comentarios} comentários) é o arquivo menos o cabeçalho, as 101 classes e {len(GRAFIAS)} grafias"
)
