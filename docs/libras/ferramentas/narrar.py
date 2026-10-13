"""Gera a camada comunicativa: `editais/<edital>/narrativas/` a partir de `narrativas.py`.

Confere que toda fonte citada é uma linha de cobertura do edital, e liga **toda** linha do edital a ao menos
uma intenção comunicativa — as três narrativas prototipadas ou, para as demais linhas, a intenção a que elas
pertencem —, para que a camada não perca nada da matriz de cobertura.

Uso, da raiz do repositório:  python3 docs/libras/ferramentas/narrar.py
"""

import sys
from collections import Counter, OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from corpus import EDITAIS, RAIZ, carregar, unidades_da_linha  # noqa: E402
from ids import IDS  # noqa: E402
from narrativas import TITULOS, N  # noqa: E402
from unidades import U  # noqa: E402

INTENCOES = OrderedDict(
    ato="Identificar o ato e navegar no documento",
    oportunidade="Entender a oportunidade e decidir participar",
    inscricao=TITULOS["inscricao"],
    classificacao=TITULOS["classificacao"],
    recurso=TITULOS["recurso"],
    convocacao="Responder à convocação e acompanhar mudanças",
)
PROTOTIPADAS = ("inscricao", "classificacao", "recurso")
# A intenção de uma linha que nenhuma narrativa prototipada cita, pela família da unidade.
POR_FAMILIA = dict(
    ATO="ato",
    GER="oportunidade",
    OFE="oportunidade",
    REQ="oportunidade",
    PER="oportunidade",
    CLA="classificacao",
    INS="inscricao",
    DOC="inscricao",
    AFI="classificacao",
    ETA="classificacao",
    CRO="oportunidade",
    REC="recurso",
    CON="convocacao",
    ANX="inscricao",
)
POR_UNIDADE = dict(
    ev_matriculas_homologadas="convocacao",
    ev_inicio_atividades="convocacao",
    ev_inicio_convocacoes="convocacao",
    ev_curso_formacao="convocacao",
    consolidacao="convocacao",
    matricula_documentacao="convocacao",
    certificado="oportunidade",
)

linhas, _, _, situacoes = carregar()
erros = []


def escrever(caminho, texto):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto.rstrip() + "\n", encoding="utf-8")


def celula(t):
    return t.replace("|", "\\|").replace("\n", " ")


def fontes_md(fontes):
    return ", ".join(f"[{f}](../cobertura.md)" for f in fontes) or "—"


