"""Invariantes da Etapa de Avaliação.

No molde de `editais/domain/cronograma.py`: o que o command atravessa, e não o que o serializer
declara. A interface administrativa invoca o command diretamente e não passa pelo serializer da
API, de modo que validar apenas ali deixaria sem verificação justamente o canal onde o dado é
digitado.
"""

from decimal import Decimal, InvalidOperation

from processo_seletivo.editais.domain.documentos import (
    NA_INSCRICAO,
    momento_de,
    vale_para_toda_inscricao,
)
from processo_seletivo.editais.domain.perfis import RecusaDeCampo


class StageValidationError(RecusaDeCampo):
    pass


def validate_stage(stage: dict, *, event_ids: frozenset[str]) -> None:
    if not (stage.get("name") or "").strip():
        raise StageValidationError(
            "A Etapa de Avaliação exige nome.", campo="name", identidade=stage.get("id", "")
        )
    if stage.get("order", 0) < 0:
        raise StageValidationError("A ordem da Etapa não pode ser negativa.")
    peso = stage.get("weight")
    # Peso zero afirmaria uma ponderação que não pondera; "esta Etapa não pondera" exprime-se
    # pela ausência, como o percentual da Regra Normativa (FR-020).
    if peso is not None and peso <= 0:
        raise StageValidationError(
            "O peso da Etapa, quando informado, deve ser maior que zero.",
            campo="weight",
            identidade=stage.get("id", ""),
        )
    nota = stage.get("minimumScore")
    if nota is not None and nota < 0:
        raise StageValidationError(
            "A nota mínima da Etapa não pode ser negativa.",
            campo="minimumScore",
            identidade=stage.get("id", ""),
        )
    # As duas do incremento da `012`, verificadas **aqui** porque é aqui que o command passa: a
    # interface administrativa não atravessa o serializer da API, e deixar a faixa só para o
    # `CheckConstraint` transformaria dado digitado errado em erro de banco (FR-007).
    previstas = stage.get("evaluationsPerRegistration")
    if previstas is not None and previstas < 1:
        raise StageValidationError(
            "A Etapa recebe ao menos uma avaliação por inscrição.",
            campo="evaluationsPerRegistration",
            identidade=stage.get("id", ""),
        )
    maxima = stage.get("maximumScore")
    # Máxima zero afirmaria uma pontuação que não pontua, pelo mesmo motivo do peso. Ausência é
    # que exprime "o Edital não declarou limite".
    if maxima is not None and maxima <= 0:
        raise StageValidationError(
            "A pontuação máxima da Etapa, quando informada, deve ser maior que zero.",
            campo="maximumScore",
            identidade=stage.get("id", ""),
        )
    if nota is not None and maxima is not None and nota > maxima:
        raise StageValidationError(
            "A nota mínima da Etapa não pode superar a pontuação máxima.",
            campo="minimumScore",
            identidade=stage.get("id", ""),
        )
    evento = stage.get("scheduleEventId")
    if evento is not None and str(evento) not in event_ids:
        raise StageValidationError(
            "A Etapa referencia um Evento que não existe no Cronograma deste Edital."
        )


def validate_stages(
    stages: list[dict], *, schedule: list[dict], document_requirements: list[dict] | None = None
) -> None:
    """As Etapas são opcionais; o que não é opcional é a coerência entre elas.

    O Evento referenciado é conferido contra o Cronograma **da mesma gravação**, e não contra o
    banco: `replace_draft` substitui o rascunho inteiro, então um Evento removido no mesmo POST já
    não existe — e um vínculo não pode sobreviver ao Evento que o sustenta.

    O documento que comprova um critério do barema, pela mesma razão, é conferido contra os
    Documentos Exigidos **desta gravação** (146, FR-5205). É também por isso que a restrição
    acrescentada ao documento depois do vínculo é recusada aqui, na gravação da etapa Inscrição: o
    barema viaja em toda gravação, e a conferência o encontra com o documento já restrito.
    """
    ids = [str(stage["id"]) for stage in stages]
    if len(ids) != len(set(ids)):
        raise StageValidationError("Etapas não podem repetir identidade no Edital.")
    orders = [stage.get("order", 0) for stage in stages]
    if len(orders) != len(set(orders)):
        raise StageValidationError("Etapas não podem repetir ordem no Edital.")
    event_ids = frozenset(str(event["id"]) for event in schedule)
    for stage in stages:
        validate_stage(stage, event_ids=event_ids)
    for stage in stages:
        for identidade, campo, mensagem in problemas_do_barema(stage, document_requirements or []):
            raise StageValidationError(mensagem, campo=campo, identidade=identidade)


# ------------------------------------------------------------------------------------------------
# O barema (146): uma regra, duas leituras
# ------------------------------------------------------------------------------------------------

