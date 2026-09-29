"""Aplicar uma declaração de um Perfil aos demais — a regra única da `DP-13` (051).

**Materialização, e não herança** (FR-910). Cada destino recebe um valor próprio, com identidade
própria, e nada guarda vínculo com a origem — como a cópia da `043`, que não registra de onde veio.
Herdar no conteúdo publicado faria uma Retificação do padrão alterar N Perfis sem dizer.

**A regra, uma só.** Nos destinos selecionados, o gesto substitui integralmente a declaração
correspondente, na fronteira de cada unidade; se ela não existir e puder nascer, nasce uma cópia
independente; e o destino fica fora do alcance quando não há correspondente inequívoco (FR-911). O
marco inteiro nunca é substituído: ele só nasce onde falta (FR-912).

**Função pura, pela razão do duplicar.** É aqui que a feature erra em silêncio se errar: um critério
que continue apontando o fato da origem é coerente com os vizinhos e atravessa a gravação — e o
LP02 publicaria desempate pela data de nascimento declarada no LP01. A diferença para o duplicar é
que o destino já existe: a referência a fato é achada **pelo código e pelo tipo** no destino, e não
remapeada para uma identidade nova (`DP-13`, fato 3).

**O que este módulo não decide.** Quem aplica, onde a prévia aparece e como se grava. Ele devolve,
por destino, um de quatro efeitos e o valor que seria gravado; a tela mostra, e a confirmação grava
pelo caminho de sempre da etapa (`D-001` da spec).
"""

import copy
import hashlib
import json
import uuid
from dataclasses import dataclass, field

from processo_seletivo.editais.domain import marcos as regras_do_marco
from processo_seletivo.editais.domain.perfis import listas_reservadas

NASCE = "NASCE"
SUBSTITUI = "SUBSTITUI"
SEM_MUDANCA = "SEM_MUDANCA"
FORA = "FORA"

#: Os efeitos que a confirmação pode aplicar. `SEM_MUDANCA` não grava nada, e `FORA` nunca é tocado.
APLICAVEIS = frozenset({NASCE, SUBSTITUI})


@dataclass(frozen=True)
class Efeito:
    """O que o gesto faria num Perfil destino. Não é gravado: é a prévia (FR-916).

    `antes` e `depois` são a unidade no destino, na forma do formulário da etapa — o que a tela
    precisa para dizer o *antes → depois* com as frases da Revisão. `impressao` é o resumo da
    unidade como ficaria, na grafia normalizada: é o que o registro do gesto guarda, e o que a
    Revisão compara depois para saber se o valor ainda é o gravado (FR-935).
    """

    perfil: str
    codigo: str
    denominacao: str
    efeito: str
    motivo: str = ""
    antes: object = None
    depois: object = None
    impressao: str = ""
    #: `(anterior, aplicada)` quando a unidade traz corte de quantidade fixa (FR-917).
    quantidade_fixa: tuple | None = None
    #: Para a Modalidade: as que o destino já declara, pelo código (FR-924).
    ja_declara: tuple = field(default_factory=tuple)
    #: Para a Modalidade: a ampla do destino, antes e depois, pelo código (FR-925).
    ampla: tuple | None = None


def impressao(unidade) -> str:
    """O resumo estável de uma unidade normalizada. Mesma unidade, mesma impressão."""
    return hashlib.sha256(
        json.dumps(unidade, sort_keys=True, default=str, ensure_ascii=False).encode()
    ).hexdigest()


def assinatura(efeitos) -> str:
    """A impressão da prévia inteira — o que a confirmação precisa reencontrar (FR-919).

    Cobre todos os destinos, e não só os marcados: um destino que passou de *fora do alcance* para
    *substitui* entre a prévia e a confirmação é uma divergência, mesmo que ninguém o tenha marcado.
    """
    return impressao([(item.perfil, item.efeito, item.impressao, item.motivo) for item in efeitos])


def alcancados(efeitos, incluidos):
    """Os efeitos que a confirmação aplica: marcados e aplicáveis (FR-918)."""
    incluidos = {str(item) for item in incluidos}
    return [item for item in efeitos if item.efeito in APLICAVEIS and item.perfil in incluidos]


