"""Monta o antes e depois da migração num HTML autocontido, no modelo do piloto.

    python montar_html.py <comparacao.json> <pasta-das-imagens> <inventario.py> <saida.html> [notas.json]
"""
import base64, json, re, sys, pathlib, html

COMP, IMG, INV, SAIDA = sys.argv[1:5]
NOTAS = json.load(open(sys.argv[5])) if len(sys.argv) > 5 else {}
comp = json.load(open(COMP))
IMG = pathlib.Path(IMG)

# As regras do inventário do estudo: (regex da rota, área, arquétipo, perfil).
fonte = pathlib.Path(INV).read_text()
inicio = fonte.index("R = [")
fim = fonte.index("\n]", inicio) + 2
ns = {}
exec(fonte[inicio:fim], ns)
REGRAS = ns["R"]

FAMILIAS = {
    "Confirmação de ato": "P2.1 · Confirmação de ato",
    "Lista administrativa": "P2.2 · Lista, registro e histórico",
    "Registro e histórico": "P2.2 · Lista, registro e histórico",
    "Relatório": "P2.2 · Lista, registro e histórico",
    "Formulário de configuração": "P2.4 · Formulário de configuração",
    "Central de trabalho": "P2.5 · Central de trabalho e página de entidade",
    "Página de entidade": "P2.5 · Central de trabalho e página de entidade",
    "Operação com etapas": "P2.6 · Operação, avaliação e conferência",
    "Avaliação ou conferência": "P2.6 · Operação, avaliação e conferência",
    "Acesso": "Acesso (só tokens)",
    "Guia incorporado": "Guia incorporado (P3.5)",
}
ORDEM = list(dict.fromkeys(FAMILIAS.values())) + ["Outras telas da gestão", "Público"]
# Abaixo disto a diferença é do dado, e não da folha: a página de acesso sugere quem mais exerceu
# cada papel, e a trilha cresce com as próprias entradas do rastreio (0,02% medido em 15/11).
RUIDO = 0.001


def familia(tela):
    if not tela.startswith("/gestao"):
        return "Público", "Portal público"
    for rx, area, arq, _ in REGRAS:
        if re.search(rx, tela):
            return FAMILIAS.get(arq, "Outras telas da gestão"), area
    return "Outras telas da gestão", "—"


IMAGENS = {}


def dado(nome):
    """A chave da imagem em IMAGENS; a tela igual nos dois lados guarda uma só."""
    if not nome:
        return None
    IMAGENS.setdefault(nome, "data:image/jpeg;base64," + base64.b64encode((IMG / nome).read_bytes()).decode())
    return nome


def num(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


estados = []
for c in comp:
    fam, area = familia(c["tela"])
    m = c["medidas"]
    altura = [num(x) for x in m["altura_1440"]]
    t375 = m["transborda_375"]
    t768 = m["transborda_768"]
    quebra = []
    if t375[1] == "True" and t375[0] != "True":
        quebra.append("passou a rolar de lado a 375 px")
    if t768[1] == "True" and t768[0] != "True":
        quebra.append("passou a rolar de lado a 768 px")
    ca, cd = num(m["nos_abaixo_do_contraste"][0]), num(m["nos_abaixo_do_contraste"][1])
    if ca is not None and cd is not None and cd > ca:
        quebra.append(f"mais nós abaixo do contraste ({ca} → {cd})")
    for w in (375, 768):
        ta, td = m[f"transbordam_{w}"]
        if ta is not None and td is not None:
            novos = sorted(set(td) - set(ta))
            if novos:
                quebra.append(f"a {w} px, passam da borda: {', '.join(novos[:4])}")
    if c["antes"] is None or c["depois"] is None:
        quebra.append("sem captura num dos lados")
    nota = NOTAS.get(c["tela"], {})
    h375 = [num(x) for x in m["altura_375"]]
    if None not in h375 and h375[1] - h375[0] > 40:
        nota = {**nota, "observacoes": [f"No celular (375 px) a página cresceu {h375[1] - h375[0]} px: "
                "use o seletor de largura para ver."] + nota.get("observacoes", [])}
    quebra += nota.get("quebra", [])
    delta = (altura[1] - altura[0]) if None not in altura else None
    if c["diferenca"] is not None and 0 < c["diferenca"] < RUIDO:
        nota = {**nota, "observacoes": [f"{c['diferenca'] * 100:.2f}% dos pixels diferem, e é dado, não folha: "
                "a página sugere quem mais exerceu cada papel, e a trilha cresce com o próprio rastreio."]
                + nota.get("observacoes", [])}
    if c["diferenca"] is not None and c["diferenca"] < RUIDO:
        situacao = "igual"
    elif quebra:
        situacao = "quebrou"
    elif delta is not None and delta > 0:
        situacao = "mais alta"
    else:
        situacao = "mudou"
    estados.append({
        "tela": c["tela"], "area": area, "familia": fam, "identidade": c["identidade"],
        "situacao": situacao, "quebra": quebra, "observacoes": nota.get("observacoes", []),
        "diferenca": c["diferenca"], "antes": dado(c["antes"]),
        "depois": dado(c["antes"] if c["diferenca"] == 0 else c["depois"]),
        "antes375": dado(c.get("antes375")), "depois375": dado(c.get("depois375")),
        "medidas": {
            "altura": altura,
            "altura375": [num(x) for x in m["altura_375"]],
            "cpl1440": [num(x) for x in m["cpl_max_1440"]],
            "cpl1920": [num(x) for x in m["cpl_max_1920"]],
            "metade1440": [num(x) for x in m["metade_direita_1440"]],
            "t375": t375, "t768": t768,
            "contraste": [ca, cd],
            "alvos": [num(x) for x in m["alvos_menores_que_24"]],
            "botoes": [num(x) for x in m["assinaturas_de_botao"]],
        },
    })
estados.sort(key=lambda e: (ORDEM.index(e["familia"]), e["area"], e["tela"]))

contagem = {s: sum(1 for e in estados if e["situacao"] == s) for s in ("quebrou", "mais alta", "mudou", "igual")}
alturas = [e["medidas"]["altura"] for e in estados if None not in e["medidas"]["altura"]]
soma_a, soma_d = sum(a for a, _ in alturas), sum(d for _, d in alturas)
resumo = {
    "total": len(estados), **contagem,
    "soma_antes": soma_a, "soma_depois": soma_d,
    "mais_baixas": sum(1 for a, d in alturas if d < a),
    "mais_altas_375": sum(1 for e in estados if None not in e["medidas"]["altura375"]
                          and e["medidas"]["altura375"][1] - e["medidas"]["altura375"][0] > 40),
}
print(json.dumps(resumo, ensure_ascii=False))

modelo = pathlib.Path(__file__).with_name("modelo.html").read_text()
saida = (modelo.replace("/*ESTADOS*/[]", json.dumps(estados, ensure_ascii=False))
               .replace("/*IMAGENS*/{}", json.dumps(IMAGENS))
               .replace("/*RESUMO*/{}", json.dumps(resumo, ensure_ascii=False))
               .replace("/*ORDEM*/[]", json.dumps(ORDEM, ensure_ascii=False)))
pathlib.Path(SAIDA).write_text(saida)
print(SAIDA, round(len(saida) / 1e6, 1), "MB")
