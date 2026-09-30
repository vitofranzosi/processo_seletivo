"""Aplicar a todos na Retificação — a regra da `DP-13`, traduzida em Alterações (051, US5).

**A mesma regra da composição**, e por isso reusada, e não reescrita: a correspondência pelo código,
o fato pelo código e pelo tipo, os quatro efeitos, a impressão e a assinatura moram em
`editais/domain/aplicacao`. O que este módulo acrescenta é o que só a Retificação tem: o conteúdo já
é norma publicada, e o gesto não grava valor — produz **Alterações**, campo a campo (FR-938).

**A leitura da `FR-802` da `048` que a `051` adota** (FR-942). A `FR-802` impede espécie nova e
genérica de Alteração, e o gesto não cria nenhuma. Cada destino recebe o que a tela de Retificação
já produz à mão: `REPLACE` de campo retificável; o nascimento, inteiro, do objeto que o contrato
deixa nascer (a janela, o corte, a reversão); e a remoção e o acréscimo de item às duas coleções que
a `048` nomeou (o critério de desempate e a Modalidade). Cada Alteração passa pelas guardas do ato
de sempre, e todas saem no mesmo ato — uma versão, um documento, o mesmo histórico (FR-795 da
`048`).
Uma interface em lote que produz Alterações já admitidas não é mecanismo novo de acréscimo.

**O contrato de mutabilidade é a única fonte do que se retifica** (FR-803 da `048`). Cada unidade só
enumera os seus campos; se um deles se retifica, quem responde é `mutabilidade.CONTRATO`. Basta um
campo não retificável diferente para o destino **inteiro** ficar fora, com o campo nomeado e a razão
que o contrato escreve (FR-939): aplicar o resto seria publicar num Perfil uma norma que não é a da
origem nem a dele.

**A ausência na origem não se aplica** (R-013). Na composição ela se aplica (FR-922), porque o
rascunho ainda não é norma; aqui, retirar de N Perfis uma declaração publicada — o prazo de recurso,
a forma de convocação — não é a correção que o gesto existe para fazer.

**Função pura.** O conteúdo que entra é o **proposto** — o vigente com as Alterações que a pessoa
já digitou neste ato —, porque é dele que sai o valor da origem: quem corrige o prazo no primeiro
marco pede para aplicar **aquele** prazo. O que depende do banco — se a Etapa já tem Resultado —
chega como função.
"""

import copy
from dataclasses import dataclass, field, replace
from decimal import Decimal, InvalidOperation
from uuid import NAMESPACE_URL, uuid5

from processo_seletivo.classificacao.domain import faixa
from processo_seletivo.editais.domain import aplicacao as regra
from processo_seletivo.editais.domain import mutabilidade
from processo_seletivo.editais.domain.perfis import listas_reservadas

NASCE, SUBSTITUI, SEM_MUDANCA, FORA = regra.NASCE, regra.SUBSTITUI, regra.SEM_MUDANCA, regra.FORA
APLICAVEIS = regra.APLICAVEIS

JANELA = "janela"
CORTE = "corte"
CRITERIOS = "criterios"
CAMPOS_DO_MARCO = "campos_do_marco"
FORMA_DE_CONVOCACAO = "callForm"
REVERSAO = "vacancyReversion"
MODALIDADE = "modalidade"

#: As unidades da `FR-938`, pelo cartão em que o gesto nasce (R-012).
UNIDADES_DO_MARCO = (JANELA, CORTE, CRITERIOS, CAMPOS_DO_MARCO)
UNIDADES_DO_PERFIL = (FORMA_DE_CONVOCACAO, REVERSAO)
UNIDADES = (*UNIDADES_DO_MARCO, *UNIDADES_DO_PERFIL, MODALIDADE)

#: O que cada unidade é numa frase — o botão, a conferência, a trilha e as recusas.
NOME_DA_UNIDADE = {
    JANELA: "a janela recursal",
    CORTE: "a regra de corte",
    CRITERIOS: "os critérios de desempate",
    CAMPOS_DO_MARCO: "a forma da ordem, a combinação e o arredondamento",
    FORMA_DE_CONVOCACAO: "a forma de convocação",
    REVERSAO: "a reversão de vaga reservada",
    MODALIDADE: "a Modalidade",
}