# ---- o marco ------------------------------------------------------------------------------------


def _fatos(perfil):
    return {
        str(fato.get("id")): fato
        for fato in perfil.get("declaredFacts") or []
        if isinstance(fato, dict)
    }


def metodo_proprio(marco) -> bool:
    """O marco declara método **próprio** de sorteio, que governa a ordem dele?

    O método guardado num marco de pontuação não conta: ele é preservado para o caso de a forma
    voltar a ser sorteio (030, FR-418), e não é publicado (`_metodo_publicado`).
    """
    declarado = bool(marco.get("drawMethod"))
    return declarado and regras_do_marco.ordena_por_sorteio(
        marco.get("orderProduction") or "", metodo_declarado=declarado
    )


def _corte_normalizado(regra):
    if not regra:
        return None
    especie = regra.get("targetKind") or ""
    return {
        "targetKind": especie,
        "targetCount": regra.get("targetCount") if especie == "FIXED" else None,
        "surplusCount": int(regra.get("surplusCount") or 0),
        "tieOutcome": regra.get("tieOutcome") or "",
        "governedStage": regra.get("governedStage") or "",
        "continuation": regra.get("continuation") or "",
    }


def _janela_normalizada(janela):
    if not janela:
        return None
    return {
        "admits": bool(janela.get("admits")),
        "durationDays": janela.get("durationDays"),
        "unit": janela.get("unit") or "DIAS_CORRIDOS",
    }


def _escala(valor):
    if valor in (None, ""):
        return None
    try:
        return int(valor)
    except (TypeError, ValueError):
        return valor


def _criterio_normalizado(criterio, fatos):
    """O critério sem identidade, com o fato dito pelo código e pelo tipo, e não pela identidade.

    É a grafia em que dois Perfis podem declarar **o mesmo** critério: a identidade do fato é de
    cada Perfil, e o código é o que o Edital escreve.
    """
    parametros = criterio.get("parameters") or {}
    if parametros.get("stageId"):
        alvo = ["etapa", str(parametros["stageId"])]
    elif parametros.get("factId"):
        fato = fatos.get(str(parametros["factId"])) or {}
        alvo = ["fato", fato.get("code") or "", fato.get("type") or ""]
    else:
        alvo = []
    return {
        "order": criterio.get("order"),
        "type": criterio.get("type") or "",
        "alvo": alvo,
        "whenMissing": criterio.get("whenMissing") or "",
    }


def unidade_do_marco(marco, perfil):
    """A unidade que o gesto leva: o marco sem a identidade (FR-922).

    Sem `id`, `code` e `name` — que são do destino (FR-913) —, e sem o método do sorteio, que não
    viaja: marco com método próprio fica fora do alcance, e o guardado em marco de pontuação é do
    destino.
    """
    fatos = _fatos(perfil)
    arredondamento = marco.get("rounding") or {}
    return {
        "orderProduction": marco.get("orderProduction") or "",
        "stages": sorted(str(item) for item in marco.get("stages") or []),
        "operation": marco.get("operation") or "",
        "normalization": marco.get("normalization") or "",
        "rounding": {
            "scale": _escala(arredondamento.get("scale")),
            "mode": arredondamento.get("mode") or "",
        },
        "appealWindow": _janela_normalizada(marco.get("appealWindow")),
        "cutRule": _corte_normalizado(marco.get("cutRule")),
        "tiebreakers": sorted(
            (_criterio_normalizado(item, fatos) for item in marco.get("tiebreakers") or []),
            key=lambda item: (item["order"] is None, item["order"] or 0),
        ),
    }


