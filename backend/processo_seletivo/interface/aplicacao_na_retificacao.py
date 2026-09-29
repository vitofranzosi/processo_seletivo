"""O "aplicar a todos" na tela de Retificação — os gestos declarados e a conferência (051, US5).

A regra mora em `publicacoes/domain/aplicacao`; aqui ela ganha a forma da tela, em três partes:

1. **Os botões** (UX-110). Cada cartão de origem oferece as suas unidades, com o alcance no rótulo.
   A origem viaja pela **referência do cartão** (`g14`), e não por caminho: a tela de Retificação
   não entrega caminho normativo ao HTML (FR-019 da `002`), e a referência só significa alguma
   coisa contra a versão base que atravessa o formulário.
2. **Os gestos declarados** (R-011). Na Retificação a prévia **é** a conferência: o botão declara o
   gesto, e a declaração atravessa as idas e voltas em campos ocultos até *Criar Retificação*, que é
   a confirmação. Declarar é barato e não grava nada; desfazer tira o gesto da tela.
3. **A conferência em palavras** (FR-916, UX-111 a UX-113) e **as consequências do ato** (FR-941,
   R-015), com os rótulos que a própria tela de Retificação usa — a conferência compara o que a
   pessoa leu nos campos, e uma terceira grafia seria a primeira a divergir.
"""

import re
from dataclasses import dataclass

from processo_seletivo.editais.domain import aplicacao as regra_da_composicao
from processo_seletivo.interface import aplicacao as aplicacao_da_composicao
from processo_seletivo.interface import retificacao as tela
from processo_seletivo.publicacoes.domain import aplicacao as regra

#: As unidades de cada cartão (R-012), na ordem em que os botões aparecem.
UNIDADES_DO_CARTAO = {
    "Marco": regra.UNIDADES_DO_MARCO,
    "Perfil": regra.UNIDADES_DO_PERFIL,
    "Modalidade": (regra.MODALIDADE,),
}

DIVERGIU = (
    "O que estava na tela mudou depois da conferência. Confira de novo antes de criar a "
    "Retificação: a conferência abaixo é a de agora."
)


def _prefixo(texto):
    """ "a janela recursal" → "A janela recursal", para abrir frase."""
    return texto[:1].upper() + texto[1:]


def anotar_botoes(grupos, conteudo):
    """Dá a cada cartão de origem os botões do gesto — ou nenhum, sem outro Perfil (UX-110)."""
    quantos = len([p for p in conteudo.get("profiles") or [] if isinstance(p, dict)]) - 1
    for grupo in grupos:
        unidades = UNIDADES_DO_CARTAO.get(grupo.get("tipo"), ()) if quantos > 0 else ()
        grupo["gestos"] = [
            {
                "valor": f"{unidade}:{grupo['referencia']}",
                "rotulo": f"Aplicar {regra.NOME_DA_UNIDADE[unidade]} aos demais Perfis ({quantos})",
            }
            for unidade in unidades
        ]
    return grupos


@dataclass(frozen=True)
class Gesto:
    valor: str
    unidade: str
    grupo: dict
    mostrado: bool
    incluidos: frozenset
    impressao: str


def _identidades(caminho):
    return re.findall(r"id=([^/]+)", caminho or "")


def declarados(dados, grupos):
    """Os gestos que o envio declara, na ordem em que foram declarados, sem repetição.

    `aplicar` acrescenta um; `desfazer_gesto` retira um. O que não aponta cartão desta tela, ou
    aponta cartão de outra espécie, é envio forjado ou tela velha, e é descartado — nenhum caminho
    sai daqui sem ter sido gerado pelo servidor.
    """
    if dados is None:
        return []
    valores = list(dict.fromkeys(dados.getlist("gesto")))
    novo = dados.get("aplicar") or ""
    if novo and novo not in valores:
        valores.append(novo)
    desfeito = dados.get("desfazer_gesto") or ""
    por_referencia = {grupo["referencia"]: grupo for grupo in grupos}
    gestos = []
    for valor in valores:
        if valor == desfeito:
            continue
        unidade, _, referencia = valor.partition(":")
        grupo = por_referencia.get(referencia)
        if grupo is None or unidade not in UNIDADES_DO_CARTAO.get(grupo.get("tipo"), ()):
            continue
        gestos.append(
            Gesto(
                valor=valor,
                unidade=unidade,
                grupo=grupo,
                mostrado=bool(dados.get(f"gesto_mostrado:{valor}")),
                incluidos=frozenset(dados.getlist(f"gesto_destino:{valor}")),
                impressao=dados.get(f"gesto_impressao:{valor}") or "",
            )
        )
    return gestos


