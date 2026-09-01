"""Consultas à trilha de auditoria.

A consulta nasceu dentro da view HTTP em T087. Ao ser também necessária pela interface, foi
trazida para a camada de aplicação: o escopo institucional precisa ser aplicado num lugar só,
e a trilha não pode virar a brecha por onde se enxerga o que não se alcança.
"""

import base64
import binascii

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.shared.api.problems import DomainError

LIMITE_PADRAO = 20
LIMITE_MAXIMO = 100


def parse_limit(valor):
    if valor in (None, ""):
        return LIMITE_PADRAO
    try:
        limite = int(valor)
    except (TypeError, ValueError) as exc:
        raise DomainError("invalid_limit", "O limite deve ser um inteiro.", 400) from exc
    if not 1 <= limite <= LIMITE_MAXIMO:
        raise DomainError("invalid_limit", f"O limite deve estar entre 1 e {LIMITE_MAXIMO}.", 400)
    return limite


def encode_cursor(registro):
    raw = f"{registro.occurred_at.isoformat()}|{registro.event_id}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def decode_cursor(cursor):
    try:
        occurred_at, event_id = (
            base64.urlsafe_b64decode(cursor.encode()).decode().split("|", 1)
        )
        return occurred_at, event_id
    except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
        raise DomainError("invalid_cursor", "O cursor informado é inválido.", 400) from exc


def consultar(*, actor, aggregate_type=None, aggregate_ids=None, cursor=None, limit=LIMITE_PADRAO):
    """Registros do escopo do ator, do mais recente para o mais antigo, com cursor estável."""
    registros = RegistroAuditoria.objects.filter(institution_scope=actor.institution_scope)
    if aggregate_type:
        registros = registros.filter(aggregate_type=aggregate_type)
    if aggregate_ids is not None:
        registros = registros.filter(aggregate_id__in=list(aggregate_ids))
    if cursor:
        occurred_at, event_id = decode_cursor(cursor)
        # O cursor aponta para o último item já entregue, na mesma ordem decrescente.
        registros = registros.filter(occurred_at__lte=occurred_at).exclude(
            occurred_at=occurred_at, event_id__gte=event_id
        )
    pagina = list(registros.order_by("-occurred_at", "-event_id")[: limit + 1])
    tem_mais = len(pagina) > limit
    pagina = pagina[:limit]
    return pagina, (encode_cursor(pagina[-1]) if pagina and tem_mais else None)


def trilha_do_edital(*, actor, edital, cursor=None, limit=LIMITE_PADRAO):
    """Tudo que aconteceu com um Edital, incluindo suas Retificações.

    Os atos de uma Retificação são auditados sob o identificador dela, não do Edital; quem
    responde questionamento sobre o certame precisa dos dois lados na mesma linha do tempo.
    """
    identificadores = [edital.id, *edital.retificacoes.values_list("id", flat=True)]
    return consultar(actor=actor, aggregate_ids=identificadores, cursor=cursor, limit=limit)


def trilha_da_comissao(*, actor, processo, cursor=None, limit=LIMITE_PADRAO):
    """Tudo que aconteceu com a comissão deste Processo — membros e alocações na mesma linha.

    Os eventos da 011 têm por agregado o membro e a alocação, e não o Processo: é assim que a
    trilha responde "qual Etapa foi afetada". Reunir os dois pelo mesmo `consultar` que já busca
    por conjunto de identificadores é o que evita um subsistema paralelo de log (011, D-018).
    """
    from processo_seletivo.comissoes.models import AlocacaoEtapa, MembroComissao

    membros = list(
        MembroComissao.objects.filter(processo=processo).values_list("id", flat=True)
    )
    alocacoes = list(
        AlocacaoEtapa.objects.filter(membro__processo=processo).values_list("id", flat=True)
    )
    return consultar(
        actor=actor, aggregate_ids=[*membros, *alocacoes], cursor=cursor, limit=limit
    )
