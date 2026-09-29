"""A prévia do "aplicar a todos", em palavras, e a leitura do pedido (051).

A regra mora em `editais/domain/aplicacao`; aqui ela ganha a forma da tela. Duas coisas só:

1. **Ler o pedido.** O gesto é um envio do formulário da etapa (R-001): o botão da origem manda
   `aplicar`, e a confirmação manda `confirmar_aplicacao` com a impressão do que foi mostrado.
   A origem viaja pelo índice **da tela** — `marco-<perfil>-<sub>`, `modalidade-<i>-<j>` —, que é o
   que o formulário conhece, e aqui vira posição na lista que a leitura da etapa devolve.
2. **Dizer o efeito com as frases da Revisão** (UX-112). O *antes → depois* do marco sai de
   `revisao._leitura_do_marco`, que já sai do documento: uma terceira grafia da mesma regra seria a
   primeira a divergir.
"""

from dataclasses import dataclass

from processo_seletivo.editais.domain import aplicacao as regra
from processo_seletivo.interface import forms, revisao
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
    forma_de_convocacao_por_extenso,
)

EFEITO_EM_PALAVRAS = {
    regra.NASCE: "nasce",
    regra.SUBSTITUI: "substitui",
    regra.SEM_MUDANCA: "sem mudança",
    regra.FORA: "fora do alcance",
}

#: O que cada unidade é na frase da tela e da trilha.
NOME_DA_UNIDADE = {
    "marco": "o marco",
    "modalidade": "a Modalidade",
    "callForm": "a forma de convocação",
    "vacancyReversion": "a reversão de vaga reservada",
}


class PedidoInvalido(ValueError):
    """O pedido não aponta uma origem que exista nesta tela — envio forjado ou tela velha."""


@dataclass(frozen=True)
class Pedido:
    valor: str
    confirmar: bool
    cancelar: bool
    incluidos: frozenset
    impressao: str

    @property
    def unidade(self):
        tipo, _, resto = self.valor.partition(":")
        if tipo == "edital":
            return resto
        return tipo


def pedido(dados):
    """O pedido de aplicação deste envio, ou `None` quando o envio é uma gravação comum."""
    valor = (
        dados.get("confirmar_aplicacao")
        or dados.get("cancelar_aplicacao")
        or dados.get("aplicar")
        or ""
    )
    if not valor:
        return None
    return Pedido(
        valor=valor,
        confirmar=bool(dados.get("confirmar_aplicacao")),
        cancelar=bool(dados.get("cancelar_aplicacao")),
        incluidos=frozenset(dados.getlist("aplicar_destino")),
        impressao=dados.get("aplicar_impressao") or "",
    )


def etapa_do_pedido(item):
    """A etapa em que o pedido pode ser feito. O marco é da Classificação; o resto, dos Perfis."""
    return "classificacao" if item.valor.startswith("marco:") else "perfis"


def _posicao(indices, alvo):
    for posicao, indice in enumerate(indices):
        if str(indice) == str(alvo):
            return posicao
    raise PedidoInvalido("origem inexistente")


def perfis_da_classificacao(edital, marcos_por_perfil):
    """Os Perfis gravados com os marcos **digitados** — o que a gravação da etapa gravaria."""
    return [
        {**perfil, "classificationMilestones": marcos_por_perfil.get(str(perfil["id"]), [])}
        for perfil in forms.perfis_persistidos(edital)
    ]


