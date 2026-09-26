"""O selector do desfecho: o estado diz se, o ato diz quando (047, `R-2`, `D-003`, `FR-775`).

Os Editais são criados direto no banco, com o estado que cada caso precisa: o que se testa é a
leitura, e não a finalização — essa tem teste próprio em `tests/integration/processos/`.
"""

import uuid
from datetime import UTC, datetime

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from processo_seletivo.processos.application.selectors import (
    CANCELADO,
    EDITAL,
    ENCERRADO,
    PROCESSO,
    desfechos,
)
from processo_seletivo.processos.models import AtoAdministrativo, Edital, ProcessoSeletivo

pytestmark = pytest.mark.django_db

QUANDO = datetime(2026, 9, 26, 18, 36, tzinfo=UTC)


def processo(status=ProcessoSeletivo.Status.ATIVO, *, codigo=None):
    return ProcessoSeletivo.objects.create(
        institution_scope="cefor",
        institutional_code=codigo or f"PS-{uuid.uuid4().hex[:8]}",
        title="Processo do teste",
        status=status,
        created_at=QUANDO,
        created_by="gestora",
        last_changed_at=QUANDO,
    )


def edital(dono, status=Edital.Status.PUBLICADO, *, numero=1):
    return Edital.objects.create(
        processo=dono,
        institution_scope="cefor",
        number=numero,
        year=2026,
        title=f"Edital {numero}",
        status=status,
        created_at=QUANDO,
        created_by="gestora",
        last_edited_by="gestora",
    )


def ato(agregado, operacao, quando=QUANDO):
    return AtoAdministrativo.objects.create(
        aggregate_type=agregado.__class__.__name__,
        aggregate_id=agregado.id,
        operation=operacao,
        actor_subject="gestora",
        reason="interno",
        occurred_at=quando,
    )


def carregados(*editais):
    return list(Edital.objects.filter(pk__in=[e.pk for e in editais]).select_related("processo"))


def test_editais_publicados_nao_consultam_os_atos():
    dono = processo()
    lidos = carregados(*(edital(dono, numero=n) for n in range(1, 4)))

    with CaptureQueriesContext(connection) as consultas:
        resultado = desfechos(lidos)

    assert set(resultado.values()) == {None}
    assert consultas.captured_queries == []


def test_n_editais_finais_custam_uma_consulta():
    dono = processo()
    finais = [edital(dono, Edital.Status.ENCERRADO, numero=n) for n in range(1, 6)]
    for item in finais:
        ato(item, "ENCERRAR")
    lidos = carregados(*finais)

    with CaptureQueriesContext(connection) as consultas:
        resultado = desfechos(lidos)

    assert len(consultas.captured_queries) == 1
    assert {(d.alcance, d.operacao, d.em) for d in resultado.values()} == {
        (EDITAL, ENCERRADO, QUANDO)
    }


def test_o_edital_vence_o_processo():
    dono = processo(ProcessoSeletivo.Status.CANCELADO)
    encerrado = edital(dono, Edital.Status.ENCERRADO)
    ato(encerrado, "ENCERRAR")
    ato(dono, "CANCELAR")

    (lido,) = carregados(encerrado)
    resultado = desfechos([lido])[lido.id]

    assert (resultado.alcance, resultado.operacao) == (EDITAL, ENCERRADO)


def test_sem_desfecho_do_edital_vale_o_do_processo():
    dono = processo(ProcessoSeletivo.Status.ENCERRADO)
    publicado = edital(dono)
    ato(dono, "ENCERRAR")

    (lido,) = carregados(publicado)
    resultado = desfechos([lido])[lido.id]

    assert (resultado.alcance, resultado.operacao, resultado.em) == (PROCESSO, ENCERRADO, QUANDO)


def test_sem_ato_encontrado_o_desfecho_vem_sem_data():
    """`FR-775`: omitir, e não inventar. `last_changed_at` não substitui o ato."""
    dono = processo()
    cancelado = edital(dono, Edital.Status.CANCELADO)

    (lido,) = carregados(cancelado)
    resultado = desfechos([lido])[lido.id]

    assert (resultado.alcance, resultado.operacao, resultado.em) == (EDITAL, CANCELADO, None)