MARCOS = "classificationMilestones"
MODALIDADES = "competitionModalities"
PERFIS = "profiles"

CAMPOS_DA_JANELA = ("appealWindow/admits", "appealWindow/durationDays", "appealWindow/unit")
CAMPOS_DO_CORTE = (
    "cutRule/targetKind",
    "cutRule/targetCount",
    "cutRule/surplusCount",
    "cutRule/tieOutcome",
    "cutRule/governedStage",
    "cutRule/continuation",
)
#: Os campos do marco fora da janela, do corte e dos critérios — os da `FR-922` que sobram. As
#: Etapas entram, e não se retificam: é o caso da `US5`, cenário 2, em que o destino inteiro sai.
CAMPOS_DO_MARCO_PROPRIOS = (
    "orderProduction",
    "stages",
    "operation",
    "normalization",
    "rounding/scale",
    "rounding/mode",
)
#: A Modalidade como a composição a declara (FR-924): os opacos da regra ficam com o destino.
CAMPOS_DA_MODALIDADE = ("name", "description")
CAMPOS_DA_REGRA = (
    "normativeRule/foundation",
    "normativeRule/version",
    "normativeRule/percentage",
    "normativeRule/rounding",
)

#: Como cada campo se diz no motivo de quem fica fora. Só o que o motivo precisa nomear; o rótulo
#: da tela, com os valores por extenso, é da interface.
NOME_DO_CAMPO = {
    (MARCOS, "orderProduction"): "a forma da ordem",
    (MARCOS, "stages"): "as Etapas que o marco mede",
    (MARCOS, "operation"): "a combinação das pontuações",
    (MARCOS, "normalization"): "a normalização",
    (MARCOS, "rounding/scale"): "as casas decimais da pontuação",
    (MARCOS, "rounding/mode"): "o modo de arredondar",
    (MARCOS, "cutRule/targetKind"): "a espécie do alvo do corte",
    (MARCOS, "cutRule/governedStage"): "a Etapa que o corte alimenta",
    (MARCOS, "cutRule/continuation"): "a continuação além da faixa",
    (MODALIDADES, "normativeRule/rounding"): "o arredondamento da reserva",
}

_AUSENTE = object()


class SemOrigem(LookupError):
    """A origem não existe, ou não declara a unidade. A mensagem é a recusa, por extenso."""


@dataclass(frozen=True)
class Efeito:
    """O que o gesto faz num Perfil destino da Retificação. Não é gravado: é a conferência.

    `alteracoes` são as Alterações Normativas que o destino recebe — só das espécies que a tela já
    produz (FR-938). `mudancas` são `(coleção, campo, antes, depois)`, o que a conferência diz com
    os rótulos da tela. `campo_fora` é `(coleção, campo, antes, depois)` quando quem deixa o destino
    fora é o contrato (FR-939): a interface o diz com os valores por extenso.
    """

    perfil: str
    codigo: str
    denominacao: str
    efeito: str
    motivo: str = ""
    alteracoes: tuple = ()
    mudancas: tuple = ()
    impressao: str = ""
    quantidade_fixa: tuple | None = None
    ja_declara: tuple = field(default_factory=tuple)
    campo_fora: tuple | None = None


@dataclass(frozen=True)
class _Resultado:
    efeito: str
    motivo: str = ""
    alteracoes: tuple = ()
    mudancas: tuple = ()
    territorio: tuple = ()
    quantidade_fixa: tuple | None = None
    ja_declara: tuple = ()
    campo_fora: tuple | None = None
    #: O código da Modalidade que nasce — o acréscimo digitado da mesma Modalidade é o mesmo campo.
    codigo_que_nasce: str = ""


def _fora(motivo, **extra):
    return _Resultado(efeito=FORA, motivo=motivo, **extra)


def alteracoes_alcancadas(efeitos, incluidos):
    """As Alterações que a confirmação leva ao ato: dos destinos marcados e aplicáveis (FR-918)."""
    return [
        alteracao for item in regra.alcancados(efeitos, incluidos) for alteracao in item.alteracoes
    ]


