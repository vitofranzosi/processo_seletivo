"""Gera o catálogo (`catalogo/`) e os pacotes por edital (`editais/*/cobertura.md`, `roteiro-producao.md`,
`oportunidades-reuso.md`) a partir dos dados desta pasta. Os demais documentos são escritos à mão.

Uso, da raiz do repositório:  python3 docs/libras/ferramentas/gerar.py
"""

import sys
from collections import Counter, OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from corpus import EDITAIS, RAIZ, avisos_de_coerencia, carregar, palavras, unidades_da_linha  # noqa: E402
from ids import IDS, V1, V3  # noqa: E402
from notas import NOTAS  # noqa: E402
from unidades import DEC_PADRAO, FAMILIAS, PADRAO, U  # noqa: E402

TABULARES = {
    "quadro_perfis",
    "matriz_vagas",
    "tabela_modalidades",
    "cronograma_tabela",
    "metodo_sorteio",
    "criterios_desempate",
    "calculo_nota",
    "etapa_decisoria",
    "etapa_pontuada",
}
# A necessidade de cada situação, nos três níveis de reaproveitamento (viabilidade.md, §6): roteiro,
# solução tradutória e gravação. Nenhuma situação documental decide o terceiro.
NECESSIDADE = {
    "INÉDITA": "Roteiro e tradução novos",
    "EXATA": "Mesmo texto já catalogado: avaliar reaproveitamento de roteiro, de solução e de gravação neste contexto",
    "PARAMETRIZÁVEL": "Mesma estrutura: roteiro reaproveitável; avaliar a solução; os valores e as condições novas pedem tradução",
    "SEMELHANTE": "Confirmar a equivalência de sentido com a área e o profissional; confirmada, avaliar reaproveitamento",
    "ESPECIALIZADA": "Tradução individual",
    "NÃO SE TRADUZ": "Nenhuma (marca da simulação)",
}
ORDEM_SIT = ["INÉDITA", "EXATA", "PARAMETRIZÁVEL", "SEMELHANTE", "ESPECIALIZADA", "NÃO SE TRADUZ"]

linhas, rodapes, ocorr, situacoes = carregar()
for aviso in avisos_de_coerencia(ocorr):
    print("AVISO:", aviso)


# ── Utilidades ──────────────────────────────────────────────────────────────────────────────────
def link(k, de="edital"):
    base = "../../catalogo/unidades/" if de == "edital" else ""
    return f"[{IDS[k]}]({base}{IDS[k]}.md)"


def celula(t):
    return t.replace("|", "\\|").replace("\n", " ")


def inicio(t, n=110):
    t = " ".join(t.split())
    return t if len(t) <= n else t[: n - 1].rstrip() + "…"


def marca(ed):
    return "(real)" if ed.get("real") else "(simulado)"


def versao(ed):
    return f"consolidada (arquivo `{ed['hash']}…`)" if ed.get("real") else f"v1 (`{ed['hash']}…`)"


def origem_da_linha(o):
    """Nos editais reais todo o texto é do documento oficial (R); as categorias A–E descrevem o sistema."""
    if not o["unidade"]:
        return "—"
    return "R" if EDITAIS[o["edital"]].get("real") else U[o["unidade"]]["ori"]


def pagina(o):
    return f"{o['pag_ini']}" if o["pag_ini"] == o["pag_fim"] else f"{o['pag_ini']}–{o['pag_fim']}"


def bloco(o):
    k = o["unidade"] or ""
    if o.get("imagem"):
        # A transcrição fiel, linha a linha; a normalização usada na comparação está na coluna da matriz.
        return "*Texto em imagem, transcrito:*\n\n```text\n" + "\n".join(o["transcricao"]) + "\n```"
    if k in TABULARES or k.startswith("ev_") or k == "rodape":
        linhas_ = [linha.rstrip() for linha in o["bruto"].splitlines()]
        recuo = min((len(x) - len(x.lstrip()) for x in linhas_ if x.strip()), default=0)
        return "```text\n" + "\n".join(x[recuo:] for x in linhas_) + "\n```"
    return "> " + " ".join(o["texto"].split())


def riscos(o):
    partes = []
    if o.get("imagem"):
        partes.append(
            f"Texto em imagem: transcrição conferida em {o['conferencia']}. Equivalência: {o['equivalencia']}"
        )
    if o.get("artefato"):
        partes.append(o["artefato"])
    jur = o.get("jur") or U.get(o["unidade"] or "", {}).get("jur")
    if jur:
        partes.append(f"Jurídico: {jur}")
    for chave, rotulo in (("dep", "Depende: "), ("nota", ""), ("vis", "Visual: ")):
        if o.get(chave):
            partes.append(f"{rotulo}{o[chave]}")
    return " ".join(partes) or "—"


