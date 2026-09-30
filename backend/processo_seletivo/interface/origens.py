"""De onde veio cada valor, e o que não se corrige depois — a Revisão sob a Constituição 1.2.0.

O Princípio IV passou a exigir que o que o sistema **inferir, derivar ou materializar** em nome do
operador apareça, antes do ato irreversível, com o resultado e a origem (051). A Revisão é o lugar:
é a última tela antes da submissão, e é ela que já lê o Edital inteiro do conteúdo canônico.

**Duas fontes de origem, porque há duas espécies de valor** (`D-002` da spec).

- **O padrão e a derivação são funções do contexto**, e por isso se afirmam por comparação: o
  corte é o padrão se declara o que o padrão declararia; o instante veio de um Evento se é o início
  dele. Não se guarda nada — e a afirmação é verdadeira mesmo quando alguém escolheu à mão o mesmo
  que o sistema escolheria, porque o que quem confere precisa saber é que aquele é o valor que o
  sistema põe.
- **O gesto não é função do contexto**, e por isso é lido da trilha (`APLICAR_A_TODOS`). A Revisão
  só o atribui ao gesto enquanto a impressão do valor atual for a que o gesto gravou (FR-935):
  editado depois, o valor passa a ser de quem o editou, e dizer "aplicado a partir de" seria falso.

**O que não se corrige depois** (FR-936, a `DP-19`) vem do contrato de mutabilidade, e não de uma
lista aqui — a lição da `026` sobre listas que envelhecem. A composição não ganha selo nenhum: os
cartões continuam sem ajuda visível (`FR-428` da `030`), e o aviso mora na Revisão, antes de
submeter.
"""

from datetime import datetime

from processo_seletivo.editais.domain import aplicacao as regra_da_aplicacao
from processo_seletivo.editais.domain import mutabilidade, quadro
from processo_seletivo.editais.domain.marcos import ARREDONDAMENTO_PADRAO, e_o_corte_padrao
from processo_seletivo.shared.tempo import ZONA as ZONA_INSTITUCIONAL
from processo_seletivo.sorteios.domain import prosa

PADRAO = "padrão do sistema"


# ---- por comparação -----------------------------------------------------------------------------


def do_corte(regra):
    return PADRAO if e_o_corte_padrao(regra) else ""


def do_arredondamento_do_marco(marco):
    arredondamento = marco.get("rounding") or {}
    try:
        escala = int(arredondamento.get("scale"))
    except (TypeError, ValueError):
        return ""
    if escala == ARREDONDAMENTO_PADRAO["scale"] and (
        arredondamento.get("mode") == ARREDONDAMENTO_PADRAO["mode"]
    ):
        return PADRAO
    return ""


def _instante(valor):
    try:
        return datetime.fromisoformat(str(valor))
    except (TypeError, ValueError):
        return None


def do_instante(valor, eventos):
    """O Evento de que o instante do sorteio é o início, se for (FR-929)."""
    instante = _instante(valor)
    if instante is None or instante.tzinfo is None:
        return ""
    for evento in eventos or []:
        inicio = _instante(evento.get("startAt"))
        if inicio is not None and inicio.tzinfo is not None and inicio == instante:
            return f"do Evento {evento.get('description') or evento.get('type') or ''}".strip()
    return ""


def da_prosa(par):
    """A frase publicada é a gerada da regra escolhida? (FR-930)"""
    par = par or {}
    gerada = prosa.da_regra(par.get("rule"))
    return "gerada da regra escolhida" if gerada and par.get("text") == gerada else ""


def da_linha_do_quadro(quantidade, modalidade, perfil):
    regra = (modalidade or {}).get("normativeRule") or {}
    sugestao = quadro.sugestao(
        percentual=regra.get("percentage"),
        vagas_imediatas=perfil.get("immediateVacancies"),
        rounding=regra.get("rounding"),
    )
    if sugestao is not None and sugestao.valor is not None and sugestao.valor == quantidade:
        return f"sugerida pelo percentual: {sugestao.conta}"
    return ""


def da_forma_de_convocacao(perfil, perfis):
    """A mesma forma em todos os Perfis é o que o Perfil novo herda ao nascer (FR-926)."""
    if (
        len(perfis) > 1
        and perfil.get("callForm")
        and (regra_da_aplicacao.valor_comum(perfis, "callForm") == perfil.get("callForm"))
    ):
        return "a mesma em todos os Perfis"
    return ""