for chave, ed in EDITAIS.items():
    por_id = {o["id"]: o for o in linhas[chave]}
    pasta = RAIZ / "editais" / ed["slug"] / "narrativas"
    citadas = {nome: set() for nome in PROTOTIPADAS}
    for nome in PROTOTIPADAS:
        n = N[chave][nome]
        fontes = (
            [f for e in n["enunciados"] for f in e["fontes"]]
            + [f for a in n["ambiguidades"] for f in a["fontes"]]
            + [f for p in n["perguntas"] for f in p["fontes"]]
        )
        for f in fontes:
            if f not in por_id:
                erros.append(f"{chave}/{nome}: fonte inexistente {f}")
        citadas[nome] = {f for f in fontes if f in por_id}

        d = [
            f"# {TITULOS[nome]} — {ed['rotulo']} {'(real)' if ed.get('real') else '(simulado)'}",
            "",
            f"> **Protótipo da camada comunicativa (rodada {3 if ed.get('real') else 2}).** Reúne, em torno de uma pergunta do candidato, o que o "
            "edital diz em várias seções. Os enunciados são **síntese documental em português**, para conferência pela "
            "área e preparação pelo profissional — não são tradução, nem roteiro de vídeo, nem substituem a tradução "
            "integral do edital. O texto exato de cada fonte está no [roteiro de produção](../roteiro-producao.md).",
            "",
            "## Pergunta do candidato",
            "",
            n["pergunta"],
            "",
            "## Destinatários",
            "",
            n["destinatarios"],
            "",
            "## Versões",
            "",
            (
                "Versão consolidada que o Cefor publicou, com as Retificações já incorporadas. Os atos de Retificação não "
                "foram lidos nesta rodada; ver [`../retificacoes.md`](../retificacoes.md)."
                if ed.get("real")
                else "Versão 1 (original). Onde uma Retificação muda o que a narrativa diz, o enunciado o registra; ver "
                "[`../retificacoes.md`](../retificacoes.md)."
            ),
            "",
            "## Enunciados normativos",
            "",
            "| ID | Modalidade | Síntese | Fontes | Pendência |",
            "|---|---|---|---|---|",
        ]
        for e in n["enunciados"]:
            pend = "**sim**" if e.get("pendencia") else "—"
            d.append(f"| {e['id']} | {e['modalidade']} | {celula(e['acao'])} | {fontes_md(e['fontes'])} | {pend} |")
        d += ["", "## Enunciados em detalhe", ""]
        variantes = OrderedDict()
        for e in n["enunciados"]:
            variantes.setdefault(e["variante"], []).append(e)
        for variante, grupo in variantes.items():
            if variante:
                d += [f"### {variante}", ""]
            for e in grupo:
                d += [f"#### {e['id']} · {e['modalidade']}", ""]
                for rotulo, valor in (
                    ("Destinatário", e["destinatario"]),
                    ("Condição", e["condicao"]),
                    ("Ação ou regra", e["acao"]),
                    ("Consequência", e["consequencia"]),
                    ("Prazo", e["prazo"]),
                    ("Alcance e exceções", e["alcance"]),
                    ("Observação", e["nota"]),
                    ("Pendência", e.get("pendencia")),
                ):
                    if valor:
                        d.append(f"- **{rotulo}:** {valor}")
                unids = sorted(
                    {k for f in e["fontes"] if f in por_id for k in unidades_da_linha(por_id[f])}, key=IDS.get
                )
                d.append(
                    f"- **Fontes:** {fontes_md(e['fontes'])} — unidades "
                    + ", ".join(f"[{IDS[k]}](../../../catalogo/unidades/{IDS[k]}.md)" for k in unids)
                )
                if e.get("atos"):
                    d.append(
                        "- **Fora da versão inventariada:** "
                        + "; ".join(e["atos"])
                        + " — ver [`../retificacoes.md`](../retificacoes.md)"
                    )
                d.append("")
        titulos = {o["texto"].split(".")[0]: o["texto"] for o in linhas[chave] if o["unidade"] == "titulo_secao"}
        secoes = OrderedDict()
        for f in sorted(citadas[nome]):
            item = por_id[f]["item"]
            numero = item.split(",")[0].split(" ›")[0].split(".")[0]
            secoes.setdefault(titulos.get(numero, numero), []).append(f"{f} ({item})")
        d += [
            "## Itens do edital mobilizados",
            "",
            f"{len(citadas[nome])} linhas de cobertura, de {len(secoes)} partes do documento:",
            "",
        ]
        d += [f"- **{s}:** " + "; ".join(v) for s, v in secoes.items()]
        d += [
            "",
            "## Ambiguidades e questões para a área responsável",
            "",
            "Não se resolvem na tradução: dependem de esclarecimento institucional ou jurídico.",
            "",
            "| Tipo | O que se observa | Fontes | Pergunta |",
            "|---|---|---|---|",
        ]
        d += [
            f"| {a['tipo']} | {celula(a['texto'])} | {fontes_md(a['fontes'])} | {celula(a['pergunta'])} |"
            for a in n["ambiguidades"]
        ]
        d += [
            "",
            "## Perguntas de verificação da compreensão",
            "",
            "Para avaliar se a pessoa surda entendeu a regra, depois de assistir à tradução. A resposta esperada é a do "
            "edital; onde ele não responde, a pergunta testa se a ausência foi comunicada sem ser preenchida. **Uma "
            "pergunta com pendência não tem gabarito fechado:** a resposta esperada é a que comunica a divergência ou a "
            "questão aberta, sem resolvê-la, e a pergunta só entra num teste depois que a área responder ou com a "
            "pendência dita ao participante.",
            "",
            "| Pergunta | Estado | Resposta esperada | Fontes | Nota |",
            "|---|---|---|---|---|",
        ]
        d += [
            f"| {celula(p['pergunta'])} | {p.get('estado', 'definitiva')}"
            + (f" — {celula(p['pendencia'])}" if p.get("pendencia") else "")
            + f" | {celula(p['resposta'])} | {fontes_md(p['fontes'])} | {celula(p['nota']) or '—'} |"
            for p in n["perguntas"]
        ]
        d += [
            "",
            "## Decisões dos profissionais de Libras",
            "",
            "Expressão, organização espacial, ordem e limites de gravação **não** são decididos aqui. Questões já "
            "identificadas:",
            "",
        ]
        d += [f"- {x}" for x in n["decisoes"]]
        r = n["reaproveitamento"]
        d += [
            "",
            "## Reaproveitamento, em três níveis",
            "",
            "Avaliação documental preliminar; cada nível é decisão do profissional e, no terceiro, da produção. Repetição "
            "textual não mede economia audiovisual.",
            "",
            f"- **Roteiro:** {r['roteiro']}",
            f"- **Solução tradutória:** {r['solucao']}",
            f"- **Gravação:** {r['gravacao']}",
        ]
        if n.get("historico"):
            d += ["", "## Histórico", ""] + [f"- {h}" for h in n["historico"]]
        escrever(pasta / f"{nome}.md", "\n".join(d))

    # Índice das narrativas do edital e mapa da cobertura.
    out = linhas[chave]
    mapa, contagem = [], Counter()
    for o in out:
        ints = [nome for nome in PROTOTIPADAS if o["id"] in citadas[nome]]
        if not ints and o["unidade"]:
            ints = [POR_UNIDADE.get(o["unidade"]) or POR_FAMILIA[U[o["unidade"]]["fam"]]]
        if not ints:
            ints = ["ato"]  # marca da simulação, que não se traduz
        for i in ints:
            contagem[i] += 1
        rotulos = "; ".join(
            f"[{INTENCOES[i]}]({i}.md)" if i in PROTOTIPADAS else f"{INTENCOES[i]} *(não prototipada)*" for i in ints
        )
        mapa.append(f"| {o['id']} | {celula(o['item'])} | {rotulos} |")
    em_alguma = sum(1 for o in out if any(o["id"] in citadas[n_] for n_ in PROTOTIPADAS))
    idx = [
        f"# Narrativas — {ed['rotulo']} {'(real)' if ed.get('real') else '(simulado)'}",
        "",
        "Protótipo da camada comunicativa: o modelo está em [`../../../camada-comunicativa.md`](../../../camada-comunicativa.md).",
        "",
        "| Narrativa | Enunciados | Linhas citadas | Ambiguidades | Perguntas |",
        "|---|---|---|---|---|",
    ]
    for nome in PROTOTIPADAS:
        n = N[chave][nome]
        idx.append(
            f"| [{TITULOS[nome]}]({nome}.md) | {len(n['enunciados'])} | {len(citadas[nome])} | {len(n['ambiguidades'])} | {len(n['perguntas'])} |"
        )
    idx += [
        "",
        "## Mapa da cobertura",
        "",
        "Três estados diferentes, que este mapa não confunde: **cobertura documental** — toda linha do edital está na "
        "[matriz](../cobertura.md), e ela é integral; **narrativa preparada** — a linha é citada por uma das três "
        f"narrativas prototipadas, **{em_alguma} das {len(out)} linhas**, em protótipo sem validação; **tradução "
        "validada** — nenhuma. As linhas que nenhuma narrativa cita têm uma intenção **atribuída pela família da "
        "unidade**, o que só diz a que situação do candidato pertencem, e não que tenham narrativa. Onde o art. 30 da "
        "LBI se aplica, as narrativas servem à preparação **dentro** da tradução completa do edital e das retificações; "
        "não a substituem.",
        "",
        "| Intenção | Linhas |",
        "|---|---|",
    ]
    idx += [
        f"| {INTENCOES[i]}{'' if i in PROTOTIPADAS else ' *(não prototipada)*'} | {contagem[i]} |"
        for i in INTENCOES
        if contagem[i]
    ]
    idx += ["", "| Linha | Item | Intenção |", "|---|---|---|", *mapa]
    escrever(pasta / "README.md", "\n".join(idx))

if erros:
    print(*erros, sep="\n")
    raise SystemExit(1)
print("ok: narrativas de", ", ".join(EDITAIS))