def escrever(caminho, texto):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto.rstrip() + "\n", encoding="utf-8")


def campo(u, nome, padrao=None):
    valor = u.get(nome)
    return padrao if valor in (None, "", []) else valor


def lista(itens, vazio="—", recuo=""):
    if not itens:
        return f"{recuo}{vazio}" if recuo else vazio
    if isinstance(itens, str):
        return itens
    return "\n".join(f"{recuo}- {i}" for i in itens)


def variaveis(u):
    var = u.get("var") or []
    cond = [v.removeprefix("condição: ") for v in var if v.startswith("condição: ")]
    valor = [v for v in var if not v.startswith("condição: ")]
    if not var:
        return "Nenhum: texto fixo."
    partes = []
    if valor:
        partes += ["**De valor** (mudam o dado, não a regra):", "", lista(valor), ""]
    if cond:
        partes += [
            "**De condição** (mudam a regra; com valor diferente, não há reaproveitamento sem nova análise):",
            "",
            lista(cond),
        ]
    return "\n".join(partes).rstrip()


def historico(k, os_):
    u = U[k]
    if k in V1:
        primeiro = os_[0] if os_ else None
        origem = (
            f"do {EDITAIS[primeiro['edital']]['rotulo']}"
            if primeiro
            else "do documento de Retificação do Edital nº 91/2026"
            if k == "consolidacao"
            else "do corpus"
        )
        if u.get("v1_ocorrencias"):
            origem = f"do {EDITAIS[u['v1_ocorrencias'][0][:3]]['rotulo']}"
        itens = [f"2026-10-11 (rodada 1) — criada a partir {origem} (simulado)."]
    else:
        itens = []
    return itens + list(u.get("hist") or [])


# ── Unidades ────────────────────────────────────────────────────────────────────────────────────
DIST = RAIZ / "catalogo" / "unidades"


def texto_de_origem(k, os_):
    partes = []
    if k == "consolidacao":
        return [
            "Só nos documentos de Retificação. Ver o `retificacoes.md` de cada edital; o texto completo das "
            "duas ocorrências do 01/2026 está em "
            "[edital-01-2026/retificacoes.md](../../editais/edital-01-2026/retificacoes.md).",
            "",
        ]
    if k == "rodape":
        return [
            "Uma linha por página, retirada do fluxo do texto antes do inventário. Exemplo:",
            "",
            "> " + " ".join(rodapes["E91"][0][1].split()),
            "",
        ]
    distintos = OrderedDict()
    for o in os_:
        distintos.setdefault(o["comparavel"], []).append(o)
    mostrar = list(distintos.items())
    for n, (_, grupo) in enumerate(mostrar[:6], 1):
        refs = ", ".join(f"{EDITAIS[o['edital']]['curto']} {o['item']} (p. {pagina(o)})" for o in grupo[:6])
        if len(grupo) > 6:
            refs += f" e mais {len(grupo) - 6}"
        partes += [f"**Texto {n}** — {refs}" if len(mostrar) > 1 else f"**Ocorrências com este texto:** {refs}", ""]
        if k != grupo[0]["unidade"]:
            partes += ["*O trecho de origem contém também outra unidade; o texto abaixo é o trecho inteiro.*", ""]
        partes += [bloco(grupo[0]), ""]
    if len(mostrar) > 6:
        partes += [f"Mais {len(mostrar) - 6} textos distintos: ver as linhas listadas em *Referências*.", ""]
    return partes


def unidade_desdobrada(k):
    u = U[k]
    filhas = ", ".join(f"[{IDS[f]}]({IDS[f]}.md) {U[f]['t']}" for f in u["desdobrada_em"])
    v1 = ", ".join(u["v1_ocorrencias"])
    return [
        f"# {IDS[k]} — {u['t']} *(desdobrada)*",
        "",
        f"> **Desdobrada na rodada 2.** Esta unidade não recebe ocorrências novas. O identificador fica, para que "
        f"as referências da versão 1 do catálogo continuem resolvendo. Sucessoras: {filhas}.",
        "",
        "## Por que foi desdobrada",
        "",
        (lambda m: m[:1].upper() + m[1:])(u["hist"][-1].split("desdobrada: ", 1)[-1]),
        "",
        "## Ocorrências na versão 1 do catálogo",
        "",
        f"{v1}. Cada uma passou a uma das sucessoras; as linhas de cobertura são as mesmas.",
        "",
        "## Registro da versão 1",
        "",
        f"- **Família:** {u['fam']} · **Classificação na versão 1:** {u['cls']} · **Origem:** {u['ori']}",
        f"- **Finalidade:** {u['fin']}",
        f"- **Contexto:** {u['ctx']}",
        f"- **Condições de equivalência:** {u.get('eq') or '—'}",
        f"- **Impedimentos:** {u.get('imp') or '—'}",
        f"- **Fonte:** {u['fonte']}",
        "",
        "## Histórico",
        "",
        lista(historico(k, [])),
    ]