def _criterios_no_destino(origem_marco, origem_perfil, destino):
    """Os critérios da origem reescritos para o destino — ou o código do fato que falta.

    Devolve `(criterios, None)` ou `(None, motivo)`. O fato é achado pelo **código e pelo tipo**
    (FR-914): um `NASC` numérico no destino não é o `NASC` de data da origem, e casá-los inverteria
    o sentido de "maior idade".
    """
    fatos_da_origem = _fatos(origem_perfil)
    do_destino = {
        (fato.get("code"), fato.get("type")): str(fato.get("id"))
        for fato in destino.get("declaredFacts") or []
        if isinstance(fato, dict)
    }
    criterios = []
    for criterio in origem_marco.get("tiebreakers") or []:
        parametros = dict(criterio.get("parameters") or {})
        if parametros.get("factId"):
            fato = fatos_da_origem.get(str(parametros["factId"])) or {}
            chave = (fato.get("code"), fato.get("type"))
            if chave not in do_destino:
                return None, (
                    f"não declara o fato {fato.get('code') or '—'} "
                    f"({_TIPO_DO_FATO.get(fato.get('type'), fato.get('type') or 'sem tipo')}), "
                    "que um critério de desempate compara"
                )
            parametros = {"factId": do_destino[chave]}
        criterios.append({**copy.deepcopy(criterio), "parameters": parametros})
    return criterios, None


_TIPO_DO_FATO = {"DATA": "data", "INTEIRO": "número inteiro"}


def _marco_no_destino(origem_marco, criterios, *, base, nova):
    """O marco da origem vestido com a identidade `base` — o existente no destino, ou a nascente."""
    novo = {
        **copy.deepcopy(origem_marco),
        "id": base["id"],
        "code": base["code"],
        "name": base["name"],
        # O método próprio não viaja; o guardado no destino, se houver, é dele (FR-922).
        "drawMethod": copy.deepcopy(base.get("drawMethod")) if base.get("drawMethod") else None,
    }
    novo["tiebreakers"] = [{**item, "id": str(nova())} for item in criterios]
    return novo


def efeitos_do_marco(perfis, *, origem, sub, nova=uuid.uuid4):
    """Um `Efeito` por Perfil que não é a origem, para o marco `sub` do Perfil `origem`.

    `perfis` está na forma da etapa: cada Perfil com `classificationMilestones` (o digitado) e
    `declaredFacts`. Levanta `LookupError` se a origem não existe — pedido forjado, e não prévia.
    """
    origem = str(origem)
    origem_perfil = next((item for item in perfis if str(item.get("id")) == origem), None)
    marcos_da_origem = (origem_perfil or {}).get("classificationMilestones") or []
    try:
        origem_marco = marcos_da_origem[int(sub)]
    except (IndexError, ValueError, TypeError):
        raise LookupError("marco de origem inexistente") from None

    proprio_na_origem = metodo_proprio(origem_marco)
    efeitos = []
    for perfil in perfis:
        identidade = str(perfil.get("id"))
        if identidade == origem:
            continue
        comum = {
            "perfil": identidade,
            "codigo": perfil.get("code") or "",
            "denominacao": perfil.get("name") or "",
        }
        existentes = perfil.get("classificationMilestones") or []
        if proprio_na_origem:
            efeitos.append(
                Efeito(
                    **comum,
                    efeito=FORA,
                    motivo=(
                        "o marco de origem declara método próprio de sorteio, que existe para "
                        "divergir e não é levado a outro Perfil"
                    ),
                )
            )
            continue
        if len(existentes) > 1:
            efeitos.append(
                Efeito(
                    **comum,
                    efeito=FORA,
                    motivo=(
                        f"tem {len(existentes)} marcos, e não há como saber qual deles corresponde"
                    ),
                )
            )
            continue
        if existentes and metodo_proprio(existentes[0]):
            efeitos.append(
                Efeito(
                    **comum,
                    efeito=FORA,
                    motivo="o marco dele declara método próprio de sorteio",
                )
            )
            continue
        criterios, falta = _criterios_no_destino(origem_marco, origem_perfil, perfil)
        if falta:
            efeitos.append(Efeito(**comum, efeito=FORA, motivo=falta))
            continue
        if existentes:
            atual = existentes[0]
            base = atual
        else:
            atual = None
            codigo, nome = regras_do_marco.identidade_derivada(
                codigo_do_perfil=perfil.get("code"), nome_do_perfil=perfil.get("name")
            )
            base = {"id": str(nova()), "code": codigo, "name": nome}
        depois = _marco_no_destino(origem_marco, criterios, base=base, nova=nova)
        unidade_depois = unidade_do_marco(depois, perfil)
        if atual is not None and unidade_do_marco(atual, perfil) == unidade_depois:
            efeitos.append(
                Efeito(
                    **comum,
                    efeito=SEM_MUDANCA,
                    antes=atual,
                    depois=atual,
                    impressao=impressao(unidade_depois),
                )
            )
            continue
        if (
            atual is not None
            and unidade_do_marco(atual, perfil)["tiebreakers"] == (unidade_depois["tiebreakers"])
        ):
            # Lista idêntica não gera alteração (FR-923): os critérios do destino ficam, com a
            # identidade que já têm.
            depois["tiebreakers"] = copy.deepcopy(atual.get("tiebreakers") or [])
        efeitos.append(
            Efeito(
                **comum,
                efeito=SUBSTITUI if atual is not None else NASCE,
                antes=atual,
                depois=depois,
                impressao=impressao(unidade_depois),
                quantidade_fixa=_quantidade_fixa(atual, depois),
            )
        )
    return efeitos


