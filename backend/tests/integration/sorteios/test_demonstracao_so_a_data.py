"""A recusa do Edital 72/2026, reproduzida sem rede (102, FR-2665, SC-959, D-007).

**Por que existe.** Com a fonte de demonstração de sempre, que responde "agora", todo congelamento é
anterior à ocorrência, inclusive no mesmo dia: o caso que derrubou o sorteio no servidor nunca
aparecia em desenvolvimento. A fonte "só a data" devolve o início do dia corrente, como a Caixa faz
com a extração publicada hoje — congelar e sortear no mesmo dia é recusado; sortear no dia
seguinte constitui.
"""

from datetime import timedelta
from pathlib import Path
from unittest import mock

import pytest
from django.utils import timezone

from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.application.ocorrencia import observar_ocorrencia
from processo_seletivo.sorteios.application.relacao import publicar_relacao
from processo_seletivo.sorteios.application.sorteio import constituir_sorteio
from tests.fixtures.sorteio import METODO, certame_de_sorteio, presidente

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

SO_A_DATA = "Fonte de demonstração (só a data)"


def _certame(gestor, api_client, manager_headers, process_payload):
    metodo = {**METODO, "source": SO_A_DATA, "occurrence": "7001"}
    return certame_de_sorteio(gestor, api_client, manager_headers, process_payload, metodo=metodo)


def _congelar(certame):
    return publicar_relacao(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        idempotency_key="so-a-data-relacao",
        correlation_id="teste-102",
    )["relacao"]


def _sortear(certame, relacao):
    ocorrencia = observar_ocorrencia(
        actor=presidente(),
        processo_id=certame["processo"].id,
        fonte=SO_A_DATA,
        referencia="7001",
        idempotency_key="so-a-data-obs",
        correlation_id="teste-102",
    )["ocorrencia"]
    return constituir_sorteio(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=certame["edital"].id,
        relacao_id=relacao,
        ocorrencia_id=ocorrencia,
        idempotency_key="so-a-data-sorteio",
        correlation_id="teste-102",
    )


def test_congelar_e_sortear_no_mesmo_dia_e_recusado(
    gestor, api_client, manager_headers, process_payload
):
    certame = _certame(gestor, api_client, manager_headers, process_payload)
    relacao = _congelar(certame)

    with pytest.raises(DomainError, match="occurrence_precedes_freeze") as recusa:
        _sortear(certame, relacao)

    assert "publica só a data da extração" in recusa.value.detail


def test_congelar_hoje_e_sortear_amanha_constitui(
    gestor, api_client, manager_headers, process_payload
):
    """O relógio vai para amanhã, e não a relação para ontem: o Edital só vigora desde hoje."""
    certame = _certame(gestor, api_client, manager_headers, process_payload)
    relacao = _congelar(certame)

    amanha = timezone.now() + timedelta(days=1)
    with mock.patch("django.utils.timezone.now", return_value=amanha):
        declarado = _sortear(certame, relacao)

    assert declarado["quantidade"] == 3


def test_a_seed_demo_nao_declara_a_fonte_nova():
    """A `seed_demo` continua com a demonstração de sempre: nada muda para quem a usa."""
    comando = (
        Path(__file__).resolve().parents[3]
        / "processo_seletivo/processos/management/commands/seed_demo.py"
    )

    assert SO_A_DATA not in comando.read_text(encoding="utf-8")