def unidade_ativa(k, os_):
    u, pad = U[k], PADRAO[U[k]["fam"]]
    p = [
        f"# {IDS[k]} — {u['t']}",
        "",
        f"> Família **{u['fam']}** ({FAMILIAS[u['fam']][0]}) · Classificação documental: **{u['cls']}** · "
        f"Origem: **{u['ori']}** · Complexidade linguística preliminar: **{u['cx']}**",
        ">",
        "> A classificação diz respeito ao potencial de reutilização **documental**. Ela não aprova reutilização "
        "audiovisual, que depende de tradução validada por profissional de Libras.",
    ]
    if u.get("origem_de"):
        pai = u["origem_de"]
        irmas = [f for f in U[pai]["desdobrada_em"] if f != k]
        p += [
            "",
            f"**Relação:** sucede, junto com {', '.join(link(f, 'unidade') for f in irmas)}, a unidade "
            f"{link(pai, 'unidade')}, desdobrada na rodada 2.",
        ]
    p += [
        "",
        "## Finalidade",
        "",
        u["fin"],
        "",
        "## Texto de origem",
        "",
        *texto_de_origem(k, os_),
        "## Referências",
        "",
    ]
    if os_:
        p += ["| Linha | Edital | Versão | Item | Pág. | Situação na rodada |", "|---|---|---|---|---|---|"]
        for o in os_:
            ed = EDITAIS[o["edital"]]
            p.append(
                f"| [{o['id']}](../../editais/{ed['slug']}/cobertura.md) | {ed['curto']} | {versao(ed)} | "
                f"{celula(o['item'])} | {pagina(o)} | {situacoes[(o['id'], k)]} |"
            )
    else:
        p.append(
            "Ocorrências nas Retificações — [91/2026](../../editais/edital-91-2026/retificacoes.md), "
            "[92/2026](../../editais/edital-92-2026/retificacoes.md) e "
            "[01/2026](../../editais/edital-01-2026/retificacoes.md) (duas)."
        )
    n_textos = len({o["comparavel"] for o in os_}) if os_ else "—"
    p += [
        "",
        f"- **Fonte no repositório:** {u['fonte']}",
        "",
        "## Contexto",
        "",
        u["ctx"],
        "",
        "## Elementos variáveis",
        "",
        variaveis(u),
        "",
        "## Dependências",
        "",
        lista(u.get("dep"), "Nenhuma identificada."),
        "",
        "## Reutilização documental",
        "",
        f"- **Classificação:** {u['cls']}",
        f"- **Ocorrências:** {len(os_) if os_ else 4} em {len({o['edital'] for o in os_}) if os_ else 3} edital(is); "
        f"{n_textos} texto(s) distinto(s)",
        f"- **Condições de equivalência:** {u.get('eq') or '—'}",
        f"- **Situações que impedem reutilização:** {u.get('imp') or '—'}",
    ]
    if u.get("jur"):
        p.append(f"- **Implicação jurídica ou contextual:** {u['jur']}")
    p += [
        "",
        "## Roteiro de produção",
        "",
        f"- **Objetivo comunicativo:** {u['fin']}",
        "- **Informações obrigatórias:**",
        "",
        lista(u.get("obr"), recuo="  "),
        "",
        f"- **Ordem lógica das informações (como no texto de origem; a tradução pode reorganizar):** {u.get('ordem') or '—'}",
        f"- **Contexto a fornecer ao tradutor:** {u['ctx']} {u.get('trad') or ''}".rstrip(),
        f"- **Elementos visuais de apoio:** {campo(u, 'vis', pad['vis'])}",
        f"- **Observações de montagem:** {campo(u, 'mont', pad['mont'])}",
        "",
        "## Tradução para Libras",
        "",
        "- Status: não produzida",
        "- Tradução validada: não disponível",
        "- Profissional responsável: não definido",
        "- Vídeo associado: não disponível",
        "",
        "## Revisão",
        "",
        "- **Pendências:**",
        "",
        lista(u.get("pend"), "Nenhuma específica além da validação profissional.", recuo="  "),
        "",
        "- **Decisões humanas necessárias:**",
        "",
        lista((u.get("dec") or []) + DEC_PADRAO, recuo="  "),
        "",
        "## Histórico",
        "",
        lista(historico(k, os_)),
    ]
    return p


for k in IDS:
    texto = unidade_desdobrada(k) if U[k].get("status") == "desdobrada" else unidade_ativa(k, ocorr.get(k, []))
    escrever(DIST / f"{IDS[k]}.md", "\n".join(texto))