def _quantidade_fixa(antes, depois):
    """`(anterior, aplicada)` quando o corte aplicado é de quantidade fixa (FR-917).

    A regra única leva a quantidade junto, e a compensação é a prévia a destacar: ela depende das
    vagas do Perfil, e propagá-la iguala Perfis que podem diferir de propósito (`DP-13`).
    """
    corte = (depois or {}).get("cutRule") or {}
    if corte.get("targetKind") != "FIXED":
        return None
    anterior = (antes or {}).get("cutRule") or {}
    return (
        anterior.get("targetCount") if anterior.get("targetKind") == "FIXED" else None,
        corte.get("targetCount"),
    )


def aplicar_marcos(perfis, efeitos, incluidos):
    """Os Perfis com o marco aplicado nos destinos alcançados. Não altera `perfis`."""
    por_perfil = {item.perfil: item for item in alcancados(efeitos, incluidos)}
    resultado = []
    for perfil in perfis:
        efeito = por_perfil.get(str(perfil.get("id")))
        if efeito is None:
            resultado.append(perfil)
            continue
        resultado.append({**perfil, "classificationMilestones": [copy.deepcopy(efeito.depois)]})
    return resultado


# ---- a Modalidade, pelo código ------------------------------------------------------------------


#: Os campos da regra normativa que a composição declara, e que por isso a unidade leva (FR-924). Os
#: opacos — `calculation`, `distribution`, `callRules` — ficam com o destino: a tela não os pede, e
#: levá-los seria materializar o que ninguém viu.
CAMPOS_DA_REGRA = ("foundation", "version", "percentage", "rounding")


def _campo_da_regra(regra, campo):
    """O campo da regra da origem, com o vazio de cada tipo: `rounding` é objeto, os demais não."""
    valor = copy.deepcopy(regra.get(campo))
    if valor is None and campo == "rounding":
        return {}
    return valor


def _regra_normalizada(regra):
    if not regra:
        return None
    return {
        campo: regra.get(campo) or ({} if campo == "rounding" else "") for campo in CAMPOS_DA_REGRA
    }


def unidade_da_modalidade(modalidade, perfil):
    """A Modalidade sem a identidade, com a declaração da ampla (FR-924, FR-925)."""
    ampla = perfil.get("generalCompetitionModalityId")
    return {
        "code": modalidade.get("code") or "",
        "name": modalidade.get("name") or "",
        "description": modalidade.get("description") or "",
        "normativeRule": _regra_normalizada(modalidade.get("normativeRule")),
        "ampla": bool(ampla) and str(ampla) == str(modalidade.get("id")),
    }


def _codigo_da_ampla(perfil):
    ampla = perfil.get("generalCompetitionModalityId")
    for modalidade in perfil.get("competitionModalities") or []:
        if ampla and str(modalidade.get("id")) == str(ampla):
            return modalidade.get("code") or ""
    return ""


