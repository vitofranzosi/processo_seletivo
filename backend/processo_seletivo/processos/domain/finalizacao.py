"""Política de desfecho: Encerrado é conclusão regular, Cancelado é interrupção administrativa.

FR-005, FR-006, FR-034 e FR-035. Os dois estados são finais e nunca sinônimos: nenhum deles
retorna a estado anterior e ambos preservam Publicações, Retificações e histórico.
"""

from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from processo_seletivo.shared.api.problems import DomainError

PROCESSO_FINAL = frozenset({ProcessoSeletivo.Status.ENCERRADO, ProcessoSeletivo.Status.CANCELADO})
EDITAL_FINAL = frozenset({Edital.Status.ENCERRADO, Edital.Status.CANCELADO})

# Encerrar é a conclusão regular do fluxo ordinário; cancelar interrompe antes dela.
PROCESSO_ENCERRAVEL = frozenset({ProcessoSeletivo.Status.ATIVO})
PROCESSO_CANCELAVEL = frozenset(
    {ProcessoSeletivo.Status.EM_ELABORACAO, ProcessoSeletivo.Status.ATIVO}
)
EDITAL_ENCERRAVEL = frozenset({Edital.Status.PUBLICADO})
EDITAL_CANCELAVEL = frozenset(
    {
        Edital.Status.EM_ELABORACAO,
        Edital.Status.EM_REVISAO,
        Edital.Status.HOMOLOGADO,
        Edital.Status.PUBLICADO,
    }
)


def _reject(detail):
    return DomainError("invalid_state", detail, 409)


def ensure_processo_can_be_closed(processo):
    if processo.status in PROCESSO_FINAL:
        raise _reject("Processo em estado final não admite nova transição.")
    if processo.status not in PROCESSO_ENCERRAVEL:
        raise _reject("Somente Processo ativo pode ser encerrado.")


def ensure_processo_can_be_cancelled(processo, pendentes):
    """FR-034: o cancelamento é bloqueado enquanto houver Edital fora de estado final."""
    if processo.status in PROCESSO_FINAL:
        raise _reject("Processo em estado final não admite nova transição.")
    if processo.status not in PROCESSO_CANCELAVEL:
        raise _reject("Este Processo não pode ser cancelado.")
    if pendentes:
        raise DomainError(
            "editais_pendentes",
            "Cancele ou encerre cada Edital antes de cancelar o Processo: "
            + ", ".join(f"{edital.number}/{edital.year}" for edital in pendentes),
            409,
        )


def ensure_edital_can_be_closed(edital):
    """FR-006: Encerrado representa a conclusão regular, depois da Publicação."""
    if edital.status in EDITAL_FINAL:
        raise _reject("Edital em estado final não admite nova transição.")
    if edital.status not in EDITAL_ENCERRAVEL:
        raise _reject("Somente Edital publicado pode ser encerrado.")


def ensure_edital_can_be_cancelled(edital):
    if edital.status in EDITAL_FINAL:
        raise _reject("Edital em estado final não admite nova transição.")
    if edital.status not in EDITAL_CANCELAVEL:
        raise _reject("Este Edital não pode ser cancelado.")


def ensure_processo_accepts_changes(processo):
    """FR-035: Processo encerrado ou cancelado não recebe novas alterações em seus Editais."""
    if processo.status in PROCESSO_FINAL:
        raise _reject(
            "O Processo Seletivo está em estado final e não admite alteração de seus Editais."
        )


def ensure_edital_accepts_changes(edital):
    if edital.status in EDITAL_FINAL:
        raise _reject("Edital em estado final não admite alteração.")


def pending_editais(processo):
    """Editais que ainda impedem o cancelamento do Processo, em ordem estável."""
    return list(processo.editais.exclude(status__in=EDITAL_FINAL).order_by("year", "number", "id"))
