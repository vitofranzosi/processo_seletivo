"""A prova de que dividir a folha comum por área não muda o vencedor de nenhuma propriedade (091, R-003).

    ordem.py preparar <gestao.css>          → candidatos.json (Chrome, sem página do sistema)
    capturar.py com CONFLITOS=candidatos.json → <saída>/conflitos.json (as páginas do inventário)
    ordem.py resolver <gestao.css> <conflitos.json> <destino>  → os arquivos por área e o relatório

A cascata decide entre duas declarações da mesma propriedade, no mesmo elemento, pela importância,
pela especificidade e, empatadas, pela ordem. Trocar a ordem de duas regras só pode mudar o resultado
se elas (1) declaram uma mesma propriedade — já expandidos os atalhos, que o Chrome expande pelo
CSSOM —, (2) têm, num par de seletores, a mesma especificidade e o mesmo pseudoelemento, e (3)
alcançam um mesmo elemento. A (3) é medida nas páginas do inventário, com o seletor **alargado**:
sem pseudoclasses, sem atributos, sem `:not()` e sem `:has()` — o casamento só cresce. Um seletor que
não casa com nada em página nenhuma, ou que o navegador recusa, é tratado como se casasse com tudo:
a regra dele não troca de ordem com quem disputa propriedade com ela.

A condição de mídia não entra (duas regras em `@media` diferentes ainda podem valer juntas). Tudo do
lado conservador: o que a prova libera, libera com folga.

A área final de cada regra sai de `areas.py` e de uma regra só: se A vinha antes de B e as duas
disputam, B não pode ficar num arquivo que carrega antes do de A — B desce para o arquivo de A.
"""

import json
import re
import sys
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from areas import AREAS, classificar  # noqa: E402
from coocorrencia import podem_coincidir  # noqa: E402

AQUI = Path(__file__).parent

# ---- seletores ------------------------------------------------------------------------------------


def separar(lista):
    """`a, b:is(c, d)` → `["a", "b:is(c, d)"]`: vírgula de primeiro nível."""
    partes, nivel, atual = [], 0, ""
    for c in lista:
        if c in "([":
            nivel += 1
        elif c in ")]":
            nivel -= 1
        if c == "," and nivel == 0:
            partes.append(atual.strip())
            atual = ""
        else:
            atual += c
    partes.append(atual.strip())
    return [p for p in partes if p]


def _argumento(texto, i):
    """O texto entre o parêntese em `i` e o que o fecha, e a posição depois dele."""
    nivel, j = 0, i
    while True:
        if texto[j] == "(":
            nivel += 1
        elif texto[j] == ")":
            nivel -= 1
            if nivel == 0:
                return texto[i + 1 : j], j + 1
        j += 1


PSEUDOELEMENTOS_ANTIGOS = ("before", "after", "first-line", "first-letter")


def especificidade(seletor):
    """(ids, classes, tipos) de um seletor complexo, como o CSS Selectors 4 conta."""
    ids = classes = tipos = 0
    i, n = 0, len(seletor)
    while i < n:
        c = seletor[i]
        if c == "#":
            ids += 1
            i += 1
            while i < n and re.match(r"[\w-]", seletor[i]):
                i += 1
        elif c == ".":
            classes += 1
            i += 1
            while i < n and re.match(r"[\w-]", seletor[i]):
                i += 1
        elif c == "[":
            classes += 1
            _, i = _argumento(seletor.replace("[", "(").replace("]", ")"), i)
        elif c == ":":
            elemento = seletor.startswith("::", i)
            i += 2 if elemento else 1
            nome = re.match(r"[\w-]+", seletor[i:]).group(0)
            i += len(nome)
            argumento = None
            if i < n and seletor[i] == "(":
                argumento, i = _argumento(seletor, i)
            if elemento or nome in PSEUDOELEMENTOS_ANTIGOS:
                tipos += 1
            elif nome == "where":
                pass
            elif nome in ("is", "not", "has"):
                maior = max(especificidade(a) for a in separar(argumento))
                ids, classes, tipos = ids + maior[0], classes + maior[1], tipos + maior[2]
            elif nome.startswith("nth-") and argumento and " of " in argumento:
                maior = max(especificidade(a) for a in separar(argumento.split(" of ", 1)[1]))
                ids, classes, tipos = ids + maior[0], classes + maior[1] + 1, tipos + maior[2]
            else:
                classes += 1
        elif re.match(r"[A-Za-z]", c):
            tipos += 1
            while i < n and re.match(r"[\w-]", seletor[i]):
                i += 1
        else:
            i += 1
    return (ids, classes, tipos)


