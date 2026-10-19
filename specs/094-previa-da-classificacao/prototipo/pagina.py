"""O HTML do protótipo da 094: a etapa Classificação simplificada, o cartão do marco e o painel.

Tudo demonstrativo, e escrito para a CSP do produto: nenhum `style=`, nenhum `<script>` inline,
nenhum `on*=`. O htmx é o do produto (`interface/htmx.min.js`, 2.0.4), com a mesma configuração do
`base.html` da gestão — sem estilo de indicador injetado e sem `eval`.

Os nomes dos campos do cartão são os do `_marco.html` (`marco-<perfil>-<n>-…`,
`criterio-<perfil>-<n>-<k>-…`): na implementação, quem lê é `marco_do_formulario`, e o protótipo
lê com um leitor próprio (`ler_marco`) só porque roda sem Django.
"""

from __future__ import annotations

import datetime
from decimal import Decimal
from html import escape

import previa

from processo_seletivo.classificacao.domain import faixa

P = "marco-0-0"


# ---------------------------------------------------------------------------------------------
# A leitura do formulário (demonstrativa: no produto, `forms.marco_do_formulario`)
# ---------------------------------------------------------------------------------------------


def _um(dados, nome, padrao=""):
    return (dados.get(nome) or [padrao])[0].strip()


def _inteiro(dados, nome):
    bruto = _um(dados, nome)
    try:
        return int(bruto)
    except ValueError:
        return None


def ler_marco(dados):
    criterios = []
    for k in range(3):
        base = f"criterio-0-0-{k}"
        tipo = _um(dados, f"{base}-type")
        if not tipo:
            continue
        alvo = _um(dados, f"{base}-target")
        chave = "stageId" if tipo == "MAIOR_PONTUACAO_NA_ETAPA" else "factId"
        parametros = {chave: alvo} if alvo else {}
        criterios.append(
            {
                "order": _inteiro(dados, f"{base}-order") or k + 1,
                "type": tipo,
                "parameters": parametros,
                "whenMissing": _um(dados, f"{base}-whenMissing"),
            }
        )
    especie = _um(dados, f"{P}-cutTargetKind")
    regra = None
    if especie:
        regra = {
            "targetKind": especie,
            "targetCount": _inteiro(dados, f"{P}-cutTargetCount")
            if especie == faixa.ALVO_FIXO
            else None,
            "surplusCount": _inteiro(dados, f"{P}-cutSurplusCount") or 0,
            "tieOutcome": _um(dados, f"{P}-cutTieOutcome"),
            "governedStage": _um(dados, f"{P}-cutGovernedStage"),
            "continuation": _um(dados, f"{P}-cutContinuation"),
        }
    return {
        "code": "CLASS-FINAL",
        "name": "Classificação para a Entrevista",
        "orderProduction": "POR_PONTUACAO",
        "stages": [s for s in dados.get(f"{P}-stages", []) if s],
        "operation": _um(dados, f"{P}-operation", "SOMA_PONDERADA"),
        "normalization": _um(dados, f"{P}-normalization", "NENHUMA"),
        "rounding": {"scale": _inteiro(dados, f"{P}-scale"), "mode": _um(dados, f"{P}-mode")},
        "tiebreakers": criterios,
        "cutRule": regra,
    }


def ler_etapas(dados):
    etapas = []
    for etapa in previa.ETAPAS:
        peso = _um(dados, f"etapa-{etapa['id']}-weight", etapa["weight"] or "")
        etapas.append({**etapa, "weight": peso or None})
    return etapas


def ler_vagas(dados):
    bruto = _um(dados, "quadro-vagas", "10")
    return int(bruto) if bruto.isdigit() else None


# ---------------------------------------------------------------------------------------------
# A configuração inicial e os exemplos do achado (só do protótipo)
# ---------------------------------------------------------------------------------------------

PADRAO = {
    f"{P}-stages": ["e-escrita", "e-titulos"],
    f"{P}-operation": ["SOMA_PONDERADA"],
    f"{P}-normalization": ["NENHUMA"],
    f"{P}-scale": ["2"],
    f"{P}-mode": ["MEIO_PARA_CIMA"],
    "criterio-0-0-0-type": ["MAIOR_PONTUACAO_NA_ETAPA"],
    "criterio-0-0-0-target": ["e-escrita"],
    "criterio-0-0-0-whenMissing": ["ULTIMO_NO_CRITERIO"],
    "criterio-0-0-1-type": ["MENOR_VALOR_DE_FATO"],
    "criterio-0-0-1-target": ["f-nascimento"],
    "criterio-0-0-1-whenMissing": ["ULTIMO_NO_CRITERIO"],
    "criterio-0-0-2-type": ["MAIOR_VALOR_DE_FATO"],
    "criterio-0-0-2-target": ["f-servico"],
    "criterio-0-0-2-whenMissing": ["ULTIMO_NO_CRITERIO"],
    f"{P}-cutTargetKind": ["FIXED"],
    f"{P}-cutTargetCount": ["10"],
    f"{P}-cutSurplusCount": ["5"],
    f"{P}-cutTieOutcome": ["ADMITS_SURPLUS"],
    f"{P}-cutGovernedStage": ["e-entrevista"],
    f"{P}-cutContinuation": ["ALLOWED"],
    "quadro-vagas": ["10"],
}

