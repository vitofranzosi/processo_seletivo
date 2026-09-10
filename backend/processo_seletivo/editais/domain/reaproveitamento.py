"""Transformar o conteúdo publicado de um Edital no rascunho de outro.

Funções puras, e a razão de serem puras é o risco: é aqui que mora a parte desta feature que, se
errar, erra **em silêncio**. A cópia preserva a coerência interna do que copia — um identificador da
origem que escape do remapeamento continua consistente com os seus vizinhos, atravessa a validação
da gravação e só falha na publicação, ou nunca (023, T-005).

Por isso `remapear` **falha alto** diante de referência que o mapa não conhece, em vez de deixá-la
passar: identificador não mapeado é defeito determinável, e o lugar de recusá-lo é aqui.
"""

import uuid
from decimal import Decimal

from django.utils.dateparse import parse_datetime

from processo_seletivo.editais.domain import secoes as secoes_do_catalogo

# O que o conteúdo publicado carrega e o rascunho não grava. Não é conveniência: `replace_draft`
# **preserva** campos que nenhuma etapa do assistente desenha, para que gravar uma etapa não apague
# em silêncio o que outra decidiu. Copiá-los entregaria ao novo Edital conteúdo normativo que quem
# elabora não tem como revisar nem remover — beco sem saída na jornada (023, FR-008, D-004).
CAMPOS_SEM_TELA = ("classificationInformation", "callInformation")

# Os instantes que o conteúdo publicado grava como texto ISO. `validate_event` chama
# `timezone.is_aware`, que **estoura** em `str` em vez de recusar: a conversão não é polimento, é
# condição de funcionamento (023, T-002).
#
# E os decimais pela mesma razão, descoberta na implementação: `_decimal_canonico` publica
# `"1.5000"`, e `validate_stage` compara `peso <= 0` — comparação entre `str` e `int` levanta
# `TypeError`. Quem chega de outro formato converte na entrada.
DECIMAIS_DA_ETAPA = ("weight", "minimumScore", "maximumScore")


class ReferenciaNaoMapeada(ValueError):
    """Referência a identidade que o mapa da cópia não conhece."""


def mapa_de_identidades(conteudo, *, nova=uuid.uuid4) -> dict[str, str]:
    """Identidade da origem → identidade do destino, para tudo o que **é** identidade.

    As dez posições do conteúdo canônico, e a lista é fechada: acrescentar entidade ao Edital
    obriga a acrescentá-la aqui, e é o teste de remapeamento que cobra.

    `attachments` entra **mesmo não viajando no payload** do rascunho: o Anexo é criado pela
    aplicação, com o id que este mapa já reservou, e é isso que permite a `documentRequirements`
    apontar o Anexo do destino por substituição uniforme (023, T-003, T-005).
    """
    mapa: dict[str, str] = {}

    def registrar(valor):
        if valor is None:
            return
        mapa[str(valor)] = str(nova())

    for perfil in conteudo.get("profiles") or []:
        registrar(perfil.get("id"))
        for modalidade in perfil.get("competitionModalities") or []:
            registrar(modalidade.get("id"))
            regra = modalidade.get("normativeRule") or {}
            registrar(regra.get("id"))
        for fato in perfil.get("declaredFacts") or []:
            registrar(fato.get("id"))
        # Passo 1 de 2 da linha do quadro (025, R-012). O `modalityId` dela **não** é registrado
        # aqui: ele referencia a Modalidade, cuja identidade já foi mapeada acima — registrá-lo
        # daria à referência uma identidade própria, e a linha copiada passaria a apontar uma
        # Modalidade que não existe.
        for linha in perfil.get("vacancyTable") or []:
            registrar(linha.get("id"))
        for marco in perfil.get("classificationMilestones") or []:
            registrar(marco.get("id"))
            for criterio in marco.get("tiebreakers") or []:
                registrar(criterio.get("id"))
    for evento in conteudo.get("schedule") or []:
        registrar(evento.get("id"))
    for etapa in conteudo.get("stages") or []:
        registrar(etapa.get("id"))
    for documento in conteudo.get("documentRequirements") or []:
        registrar(documento.get("id"))
    for anexo in conteudo.get("attachments") or []:
        registrar(anexo.get("id"))
    return mapa