def da_etapa(etapa):
    if etapa.get("forma") == "DECISORIA" and etapa.get("eliminatory"):
        return "eliminatória é o padrão da Etapa decisória"
    return ""


def com_origem(texto, origem):
    return f"{texto} ({origem})" if origem else texto


# ---- pelo registro do gesto ---------------------------------------------------------------------


def gestos_por_destino(registros):
    """`{(unidade, perfil, chave): (registro, impressão)}` — o gesto mais recente de cada destino.

    `chave` é o código da Modalidade, ou `""` nas unidades que o Perfil tem uma só. `registros` vem
    em ordem de ocorrência; o mais recente sobrescreve, e é o certo: ele é o último que gravou ali.
    """
    alcance = {}
    for registro in registros or []:
        detalhe = registro.detalhe or {}
        unidade = detalhe.get("unidade") or ""
        chave = (detalhe.get("origem") or {}).get("modalidade") or ""
        for destino in detalhe.get("destinos") or []:
            alcance[(unidade, str(destino.get("perfil")), chave)] = (
                registro,
                destino.get("impressao") or "",
            )
    return alcance


def _quando(registro):
    return registro.occurred_at.astimezone(ZONA_INSTITUCIONAL).strftime("%d/%m/%Y %H:%M")


def frase_do_gesto(registro):
    origem = (registro.detalhe or {}).get("origem") or {}
    de_onde = f"a partir do Perfil {origem['codigo']}" if origem.get("codigo") else "pelo Edital"
    return f"aplicado {de_onde}, por {registro.actor_subject}, em {_quando(registro)}"


def gesto_do_marco(alcance, perfil):
    """O gesto que gravou o marco deste Perfil, se o valor atual ainda for o que ele gravou."""
    marcos = perfil.get("classificationMilestones") or []
    achado = alcance.get(("marco", str(perfil.get("id")), ""))
    if achado is None or len(marcos) != 1:
        return None
    registro, impressao = achado
    atual = regra_da_aplicacao.impressao(regra_da_aplicacao.unidade_do_marco(marcos[0], perfil))
    return registro if atual == impressao else None


def origem_dos_marcos(perfis, alcance):
    """`{id do Perfil: frase}` — os marcos que ainda são o que um gesto gravou (053, FR-964).

    **A mesma regra e a mesma frase da Revisão**, para a linha da etapa Classificação: é
    `gesto_do_marco` que decide — a impressão do gravado ainda é a do gesto, e o Perfil tem um marco
    só —, e é `frase_do_gesto` que diz. Uma segunda leitura da origem divergiria desta na primeira
    mudança, e a tela afirmaria o que a Revisão nega.
    """
    origens = {}
    for perfil in perfis or []:
        if (gesto := gesto_do_marco(alcance, perfil)) is not None:
            origens[str(perfil.get("id"))] = frase_do_gesto(gesto)
    return origens


def gesto_da_modalidade(alcance, perfil, modalidade):
    achado = alcance.get(("modalidade", str(perfil.get("id")), modalidade.get("code") or ""))
    if achado is None:
        return None
    registro, impressao = achado
    atual = regra_da_aplicacao.impressao(
        regra_da_aplicacao.unidade_da_modalidade(modalidade, perfil)
    )
    return registro if atual == impressao else None


def gesto_do_campo(alcance, perfil, campo):
    achado = alcance.get((campo, str(perfil.get("id")), ""))
    if achado is None:
        return None
    registro, impressao = achado
    valor = regra_da_aplicacao.valor_do_campo(perfil, campo)
    atual = regra_da_aplicacao.impressao({campo: valor})
    return registro if atual == impressao else None


# ---- o que não se corrige depois de publicado ---------------------------------------------------

#: Os estruturais que quem compõe **declara** — os códigos. Os demais estruturais são identidade
#: interna (`id`), posição (`order`) ou vínculo que outra tela decide, e dizê-los a quem confere
#: seria mostrar o modelo, e não o Edital.
ESTRUTURAIS_DECLARADOS = {
    ("profiles", "code"): "Código do Perfil",
    ("competitionModalities", "code"): "Código da Modalidade",
    ("declaredFacts", "code"): "Código do fato",
    ("classificationMilestones", "code"): "Código do marco",
}