def assinatura(efeitos):
    """A impressão da conferência inteira: o que *Criar Retificação* reencontra (FR-919)."""
    return regra.assinatura(efeitos)


# ---- leitura -------------------------------------------------------------------------------------


def _em(objeto, campo):
    """O valor de `campo` (`cutRule/targetKind`) dentro de `objeto`, ou `_AUSENTE`."""
    atual = objeto
    for parte in campo.split("/"):
        if not isinstance(atual, dict) or parte not in atual:
            return _AUSENTE
        atual = atual[parte]
    return atual


def _decimal(valor):
    try:
        return Decimal(str(valor))
    except (InvalidOperation, ValueError):
        return valor


def _igual(campo, antes, depois):
    """Iguais na norma, e não na grafia: `5.0000` e `5` são o mesmo percentual."""
    if antes is _AUSENTE or depois is _AUSENTE:
        return antes is depois
    if campo == "stages":
        return sorted(str(item) for item in antes or []) == sorted(
            str(item) for item in depois or []
        )
    if campo.endswith("percentage") and antes not in (None, "") and depois not in (None, ""):
        return _decimal(antes) == _decimal(depois)
    if campo == "normativeRule/rounding":
        return (antes or {}) == (depois or {})
    return antes == depois


def _nome(colecao, campo):
    return NOME_DO_CAMPO.get((colecao, campo), campo)


def _campo_a_campo(colecao, antes, depois, campos, base):
    """`(alterações, mudanças, None)` — ou `((), (), resultado fora)` quando o contrato não deixa.

    Todos os campos são julgados antes de qualquer Alteração valer: um retificável diferente não
    salva o destino de um não retificável diferente (FR-939).
    """
    alteracoes, mudancas = [], []
    for campo in campos:
        anterior, novo = _em(antes, campo), _em(depois, campo)
        if _igual(campo, anterior, novo):
            continue
        decisao = mutabilidade.CONTRATO[(colecao, campo)]
        fora_do_contrato = (anterior, novo)
        if decisao.natureza is not mutabilidade.Natureza.RETIFICAVEL:
            return (
                (),
                (),
                _fora(
                    f"{_nome(colecao, campo)} difere da origem, e não se corrige por Retificação: "
                    f"{decisao.razao}".strip(),
                    campo_fora=(colecao, campo, *fora_do_contrato),
                ),
            )
        if anterior is _AUSENTE:
            return (
                (),
                (),
                _fora(
                    f"não declara {_nome(colecao, campo)}, e a declaração não nasce por Retificação"
                ),
            )
        if novo is _AUSENTE:
            return (
                (),
                (),
                _fora(
                    f"declara {_nome(colecao, campo)}, e a origem não: retirar declaração "
                    "publicada não é o que o gesto faz"
                ),
            )
        alteracoes.append(
            {
                "targetPath": f"{base}/{campo}",
                "operation": "REPLACE",
                "newValue": copy.deepcopy(novo),
            }
        )
        mudancas.append((colecao, campo, anterior, novo))
    return tuple(alteracoes), tuple(mudancas), None


def _caminho_do_perfil(perfil):
    return f"/profiles/id={perfil.get('id')}"


def _marco_unico(destino):
    marcos = [item for item in destino.get(MARCOS) or [] if isinstance(item, dict)]
    if not marcos:
        return None, "não tem marco classificatório, e marco não nasce por Retificação"
    if len(marcos) > 1:
        return None, f"tem {len(marcos)} marcos, e não há como saber qual deles corresponde"
    return marcos[0], ""


def _caminho_do_marco(perfil, marco):
    return f"{_caminho_do_perfil(perfil)}/{MARCOS}/id={marco.get('id')}"


def derivada(*partes):
    """Identidade estável do que o gesto faz nascer (R-011).

    A conferência e a confirmação calculam duas vezes, e uma identidade sorteada mudaria o ato sob
    a mesma chave de idempotência — a razão que a `020` deu para o Anexo, e a `048` para a
    Modalidade.
    """
    return str(uuid5(NAMESPACE_URL, "retificacao/aplicar-a-todos/" + "/".join(map(str, partes))))


# ---- as unidades do marco ------------------------------------------------------------------------