def alargar(seletor):
    """O seletor sem o que muda com o uso: (seletor alargado, pseudoelemento).

    Saem as pseudoclasses (estado e estrutura), os atributos, `:not()` e `:has()`; `:is()` e
    `:where()` ficam, com os argumentos alargados. Compostos que ficam vazios viram `*`.
    """
    pseudo = ""
    saida, i, n = "", 0, len(seletor)
    while i < n:
        c = seletor[i]
        if c == "[":
            _, i = _argumento(seletor.replace("[", "(").replace("]", ")"), i)
            continue
        if c == ":":
            elemento = seletor.startswith("::", i)
            j = i + (2 if elemento else 1)
            nome = re.match(r"[\w-]+", seletor[j:]).group(0)
            j += len(nome)
            argumento = None
            if j < n and seletor[j] == "(":
                argumento, j = _argumento(seletor, j)
            if elemento or nome in PSEUDOELEMENTOS_ANTIGOS:
                pseudo = nome
            elif nome in ("is", "where"):
                saida += ":is(" + ", ".join(alargar(a)[0] for a in separar(argumento)) + ")"
            i = j
            continue
        saida += c
        i += 1
    # Composto vazio — `.a > :hover` virou `.a > `, e `.a :hover`, `.a ` — ganha `*`. Sem tirar o
    # espaço do fim antes: ele é o combinador de descendência.
    pedacos = re.split(r"(\s*[>+~]\s*|\s+)", saida.lstrip())
    montado = "".join(p if k % 2 or p else "*" for k, p in enumerate(pedacos))
    return montado.strip() or "*", pseudo


def sujeito(largo):
    """O último composto de um seletor alargado: `.a > .b input` → `input`.

    Mais largo que o seletor inteiro. Serve ao seletor que não casa com nada no inventário: se o
    sujeito dele casa, o inventário diz com quem ele poderia dividir elemento; se nem o sujeito
    casa, nada se sabe, e o seletor casa com tudo (a suposição da spec).
    """
    nivel, corte = 0, 0
    for k, c in enumerate(largo):
        if c == "(":
            nivel += 1
        elif c == ")":
            nivel -= 1
        elif nivel == 0 and c in " >+~":
            corte = k + 1
    return largo[corte:].strip() or "*"


# ---- preparar ----------------------------------------------------------------------------------

EXPANDIR = r"""(regras) => regras.map((texto) => {
  const folha = new CSSStyleSheet();
  try { folha.replaceSync(texto); } catch (e) { return {erro: String(e)}; }
  const seletores = [], propriedades = new Set();
  const andar = (lista) => {
    for (const r of lista) {
      if (r.cssRules && r.selectorText === undefined) { andar(r.cssRules); continue; }
      if (r.selectorText !== undefined) seletores.push(r.selectorText);
      if (r.style) for (let k = 0; k < r.style.length; k++) propriedades.add(r.style[k]);
    }
  };
  andar(folha.cssRules);
  return {seletores, propriedades: [...propriedades], regras: folha.cssRules.length};
})"""