@dataclass(frozen=True)
class Calculado:
    gesto: Gesto
    efeitos: list
    incluidos: frozenset
    alteracoes: list
    origem: dict

    @property
    def divergiu(self):
        """Não foi mostrado, ou o que foi mostrado não é o de agora (FR-919)."""
        return not self.gesto.mostrado or self.gesto.impressao != regra.assinatura(self.efeitos)

    @property
    def sem_destino(self):
        """Há o que aplicar, e ninguém marcado: a pessoa desmarcou tudo e não desfez o gesto."""
        return not self.alteracoes and any(e.efeito in regra.APLICAVEIS for e in self.efeitos)


def _origem(gesto, proposto):
    perfil_id, *resto = _identidades(gesto.grupo["caminho"])
    perfil = next((p for p in proposto.get("profiles") or [] if str(p.get("id")) == perfil_id), {})
    origem = {"perfil": perfil_id, "codigo": perfil.get("code") or ""}
    if gesto.unidade in regra.UNIDADES_DO_MARCO:
        origem["marco"] = resto[0] if resto else ""
    if gesto.unidade == regra.MODALIDADE:
        modalidade = next(
            (
                m
                for m in perfil.get("competitionModalities") or []
                if resto and str(m.get("id")) == resto[0]
            ),
            {},
        )
        origem["modalidade"] = modalidade.get("code") or ""
    return origem, (resto[0] if resto else None)


def calcular(gestos, proposto, alterados, *, tem_resultado):
    """`(calculados, recusas)` — cada gesto sobre o conteúdo proposto, um depois do outro.

    As Alterações de um gesto entram no conjunto dos já alterados antes do seguinte: dois gestos
    sobre o mesmo campo de um Perfil não se somam (R-014). O gesto cuja origem não declara a unidade
    é recusado com a frase do domínio e sai da tela (R-013).
    """
    calculados, recusas = [], []
    acumuladas = list(alterados)
    for gesto in gestos:
        origem, alvo = _origem(gesto, proposto)
        try:
            efeitos = regra.efeitos(
                proposto,
                unidade=gesto.unidade,
                perfil=origem["perfil"],
                alvo=alvo,
                alterados=acumuladas,
                tem_resultado=tem_resultado,
            )
        except regra.SemOrigem as exc:
            recusas.append(str(exc))
            continue
        incluidos = (
            gesto.incluidos
            if gesto.mostrado
            else frozenset(e.perfil for e in efeitos if e.efeito in regra.APLICAVEIS)
        )
        alteracoes = regra.alteracoes_alcancadas(efeitos, incluidos)
        acumuladas.extend(alteracoes)
        calculados.append(Calculado(gesto, efeitos, incluidos, alteracoes, origem))
    return calculados, recusas


def registro(calculado):
    """`(detalhe, razão)` do gesto confirmado, no contrato do registro (R-016)."""
    destinos = [
        {"perfil": e.perfil, "codigo": e.codigo, "efeito": e.efeito, "impressao": e.impressao}
        for e in calculado.efeitos
        if e.efeito in regra.APLICAVEIS and e.perfil in calculado.incluidos
    ]
    origem = calculado.origem
    unidade = regra.NOME_DA_UNIDADE[calculado.gesto.unidade]
    de_onde = (
        f" {origem['modalidade']} do Perfil {origem['codigo']}"
        if origem.get("modalidade")
        else f" do Perfil {origem['codigo']}"
    )
    detalhe = {
        "etapa": "retificacao",
        "unidade": calculado.gesto.unidade,
        "origem": origem,
        "destinos": destinos,
    }
    return detalhe, f"Retificação — {unidade}{de_onde} aplicado(a) a {len(destinos)} Perfil(is)"


