"""Consultas públicas: expõem somente atos publicados, nunca material de elaboração."""

import base64
import binascii

from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from processo_seletivo.shared.api.problems import DomainError

DEFAULT_LIMIT = 20
MAX_LIMIT = 100
PUBLICACAO = "PUBLICACAO"
RETIFICACAO = "RETIFICACAO"
VERSAO_CONSOLIDADA = "VERSAO_CONSOLIDADA"
_KIND_ORDER = {PUBLICACAO: 0, RETIFICACAO: 1, VERSAO_CONSOLIDADA: 2}


def _not_found():
    return DomainError("not_found", "Recurso não encontrado.", 404)


def effective_version(*, edital_id, at=None):
    """Versão vigente no instante informado, sem aplicar vigências ainda não iniciadas."""
    moment = at or timezone.now()
    version = (
        VersaoConsolidada.objects.filter(edital_id=edital_id, valid_from__lte=moment)
        .prefetch_related("proveniencias")
        .order_by("-valid_from", "-materialized_at")
        .first()
    )
    if version is None:
        raise DomainError(
            "no_effective_version",
            "Não havia conteúdo vigente para este Edital no instante consultado.",
            404,
        )
    return version


def consolidated_version(*, versao_id):
    try:
        return VersaoConsolidada.objects.prefetch_related("proveniencias").get(pk=versao_id)
    except VersaoConsolidada.DoesNotExist as exc:
        raise _not_found() from exc


def published_publication(*, publicacao_id):
    try:
        return Publicacao.objects.select_related("documento", "retificacao").get(pk=publicacao_id)
    except Publicacao.DoesNotExist as exc:
        raise _not_found() from exc


def published_retification(*, retificacao_id):
    """Retificação ainda não publicada não existe para o público (FR-031)."""
    try:
        return (
            Retificacao.objects.select_related("publication")
            .prefetch_related("alteracoes")
            .get(pk=retificacao_id, status=Retificacao.Status.PUBLICADA)
        )
    except Retificacao.DoesNotExist as exc:
        raise _not_found() from exc


def _sort_key(entry):
    return (entry["occurredAt"], _KIND_ORDER[entry["kind"]], str(entry["item"].id))


def _encode_cursor(entry):
    occurred_at, kind_rank, identifier = _sort_key(entry)
    raw = f"{occurred_at.isoformat()}|{kind_rank}|{identifier}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def _decode_cursor(cursor):
    try:
        occurred_at, kind_rank, identifier = (
            base64.urlsafe_b64decode(cursor.encode()).decode().split("|", 2)
        )
        moment = parse_datetime(occurred_at)
        if moment is None:
            raise ValueError(occurred_at)
        return (moment, int(kind_rank), identifier)
    except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
        raise DomainError("invalid_cursor", "O cursor informado é inválido.", 400) from exc


def parse_limit(value):
    if value in (None, ""):
        return DEFAULT_LIMIT
    try:
        limit = int(value)
    except (TypeError, ValueError) as exc:
        raise DomainError("invalid_limit", "O limite deve ser um inteiro.", 400) from exc
    if not 1 <= limit <= MAX_LIMIT:
        raise DomainError("invalid_limit", f"O limite deve estar entre 1 e {MAX_LIMIT}.", 400)
    return limit


def _after_cursor(campo, rank, after):
    """Filtro que reproduz, no banco, a comparação `(instante, tipo, id) > cursor`.

    Cada fonte tem um `rank` fixo, então o desempate por tipo é constante dentro dela: ou toda a
    fonte vem depois do cursor no instante empatado, ou nenhuma, ou desempata pelo identificador.
    """
    momento, rank_do_cursor, identificador = after
    depois = Q(**{f"{campo}__gt": momento})
    empate = Q(**{campo: momento})
    if rank > rank_do_cursor:
        return depois | empate
    if rank < rank_do_cursor:
        return depois
    return depois | (empate & Q(id__gt=identificador))


def _pagina_da_fonte(queryset, *, campo, kind, cursor, limit):
    """Os `limit + 1` primeiros desta fonte a partir do cursor, ordenados no banco.

    O `+1` é o que responde "há mais?" sem contar o resto. Ordenar e cortar aqui é o ponto da
    FR-024: antes, as três fontes vinham inteiras para a memória, eram concatenadas, ordenadas
    em Python e só então fatiadas — o número de consultas era constante, mas o volume lido
    crescia com todo o histórico do Edital.
    """
    if cursor:
        queryset = queryset.filter(_after_cursor(campo, _KIND_ORDER[kind], cursor))
    ordenado = queryset.order_by(campo, "id")[: limit + 1]
    return [
        {"kind": kind, "item": item, "occurredAt": _valor_do_campo(item, campo)}
        for item in ordenado
    ]


def _valor_do_campo(item, campo):
    valor = item
    for parte in campo.split("__"):
        valor = getattr(valor, parte)
    return valor


