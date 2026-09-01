"""T018 — a sentinela do registrador de auditoria.

`None` não serve como padrão: `new_revision` é coluna anulável, então é valor legítimo. Usá-lo
também como marcador de "leia do agregado" faria o registrador tentar `aggregate.revision` num
agregado que não tem revisão — e o defeito só apareceria no dia em que alguém quisesse gravar
revisão nula de propósito (D-014).
"""

import uuid

import pytest

from processo_seletivo.auditoria.application import record_event
from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.seguranca.domain import Actor

pytestmark = pytest.mark.django_db


class AgregadoSemCicloDeVida:
    """Como `MembroComissao`: tem identidade, não tem `status` nem `revision`."""

    def __init__(self):
        self.pk = uuid.uuid4()


@pytest.fixture
def ator():
    return Actor("carlos", "cefor", frozenset({"comissao:gerir"}))


def test_agregado_sem_estado_e_sem_revisao_e_registrado(ator, django_assert_num_queries=None):
    agregado = AgregadoSemCicloDeVida()

    record_event(
        actor=ator,
        permission="comissao:gerir",
        operation="COMISSAO_INCLUIR_MEMBRO",
        aggregate=agregado,
        now=_agora(),
        correlation_id="c-1",
        new_state="",
        new_revision=None,
    )

    registro = RegistroAuditoria.objects.get(aggregate_id=agregado.pk)
    assert registro.new_state == ""
    assert registro.new_revision is None
    assert registro.permission == "comissao:gerir"


def test_sem_os_argumentos_o_registrador_le_do_agregado(ator):
    """Quem já chamava não muda: a sentinela preserva o comportamento antigo."""
    from processo_seletivo.processos.models import ProcessoSeletivo

    processo = ProcessoSeletivo.objects.create(
        institution_scope="cefor",
        institutional_code="PS-REC-1",
        title="Processo",
        created_at=_agora(),
        created_by="carlos",
        last_changed_at=_agora(),
    )

    record_event(
        actor=ator,
        permission="processo:criar",
        operation="CRIAR",
        aggregate=processo,
        now=_agora(),
        correlation_id="c-2",
    )

    registro = RegistroAuditoria.objects.get(aggregate_id=processo.pk)
    assert registro.new_state == processo.status
    assert registro.new_revision == processo.revision


def _agora():
    from django.utils import timezone

    return timezone.now()