def remapear(conteudo, mapa):
    """O mesmo conteúdo com identidades e referências do destino.

    A Seção **não** entra: a identidade dela é derivada de `(edital, chave)` e `replace_draft` a
    recalcula a partir do Edital de destino. Remapeá-la aqui criaria uma segunda identidade para a
    mesma seção.
    """

    def trocar(valor, onde):
        if valor is None:
            return None
        chave = str(valor)
        if chave not in mapa:
            raise ReferenciaNaoMapeada(f"{onde} referencia identidade não mapeada: {chave}")
        return mapa[chave]

    perfis = []
    for perfil in conteudo.get("profiles") or []:
        novo_perfil = {**perfil, "id": trocar(perfil.get("id"), "profiles[].id")}
        modalidades = []
        for modalidade in perfil.get("competitionModalities") or []:
            nova_modalidade = {
                **modalidade,
                "id": trocar(modalidade.get("id"), "competitionModalities[].id"),
            }
            regra = modalidade.get("normativeRule")
            if regra:
                nova_modalidade["normativeRule"] = {
                    **regra,
                    "id": trocar(regra.get("id"), "normativeRule.id"),
                }
            modalidades.append(nova_modalidade)
        novo_perfil["competitionModalities"] = modalidades
        novo_perfil["declaredFacts"] = [
            {**fato, "id": trocar(fato.get("id"), "declaredFacts[].id")}
            for fato in perfil.get("declaredFacts") or []
        ]
        # Passo 2 de 2, e é o que quebra em silêncio se for esquecido: sem trocar o `modalityId`,
        # a linha copiada continuaria apontando a Modalidade do Edital **anterior**, e nada
        # acusaria. `None` atravessa intocado — a linha geral não referencia nada (025, R-012).
        novo_perfil["vacancyTable"] = [
            {
                **linha,
                "id": trocar(linha.get("id"), "vacancyTable[].id"),
                "modalityId": trocar(linha.get("modalityId"), "vacancyTable[].modalityId"),
            }
            for linha in perfil.get("vacancyTable") or []
        ]
        marcos = []
        for marco in perfil.get("classificationMilestones") or []:
            novo_marco = {
                **marco,
                "id": trocar(marco.get("id"), "classificationMilestones[].id"),
                # As Etapas que o marco **enumera**. A gravação não confere a existência delas —
                # só a publicação o faz —, e é por isso que esquecer esta linha seria defeito
                # silencioso (023, FR-010a).
                "stages": [
                    trocar(etapa, "classificationMilestones[].stages[]")
                    for etapa in marco.get("stages") or []
                ],
            }
            metodo = marco.get("drawMethod")
            if metodo and metodo.get("qualifyingStageId") is not None:
                novo_marco["drawMethod"] = {
                    **metodo,
                    "qualifyingStageId": trocar(
                        metodo["qualifyingStageId"], "drawMethod.qualifyingStageId"
                    ),
                }
            criterios = []
            for criterio in marco.get("tiebreakers") or []:
                parametros = dict(criterio.get("parameters") or {})
                for chave in ("stageId", "factId"):
                    if parametros.get(chave) is not None:
                        parametros[chave] = trocar(parametros[chave], f"tiebreakers[].{chave}")
                criterios.append(
                    {
                        **criterio,
                        "id": trocar(criterio.get("id"), "tiebreakers[].id"),
                        "parameters": parametros,
                    }
                )
            novo_marco["tiebreakers"] = criterios
            marcos.append(novo_marco)
        novo_perfil["classificationMilestones"] = marcos
        perfis.append(novo_perfil)

    return {
        **conteudo,
        "profiles": perfis,
        "schedule": [
            {**evento, "id": trocar(evento.get("id"), "schedule[].id")}
            for evento in conteudo.get("schedule") or []
        ],
        "stages": [
            {
                **etapa,
                "id": trocar(etapa.get("id"), "stages[].id"),
                "scheduleEventId": trocar(etapa.get("scheduleEventId"), "stages[].scheduleEventId"),
            }
            for etapa in conteudo.get("stages") or []
        ],
        "documentRequirements": [
            {
                **documento,
                "id": trocar(documento.get("id"), "documentRequirements[].id"),
                "profileId": trocar(documento.get("profileId"), "documentRequirements[].profileId"),
                "modalityId": trocar(
                    documento.get("modalityId"), "documentRequirements[].modalityId"
                ),
                "attachmentId": trocar(
                    documento.get("attachmentId"), "documentRequirements[].attachmentId"
                ),
            }
            for documento in conteudo.get("documentRequirements") or []
        ],
        "attachments": [
            {**anexo, "id": trocar(anexo.get("id"), "attachments[].id")}
            for anexo in conteudo.get("attachments") or []
        ],
    }