EXEMPLOS = {
    "achado-1": (
        "Achado, linha 1: 10 + 5, empate na 10ª",
        {f"{P}-cutSurplusCount": ["5"], "cenario": ["empate_nas_vagas"]},
    ),
    "achado-2": (
        "Achado, linha 2: 10 + 5, empate na 15ª, STRICT",
        {
            f"{P}-cutSurplusCount": ["5"],
            f"{P}-cutTieOutcome": ["STRICT"],
            "cenario": ["empate_na_faixa"],
        },
    ),
    "achado-3": (
        "Achado, linha 3: 10 sem suplentes, empate na 10ª",
        {f"{P}-cutSurplusCount": ["0"], "cenario": ["empate_nas_vagas"]},
    ),
    "sem-desfecho": (
        "Desfecho não declarado",
        {f"{P}-cutTieOutcome": [""], "cenario": ["empate_na_faixa"]},
    ),
}


def configuracao(exemplo):
    dados = {chave: list(valor) for chave, valor in PADRAO.items()}
    if exemplo in EXEMPLOS:
        dados.update(EXEMPLOS[exemplo][1])
    return dados


# ---------------------------------------------------------------------------------------------
# Formatação
# ---------------------------------------------------------------------------------------------


def numero(valor, escala=2):
    if valor is None:
        return "—"
    if isinstance(valor, datetime.date):
        return valor.strftime("%d/%m/%Y")
    if isinstance(valor, int):
        return str(valor)
    texto = f"{Decimal(valor):,.{escala}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def ordinal(n):
    return f"{n}ª"


def _opcao(valor, rotulo, atual):
    marcado = " selected" if valor == atual else ""
    return f'<option value="{escape(valor)}"{marcado}>{escape(rotulo)}</option>'


def _select(nome, opcoes, atual, rotulo, *, obrigatorio=False):
    corpo = "".join(_opcao(v, r, atual) for v, r in opcoes)
    marca = ' <span class="obrigatorio" aria-hidden="true">*</span>' if obrigatorio else ""
    return (
        f'<p class="campo"><label for="{nome}">{escape(rotulo)}{marca}</label>'
        f'<select id="{nome}" name="{nome}">{corpo}</select></p>'
    )


def _input(nome, valor, rotulo, *, tipo="number", classe="campo curto"):
    return (
        f'<p class="{classe}"><label for="{nome}">{escape(rotulo)}</label>'
        f'<input type="{tipo}" id="{nome}" name="{nome}" value="{escape(valor)}" min="0"></p>'
    )


# ---------------------------------------------------------------------------------------------
# A página
# ---------------------------------------------------------------------------------------------