def _janela(fonte, origem, destino, contexto):
    marco, motivo = _marco_unico(destino)
    if motivo:
        return _fora(motivo)
    base = _caminho_do_marco(destino, marco)
    territorio = (f"{base}/appealWindow",)
    janela = fonte["appealWindow"]
    if not isinstance(marco.get("appealWindow"), dict):
        if janela.get("admits") is not True:
            return _fora(
                "não declara janela recursal, e a janela que nasce por Retificação precisa admitir "
                "recurso — a da origem não admite"
            )
        nova = {
            "admits": True,
            "durationDays": janela.get("durationDays"),
            "unit": janela.get("unit") or "DIAS_CORRIDOS",
        }
        return _Resultado(
            efeito=NASCE,
            alteracoes=(
                {"targetPath": f"{base}/appealWindow", "operation": "REPLACE", "newValue": nova},
            ),
            mudancas=tuple(
                (MARCOS, f"appealWindow/{chave}", None, valor) for chave, valor in nova.items()
            ),
            territorio=territorio,
        )
    alteracoes, mudancas, fora = _campo_a_campo(MARCOS, marco, fonte, CAMPOS_DA_JANELA, base)
    if fora:
        return fora
    return _Resultado(
        efeito=SUBSTITUI if alteracoes else SEM_MUDANCA,
        alteracoes=alteracoes,
        mudancas=mudancas,
        territorio=territorio,
    )


def _quantidade_fixa(antes, depois):
    """`(anterior, aplicada)` quando o corte aplicado é de quantidade fixa (FR-917)."""
    if (depois or {}).get("targetKind") != "FIXED":
        return None
    anterior = antes or {}
    return (
        anterior.get("targetCount") if anterior.get("targetKind") == "FIXED" else None,
        depois.get("targetCount"),
    )


def _corte(fonte, origem, destino, contexto):
    marco, motivo = _marco_unico(destino)
    if motivo:
        return _fora(motivo)
    base = _caminho_do_marco(destino, marco)
    territorio = (f"{base}/cutRule",)
    corte = fonte["cutRule"]
    atual = marco.get("cutRule")
    if not isinstance(atual, dict):
        # O corte que nasce governando Etapa já avaliada tiraria dela quem já foi avaliado — a
        # guarda que o ato aplica (FR-789), dita antes da confirmação, e não depois dela (FR-940).
        etapa = faixa.etapa_governada(corte)
        if etapa and contexto["tem_resultado"](etapa):
            nome = contexto["etapas"].get(etapa) or etapa
            return _fora(
                f"não declara regra de corte, e a que nasceria governa a Etapa {nome}, que já tem "
                "Resultado registrado"
            )
        nova = {
            campo.split("/", 1)[1]: copy.deepcopy(_em(fonte, campo)) for campo in CAMPOS_DO_CORTE
        }
        nova = {chave: (None if valor is _AUSENTE else valor) for chave, valor in nova.items()}
        return _Resultado(
            efeito=NASCE,
            alteracoes=(
                {"targetPath": f"{base}/cutRule", "operation": "REPLACE", "newValue": nova},
            ),
            mudancas=tuple(
                (MARCOS, f"cutRule/{chave}", None, valor) for chave, valor in nova.items()
            ),
            territorio=territorio,
            quantidade_fixa=_quantidade_fixa(None, nova),
        )
    alteracoes, mudancas, fora = _campo_a_campo(MARCOS, marco, fonte, CAMPOS_DO_CORTE, base)
    if fora:
        return fora
    return _Resultado(
        efeito=SUBSTITUI if alteracoes else SEM_MUDANCA,
        alteracoes=alteracoes,
        mudancas=mudancas,
        territorio=territorio,
        quantidade_fixa=_quantidade_fixa(atual, corte) if alteracoes else None,
    )


def _chave_do_criterio(criterio, fatos):
    """O critério sem identidade e sem ordem: o que ele compara, e como."""
    normalizado = regra._criterio_normalizado(criterio, fatos)
    return (normalizado["type"], tuple(normalizado["alvo"]), normalizado["whenMissing"])