def preparar(caminho_css):
    from playwright.sync_api import sync_playwright

    unidades, _ = classificar(caminho_css)
    with sync_playwright() as p:
        navegador = p.chromium.launch(channel="chrome")
        pagina = navegador.new_page()
        pagina.set_content("<!doctype html><title>x</title>")
        expandidas = pagina.evaluate(EXPANDIR, [u.regra for u in unidades])
        navegador.close()

    seletores, chave_do_seletor = [], {}
    por_unidade = []
    for u, e in zip(unidades, expandidas, strict=True):
        assert "erro" not in e and e["regras"] == 1, (u.linha, u.cabeca, e)
        lista = []
        for s in e["seletores"]:
            for simples in separar(s):
                largo, pseudo = alargar(simples)
                if largo not in chave_do_seletor:
                    chave_do_seletor[largo] = len(seletores)
                    seletores.append(largo)
                lista.append((chave_do_seletor[largo], pseudo, especificidade(simples), simples))
        por_unidade.append({"propriedades": set(e["propriedades"]), "seletores": lista})

    # O sujeito de cada seletor entra na lista, para ser medido junto (`conflitos_entre_regras`).
    sujeitos = []
    for largo in list(seletores):
        alvo = sujeito(largo)
        if alvo not in chave_do_seletor:
            chave_do_seletor[alvo] = len(seletores)
            seletores.append(alvo)
        sujeitos.append(chave_do_seletor[alvo])
    sujeitos += list(range(len(sujeitos), len(seletores)))
    pares, de_quem = {}, {}
    for i, j in product(range(len(unidades)), repeat=2):
        if i >= j:
            continue
        if not por_unidade[i]["propriedades"] & por_unidade[j]["propriedades"]:
            continue
        for a, b in product(por_unidade[i]["seletores"], por_unidade[j]["seletores"]):
            if a[1] != b[1] or a[2] != b[2]:
                continue
            par = (min(a[0], b[0]), max(a[0], b[0]))
            pares.setdefault(par, len(pares))
            de_quem.setdefault(pares[par], set()).add((i, j))

    destino = AQUI / "candidatos.json"
    destino.write_text(
        json.dumps(
            {
                "seletores": seletores,
                "sujeitos": sujeitos,
                "pares": [list(p) for p in pares],
                "de_quem": {k: sorted(v) for k, v in de_quem.items()},
                "unidades": [
                    {
                        "linha": u.linha,
                        "cabeca": u.cabeca,
                        "area": u.area,
                        "propriedades": sorted(d["propriedades"]),
                        "seletores": [[s[0], s[1], list(s[2]), s[3]] for s in d["seletores"]],
                    }
                    for u, d in zip(unidades, por_unidade, strict=True)
                ],
            },
            ensure_ascii=False,
        )
    )
    print(len(unidades), "regras,", len(seletores), "seletores alargados,", len(pares), "pares candidatos")


# ---- resolver ----------------------------------------------------------------------------------


def conflitos_entre_regras(candidatos, medidos):
    """Os pares de regras (i, j), i antes de j, que não podem trocar de ordem."""
    nunca = {k for k, n in enumerate(medidos["casou"]) if n <= 0}
    sujeitos, seletores = candidatos["sujeitos"], candidatos["seletores"]
    # `acertos[v]`: os pares que se alcançam, com o seletor trocado pelo sujeito — v=0 nenhum, 1 o
    # da esquerda, 2 o da direita, 3 os dois.
    acertos = [set(a) for a in medidos["acertos"]]
    conflito, sem_saber = set(), set()
    for k, (a, b) in enumerate(candidatos["pares"]):
        troca_a, troca_b = a in nunca, b in nunca
        if (troca_a and sujeitos[a] in nunca) or (troca_b and sujeitos[b] in nunca):
            # O inventário não sabe; os modelos podem saber (`coocorrencia.py`).
            alcanca = podem_coincidir(seletores[sujeitos[a]], seletores[sujeitos[b]])
            if alcanca:
                sem_saber.add(k)
        else:
            alcanca = k in acertos[troca_a + 2 * troca_b]
        if alcanca:
            conflito |= {tuple(p) for p in candidatos["de_quem"][str(k)]}
    return conflito, nunca, sem_saber


CABECALHOS = {
    "base": "",  # o comentário de topo da 089, que abre a primeira regra, fica como está
    "moldura": """/* A moldura da gestão: o cabeçalho do topo das telas sem barra e o shell da 076 — a barra lateral,
   as seções, a pessoa identificada, o cabeçalho de contexto. Segundo arquivo da folha comum, depois
   de `base.css` (091; a ordem de carga está em `shared/estaticos.py`, `FOLHAS_DA_GESTAO`). */
""",
    "impressao": """/* O que a gestão põe no papel (088). Terceiro arquivo, e não o último: a regra de impressão estava
   logo depois do shell, e disputa propriedade com centenas de regras que vêm depois dela — no fim da
   folha, ela passaria a vencê-las no papel (091, R-002). */
""",
    "componentes": """/* Os componentes comuns: botões e ações, marcas, cartões, a ajuda, o vazio, a situação. A área de
   cada regra é a do seletor; as poucas que ficaram noutro arquivo para não trocar de ordem com uma
   regra que disputa a mesma propriedade estão listadas no R-002 da 091. */
""",
    "formularios": """/* Os formulários: campos, linhas de campos, escolhas, filtros, a barra de gravação, os controles.
   Depois dos componentes, na ordem em que as regras já se aplicavam (091). */
""",
    "tabelas": """/* As tabelas: célula, cabeçalho, legenda, a moldura que rola, a paginação (091). */
""",
    "telas": """/* As regras que citam uma tela ou um painel de uma tela só, e que ficam na folha comum porque mais
   de uma página as usa, ou porque saíram de lá antes de existir o estilo por tela. O estilo que é de
   uma tela só mora em `interface/telas/`, e o de um grupo de telas, em `interface/grupos/`. Último
   arquivo da folha comum: `[hidden]` está aqui, no fim, porque precisa vencer o `display` de toda
   regra anterior (091, R-002). */
""",
}


