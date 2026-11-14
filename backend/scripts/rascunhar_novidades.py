"""O rascunho das próximas Novidades do GPS: o que entrou e ainda não foi curado (168, FR-7424).

Rode de `backend/`, com o `gh` autenticado:

    uv run python scripts/rascunhar_novidades.py --saida /tmp/rascunho-das-novidades.md

**Pendente é o que ninguém decidiu ainda.** Todo PR mergeado na `main` desde o `inicio` de
`novidades/curadoria.toml` termina num de três lugares: citado por uma nota de `novidades.toml`,
listado em `[[sem_nota]]` do registro com o motivo, ou só de documentação (reconhecido pelos
arquivos). O que não está em nenhum é pendente, e o rascunho o agrupa pela spec, com um esqueleto
`[[nota]]` por grupo.

**O corte é pela data do merge, e não pelo número do PR.** A primeira versão deste roteiro listava
os PRs de número maior que o maior citado; o número diz quando o PR foi aberto, e um PR antigo
mergeado depois sumia do levantamento — na janela de 17/10 a 14/11, 55 de 249 PRs entraram fora da
ordem do número. E o PR deixado de fora de propósito também sumia, sem registro de que foi
revisado.

**Só rascunha.** Não escreve no arquivo das notas nem no registro, não chama modelo de linguagem e
não publica: decidir o que é capacidade entregue e traduzir para quem opera é curadoria, e a revisão
do PR é a barreira (guia em `doc/curadoria-das-novidades.md`).
"""

import argparse
import json
import re
import subprocess
import sys
import tomllib
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
NOTAS = RAIZ / "processo_seletivo" / "novidades" / "novidades.toml"
REGISTRO = RAIZ / "processo_seletivo" / "novidades" / "curadoria.toml"
BRASILIA = timezone(timedelta(hours=-3))

# O que não muda o produto que a pessoa usa: especificação, estudo, auditoria e o próprio guia.
SO_DOCUMENTACAO = re.compile(r"^(?:doc/|docs/|specs/|.*\.md$|\.claude/|\.specify/)")
# A spec de um PR, nesta ordem: a branch `claude/164-…`; o título "164: …", "feat(152): …",
# "Spec 165: …" ou "143 — …". Um número de três dígitos solto no meio do título — "a ficha a
# 375 px" — não é spec, e agruparia o PR com outra capacidade.
SPEC_NA_BRANCH = re.compile(r"(?:^|/)(\d{3})-")
SPEC_NO_TITULO = (
    re.compile(r"^(\d{3})\b"),
    re.compile(r"^\w+\((\d{3})\)"),
    re.compile(r"\b[Ss]pecs? (\d{3})\b"),
)
# O `gh` devolve no máximo 100 arquivos por PR: com a lista cheia, não dá para afirmar que o PR só
# toca documentação.
TETO_DE_ARQUIVOS = 100


def ler_registro(notas, registro):
    """`(inicio, citados, sem_nota)`: o começo da janela e os PRs já decididos."""
    citados = {pr for nota in tomllib.loads(notas).get("nota", []) for pr in nota.get("prs", [])}
    dados = tomllib.loads(registro)
    sem_nota = {pr for grupo in dados.get("sem_nota", []) for pr in grupo.get("prs", [])}
    return dados["inicio"], citados, sem_nota


def spec_do_pr(pr):
    achado = SPEC_NA_BRANCH.search(pr.get("headRefName", ""))
    if achado:
        return achado.group(1)
    titulo = pr.get("title", "")
    for padrao in SPEC_NO_TITULO:
        achado = padrao.search(titulo)
        if achado:
            return achado.group(1)
    return ""


def so_documentacao(pr):
    arquivos = [arquivo["path"] for arquivo in pr.get("files", [])]
    if not arquivos or len(arquivos) >= TETO_DE_ARQUIVOS:
        return False
    return all(SO_DOCUMENTACAO.match(caminho) for caminho in arquivos)


def dia_do_merge(pr):
    instante = datetime.fromisoformat(pr["mergedAt"].replace("Z", "+00:00"))
    return instante.astimezone(BRASILIA).date()


def separar(prs, inicio, citados, sem_nota):
    """`(pendentes, documentais)` da janela; o resto já foi decidido."""
    da_janela = [pr for pr in prs if pr.get("mergedAt") and dia_do_merge(pr) >= inicio]
    abertos = [pr for pr in da_janela if pr["number"] not in citados | sem_nota]
    documentais = [pr for pr in abertos if so_documentacao(pr)]
    return [pr for pr in abertos if pr not in documentais], documentais


