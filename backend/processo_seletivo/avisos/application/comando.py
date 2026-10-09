"""O contexto de um ato de aviso: transação, trava, autorização pela origem, reserva (`R-009`).

**Irmão de `comando_de_comissao`, e não ele.** A ordem é a mesma — transação, `select_for_update` do
Processo filtrado pelo escopo, autorização, estado do Processo, reserva da idempotência —, mas a
porta não: o aviso de resultado é de quem tem `aviso:enviar`, e o publicador não tem base de
comissão. Reaproveitar o comando da comissão o barraria (`D-004`).

**A trava do Processo é o que impede dois avisos sobre as mesmas publicações.** A conferência de "já
avisada" corre sob ela: duas confirmações simultâneas se enfileiram, e a segunda encontra a primeira
gravada. O Processo é mutável, e o lock é permitido — ao contrário das tabelas do aviso, que são
append-only e que a role de runtime não pode travar com `FOR UPDATE` (`R-002`).
"""

from contextlib import contextmanager

from django.conf import settings

from processo_seletivo.avisos.domain import nomes
from processo_seletivo.comissoes.domain.autorizacao import Base, pode_gerir_comissao
from processo_seletivo.processos.domain.finalizacao import PROCESSO_FINAL
from processo_seletivo.processos.models import ProcessoSeletivo
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.shared.application.commands import command_context
from processo_seletivo.shared.idempotency import reservar


def nao_encontrado():
    """A mesma resposta para tudo que o ator não alcança: existir já seria informação."""
    return DomainError("not_found", "Recurso não encontrado.", 404)


def envio_habilitado():
    return bool(getattr(settings, "AVISOS_AOS_CANDIDATOS", False))


def recusar_se_desabilitado():
    """`FR-1282`: com a chave desligada, ninguém confirma aviso nem reenvio."""
    if not envio_habilitado():
        raise DomainError(
            nomes.AVISO_ENVIO_DESABILITADO,
            "O envio de avisos aos candidatos está desabilitado nesta instalação. Ele depende da "
            "validação institucional de proteção de dados e da infraestrutura de correio.",
            409,
        )


def base_do_aviso(actor, processo, *, origem):
    """A base que autoriza avisar sobre um ato desta origem, ou `None` (`D-004`).

    - **Resultado**: `aviso:enviar` (publicador e gestor), ou a presidência ativa da comissão, que
      entra pelo vínculo, como em `comissao:gerir`.
    - **Chamada**: só a base de gestão da comissão — a mesma porta da comunicação da convocação. A
      convocação é ato da comissão, e o publicador sozinho não basta.
    """
    if actor is None or actor.institution_scope != processo.institution_scope:
        return None
    if origem == nomes.CHAMADA:
        return pode_gerir_comissao(actor, processo)
    if actor.can(nomes.PERMISSAO):
        return Base(nomes.PERMISSAO)
    return pode_gerir_comissao(actor, processo)


def pode_consultar(actor, processo):
    """Quem lê o histórico: quem pode enviar por alguma origem, ou quem audita."""
    if actor is None or actor.institution_scope != processo.institution_scope:
        return False
    return (
        actor.can("auditoria:consultar")
        or base_do_aviso(actor, processo, origem=nomes.RESULTADO) is not None
    )


def processo_do_ator(actor, processo_id):
    """O Processo, se o ator o alcança pelo escopo — sem trava, para as leituras e as prévias."""
    if actor is None:
        raise nao_encontrado()
    processo = ProcessoSeletivo.objects.filter(
        pk=processo_id, institution_scope=actor.institution_scope
    ).first()
    if processo is None:
        raise nao_encontrado()
    return processo


def exigir_base(actor, processo, *, origem):
    base = base_do_aviso(actor, processo, origem=origem)
    if base is None:
        raise nao_encontrado()
    return base


def recusar_processo_em_estado_final(processo):
    """`FR-1244`: Processo encerrado ou cancelado não recebe aviso, como não recebe alteração."""
    if processo.status in PROCESSO_FINAL:
        raise DomainError(
            nomes.AVISO_PROCESSO_EM_ESTADO_FINAL,
            "Este Processo Seletivo está encerrado ou cancelado e não recebe avisos novos.",
            409,
        )


class Contexto:
    def __init__(self, *, now, processo, base, reserva, criada):
        self.now = now
        self.processo = processo
        self.base = base
        self.reserva = reserva
        self.criada = criada

    @property
    def repetido(self):
        return self.reserva.response_status is not None

    @property
    def desfecho_anterior(self):
        return self.reserva.result_payload


@contextmanager
def comando_de_aviso(*, actor, processo_id, origem, operation, payload, idempotency_key):
    """Abre a transação, trava o Processo, autoriza pela origem, confere o estado e reserva."""
    recusar_se_desabilitado()
    with command_context() as now:
        processo = (
            ProcessoSeletivo.objects.select_for_update()
            .filter(pk=processo_id, institution_scope=actor.institution_scope)
            .first()
            if actor is not None
            else None
        )
        if processo is None:
            raise nao_encontrado()
        base = exigir_base(actor, processo, origem=origem)
        recusar_processo_em_estado_final(processo)
        reserva, criada = reservar(
            actor=actor, operation=operation, key=idempotency_key, payload=payload
        )
        yield Contexto(now=now, processo=processo, base=base, reserva=reserva, criada=criada)


__all__ = [
    "Contexto",
    "base_do_aviso",
    "comando_de_aviso",
    "envio_habilitado",
    "exigir_base",
    "nao_encontrado",
    "pode_consultar",
    "processo_do_ator",
    "recusar_processo_em_estado_final",
    "recusar_se_desabilitado",
]