def _criterios(fonte, origem, destino, contexto):
    """A lista inteira, como na composição (FR-923) — por remoção e acréscimo (FR-792 da `048`).

    Tipo, parâmetro e ausência não se retificam no lugar, e o critério que muda de espécie é outro
    critério: sai o do destino, entra o da origem. O que já é igual fica, com a identidade que tem;
    o que só difere na ordem recebe a ordem, que se retifica.
    """
    marco, motivo = _marco_unico(destino)
    if motivo:
        return _fora(motivo)
    base = _caminho_do_marco(destino, marco)
    reescritos, falta = regra._criterios_no_destino(fonte, origem, destino)
    if falta:
        return _fora(falta)
    fatos = regra._fatos(destino)
    existentes = [item for item in marco.get("tiebreakers") or [] if isinstance(item, dict)]
    livres = list(existentes)
    ficam, entram, reordenados = [], [], []
    for criterio in sorted(
        reescritos, key=lambda item: (item.get("order") is None, item.get("order") or 0)
    ):
        chave = _chave_do_criterio(criterio, fatos)
        candidatos = [item for item in livres if _chave_do_criterio(item, fatos) == chave]
        par = next(
            (item for item in candidatos if item.get("order") == criterio.get("order")),
            candidatos[0] if candidatos else None,
        )
        if par is None:
            entram.append(
                {**criterio, "id": derivada("criterio", marco.get("id"), criterio.get("id"))}
            )
            continue
        livres.remove(par)
        if par.get("order") != criterio.get("order"):
            reordenados.append((par, criterio.get("order")))
        ficam.append({**par, "order": criterio.get("order")})
    alteracoes = [
        {"targetPath": f"{base}/tiebreakers/id={item.get('id')}", "operation": "REMOVE"}
        for item in livres
    ]
    alteracoes += [
        {
            "targetPath": f"{base}/tiebreakers/id={item.get('id')}/order",
            "operation": "REPLACE",
            "newValue": ordem,
        }
        for item, ordem in reordenados
    ]
    alteracoes += [
        {"targetPath": f"{base}/tiebreakers/-", "operation": "ADD", "newValue": item}
        for item in entram
    ]
    if not alteracoes:
        return _Resultado(efeito=SEM_MUDANCA, territorio=(f"{base}/tiebreakers",))
    depois = sorted(ficam + entram, key=lambda item: item.get("order") or 0)
    return _Resultado(
        efeito=SUBSTITUI if existentes else NASCE,
        alteracoes=tuple(alteracoes),
        mudancas=((MARCOS, "tiebreakers", existentes, depois),),
        territorio=(f"{base}/tiebreakers",),
    )


def _campos_do_marco(fonte, origem, destino, contexto):
    marco, motivo = _marco_unico(destino)
    if motivo:
        return _fora(motivo)
    if regra.metodo_proprio(fonte):
        return _fora(
            "o marco de origem declara método próprio de sorteio, que existe para divergir e não é "
            "levado a outro Perfil"
        )
    if regra.metodo_proprio(marco):
        return _fora("o marco dele declara método próprio de sorteio")
    base = _caminho_do_marco(destino, marco)
    alteracoes, mudancas, fora = _campo_a_campo(
        MARCOS, marco, fonte, CAMPOS_DO_MARCO_PROPRIOS, base
    )
    if fora:
        return fora
    if regra.metodo_proprio({**marco, "orderProduction": fonte.get("orderProduction")}):
        # O método guardado num marco de pontuação é dele (030, FR-418), e passaria a governar a
        # ordem assim que a forma virasse sorteio: o destino sortearia por outro algoritmo sem que a
        # conferência o dissesse (a mesma razão da composição, `FR-922`).
        return _fora(
            "o marco dele guarda um método de sorteio próprio, que passaria a governar a ordem"
        )
    return _Resultado(
        efeito=SUBSTITUI if alteracoes else SEM_MUDANCA,
        alteracoes=alteracoes,
        mudancas=mudancas,
        territorio=tuple(
            f"{base}/{campo}"
            for campo in ("orderProduction", "stages", "operation", "normalization", "rounding")
        ),
    )


# ---- as unidades do Perfil -----------------------------------------------------------------------


