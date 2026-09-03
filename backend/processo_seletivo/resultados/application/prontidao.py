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

from django.db.models import Exists, OuterRef

from processo_seletivo.avaliacoes.application.selectors import avaliacoes_elegiveis
from processo_seletivo.comissoes.domain.etapas import etapas_vigentes as etapas_vigentes_do_edital
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
from processo_seletivo.resultados.models import ResultadoEtapa

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


def participacao(*, edital, etapa_id, vigentes=None):
    """`(participantes, eliminadas, aguardando)` — as duas regras de D-003, nesta ordem.

    **É a única fonte da participação**, e é por isso que ela vive aqui e não em cada superfície.
    A distribuição, a Mesa, a inscrição de trabalho, o documento e a próxima pendente perguntam
    todas a mesma coisa, e a resposta precisa ser a mesma nas cinco — senão a organização exclui e
    a Mesa entrega, que é a pior combinação possível.

    `vigentes` chega por parâmetro quando quem chama já o resolveu: a tela da Etapa lê o conteúdo
    publicado uma vez e o entrega, em vez de cada seletor relê-lo.
    """
    if vigentes is None:
        vigentes = etapas_vigentes_do_edital(edital)
    submetidas = set(
        Inscricao.objects.filter(edital=edital, status=Inscricao.Status.SUBMETIDA).values_list(
            "id", flat=True
        )
    )
    anteriores = [identidade for identidade, _ in etapas_anteriores(vigentes, etapa_id)]
    eliminadas = eliminadas_ate(edital=edital, etapas_ids=anteriores) & submetidas

    aguardando = set()
    imediata = etapa_anterior(vigentes, etapa_id)
    # O gate, e só ele: a exigência de habilitação fica dormente enquanto a Etapa anterior não
    # produziu Resultado nenhum. A exclusão por eliminação, acima, não tem gate.
    if imediata is not None and ha_resultado_em(edital=edital, etapa_id=imediata[0]):
        habilitadas = habilitadas_em(edital=edital, etapa_id=imediata[0])
        aguardando = submetidas - eliminadas - habilitadas
    return submetidas - eliminadas - aguardando, eliminadas, aguardando


def _anteriores_e_gate(edital, etapa_id, vigentes=None):
    """`(identidades anteriores, identidade da imediata quando a exigência vigora)`.

    Uma leitura do conteúdo publicado e, no máximo, uma pergunta de existência. É todo o custo fixo
    que a progressão impõe às superfícies da 012 — o resto vira junção dentro da consulta que já ia
    acontecer.
    """
    if vigentes is None:
        vigentes = etapas_vigentes_do_edital(edital)
    anteriores = [identidade for identidade, _ in etapas_anteriores(vigentes, etapa_id)]
    imediata = etapa_anterior(vigentes, etapa_id)
    exigir = (
        imediata[0]
        if imediata is not None and ha_resultado_em(edital=edital, etapa_id=imediata[0])
        else None
    )
    return anteriores, exigir


def restringir_a_participantes(consulta, *, edital, etapa_id, vigentes=None, prefixo="inscricao"):
    """Aplica as duas regras de D-003 a um queryset que já fala de inscrições.

    **Restringir a consulta, e não materializar o conjunto.** Devolver ids e passá-los em `__in`
    custaria duas leituras completas de população por listagem, e as superfícies da 012 têm
    orçamento de consulta declarado em teste — a 011 e a 012 os escreveram justamente para que uma
    feature seguinte não os corroesse em silêncio. Dobradas em junção, as duas regras não custam
    round-trip nenhum: o que sobra é a leitura do conteúdo publicado e a pergunta do gate.

    `prefixo` diz como o queryset alcança a inscrição — `"inscricao"` a partir de `Atribuicao`,
    `""` quando a própria linha é a inscrição.

    **Subconsulta correlacionada, e não `exclude()` com dois campos.** A primeira redação usava
    `exclude(rel__etapa_id__in=..., rel__consequencia=ELIMINADA)`, e Django **não** garante que as
    duas condições recaiam sobre a mesma linha relacionada: ele gera dois `EXISTS` independentes.
    O efeito é uma exclusão indevida — quem foi eliminado numa Etapa *posterior* e habilitado numa
    anterior satisfaz as duas metades separadamente, e sairia do conjunto de uma Etapa em que
    deveria estar. `Exists` amarra Etapa e consequência na mesma linha, que é o que a regra diz.
    """
    anteriores, exigir = _anteriores_e_gate(edital, etapa_id, vigentes)
    referencia = OuterRef(f"{prefixo}_id") if prefixo else OuterRef("pk")
    if anteriores:
        # Regra 1, sem gate: eliminada em qualquer Etapa anterior está fora, sempre.
        consulta = consulta.filter(
            ~Exists(
                ResultadoEtapa.objects.filter(
                    inscricao_id=referencia,
                    etapa_id__in=anteriores,
                    consequencia=ResultadoEtapa.Consequencia.ELIMINADA,
                )
            )
        )
    if exigir is not None:
        # Regra 2, com gate: só depois que a imediatamente anterior produziu Resultado.
        consulta = consulta.filter(
            Exists(
                ResultadoEtapa.objects.filter(
                    inscricao_id=referencia,
                    etapa_id=exigir,
                    consequencia=ResultadoEtapa.Consequencia.HABILITADA,
                )
            )
        )
    return consulta


def participa_da_etapa(*, edital, etapa_id, inscricao_id, vigentes=None):
    """A mesma pergunta, para **uma** inscrição — na rota individual, onde ela cabe.

    Duas perguntas de existência no pior caso, e nenhuma listagem passa por aqui: o docstring de
    `autorizacao.py` registra que listagem usa a forma em conjunto, e é ela que está acima.
    """
    anteriores, exigir = _anteriores_e_gate(edital, etapa_id, vigentes)
    if (
        anteriores
        and ResultadoEtapa.objects.filter(
            inscricao_id=inscricao_id,
            etapa_id__in=anteriores,
            consequencia=ResultadoEtapa.Consequencia.ELIMINADA,
        ).exists()
    ):
        return False
    if exigir is None:
        return True
    return ResultadoEtapa.objects.filter(
        inscricao_id=inscricao_id,
        etapa_id=exigir,
        consequencia=ResultadoEtapa.Consequencia.HABILITADA,
    ).exists()


def panorama_da_etapa(*, edital, etapa, etapas_vigentes):
    """Participação e prontidão da Etapa inteira, em consultas de número constante.

    Devolve `estados` como `{inscricao_id: (estado, motivo)}` cobrindo **toda** inscrição
    submetida, mais o impedimento da Etapa quando ele existe. É a única fonte dos números: o resumo
    conta a partir daqui, e a listagem filtra a partir daqui, de modo que os dois não podem
    divergir.
    """
    participantes, eliminadas, aguardando = participacao(
        edital=edital, etapa_id=etapa["id"], vigentes=etapas_vigentes
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