# ---- a conferência em palavras -------------------------------------------------------------------


def _apresentacao(conteudo):
    """`(coleção, campo) → (rótulo, tipo, opções)` — as palavras da própria tela de Retificação."""
    marcos = (
        tela.CAMPOS_MARCO
        + tela.CAMPOS_DA_FORMA_DA_ORDEM
        + tela.CAMPOS_DO_ARREDONDAMENTO
        + tela.CAMPOS_DA_JANELA
        + tela.CAMPOS_DO_NASCIMENTO_DO_CORTE
    )
    etapas = tuple(
        (str(etapa.get("id")), etapa.get("name") or "")
        for etapa in conteudo.get("stages") or []
        if isinstance(etapa, dict)
    )
    opcoes = {
        "orderProduction": tela.FORMAS_DA_ORDEM,
        "operation": tela.COMBINACOES,
        "normalization": tela.NORMALIZACOES,
        "rounding/mode": tela.MODOS_DE_ARREDONDAR,
        "appealWindow/unit": tela.UNIDADES_DO_PRAZO,
        "cutRule/targetKind": tela.ESPECIES_DO_ALVO,
        "cutRule/tieOutcome": tela.DESFECHOS_DO_EMPATE,
        "cutRule/continuation": tela.POLITICAS_DE_CONTINUACAO,
        "cutRule/governedStage": (tela.SEM_ETAPA_GOVERNADA, *etapas),
        "callForm": tela.FORMAS_DE_CONVOCACAO,
        "vacancyReversion/kind": tela.ESPECIES_DE_REVERSAO,
        "vacancyReversion": tela.ESPECIES_DE_REVERSAO,
    }
    rotulos = {}
    for colecao, lista in (
        (regra.MARCOS, marcos),
        (regra.PERFIS, tela.CAMPOS_PERFIL + tela.CAMPOS_DA_REVERSAO),
        (regra.MODALIDADES, tela.CAMPOS_MODALIDADE + tela.CAMPOS_REGRA),
    ):
        for campo, rotulo, tipo in lista:
            rotulos[(colecao, campo)] = (rotulo, tipo, opcoes.get(campo, ()))
    rotulos[(regra.MARCOS, "cutRule/targetCount")] = (
        "Alvo (só na quantidade fixa)",
        tela.INTEIRO,
        (),
    )
    rotulos[(regra.MARCOS, "stages")] = (
        tela.ROTULO_DO_EXCLUIDO[(regra.MARCOS, "stages")],
        "",
        etapas,
    )
    rotulos[(regra.MODALIDADES, "normativeRule/rounding")] = (
        tela.ROTULO_DO_EXCLUIDO[(regra.MODALIDADES, "normativeRule/rounding")],
        "",
        (),
    )
    rotulos[(regra.PERFIS, "vacancyReversion")] = (
        "Gatilho da reversão de vaga reservada",
        tela.REFERENCIA,
        tela.ESPECIES_DE_REVERSAO,
    )
    return rotulos, dict(etapas)


def _legivel(valor, tipo, opcoes):
    if valor is None or valor == "" or valor is regra._AUSENTE:
        return "nada declarado"
    if isinstance(valor, bool) or tipo == tela.BOOLEANO:
        return "Sim" if valor else "Não"
    if isinstance(valor, list):
        nomes = dict(opcoes)
        return ", ".join(nomes.get(str(item), str(item)) for item in valor) or "nenhuma"
    if isinstance(valor, dict):
        return tela.objeto_legivel(valor) or "declarado fora da lista"
    return dict(opcoes).get(str(valor), str(valor))