def _campo_do_perfil(campo):
    def unidade(valor, origem, destino, contexto):
        base = _caminho_do_perfil(destino)
        territorio = (f"{base}/{campo}",)
        if campo == REVERSAO and not listas_reservadas(destino):
            return _fora("não declara lista reservada, e a reversão só existe onde há uma")
        antes = regra.valor_do_campo(destino, campo)
        if antes == valor:
            return _Resultado(efeito=SEM_MUDANCA, territorio=territorio)
        if campo == REVERSAO and not isinstance(destino.get(REVERSAO), dict):
            alteracao = {
                "targetPath": f"{base}/{REVERSAO}",
                "operation": "REPLACE",
                "newValue": {"kind": valor},
            }
        elif campo == REVERSAO:
            alteracao = {
                "targetPath": f"{base}/{REVERSAO}/kind",
                "operation": "REPLACE",
                "newValue": valor,
            }
        else:
            alteracao = {"targetPath": f"{base}/{campo}", "operation": "REPLACE", "newValue": valor}
        return _Resultado(
            efeito=SUBSTITUI if antes else NASCE,
            alteracoes=(alteracao,),
            mudancas=((PERFIS, campo, antes or None, valor),),
            territorio=territorio,
        )

    return unidade


# ---- a Modalidade, pelo código -------------------------------------------------------------------


def _modalidade(fonte, origem, destino, contexto):
    """A Modalidade pelo código (FR-924), com a declaração da ampla (FR-925), campo a campo."""
    codigo = fonte.get("code") or ""
    base = _caminho_do_perfil(destino)
    existentes = [item for item in destino.get(MODALIDADES) or [] if isinstance(item, dict)]
    ja_declara = tuple(item.get("code") or "" for item in existentes)
    origem_e_a_ampla = str(origem.get("generalCompetitionModalityId") or "") == str(fonte.get("id"))
    aponta = str(destino.get("generalCompetitionModalityId") or "")
    ampla_antes = regra._codigo_da_ampla(destino) or None
    regra_da_origem = fonte.get("normativeRule")
    atual = next((item for item in existentes if item.get("code") == codigo), None)

    if atual is None:
        identidade = derivada("modalidade", destino.get("id"), codigo)
        nova = {
            "id": identidade,
            "code": codigo,
            "name": fonte.get("name") or "",
            "description": fonte.get("description") or "",
            "normativeRule": (
                {
                    "id": derivada("modalidade", destino.get("id"), codigo, "normativeRule"),
                    "foundation": regra_da_origem.get("foundation") or "",
                    "version": regra_da_origem.get("version") or "",
                    "percentage": regra_da_origem.get("percentage"),
                    # Os opacos nascem vazios, como a tela os cria (`_modalidade_nova`): a
                    # composição não os pede, e levá-los seria materializar o que ninguém viu.
                    "calculation": {},
                    "rounding": copy.deepcopy(regra_da_origem.get("rounding") or {}),
                    "distribution": {},
                    "callRules": {},
                    "effectiveFrom": regra_da_origem.get("effectiveFrom"),
                }
                if isinstance(regra_da_origem, dict)
                else None
            ),
        }
        alteracoes = [
            {"targetPath": f"{base}/{MODALIDADES}/-", "operation": "ADD", "newValue": nova}
        ]
        mudancas = [(MODALIDADES, "", None, nova)]
        territorio = [f"{base}/{MODALIDADES}/id={identidade}"]
        if origem_e_a_ampla:
            alteracoes.append(
                {
                    "targetPath": f"{base}/generalCompetitionModalityId",
                    "operation": "REPLACE",
                    "newValue": identidade,
                }
            )
            mudancas.append((PERFIS, "generalCompetitionModalityId", ampla_antes, codigo))
            territorio.append(f"{base}/generalCompetitionModalityId")
        return _Resultado(
            efeito=NASCE,
            alteracoes=tuple(alteracoes),
            mudancas=tuple(mudancas),
            territorio=tuple(territorio),
            ja_declara=ja_declara,
            codigo_que_nasce=codigo,
        )

    regra_atual = atual.get("normativeRule")
    if isinstance(regra_da_origem, dict) and not isinstance(regra_atual, dict):
        return _fora(
            f"a Modalidade {codigo} dele não declara regra normativa, e a regra não nasce em "
            "Modalidade publicada",
            ja_declara=ja_declara,
        )
    if isinstance(regra_atual, dict) and not isinstance(regra_da_origem, dict):
        return _fora(
            f"a Modalidade {codigo} dele declara regra normativa, e a da origem não: retirar "
            "declaração publicada não é o que o gesto faz",
            ja_declara=ja_declara,
        )
    campos = CAMPOS_DA_MODALIDADE + (CAMPOS_DA_REGRA if isinstance(regra_atual, dict) else ())
    caminho = f"{base}/{MODALIDADES}/id={atual.get('id')}"
    alteracoes, mudancas, fora = _campo_a_campo(MODALIDADES, atual, fonte, campos, caminho)
    if fora:
        return replace(fora, ja_declara=ja_declara)
    alteracoes, mudancas = list(alteracoes), list(mudancas)
    territorio = [caminho]
    nova_ampla = None
    if origem_e_a_ampla and aponta != str(atual.get("id")):
        nova_ampla = str(atual.get("id"))
    elif not origem_e_a_ampla and aponta == str(atual.get("id")):
        nova_ampla = ""
    if nova_ampla is not None:
        alteracoes.append(
            {
                "targetPath": f"{base}/generalCompetitionModalityId",
                "operation": "REPLACE",
                "newValue": nova_ampla or None,
            }
        )
        mudancas.append(
            (PERFIS, "generalCompetitionModalityId", ampla_antes, codigo if nova_ampla else None)
        )
        territorio.append(f"{base}/generalCompetitionModalityId")
    return _Resultado(
        efeito=SUBSTITUI if alteracoes else SEM_MUDANCA,
        alteracoes=tuple(alteracoes),
        mudancas=tuple(mudancas),
        territorio=tuple(territorio),
        ja_declara=ja_declara,
    )