def distribuir(desejada, conflitos):
    """O arquivo de cada regra: o mais perto da área desejada, sem inverter par em conflito.

    A restrição é `arquivo[i] <= arquivo[j]` para todo par (i, j) em conflito, i antes de j. Entre
    as distribuições que a cumprem, a que menos afasta as regras das suas áreas, somando a distância
    em arquivos — regressão isotônica com perda L1 sobre a ordem parcial dos conflitos. Ela se
    resolve limiar a limiar: para cada `t`, quais regras ficam no arquivo `t` ou depois é um corte
    mínimo, e os cortes de limiares seguidos se encaixam. Empurrar sempre a regra de baixo — a
    primeira versão — também cumpria a restrição, mas levava `.acao` e `.campo` para as telas.
    """
    import networkx as nx

    n = len(desejada)
    arquivo = [0] * n
    anterior = set(range(n))
    for t in range(1, len(AREAS)):
        grafo = nx.DiGraph()
        grafo.add_nodes_from(["s", "t", *range(n)])
        for i, j in conflitos:
            grafo.add_edge(i, j, capacity=float("inf"))
        for k in range(n):
            if desejada[k] >= t:
                grafo.add_edge("s", k, capacity=1)
            else:
                grafo.add_edge(k, "t", capacity=1)
        _, (lado_s, _) = nx.minimum_cut(grafo, "s", "t")
        acima = {k for k in lado_s if k != "s"}
        # Os limiares se encaixam: quem fica a partir de `t` ficava a partir de `t - 1`.
        acima &= anterior
        for k in acima:
            arquivo[k] = t
        anterior = acima
    return arquivo


def resolver(caminho_css, caminho_conflitos, destino):
    candidatos = json.loads((AQUI / "candidatos.json").read_text())
    medidos = json.loads(Path(caminho_conflitos).read_text())
    unidades, resto = classificar(caminho_css)
    conflitos, nunca, sem_saber = conflitos_entre_regras(candidatos, medidos)

    ordem = {a: k for k, a in enumerate(AREAS)}
    desejada = [ordem[u.area] for u in unidades]
    arquivo = distribuir(desejada, conflitos)

    # Conferência: nenhum par em conflito invertido na ordem de carga.
    posicao = sorted(range(len(unidades)), key=lambda k: (arquivo[k], k))
    lugar = {k: n for n, k in enumerate(posicao)}
    invertidos = [(i, j) for i, j in conflitos if lugar[i] > lugar[j]]
    assert not invertidos, invertidos[:5]

    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    textos = {a: "" for a in AREAS}
    for k in range(len(unidades)):
        textos[AREAS[arquivo[k]]] += unidades[k].texto
    textos[AREAS[-1]] += resto
    for area, texto in textos.items():
        # O texto de cada unidade começa pelo que vinha antes dela — a quebra de linha da regra
        # anterior e os comentários. O arquivo começa pelo cabeçalho, e sem linha em branco.
        (destino / f"{area}.css").write_text(CABECALHOS[area] + texto.lstrip("\n"))
    fora = [
        (unidades[k].linha, unidades[k].cabeca, AREAS[desejada[k]], AREAS[arquivo[k]])
        for k in range(len(unidades))
        if arquivo[k] != desejada[k]
    ]
    relatorio = {
        "regras": len(unidades),
        "pares_em_conflito": len(conflitos),
        "seletores_sem_elemento": len(nunca),
        "pares_sem_saber": len(sem_saber),
        "por_area": {a: sum(1 for k in range(len(unidades)) if AREAS[arquivo[k]] == a) for a in AREAS},
        "fora_da_area": fora,
        "trocas_de_ordem": sum(
            1 for i in range(len(unidades)) for j in range(i + 1, len(unidades)) if lugar[i] > lugar[j]
        ),
    }
    (AQUI / "ordem.json").write_text(json.dumps(relatorio, ensure_ascii=False, indent=1))
    print(json.dumps({k: v for k, v in relatorio.items() if k != "fora_da_area"}, ensure_ascii=False))
    print(len(fora), "regras fora da área desejada")
    return textos, resto


if __name__ == "__main__":
    if sys.argv[1] == "preparar":
        preparar(sys.argv[2])
    elif sys.argv[1] == "resolver":
        resolver(sys.argv[2], sys.argv[3], sys.argv[4])