def efeitos(item, *, etapa, digitados, dados, edital):
    """`(efeitos, perfis, origem, na_tela)` — os efeitos do pedido sobre o conteúdo da etapa.

    `perfis` é a lista sobre a qual os efeitos se aplicam; `origem` descreve a origem para a
    frase e para o registro. `na_tela` é o pedido reescrito em **posições**: a tela que volta com a
    prévia renumera os cartões a partir de zero, e o índice que o botão enviou — o de um cartão
    acrescentado pelo htmx, por exemplo — deixaria de existir nela.
    """
    tipo, _, resto = item.valor.partition(":")
    if etapa_do_pedido(item) != etapa:
        raise PedidoInvalido("pedido de outra etapa")
    try:
        if tipo == "marco":
            perfil_id, _, sub = resto.partition(":")
            perfis = perfis_da_classificacao(edital, digitados)
            posicao = _posicao(forms._indices(dados, f"marco-{perfil_id}"), sub)
            lista = regra.efeitos_do_marco(perfis, origem=perfil_id, sub=posicao)
            origem_perfil = next(p for p in perfis if str(p["id"]) == str(perfil_id))
            return (
                lista,
                perfis,
                {"perfil": str(perfil_id), "codigo": origem_perfil["code"]},
                f"marco:{perfil_id}:{posicao}",
            )
        if tipo == "modalidade":
            indice_do_perfil, _, indice = resto.partition(":")
            perfis = digitados
            origem = _posicao(forms._indices(dados, "perfil"), indice_do_perfil)
            posicao = _posicao(forms._indices(dados, f"modalidade-{indice_do_perfil}"), indice)
            lista = regra.efeitos_da_modalidade(perfis, origem=origem, indice=posicao)
            modalidade = perfis[origem]["competitionModalities"][posicao]
            return (
                lista,
                perfis,
                {
                    "perfil": perfis[origem].get("id") or "",
                    "codigo": perfis[origem].get("code") or "",
                    "modalidade": modalidade.get("code") or "",
                },
                f"modalidade:{origem}:{posicao}",
            )
        if tipo == "edital" and resto in regra.CAMPOS_DO_PERFIL:
            perfis = digitados
            lista = regra.efeitos_do_campo_do_perfil(
                perfis, campo=resto, valor=dados.get(f"edital-{resto}") or ""
            )
            return lista, perfis, {}, item.valor
    except LookupError as exc:
        raise PedidoInvalido(str(exc)) from exc
    raise PedidoInvalido("pedido desconhecido")


def aplicar(item, efeitos_calculados, perfis, *, dados):
    """O conteúdo da etapa com os valores materializados nos destinos incluídos."""
    tipo, _, resto = item.valor.partition(":")
    if tipo == "marco":
        novos = regra.aplicar_marcos(perfis, efeitos_calculados, item.incluidos)
        return {str(perfil["id"]): perfil["classificationMilestones"] for perfil in novos}
    if tipo == "modalidade":
        return regra.aplicar_modalidades(perfis, efeitos_calculados, item.incluidos)
    return regra.aplicar_campo_do_perfil(
        perfis,
        efeitos_calculados,
        item.incluidos,
        campo=resto,
        valor=dados.get(f"edital-{resto}") or "",
    )


def _identidade_do_destino(efeito, perfis):
    """A identidade do Perfil destino. Na etapa Perfis o efeito conhece a posição, e não o `id`."""
    if efeito.perfil.isdigit() and int(efeito.perfil) < len(perfis):
        return str(perfis[int(efeito.perfil)].get("id") or "")
    return efeito.perfil


def registro(item, efeitos_calculados, perfis, *, etapa, origem):
    """O `detalhe` do gesto, no contrato `contracts/registro-do-gesto.md`."""
    return {
        "etapa": etapa,
        "unidade": item.unidade,
        "origem": origem,
        "destinos": [
            {
                "perfil": _identidade_do_destino(efeito, perfis),
                "codigo": efeito.codigo,
                "efeito": efeito.efeito,
                "impressao": efeito.impressao,
            }
            for efeito in regra.alcancados(efeitos_calculados, item.incluidos)
        ],
    }


def razao(item, efeitos_calculados, *, origem):
    """A frase que a trilha exibe."""
    quantos = len(regra.alcancados(efeitos_calculados, item.incluidos))
    unidade = NOME_DA_UNIDADE.get(item.unidade, item.unidade)
    de_onde = ""
    if origem.get("modalidade"):
        de_onde = f" {origem['modalidade']} do Perfil {origem.get('codigo', '')}"
    elif origem.get("codigo"):
        de_onde = f" do Perfil {origem['codigo']}"
    etapa = "Classificação" if item.unidade == "marco" else "Perfis de Vaga"
    return f"{etapa} — {unidade}{de_onde} aplicado(a) a {quantos} Perfil(is)"


# ---- a prévia -----------------------------------------------------------------------------------


def _leitura(marco, perfil, contexto):
    if not marco:
        return {}
    snapshot = {**contexto, "profiles": [{**perfil, "classificationMilestones": [marco]}]}
    return dict(revisao._leitura_do_marco(marco, perfil, snapshot))


def _mudancas_do_marco(efeito, perfil, contexto):
    antes = _leitura(efeito.antes, perfil, contexto)
    depois = _leitura(efeito.depois, perfil, contexto)
    if efeito.efeito == regra.NASCE:
        return [
            ("Código", "—", efeito.depois.get("code") or "—"),
            ("Denominação", "—", efeito.depois.get("name") or "—"),
            *((rotulo, "—", valor) for rotulo, valor in depois.items()),
        ]
    return [
        (rotulo, antes.get(rotulo, "nada declarado"), depois.get(rotulo, "nada declarado"))
        for rotulo in dict.fromkeys([*antes, *depois])
        if antes.get(rotulo) != depois.get(rotulo)
    ]


