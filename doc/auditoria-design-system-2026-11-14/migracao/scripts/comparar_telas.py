"""Compara dois rastreios do instrumento do estudo (antes e depois), tela a tela.

    uv run --with pillow python comparar_telas.py <antes> <depois> <saida.json> <pasta-das-imagens>

Para cada padrão de tela que os dois lados têm: recorta a captura de 1440 px na área do `main`,
compara os pixels, e junta as medidas do telas.csv. Grava as imagens reduzidas em JPEG e um JSON
com tudo, que o montador do HTML lê.
"""
import csv, json, re, sys, pathlib, hashlib
from PIL import Image, ImageChops

A, D, SAIDA, IMG = (pathlib.Path(x) for x in sys.argv[1:5])
IMG.mkdir(parents=True, exist_ok=True)
LARGURA = int(sys.argv[5]) if len(sys.argv) > 5 else 720
QUALIDADE = int(sys.argv[6]) if len(sys.argv) > 6 else 50


def ler(pasta):
    rep = json.load(open(pasta / "representantes.json"))
    linhas = {r["tela"]: r for r in csv.DictReader(open(pasta / "telas.csv"))}
    larguras = json.load(open(pasta / "larguras.json"))
    return rep, linhas, larguras


def recorte(pasta, r):
    if not r.get("captura"):
        return None
    caminho = pasta / "cap" / r["captura"]
    if not caminho.exists():
        return None
    im = Image.open(caminho).convert("RGB")
    m = r.get("main") or {}
    x, w = m.get("x", 0), m.get("w", im.width)
    # A coluna do conteúdo, com 16 px de margem; a barra lateral da moldura fica fora. O instrumento
    # só mede o `main` na horizontal, e a altura é a da página inteira.
    caixa = (max(0, x - 16), 0, min(im.width, x + w + 16), im.height)
    if caixa[2] - caixa[0] < 50 or caixa[3] - caixa[1] < 50:
        caixa = (0, 0, im.width, im.height)
    return im.crop(caixa)


def diferenca(a, b):
    if a is None or b is None:
        return None
    if a.size != b.size:
        return 1.0
    d = ImageChops.difference(a, b).convert("L").point(lambda v: 255 if v > 24 else 0)
    caixa = d.getbbox()
    if not caixa:
        return 0.0
    return sum(d.histogram()[255:]) / (a.width * a.height)


def gravar(im, nome):
    if im is None:
        return None
    if im.width > LARGURA:
        im = im.resize((LARGURA, round(im.height * LARGURA / im.width)), Image.LANCZOS)
    alvo = IMG / f"{nome}.jpg"
    im.save(alvo, "JPEG", quality=QUALIDADE, optimize=True, progressive=True)
    return alvo.name


ra, la, ga = ler(A)
rd, ld, gd = ler(D)


def em(g, tela, w, campo):
    return ((g.get(tela) or {}).get("w", {}).get(str(w)) or {}).get(campo)
saida = []
for tela in sorted(set(ra) | set(rd)):
    a, d = ra.get(tela), rd.get(tela)
    ia = recorte(A, a) if a else None
    id_ = recorte(D, d) if d else None
    nome = hashlib.sha1(tela.encode()).hexdigest()[:10]
    item = {
        "tela": tela,
        "identidade": (a or d)["ident"],
        "titulo": (a or d).get("titulo") or (a or d).get("title") or "",
        "diferenca": diferenca(ia, id_),
        "antes": gravar(ia, nome + "-a"),
        "depois": gravar(id_, nome + "-d"),
        "medidas": {},
    }
    for c in ("altura_1440", "cpl_max_1440", "cpl_max_1920", "transborda_375", "transborda_768",
              "metade_direita_1440", "metade_direita_1920", "nos_abaixo_do_contraste",
              "alvos_menores_que_24", "caixas", "assinaturas_de_botao", "folhas_proprias"):
        item["medidas"][c] = [(la.get(tela) or {}).get(c), (ld.get(tela) or {}).get(c)]
    for w in (375, 768):
        item["medidas"][f"altura_{w}"] = [em(ga, tela, w, "scrollH"), em(gd, tela, w, "scrollH")]
        item["medidas"][f"transbordam_{w}"] = [em(ga, tela, w, "transbordam"), em(gd, tela, w, "transbordam")]
    # O celular, só onde a página cresceu: a captura de 375 px que o instrumento já grava.
    h375 = item["medidas"]["altura_375"]
    if None not in h375 and h375[1] - h375[0] > 40:
        arq = (re.sub(r"[^a-z0-9]+", "-", tela.lower()).strip("-")[:80] or "raiz") + ".png"
        ca, cd = A / "cap" / "w375" / arq, D / "cap" / "w375" / arq
        if ca.exists() and cd.exists():
            item["antes375"] = gravar(Image.open(ca).convert("RGB"), nome + "-a375")
            item["depois375"] = gravar(Image.open(cd).convert("RGB"), nome + "-d375")
    saida.append(item)
json.dump(saida, open(SAIDA, "w"), ensure_ascii=False, indent=1)
mudaram = [s for s in saida if s["diferenca"]]
print(len(saida), "telas;", len(mudaram), "com diferença de pixel;",
      sum(1 for s in saida if s["diferenca"] is None), "sem captura num dos lados")
