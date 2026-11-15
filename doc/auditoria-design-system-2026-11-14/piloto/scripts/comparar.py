"""Compara duas fotografias do piloto, estado a estado e largura a largura (172, FR-7723).

    python comparar.py <antes> <depois> <saida>

Lê os inventários `<pasta>/<código>/<largura>.json` que a jornada
`tests/navegador/test_fotografia_do_piloto.py` grava, e escreve `<saida>/<código>/<largura>.json`
com a diferença e `<saida>/resumo.md` com uma linha por estado.

**Conjunto, e não sequência.** Os blocos se comparam pelo texto e pelo item da estrutura que os
contém (D-006 da spec); a ordem só reprova onde uma sequência declarada em `sequencias.toml` se
inverte, na ordem do documento ou na visual. O resto da ordem fica registrado, sem valor de
aprovação (FR-7715).

Não grava nada no banco nem depende do Django: roda com o Python do projeto (`uv run python`),
que tem o `tomllib`; o do macOS é antigo demais.
"""

import json
import sys
import tomllib
from collections import Counter
from pathlib import Path

LIMITE_DA_LINHA = 80
SEQUENCIAS = Path(__file__).with_name("sequencias.toml")


def carregar(pasta):
    estados = {}
    for arquivo in sorted(Path(pasta).glob("*/*.json")):
        if arquivo.name == "fotografia.json":
            continue
        estados[(arquivo.parent.name, arquivo.stem)] = json.loads(arquivo.read_text())
    return estados


def chave_do_bloco(b):
    return (b["texto"], b["item"], b["visibilidade"])


def multiconjunto(itens, chave):
    return Counter(chave(i) for i in itens)


def diferenca(antes, depois, chave):
    a, d = multiconjunto(antes, chave), multiconjunto(depois, chave)
    return sorted((a - d).elements()), sorted((d - a).elements())


def tela_do_codigo(codigo):
    return {"C": "confirmacao", "O": "ocupacao", "R": "ocupacao", "K": "conferencia", "L": "lista"}[
        codigo[0]
    ]


def casa_um(bloco, termo):
    """Um termo de sequência: `=texto` é igual, `.classe` é classe, `<tag>` é etiqueta, `item:x`
    procura no item da estrutura, e o resto é trecho contido no texto."""
    if termo.startswith("="):
        return bloco["texto"] == termo[1:]
    if termo.startswith("."):
        return termo[1:] in bloco["classes"]
    if termo.startswith("<") and termo.endswith(">"):
        return bloco["tag"] == termo[1:-1]
    if termo.startswith("item:"):
        return termo[5:] in bloco["item"]
    return termo in bloco["texto"]


def casa(bloco, trechos):
    return any(casa_um(bloco, t) for t in trechos)


def sem_o_instavel(inventario, itens):
    """Tira do inventário o que a fixture não reproduz de uma montagem para a outra."""
    if not itens:
        return inventario
    fora = lambda item: any(item.startswith(i) or (" > " + i) in item for i in itens)  # noqa: E731
    blocos = [b for b in inventario["blocos"] if not fora(b["item"])]
    ids = {b["id"] for b in blocos}
    return {
        **inventario,
        "blocos": blocos,
        "quantidades": [q for q in inventario["quantidades"] if not fora(q["item"])],
        "acoes": [a for a in inventario["acoes"] if not fora(a.get("item", ""))],
        "ordem_documento": [i for i in inventario["ordem_documento"] if i in ids],
        "ordem_visual": [i for i in inventario["ordem_visual"] if i in ids],
    }


def escopos(blocos, escopo):
    """Agrupa os blocos pelo item do escopo pedido (`recorte`, `processo`) ou pela página."""
    if escopo == "pagina":
        return {"pagina": blocos}
    grupos = {}
    for b in blocos:
        parte = next((p for p in b["item"].split(" > ") if p.startswith(escopo + ":")), None)
        if parte:
            grupos.setdefault(parte, []).append(b)
    return grupos


def conferir_sequencia(seq, inventario):
    """`aprovada`, `invertida no documento`, `invertida na tela` ou `não se aplica`."""
    por_id = {b["id"]: b for b in inventario["blocos"]}
    resultados = []
    ordens = (("documento", inventario["ordem_documento"]), ("tela", inventario["ordem_visual"]))
    for nome_da_ordem, ordem in ordens:
        if seq.get("somente") and seq["somente"] != nome_da_ordem:
            continue
        blocos = [por_id[i] for i in ordem if i in por_id]
        for _, grupo in escopos(blocos, seq.get("escopo", "pagina")).items():
            primeiros = [i for i, b in enumerate(grupo) if casa(b, seq["antes"])]
            segundos = [i for i, b in enumerate(grupo) if casa(b, seq["depois"])]
            if not primeiros or not segundos:
                continue
            resultados.append(nome_da_ordem if max(primeiros) > min(segundos) else None)
    if not resultados:
        return "não se aplica"
    invertidas = sorted({r for r in resultados if r})
    return "aprovada" if not invertidas else "invertida no " + " e na ".join(invertidas)


def ordem_relativa(inventario_antes, inventario_depois):
    """Os blocos comuns que mudaram de posição relativa na ordem do documento."""
    def posicoes(inv):
        por_id = {b["id"]: b for b in inv["blocos"]}
        return [chave_do_bloco(por_id[i]) for i in inv["ordem_documento"] if i in por_id]

    a, d = posicoes(inventario_antes), posicoes(inventario_depois)
    comuns = [k for k in a if k in d]
    em_d = [k for k in d if k in comuns]
    return [k[0][:80] for i, k in enumerate(comuns) if i < len(em_d) and em_d[i] != k][:20]