# ── Índice do catálogo ──────────────────────────────────────────────────────────────────────────
ativas = [k for k in IDS if U[k].get("status") != "desdobrada"]
REAIS_RECLASSIFICADAS = [
    k for k in IDS if k not in V3 and any("rodada 3" in h and "→" in h for h in U[k].get("hist") or [])
]
desdobradas = [k for k in IDS if U[k].get("status") == "desdobrada"]
por_cls = Counter(U[k]["cls"] for k in ativas)


def contagem(k):
    if k == "consolidacao":
        return ["(1)", "(1)", "(2)"] + ["—"] * (len(EDITAIS) - 3)
    c = Counter(o["edital"] for o in ocorr.get(k, []))
    return [str(c.get(e, 0)) for e in EDITAIS]


tabela = []
for fam, (nome, desc) in FAMILIAS.items():
    tabela += [
        f"### {fam} — {nome}",
        "",
        desc,
        "",
        "| ID | Unidade | Classificação | Origem | Complex. | " + " | ".join(e[1:] for e in EDITAIS) + " |",
        "|---|---|---|---|---|" + "---|" * len(EDITAIS),
    ]
    for k in IDS:
        u = U[k]
        if u["fam"] != fam:
            continue
        if u.get("status") == "desdobrada":
            suc = ", ".join(IDS[f] for f in u["desdobrada_em"])
            tabela.append(
                f"| [{IDS[k]}](unidades/{IDS[k]}.md) | ~~{u['t']}~~ — desdobrada em {suc} | — | — | — | "
                + " | ".join("—" for _ in EDITAIS)
                + " |"
            )
        else:
            tabela.append(
                f"| [{IDS[k]}](unidades/{IDS[k]}.md) | {u['t']} | {u['cls']} | {u['ori']} | {u['cx']} | "
                + " | ".join(contagem(k))
                + " |"
            )
    tabela.append("")

