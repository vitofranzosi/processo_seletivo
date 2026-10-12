"""Carrega o corpus e calcula as ocorrências: o núcleo comum de gerar.py, medir.py e narrar.py.

Entradas, todas no repositório: os PDFs em `docs/libras/editais/<edital>/fonte/` e os dados desta pasta
(`linhas.py`, `unidades.py`, `ids.py`). Dependência externa: `pdftotext` (poppler), via `fatiar.py`.
"""

import re
from collections import OrderedDict, defaultdict
from pathlib import Path

from fatiar import fatiar
from ids import IDS
from linhas import E01, E28, E59, E91, E92, IMAGENS
from unidades import U

RAIZ = Path(__file__).resolve().parent.parent  # docs/libras

EDITAIS = OrderedDict(
    E91=dict(slug="edital-91-2026", rotulo="Edital nº 91/2026", curto="91/2026", linhas=E91, hash="083468eb97dfa584"),
    E92=dict(slug="edital-92-2026", rotulo="Edital nº 92/2026", curto="92/2026", linhas=E92, hash="34bc1a9f9a9f3de8"),
    E01=dict(slug="edital-01-2026", rotulo="Edital nº 01/2026", curto="01/2026", linhas=E01, hash="c29f09d938a87806"),
    # Rodada 3: editais REAIS, na versão consolidada que o Cefor publicou. Não saem do sistema: o hash é o
    # SHA-256 do arquivo (16 primeiros dígitos), e não o do conteúdo canônico.
    E28=dict(
        slug="edital-28-2026",
        rotulo="Edital nº 28/2026",
        curto="28/2026",
        linhas=E28,
        real=True,
        pdf="edital-retificado-em-2026-08-24.pdf",
        hash="ff9e7d3ccadc7e28",
    ),
    E59=dict(
        slug="edital-59-2026",
        rotulo="Edital nº 59/2026",
        curto="59/2026",
        linhas=E59,
        real=True,
        pdf="edital-retificado-em-2026-07-30.pdf",
        hash="dbe990a0838f597d",
    ),
)
SIMULADOS = [k for k, ed in EDITAIS.items() if not ed.get("real")]
REAIS = [k for k, ed in EDITAIS.items() if ed.get("real")]


def pdf_original(chave):
    return RAIZ / "editais" / EDITAIS[chave]["slug"] / "fonte" / EDITAIS[chave].get("pdf", "pub1.pdf")


def comparavel(texto):
    """O texto de comparação: sem enumerador inicial (item, alínea, marcador) e com espaços normalizados."""
    t = re.sub(r"^(\d+(\.\d+)*\.?|[a-z]\)|•)\s+", "", texto.strip())
    return " ".join(t.split())


def palavras(t):
    return len(t.split())


def unidades_da_linha(o):
    return ([o["unidade"]] if o["unidade"] else []) + list(o.get("extras") or [])


def linha_de_imagem(im):
    return dict(
        im,
        texto=" ".join(" ".join(im["transcricao"]).split()),
        bruto="\n".join(im["transcricao"]),
        pag_ini=im["pag"],
        pag_fim=im["pag"],
        ancora="",
        imagem=True,
    )


def carregar():
    """Fatia os editais, confere identificadores e calcula a situação de cada ocorrência."""
    linhas, rodapes = OrderedDict(), {}
    for chave, ed in EDITAIS.items():
        out, rod = fatiar(str(pdf_original(chave)), ed["linhas"])
        # Texto que o PDF só tem em imagem não sai do pdftotext: entra transcrito (linhas.py, IMAGENS). O `texto` e o
        # `comparavel` saem da normalização comum a todas as linhas; a transcrição fiel fica em `bruto`.
        frente = [linha_de_imagem(im) for im in IMAGENS.get(chave, []) if im["depois_de"] == 0]
        out = frente + out
        for i, o in enumerate(out, 1):
            o.update(id=f"{chave}-{i:03d}", edital=chave, comparavel=comparavel(o["texto"]))
        for im in sorted((im for im in IMAGENS.get(chave, []) if im["depois_de"]), key=lambda im: -im["depois_de"]):
            o = linha_de_imagem(im)
            o.update(id=f"{chave}-{im['depois_de']:03d}a", edital=chave, comparavel=comparavel(o["texto"]))
            out.insert(im["depois_de"], o)
        # O rodapé sai do fluxo antes do corte e entra como linha própria, no fim. Os editais reais não o têm.
        if rod:
            out.append(
                dict(
                    id=f"{chave}-{sum(not o['id'].endswith('a') for o in out) + 1:03d}",
                    edital=chave,
                    item="Rodapé (todas as páginas)",
                    unidade="rodape",
                    texto=" | ".join(r[1] for r in rod),
                    bruto="\n".join(r[1] for r in rod),
                    pag_ini=1,
                    pag_fim=rod[-1][0],
                    comparavel=f"rodapé {chave} {len(rod)} páginas",
                    ancora="",
                )
            )
        linhas[chave], rodapes[chave] = out, rod

    usadas = {k for out in linhas.values() for o in out for k in unidades_da_linha(o)}
    assert usadas <= set(U), sorted(usadas - set(U))
    assert set(U) <= set(IDS), sorted(set(U) - set(IDS))
    desdobradas = {k for k, u in U.items() if u.get("status") == "desdobrada"}
    assert not (usadas & desdobradas), sorted(usadas & desdobradas)

    # A situação é relativa ao catálogo no momento em que a ocorrência é processada: 91 → 92 → 01 → 28 → 59.
    vistos = defaultdict(list)
    situacoes = {}
    for chave in EDITAIS:
        for o in linhas[chave]:
            for k in unidades_da_linha(o):
                if not vistos[k]:
                    s = "INÉDITA"
                elif o["comparavel"] in vistos[k]:
                    s = "EXATA"
                else:
                    cls = U[k]["cls"]
                    s = cls if cls in ("PARAMETRIZÁVEL", "SEMELHANTE", "ESPECIALIZADA") else "SEMELHANTE"
                situacoes[(o["id"], k)] = s
                vistos[k].append(o["comparavel"])
            o["situacao"] = situacoes[(o["id"], o["unidade"])] if o["unidade"] else "NÃO SE TRADUZ"

    ocorr = defaultdict(list)
    for chave in EDITAIS:
        for o in linhas[chave]:
            for k in unidades_da_linha(o):
                ocorr[k].append(o)
    return linhas, rodapes, ocorr, situacoes


def avisos_de_coerencia(ocorr):
    """O que o corpus mostra contra a classificação declarada da unidade."""
    avisos = []
    for k, os_ in ocorr.items():
        cls, textos = U[k]["cls"], {o["comparavel"] for o in os_}
        if cls in ("INÉDITA", "EXATA") and len(textos) > 1:
            avisos.append(f"{k} ({cls}) com {len(textos)} textos")
        if cls == "SEMELHANTE" and len(textos) < 2:
            avisos.append(f"{k} SEMELHANTE com um texto só")
    return avisos