def comparar_estado(antes, depois, sequencias, codigo, instaveis=()):
    antes, depois = sem_o_instavel(antes, instaveis), sem_o_instavel(depois, instaveis)
    faltaram, sobraram = diferenca(antes["blocos"], depois["blocos"], chave_do_bloco)
    q_falt, q_sobr = diferenca(
        antes["quantidades"], depois["quantidades"], lambda q: (q["numero"], q["rotulo"], q["item"])
    )
    acao = lambda a: (a["tipo"], a["rotulo"], a.get("metodo", ""), a["destino"], tuple(a.get("campos", [])))  # noqa: E731
    a_falt, a_sobr = diferenca(antes["acoes"], depois["acoes"], acao)

    # Uma associação desfeita é o bloco cujo texto continua, mas noutro item.
    textos_que_faltam = Counter(t for t, _, _ in faltaram)
    textos_que_sobram = Counter(t for t, _, _ in sobraram)
    associacoes = sorted((textos_que_faltam & textos_que_sobram).elements())

    tela = tela_do_codigo(codigo)
    resultado_das_sequencias = {
        s["id"]: conferir_sequencia(s, depois)
        for s in sequencias
        if "todas" in s["telas"] or tela in s["telas"]
    }
    longas = [
        {"bloco": next(b["texto"][:80] for b in depois["blocos"] if b["id"] == linha["bloco"]), "maior_linha": linha["maior_linha"]}
        for linha in depois.get("linhas", [])
        if linha["maior_linha"] > LIMITE_DA_LINHA
    ]
    falhas = []
    if faltaram or sobraram:
        falhas.append("texto")
    if q_falt or q_sobr:
        falhas.append("quantidade")
    if a_falt or a_sobr:
        falhas.append("ação")
    if any(v.startswith("invertida") for v in resultado_das_sequencias.values()):
        falhas.append("sequência")
    if longas:
        falhas.append("linha acima de 80")
    if depois.get("violacoes_de_csp"):
        falhas.append("CSP")
    if depois.get("rolagem_horizontal"):
        falhas.append("rolagem horizontal")
    dobra = depois.get("dobra")
    if dobra and dobra.get("achada") and not dobra.get("acima") and not dobra.get("anunciada"):
        falhas.append("ação abaixo da dobra")
    return {
        "faltaram": [list(f) for f in faltaram],
        "sobraram": [list(s) for s in sobraram],
        "associacoes": associacoes,
        "quantidades": {"faltaram": [list(q) for q in q_falt], "sobraram": [list(q) for q in q_sobr]},
        "acoes": {"faltaram": [list(map(str, a)) for a in a_falt], "sobraram": [list(map(str, a)) for a in a_sobr]},
        "sequencias": resultado_das_sequencias,
        "ordem_fora_das_sequencias": ordem_relativa(antes, depois),
        "linhas_acima_de_80": longas,
        "dobra": dobra,
        "falhas": falhas,
    }


def main(pasta_antes, pasta_depois, pasta_saida):
    dados = tomllib.loads(SEQUENCIAS.read_text())
    sequencias = dados["sequencia"]
    instaveis = {}
    for item in dados.get("instavel", []):
        instaveis.setdefault(item["codigo"], []).append(item["item"])
    antes, depois = carregar(pasta_antes), carregar(pasta_depois)
    if set(antes) != set(depois):
        so_antes = sorted(set(antes) - set(depois))
        so_depois = sorted(set(depois) - set(antes))
        sys.exit(f"as duas fotografias não têm os mesmos estados: só antes {so_antes}, só depois {so_depois}")
    saida = Path(pasta_saida)
    linhas = ["| Estado | Largura | Resultado |", "|---|---:|---|"]
    reprovados = 0
    for codigo, largura in sorted(antes, key=lambda k: (k[0], int(k[1]))):
        resultado = comparar_estado(
            antes[(codigo, largura)],
            depois[(codigo, largura)],
            sequencias,
            codigo,
            instaveis.get(codigo, ()),
        )
        destino = saida / codigo / f"{largura}.json"
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=1))
        reprovados += bool(resultado["falhas"])
        linhas.append(f"| {codigo} | {largura} | {', '.join(resultado['falhas']) or 'passou'} |")
    total = len(antes)
    # Uma sequência que não se aplica a estado nenhum tem trecho errado, e não aprova nada.
    aplicadas = set()
    for arquivo in saida.glob("*/*.json"):
        for sid, valor in json.loads(arquivo.read_text())["sequencias"].items():
            if valor != "não se aplica":
                aplicadas.add(sid)
    nunca = sorted({s["id"] for s in sequencias} - aplicadas)
    if nunca:
        linhas.insert(0, f"**Sequências que não se aplicaram a estado nenhum** (trecho a conferir): {', '.join(nunca)}\n")
    (saida / "resumo.md").write_text(
        f"# Comparação do piloto\n\n{total - reprovados} de {total} fotografias passaram.\n\n"
        + "\n".join(linhas)
        + "\n"
    )
    print(f"{total - reprovados} de {total} passaram; resumo em {saida / 'resumo.md'}")
    return 1 if reprovados else 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    sys.exit(main(*sys.argv[1:]))