INDICE = f"""# Catálogo de unidades semânticas

**Versão 3 — 2026-10-11 (rodada 3).** {len(IDS)} identificadores: **{len(ativas)} unidades ativas** e
{len(desdobradas)} desdobradas na rodada 2, a partir de três editais **simulados** (91/2026, 92/2026 e 01/2026)
e das suas quatro Retificações, e de dois editais **reais** do Cefor (28/2026 e 59/2026, na versão consolidada
que o Cefor publicou). Nenhuma unidade tem tradução produzida, validada ou vídeo associado.

> **O que mudou da versão 2 para a 3.** Entraram os dois editais reais, com os anexos que estão dentro do PDF.
> {len(V3)} unidades novas (a partir de LIB-0155) e uma família nova, **ANX** (formulários, declarações e
> termos). {len(REAIS_RECLASSIFICADAS)} unidades anteriores ganharam ocorrência real com outra redação e
> passaram a `SEMELHANTE` ou `PARAMETRIZÁVEL`, com a equivalência a confirmar — o texto do sistema e o texto do
> Cefor dizem, à primeira análise, a mesma coisa de outra maneira. Nenhuma unidade foi desdobrada nesta rodada.

> **O que mudou da versão 1 para a 2.** A rodada 1 tinha 126 unidades. A revisão crítica mostrou dois erros
> de método, e eles foram corrigidos em todo o catálogo: regras diferentes agrupadas por ocuparem a mesma
> posição no documento (12 unidades desdobradas; 3 regras embutidas em descrições de Evento ganharam unidade
> própria) e diferenças só de redação tratadas como diferença de sentido (6 unidades passaram a registrar
> equivalência a confirmar). Também foram retiradas orientações que decidiam a solução linguística para
> favorecer o reuso. Cada correção está no *Histórico* da unidade; o registro da versão 1 está em
> [`../ferramentas/referencia/catalogo-v1.json`](../ferramentas/referencia/catalogo-v1.json).

## O que é uma unidade

Uma informação ou comunicação completa o bastante para ser traduzida com sentido dentro de um contexto
documentado: uma regra, um requisito, um documento pedido, um Evento do Cronograma, uma tabela. Nem uma
palavra, nem uma seção inteira. Termos isolados não são unidades: estão em [`terminologia.md`](terminologia.md).

A unidade é **documental**: serve para controlar cobertura e rastrear origem. Ela não define o limite de um
vídeo, nem a organização da tradução — para isso existe a camada comunicativa
([`../camada-comunicativa.md`](../camada-comunicativa.md)), que reúne unidades de várias seções numa situação
do candidato.

## Quando é a mesma unidade e quando é outra

**É outra unidade** quando muda o destinatário, a modalidade normativa (obrigação, possibilidade, proibição),
a condição ou a consequência — ainda que a diferença de letra seja pequena. Ex.: experiência “no magistério”,
“no magistério superior” e “no ensino básico ou superior, ou vinculação a pós-graduação” (LIB-0139, LIB-0141,
LIB-0142).

**É a mesma unidade, `SEMELHANTE`,** quando a função e, à primeira análise, o efeito são os mesmos, e a
redação difere. A equivalência fica **a confirmar** com a área responsável pelas regras e com o profissional
de Libras. Ex.: “pela internet, no endereço do certame” e “pelo sistema de inscrições” (LIB-0031).

## Identificador

`LIB-NNNN`, atribuído na ordem de descoberta e **nunca reaproveitado nem renumerado** (os mapas estão em
[`../ferramentas/ids.py`](../ferramentas/ids.py)). Unidade desdobrada fica no catálogo, riscada, com as
ocorrências que tinha e o apontamento para as sucessoras.

## Classificação documental

| Classificação | Quer dizer | Unidades ativas |
|---|---|---|
| **EXATA** | texto e contexto equivalentes em todas as ocorrências: texto fixo do sistema, nos simulados, e cláusulas que o Cefor repete literalmente entre 28 e 59 | {por_cls["EXATA"]} |
| **PARAMETRIZÁVEL** | estrutura recorrente com variáveis; as variáveis são **de valor** (o dado) ou **de condição** (a regra) | {por_cls["PARAMETRIZÁVEL"]} |
| **SEMELHANTE** | mesma função e, provavelmente, mesmo efeito, com redação diferente; equivalência a confirmar | {por_cls["SEMELHANTE"]} |
| **INÉDITA** | uma ocorrência só no corpus (ou repetida só no mesmo edital) | {por_cls["INÉDITA"]} |
| **ESPECIALIZADA** | conteúdo próprio de cada edital, que pede tradução individual | {por_cls["ESPECIALIZADA"]} |

**A classificação é documental, não audiovisual.** Ela não diz se um roteiro, uma solução tradutória ou uma
gravação podem ser reaproveitados: são três perguntas diferentes, avaliadas em
[`../viabilidade.md`](../viabilidade.md), §6.

**Situação na rodada** (nas matrizes de cobertura) é a relação de cada ocorrência com o catálogo no momento
em que foi processada, na ordem 91 → 92 → 01 → 28 → 59: `INÉDITA` se a unidade nasce ali; `EXATA` se o texto é igual
ao de uma ocorrência anterior (numeração de item e alínea não contam); nos demais casos, a classificação da
unidade.

## Origem

Conforme a auditoria do PDF de 08/10/2026, §3.2: **A** gerada automaticamente · **B** campo estruturado ·
**C** frase escrita pelo sistema a partir de regra · **D** redação livre do gestor · **E** outra entidade.
Nas unidades criadas a partir dos editais reais, a origem é **D**: texto do documento oficial, escrito fora do
sistema. Nas matrizes de cobertura dos editais reais, toda linha tem origem **R** (documento real).

## Complexidade linguística preliminar

`baixa`, `média` ou `alta`: estimativa **documental** do esforço de tradução, para escolher o piloto. Não é
avaliação linguística, e deve ser revista pelo profissional.

## Famílias e unidades

Colunas 91, 92 e 01: ocorrências em cada edital simulado (versão original); 28 e 59: nos editais reais (versão
consolidada). Para a marca de consolidação, entre parênteses, o número de Retificações em que aparece.

{chr(10).join(tabela)}
## Variantes previstas no código e não observadas

O compositor pode escrever frases que o corpus não exercitou. Não viraram unidade, mas uma rodada futura
que as encontre sabe de onde vêm (`backend/processo_seletivo/publicacoes/infrastructure/pdf.py`,
`publicacoes/domain/vocabulario_da_regra.py`).

| Variante | Par de | Fonte |
|---|---|---|
| “Não caberá recurso contra o resultado de …” — **negativa expressa** | LIB-0028 | `_janela_recursal` |
| “Caberá recurso no prazo de …, contados da divulgação do resultado.” (marco sem nome) | LIB-0028 | `_janela_recursal` |
| “participam apenas as inscrições habilitadas na Etapa …” | LIB-0027 | `_habilitacao_ao_sorteio` |
| “Método: próprio deste marco” / “— diverge do comum deste Edital” / “o comum a este Edital, descrito no item N.” | LIB-0026 | `_origem_do_metodo`, `_marcos` |
| “média ponderada”, “pela soma dos pesos”, “meio para par”, “truncamento”, “sem casas decimais”, “(não pontua)” | LIB-0091 | `_combinacao`, `_arredondamento` |
| “Progride … o 1 (um) primeiro” | LIB-0092 | `_regra_de_corte` |
| “Cada candidato poderá ter no máximo N inscrições enviadas neste Edital.” | LIB-0034 | `teto_de_inscricoes` |
| “O Requerimento de Matrícula será enviado quando o candidato for convocado.” | LIB-0064 | `MOMENTO_DO_REQUERIMENTO` |
| “Dos candidatos ao perfil X concorrentes na modalidade Y:” | LIB-0101, LIB-0041 | `_titulo_do_grupo` |
| “No Perfil X, …” / “Nos Perfis X e Y, …” antes de reversão e convocação | LIB-0015, LIB-0078, LIB-0017, LIB-0079 | `_frases_consolidadas` |
| “maior pontuação na Etapa …” com “sem o valor, o critério não se aplica” | LIB-0094 | `vocabulario_da_regra.py` |

Duas seções do catálogo nunca saíram no corpus — Do Acesso ao Curso e Da Homologação da Matrícula. Os
títulos ficam cobertos por LIB-0005; o conteúdo, que é texto livre, pedirá unidades novas.

## Arquivos

- [`terminologia.md`](terminologia.md) — termos que pedem decisão de sinal antes de qualquer gravação.
- [`unidades/`](unidades/) — um arquivo por identificador, inclusive os desdobrados.
"""
escrever(RAIZ / "catalogo" / "indice.md", INDICE)