def _leitura_da_modalidade(modalidade):
    if not modalidade:
        return {}
    regra_normativa = modalidade.get("normativeRule") or {}
    return {
        "Denominação": modalidade.get("name") or "—",
        "Descrição": modalidade.get("description") or "—",
        "Percentual": (
            f"{regra_normativa['percentage']}%" if regra_normativa.get("percentage") else "—"
        ),
        "Fundamento": regra_normativa.get("foundation") or "—",
        "Versão do fundamento": regra_normativa.get("version") or "—",
        "Arredondamento da reserva": revisao.arredondamento_da_reserva(
            regra_normativa.get("rounding")
        ),
    }


def _mudancas_da_modalidade(efeito):
    antes = _leitura_da_modalidade(efeito.antes)
    depois = _leitura_da_modalidade(efeito.depois)
    mudancas = [
        (rotulo, antes.get(rotulo, "—"), valor)
        for rotulo, valor in depois.items()
        if efeito.efeito == regra.NASCE or antes.get(rotulo) != valor
    ]
    if efeito.ampla is not None:
        anterior, aplicada = efeito.ampla
        mudancas.append(
            (
                "Ampla concorrência",
                anterior or "nenhuma Modalidade",
                aplicada or "nenhuma Modalidade",
            )
        )
    return mudancas


def _valor_do_campo_em_palavras(campo, valor):
    if campo == "callForm":
        return forma_de_convocacao_por_extenso(valor or None)
    return revisao.REVERSAO.get(valor, "não reverte") if valor else "não reverte"


def previa(item, efeitos_calculados, perfis, *, edital, dados, recusa="", valor=None):
    """O que a tela desenha antes da confirmação (FR-916, UX-111, UX-113)."""
    contexto = {
        "stages": forms.etapas_persistidas(edital),
        "drawMethod": (
            forms.metodo_comum_do_formulario(dados)
            if item.unidade == "marco"
            else edital.metodo_de_sorteio_comum
        )
        or {},
    }
    por_id = {str(perfil.get("id")): perfil for perfil in perfis}
    linhas = []
    for efeito in efeitos_calculados:
        if item.unidade == "marco":
            mudancas = (
                _mudancas_do_marco(efeito, por_id.get(efeito.perfil, {}), contexto)
                if efeito.efeito in regra.APLICAVEIS
                else []
            )
        elif item.unidade == "modalidade":
            mudancas = _mudancas_da_modalidade(efeito) if efeito.efeito in regra.APLICAVEIS else []
        else:
            mudancas = (
                [
                    (
                        revisao.ROTULO_DO_CAMPO_DO_PERFIL[item.unidade],
                        _valor_do_campo_em_palavras(item.unidade, efeito.antes),
                        _valor_do_campo_em_palavras(item.unidade, efeito.depois),
                    )
                ]
                if efeito.efeito in regra.APLICAVEIS
                else []
            )
        linhas.append(
            {
                "perfil": efeito.perfil,
                "codigo": efeito.codigo,
                "denominacao": efeito.denominacao,
                "efeito": efeito.efeito,
                "efeito_em_palavras": EFEITO_EM_PALAVRAS[efeito.efeito],
                "motivo": efeito.motivo,
                "aplicavel": efeito.efeito in regra.APLICAVEIS,
                "marcado": efeito.efeito in regra.APLICAVEIS
                and (not item.confirmar or efeito.perfil in item.incluidos),
                "mudancas": mudancas,
                "quantidade_fixa": efeito.quantidade_fixa,
                "ja_declara": ", ".join(efeito.ja_declara) or "nenhuma",
                "mostra_ja_declara": item.unidade == "modalidade",
            }
        )
    contagem = {
        efeito: sum(1 for linha in linhas if linha["efeito"] == efeito)
        for efeito in EFEITO_EM_PALAVRAS
    }
    aplicaveis = contagem[regra.NASCE] + contagem[regra.SUBSTITUI]
    return {
        "valor": valor or item.valor,
        "unidade": NOME_DA_UNIDADE.get(item.unidade, item.unidade),
        # O controle do Edital não tem Perfil de origem: todos são destino.
        "alcance": "a todos os Perfis" if item.valor.startswith("edital:") else "aos demais Perfis",
        "linhas": linhas,
        "frase": _frase_do_alcance(contagem),
        "aplicaveis": aplicaveis,
        "impressao": regra.assinatura(efeitos_calculados),
        "recusa": recusa,
    }