_UNIDADE = {
    JANELA: _janela,
    CORTE: _corte,
    CRITERIOS: _criterios,
    CAMPOS_DO_MARCO: _campos_do_marco,
    FORMA_DE_CONVOCACAO: _campo_do_perfil(FORMA_DE_CONVOCACAO),
    REVERSAO: _campo_do_perfil(REVERSAO),
    MODALIDADE: _modalidade,
}


# ---- a origem e o alcance -----------------------------------------------------------------------


def _fonte(unidade, origem, alvo):
    """O que a origem declara para a unidade — ou `SemOrigem`, com a recusa por extenso (R-013)."""
    codigo = origem.get("code") or ""
    if unidade in UNIDADES_DO_MARCO:
        marco = next(
            (item for item in origem.get(MARCOS) or [] if str(item.get("id")) == str(alvo)), None
        )
        if marco is None:
            raise SemOrigem("O marco de origem não existe no conteúdo que esta Retificação produz.")
        nome = marco.get("name") or marco.get("code") or codigo
        exigido = {
            JANELA: ("appealWindow", "janela recursal"),
            CORTE: ("cutRule", "regra de corte"),
        }.get(unidade)
        if exigido and not isinstance(marco.get(exigido[0]), dict):
            raise SemOrigem(
                f"O marco {nome}, do Perfil {codigo}, não declara {exigido[1]}: não há o que "
                "aplicar."
            )
        if unidade == CRITERIOS and not marco.get("tiebreakers"):
            raise SemOrigem(
                f"O marco {nome}, do Perfil {codigo}, não declara critério de desempate: não há o "
                "que aplicar."
            )
        return marco
    if unidade in UNIDADES_DO_PERFIL:
        valor = regra.valor_do_campo(origem, unidade)
        if not valor:
            raise SemOrigem(
                f"O Perfil {codigo} não declara {NOME_DA_UNIDADE[unidade].split(' ', 1)[1]}: "
                "não há o que aplicar."
            )
        return valor
    if unidade == MODALIDADE:
        modalidade = next(
            (item for item in origem.get(MODALIDADES) or [] if str(item.get("id")) == str(alvo)),
            None,
        )
        if modalidade is None or not modalidade.get("code"):
            raise SemOrigem(
                "A Modalidade de origem não existe no conteúdo que esta Retificação produz."
            )
        return modalidade
    raise SemOrigem("Unidade desconhecida.")