#: Por que um estrutural não se corrige. O contrato não lhe dá razão — a natureza o explica
#: (`Mutabilidade` a proíbe) —, e a tela precisa dizer em palavras o que a natureza diz.
RAZAO_DO_ESTRUTURAL = (
    "É a identidade que outras declarações citam — o recorte, a inscrição, o documento exigido e "
    "os atos da operação —, e trocá-la depois de publicada desfaria essas referências."
)


def _itens(snapshot, colecao):
    """`(dono, item)` de cada item da coleção, com o nome de quem o tem, para a frase."""
    if colecao == mutabilidade.RAIZ:
        return [("o Edital", snapshot)]
    if colecao in ("schedule", "stages", "sections", "attachments", "documentRequirements"):
        return [
            (item.get("description") or item.get("name") or item.get("title") or "", item)
            for item in snapshot.get(colecao) or []
            if isinstance(item, dict)
        ]
    perfis = [perfil for perfil in snapshot.get("profiles") or [] if isinstance(perfil, dict)]
    if colecao == "profiles":
        return [(perfil.get("code") or "", perfil) for perfil in perfis]
    if colecao == "tiebreakers":
        return [
            (f"{perfil.get('code') or ''}, {criterio.get('order')}º critério", criterio)
            for perfil in perfis
            for marco in perfil.get("classificationMilestones") or []
            for criterio in marco.get("tiebreakers") or []
            if isinstance(criterio, dict)
        ]
    return [
        (
            f"{perfil.get('code') or ''} · {item.get('code')}"
            if colecao == "competitionModalities"
            else perfil.get("code") or "",
            item,
        )
        for perfil in perfis
        for item in perfil.get(colecao) or []
        if isinstance(item, dict)
    ]


def _no_caminho(item, caminho):
    valor = item
    for parte in caminho.split("/"):
        if not isinstance(valor, dict):
            return None
        valor = valor.get(parte)
    return valor


def campos_definitivos(snapshot, *, rotulos, em_palavras):
    """Os campos que não se corrigem depois de publicados, com o valor deste Edital (FR-936).

    `rotulos` é `(coleção, caminho) → rótulo em português`; `em_palavras(coleção, caminho, valor,
    snapshot)` diz o valor como quem confere o lê. Os dois vêm de quem desenha a tela.

    **Do contrato, e não de uma lista.** Entra toda entrada não retificável, menos as opacas que a
    composição não pede — a tela não as escreve, e mostrá-las seria mostrar o que ninguém
    declarou —, e os estruturais que se declaram. Campo novo não retificável aparece aqui no dia em
    que entra no contrato; o guardião de completude o cobra (SC-346).
    """
    itens = []
    for (colecao, caminho), decisao in mutabilidade.CONTRATO.items():
        if decisao.natureza is mutabilidade.Natureza.NAO_RETIFICAVEL:
            if (colecao, caminho) in mutabilidade.OPACOS and caminho != "normativeRule/rounding":
                continue
            razao = decisao.razao
        elif (colecao, caminho) in ESTRUTURAIS_DECLARADOS:
            razao = RAZAO_DO_ESTRUTURAL
        else:
            continue
        valores = {}
        for dono, item in _itens(snapshot, colecao):
            valor = _no_caminho(item, caminho)
            if valor in (None, "", [], {}):
                continue
            valores.setdefault(em_palavras(colecao, caminho, valor, snapshot), []).append(dono)
        if not valores:
            continue
        rotulo = rotulos.get((colecao, caminho)) or ESTRUTURAIS_DECLARADOS.get(
            (colecao, caminho), caminho
        )
        if (colecao, caminho) in ESTRUTURAIS_DECLARADOS:
            linhas = [", ".join(valores)]
        else:
            linhas = [
                valor if donos == ["o Edital"] else f"{valor} — {', '.join(donos)}"
                for valor, donos in valores.items()
            ]
        itens.append(
            {
                "titulo": rotulo,
                "chave": (colecao, caminho),
                "linhas": [*linhas, f"Por que não se corrige: {razao}"],
            }
        )
    return itens