def efeitos_da_modalidade(perfis, *, origem, indice, nova=uuid.uuid4):
    """Um `Efeito` por Perfil que não é a origem, para a Modalidade `indice` do Perfil `origem`.

    `origem` é a posição do Perfil na lista, e não a identidade: na etapa Perfis o destino pode ser
    um Perfil que ainda não foi gravado, e a tela o conhece pela posição.

    O código é a correspondência, e ele é único no Perfil (`uq_modalidade_perfil_code`): nunca há
    dois candidatos. A Modalidade equivalente sob outro código não é reconhecida — casar nome é o
    que a `R-006` da `025` recusa —, e só a prévia a protege, listando o que cada destino já tem.
    """
    try:
        origem_perfil = perfis[int(origem)]
        modalidade = (origem_perfil.get("competitionModalities") or [])[int(indice)]
    except (IndexError, ValueError, TypeError):
        raise LookupError("Modalidade de origem inexistente") from None
    codigo = modalidade.get("code") or ""
    if not codigo:
        raise LookupError("Modalidade de origem sem código")
    origem_e_a_ampla = unidade_da_modalidade(modalidade, origem_perfil)["ampla"]

    efeitos = []
    for posicao, perfil in enumerate(perfis):
        if posicao == int(origem):
            continue
        comum = {
            "perfil": str(posicao),
            "codigo": perfil.get("code") or "",
            "denominacao": perfil.get("name") or "",
        }
        existentes = perfil.get("competitionModalities") or []
        ja_declara = tuple(item.get("code") or "" for item in existentes)
        atual = next((item for item in existentes if item.get("code") == codigo), None)
        if atual is not None:
            regra_atual = atual.get("normativeRule") or {}
            regra_da_origem = modalidade.get("normativeRule")
            depois = {
                **copy.deepcopy(atual),
                "name": modalidade.get("name") or "",
                "description": modalidade.get("description") or "",
                "normativeRule": (
                    {
                        **copy.deepcopy(regra_atual),
                        **{
                            campo: _campo_da_regra(regra_da_origem, campo)
                            for campo in CAMPOS_DA_REGRA
                        },
                        "id": regra_atual.get("id") or str(nova()),
                    }
                    if regra_da_origem
                    else None
                ),
            }
        else:
            regra_da_origem = modalidade.get("normativeRule")
            depois = {
                **copy.deepcopy(modalidade),
                "id": str(nova()),
                "normativeRule": (
                    {
                        **{
                            campo: _campo_da_regra(regra_da_origem, campo)
                            for campo in CAMPOS_DA_REGRA
                        },
                        "id": str(nova()),
                    }
                    if regra_da_origem
                    else None
                ),
            }
        ampla_antes = _codigo_da_ampla(perfil)
        if origem_e_a_ampla:
            ampla_depois = codigo
        elif ampla_antes == codigo:
            ampla_depois = ""
        else:
            ampla_depois = ampla_antes
        perfil_depois = {
            **perfil,
            "generalCompetitionModalityId": depois["id"]
            if ampla_depois == codigo
            else (None if ampla_depois == "" else perfil.get("generalCompetitionModalityId")),
        }
        unidade_depois = unidade_da_modalidade(depois, perfil_depois)
        mudou_a_ampla = ampla_antes != ampla_depois
        if atual is not None and unidade_da_modalidade(atual, perfil) == unidade_depois:
            efeitos.append(
                Efeito(
                    **comum,
                    efeito=SEM_MUDANCA,
                    antes=atual,
                    depois=atual,
                    impressao=impressao(unidade_depois),
                    ja_declara=ja_declara,
                )
            )
            continue
        efeitos.append(
            Efeito(
                **comum,
                efeito=SUBSTITUI if atual is not None else NASCE,
                antes=atual,
                depois=depois,
                impressao=impressao(unidade_depois),
                ja_declara=ja_declara,
                ampla=(ampla_antes, ampla_depois) if mudou_a_ampla else None,
            )
        )
    return efeitos


