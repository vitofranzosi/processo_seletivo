"""Encerrar recusa o que torna a conclusão falsa; cancelar nunca recusa (113, FR-3528, FR-3536).

Cada impedimento é montado **sozinho**, e a recusa é conferida pelo que ela não pode ter mudado:
situação, revisão, ato administrativo e trilha do Edital. Resolvido o impedimento, o ato passa.
"""

from unittest import mock

import pytest
from django.db import connection
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.processos.application import pendencias_do_edital
from processo_seletivo.processos.application.finalizacao import cancel_edital, close_edital
from processo_seletivo.processos.models import AtoAdministrativo, Edital
from processo_seletivo.publicacoes.models_retificacao import Retificacao
from processo_seletivo.recursos.application.julgar import julgar
from processo_seletivo.recursos.models import DecisaoRecurso
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.divulgacao import publicar_o_ato
from tests.fixtures.papel_de_producao import como_producao  # noqa: F401
from tests.fixtures.publicacao import publish_original
from tests.fixtures.recursos_us4 import cenario_julgavel, julgador
from tests.integration.portal.test_desfecho_publico import publicar as publicar_com_periodo
from tests.integration.publicacoes.test_retificacao_de_edital_encerrado import levar_a
from tests.portal.test_prazo_recursal_publico import montar
from tests.unit.processos.test_pendencias_do_edital import criar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

GESTORA = Actor("gabi", "cefor", frozenset({"edital:encerrar", "edital:cancelar"}))
JANELA = {"admits": True, "durationDays": 5, "unit": "DIAS_CORRIDOS"}


def encerrar(edital, chave="encerrar-113-000001"):
    edital.refresh_from_db()
    return close_edital(
        actor=GESTORA,
        edital_id=edital.id,
        expected_revision=edital.revision,
        reason="Etapas concluídas",
        idempotency_key=chave,
        correlation_id="113",
    )


def cancelar(edital, chave="cancelar-113-000001"):
    edital.refresh_from_db()
    return cancel_edital(
        actor=GESTORA,
        edital_id=edital.id,
        expected_revision=edital.revision,
        reason="Interrupção administrativa",
        idempotency_key=chave,
        correlation_id="113",
    )


def retrato(edital):
    edital.refresh_from_db()
    return (
        edital.status,
        edital.revision,
        AtoAdministrativo.objects.filter(aggregate_id=edital.id).count(),
        RegistroAuditoria.objects.filter(aggregate_id=edital.id).count(),
    )


def recusa(edital, trecho):
    antes = retrato(edital)
    with pytest.raises(DomainError) as exc:
        encerrar(edital)
    assert (exc.value.code, exc.value.status) == ("pendencias_impeditivas", 409)
    assert exc.value.detail.startswith("Antes de encerrar, resolva: ")
    assert trecho in exc.value.detail
    assert retrato(edital) == antes


def test_periodo_com_termino_em_curso_impede(api_client, manager_headers, process_payload):
    edital = publicar_com_periodo(api_client, manager_headers, process_payload)
    recusa(edital, "O período de inscrições vai até")


def test_periodo_por_abrir_impede(api_client, manager_headers, process_payload):
    edital = publicar_com_periodo(
        api_client, manager_headers, process_payload, inicio_em_dias=5, termino_em_dias=15
    )
    recusa(edital, "ainda não começou")


def test_prazo_recursal_em_curso_impede(gestor, api_client, manager_headers, process_payload):
    cenario = montar(gestor, api_client, manager_headers, process_payload, seed=41, janela=JANELA)
    publicar_o_ato(cenario, chave="publicar-113-41")
    recusa(cenario["edital"], "O prazo de recurso contra “")


def test_recurso_aguardando_impede_e_julgado_libera(
    gestor, api_client, manager_headers, process_payload
):
    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=141, codigo="1141"
    )
    edital = peca["cenario"]["edital"]
    recusa(edital, "1 recurso aguarda decisão")

    julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.INDEFERIDO,
        motivacao="Sem razão.",
        idempotency_key="indeferir-113-141",
    )
    encerrar(edital)
    edital.refresh_from_db()
    assert edital.status == Edital.Status.ENCERRADO