def _frase_do_alcance(contagem):
    partes = []
    for efeito, singular, plural in (
        (regra.NASCE, "nasce", "nascem"),
        (regra.SUBSTITUI, "muda", "mudam"),
        (regra.SEM_MUDANCA, "fica como está", "ficam como estão"),
        (regra.FORA, "fica fora do alcance", "ficam fora do alcance"),
    ):
        quantos = contagem[efeito]
        if quantos:
            partes.append(f"{quantos} {singular if quantos == 1 else plural}")
    return ", ".join(partes) or "nenhum Perfil a alcançar"


def quantos_destinos(perfis_na_tela):
    """O número do rótulo do botão: os demais Perfis (UX-110)."""
    return max(len(perfis_na_tela) - 1, 0)


#: O rótulo de cada controle do Edital, para o resumo da recusa — o mesmo do `<label>` da tela.
ROTULO_DO_CONTROLE = {
    "callForm": "Como a convocação é comunicada",
    "vacancyReversion": "Reverter vaga reservada não preenchida para a ampla concorrência",
}


def escolhas_pendentes(perfis, dados, *, gravados):
    """`{campo: valor}` dos controles do Edital cuja escolha ainda não chegou aos Perfis (051).

    O controle não é campo do Edital: é origem de um gesto, e o gesto só grava depois da prévia
    (FR-916). *Salvar* que o ignorasse descartaria a escolha em silêncio, e *Salvar* que a aplicasse
    pularia a prévia — por isso a escolha pendente impede a gravação e fica na tela.

    **Escolha** é o controle diferente do que ele mostrava ao abrir a etapa, o comum dos `gravados`:
    sem isso, quem muda um Perfil no cartão teria a gravação recusada por um controle em que não
    tocou. **Pendente** é a escolha que a prévia ainda teria o que fazer — algum Perfil nasce ou é
    substituído. O Perfil fora do alcance não conta: sem lista reservada, a reversão nunca o
    alcançaria, e a recusa seria perpétua.
    """
    pendentes = {}
    for campo in regra.CAMPOS_DO_PERFIL:
        chave = f"edital-{campo}"
        if chave not in dados:
            continue
        escolhido = dados.get(chave) or ""
        if escolhido == regra.valor_comum(gravados, campo):
            continue
        efeitos_do_controle = regra.efeitos_do_campo_do_perfil(perfis, campo=campo, valor=escolhido)
        if any(item.efeito in (regra.NASCE, regra.SUBSTITUI) for item in efeitos_do_controle):
            pendentes[campo] = escolhido
    return pendentes


def preencher_quadro(perfis):
    """`(perfis, preenchidas)` — as linhas vazias de lista reservada com a sugestão (051, FR-932).

    Só a linha **vazia**, e só quando a sugestão é um número: o que alguém digitou é decisão, e a
    faixa sem arredondamento declarado não escolhe por ninguém. Não grava — devolve o formulário,
    e gravar continua sendo *Salvar*. `preenchidas` é `[(código do Perfil, quantas)]`, para a frase.
    """
    from uuid import uuid4

    from processo_seletivo.editais.domain import quadro
    from processo_seletivo.editais.domain.perfis import listas_reservadas

    novos, preenchidas = [], []
    for perfil in perfis:
        reservadas = listas_reservadas(perfil)
        linhas = [dict(linha) for linha in perfil.get("vacancyTable") or []]
        com_linha = {str(linha.get("modalityId")) for linha in linhas if linha.get("modalityId")}
        quantas = 0
        for modalidade in perfil.get("competitionModalities") or []:
            identidade = str(modalidade.get("id") or "")
            if identidade not in reservadas or identidade in com_linha:
                continue
            regra = modalidade.get("normativeRule") or {}
            sugestao = quadro.sugestao(
                percentual=regra.get("percentage"),
                vagas_imediatas=perfil.get("immediateVacancies"),
                rounding=regra.get("rounding"),
            )
            if sugestao is None or sugestao.valor is None:
                continue
            linhas.append(
                {"id": str(uuid4()), "modalityId": identidade, "immediateVacancies": sugestao.valor}
            )
            quantas += 1
        if quantas:
            preenchidas.append((perfil.get("code") or "", quantas))
        novos.append({**perfil, "vacancyTable": linhas})
    return novos, preenchidas