def _criterios_em_palavras(criterios, conteudo, etapas):
    fatos = {
        str(fato.get("id")): fato.get("label") or fato.get("code") or ""
        for perfil in conteudo.get("profiles") or []
        for fato in perfil.get("declaredFacts") or []
    }
    tipos = dict(tela.TIPOS_DE_CRITERIO)
    partes = []
    for criterio in criterios or []:
        parametros = criterio.get("parameters") or {}
        alvo = etapas.get(str(parametros.get("stageId")), "") or fatos.get(
            str(parametros.get("factId")), ""
        )
        partes.append(
            f"{criterio.get('order')} — {tipos.get(criterio.get('type'), criterio.get('type'))}"
            + (f": {alvo}" if alvo else "")
        )
    return "; ".join(partes) or "nenhum"


def _mudancas(efeito, conteudo, rotulos, etapas):
    linhas = []
    for colecao, campo, antes, depois in efeito.mudancas:
        if campo == "tiebreakers":
            linhas.append(
                (
                    "Critérios de desempate",
                    _criterios_em_palavras(antes, conteudo, etapas),
                    _criterios_em_palavras(depois, conteudo, etapas),
                )
            )
            continue
        if colecao == regra.MODALIDADES and campo == "":
            regra_normativa = depois.get("normativeRule") or {}
            percentual = (
                f"; {regra_da_composicao._percentual(regra_normativa.get('percentage'))}%"
                if regra_normativa.get("percentage")
                else ""
            )
            linhas.append(
                ("Acréscimo", "—", f"{depois.get('code')} — {depois.get('name')}{percentual}")
            )
            continue
        if campo == "generalCompetitionModalityId":
            linhas.append(
                (
                    "Ampla concorrência do Perfil",
                    antes or "nenhuma Modalidade",
                    depois or "nenhuma Modalidade",
                )
            )
            continue
        rotulo, tipo, opcoes = rotulos.get((colecao, campo), (campo, "", ()))
        linhas.append(
            (
                rotulo,
                "—" if antes is None else _legivel(antes, tipo, opcoes),
                _legivel(depois, tipo, opcoes),
            )
        )
    return linhas


def _motivo(efeito, rotulos):
    if not efeito.campo_fora:
        return efeito.motivo
    colecao, campo, antes, depois = efeito.campo_fora
    _rotulo, tipo, opcoes = rotulos.get((colecao, campo), (campo, "", ()))
    return (
        f"{efeito.motivo} (aqui: {_legivel(antes, tipo, opcoes)}; na origem: "
        f"{_legivel(depois, tipo, opcoes)})"
    )


def _titulo(calculado):
    origem = calculado.origem
    unidade = _prefixo(regra.NOME_DA_UNIDADE[calculado.gesto.unidade])
    if origem.get("modalidade"):
        return f"{unidade} {origem['modalidade']}, do Perfil {origem['codigo']}, aos demais Perfis"
    return f"{unidade} do Perfil {origem['codigo']} aos demais Perfis"


def rotulo(calculado):
    """Como a recusa nomeia o gesto: pelo título do bloco dele na conferência."""
    return _titulo(calculado)


def blocos(calculados, conteudo):
    """O que a conferência desenha para cada gesto (FR-916, FR-918, UX-111 a UX-113)."""
    rotulos, etapas = _apresentacao(conteudo)
    resultado = []
    for calculado in calculados:
        linhas = []
        for efeito in calculado.efeitos:
            aplicavel = efeito.efeito in regra.APLICAVEIS
            linhas.append(
                {
                    "perfil": efeito.perfil,
                    "codigo": efeito.codigo,
                    "denominacao": efeito.denominacao,
                    "efeito_em_palavras": aplicacao_da_composicao.EFEITO_EM_PALAVRAS[efeito.efeito],
                    "motivo": _motivo(efeito, rotulos),
                    "aplicavel": aplicavel,
                    "marcado": aplicavel and efeito.perfil in calculado.incluidos,
                    "mudancas": _mudancas(efeito, conteudo, rotulos, etapas) if aplicavel else [],
                    "quantidade_fixa": efeito.quantidade_fixa,
                    "ja_declara": ", ".join(efeito.ja_declara) or "nenhuma",
                    "mostra_ja_declara": calculado.gesto.unidade == regra.MODALIDADE,
                }
            )
        contagem = {
            chave: sum(1 for e in calculado.efeitos if e.efeito == chave)
            for chave in aplicacao_da_composicao.EFEITO_EM_PALAVRAS
        }
        resultado.append(
            {
                "valor": calculado.gesto.valor,
                "titulo": _titulo(calculado),
                "frase": aplicacao_da_composicao._frase_do_alcance(contagem),
                "linhas": linhas,
                "alteracoes": len(calculado.alteracoes),
                "impressao": regra.assinatura(calculado.efeitos),
            }
        )
    return resultado


