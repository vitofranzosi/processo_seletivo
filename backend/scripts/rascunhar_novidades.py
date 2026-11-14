"""O rascunho das próximas Novidades do GPS, a partir dos PRs mergeados (168, FR-7424, `D-008`).

Rode de `backend/`, com o `gh` autenticado:

    uv run python scripts/rascunhar_novidades.py --saida /tmp/rascunho-das-novidades.md

Lista os PRs mergeados na `main` **depois do maior PR citado** em `novidades.toml`, agrupados pela
spec que o título ou a branch nomeiam, e marca os que só tocam documentação. Escreve um rascunho
em Markdown, com um esqueleto `[[nota]]` por grupo — a data já é a do último merge do grupo, no
horário de Brasília.

**Só rascunha.** Não escreve no arquivo das notas, não chama modelo de linguagem e não publica:
decidir o que é capacidade entregue, agrupar, descartar o que é só técnico e traduzir para quem
opera é curadoria, e a revisão do PR é a barreira (guia em `doc/curadoria-das-novidades.md`).
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
ARQUIVO = RAIZ / "processo_seletivo" / "novidades" / "novidades.toml"
BRASILIA = timezone(timedelta(hours=-3))

# O que não muda o produto que a pessoa usa: especificação, estudo, auditoria e o próprio guia.
SO_DOCUMENTACAO = re.compile(r"^(?:doc/|docs/|specs/|.*\.md$|\.claude/|\.specify/)")
# O título de um PR é "164: …", "feat(152): …", "Spec 165: …" ou cita a spec no meio; a branch
# costuma ser `claude/164-…`. O primeiro número de três dígitos é a spec.
SPEC = re.compile(r"(?<![\d#])(\d{3})(?!\d)")


def maior_pr_citado(conteudo):
    notas = tomllib.loads(conteudo).get("nota", [])
    return max((pr for nota in notas for pr in nota.get("prs", [])), default=0)


def spec_do_pr(pr):
    for texto in (pr.get("title", ""), pr.get("headRefName", "")):
        achado = SPEC.search(texto)
        if achado:
            return achado.group(1)
    return ""


def so_documentacao(pr):
    arquivos = [arquivo["path"] for arquivo in pr.get("files", [])]
    return bool(arquivos) and all(SO_DOCUMENTACAO.match(caminho) for caminho in arquivos)


def dia_do_merge(pr):
    instante = datetime.fromisoformat(pr["mergedAt"].replace("Z", "+00:00"))
    return instante.astimezone(BRASILIA).date()


def agrupar(prs, desde):
    """Os PRs depois de `desde`, por spec, na ordem do merge mais recente primeiro."""
    novos = sorted(
        (pr for pr in prs if pr["number"] > desde and pr.get("mergedAt")),
        key=lambda pr: pr["mergedAt"],
        reverse=True,
    )
    grupos = OrderedDict()
    for pr in novos:
        grupos.setdefault(spec_do_pr(pr) or f"sem-spec-{pr['number']}", []).append(pr)
    return grupos


def rascunho(grupos, desde):
    linhas = [
        "# Rascunho das Novidades do GPS",
        "",
        f"PRs mergeados na `main` depois do #{desde}, o maior citado em `novidades.toml`.",
        "Cada grupo é uma **candidata** a nota. Antes de copiar um esqueleto, confira no guia:",
        "o PR entrega capacidade que a pessoa usa? Todos os PRs da capacidade já estão na `main`?",
        "",
    ]
    for spec, prs in grupos.items():
        documentais = [pr for pr in prs if so_documentacao(pr)]
        produto = [pr for pr in prs if pr not in documentais]
        rotulo = f"spec {spec}" if not spec.startswith("sem-spec") else "sem spec"
        linhas += [f"## {rotulo}", ""]
        for pr in prs:
            marca = " — *só documentação: não vira nota*" if pr in documentais else ""
            linhas.append(f"- #{pr['number']} ({dia_do_merge(pr):%d/%m}) {pr['title']}{marca}")
        if produto:
            numeros = ", ".join(str(numero) for numero in sorted(pr["number"] for pr in produto))
            specs = f'["{spec}"]' if not spec.startswith("sem-spec") else "[]"
            linhas += [
                "",
                "```toml",
                "[[nota]]",
                'id = ""',
                f"data = {max(dia_do_merge(pr) for pr in produto).isoformat()}",
                'categoria = ""  # novidade, melhoria ou correcao',
                'titulo = ""',
                'resumo = """',
                '"""',
                'beneficio = ""',
                f"prs = [{numeros}]",
                f"specs = {specs}",
                "```",
            ]
        linhas.append("")
    if not grupos:
        linhas.append("Nenhum PR mergeado depois da última nota.")
    return "\n".join(linhas) + "\n"


def prs_mergeados(limite):
    saida = subprocess.run(
        [
            "gh",
            "pr",
            "list",
            "--state",
            "merged",
            "--base",
            "main",
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
    argumentos.add_argument("--limite", type=int, default=200, help="quantos PRs ler do GitHub")
    opcoes = argumentos.parse_args(argv)
    desde = maior_pr_citado(ARQUIVO.read_text(encoding="utf-8"))
    texto = rascunho(agrupar(prs_mergeados(opcoes.limite), desde), desde)
    if opcoes.saida:
        opcoes.saida.write_text(texto, encoding="utf-8")
        print(f"Rascunho em {opcoes.saida}", file=sys.stderr)
    else:
        print(texto)


if __name__ == "__main__":
    main()
