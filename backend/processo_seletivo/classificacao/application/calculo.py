"""Leitura do universo e cálculo da ordem, sem gravar ato, posição ou auditoria.

Todas as consultas acontecem antes do laço de participantes. Em particular, as Versões citadas
pelos Resultados são resolvidas uma vez por identidade distinta: fazer ``select_related('versao')``
traria uma cópia do JSON inteiro do Edital por Resultado sem alterar a contagem de consultas.
"""

from collections import defaultdict

from processo_seletivo.classificacao.domain.combinacao import SEM_PONTUACAO, combinar
from processo_seletivo.classificacao.domain.desempate import ordenar
from processo_seletivo.inscricoes.models import Inscricao, ValorDeFato
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.resultados.application.prontidao import restringir_a_participantes
from processo_seletivo.resultados.application.selectors import conteudos_das_versoes
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError


def calcular_ordem(*, edital, perfil_id, marco_id, at=None):
    """Calcula a proposta vigente de um marco e devolve sua proveniência em memória.

    A função é deliberadamente read-only. Quem emite chama o mesmo cálculo dentro do comando
    transacional; abrir a tela pode chamá-la quantas vezes quiser sem constituir ato algum.
    """
    versao = effective_version(edital_id=edital.id, at=at)
    conteudo = versao.content
    perfil = _por_identidade(conteudo.get("profiles"), perfil_id)
    marco = _por_identidade(perfil.get("classificationMilestones") if perfil else None, marco_id)
    if perfil is None or marco is None:
        raise DomainError("not_found", "Recurso não encontrado.", 404)

    etapas = {str(item["id"]): item for item in conteudo.get("stages") or []}
    enumeradas = [str(item) for item in marco.get("stages") or []]
    etapa_do_marco = _ultima_etapa(enumeradas, etapas)

    # A progressão é aplicada no próprio queryset: nenhuma lista integral é lida uma segunda vez
    # só para ser devolvida em ``id__in``. O conjunto inclui quem foi eliminado na Etapa do marco
    # e exclui quem já havia sido eliminado antes dela.
    consulta = Inscricao.objects.filter(
        edital=edital,
        profile_id=perfil["id"],
        status=Inscricao.Status.SUBMETIDA,
    )
    consulta = restringir_a_participantes(
        consulta,
        edital=edital,
        etapa_id=etapa_do_marco["id"],
        vigentes={_uuid_da_etapa(chave): valor for chave, valor in etapas.items()},
        prefixo="",
    )
    inscricoes = list(
        consulta.order_by("id").values("id", "protocolo", "nome", "identity_subject", "modality_id")
    )
    inscricoes_ids = [item["id"] for item in inscricoes]

    resultados = list(
        ResultadoEtapa.objects.filter(
            edital=edital,
            inscricao_id__in=inscricoes_ids,
            etapa_id__in=enumeradas,
        ).values(
            "id",
            "inscricao_id",
            "etapa_id",
            "versao_id",
            "pontuacao",
            "consequencia",
            "motivo",
            "consolidado_em",
        )
    )
    # Uma linha por versão distinta, e nenhuma cópia do conteúdo dentro da consulta de Resultados.
    conteudos_historicos = conteudos_das_versoes({item["versao_id"] for item in resultados})
    _conferir_ancoras_dos_resultados(resultados, conteudos_historicos)

    fatos_ids = _fatos_consumidos(marco)
    fatos = list(
        ValorDeFato.objects.filter(
            inscricao_id__in=inscricoes_ids,
            fato_id__in=fatos_ids,
        ).values("inscricao_id", "fato_id", "valor_data", "valor_inteiro")
    )

    resultados_por_inscricao = defaultdict(list)
    for resultado in resultados:
        resultados_por_inscricao[resultado["inscricao_id"]].append(resultado)
    fatos_por_inscricao = defaultdict(dict)
    for fato in fatos:
        fatos_por_inscricao[fato["inscricao_id"]][str(fato["fato_id"])] = (
            fato["valor_data"] if fato["valor_data"] is not None else fato["valor_inteiro"]
        )

    classificaveis, sem_posicao = [], []
    for inscricao in inscricoes:
        da_inscricao = resultados_por_inscricao[inscricao["id"]]
        pontuacoes = {
            str(resultado["etapa_id"]): resultado["pontuacao"] for resultado in da_inscricao
        }
        base = {
            "inscricao_id": str(inscricao["id"]),
            "protocolo": inscricao["protocolo"],
            "nome": inscricao["nome"],
            "identity_subject": inscricao["identity_subject"],
            "modalidade_id": (str(inscricao["modality_id"]) if inscricao["modality_id"] else None),
            "pontuacoes": pontuacoes,
            "fatos": fatos_por_inscricao[inscricao["id"]],
            "resultados": [str(resultado["id"]) for resultado in da_inscricao],
        }
        eliminacao = _eliminacao_mais_recente(da_inscricao, etapas)
        if eliminacao is not None:
            sem_posicao.append(
                {
                    **base,
                    "posicao": None,
                    "pontuacao": None,
                    "consequencia": eliminacao["consequencia"],
                    "motivo": eliminacao["motivo"],
                    "empate_residual": False,
                    "separado_por": None,
                }
            )
            continue

        pontuacao = combinar(marco, etapas, pontuacoes)
        if pontuacao is SEM_PONTUACAO:
            sem_posicao.append(
                {
                    **base,
                    "posicao": None,
                    "pontuacao": None,
                    "consequencia": "",
                    "motivo": _motivo_da_pontuacao_ausente(enumeradas, pontuacoes, etapas),
                    "empate_residual": False,
                    "separado_por": None,
                }
            )
            continue
        classificaveis.append(
            {
                **base,
                "pontuacao": pontuacao,
                "consequencia": ResultadoEtapa.Consequencia.HABILITADA,
                "motivo": "",
            }
        )

    posicoes = ordenar(classificaveis, marco.get("tiebreakers") or [])
    return {
        "edital": edital,
        "versao": versao,
        "perfil": perfil,
        "marco": marco,
        "etapas": etapas,
        "posicoes": posicoes,
        "sem_posicao": sem_posicao,
        "universo": _resumo_do_universo(edital, perfil, marco, versao, inscricoes, resultados),
    }