# ---- as consequências do ato (FR-941, R-015) ----------------------------------------------------


def _por_id(itens):
    return {str(item.get("id")): item for item in itens or [] if isinstance(item, dict)}


def consequencias(edital, vigente, resultante):
    """O que o ato provoca além do conteúdo: `[frase]`, na ordem dos Perfis.

    As perguntas são as das telas de condução, lidas de onde elas as leem — a regra do marco que a
    ordem cita, o ato vigente de cada recorte, o histórico de divulgação —, e só para o marco que o
    ato alcança: uma leitura por marco, e nenhuma por participante.
    """
    from processo_seletivo.classificacao.application.selectors import ato_vigente
    from processo_seletivo.classificacao.domain.universo import recorte_da_regra
    from processo_seletivo.divulgacao.application.selectors import historico_do_marco
    from processo_seletivo.interface.supervisao import listas_do_marco

    frases = []
    perfis_de_antes = _por_id(vigente.get("profiles"))
    for perfil in resultante.get("profiles") or []:
        antes = perfis_de_antes.get(str(perfil.get("id")))
        if antes is None:
            continue
        marcos_de_antes = _por_id(antes.get("classificationMilestones"))
        com_ordem = []
        for marco in perfil.get("classificationMilestones") or []:
            anterior = marcos_de_antes.get(str(marco.get("id")))
            if anterior is None:
                continue
            nome = marco.get("name") or marco.get("code") or ""
            ids = {"perfil_id": perfil.get("id"), "marco_id": marco.get("id")}
            regra_mudou = recorte_da_regra(vigente, **ids) != recorte_da_regra(resultante, **ids)
            janela_mudou = (anterior.get("appealWindow") or None) != (
                marco.get("appealWindow") or None
            )
            nova_reservada = _modalidades_reservadas_novas(antes, perfil)
            if not (regra_mudou or janela_mudou or nova_reservada):
                continue
            tem_ato = any(
                ato_vigente(edital=edital, marco_id=marco.get("id"), lista_id=lista)
                for lista, _ in listas_do_marco(antes, anterior, vigente)
            )
            if tem_ato:
                com_ordem.append(nome)
            if regra_mudou and tem_ato:
                frases.append(
                    f"A ordem emitida do marco {nome}, do Perfil {perfil.get('code')}, fica "
                    "obsoleta: a regra que ela cita muda, e ela terá de ser emitida de novo."
                )
            if janela_mudou and any(
                linha["vigente"]
                for linha in historico_do_marco(edital=edital, marco_id=marco.get("id"))
            ):
                frases.append(
                    f"O marco {nome}, do Perfil {perfil.get('code')}, já tem resultado divulgado, "
                    f"e a janela recursal dele muda: {_janela(anterior)} → {_janela(marco)}."
                )
        for codigo in _modalidades_reservadas_novas(antes, perfil):
            if com_ordem:
                frases.append(
                    f"O recorte da Modalidade {codigo}, que nasce no Perfil {perfil.get('code')}, "
                    f"nasce sem ordem: o marco {com_ordem[0]} já tem ordem emitida nos outros."
                )
    return frases


def _janela(marco):
    janela = marco.get("appealWindow")
    return tela.objeto_legivel(janela) if isinstance(janela, dict) else "sem janela"


def _modalidades_reservadas_novas(antes, depois):
    ja = set(_por_id(antes.get("competitionModalities")))
    ampla = str(depois.get("generalCompetitionModalityId") or "")
    return [
        modalidade.get("code") or ""
        for modalidade in depois.get("competitionModalities") or []
        if str(modalidade.get("id")) not in ja and str(modalidade.get("id")) != ampla
    ]
