"""Reproduz um ato apenas de sua versão histórica e da proveniência que ele congelou."""

from datetime import date
from decimal import Decimal

from processo_seletivo.classificacao.domain.combinacao import SEM_PONTUACAO, combinar
from processo_seletivo.classificacao.domain.desempate import ordenar
from processo_seletivo.classificacao.domain.universo import por_identidade
from processo_seletivo.classificacao.models import PosicaoNaOrdem
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError


def reproduzir_ato(ato):
    """Calcula novamente as posições sem consultar conteúdo ou Resultados vigentes.

    Os Resultados são buscados exclusivamente pelos identificadores congelados em ``universo``;
    linhas tardias não entram. Os fatos vêm da proveniência de desempate da própria posição, e a
    regra vem de ``ato.versao``. A posição gravada nunca é usada como entrada do motor.
    """
    conteudo = ato.versao.content
    perfil = por_identidade(conteudo.get("profiles"), ato.perfil_id)
    marco = por_identidade(
        perfil.get("classificationMilestones") if perfil else None,
        ato.marco_id,
    )
    if marco is None:
        raise DomainError(
            "historical_rule_missing",
            "A versão histórica do ato não contém o marco que deveria reproduzi-lo.",
            409,
        )
    etapas = {str(item["id"]): item for item in conteudo.get("stages") or []}
    ids_resultados = [item["id"] for item in ato.universo.get("stageResults") or []]
    resultados = list(
        ResultadoEtapa.objects.filter(pk__in=ids_resultados).values(
            "id",
            "inscricao_id",
            "etapa_id",
            "pontuacao",
            "consequencia",
            "motivo",
        )
    )
    if len(resultados) != len(set(ids_resultados)):
        raise DomainError(
            "historical_input_missing",
            "A proveniência cita Resultado histórico que não está disponível.",
            409,
        )
    por_inscricao = {}
    for resultado in resultados:
        por_inscricao.setdefault(str(resultado["inscricao_id"]), []).append(resultado)

    snapshots = list(PosicaoNaOrdem.objects.filter(ato=ato).order_by("inscricao_id"))
    fatos_publicados = {str(item["id"]): item for item in (perfil.get("declaredFacts") or [])}
    classificaveis, sem_posicao = [], []
    for snapshot in snapshots:
        inscricao_id = str(snapshot.inscricao_id)
        da_inscricao = por_inscricao.get(inscricao_id, [])
        pontuacoes = {
            str(resultado["etapa_id"]): resultado["pontuacao"] for resultado in da_inscricao
        }
        fatos = _fatos_da_proveniencia(snapshot.desempate, marco, fatos_publicados)
        base = {
            "inscricao_id": inscricao_id,
            "pontuacoes": pontuacoes,
            "fatos": fatos,
        }
        eliminacao = next(
            (
                item
                for item in da_inscricao
                if item["consequencia"] == ResultadoEtapa.Consequencia.ELIMINADA
            ),
            None,
        )
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
                    "motivo": snapshot.motivo,
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
    return {
        "posicoes": ordenar(classificaveis, marco.get("tiebreakers") or []),
        "sem_posicao": sem_posicao,
    }


def divergencias_da_reproducao(ato, *, reproduzido=None):
    """Diferenças detectáveis entre o motor histórico e o snapshot emitido."""
    reproduzido = reproduzido or reproduzir_ato(ato)
    atual = {
        item["inscricao_id"]: (
            item["posicao"],
            item["pontuacao"],
            item["empate_residual"],
        )
        for item in reproduzido["posicoes"] + reproduzido["sem_posicao"]
    }
    gravado = {
        str(item.inscricao_id): (
            item.posicao,
            item.pontuacao_combinada,
            item.empate_residual,
        )
        for item in PosicaoNaOrdem.objects.filter(ato=ato)
    }
    return [
        {"inscricao_id": chave, "gravado": gravado.get(chave), "reproduzido": atual.get(chave)}
        for chave in sorted(set(gravado) | set(atual))
        if gravado.get(chave) != atual.get(chave)
    ]


def _fatos_da_proveniencia(proveniencia, marco, fatos_publicados):
    por_criterio = {str(item.get("criterionId")): item.get("value") for item in proveniencia or []}
    fatos = {}
    for criterio in marco.get("tiebreakers") or []:
        fato_id = str((criterio.get("parameters") or {}).get("factId") or "")
        if not fato_id:
            continue
        valor = por_criterio.get(str(criterio.get("id")))
        tipo = (fatos_publicados.get(fato_id) or {}).get("type")
        if valor is not None and tipo == "INTEIRO":
            valor = int(valor)
        elif valor is not None and tipo == "DATA":
            valor = date.fromisoformat(valor)
        elif valor is not None:
            valor = Decimal(str(valor))
        fatos[fato_id] = valor
    return fatos


__all__ = ["divergencias_da_reproducao", "reproduzir_ato"]