#: O maior valor que `decimal(7,4)` comporta, que é a coluna da máxima da Etapa e da do critério.
LIMITE_DA_PONTUACAO = Decimal("999.9999")
LIMITE_DO_NOME = 200
LIMITE_DA_UNIDADE = 60
DECISORIA = "DECISORIA"


def _numero(valor):
    """O decimal do rascunho (`Decimal`) ou do conteúdo publicado (`"20.0000"`), ou `None`.

    `False` quando o valor existe e não é número: a recusa diz o que a pessoa escreveu, em vez de
    tratá-lo como ausente.
    """
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return None
    if isinstance(valor, bool):
        return False
    try:
        numero = Decimal(str(valor).strip())
    except (InvalidOperation, ValueError):
        return False
    return numero if numero.is_finite() else False


def _quatro_casas(numero: Decimal) -> bool:
    """`20.00000` tem quatro casas que valem; `0.12345`, não. O número enorme não se quantiza."""
    try:
        return numero == numero.quantize(Decimal("0.0001"))
    except InvalidOperation:
        return False


def _texto(valor) -> str:
    return valor.strip() if isinstance(valor, str) else ""


def _nome_da_etapa(etapa: dict) -> str:
    return _texto(etapa.get("name")) or "sem nome"


def _nome_do_documento(documento: dict) -> str:
    return _texto(documento.get("name")) or _texto(documento.get("key")) or "sem nome"


def criterios_de(etapa) -> list:
    """A lista de critérios da Etapa, com a ausência lida como lista vazia (FR-5208, FR-5213)."""
    if not isinstance(etapa, dict):
        return []
    criterios = etapa.get("criteria")
    return criterios if isinstance(criterios, list) else []


def soma_das_maximas(etapa) -> Decimal | None:
    """A soma das máximas dos critérios, ou `None` quando alguma não é número (D-003)."""
    soma = Decimal("0")
    for criterio in criterios_de(etapa):
        maxima = _numero(criterio.get("maximumScore")) if isinstance(criterio, dict) else False
        if not maxima:
            return None
        soma += maxima
    return soma


def problemas_do_barema(etapa: dict, documentos: list[dict]) -> list[tuple[str, str, str]]:
    """O que está errado no barema de uma Etapa, como `(identidade, campo, mensagem)` (146).

    **Uma regra, duas leituras**, no molde de `documentos.problemas_do_momento`: a gravação do
    rascunho recusa o primeiro problema, e a conferência da publicação — que é também a da
    Retificação, sobre o conteúdo consolidado — lista todos (FR-5203, FR-5210). Recebe a Etapa no
    formato do rascunho ou do conteúdo publicado: os decimais chegam como `Decimal` num e como texto
    canônico no outro, e `_numero` lê os dois.

    `identidade` é a do critério quando o problema é dele, e a da Etapa quando é do conjunto — a
    soma e a forma —, para que a tela ancore a recusa no campo que a causou (FR-033).
    """
    criterios = criterios_de(etapa)
    if not criterios:
        return []
    nome_da_etapa = _nome_da_etapa(etapa)
    identidade_da_etapa = str(etapa.get("id") or "")
    if etapa.get("forma") == DECISORIA:
        # FR-5204: a decisória não produz nota, e o barema é a soma de parcelas de uma nota.
        return [
            (
                identidade_da_etapa,
                "criteria",
                f"A Etapa «{nome_da_etapa}» é concluída com decisão, sem nota, e por isso não tem "
                "barema. Remova os critérios ou passe a Etapa para «Com pontuação».",
            )
        ]
    por_id = {str(documento.get("id")): documento for documento in documentos or []}
    problemas = []
    nomes = {}
    for posicao, criterio in enumerate(criterios, 1):
        if not isinstance(criterio, dict):
            problemas.append(
                (identidade_da_etapa, "criteria", f"O {posicao}º critério do barema não é válido.")
            )
            continue
        identidade = str(criterio.get("id") or "")
        nome = _texto(criterio.get("name"))
        rotulo = f"«{nome}»" if nome else f"{posicao}º"
        onde = f"O critério {rotulo} da Etapa «{nome_da_etapa}»"
        if not nome:
            problemas.append(
                (identidade, "name", f"{onde} precisa de nome — é o título que o Edital imprime.")
            )
        elif len(nome) > LIMITE_DO_NOME:
            problemas.append(
                (identidade, "name", f"{onde} tem nome com mais de {LIMITE_DO_NOME} caracteres.")
            )
        elif nome.casefold() in nomes:
            problemas.append(
                (
                    identidade,
                    "name",
                    f"Dois critérios da Etapa «{nome_da_etapa}» se chamam «{nome}». Cada critério "
                    "precisa de nome próprio, para que a comissão e o candidato saibam qual é "
                    "qual.",
                )
            )
        else:
            nomes[nome.casefold()] = identidade
        maxima = _numero(criterio.get("maximumScore"))
        if maxima is None:
            problemas.append((identidade, "maximumScore", f"{onde} precisa de pontuação máxima."))
        elif maxima is False or maxima <= 0:
            problemas.append(
                (identidade, "maximumScore", f"{onde} precisa de pontuação máxima maior que zero.")
            )
            maxima = None
        elif maxima > LIMITE_DA_PONTUACAO or not _quatro_casas(maxima):
            problemas.append(
                (
                    identidade,
                    "maximumScore",
                    f"{onde} tem pontuação máxima fora do que o Edital registra: até 999,9999, "
                    "com no máximo quatro casas decimais.",
                )
            )
            maxima = None
        pontos = _numero(criterio.get("pointsPerUnit"))
        unidade = _texto(criterio.get("unitLabel"))
        if pontos is False or (pontos is not None and pontos <= 0):
            problemas.append(
                (
                    identidade,
                    "pointsPerUnit",
                    f"{onde} tem pontos por unidade que não são um número maior que zero.",
                )
            )
        elif pontos is not None and not _quatro_casas(pontos):
            problemas.append(
                (
                    identidade,
                    "pointsPerUnit",
                    f"{onde} tem pontos por unidade com mais de quatro casas decimais.",
                )
            )
        elif pontos is not None and maxima is not None and pontos > maxima:
            problemas.append(
                (
                    identidade,
                    "pointsPerUnit",
                    f"{onde} dá mais pontos por unidade do que a máxima dele: uma unidade só já "
                    "passaria do teto.",
                )
            )
        elif pontos is not None and not unidade:
            problemas.append(
                (
                    identidade,
                    "unitLabel",
                    f"{onde} tem pontos por unidade e não diz a unidade — certificado, mês, "
                    "diploma.",
                )
            )
        elif pontos is None and unidade:
            problemas.append(
                (
                    identidade,
                    "pointsPerUnit",
                    f"{onde} tem unidade («{unidade}») sem pontos por unidade. Informe quantos "
                    "pontos vale cada unidade, ou apague a unidade para a comissão atribuir a "
                    "pontuação diretamente.",
                )
            )
        elif len(unidade) > LIMITE_DA_UNIDADE:
            problemas.append(
                (
                    identidade,
                    "unitLabel",
                    f"{onde} tem unidade com mais de {LIMITE_DA_UNIDADE} caracteres.",
                )
            )
        problemas.extend(_problemas_do_documento(criterio, identidade, onde, por_id))
    if not problemas:
        problemas.extend(_problemas_da_soma(etapa, identidade_da_etapa, nome_da_etapa))
    return problemas


