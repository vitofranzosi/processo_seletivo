"""Quem participa da Etapa, e o que impede cada um de ser consolidado.

Uma leitura, um número de consultas **constante**, e uma partição: cada participante ocupa
exatamente um estado, e a soma deles é o total. Sem isso, resumo e detalhe filtrado divergiriam, e
a presidência teria dois números para a mesma Etapa.

**Por que a classificação é Python sobre conjuntos, e não SQL.** A compatibilidade normativa
compara conteúdo publicado de duas Versões Consolidadas; isso não se exprime em agregação. O que
não se pode é pagar uma consulta por inscrição — e não se paga: o conjunto elegível vem numa
consulta só, com a versão junto, e a comparação acontece em memória sobre ele.

**A participação tem duas regras, e elas têm alcances diferentes** (D-003). A eliminação em
qualquer Etapa anterior exclui sempre; a exigência de habilitação é da imediatamente anterior e só
vale depois que ela produz Resultado. Enquanto não produz, a Etapa seguinte conserva o conjunto da
012 — e é isso que impede esta feature de esvaziar permanentemente a Etapa seguinte de um Edital de
leitura múltipla, que a V1 não consolida.
"""

from processo_seletivo.avaliacoes.application.selectors import avaliacoes_elegiveis
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.resultados.application.selectors import (
    eliminadas_ate,
    ha_resultado_em,
    habilitadas_em,
    resultados_por_inscricao,
)
from processo_seletivo.resultados.domain.compatibilidade import incompatibilidade
from processo_seletivo.resultados.domain.progressao import etapa_anterior, etapas_anteriores
from processo_seletivo.resultados.domain.regra import impedimento_da_regra

# Os cinco estados de prontidão. Formam partição: toda inscrição submetida do Edital ocupa um, e
# apenas um. `PENDENTE` e `CONSOLIDADO` da spec aparecem aqui como ausência e presença de linha —
# não há coluna de workflow, e ela não diria nada que a existência do Resultado já não diga.
ELIMINADA_ANTES = "eliminada-antes"
AGUARDANDO_ANTERIOR = "aguardando-anterior"
CONSOLIDADA = "consolidada"
PRONTA = "pronta"
IMPEDIDA = "impedida"

SEM_CONCLUSAO = "ainda não há avaliação concluída para esta inscrição"
CONCLUSOES_DEMAIS = (
    "há {quantas} avaliações concluídas onde o Edital prevê uma, e o sistema não escolhe qual vale"
)


def _participacao(*, edital, etapa, etapas_vigentes):
    """`(participantes, eliminadas, aguardando)` — as duas regras de D-003, nesta ordem."""
    submetidas = set(
        Inscricao.objects.filter(edital=edital, status=Inscricao.Status.SUBMETIDA).values_list(
            "id", flat=True
        )
    )
    anteriores = [identidade for identidade, _ in etapas_anteriores(etapas_vigentes, etapa["id"])]
    eliminadas = eliminadas_ate(edital=edital, etapas_ids=anteriores) & submetidas

    aguardando = set()
    imediata = etapa_anterior(etapas_vigentes, etapa["id"])
    # O gate, e só ele: a exigência de habilitação fica dormente enquanto a Etapa anterior não
    # produziu Resultado nenhum. A exclusão por eliminação, acima, não tem gate.
    if imediata is not None and ha_resultado_em(edital=edital, etapa_id=imediata[0]):
        habilitadas = habilitadas_em(edital=edital, etapa_id=imediata[0])
        aguardando = submetidas - eliminadas - habilitadas
    return submetidas - eliminadas - aguardando, eliminadas, aguardando


def panorama_da_etapa(*, edital, etapa, etapas_vigentes):
    """Participação e prontidão da Etapa inteira, em consultas de número constante.

    Devolve `estados` como `{inscricao_id: (estado, motivo)}` cobrindo **toda** inscrição
    submetida, mais o impedimento da Etapa quando ele existe. É a única fonte dos números: o resumo
    conta a partir daqui, e a listagem filtra a partir daqui, de modo que os dois não podem
    divergir.
    """
    participantes, eliminadas, aguardando = _participacao(
        edital=edital, etapa=etapa, etapas_vigentes=etapas_vigentes
    )
    resultados = resultados_por_inscricao(edital=edital, etapa_id=etapa["id"])
    impedimento = impedimento_da_regra(etapa)

    elegiveis = {}
    if impedimento is None:
        for avaliacao in avaliacoes_elegiveis(edital=edital, etapa_id=etapa["id"]):
            elegiveis.setdefault(avaliacao.inscricao_id, []).append(avaliacao)

    estados = {}
    for identidade in eliminadas:
        estados[identidade] = (ELIMINADA_ANTES, "eliminada em Etapa anterior")
    for identidade in aguardando:
        estados[identidade] = (AGUARDANDO_ANTERIOR, "aguardando o resultado da Etapa anterior")
    for identidade in participantes:
        estados[identidade] = _estado_do_participante(
            identidade, etapa, resultados, elegiveis, impedimento
        )
    panorama = {
        "participantes": participantes,
        "eliminadas": eliminadas,
        "aguardando": aguardando,
        "resultados": resultados,
        "elegiveis": elegiveis,
        "impedimento_da_etapa": impedimento,
        "estados": estados,
    }
    # As contagens viajam **dentro** do panorama porque o resumo as lê daqui: um segundo cálculo,
    # em outro lugar, é exatamente o painel paralelo que D-004 recusa.
    panorama["contagens"] = contagens(panorama)
    return panorama


def _estado_do_participante(identidade, etapa, resultados, elegiveis, impedimento):
    if identidade in resultados:
        # Já consolidada vem antes de tudo: reconsolidar não é o caminho normal esbarrando numa
        # regra, e apresentá-la como "pronta" convidaria a um ato que será recusado.
        return (CONSOLIDADA, "esta inscrição já possui Resultado nesta Etapa")
    if impedimento is not None:
        return (IMPEDIDA, impedimento[1])
    conclusoes = elegiveis.get(identidade, [])
    if not conclusoes:
        return (IMPEDIDA, SEM_CONCLUSAO)
    if len(conclusoes) > 1:
        # Só alcançável quando a quantidade prevista mudou depois das conclusões. Escolher uma
        # seria o sistema decidindo qual nota vale.
        return (IMPEDIDA, CONCLUSOES_DEMAIS.format(quantas=len(conclusoes)))
    divergencia = incompatibilidade(
        versao=conclusoes[0].versao, etapa_id=etapa["id"], etapa_vigente=etapa
    )
    if divergencia is not None:
        return (IMPEDIDA, divergencia[1])
    return (PRONTA, "pronta para consolidar")


def contagens(panorama):
    """Os totais da Etapa, derivados do mesmo dicionário que a listagem filtra.

    A partição é verificável por construção: `participantes + eliminadas + aguardando` é o total, e
    os quatro estados dos participantes somam `participantes`.
    """
    por_estado = {estado: 0 for estado in (CONSOLIDADA, PRONTA, IMPEDIDA)}
    for estado, _ in panorama["estados"].values():
        if estado in por_estado:
            por_estado[estado] += 1
    return {
        "participantes": len(panorama["participantes"]),
        "eliminadas_antes": len(panorama["eliminadas"]),
        "aguardando_anterior": len(panorama["aguardando"]),
        "consolidadas": por_estado[CONSOLIDADA],
        "prontas": por_estado[PRONTA],
        "impedidas": por_estado[IMPEDIDA],
        "total": len(panorama["estados"]),
    }