def _por_identidade(itens, identidade):
    alvo = str(identidade)
    return next((item for item in itens or [] if str(item.get("id")) == alvo), None)


def _uuid_da_etapa(valor):
    from uuid import UUID

    return UUID(str(valor))


def _ultima_etapa(enumeradas, etapas):
    existentes = [etapas[item] for item in enumeradas if item in etapas]
    if not existentes:
        raise DomainError(
            "marco_sem_etapa",
            "O marco não enumera uma Etapa publicada executável.",
            422,
        )
    return max(existentes, key=lambda item: item.get("order") or 0)


def _conferir_ancoras_dos_resultados(resultados, conteudos):
    """Cada Resultado precisa citar uma versão em que a sua Etapa realmente existia."""
    for resultado in resultados:
        conteudo = conteudos.get(resultado["versao_id"])
        if (
            conteudo is None
            or _por_identidade(conteudo.get("stages"), resultado["etapa_id"]) is None
        ):
            raise DomainError(
                "resultado_sem_norma",
                "Um Resultado do universo não encontra sua Etapa na versão que o fundamentou.",
                409,
            )


def _fatos_consumidos(marco):
    return {
        str((criterio.get("parameters") or {}).get("factId"))
        for criterio in marco.get("tiebreakers") or []
        if (criterio.get("parameters") or {}).get("factId")
    }


def _eliminacao_mais_recente(resultados, etapas):
    eliminadas = [
        item for item in resultados if item["consequencia"] == ResultadoEtapa.Consequencia.ELIMINADA
    ]
    if not eliminadas:
        return None
    return max(
        eliminadas,
        key=lambda item: (etapas.get(str(item["etapa_id"])) or {}).get("order") or 0,
    )


def _motivo_da_pontuacao_ausente(enumeradas, pontuacoes, etapas):
    faltantes = [
        (etapas.get(etapa_id) or {}).get("name") or etapa_id
        for etapa_id in enumeradas
        if pontuacoes.get(etapa_id) is None
    ]
    return "Sem pontuação nas Etapas enumeradas: " + ", ".join(faltantes) + "."


def _resumo_do_universo(edital, perfil, marco, versao, inscricoes, resultados):
    return {
        "processoId": str(edital.processo_id),
        "editalId": str(edital.id),
        "profileId": str(perfil["id"]),
        "milestoneId": str(marco["id"]),
        "versionId": str(versao.id),
        "participants": [str(item["id"]) for item in inscricoes],
        "stageResults": [
            {
                "id": str(item["id"]),
                "registrationId": str(item["inscricao_id"]),
                "stageId": str(item["etapa_id"]),
                "versionId": str(item["versao_id"]),
                "consolidatedAt": item["consolidado_em"].isoformat(),
            }
            for item in sorted(resultados, key=lambda item: str(item["id"]))
        ],
    }


__all__ = ["calcular_ordem"]
