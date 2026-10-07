"""Leituras do registro de unidades e autoridades — o que as outras partes do sistema perguntam."""

import uuid

from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.unidades.domain import nomes
from processo_seletivo.unidades.models import AutoridadeHabilitada, Unidade


def unidade(codigo):
    """A Unidade daquele escopo, ativa ou não, ou `None` quando o escopo não está registrado."""
    return Unidade.objects.filter(codigo=str(codigo or "")).first()


def exigir_unidade(codigo, *, ativa=False):
    """A Unidade do escopo, ou a recusa que diz que ela não está registrada (FR-1110).

    `ativa=True` é a exigência de quem cria: Processo e Edital novos só nascem em Unidade ativa.
    Quem mantém o que já existe — inclusive as autoridades de uma unidade desativada — pede só que
    ela exista, porque o certame em curso precisa terminar.
    """
    encontrada = unidade(codigo)
    if encontrada is None:
        raise DomainError(
            nomes.UNIDADE_NAO_REGISTRADA,
            f"{codigo} não é uma unidade registrada no sistema.",
            422,
        )
    if ativa and not encontrada.ativa:
        raise DomainError(
            nomes.UNIDADE_NAO_REGISTRADA,
            f"{encontrada.nome} está desativada e não recebe Processo nem Edital novo.",
            422,
        )
    return encontrada


def autoridades_vigentes(codigo, data):
    """As autoridades habilitadas na Unidade e vigentes em `data`, por cargo e nome (FR-1125)."""
    return list(
        AutoridadeHabilitada.objects.filter(
            unidade__codigo=str(codigo or ""), inicio_vigencia__lte=data
        )
        .exclude(fim_vigencia__lt=data)
        .select_related("unidade")
        .order_by("cargo", "nome", "inicio_vigencia")
    )


def autoridades_da_unidade(codigo):
    """Todas as autoridades da Unidade, vigentes, futuras e encerradas — a lista da tela."""
    return list(
        AutoridadeHabilitada.objects.filter(unidade__codigo=str(codigo or "")).order_by(
            "cargo", "nome", "inicio_vigencia"
        )
    )


def identificador(valor):
    """O UUID enviado, ou `None` quando não é um — o formulário e a API mandam texto."""
    try:
        return uuid.UUID(str(valor or ""))
    except ValueError:
        return None


def autoridade_da_unidade(autoridade_id, codigo):
    """A autoridade daquele identificador **nesta** Unidade, ou `None`.

    Outra unidade, inexistente e identificador malformado respondem o mesmo `None`: a de outra
    unidade é indistinguível de inexistente para quem não tem escopo sobre ela (FR-1122).
    """
    chave = identificador(autoridade_id)
    if chave is None:
        return None
    return AutoridadeHabilitada.objects.filter(pk=chave, unidade__codigo=str(codigo or "")).first()
