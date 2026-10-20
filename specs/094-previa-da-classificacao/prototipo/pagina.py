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
    "sem-empate": (
        "Classificação comum, sem empate",
        {"candidatos": ["caso:sem_empate"]},
    ),
    "achado-1": (
        "Achado, linha 1: 10 + 5, empate na 10ª",
        {f"{P}-cutSurplusCount": ["5"], "candidatos": ["caso:empate_nas_vagas"]},
    ),
    "achado-2": (
        "Achado, linha 2: 10 + 5, empate na 15ª, STRICT",
        {
            f"{P}-cutSurplusCount": ["5"],
            f"{P}-cutTieOutcome": ["STRICT"],
            "candidatos": ["caso:empate_na_faixa"],
        },
    ),
    "achado-3": (
        "Achado, linha 3: 10 sem suplentes, empate na 10ª",
        {f"{P}-cutSurplusCount": ["0"], "candidatos": ["caso:empate_nas_vagas"]},
    ),
    "sem-desfecho": (
        "Desfecho não declarado",
        {f"{P}-cutTieOutcome": [""], "candidatos": ["caso:empate_na_faixa"]},
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
    candidatos = um("candidatos") or "estavel"
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
    <ul class="exemplos"><li><a href="/">População estável (padrão)</a></li>{exemplos}</ul></nav>
</header>
<div class="pagina">
<main>
<h1>Etapa Classificação <span class="selo selo-demo">demonstrativo</span></h1>
<form id="composicao" action="/" method="get">
<input type="hidden" name="candidatos-inicial" value="{escape(candidatos)}">
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
# O painel — segunda rodada (19/10): a consequência primeiro, a tabela depois
# ---------------------------------------------------------------------------------------------
#
# A primeira versão abria com a tabela inteira, e cada linha repetia um parágrafo. Ela demonstrava o
# algoritmo; não respondia, de relance, "quantos avançam, quem fica de fora, por que empatou, o que
# acontece depois, o que mudou". A ordem agora é essa: manchete, fluxo, o que mudou, a fronteira, os
# empates lado a lado — e a classificação completa e a explicação técnica atrás de um clique.

C = previa

CONSEQUENCIA = {
    C.PROGRIDE: ("progride", "Progride"),
    C.PELO_EMPATE: ("pelo-empate", "Progride pelo empate"),
    C.NAO_PROGRIDE: ("nao-progride", "Não progride"),
    C.AGUARDA: ("aguarda", "Aguarda desempate"),
    C.SEM_POSICAO: ("sem-posicao", "Sem posição"),
    C.SEGUE: ("segue", "Segue — sem corte"),
}
PLURAL = {
    C.PROGRIDE: "progridem",
    C.PELO_EMPATE: "progridem pelo empate",
    C.NAO_PROGRIDE: "não progridem",
    C.AGUARDA: "aguardam o desempate",
    C.SEM_POSICAO: "sem posição",
    C.SEGUE: "seguem, sem corte",
}


def _desfecho(valor):
    return {
        "ADMITS_SURPLUS": "“Todos os empatados progridem”",
        "STRICT": "“A faixa para no alvo”",
    }.get(valor, "não declarado")


def _alvo_do_criterio(criterio):
    parametros = criterio.get("parameters") or {}
    return parametros.get("stageId") or parametros.get("factId")


def _criterio(criterio, etapas, *, curto=False):
    alvo = _alvo_do_criterio(criterio)
    nome = (etapas.get(alvo) or {}).get("name") or next(
        (f["name"] for f in previa.FATOS if f["id"] == alvo), alvo
    )
    tipo = {
        "MAIOR_PONTUACAO_NA_ETAPA": f"maior nota na {nome}",
        "MAIOR_VALOR_DE_FATO": f"maior {nome.lower()}",
        "MENOR_VALOR_DE_FATO": f"menor {nome.lower()}",
    }.get(criterio.get("type"), criterio.get("type"))
    return tipo if curto else f"{criterio['order']}º · {tipo}"


def _valor(criterio, item):
    from processo_seletivo.classificacao.domain.desempate import _valor_do_criterio

    return _valor_do_criterio(criterio, item)


def _lista(nomes):
    nomes = list(nomes)
    if len(nomes) <= 1:
        return "".join(nomes)
    return ", ".join(nomes[:-1]) + " e " + nomes[-1]


def _contagens(r):
    codigos = list(r["consequencias"].values())
    return {
        "total": r["total"],
        "com_posicao": len(r["ordem"]),
        "sem_posicao": len(r["sem_posicao"]),
        "progridem": sum(1 for c in codigos if c in (C.PROGRIDE, C.PELO_EMPATE, C.SEGUE)),
        "pelo_empate": sum(1 for c in codigos if c == C.PELO_EMPATE),
        # Quantos entraram **além da faixa** — o número que o corte registra (FR-196 da `014`).
        # Não é o tamanho do grupo empatado: dois empatados na 15ª de uma faixa de 15 são um dentro
        # e um além, e os dois progridem pelo desfecho.
        "alem_da_faixa": len(r["corte"].get("excedentes") or []),
        "nao_progridem": sum(1 for c in codigos if c == C.NAO_PROGRIDE),
        "empates": len(_grupos_empatados(r, so_residuais=True)),
    }


def _etapa_seguinte(r):
    governada = (r["regra"] or {}).get("governedStage")
    if governada == "NONE":
        return None, "Nenhuma Etapa"
    nome = (r["etapas"].get(governada) or {}).get("name")
    return nome, nome or "Etapa seguinte não declarada"


def _impedido(r):
    corte = r["corte"]
    return bool(corte.get("recusado") or (corte.get("sem_desfecho") and corte.get("atravessa")))


# --- 1. A manchete ----------------------------------------------------------------------------


def _manchete(r):
    """A consequência geral, em uma frase — a primeira coisa que o painel diz."""
    n = _contagens(r)
    corte = r["corte"]
    nome, rotulo = _etapa_seguinte(r)
    if not corte["declarado"]:
        return (
            f"<strong>Este marco não corta:</strong> os {n['com_posicao']} classificados seguem, "
            f"e {n['sem_posicao']} ficam sem posição.",
            f"Sem corte: {n['com_posicao']} classificados seguem.",
        )
    if corte.get("recusado"):
        return (
            "<strong>O corte não seria emitido.</strong> "
            f"{corte['quantas']} candidatos empatam na {corte['posicao']}ª posição, a última da "
            "faixa, e o desfecho declarado não deixa todos entrarem. Ninguém progride até o "
            "desempate ser julgado ou o desfecho ser retificado.",
            f"Corte impedido: empate na {corte['posicao']}ª posição.",
        )
    if corte.get("sem_desfecho") and corte.get("atravessa"):
        estrito = corte["comparacao"]["estrito"]
        return (
            "<strong>Falta declarar o desfecho do empate.</strong> "
            f"Há empate na {estrito['posicao']}ª posição, a última da faixa, e o resultado depende "
            "dele: veja as duas possibilidades no corte, abaixo.",
            "Desfecho do empate não declarado.",
        )
    destino = f"para a {nome}" if nome else "na faixa"
    pelo_empate = (
        f", {n['alem_da_faixa']} além da faixa pelo empate na {corte['ultima']}ª"
        if n["alem_da_faixa"]
        else ""
    )
    return (
        f"<strong>{n['progridem']} de {n['total']} candidatos progridem {escape(destino)}</strong>"
        f"{pelo_empate}. {n['nao_progridem']} não progridem"
        + (f"; {n['sem_posicao']} ficam sem posição." if n["sem_posicao"] else "."),
        f"{n['progridem']} de {n['total']} progridem.",
    )


# --- 2. O fluxo: classificação → corte → Etapa seguinte, e depois a ocupação ------------------


def _fluxo(r):
    n = _contagens(r)
    corte = r["corte"]
    regra = r["regra"] or {}
    nome, rotulo = _etapa_seguinte(r)
    empates = (
        f"{n['empates']} empate{'s' if n['empates'] > 1 else ''} não resolvido"
        f"{'s' if n['empates'] > 1 else ''}"
        if n["empates"]
        else "nenhum empate não resolvido"
    )
    classificacao = (
        '<li class="passo"><span class="passo-nome">Classificação</span>'
        f"<strong>{n['com_posicao']} com posição</strong>"
        f"<span>{n['sem_posicao']} sem posição · {empates}</span></li>"
    )
    if not corte["declarado"]:
        passo_corte = (
            '<li class="passo passo-neutro"><span class="passo-nome">Corte</span>'
            "<strong>Não corta</strong><span>ninguém é excluído por este marco</span></li>"
        )
        seguinte = (
            '<li class="passo"><span class="passo-nome">Depois</span>'
            f"<strong>{n['com_posicao']} seguem</strong><span>na ordem acima</span></li>"
        )
    else:
        alvo, suplentes = r["alvo"], r["suplentes"]
        tamanho = f"faixa de {alvo + suplentes}" + (
            f" = alvo {alvo} + {suplentes} suplentes" if suplentes else f" = alvo {alvo}"
        )
        if corte.get("recusado"):
            estado, marca, detalhe = "impedido", "Impedido", f"empate na {corte['posicao']}ª"
        elif corte.get("sem_desfecho") and corte.get("atravessa"):
            estado, marca, detalhe = "impedido", "Depende do desfecho", "não declarado"
        else:
            estado, marca = "emitivel", "Emitível"
            detalhe = (
                f"+{n['alem_da_faixa']} além da faixa, pelo empate na {corte['ultima']}ª"
                if n["alem_da_faixa"]
                else "nenhum empate na última posição"
            )
            if alvo + suplentes >= n["com_posicao"]:
                # Na população estável a faixa pode passar do total depois de uma mudança: dizer
                # isso evita ler "todos progridem" como efeito da regra, e não da amostra.
                detalhe = (
                    f"a faixa passa dos {n['com_posicao']} classificados: todos cabem — "
                    "remonte a população para ver a fronteira"
                    if r["modo"] == previa.ESTAVEL
                    else f"a faixa passa dos {n['com_posicao']} classificados: todos cabem"
                )
        passo_corte = (
            f'<li class="passo passo-{estado}"><span class="passo-nome">Corte</span>'
            f"<strong>{marca}</strong><span>{tamanho}</span><span>{escape(detalhe)}</span></li>"
        )
        if _impedido(r):
            quantos, sub = "Ninguém, por enquanto", "até o desempate ou a Retificação"
        elif nome is None and regra.get("governedStage") == "NONE":
            quantos, sub = f"{n['progridem']} na faixa", "o corte não alimenta Etapa"
        else:
            quantos, sub = f"{n['progridem']} participam", "os que progridem no corte"
        seguinte = (
            f'<li class="passo"><span class="passo-nome">{escape(rotulo)}</span>'
            f"<strong>{quantos}</strong><span>{sub}</span></li>"
        )
    ramo = ""
    if corte["declarado"] and not _impedido(r) and n["nao_progridem"]:
        continuacao = regra.get("continuation")
        texto = {
            "ALLOWED": "o Edital admite faixa seguinte: um novo corte, emitido depois, pode "
            "alcançá-los.",
            "NONE": "o Edital não admite faixa seguinte: a participação deles termina aqui.",
        }.get(continuacao, "a continuação não foi declarada.")
        ramo = (
            f'<p class="ramo"><span aria-hidden="true">↳</span> Os {n["nao_progridem"]} que não '
            f"progridem: {texto}</p>"
        )
    return (
        '<ol class="fluxo" aria-label="Da classificação à Etapa seguinte">'
        f"{classificacao}{passo_corte}{seguinte}</ol>{ramo}"
    )


def _ocupacao(r):
    """A apuração das vagas — separada do corte, e sempre como hipótese (D-006)."""
    aviso = r["aviso_das_vagas"]
    vagas = r["vagas"]
    cabeca = (
        '<section class="ocupacao" aria-labelledby="titulo-ocupacao">'
        '<h3 id="titulo-ocupacao">Depois do corte: a apuração das vagas '
        '<span class="selo selo-hipotese">hipótese</span></h3>'
    )
    if not aviso["avaliado"]:
        corpo = f'<p class="estado-neutro">Não avaliada: {escape(aviso["motivo"])}</p>'
    elif aviso["para"]:
        corpo = (
            f'<p class="estado-aviso"><strong>Pararia na {aviso["posicao"]}ª posição.</strong> '
            f"{aviso['quantas']} empatados disputam a última das {vagas} vagas do quadro, e a "
            "apuração não escolhe entre eles — qualquer que seja o desfecho declarado para o "
            "corte. Nenhum campo deste cartão trata disso.</p>"
        )
    else:
        corpo = (
            f'<p class="estado-ok">Seria possível: nenhum empate atravessa a última das {vagas} '
            "vagas.</p>"
        )
    return (
        cabeca
        + corpo
        + '<p class="nota">Se a ocupação for apurada sobre este marco, com as vagas da linha geral '
        "do quadro e todos os que progrediram habilitados. A prévia não simula chamadas, "
        "desistências, movimentos nem reversão.</p></section>"
    )


# --- 3. O que mudou ----------------------------------------------------------------------------


def _o_que_mudou(diff, r):
    if diff is None:
        return ""
    if not diff["mudancas"] and not diff["quantos"]:
        return (
            '<p class="mudou nada">Com a última alteração, a consequência não mudou para '
            "ninguém.</p>"
        )
    nomes = {i["inscricao_id"]: i["nome"] for i in r["ordem"] + r["sem_posicao"]}
    quem = sorted(nomes[i] for i in diff["mudaram"] if i in nomes)
    itens = "".join(f"<li>{escape(m)}</li>" for m in diff["mudancas"])
    if len(quem) > 5:
        itens += f"<li>{len(quem)} candidatos mudaram de situação (marcados na tabela).</li>"
    elif quem:
        itens += f"<li>Mudaram de situação: {escape(_lista(quem))} (marcados na tabela).</li>"
    return (
        '<section class="mudou" aria-labelledby="titulo-mudou">'
        '<h3 id="titulo-mudou">O que mudou com a sua alteração</h3>'
        f"<ul>{itens}</ul></section>"
    )


# --- 4. A fronteira ---------------------------------------------------------------------------


def _limites(r):
    """`[(quantos, rótulo)]` — onde a tabela traça uma linha: alvo, fim da faixa, vagas."""
    limites = {}
    if r["corte"]["declarado"]:
        alvo, suplentes = r["alvo"], r["suplentes"]
        limites.setdefault(alvo, []).append(f"alvo ({alvo})")
        if suplentes:
            limites.setdefault(alvo + suplentes, []).append(
                f"fim da faixa ({alvo} + {suplentes} suplentes)"
            )
    if r["vagas"]:
        limites.setdefault(r["vagas"], []).append(f"última vaga ({r['vagas']})")
    return sorted((k, " · ".join(v)) for k, v in limites.items() if k)


def _na_ordem(r, itens):
    """Os participantes como a ordem final os tem — com posição. A trajetória guarda os crus."""
    por_id = {i["inscricao_id"]: i for i in r["ordem"]}
    return [por_id[i["inscricao_id"]] for i in itens]


def _grupos_empatados(r, *, so_residuais=False):
    vistos, grupos = set(), []
    for item in r["ordem"]:
        grupo = item["grupo_final"] if so_residuais else item["grupo_da_pontuacao"]
        chave = tuple(sorted(i["inscricao_id"] for i in grupo))
        if len(grupo) > 1 and chave not in vistos:
            vistos.add(chave)
            grupos.append(_na_ordem(r, grupo))
    return grupos


def _marca(codigo, r):
    classe, rotulo = CONSEQUENCIA[codigo]
    if codigo == C.PROGRIDE and (r["regra"] or {}).get("governedStage") == "NONE":
        rotulo = "Na faixa"
    return f'<span class="marca marca-{classe}">{rotulo}</span>'


def _rotulo_de_posicao(item, r):
    juntos = sum(1 for o in r["ordem"] if o["posicao"] == item["posicao"])
    dividida = f'<span class="dividida">dividida por {juntos}</span>' if juntos > 1 else ""
    return f"{item['posicao']}ª{dividida}"


def _linha(item, r, mudaram):
    codigo = r["consequencias"][item["inscricao_id"]]
    etiqueta = ""
    if item["empate_residual"]:
        etiqueta = '<span class="etiqueta etiqueta-empate">empate não resolvido</span>'
    elif len(item["grupo_da_pontuacao"]) > 1:
        etiqueta = '<span class="etiqueta">desempatado</span>'
    mudou = (
        '<span class="etiqueta etiqueta-mudou">mudou</span>'
        if item["inscricao_id"] in mudaram
        else ""
    )
    return (
        f'<tr class="linha-{CONSEQUENCIA[codigo][0]}">'
        f'<td data-rotulo="Posição">{_rotulo_de_posicao(item, r)}</td>'
        f'<td data-rotulo="Candidato">{escape(item["nome"])}{etiqueta}</td>'
        f'<td data-rotulo="Pontuação">{numero(item["pontuacao"], r["escala"])}</td>'
        f'<td data-rotulo="Consequência">{_marca(codigo, r)}{mudou}</td></tr>'
    )


def _fronteira(r, mudaram):
    """Só quem ajuda a entender o cenário: perto de cada limite, nos empates, e quem mudou."""
    ordem = r["ordem"]
    limites = _limites(r)
    relevantes = set()
    for quantos, _ in limites:
        relevantes.update(range(max(quantos - 2, 0), min(quantos + 2, len(ordem))))
    for indice, item in enumerate(ordem):
        if len(item["grupo_da_pontuacao"]) > 1 or item["inscricao_id"] in mudaram:
            relevantes.add(indice)
    if not limites:
        relevantes.update(range(min(5, len(ordem))))
    linhas, pulados = [], []

    def fechar():
        if pulados:
            codigo = r["consequencias"][pulados[0]["inscricao_id"]]
            linhas.append(
                '<tr class="agrupada"><td colspan="4">'
                f"{_intervalo(pulados)} sem empate — "
                f"{PLURAL[codigo] if len(pulados) > 1 else CONSEQUENCIA[codigo][1].lower()}"
                "</td></tr>"
            )
            pulados.clear()

    por_limite = dict(limites)
    for indice, item in enumerate(ordem):
        codigo = r["consequencias"][item["inscricao_id"]]
        if indice not in relevantes:
            if pulados and r["consequencias"][pulados[-1]["inscricao_id"]] != codigo:
                fechar()
            pulados.append(item)
        else:
            fechar()
            linhas.append(_linha(item, r, mudaram))
        if indice + 1 in por_limite:
            fechar()
            proximo = ordem[indice + 1] if indice + 1 < len(ordem) else None
            atravessa = (
                f" — o empate da {item['posicao']}ª atravessa esta linha"
                if proximo and proximo["posicao"] == item["posicao"]
                else ""
            )
            linhas.append(
                f'<tr class="limite"><td colspan="4"><span>Linha do '
                f"{escape(por_limite[indice + 1])}{atravessa}</span></td></tr>"
            )
    fechar()
    for item in r["sem_posicao"]:
        linhas.append(
            '<tr class="linha-sem-posicao"><td data-rotulo="Posição">—</td>'
            f'<td data-rotulo="Candidato">{escape(item["nome"])}'
            f'<span class="etiqueta">{escape(_motivo_curto(item))}</span></td>'
            '<td data-rotulo="Pontuação">—</td>'
            f'<td data-rotulo="Consequência">{_marca(C.SEM_POSICAO, r)}</td></tr>'
        )
    return (
        '<section aria-labelledby="titulo-fronteira"><h3 id="titulo-fronteira">Quem está perto '
        'dos limites</h3><div class="rolavel"><table class="fronteira"><thead><tr>'
        '<th scope="col">Posição</th><th scope="col">Candidato</th>'
        '<th scope="col">Pontuação</th><th scope="col">Consequência</th></tr></thead>'
        f"<tbody>{''.join(linhas)}</tbody></table></div></section>"
    )


def _intervalo(itens):
    if len(itens) == 1:
        return f"{itens[0]['posicao']}ª: 1 candidato"
    return f"{itens[0]['posicao']}ª a {itens[-1]['posicao']}ª: {len(itens)} candidatos"


def _motivo_curto(item):
    motivo = item.get("motivo") or ""
    if motivo.startswith("Eliminado"):
        return motivo.rstrip(".").lower()
    if motivo.startswith("Sem nota em "):
        return "sem nota na " + motivo.removeprefix("Sem nota em ").split(":")[0]
    return motivo


# --- 5. Os empates, lado a lado ---------------------------------------------------------------


def _efeito(criterio, grupo, r):
    """O que este critério fez **com este grupo**, lido da trajetória do motor (D-011)."""
    passos = [
        (passo, sub)
        for item in grupo
        for passo, c, sub in item["trajetoria"]
        if c is criterio or c == criterio
    ]
    if not passos:
        return "nao-usado", "Não chegou a ser usado: o grupo já estava separado"
    separou = [sub for passo, sub in passos if passo == "separou"]
    if separou:
        sub = _na_ordem(r, max(separou, key=len))
        ordenados = sorted(sub, key=lambda i: i["posicao"])
        blocos, atual = [], [ordenados[0]]
        for anterior, item in zip(ordenados, ordenados[1:], strict=False):
            if _valor(criterio, item) == _valor(criterio, anterior):
                atual.append(item)
            else:
                blocos.append(atual)
                atual = [item]
        blocos.append(atual)
        texto = " › ".join(" = ".join(i["nome"] for i in bloco) for bloco in blocos)
        return "separou", f"Separou: {texto}"
    _, sub = passos[0]
    valores = [_valor(criterio, i) for i in sub]
    if None in valores and criterio.get("whenMissing") == "CRITERIO_NAO_SE_APLICA":
        faltam = _lista(i["nome"] for i in sub if _valor(criterio, i) is None)
        return "nao-separou", f"Não se aplica: falta o valor de {faltam}"
    if all(v is None for v in valores):
        return "nao-separou", "Ninguém no grupo tem o valor"
    return "nao-separou", "Não separou: valores iguais"


def _por_que_importa(membros, r):
    """Que linha este empate atravessa, e o que isso causa — a pergunta que a tabela não faz."""
    antes = sum(1 for o in r["ordem"] if o["posicao"] < membros[0]["posicao"])
    juntos = len(membros)
    corte = r["corte"]
    linhas = []
    if corte["declarado"]:
        linhas.append(("alvo", r["alvo"]))
        if r["suplentes"]:
            linhas.append(("faixa", r["alvo"] + r["suplentes"]))
    if r["vagas"]:
        linhas.append(("vagas", r["vagas"]))
    frases = []
    for tipo, k in linhas:
        if not antes < k < antes + juntos:
            continue
        if tipo == "vagas":
            frases.append(
                f"Atravessa a última das {k} vagas: é ele que pararia a apuração das vagas."
            )
        elif tipo == "faixa" or (tipo == "alvo" and not r["suplentes"]):
            if _impedido(r):
                frases.append(
                    f"Atravessa a última posição da faixa ({k}): é ele que impede o corte."
                )
            else:
                frases.append(
                    f"Atravessa a última posição da faixa ({k}): o desfecho declarado faz todos "
                    "progredirem."
                )
        else:
            frases.append(f"Atravessa a linha do alvo ({k}), dentro da faixa: não muda o corte.")
    if not frases:
        return "Não atravessa nenhuma linha: o empate não muda a consequência de ninguém."
    return " ".join(frases)


def _empates(r):
    grupos = _grupos_empatados(r)
    if not grupos:
        return (
            '<section aria-labelledby="titulo-empates"><h3 id="titulo-empates">Empates</h3>'
            '<p class="estado-neutro">Nenhum empate na pontuação: nenhum critério de desempate '
            "precisou ser usado.</p></section>"
        )
    blocos = []
    for numero_do_grupo, grupo in enumerate(grupos):
        membros = sorted(grupo, key=lambda i: (i["posicao"], i["inscricao_id"]))
        nomes = _lista(i["nome"] for i in membros)
        posicoes = {i["posicao"] for i in membros}
        if len(posicoes) == 1:
            resultado = (
                f"<strong>Dividem a {membros[0]['posicao']}ª posição:</strong> nenhum critério "
                "declarado os separa, e o sistema não escolhe entre eles."
            )
        elif len(posicoes) == len(membros):
            resultado = "<strong>Separados:</strong> " + escape(
                ", ".join(f"{i['nome']} {i['posicao']}ª" for i in membros)
            )
        else:
            resultado = "<strong>Separados em parte:</strong> " + escape(
                ", ".join(f"{i['nome']} {i['posicao']}ª" for i in membros)
            )
        importa = _por_que_importa(membros, r) if len(posicoes) == 1 else ""
        if importa:
            resultado += f'<span class="importa">{escape(importa)}</span>'
        cabeca = "".join(f'<th scope="col">{escape(i["nome"])}</th>' for i in membros)
        linhas = (
            '<tr class="base"><th scope="row">Pontuação combinada</th>'
            + "".join(f"<td>{numero(i['pontuacao'], r['escala'])}</td>" for i in membros)
            + '<td class="efeito">Iguais: empate</td></tr>'
        )
        for criterio in r["criterios"]:
            classe, efeito = _efeito(criterio, membros, r)
            celulas = "".join(f"<td>{numero(_valor(criterio, i))}</td>" for i in membros)
            # O efeito sai duas vezes: na coluna própria, e sob o nome do critério para o estreito,
            # onde a coluna some — a folha escolhe qual se vê, e o leitor de tela lê a da coluna.
            linhas += (
                f'<tr class="efeito-{classe}"><th scope="row">'
                f"{escape(_criterio(criterio, r['etapas']))}"
                f'<span class="efeito-curto" aria-hidden="true">{escape(efeito)}</span></th>'
                f'{celulas}<td class="efeito">{escape(efeito)}</td></tr>'
            )
        if not r["criterios"]:
            linhas += (
                '<tr class="efeito-nao-usado"><th scope="row">Critérios de desempate</th>'
                f'<td colspan="{len(membros) + 1}">Este marco não declara nenhum</td></tr>'
            )
        blocos.append(
            f'<section class="empate" aria-labelledby="empate-{numero_do_grupo}">'
            f'<h4 id="empate-{numero_do_grupo}">{escape(nomes)}</h4>'
            f'<p class="resultado-do-empate">{resultado}</p>'
            '<div class="rolavel"><table class="comparacao"><thead><tr>'
            f'<th scope="col">Critério, na ordem</th>{cabeca}<th scope="col">Efeito</th>'
            f"</tr></thead><tbody>{linhas}</tbody></table></div></section>"
        )
    return (
        '<section aria-labelledby="titulo-empates"><h3 id="titulo-empates">Empates na '
        f"pontuação</h3>{''.join(blocos)}</section>"
    )


# --- 6. O que fica atrás de um clique ---------------------------------------------------------


def _completa(r, mudaram):
    notas = [e for e in r["etapas_do_marco"] if e["forma"] != previa.DECISORIA]
    fatos = [
        f for f in previa.FATOS if any(_alvo_do_criterio(c) == f["id"] for c in r["criterios"])
    ]
    cabeca = (
        '<th scope="col">Posição</th><th scope="col">Candidato</th>'
        + "".join(f'<th scope="col">{escape(e["name"])}</th>' for e in notas)
        + '<th scope="col">Pontuação</th>'
        + "".join(f'<th scope="col">{escape(f["name"])}</th>' for f in fatos)
        + '<th scope="col">Por quê</th><th scope="col">Consequência</th>'
    )
    linhas = []
    for item in r["ordem"]:
        if item["empate_residual"]:
            motivo = "empate não resolvido"
        elif item["trajetoria"]:
            ultimo = [c for p, c, _ in item["trajetoria"] if p == "separou"][-1]
            motivo = f"desempate pelo {ultimo['order']}º critério"
        else:
            motivo = "pontuação"
        codigo = r["consequencias"][item["inscricao_id"]]
        mudou = (
            '<span class="etiqueta etiqueta-mudou">mudou</span>'
            if item["inscricao_id"] in mudaram
            else ""
        )
        linhas.append(
            f'<tr><td data-rotulo="Posição">{_rotulo_de_posicao(item, r)}</td>'
            f'<td data-rotulo="Candidato">{escape(item["nome"])}</td>'
            + "".join(
                f'<td data-rotulo="{escape(e["name"])}">'
                f"{numero(item['pontuacoes'].get(e['id']), r['escala'])}</td>"
                for e in notas
            )
            + f'<td data-rotulo="Pontuação">{numero(item["pontuacao"], r["escala"])}</td>'
            + "".join(
                f'<td data-rotulo="{escape(f["name"])}">{numero(item["fatos"].get(f["id"]))}</td>'
                for f in fatos
            )
            + f'<td data-rotulo="Por quê">{motivo}</td>'
            f'<td data-rotulo="Consequência">{_marca(codigo, r)}{mudou}</td></tr>'
        )
    for item in r["sem_posicao"]:
        linhas.append(
            '<tr><td data-rotulo="Posição">—</td>'
            f'<td data-rotulo="Candidato">{escape(item["nome"])}</td>'
            + "".join(
                f'<td data-rotulo="{escape(e["name"])}">'
                f"{numero(item['pontuacoes'].get(e['id']), r['escala'])}</td>"
                for e in notas
            )
            + '<td data-rotulo="Pontuação">—</td>'
            + "".join(f'<td data-rotulo="{escape(f["name"])}">—</td>' for f in fatos)
            + f'<td data-rotulo="Por quê">{escape(item["motivo"])}</td>'
            f'<td data-rotulo="Consequência">{_marca(C.SEM_POSICAO, r)}</td></tr>'
        )
    return (
        '<details class="completa"><summary>Classificação completa — '
        f"{r['total']} candidatos, com as notas e os dados de desempate</summary>"
        '<div class="rolavel"><table class="detalhada"><thead><tr>'
        f"{cabeca}</tr></thead><tbody>{''.join(linhas)}</tbody></table></div></details>"
    )


def _como_calcula(r):
    corte = r["corte"]
    linhas = [
        "As posições seguem a numeração do sistema: empatados dividem a posição, e a seguinte é "
        "pulada (10ª, 10ª, 12ª).",
        "Quem não tem nota numa Etapa enumerada fica sem posição: ausência não vira zero.",
    ]
    if corte["declarado"]:
        linhas.append(
            f"O desfecho do empate declarado é {_desfecho(corte.get('desfecho'))}. A prévia "
            "mostra o <strong>comportamento atual do sistema</strong>: com “A faixa para no alvo”, "
            "um empate na última posição da faixa — alvo mais suplentes, e não só o alvo — impede "
            "a emissão do corte. O rótulo do campo e a frase do Edital sobre este caso estão em "
            "revisão (DP-1 e DP-2 da spec), e esta prévia não os substitui."
        )
        if corte.get("alternativo"):
            alt = corte["alternativo"]
            efeito = (
                f"o corte não seria emitido (empate na {alt['posicao']}ª)"
                if alt.get("recusado")
                else f"{len(alt['progrediram'])} progrediriam"
            )
            linhas.append(f"Com o outro desfecho, {_desfecho(alt['desfecho'])}, {efeito}.")
        if corte.get("sem_desfecho") and corte.get("atravessa"):
            a = corte["comparacao"]["admite"]
            linhas.append(
                f"Sem desfecho declarado: com “Todos os empatados progridem”, "
                f"{len(a['progrediram'])} progridem; com “A faixa para no alvo”, o corte não "
                "seria emitido. Sem a declaração, o Edital não publica."
            )
    conferencia = (
        "A ordem foi conferida com <code>desempate.ordenar</code>: idêntica."
        if r["conferida"]
        else '<strong class="divergiu">A trajetória divergiu de <code>desempate.ordenar</code>: '
        "não leia esta prévia.</strong>"
    )
    linhas.append(
        "Calculado pelo motor oficial (<code>combinar</code>, <code>ordenar</code>, "
        "<code>faixa.calcular</code>, <code>titulares_iniciais</code>). " + conferencia
    )
    linhas.append("Nada foi gravado: nem candidatos, nem configuração, nem ato.")
    itens = "".join(f"<li>{texto}</li>" for texto in linhas)
    return (
        '<details class="como-calcula"><summary>Como a prévia chega a este resultado</summary>'
        f"<ul>{itens}</ul></details>"
    )


# --- 7. Os candidatos: população estável ou caso-limite ---------------------------------------


def _candidatos(r, escolha, dados):
    opcoes = _opcao("estavel", "População estável — testar a regra", escolha) + (
        '<optgroup label="Caso-limite — demonstração dirigida">'
        + "".join(_opcao(f"caso:{k}", v[0], escolha) for k, v in previa.CENARIOS.items())
        + "</optgroup>"
    )
    seletor = (
        '<p class="campo"><label for="candidatos-da-previa">Candidatos fictícios</label>'
        '<select id="candidatos-da-previa" name="candidatos" hx-get="/previa" '
        'hx-include="#composicao, #anterior-da-previa" hx-target="#painel-da-previa" '
        f'hx-swap="innerHTML">{opcoes}</select></p>'
    )
    if r is None:
        return f'<div class="candidatos">{seletor}</div>'
    if r["modo"] == previa.CASO_LIMITE:
        descricao = previa.CENARIOS[r["cenario"]][1]
        agora = f" Agora: {escape(r['ancora'])}." if r["ancora"] else ""
        corpo = (
            '<p class="aviso-do-modo">Caso construído para demonstração: ele acompanha alvo, '
            "suplentes e vagas, e os candidatos mudam junto. Para comparar a mesma gente, use a "
            "população estável.</p>"
            f'<details class="montagem"><summary>O que este caso mostra</summary><p>'
            f"{escape(descricao)}{agora}</p></details>"
        )
        return f'<div class="candidatos">{seletor}{corpo}</div>'
    alvo0, faixa0, vagas0 = r["ancoras"]
    plantados = _lista(r["plantados"]) if r["plantados"] else "nenhum empate plantado"
    corpo = (
        f'<p class="descricao">{r["total"]} candidatos fixos enquanto o painel estiver aberto: '
        "mude a regra e compare.</p>"
        f'<details class="montagem"><summary>Como foram montados</summary><p>Para alvo {alvo0}, '
        f"faixa de {faixa0} e {vagas0} vagas, com {escape(plantados)}, mais uma candidata sem "
        "nota e um candidato eliminado.</p></details>"
        f'<input type="hidden" id="populacao-da-previa" name="populacao" '
        f'value="{alvo0}:{faixa0}:{vagas0}">'
    )
    if tuple(r["fronteiras"]) != tuple(r["ancoras"]):
        corpo += (
            '<p class="aviso-do-modo">A regra mudou desde a montagem; os empates continuam onde '
            "estavam, e é isso que deixa ver o efeito. "
            '<button type="button" class="acao-discreta" hx-get="/previa" '
            'hx-include="#composicao, #candidatos-da-previa" hx-target="#painel-da-previa" '
            'hx-swap="innerHTML">Remontar para esta configuração</button></p>'
        )
    return f'<div class="candidatos">{seletor}{corpo}</div>'


def _escolha(dados):
    escolha = _um(dados, "candidatos") or _um(dados, "candidatos-inicial") or "estavel"
    if escolha.startswith("caso:") and escolha[5:] in previa.CENARIOS:
        return escolha, previa.CASO_LIMITE, escolha[5:]
    return "estavel", previa.ESTAVEL, ""


def _populacao(dados):
    bruto = _um(dados, "populacao")
    try:
        alvo, faixa_total, vagas = (int(n) for n in bruto.split(":"))
    except ValueError:
        return None
    return alvo, faixa_total, vagas


def painel(dados):
    marco = ler_marco(dados)
    etapas = ler_etapas(dados)
    vagas = ler_vagas(dados)
    escolha, modo, chave = _escolha(dados)
    cabecalho = (
        '<div class="cabeca-do-painel">'
        '<h2 id="titulo-da-previa" tabindex="-1">Prévia da classificação</h2>'
        '<button type="button" class="fechar" hx-get="/fechar" hx-target="#painel-da-previa" '
        'hx-swap="innerHTML">Fechar</button></div>'
        '<p class="contexto">PROF-MAT · CLASS-FINAL — Classificação para a Entrevista</p>'
    )
    # O recálculo: qualquer mudança no formulário de composição pede o painel de novo, com o que
    # está digitado, a população e o estado anterior. O cálculo é no servidor (D-002).
    gatilho = (
        '<div class="recalculo" hx-get="/previa" '
        'hx-include="#composicao, #candidatos-da-previa, #populacao-da-previa, '
        '#anterior-da-previa" hx-target="#painel-da-previa" hx-swap="innerHTML" '
        'hx-trigger="change from:#composicao, input changed delay:400ms from:#composicao">'
    )
    try:
        r = previa.calcular(
            marco,
            etapas,
            chave_do_cenario=chave,
            vagas=vagas,
            modo=modo,
            populacao=_populacao(dados) if modo == previa.ESTAVEL else None,
        )
    except previa.Incompleto as erro:
        faltas = "".join(f"<li>{escape(f)}</li>" for f in erro.faltas)
        return (
            gatilho
            + cabecalho
            + _candidatos(None, escolha, dados)
            + '<div class="incompleto"><p><strong>A prévia ainda não calcula.</strong> Falta:</p>'
            f"<ul>{faltas}</ul></div>"
            + '<input type="hidden" id="anterior-da-previa" name="anterior" value="'
            + escape(_um(dados, "anterior"))
            + '"></div>'
            + _anuncio("Prévia não calculada: falta declarar " + str(len(erro.faltas)) + ".")
        )
    r["escala"] = marco["rounding"]["scale"]
    r["etapas_do_marco"] = [r["etapas"][e] for e in marco["stages"] if e in r["etapas"]]
    atual = previa.estado(r)
    diff = previa.comparar(_um(dados, "anterior"), atual, None)
    mudaram = diff["mudaram"] if diff else set()
    manchete, anuncio = _manchete(r)
    if diff and (diff["mudancas"] or diff["quantos"]):
        anuncio += " Mudou: " + " ".join(diff["mudancas"])
    estado_geral = "impedido" if _impedido(r) else "emitivel"
    return (
        gatilho
        + cabecalho
        + _candidatos(r, escolha, dados)
        + f'<p class="manchete manchete-{estado_geral}">{manchete}</p>'
        + _o_que_mudou(diff, r)
        + _fluxo(r)
        + _ocupacao(r)
        + _fronteira(r, mudaram)
        + _empates(r)
        + _completa(r, mudaram)
        + _como_calcula(r)
        + f'<input type="hidden" id="anterior-da-previa" name="anterior" value="{escape(atual)}">'
        + "</div>"
        + _anuncio(anuncio)
    )


def _anuncio(texto):
    return (
        '<p id="anuncio-da-previa" class="oculto" role="status" aria-live="polite" '
        f'hx-swap-oob="true">{escape(texto)}</p>'
    )
