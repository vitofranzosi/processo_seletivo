"""Leitura do vigente, da proposta atual e da divergência entre os dois."""

from django.core.paginator import Paginator
from django.db.models import F

from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.classificacao.domain.universo import (
    comparar,
    por_identidade,
    recorte_da_regra,
)
from processo_seletivo.classificacao.models import AtoDeOrdenacao, PosicaoNaOrdem
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.shared.api.problems import DomainError


def ato_vigente(*, edital, marco_id):
    """O ato sem sucessor, derivado da cadeia append-only."""
    return (
        AtoDeOrdenacao.objects.filter(
            edital=edital,
            marco_id=marco_id,
            sucessores__isnull=True,
        )
        .select_related("versao")
        .order_by("-emitido_em")
        .first()
    )


def historico(*, edital, marco_id):
    return list(
        AtoDeOrdenacao.objects.filter(edital=edital, marco_id=marco_id)
        .select_related("versao", "ato_anterior")
        .order_by("-emitido_em")
    )


def ato_por_id(*, edital, marco_id, ato_id):
    return (
        AtoDeOrdenacao.objects.filter(
            pk=ato_id,
            edital=edital,
            marco_id=marco_id,
        )
        .select_related("versao", "ato_anterior")
        .first()
    )


def estado_do_marco(*, edital, marco_id, at=None):
    """A proposta de agora ao lado do ato vigente, sem escrever nenhum dos dois."""
    vigente = ato_vigente(edital=edital, marco_id=marco_id)
    versao_atual = effective_version(edital_id=edital.id, at=at)
    perfil, marco = _marco_na_versao(versao_atual.content, marco_id)

    if marco is None:
        if vigente is None:
            raise DomainError("not_found", "Recurso não encontrado.", 404)
        perfil_historico, marco_historico = _marco_na_versao(
            vigente.versao.content,
            marco_id,
        )
        return {
            "proposta": None,
            "vigente": vigente,
            "perfil": perfil_historico or {"id": str(vigente.perfil_id), "name": "Perfil"},
            "marco": marco_historico or {"id": str(vigente.marco_id), "name": "Marco removido"},
            "obsoleto": True,
            "recomputavel": False,
            "divergencias": [
                {
                    "tipo": "regra_ausente",
                    "descricao": (
                        "O marco não existe na norma vigente; "
                        "não há regra vigente com que comparar."
                    ),
                }
            ],
            "posicoes_divergentes": [],
        }

    proposta = calcular_ordem(
        edital=edital,
        perfil_id=perfil["id"],
        marco_id=marco_id,
        at=at,
    )
    divergencias = []
    if vigente is not None:
        divergencias = comparar(
            gravado=vigente.universo,
            atual=proposta["universo"],
            regra_gravada=recorte_da_regra(
                vigente.versao.content,
                perfil_id=vigente.perfil_id,
                marco_id=vigente.marco_id,
            ),
            regra_atual=recorte_da_regra(
                versao_atual.content,
                perfil_id=perfil["id"],
                marco_id=marco_id,
            ),
        )
    return {
        "proposta": proposta,
        "vigente": vigente,
        "perfil": perfil,
        "marco": marco,
        "obsoleto": bool(divergencias),
        "recomputavel": True,
        "divergencias": divergencias,
        "posicoes_divergentes": (
            _divergencias_das_posicoes(vigente, proposta) if vigente is not None else []
        ),
    }


def posicoes_do_ato(*, ato, pagina=1, por_pagina=50):
    """Snapshot paginado; valores nulos vêm depois da ordem classificatória."""
    consulta = (
        PosicaoNaOrdem.objects.filter(ato=ato)
        .select_related("inscricao")
        .order_by(
            F("posicao").asc(nulls_last=True),
            "inscricao__protocolo",
            "inscricao_id",
        )
    )
    return Paginator(consulta, por_pagina).get_page(pagina)


def _marco_na_versao(conteudo, marco_id):
    alvo = str(marco_id)
    for perfil in conteudo.get("profiles") or []:
        marco = por_identidade(perfil.get("classificationMilestones"), alvo)
        if marco is not None:
            return perfil, marco
    return None, None


def _divergencias_das_posicoes(ato, proposta):
    """Mudanças linha a linha entre o snapshot e a proposta calculada agora."""
    antes = {
        str(item["inscricao_id"]): item
        for item in PosicaoNaOrdem.objects.filter(ato=ato).values(
            "inscricao_id",
            "posicao",
            "pontuacao_combinada",
            "consequencia",
            "motivo",
            "empate_residual",
        )
    }
    depois = {item["inscricao_id"]: item for item in proposta["posicoes"] + proposta["sem_posicao"]}
    divergencias = []
    for inscricao_id in sorted(set(antes) | set(depois)):
        anterior = antes.get(inscricao_id)
        atual = depois.get(inscricao_id)
        assinatura_anterior = (
            None
            if anterior is None
            else (
                anterior["posicao"],
                anterior["pontuacao_combinada"],
                anterior["consequencia"],
                anterior["motivo"],
                anterior["empate_residual"],
            )
        )
        assinatura_atual = (
            None
            if atual is None
            else (
                atual["posicao"],
                atual["pontuacao"],
                atual["consequencia"],
                atual["motivo"],
                atual["empate_residual"],
            )
        )
        if assinatura_anterior != assinatura_atual:
            divergencias.append(
                {
                    "inscricao_id": inscricao_id,
                    "antes": anterior,
                    "agora": atual,
                }
            )
    return divergencias


__all__ = ["ato_por_id", "ato_vigente", "estado_do_marco", "historico", "posicoes_do_ato"]