def _problemas_do_documento(criterio, identidade, onde, por_id):
    """O documento ligado: do Edital, da inscrição e pedido a toda inscrição (FR-5205, D-010)."""
    referencia = criterio.get("documentRequirementId")
    if referencia in (None, ""):
        return []
    documento = por_id.get(str(referencia))
    if documento is None:
        return [
            (
                identidade,
                "documentRequirementId",
                f"{onde} aponta um documento que não está entre os Documentos Exigidos deste "
                "Edital.",
            )
        ]
    nome = _nome_do_documento(documento)
    if momento_de(documento) != NA_INSCRICAO:
        return [
            (
                identidade,
                "documentRequirementId",
                f"{onde} é comprovado por «{nome}», que é pedido na convocação. O barema se "
                "pontua com o que a inscrição apresenta: escolha um documento da inscrição.",
            )
        ]
    if not vale_para_toda_inscricao(documento):
        return [
            (
                identidade,
                "documentRequirementId",
                f"{onde} é comprovado por «{nome}», que não é pedido a toda inscrição. O barema "
                "vale para toda inscrição da Etapa, e o documento que o comprova também precisa "
                "valer: sem restrição de Perfil, de modalidade ou de condição.",
            )
        ]
    return []


def _problemas_da_soma(etapa, identidade_da_etapa, nome_da_etapa):
    """A máxima da Etapa é a soma das máximas dos critérios (D-003, FR-5203)."""
    soma = soma_das_maximas(etapa)
    if soma is None:
        return []
    if soma > LIMITE_DA_PONTUACAO:
        return [
            (
                identidade_da_etapa,
                "criteria",
                f"A soma das máximas dos critérios da Etapa «{nome_da_etapa}» passa de 999,9999, "
                "o maior valor que a pontuação de uma Etapa registra.",
            )
        ]
    declarada = _numero(etapa.get("maximumScore"))
    if declarada is None or declarada is False or declarada != soma:
        return [
            (
                identidade_da_etapa,
                "maximumScore",
                f"A pontuação máxima da Etapa «{nome_da_etapa}» precisa ser a soma das máximas dos "
                f"critérios do barema, {_legivel(soma)}.",
            )
        ]
    return []


def _legivel(numero: Decimal) -> str:
    texto = format(numero, "f")
    if "." in texto:
        texto = texto.rstrip("0").rstrip(".")
    return texto.replace(".", ",")