# ── Pacotes por edital ──────────────────────────────────────────────────────────────────────────
for chave, ed in EDITAIS.items():
    out, pasta = linhas[chave], RAIZ / "editais" / ed["slug"]
    total = sum(palavras(o["texto"]) for o in out if o["unidade"] != "rodape")
    sit, sit_pal = Counter(o["situacao"] for o in out), Counter()
    for o in out:
        if o["unidade"] != "rodape":
            sit_pal[o["situacao"]] += palavras(o["texto"])
    novas = sorted({k for o in out for k in unidades_da_linha(o) if situacoes[(o["id"], k)] == "INÉDITA"}, key=IDS.get)
    distintas = {k for o in out for k in unidades_da_linha(o)}

    c = [
        f"# Cobertura — {ed['rotulo']} {marca(ed)}",
        "",
        (
            f"Mapa integral do documento oficial, na versão consolidada que o Cefor publicou (arquivo `{ed['hash']}…`, "
            "SHA-256 do PDF). O texto que o PDF só tem em imagem — o cabeçalho institucional — entra transcrito, em linha "
            "marcada. Cada linha"
            if ed.get("real")
            else f"Mapa integral do documento publicado (versão 1, conteúdo `{ed['hash']}…`). Cada linha"
        )
        + " é um trecho consecutivo "
        "do texto do PDF; juntas, elas reproduzem o documento inteiro, sem sobra e sem lacuna (conferido mecanicamente — "
        "ver [`../../README.md`](../../README.md), *Como a cobertura foi construída*). O texto integral de cada trecho está "
        "no [roteiro de produção](roteiro-producao.md).",
        "",
        "**A matriz é controle de cobertura, não plano de vídeo.** Uma linha não corresponde a um vídeo; as "
        "[narrativas](narrativas/) reúnem linhas de várias seções em situações do candidato.",
        "",
        "**Situação no catálogo** é a da rodada, na ordem 91 → 92 → 01 → 28 → 59: `INÉDITA` quando a unidade aparece pela primeira "
        "vez; `EXATA` quando o texto é igual ao de uma ocorrência já catalogada (numeração de item e alínea não contam); "
        "nos demais casos, a classificação da unidade. Quando a linha tem mais de uma unidade (regra embutida noutra), "
        "a situação é a da primeira. **Necessidade** é a consequência documental, e não decisão de produção.",
        "",
        "## Resumo",
        "",
        f"- Linhas de cobertura: **{len(out)}** "
        + (
            f"(inclui uma linha para os {len(rodapes[chave])} rodapés)"
            if rodapes[chave]
            else f"(inclui {sum(1 for o in out if o.get('imagem'))} de texto em imagem, transcrito; o documento não tem rodapé textual)"
        ),
        f"- Palavras (sem rodapé): **{total}**",
        f"- Unidades distintas usadas: **{len(distintas)}**; novas no catálogo nesta rodada: **{len(novas)}**",
        "",
        "| Situação | Linhas | Palavras | % das palavras |",
        "|---|---|---|---|",
    ]
    for s in ORDEM_SIT:
        if sit.get(s):
            c.append(f"| {s} | {sit[s]} | {sit_pal.get(s, 0)} | {100 * sit_pal.get(s, 0) / total:.0f}% |")
    c += [
        "",
        "## Matriz",
        "",
        "| Linha | Item | Pág. | Conteúdo a traduzir (início) | Pal. | Origem | Unidade | Situação | Necessidade | Pendências e riscos |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for o in out:
        uns = " + ".join(link(k) for k in unidades_da_linha(o)) or "—"
        c.append(
            f"| {o['id']} | {celula(o['item'])} | {pagina(o)} | {celula(inicio(o['texto']))} | {palavras(o['texto'])} | "
            f"{origem_da_linha(o)} | {uns} | {o['situacao']} | {NECESSIDADE[o['situacao']]} | {celula(riscos(o))} |"
        )
    c += [
        "",
        "Origem: **A** gerada · **B** campo estruturado · **C** frase do sistema · **D** redação livre · "
        "**E** outra entidade (auditoria do PDF de 08/10/2026, §3.2) · **R** documento real, escrito fora do sistema.",
    ]
    escrever(pasta / "cobertura.md", "\n".join(c))

    r = [
        f"# Roteiro de produção — {ed['rotulo']} {marca(ed)}",
        "",
        "Documento de trabalho para a equipe de tradução e interpretação em Libras e para a produção audiovisual, "
        "**na sequência do edital**. Para cada trecho: finalidade, texto de origem, contexto, o que não pode ser omitido, "
        "unidade do catálogo, necessidade e observações.",
        "",
        "> **O que este roteiro não é.** Não é tradução, nem glosa, nem sequência de sinais, nem plano de vídeos. Segue a "
        "ordem do documento em português para que nada se perca; a organização da tradução — o que se agrupa, em que "
        "ordem, com que limites — é do profissional, e as [narrativas](narrativas/) propõem agrupamentos por situação do "
        "candidato. Nenhuma unidade tem vídeo aprovado.",
        "",
        (
            "> **Documento oficial.** O texto é o do PDF publicado pelo Cefor, transcrito sem correção. Erros, remissões "
            "quebradas e contradições do original estão anotados nos trechos e no [manifesto](manifesto.md); resolvê-los é "
            "da área responsável, não da tradução."
            if ed.get("real")
            else "> **Marcas da simulação.** “(DEMONSTRAÇÃO)”, “[DOCUMENTO DE DEMONSTRAÇÃO …]”, “(fictícia)” e “endereço "
            "fictício de demonstração” estão registrados, mas não se traduzem."
        ),
        "",
        "Trechos que repetem, no mesmo edital, o texto de outro trecho da mesma unidade aparecem em forma curta, com "
        "remissão ao primeiro.",
        "",
    ]
    anteriores, secao_aberta = {}, False
    for o in out:
        k = o["unidade"]
        if k == "titulo_secao":
            r += [f"## {o['texto']}", ""]
            secao_aberta = True
        elif not secao_aberta and o["id"].endswith("-001"):
            r += ["## Abertura do ato", ""]
        elif k == "fecho":
            r += ["## Fecho do ato", ""]
        chave_rep = (k, o["comparavel"])
        if k and k != "titulo_secao" and chave_rep in anteriores:
            r += [
                f"**{o['id']} · {o['item']}** (p. {pagina(o)}) — repete {anteriores[chave_rep]} ({link(k)}), mesmo texto. "
                "Mesma finalidade, contexto e necessidade; ver o primeiro.",
                "",
            ]
            continue
        if k:
            anteriores[chave_rep] = o["id"]
        r += [f"### {o['id']} · {o['item']} (p. {pagina(o)})", ""]
        if not k:
            r += [bloco(o), "", f"- **Tratamento:** {o.get('artefato')}", ""]
            continue
        u, pad = U[k], PADRAO[U[k]["fam"]]
        r += [f"- **Finalidade comunicativa:** {u['fin']}", "", "**Texto de origem**", "", bloco(o), ""]
        ctx = (
            u["ctx"]
            + (f" Neste edital: {o['dep']}" if o.get("dep") else "")
            + (f" Observação: {o['nota']}" if o.get("nota") else "")
        )
        r += [
            f"- **Contexto necessário:** {ctx}",
            f"- **Não pode ser omitido:** {'; '.join(u.get('obr') or []) or '—'}",
            f"- **Unidade do catálogo:** {link(k)} — {u['t']} · situação **{o['situacao']}**",
            f"- **Necessidade:** {NECESSIDADE[o['situacao']]}",
            f"- **Elementos gráficos possíveis:** {o.get('vis') or campo(u, 'vis', pad['vis'])}",
            f"- **Observações de composição:** {campo(u, 'mont', pad['mont'])}",
        ]
        for x in o.get("extras") or []:
            ux = U[x]
            r += [
                f"- **Este trecho contém também outra regra:** {link(x)} — {ux['t']} · situação "
                f"**{situacoes[(o['id'], x)]}**. {ux['fin']} Não pode ser omitido: {'; '.join(ux.get('obr') or [])}."
            ]
        jur = o.get("jur") or u.get("jur")
        if jur:
            r.append(f"- **Atenção jurídica:** {jur}")
        r.append("")
    escrever(pasta / "roteiro-producao.md", "\n".join(r))

    # oportunidades-reuso.md
    ordem_ed = list(EDITAIS)
    anteriores_ed = ordem_ed[: ordem_ed.index(chave)]
    n = NOTAS[chave]
    usadas = OrderedDict()
    for o in out:
        for k in unidades_da_linha(o):
            if k != "rodape":
                usadas.setdefault(k, []).append(o)
    rec, novas_, variacoes, internas = [], [], [], []
    for k, os_ in usadas.items():
        antes = [x for e in anteriores_ed for x in linhas[e] if k in unidades_da_linha(x)]
        if antes:
            iguais = any(x["comparavel"] == o["comparavel"] for o in os_ for x in antes)
            rec.append(
                (
                    k,
                    sorted({EDITAIS[x["edital"]]["curto"] for x in antes}),
                    "texto idêntico" if iguais else "mesma função, texto diferente",
                )
            )
            if not iguais:
                variacoes.append((k, os_[0], antes[0]))
        else:
            novas_.append((k, os_[0]))
        rep = sum(c_ for c_ in Counter(o["comparavel"] for o in os_).values() if c_ > 1)
        if rep:
            internas.append((k, rep, len(os_)))
    d = [
        f"# Oportunidades de reutilização — {ed['rotulo']} {marca(ed)}",
        "",
        n["abertura"],
        "",
        "> Uma unidade documental repetida **não** é um vídeo disponível, e texto repetido não mede economia. "
        "“Reutilizável” aqui quer dizer candidata a três análises diferentes — de roteiro, de solução tradutória e de "
        "gravação ([`../../viabilidade.md`](../../viabilidade.md), §6) —, todas do profissional de Libras.",
        "",
        "## Unidades recorrentes",
        "",
    ]
    if rec:
        d += [
            f"{len(rec)} das {len(usadas)} unidades deste edital já estavam no catálogo.",
            "",
            "| Unidade | Já vista em | Relação com a ocorrência anterior |",
            "|---|---|---|",
        ]
        d += [f"| {link(k)} {U[k]['t']} | {', '.join(e)} | {rel} |" for k, e, rel in rec]
    else:
        d.append("Nenhuma: é o primeiro edital da rodada.")
    d += [
        "",
        "## Unidades novas",
        "",
        f"{len(novas_)} unidades entraram no catálogo a partir deste edital.",
        "",
        "| Unidade | Classificação após a rodada | Primeira linha |",
        "|---|---|---|",
    ]
    d += [f"| {link(k)} {U[k]['t']} | {U[k]['cls']} | {o['id']} ({celula(o['item'])}) |" for k, o in novas_]
    d += ["", "## Variações encontradas", ""]
    if variacoes:
        d += [
            "Mesma unidade, texto diferente do já catalogado. Numa unidade `PARAMETRIZÁVEL`, a diferença é de valor ou "
            "de condição (a unidade diz qual variável é qual); numa `SEMELHANTE`, a equivalência de sentido está a confirmar.",
            "",
            "| Unidade | Classificação | Texto anterior (início) | Texto neste edital (início) |",
            "|---|---|---|---|",
        ]
        d += [
            f"| {link(k)} | {U[k]['cls']} | {celula(inicio(x['texto'], 80))} ({x['id']}) | {celula(inicio(o['texto'], 80))} ({o['id']}) |"
            for k, o, x in variacoes
        ]
    else:
        d.append("Não se aplica ao primeiro edital da rodada.")
    d += ["", "## Repetições dentro do edital", ""]
    if internas:
        d += [
            "Ocorrências com texto idêntico a outra ocorrência **do mesmo edital** (numeração de item e alínea não contam).",
            "",
            "| Unidade | Ocorrências com texto repetido | Ocorrências no edital |",
            "|---|---|---|",
        ]
        d += [f"| {link(k)} {U[k]['t']} | {rep} | {tot} |" for k, rep, tot in internas]
    else:
        d.append("Nenhuma.")
    d += ["", "## Blocos que exigem adaptação", ""] + [f"- {x}" for x in n["adaptar"]]
    d += ["", "## Condições que inviabilizam a reutilização", ""] + [f"- {x}" for x in n["inviabiliza"]]
    d += ["", "## Oportunidades futuras de gravação padronizada", ""] + [f"- {x}" for x in n["padronizar"]]
    d += [
        "",
        "## Possíveis equivalências a validar",
        "",
        "Nenhuma equivalência é declarada aqui. As candidatas são as linhas “texto idêntico” da tabela de recorrentes e "
        "as unidades `SEMELHANTE`, cuja equivalência a área e o profissional precisam confirmar; as “mesma função, texto "
        "diferente” de unidades `PARAMETRIZÁVEL` pedem atenção às variáveis de condição.",
    ]
    escrever(pasta / "oportunidades-reuso.md", "\n".join(d))

print(
    f"ok: {len(IDS)} identificadores, {len(ativas)} ativas, {len(desdobradas)} desdobradas; "
    + ", ".join(f"{e}: {len(linhas[e])} linhas" for e in EDITAIS)
)