def aplicar_modalidades(perfis, efeitos, incluidos):
    """Os Perfis com a Modalidade aplicada. Nunca remove Modalidade nem toca o quadro (FR-924)."""
    por_posicao = {item.perfil: item for item in alcancados(efeitos, incluidos)}
    resultado = []
    for posicao, perfil in enumerate(perfis):
        efeito = por_posicao.get(str(posicao))
        if efeito is None:
            resultado.append(perfil)
            continue
        modalidades = [copy.deepcopy(item) for item in perfil.get("competitionModalities") or []]
        depois = copy.deepcopy(efeito.depois)
        trocada = False
        for lugar, item in enumerate(modalidades):
            if item.get("code") == depois.get("code"):
                modalidades[lugar] = depois
                trocada = True
        if not trocada:
            modalidades.append(depois)
        novo = {**perfil, "competitionModalities": modalidades}
        if efeito.ampla is not None:
            _, ampla_depois = efeito.ampla
            novo["generalCompetitionModalityId"] = (
                depois["id"] if ampla_depois == depois.get("code") else None
            )
        resultado.append(novo)
    return resultado


# ---- os valores do Perfil que o Edital declara uma vez -------------------------------------------


#: Os valores do Perfil que o controle do Edital aplica (FR-926), e como cada um se lê.
CAMPOS_DO_PERFIL = ("callForm", "vacancyReversion")


def valor_do_campo(perfil, campo):
    valor = perfil.get(campo)
    if campo == "vacancyReversion":
        return ((valor or {}).get("kind") or "") if isinstance(valor, dict) else (valor or "")
    return valor or ""


def efeitos_do_campo_do_perfil(perfis, *, campo, valor):
    """Um `Efeito` por Perfil, para o valor que o controle do Edital declara.

    Não há origem: o valor é do Edital, e todo Perfil é destino. A reversão pressupõe lista
    reservada (016, FR-251), e o Perfil sem ela fica fora do alcance — a validação já a recusa ali.
    """
    if campo not in CAMPOS_DO_PERFIL:
        raise LookupError(f"campo do Perfil não aplicável: {campo}")
    valor = valor or ""
    efeitos = []
    for posicao, perfil in enumerate(perfis):
        comum = {
            "perfil": str(posicao),
            "codigo": perfil.get("code") or "",
            "denominacao": perfil.get("name") or "",
        }
        antes = valor_do_campo(perfil, campo)
        if campo == "vacancyReversion" and valor and not listas_reservadas(perfil):
            efeitos.append(
                Efeito(
                    **comum,
                    efeito=FORA,
                    motivo="não declara lista reservada, e a reversão só existe onde há uma",
                )
            )
            continue
        if antes == valor:
            efeito = SEM_MUDANCA
        elif not antes:
            efeito = NASCE
        else:
            efeito = SUBSTITUI
        efeitos.append(
            Efeito(
                **comum,
                efeito=efeito,
                antes=antes,
                depois=valor,
                impressao=impressao({campo: valor}),
            )
        )
    return efeitos


def aplicar_campo_do_perfil(perfis, efeitos, incluidos, *, campo, valor):
    por_posicao = {item.perfil: item for item in alcancados(efeitos, incluidos)}
    resultado = []
    for posicao, perfil in enumerate(perfis):
        if str(posicao) not in por_posicao:
            resultado.append(perfil)
            continue
        if campo == "vacancyReversion":
            novo_valor = {"kind": valor} if valor else None
        else:
            novo_valor = valor or None
        resultado.append({**perfil, campo: novo_valor})
    return resultado


def valor_comum(perfis, campo):
    """O valor que **todos** os Perfis declaram iguais, ou `""` quando divergem ou faltam (FR-926).

    É o que o Perfil novo recebe, e o que o controle do Edital mostra: a forma de convocação *do
    Edital* não é campo do Edital (`D-003` da spec), e sim o que os Perfis dele concordam em dizer.
    """
    valores = {valor_do_campo(perfil, campo) for perfil in perfis}
    if len(valores) == 1:
        return next(iter(valores))
    return ""