def converter_valores(conteudo):
    """Texto de volta a instante e a decimal, nos campos em que o rascunho espera objeto.

    **Só nos campos nomeados**, e nunca por varredura de formato: converter o que se parece com uma
    data transformaria em data qualquer texto que se pareça com uma.
    """

    def instante(valor):
        return parse_datetime(valor) if isinstance(valor, str) else valor

    def decimal(valor):
        return Decimal(valor) if isinstance(valor, str) else valor

    perfis = []
    for perfil in conteudo.get("profiles") or []:
        modalidades = []
        for modalidade in perfil.get("competitionModalities") or []:
            regra = modalidade.get("normativeRule")
            if regra:
                modalidade = {
                    **modalidade,
                    "normativeRule": {
                        **regra,
                        "effectiveFrom": instante(regra.get("effectiveFrom")),
                    },
                }
            modalidades.append(modalidade)
        perfis.append({**perfil, "competitionModalities": modalidades})

    return {
        **conteudo,
        "profiles": perfis,
        "schedule": [
            {
                **evento,
                "startAt": instante(evento.get("startAt")),
                "endAt": instante(evento.get("endAt")),
            }
            for evento in conteudo.get("schedule") or []
        ],
        "stages": [
            {**etapa, **{campo: decimal(etapa.get(campo)) for campo in DECIMAIS_DA_ETAPA}}
            for etapa in conteudo.get("stages") or []
        ],
    }


def payload_do_conteudo(conteudo):
    """As cinco coleções que `replace_draft` aceita, já sem o que não se copia.

    O que sai daqui: os campos sem tela (`FR-008`), a identificação do Edital — que é entrada da
    criação, e não conteúdo a copiar (`FR-007`) —, as Seções geradas, e o `status` do Evento, que
    descreve o que **aconteceu** e por isso reinicia (`FR-008a`).
    """
    perfis = [
        {chave: valor for chave, valor in perfil.items() if chave not in CAMPOS_SEM_TELA}
        for perfil in conteudo.get("profiles") or []
    ]
    return {
        "profiles": perfis,
        "schedule": [
            {**evento, "status": "PLANEJADO"} for evento in conteudo.get("schedule") or []
        ],
        "stages": list(conteudo.get("stages") or []),
        # Só as textuais: a gerada não carrega texto, e persistir o que é derivado criaria dois
        # endereços para o mesmo conteúdo normativo (006, FR-036).
        "sections": [
            {"key": secao["key"], "content": secao.get("content") or ""}
            for secao in conteudo.get("sections") or []
            if secoes_do_catalogo.e_textual(secao.get("key") or "")
        ],
        "documentRequirements": list(conteudo.get("documentRequirements") or []),
    }