def pagina(dados, exemplo):
    um = lambda nome: _um(dados, nome)  # noqa: E731
    etapas = ler_etapas(dados)
    com_nota = [e for e in etapas if e["forma"] != previa.DECISORIA]
    escolhidas = set(dados.get(f"{P}-stages", []))
    exemplos = "".join(
        f'<li><a href="/?exemplo={chave}"{' aria-current="page"' if chave == exemplo else ""}>'
        f"{escape(rotulo)}</a></li>"
        for chave, (rotulo, _) in EXEMPLOS.items()
    )
    pesos = "".join(
        f'<li><label for="etapa-{e["id"]}-weight">{escape(e["name"])}</label> '
        + (
            f'<input type="number" step="0.5" min="0" id="etapa-{e["id"]}-weight" '
            f'name="etapa-{e["id"]}-weight" value="{escape(e["weight"] or "")}">'
            if e["forma"] != previa.DECISORIA
            else '<span class="porta">decisória, sem peso</span>'
        )
        + "</li>"
        for e in etapas
    )
    etapas_do_marco = "".join(
        f'<label class="escolha"><input type="checkbox" name="{P}-stages" value="{e["id"]}"'
        f"{' checked' if e['id'] in escolhidas else ''}> {escape(e['name'])}</label>"
        for e in etapas
    )
    alvos = [(e["id"], f"Pontuação na {e['name']}") for e in com_nota] + [
        (f["id"], f["name"]) for f in previa.FATOS
    ]
    criterios = ""
    for k in range(3):
        base = f"criterio-0-0-{k}"
        criterios += (
            f'<fieldset class="linha criterio"><legend>{k + 1}º critério de desempate</legend>'
            f'<input type="hidden" name="{base}-order" value="{k + 1}"><div class="campos">'
            + _select(
                f"{base}-type",
                [
                    ("", "Nenhum"),
                    ("MAIOR_PONTUACAO_NA_ETAPA", "Maior pontuação numa Etapa"),
                    ("MAIOR_VALOR_DE_FATO", "Maior valor de um fato declarado"),
                    ("MENOR_VALOR_DE_FATO", "Menor valor de um fato declarado"),
                ],
                um(f"{base}-type"),
                "Critério",
            )
            + _select(f"{base}-target", [("", "—"), *alvos], um(f"{base}-target"), "O que compara")
            + _select(
                f"{base}-whenMissing",
                [
                    ("", "Não declarado"),
                    ("ULTIMO_NO_CRITERIO", "Fica por último neste critério"),
                    ("CRITERIO_NAO_SE_APLICA", "O critério não se aplica"),
                ],
                um(f"{base}-whenMissing"),
                "Quando o valor não existe",
            )
            + "</div></fieldset>"
        )
    governaveis = [("", "Escolha a Etapa"), ("NONE", "Não governa Etapa alguma")] + [
        (e["id"], e["name"]) for e in etapas
    ]
    cartao = (
        f'<fieldset class="linha marco" id="{P}"><legend>Marco classificatório</legend>'
        '<div class="campos"><p class="campo largo"><span class="rotulo">Como a ordem deste marco '
        "é produzida</span> <strong>Pela pontuação combinada das Etapas</strong></p>"
        '<p class="campo largo"><span class="rotulo">Código e denominação</span> '
        "<strong>CLASS-FINAL — Classificação para a Entrevista</strong></p></div>"
        f'<fieldset class="campos etapas"><legend>Etapas que entram neste marco</legend>'
        f"{etapas_do_marco}</fieldset>"
        '<div class="campos">'
        + _select(
            f"{P}-operation",
            [
                ("SOMA_PONDERADA", "Soma ponderada pelos pesos das Etapas"),
                ("MEDIA_PONDERADA", "Média ponderada pelos pesos das Etapas"),
            ],
            um(f"{P}-operation"),
            "Como as pontuações se combinam",
        )
        + _select(
            f"{P}-normalization",
            [("NENHUMA", "Nenhuma"), ("PELA_SOMA_DOS_PESOS", "Dividir pela soma dos pesos")],
            um(f"{P}-normalization"),
            "Normalização",
        )
        + _input(f"{P}-scale", um(f"{P}-scale"), "Casas decimais")
        + _select(
            f"{P}-mode",
            [
                ("", "Escolha o arredondamento"),
                ("MEIO_PARA_CIMA", "Meio para cima (2,5 vira 3)"),
                ("MEIO_PARA_PAR", "Meio para par (2,5 vira 2)"),
                ("TRUNCAR", "Truncar (2,9 vira 2)"),
            ],
            um(f"{P}-mode"),
            "Arredondamento",
        )
        + "</div>"
        + criterios
        + '<details class="bloco-do-marco" open><summary>Regra de corte</summary>'
        '<div class="campos">'
        + _select(
            f"{P}-cutTargetKind",
            [
                ("", "Este marco não corta"),
                ("FIXED", "Uma quantidade fixa, publicada abaixo"),
                ("FROM_VACANCY_TABLE", "Quantas vagas o quadro publicar no recorte"),
            ],
            um(f"{P}-cutTargetKind"),
            "Quantos progridem",
        )
        + _input(f"{P}-cutTargetCount", um(f"{P}-cutTargetCount"), "Alvo")
        + _input(f"{P}-cutSurplusCount", um(f"{P}-cutSurplusCount"), "Suplentes")
        + _select(
            f"{P}-cutTieOutcome",
            [
                ("", "Escolha o desfecho"),
                ("ADMITS_SURPLUS", "Todos os empatados progridem"),
                ("STRICT", "A faixa para no alvo"),
            ],
            um(f"{P}-cutTieOutcome"),
            "Empate na última posição",
        )
        + _select(
            f"{P}-cutGovernedStage",
            governaveis,
            um(f"{P}-cutGovernedStage"),
            "Etapa que o corte alimenta",
        )
        + _select(
            f"{P}-cutContinuation",
            [
                ("", "Escolha"),
                ("ALLOWED", "Admite continuar além da faixa publicada"),
                ("NONE", "Não admite: a faixa é o que foi publicado"),
            ],
            um(f"{P}-cutContinuation"),
            "Faixa seguinte",
        )
        + "</div></details>"
        # O botão: controle, e não ajuda — o resultado mora fora do cartão (D-001).
        + '<p class="acoes-do-marco"><button type="button" class="acao" data-abre-previa '
        'hx-get="/previa" hx-include="#composicao" hx-target="#painel-da-previa" '
        'hx-swap="innerHTML" aria-controls="painel-da-previa">Simular classificação</button></p>'
        "</fieldset>"
    )
    cenario = um("cenario") or "sem_empate"
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="htmx-config" content='{{"includeIndicatorStyles":false,"allowEval":false}}'>
<title>Prévia da classificação — protótipo da 094</title>
<link rel="stylesheet" href="/estatico/prototipo.css">
<script src="/estatico/htmx.min.js" defer></script>
<script src="/estatico/prototipo.js" defer></script>
</head>
<body>
<header class="faixa-do-prototipo">
  <p><strong>Protótipo da spec 094</strong> — não é a tela do produto, e nada aqui grava.</p>
  <ul class="legenda">
    <li><span class="selo selo-motor">motor oficial</span> executado de verdade:
      <code>combinar</code>, <code>ordenar</code>, <code>faixa.calcular</code>,
      <code>titulares_iniciais</code></li>
    <li><span class="selo selo-demo">demonstrativo</span> cenários, a função extraída em esboço,
      as frases, este cartão simplificado</li>
  </ul>
  <nav aria-label="Configurações de exemplo"><p>Configurações de exemplo:</p>
    <ul class="exemplos"><li><a href="/">Padrão</a></li>{exemplos}</ul></nav>