def public_history(*, edital_id, cursor=None, limit=DEFAULT_LIMIT):
    """Edital original, Retificações publicadas e versões consolidadas, em ordem cronológica.

    Cada fonte devolve no máximo `limit + 1` linhas já ordenadas pelo banco; a mescla acontece
    sobre no máximo três vezes isso. Como a página global é o menor prefixo das três, os
    `limit + 1` primeiros de cada fonte necessariamente contêm os `limit` primeiros do todo — e
    `has_more` continua exato sem precisar contar o restante.
    """
    after = _decode_cursor(cursor) if cursor else None
    entries = _pagina_da_fonte(
        Publicacao.objects.filter(edital_id=edital_id).select_related("documento"),
        campo="published_at",
        kind=PUBLICACAO,
        cursor=after,
        limit=limit,
    )
    entries += _pagina_da_fonte(
        Retificacao.objects.filter(edital_id=edital_id, status=Retificacao.Status.PUBLICADA)
        .select_related("publication")
        .prefetch_related("alteracoes"),
        campo="publication__published_at",
        kind=RETIFICACAO,
        cursor=after,
        limit=limit,
    )
    entries += _pagina_da_fonte(
        # Sem o prefetch, a proveniência de cada versão vira uma consulta própria e o
        # custo do histórico cresce com o número de Retificações.
        VersaoConsolidada.objects.filter(edital_id=edital_id).prefetch_related("proveniencias"),
        campo="valid_from",
        kind=VERSAO_CONSOLIDADA,
        cursor=after,
        limit=limit,
    )
    entries.sort(key=_sort_key)
    page = entries[:limit]
    has_more = len(entries) > limit
    return page, (_encode_cursor(page[-1]) if page and has_more else None)


def participantes_do_edital(edital):
    """Quem elaborou, homologou e publicou — base da segregação de funções (FR-012).

    A regra é do domínio e é ele quem recusa; a tela precisa desses nomes para comunicar a
    exigência **antes** da tentativa, e não só depois da recusa.
    """
    from processo_seletivo.publicacoes.models import Homologacao, Publicacao, RevisaoEdital

    revisao = RevisaoEdital.objects.filter(edital=edital).order_by("-submitted_at").first()
    homologacao = (
        Homologacao.objects.filter(revisao=revisao, revoked_at__isnull=True)
        .order_by("-homologated_at")
        .first()
        if revisao
        else None
    )
    publicacao = (
        Publicacao.objects.filter(edital=edital, revisao__isnull=False)
        .order_by("-publication_order")
        .first()
    )
    return {
        "elaborou": revisao.prepared_by if revisao else "",
        "elaborou_em": revisao.submitted_at if revisao else None,
        "homologou": homologacao.homologated_by if homologacao else "",
        "homologou_em": homologacao.homologated_at if homologacao else None,
        "publicou": publicacao.published_by if publicacao else "",
        "publicou_em": publicacao.published_at if publicacao else None,
        "signatario": (
            f"{publicacao.signatory_name} — {publicacao.signatory_role}" if publicacao else ""
        ),
    }


def impede_por_segregacao(participantes, ator):
    """Publicar exige que outra pessoa tenha elaborado ou homologado (FR-021 da 001)."""
    return bool(
        participantes["elaborou"]
        and participantes["elaborou"] == participantes["homologou"] == ator.subject
    )


def selecoes_publicas(*, at=None):
    """As seleções que uma pessoa de fora pode consultar, com a versão vigente de cada uma.

    "Publicamente consultável" é o que já significava na API pública: existe versão consolidada
    cuja vigência começou. Não há estado novo a inventar — a `001` já decidiu o que é público
    quando decidiu o que a consulta anônima devolve.

    **Cancelado não entra na vitrine, e continua alcançável pelo endereço.** A Publicação é
    imutável e o histórico não se apaga (princípio II), mas listar como oportunidade uma seleção
    cancelada convidaria alguém a se inscrever no que não existe mais. A distinção é entre
    *anunciar* e *preservar*.

    Duas consultas, e a primeira não carrega o conteúdo: `values_list` decide qual versão vence
    por Edital lendo só identificador e vigência, e a segunda materializa apenas as vencedoras.
    Ordenar e escolher em memória sobre o conteúdo inteiro faria a vitrine crescer com o
    histórico, não com o número de seleções.
    """
    from processo_seletivo.processos.models import Edital

    moment = at or timezone.now()
    vigentes = {}
    for edital_id, versao_id in (
        VersaoConsolidada.objects.filter(valid_from__lte=moment)
        .exclude(edital__status=Edital.Status.CANCELADO)
        .order_by("edital_id", "-valid_from", "-materialized_at")
        .values_list("edital_id", "id")
    ):
        vigentes.setdefault(edital_id, versao_id)
    return list(
        VersaoConsolidada.objects.filter(id__in=list(vigentes.values()))
        .select_related("edital", "edital__processo")
        .order_by("-valid_from", "-materialized_at")
    )


def selecao_publica(*, edital_id, at=None):
    """A versão vigente de uma seleção, para o canal público.

    Diferente de `selecoes_publicas`, **não** exclui o cancelado: a página de um Edital publicado
    continua consultável depois de encerrado (FR-017) e depois de cancelado, porque o que foi
    publicado permanece. O que muda é ser anunciado, não ser lido.
    """
    versao = effective_version(edital_id=edital_id, at=at)
    return (
        VersaoConsolidada.objects.select_related("edital", "edital__processo")
        .filter(pk=versao.pk)
        .first()
    )
