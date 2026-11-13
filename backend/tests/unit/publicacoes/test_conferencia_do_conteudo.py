"""A conferência de conteúdo da criação, chamada também pela tela (123, R-001, R-002).

«Ver o que vai mudar» passa a dizer o que «Criar Retificação» diria. A garantia só vale enquanto
as duas portas chamarem **a mesma** função com **os mesmos** argumentos, e é o que se prende aqui:
as frases são as que compõem a recusa da criação, a primeira guarda interrompe como na criação, os
argumentos de `validate_for_publication` são idênticos, e conferir não grava nada.
"""

from unittest import mock

import pytest

from processo_seletivo.auditoria.models import IdempotencyRecord, RegistroAuditoria
from processo_seletivo.publicacoes.application import retificacoes
from processo_seletivo.publicacoes.application.retificacoes import (
    conferir_retificacao,
    conteudo_base,
)
from processo_seletivo.publicacoes.models_retificacao import AlteracaoNormativa, Retificacao
from tests.fixtures.edital_da_auditoria import versao_mais_recente
from tests.fixtures.publicacao import create_retification
from tests.fixtures.snapshot import CRITERIO, EVENTO, MARCO, PERFIL

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

MARCO_FINAL = f"/profiles/id={PERFIL['A']}/classificationMilestones/id={MARCO}"


def _quadro_que_nao_fecha():
    # O Perfil principal tem quadro completo (geral 1, PPI 0): declarar 2 vagas sem mexer no quadro
    # é a incoerência do cenário B da auditoria.
    return [
        {
            "targetPath": f"/profiles/id={PERFIL['A']}/immediateVacancies",
            "operation": "REPLACE",
            "newValue": 2,
        }
    ]


def _evento_sem_inicio():
    return [
        {
            "targetPath": f"/schedule/id={EVENTO['B']}/startAt",
            "operation": "REPLACE",
            "newValue": None,
        }
    ]


def _criterio_repetido():
    return [
        {
            "targetPath": f"{MARCO_FINAL}/tiebreakers/-",
            "operation": "ADD",
            "newValue": {"id": "00000000-0000-4000-8000-000000123001", "order": 1},
        }
    ]


def _conferir(edital, changes):
    return conferir_retificacao(edital, conteudo_base(versao_mais_recente(edital)), changes)


@pytest.mark.parametrize("changes", [_quadro_que_nao_fecha(), _evento_sem_inicio()])
def test_as_frases_sao_as_que_compoem_a_recusa_da_criacao(edital_da_auditoria, api_client, changes):
    conferido = _conferir(edital_da_auditoria, changes)
    assert conferido.recusa is None
    assert conferido.impeditivos, "o formulário deveria ter impeditivo"

    recusa = create_retification(api_client, edital_da_auditoria, changes, esperar=422)
    assert recusa["code"] == "blocking_findings"
    juntadas = recusa["detail"].split(" possui erros impeditivos: ", 1)[1]
    assert juntadas == "; ".join(item.message for item in conferido.impeditivos)


def test_a_primeira_guarda_interrompe_como_na_criacao(edital_da_auditoria, api_client):
    conferido = _conferir(edital_da_auditoria, _criterio_repetido())
    assert conferido.recusa is not None
    assert conferido.impeditivos == []

    recusa = create_retification(api_client, edital_da_auditoria, _criterio_repetido(), esperar=422)
    assert recusa["code"] == conferido.recusa.code
    assert recusa["detail"] == conferido.recusa.detail


def test_sem_impeditivo_nada_a_dizer(edital_da_auditoria):
    changes = [
        {
            "targetPath": f"/profiles/id={PERFIL['C']}/locality",
            "operation": "REPLACE",
            "newValue": "Serra",
        }
    ]
    conferido = _conferir(edital_da_auditoria, changes)
    assert conferido.recusa is None
    assert conferido.impeditivos == []


def test_conferir_nao_grava_nada(edital_da_auditoria):
    antes = (
        Retificacao.objects.count(),
        AlteracaoNormativa.objects.count(),
        RegistroAuditoria.objects.count(),
        IdempotencyRecord.objects.count(),
    )
    _conferir(edital_da_auditoria, _quadro_que_nao_fecha())
    _conferir(edital_da_auditoria, _criterio_repetido())
    assert (
        Retificacao.objects.count(),
        AlteracaoNormativa.objects.count(),
        RegistroAuditoria.objects.count(),
        IdempotencyRecord.objects.count(),
    ) == antes


def test_os_argumentos_da_validacao_sao_os_da_criacao(edital_da_auditoria, api_client):
    """R-002: a mesma chamada nos dois caminhos — o guardião contra esquecer um argumento."""
    original = retificacoes.validate_for_publication
    chamadas = []

    def espiao(content, **kwargs):
        chamadas.append(kwargs)
        return original(content, **kwargs)

    with mock.patch.object(retificacoes, "validate_for_publication", espiao):
        _conferir(edital_da_auditoria, _quadro_que_nao_fecha())
        create_retification(api_client, edital_da_auditoria, _quadro_que_nao_fecha(), esperar=422)
    assert len(chamadas) == 2
    assert chamadas[0] == chamadas[1]
    assert set(chamadas[0]) == {"ato", "topologia", "situacoes"}
    assert chamadas[0]["situacoes"] is None


def test_o_criterio_usado_aqui_e_o_do_marco_da_fixture():
    # Sentinela: o critério repetido só é guarda enquanto a fixture tiver critério de ordem 1.
    assert CRITERIO["ETAPA"]