</header>
<div class="pagina">
<main>
<h1>Etapa Classificação <span class="selo selo-demo">demonstrativo</span></h1>
<form id="composicao" action="/" method="get">
<input type="hidden" name="cenario-inicial" value="{escape(cenario)}">
<details class="de-outros-passos" open>
  <summary>Vem de outros passos
    <span class="resumo-do-bloco">no produto, só leitura</span></summary>
  <p class="ajuda">No produto, os pesos são do passo Etapas e o quadro de vagas do passo Perfis.
    Aqui eles se editam só para a avaliação.</p>
  <ul class="pesos">{pesos}</ul>
  <p class="campo curto"><label for="quadro-vagas">Vagas na linha geral do quadro</label>
    <input type="number" min="0" id="quadro-vagas" name="quadro-vagas"
      value="{escape(um("quadro-vagas"))}"></p>
  <p class="ajuda">Fatos declarados do Perfil: Data de nascimento (data), Tempo de serviço
    (inteiro).</p>
</details>
<fieldset class="linha perfil"><legend>PROF-MAT — Professor de Matemática</legend>
{cartao}
</fieldset>
</form>
</main>
<aside id="painel-da-previa" class="painel-da-previa" aria-label="Prévia da classificação"></aside>
</div>
<p id="anuncio-da-previa" class="oculto" role="status" aria-live="polite"></p>
</body>
</html>"""


# ---------------------------------------------------------------------------------------------
# O painel
# ---------------------------------------------------------------------------------------------


def _desfecho(valor):
    return {
        "ADMITS_SURPLUS": "“Todos os empatados progridem”",
        "STRICT": "“A faixa para no alvo”",
    }.get(valor, "não declarado")


def _criterio(criterio, etapas):
    alvo = (criterio.get("parameters") or {}).get("stageId") or (
        criterio.get("parameters") or {}
    ).get("factId")
    nome = (etapas.get(alvo) or {}).get("name") or next(
        (f["name"] for f in previa.FATOS if f["id"] == alvo), alvo
    )
    tipo = {
        "MAIOR_PONTUACAO_NA_ETAPA": f"maior pontuação na {nome}",
        "MAIOR_VALOR_DE_FATO": f"maior {nome.lower()}",
        "MENOR_VALOR_DE_FATO": f"menor {nome.lower()}",
    }.get(criterio.get("type"), criterio.get("type"))
    return f"{criterio['order']}º critério ({tipo})"


def _valor(criterio, item):
    from processo_seletivo.classificacao.domain.desempate import _valor_do_criterio

    return _valor_do_criterio(criterio, item)


def _nomes(itens, exceto):
    outros = [i["nome"] for i in itens if i["inscricao_id"] != exceto["inscricao_id"]]
    if len(outros) <= 3:
        return " e ".join([", ".join(outros[:-1]), outros[-1]] if len(outros) > 1 else outros)
    return f"{', '.join(outros[:3])} e mais {len(outros) - 3}"


def porque(item, etapas, escala):
    """A frase da linha — da trajetória da partição, e não de uma segunda ordenação (D-011)."""
    pontuacao = numero(item["pontuacao"], escala)
    grupo = item["grupo_da_pontuacao"]
    if len(grupo) == 1:
        return f"Pontuação combinada {pontuacao}, distinta de todas."
    partes = [f"Empatou na pontuação ({pontuacao}) com {_nomes(grupo, item)}."]
    for passo, criterio, sub in item["trajetoria"]:
        rotulo = _criterio(criterio, etapas)
        meu = _valor(criterio, item)
        if passo == "separou":
            outros = [o for o in sub if _valor(criterio, o) != meu]
            if meu is None:
                partes.append(f"No {rotulo}, não tem o valor e fica por último nele.")
            else:
                valores = {_valor(criterio, o) for o in outros}
                contra = ", ".join(sorted(numero(v) for v in valores if v is not None))
                if None in valores:
                    contra = ", ".join(filter(None, [contra, "quem não tem o valor"]))
                partes.append(f"Separado pelo {rotulo}: {numero(meu)}, contra {contra}.")
        else:
            valores = {_valor(criterio, o) for o in sub}
            if None in valores and criterio.get("whenMissing") == "CRITERIO_NAO_SE_APLICA":
                partes.append(
                    f"O {rotulo} não se aplica a este grupo: alguém nele não tem o valor."
                )
            elif valores == {None}:
                partes.append(f"O {rotulo} não separou: ninguém no grupo tem o valor.")
            else:
                partes.append(
                    f"O {rotulo} não separou: valores iguais ({numero(next(iter(valores)))})."
                )
    if item["empate_residual"]:
        quantos = len(item["grupo_final"])
        partes.append(
            f"Nenhum critério declarado separa os {quantos}: dividem a {ordinal(item['posicao'])} "
            "posição, e o sistema não escolhe entre eles."
        )
    return " ".join(partes)


def _situacao(item, r):
    corte = r["corte"]
    if not corte["declarado"]:
        return "sem-corte", "Classificado — o marco não corta"
    if corte.get("recusado") or (corte.get("sem_desfecho") and corte.get("atravessa")):
        return "parado", "Corte não emitido"
    progrediram = corte["progrediram"]
    if item["inscricao_id"] not in progrediram:
        return "fora", "Fora da faixa"
    # O empate divide a posição, e a marca é do grupo inteiro: dizer que um é suplente e o outro
    # entrou por empate seria escolher entre eles pela ordem de entrada, que o motor não faz.
    excedentes = set(corte.get("excedentes", []))
    if excedentes and any(o["inscricao_id"] in excedentes for o in item["grupo_final"]):
        return "excedente", "Empate na última posição da faixa — todos progridem pelo desfecho"
    alvo = r["alvo"] or 0
    antes = sum(1 for o in r["ordem"] if o["posicao"] < item["posicao"])
    juntos = sum(1 for o in r["ordem"] if o["posicao"] == item["posicao"])
    if antes < alvo < antes + juntos:
        return "fronteira", "Na faixa — empate na fronteira do alvo"
    if antes < alvo:
        return "alvo", "Dentro do alvo"
    return "suplente", "Suplente"


def _consequencia(classe, r):
    regra = r["regra"] or {}
    governada = regra.get("governedStage")
    nome = (r["etapas"].get(governada) or {}).get("name")
    if classe == "sem-corte":
        return "Ninguém é excluído da Etapa seguinte por este marco"
    if classe == "parado":
        return "Aguarda o desempate julgado ou a Retificação do desfecho"
    if classe == "fora":
        continuacao = regra.get("continuation")
        if continuacao == "ALLOWED":
            return "Não progride nesta faixa; o Edital admite faixa seguinte"
        if continuacao == "NONE":
            return "Não progride; o Edital não admite faixa seguinte"
        return "Não progride nesta faixa; a continuação não foi declarada"
    if governada == "NONE":
        return "Dentro da faixa; este corte não alimenta Etapa"
    if not nome:
        return "Dentro da faixa; a Etapa governada não foi declarada"
    return f"Progride para a {nome}"


def _interessante(item, r, total):
    pos = item["posicao"]
    fronteiras = [
        r["alvo"],
        (r["alvo"] or 0) + (r["suplentes"] or 0) if r["regra"] else None,
        r["vagas"],
    ]
    if (
        pos <= 3
        or pos > total - 2
        or item["empate_residual"]
        or len(item["grupo_da_pontuacao"]) > 1
    ):
        return True
    return any(f and abs(pos - f) <= 2 for f in fronteiras)


def _linhas(r):
    escala = r["escala"]
    linhas = []
    pulados = []
    total = len(r["ordem"])

    def fechar_pulados():
        if not pulados:
            return
        primeiro, ultimo = pulados[0]["posicao"], pulados[-1]["posicao"]
        _, rotulo = _situacao(pulados[0], r)
        linhas.append(
            f'<tr class="agrupada"><td colspan="5">Posições {primeiro} a {ultimo}: '
            f"{len(pulados)} candidatos com pontuações distintas — "
            f"{escape(rotulo.lower())}.</td></tr>"
        )
        pulados.clear()

    notas = [e for e in r["etapas_do_marco"] if e["forma"] != previa.DECISORIA]
    for item in r["ordem"]:
        classe, rotulo = _situacao(item, r)
        if not _interessante(item, r, total) and (
            not pulados or _situacao(pulados[-1], r)[0] == classe
        ):
            pulados.append(item)
            continue
        fechar_pulados()
        dividida = sum(1 for o in r["ordem"] if o["posicao"] == item["posicao"])
        posicao = ordinal(item["posicao"]) + (
            f'<span class="dividida">dividida por {dividida}</span>' if dividida > 1 else ""
        )
        detalhe = " · ".join(
            f"{escape(e['name'])} {numero(item['pontuacoes'].get(e['id']), escala)}" for e in notas
        )
        fatos = " · ".join(
            f"{escape(f['name'])} {numero(item['fatos'].get(f['id']))}"
            for f in previa.FATOS
            if any((c.get("parameters") or {}).get("factId") == f["id"] for c in r["criterios"])
        )
        linhas.append(
            f'<tr class="situacao-{classe}"><td data-rotulo="Posição">{posicao}</td>'
            f'<td data-rotulo="Candidato"><strong>{escape(item["nome"])}</strong>'
            f'<span class="detalhe">{detalhe}{" · " + fatos if fatos else ""}</span></td>'
            f'<td data-rotulo="Pontuação">{numero(item["pontuacao"], escala)}</td>'
            f'<td data-rotulo="Por quê">{escape(porque(item, r["etapas"], escala))}</td>'
            f'<td data-rotulo="Corte e próxima Etapa"><span class="marca-{classe}">'
            f"{escape(rotulo)}</span>"
            f'<span class="consequencia">{escape(_consequencia(classe, r))}</span></td></tr>'
        )
    fechar_pulados()
    for item in r["sem_posicao"]:
        linhas.append(
            '<tr class="situacao-sem-posicao"><td data-rotulo="Posição">sem posição</td>'
            f'<td data-rotulo="Candidato"><strong>{escape(item["nome"])}</strong></td>'
            '<td data-rotulo="Pontuação">—</td>'
            f'<td data-rotulo="Por quê">{escape(item["motivo"])}</td>'
            '<td data-rotulo="Corte e próxima Etapa"><span class="marca-sem-posicao">Sem posição'
            '</span><span class="consequencia">Nunca entra na faixa</span></td></tr>'
        )
    return "".join(linhas)


def _bloco_do_corte(r):
    corte = r["corte"]
    if not corte["declarado"]:
        return (
            '<p class="resultado neutro">Este marco não corta: a ordem é o resultado, e ninguém é '
            "excluído da Etapa seguinte por ele.</p>"
        )
    alvo, suplentes = r["alvo"], r["suplentes"]
    faixa_total = alvo + suplentes
    origem = escape(r["origem_do_alvo"])
    resumo = (
        f'<p class="resumo-da-faixa">Faixa: alvo {alvo} ({origem}) + {suplentes} suplentes = '
        f"<strong>{faixa_total} posições</strong>. Desfecho do empate: "
        f"{_desfecho(corte.get('desfecho'))}.</p>"
    )
    atual = (
        '<p class="comportamento-atual"><span class="selo selo-motor">comportamento atual</span> '
        "É o que o sistema faz hoje. O rótulo do campo e a frase do Edital sobre este caso estão "
        "em revisão, e esta prévia não os substitui.</p>"
    )
    if corte.get("sem_desfecho"):
        if not corte["atravessa"]:
            return resumo + (
                '<p class="resultado neutro">Nenhum empate atravessa a última posição da faixa: '
                "nesta configuração o desfecho não muda nada. Sem a declaração, porém, o Edital "
                "não publica.</p>"
            )
        a, e = corte["comparacao"]["admite"], corte["comparacao"]["estrito"]
        return (
            resumo
            + '<div class="resultado parado" role="group" aria-label="Desfecho não declarado">'
            f"<p><strong>O desfecho do empate não está declarado</strong>, e há empate residual "
            f"na {ordinal(e['posicao'])} posição, a última da faixa, com {e['quantas']} "
            "candidatos. A prévia não escolhe:</p><ul>"
            f"<li>com “Todos os empatados progridem”: {len(a['progrediram'])} progridem, "
            f"{len(a['excedentes'])} além da faixa por empate;</li>"
            "<li>com “A faixa para no alvo”: o corte não seria emitido.</li></ul>"
            "<p>Sem a declaração, o Edital não publica.</p></div>" + atual
        )
    if corte.get("recusado"):
        alternativo = corte.get("alternativo") or {}
        # Com suplentes, a fronteira que o motor confere não é a do alvo, e é isso que o rótulo
        # atual não diz (achado de 19/10). Sem suplentes, as duas coincidem.
        nao_a_do_alvo = f", e não a do alvo ({alvo})" if suplentes else ""
        return (
            resumo + '<div class="resultado parado" role="group" aria-label="Corte não emitido">'
            f"<p><strong>O corte não seria emitido.</strong> Há empate residual de "
            f"{corte['quantas']} candidatos na {ordinal(corte['posicao'])} posição — a última "
            f"da faixa de {faixa_total}{nao_a_do_alvo} —, e o desfecho declarado é "
            f"{_desfecho(corte['desfecho'])}. Ninguém progride até que o desempate seja julgado "
            "ou o desfecho retificado.</p>"
            + (
                f"<p>Com o outro desfecho, {_desfecho(alternativo['desfecho'])}, "
                f"{len(alternativo['progrediram'])} progrediriam, "
                f"{len(alternativo['excedentes'])} além da faixa por empate.</p>"
                if alternativo and not alternativo.get("recusado")
                else ""
            )
            + "</div>"
            + atual
        )
    progrediram, excedentes = len(corte["progrediram"]), len(corte["excedentes"])
    texto = (
        f'<p class="resultado saiu"><strong>O corte sairia:</strong> {progrediram} progridem'
        + (f", {excedentes} além da faixa por empate" if excedentes else "")
        + f"; {len(r['sem_posicao'])} sem posição.</p>"
    )
    if corte.get("alternativo"):
        alt = corte["alternativo"]
        texto += (
            '<p class="comparacao">Há empate na última posição da faixa. Com o outro desfecho, '
            f"{_desfecho(alt['desfecho'])}, "
            + (
                f"o corte não seria emitido (empate de {alt['quantas']} na "
                f"{ordinal(alt['posicao'])} posição)."
                if alt.get("recusado")
                else f"{len(alt['progrediram'])} progrediriam."
            )
            + "</p>"
            + atual
        )
    return resumo + texto


def _bloco_das_vagas(r):
    aviso = r["aviso_das_vagas"]
    if not aviso["avaliado"]:
        return (
            '<p class="resultado neutro">Fronteira das vagas não avaliada: '
            f"{escape(aviso['motivo'])}</p>"
        )
    if aviso["para"]:
        return (
            '<div class="resultado aviso" role="group" aria-label="Fronteira das vagas">'
            f"<p><strong>A apuração das vagas pararia</strong> na {ordinal(aviso['posicao'])} "
            f"posição, se a ocupação fosse apurada sobre este marco: o empate residual de "
            f"{aviso['quantas']} candidatos fica parte dentro e parte fora das {r['vagas']} vagas "
            "do quadro. Isso acontece qualquer que seja o desfecho declarado para o corte, e "
            "nenhum campo deste cartão o declara.</p>"
            '<p class="suposicao">A prévia supõe todos os que progrediram habilitados na Etapa '
            "governada.</p></div>"
        )
    return (
        f'<p class="resultado neutro">Nenhum empate na fronteira das {r["vagas"]} vagas: a '
        "apuração das vagas não pararia por empate.</p>"
    )


def painel(dados):
    marco = ler_marco(dados)
    etapas = ler_etapas(dados)
    vagas = ler_vagas(dados)
    # O cenário do painel vence; o inicial é só o da configuração de exemplo, na primeira abertura.
    chave = _um(dados, "cenario") or _um(dados, "cenario-inicial") or "sem_empate"
    opcoes = "".join(_opcao(k, v[0], chave) for k, v in previa.CENARIOS.items())
    descricao = previa.CENARIOS.get(chave, previa.CENARIOS["sem_empate"])[1]
    cabecalho = (
        '<div class="cabeca-do-painel">'
        '<h2 id="titulo-da-previa" tabindex="-1">Prévia da classificação</h2>'
        '<button type="button" class="fechar" hx-get="/fechar" hx-target="#painel-da-previa" '
        'hx-swap="innerHTML">Fechar</button></div>'
        '<p class="contexto">PROF-MAT · CLASS-FINAL — Classificação para a Entrevista. '
        '<span class="selo selo-demo">candidatos fictícios</span></p>'
        '<p class="campo"><label for="cenario-da-previa">Cenário</label>'
        '<select id="cenario-da-previa" name="cenario" hx-get="/previa" '
        'hx-include="#composicao" hx-target="#painel-da-previa" hx-swap="innerHTML">'
        f"{opcoes}</select></p>"
        f'<p class="descricao-do-cenario">{escape(descricao)}</p>'
    )
    # O recálculo: qualquer mudança no formulário de composição pede o painel de novo, com o que
    # está digitado. O cálculo é no servidor; o navegador só leva os campos (D-002).
    gatilho = (
        '<div class="recalculo" hx-get="/previa" '
        'hx-include="#composicao, #cenario-da-previa, #fronteiras-da-previa" '
        'hx-target="#painel-da-previa" hx-swap="innerHTML" '
        'hx-trigger="change from:#composicao, input changed delay:400ms from:#composicao">'
    )
    try:
        r = previa.calcular(marco, etapas, chave_do_cenario=chave, vagas=vagas)
    except previa.Incompleto as erro:
        faltas = "".join(f"<li>{escape(f)}</li>" for f in erro.faltas)
        anuncio = "Prévia não calculada: falta declarar " + str(len(erro.faltas)) + " item(ns)."
        return (
            gatilho
            + cabecalho
            + '<div class="resultado incompleto"><p><strong>A prévia ainda não calcula.</strong> '
            f"Falta:</p><ul>{faltas}</ul></div></div>" + _anuncio(anuncio)
        )
    r["escala"] = marco["rounding"]["scale"]
    r["etapas_do_marco"] = [r["etapas"][e] for e in marco["stages"] if e in r["etapas"]]
    tem_problema = (
        r["corte"].get("recusado")
        or r["aviso_das_vagas"].get("para")
        or (r["corte"].get("sem_desfecho") and r["corte"].get("atravessa"))
    )
    tranquilo = ""
    if not tem_problema and not any(i["empate_residual"] for i in r["ordem"]):
        tranquilo = (
            '<p class="resultado neutro">Nenhum empate residual nesta ordem: nenhuma fronteira '
            "é atravessada por empate.</p>"
        )
    conferencia = (
        '<p class="conferencia"><span class="selo selo-motor">motor oficial</span> Ordem conferida '
        "com <code>desempate.ordenar</code>: idêntica.</p>"
        if r["conferida"]
        else '<p class="conferencia divergiu">A trajetória do esboço divergiu de '
        "<code>desempate.ordenar</code>: a prévia não deve ser lida.</p>"
    )
    ancora = (
        f'<p class="ancora">Posicionamento do cenário: {escape(r["ancora"])}.</p>'
        if r["ancora"]
        else ""
    )
    # As fronteiras com que o cenário foi posicionado viajam no painel: mudou alvo, suplentes ou
    # vagas, e o painel diz que os candidatos foram reposicionados (FR-2206).
    regra = marco["cutRule"] or {}
    fronteiras = f"{r['alvo']}:{regra.get('surplusCount') if regra else ''}:{vagas}"
    anteriores = _um(dados, "fronteiras")
    if anteriores and anteriores != fronteiras:
        ancora += (
            '<p class="ancora reposicionado">Alvo, suplentes ou vagas mudaram: o cenário foi '
            "refeito sobre a nova fronteira.</p>"
        )
    ancora += (
        f'<input type="hidden" id="fronteiras-da-previa" name="fronteiras" '
        f'value="{escape(fronteiras)}">'
    )
    tabela = (
        '<div class="rolavel"><table class="previa"><caption class="oculto">Candidatos '
        "fictícios em ordem, com o motivo da posição e a situação no corte</caption><thead><tr>"
        '<th scope="col">Posição</th><th scope="col">Candidato fictício</th>'
        '<th scope="col">Pontuação</th><th scope="col">Por quê</th>'
        '<th scope="col">Corte e próxima Etapa</th></tr></thead><tbody>'
        f"{_linhas(r)}</tbody></table></div>"
    )
    corte = r["corte"]
    if corte.get("recusado"):
        anuncio = f"Corte não emitido: empate na {ordinal(corte['posicao'])} posição."
    elif corte["declarado"] and not corte.get("sem_desfecho"):
        anuncio = f"O corte sairia com {len(corte['progrediram'])} candidatos."
    else:
        anuncio = "Prévia recalculada."
    if r["aviso_das_vagas"].get("para"):
        anuncio += " A apuração das vagas pararia."
    return (
        gatilho
        + cabecalho
        + ancora
        + '<section class="resumo" aria-label="Resumo">'
        + _bloco_do_corte(r)
        + _bloco_das_vagas(r)
        + tranquilo
        + "</section>"
        + tabela
        + conferencia
        + "</div>"
        + _anuncio(anuncio)
    )


def _anuncio(texto):
    return (
        '<p id="anuncio-da-previa" class="oculto" role="status" aria-live="polite" '
        f'hx-swap-oob="true">{escape(texto)}</p>'
    )