def test_reavaliacao_pendente_impede(gestor, api_client, manager_headers, process_payload):
    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=142, codigo="1142"
    )
    julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.REAVALIACAO_DETERMINADA,
        motivacao="Reavalie-se a prova didática por avaliador diverso.",
        etapa_id=peca["cenario"]["etapa_do_recurso"],
        assinatura_do_resultado=str(peca["superado"].id),
        idempotency_key="reavaliar-113-142",
    )
    recusa(peca["cenario"]["edital"], "Reavaliação determinada em recurso")


def test_retificacao_homologada_impede_e_publicada_libera(
    api_client, manager_headers, process_payload
):
    from tests.integration.publicacoes.test_retificacao_de_edital_encerrado import publicar

    edital = publish_original(api_client, manager_headers, process_payload)
    retificacao = levar_a(criar(api_client, edital), Retificacao.Status.HOMOLOGADA)
    recusa(edital, "foi homologada e não publicada")

    publicar(retificacao, chave="publicar-113-homologada")
    encerrar(edital)
    edital.refresh_from_db()
    assert edital.status == Edital.Status.ENCERRADO


def test_o_que_so_se_adverte_nao_impede(api_client, manager_headers, process_payload):
    """Período sem término (D-008) e Retificação em elaboração não impedem."""
    edital = publish_original(api_client, manager_headers, process_payload)
    criar(api_client, edital)

    encerrar(edital)

    edital.refresh_from_db()
    assert edital.status == Edital.Status.ENCERRADO


def test_repetir_o_pedido_concluido_devolve_o_ato_sem_reconferir(
    api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    primeiro, _ = encerrar(edital, chave="encerrar-113-repetido")
    impedimento = pendencias_do_edital.Situacao(
        pendencias_do_edital.IMPEDIMENTO, pendencias_do_edital.RECURSO_AGUARDANDO
    )
    with mock.patch.object(pendencias_do_edital, "impedimentos", return_value=[impedimento]):
        segundo, status = close_edital(
            actor=GESTORA,
            edital_id=edital.id,
            expected_revision=primeiro.revision - 1,
            reason="Etapas concluídas",
            idempotency_key="encerrar-113-repetido",
            correlation_id="113",
        )
    assert (segundo.pk, status) == (primeiro.pk, 200)


def test_cancelar_e_aceito_com_tudo_junto(gestor, api_client, manager_headers, process_payload):
    """FR-3536, SC-1068: recurso, prazo recursal, período e Retificação homologada, e cancela."""
    peca = cenario_julgavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=143,
        codigo="1143",
        janela_recursal=JANELA,
    )
    edital = peca["cenario"]["edital"]
    levar_a(criar(api_client, edital), Retificacao.Status.HOMOLOGADA)
    assert len(pendencias_do_edital.impedimentos(edital, agora=timezone.now())) >= 3

    cancelar(edital)

    edital.refresh_from_db()
    assert edital.status == Edital.Status.CANCELADO


@pytest.mark.skipif(connection.vendor != "postgresql", reason="papel de produção exige PostgreSQL")
def test_a_conferencia_cabe_nos_privilegios_de_producao(
    gestor,
    api_client,
    manager_headers,
    process_payload,
    como_producao,  # noqa: F811
):
    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=144, codigo="1144"
    )
    edital = peca["cenario"]["edital"]

    with como_producao():
        recusa(edital, "1 recurso aguarda decisão")

    julgar(
        actor=julgador(),
        recurso_id=peca["recurso"].id,
        especie=DecisaoRecurso.Especie.INDEFERIDO,
        motivacao="Sem razão.",
        idempotency_key="indeferir-113-144",
    )
    with como_producao():
        encerrar(edital)
    edital.refresh_from_db()
    assert edital.status == Edital.Status.ENCERRADO
