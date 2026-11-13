"""De que versão é o «antes» (123, M3, R-009).

A tela Retificar compõe sobre a **última versão publicada** — a de maior início de vigência —, e é
o certo: é a base que a precondição da publicação espera. O defeito estava no nome. A coluna dizia
"Vigente hoje", e com uma Retificação publicada de vigência futura mostrava um término que ainda não
vigorava (`RU-04` da auditoria de 05/11/2026). Quem homologa e quem publica liam o mesmo «Antes».

Aqui a base se descreve pelo que ela **é**, e não pelo que se supõe dela:

- **o que ela incorpora** — a Publicação original e as Retificações que a versão registra ter
  aplicado (`applied_publications`), a mesma leitura que a consolidação do documento faz para dizer
  "retificado em" (054). Não pela `source_publication`: depois de uma publicação fora de ordem de
  vigência, a publicação que materializou a versão não é "a Retificação da base" (D-006);
- **a situação de vigência**, no instante da tela: vigora, ainda não vigora, ou já foi sucedida.

A numeração é a do detalhe do Edital: "Retificação nº N", com N a ordem da publicação no Edital — a
Publicação original é a nº 1 (D-006). Nada aqui escolhe a base nem a muda (FR-3936).
"""

from dataclasses import dataclass

from django.db.models import Q
from django.utils import timezone

from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.tempo import ZONA

VIGORA = "VIGORA"
FUTURA = "FUTURA"
SUCEDIDA = "SUCEDIDA"


@dataclass(frozen=True)
class RetificacaoIncorporada:
    numero: int
    publicada_em: object


@dataclass(frozen=True)
class DescricaoDaVersaoBase:
    original_em: object
    retificacoes: tuple
    situacao: str
    inicio: object


def descrever_versao_base(versao, agora=None):
    """A frase da base, em dados: o que ela incorpora, quando começa e se vigora agora.

    Até quatro consultas, nenhuma por item: as publicações (original e aplicadas, numa só), a versão
    em vigor — pela mesma `effective_version` que o portal e a classificação usam — e a existência
    de uma versão rematerializada com o mesmo início.
    """
    agora = agora or timezone.now()
    publicacoes = list(
        Publicacao.objects.filter(
            Q(edital_id=versao.edital_id, revisao__isnull=False)
            | Q(pk__in=versao.applied_publications or [], revisao__isnull=True)
        )
        .order_by("publication_order")
        .values_list("publication_order", "published_at", "revisao_id")
    )
    original_em = next(
        (publicada_em for _, publicada_em, revisao in publicacoes if revisao is not None), None
    )
    retificacoes = tuple(
        RetificacaoIncorporada(numero=ordem, publicada_em=publicada_em.astimezone(ZONA))
        for ordem, publicada_em, revisao in publicacoes
        if revisao is None
    )
    return DescricaoDaVersaoBase(
        original_em=original_em.astimezone(ZONA) if original_em else None,
        retificacoes=retificacoes,
        situacao=_situacao(versao, agora),
        inicio=versao.valid_from.astimezone(ZONA),
    )


def _situacao(versao, agora):
    """Vigora, ainda não vigora, ou já foi sucedida — nesta ordem de pergunta.

    **Sucedida inclui a rematerializada.** Uma publicação fora de ordem de vigência cria versões
    novas com o mesmo início das antigas (`_materialize_affected_versions`); a antiga, com início
    futuro, nunca vai vigorar — e dizer "passa a vigorar em" dela seria prometer o que não acontece.
    """
    try:
        if effective_version(edital_id=versao.edital_id, at=agora).pk == versao.pk:
            return VIGORA
    except DomainError:
        pass
    rematerializada = VersaoConsolidada.objects.filter(
        edital_id=versao.edital_id,
        valid_from=versao.valid_from,
        materialized_at__gt=versao.materialized_at,
    ).exists()
    if versao.valid_from <= agora or rematerializada:
        return SUCEDIDA
    return FUTURA