def _ja_alterado(alterados, territorio, codigo_que_nasce):
    """O destino já recebeu, neste ato, Alteração no mesmo lugar? (R-014).

    O acréscimo (`…/-`) só toca a coleção inteira — a dos critérios —, ou a Modalidade de mesmo
    código que o gesto faria nascer; acrescentar outra Modalidade ao destino não é o mesmo campo.
    """
    for alteracao in alterados:
        caminho = alteracao.get("targetPath") or ""
        if caminho.endswith("/-"):
            colecao = caminho[:-2]
            if colecao in territorio:
                return True
            if (
                codigo_que_nasce
                and colecao.endswith(f"/{MODALIDADES}")
                and (alteracao.get("newValue") or {}).get("code") == codigo_que_nasce
                and any(lugar.startswith(f"{colecao}/") for lugar in territorio)
            ):
                return True
            continue
        for lugar in territorio:
            if (
                caminho == lugar
                or caminho.startswith(f"{lugar}/")
                or lugar.startswith(f"{caminho}/")
            ):
                return True
    return False


def efeitos(conteudo, *, unidade, perfil, alvo=None, alterados=(), tem_resultado=None):
    """Um `Efeito` por Perfil do conteúdo que não é a origem, na ordem dos Perfis.

    `conteudo` é o proposto: o vigente com as Alterações que o ato já traz. `perfil` é a identidade
    do Perfil de origem, e `alvo` a do marco ou da Modalidade. `alterados` são as Alterações que o
    ato já traz — as digitadas e as de gestos anteriores —, para que o mesmo campo não receba duas
    (R-014). `tem_resultado(etapa_id)` responde se a Etapa já tem Resultado (FR-789).

    Levanta `SemOrigem` quando a origem não existe ou não declara a unidade.
    """
    if unidade not in _UNIDADE:
        raise SemOrigem("Unidade desconhecida.")
    perfis = [item for item in conteudo.get(PERFIS) or [] if isinstance(item, dict)]
    origem = next((item for item in perfis if str(item.get("id")) == str(perfil)), None)
    if origem is None:
        raise SemOrigem("O Perfil de origem não existe no conteúdo que esta Retificação produz.")
    fonte = _fonte(unidade, origem, alvo)
    contexto = {
        "tem_resultado": tem_resultado or (lambda etapa: False),
        "etapas": {
            str(etapa.get("id")): etapa.get("name") or ""
            for etapa in conteudo.get("stages") or []
            if isinstance(etapa, dict)
        },
    }
    removidos = {
        alteracao.get("targetPath")
        for alteracao in alterados
        if alteracao.get("operation") == "REMOVE"
    }
    lista = []
    for destino in perfis:
        if destino is origem:
            continue
        comum = {
            "perfil": str(destino.get("id")),
            "codigo": destino.get("code") or "",
            "denominacao": destino.get("name") or "",
        }
        if _caminho_do_perfil(destino) in removidos:
            lista.append(Efeito(**comum, efeito=FORA, motivo="é removido por esta Retificação"))
            continue
        resultado = _UNIDADE[unidade](fonte, origem, destino, contexto)
        if resultado.efeito in APLICAVEIS and _ja_alterado(
            alterados, resultado.territorio, resultado.codigo_que_nasce
        ):
            resultado = _fora(
                f"já tem, nesta Retificação, alteração em {NOME_DA_UNIDADE[unidade]}: a edição à "
                "mão e o gesto não se somam no mesmo campo",
                ja_declara=resultado.ja_declara,
            )
        lista.append(
            Efeito(
                **comum,
                efeito=resultado.efeito,
                motivo=resultado.motivo,
                alteracoes=resultado.alteracoes,
                mudancas=resultado.mudancas,
                impressao=regra.impressao(list(resultado.alteracoes))
                if resultado.efeito in APLICAVEIS
                else "",
                quantidade_fixa=resultado.quantidade_fixa,
                ja_declara=resultado.ja_declara,
                campo_fora=resultado.campo_fora,
            )
        )
    return lista
