"""O custo de abrir o corte é do conjunto, não uma consulta por participante (014, SC-067).

O teto é o mesmo da tela da ordem, e a razão é a mesma: a faixa é calculada **ao abrir**, e uma
tela que consulta por participante deixa de abrir muito antes de mil. O teste de contagem é o que
cobra — o do relógio mede a máquina, e o da contagem mede o desenho.
"""

import time

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.classificacao.application.corte import calcular_corte
from processo_seletivo.classificacao.application.emissao import assinatura_da_proposta, emitir_ordem
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.comissao import rascunho_com_etapas
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.performance, pytest.mark.django_db(transaction=True)]

MARCO = "00000000-0000-4000-8000-000000000491"
ENTREVISTA = "00000000-0000-4000-8000-000000000492"
TETO_SEGUNDOS = 3.0


def _acrescentar_inscricoes(edital, *, quantidade, inicio):
    versao = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    agora = timezone.now()
    Inscricao.objects.bulk_create(
        [
            Inscricao(
                identity_subject=f"cpf:corte-escala-{numero:04d}",
                edital=edital,
                profile_id=PROFILE_ID,
                status=Inscricao.Status.SUBMETIDA,
                protocolo=f"C{numero:04d}",
                nome=f"Participante {numero:04d}",
                cpf="111.444.777-35",
                cpf_normalizado="11144477735",
                email=f"corte{numero}@example.test",
                versao_aceita=versao,
                declaracoes_aceitas_em=agora,
                submitted_at=agora,
                created_at=agora,
            )
            for numero in range(inicio, inicio + quantidade)
        ]
    )


@pytest.fixture
def edital_com_corte(gestor, api_client, manager_headers, process_payload):
    """Um marco que corta, com a ordem já emitida sobre mil participantes."""
    rascunho = rascunho_com_etapas(avaliacoes=1, maxima="100.0000", minima="0.0000")
    etapa = rascunho["stages"][1]
    etapa["weight"] = "1.0000"
    rascunho["stages"].append(
        {
            "id": ENTREVISTA,
            "name": "Entrevista",
            "order": 3,
            "eliminatory": False,
            "classificatory": True,
            "minimumScore": "0.0000",
            "maximumScore": "100.0000",
            "evaluationsPerRegistration": 1,
            "weight": "1.0000",
            "scheduleEventId": None,
        }
    )
    rascunho["profiles"][0]["classificationMilestones"] = [
        {
            "id": MARCO,
            "code": "FINAL",
            "name": "Classificação final",
            "stages": [etapa["id"]],
            "operation": "SOMA_PONDERADA",
            "normalization": "NENHUMA",
            "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
            "tiebreakers": [],
            "cutRule": {
                "targetKind": "FIXED",
                "targetCount": 100,
                "surplusCount": 0,
                "tieOutcome": "ADMITS_SURPLUS",
                "governedStage": ENTREVISTA,
                "continuation": "NONE",
            },
        }
    ]
    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho)
    _acrescentar_inscricoes(edital, quantidade=1000, inicio=1)
    emitir_ordem(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key="corte-escala-ordem",
        correlation_id="teste-014-escala",
        confirmacao_do_calculo=assinatura_da_proposta(
            calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)
        ),
    )
    return edital


def _suceder_a_ordem(edital, gestor):
    from processo_seletivo.classificacao.models import AtoDeOrdenacao

    vigente = AtoDeOrdenacao.objects.filter(
        edital=edital, marco_id=MARCO, lista_id=None, sucessores__isnull=True
    ).first()
    emitir_ordem(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        idempotency_key="corte-escala-ordem-2",
        correlation_id="teste-014-escala",
        confirmacao_do_calculo=assinatura_da_proposta(
            calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO),
            ato_vigente=vigente,
        ),
        motivo="População ampliada.",
    )


def test_o_numero_de_consultas_do_calculo_nao_cresce_com_os_participantes(edital_com_corte, gestor):
    """Cinco a mais ou mil a mais: o mesmo número de consultas.

    A comparação é entre **dois recortes do mesmo Edital** porque é o crescimento que importa: um
    número absoluto vira orçamento a manter, e o que o `SC-067` promete é que a conta não dependa
    da população.
    """
    with CaptureQueriesContext(connection) as antes:
        calcular_corte(edital=edital_com_corte, perfil_id=PROFILE_ID, marco_id=MARCO)
    # **A ordem é sucedida**, e não só a população aumentada: acrescentar participantes obsoleta o
    # ato, e sobre ordem obsoleta não se corta (FR-198). Medir o crescimento exige uma ordem
    # vigente dos dois lados.
    _acrescentar_inscricoes(edital_com_corte, quantidade=1000, inicio=2001)
    _suceder_a_ordem(edital_com_corte, gestor)
    with CaptureQueriesContext(connection) as depois:
        proposta = calcular_corte(edital=edital_com_corte, perfil_id=PROFILE_ID, marco_id=MARCO)

    assert len(proposta["itens"]) == 2000
    assert len(depois) == len(antes)


def test_abrir_a_tela_do_corte_com_mil_participantes_fica_abaixo_do_teto(
    edital_com_corte, client, seletor_ligado
):
    identificar(client, "gestora", ["gestor"])

    inicio = time.monotonic()
    resposta = client.get(reverse("interface:corte", args=[edital_com_corte.id, MARCO]))
    duracao = time.monotonic() - inicio

    assert resposta.status_code == 200
    assert duracao < TETO_SEGUNDOS, f"a tela levou {duracao:.3f}s"