def agrupar(prs):
    """Os PRs por spec, o grupo do merge mais recente primeiro."""
    grupos = OrderedDict()
    for pr in sorted(prs, key=lambda pr: pr["mergedAt"], reverse=True):
        grupos.setdefault(spec_do_pr(pr) or f"sem-spec-{pr['number']}", []).append(pr)
    return grupos


def talvez_cortado(prs, limite):
    """O GitHub devolveu o limite pedido: pode haver PR da janela que não veio."""
    return len(prs) >= limite


def rascunho(grupos, inicio, *, documentais=0, cortado=False):
    linhas = []
    if cortado:
        linhas += [
            "> **Atenção: a lista pode estar incompleta.** O GitHub devolveu o limite de PRs",
            "> pedido. Rode de novo com um `--limite` maior antes de curar.",
            "",
        ]
    pendentes = sum(len(prs) for prs in grupos.values())
    linhas += [
        "# Rascunho das Novidades do GPS",
        "",
        f"PRs mergeados na `main` desde {inicio:%d/%m/%Y} que nenhuma nota cita e que o registro",
        f"`curadoria.toml` não dispensou: **{pendentes}**, em {len(grupos)} grupo(s).",
        f"Só de documentação, fora do rascunho: {documentais}.",
        "",
        "Cada grupo termina numa nota de `novidades.toml` — nova, ou acrescentada a uma que já",
        "existe — ou em `[[sem_nota]]` do registro, com o motivo. Nenhum fica sem destino.",
        "",
    ]
    for spec, prs in grupos.items():
        rotulo = f"spec {spec}" if not spec.startswith("sem-spec") else "sem spec"
        linhas += [f"## {rotulo}", ""]
        linhas += [f"- #{pr['number']} ({dia_do_merge(pr):%d/%m}) {pr['title']}" for pr in prs]
        numeros = ", ".join(str(numero) for numero in sorted(pr["number"] for pr in prs))
        specs = f'["{spec}"]' if not spec.startswith("sem-spec") else "[]"
        linhas += [
            "",
            "```toml",
            "[[nota]]",
            'id = ""',
            f"data = {max(dia_do_merge(pr) for pr in prs).isoformat()}",
            'categoria = ""  # novidade, melhoria ou correcao',
            'titulo = ""',
            'resumo = """',
            '"""',
            'beneficio = ""',
            f"prs = [{numeros}]",
            f"specs = {specs}",
            "```",
            "",
        ]
    if not grupos:
        linhas.append("Nada pendente: todo PR da janela já tem destino.")
    return "\n".join(linhas) + "\n"


def prs_mergeados(inicio, limite):
    saida = subprocess.run(
        [
            "gh",
            "pr",
            "list",
            "--state",
            "merged",
            "--base",
            "main",
            "--search",
            f"merged:>={inicio.isoformat()}",
            "--limit",
            str(limite),
            "--json",
            "number,title,mergedAt,headRefName,files",
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return json.loads(saida)


def main(argv=None):
    argumentos = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    argumentos.add_argument("--saida", type=Path, help="arquivo do rascunho (padrão: a tela)")
    argumentos.add_argument("--limite", type=int, default=1000, help="quantos PRs ler do GitHub")
    opcoes = argumentos.parse_args(argv)
    inicio, citados, sem_nota = ler_registro(
        NOTAS.read_text(encoding="utf-8"), REGISTRO.read_text(encoding="utf-8")
    )
    # Um dia antes, porque a busca do GitHub é em UTC e a janela é em Brasília; `separar` corta.
    prs = prs_mergeados(inicio - timedelta(days=1), opcoes.limite)
    cortado = talvez_cortado(prs, opcoes.limite)
    if cortado:
        print("Atenção: a lista pode estar incompleta; aumente --limite.", file=sys.stderr)
    pendentes, documentais = separar(prs, inicio, citados, sem_nota)
    texto = rascunho(agrupar(pendentes), inicio, documentais=len(documentais), cortado=cortado)
    if opcoes.saida:
        opcoes.saida.write_text(texto, encoding="utf-8")
        print(f"Rascunho em {opcoes.saida}", file=sys.stderr)
    else:
        print(texto)


if __name__ == "__main__":
    main()
