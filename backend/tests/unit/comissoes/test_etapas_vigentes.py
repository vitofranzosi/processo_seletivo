"""T013 — o resolvedor de Etapas, que é a fonte única da 011."""

import pytest

from processo_seletivo.comissoes.domain.etapas import etapa_vigente, etapas_vigentes
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.comissao import ETAPA_A1, ETAPA_A2
from tests.fixtures.edital import identificador

pytestmark = pytest.mark.django_db


def test_devolve_as_etapas_do_conteudo_vigente(edital_a):
    vigentes = etapas_vigentes(edital_a)

    assert set(vigentes) == {
        __import__("uuid").UUID(identificador(ETAPA_A1, 0)),
        __import__("uuid").UUID(identificador(ETAPA_A2, 0)),
    }
    assert vigentes[__import__("uuid").UUID(identificador(ETAPA_A1, 0))]["name"] == (
        "Análise documental"
    )


def test_nao_le_a_colecao_de_elaboracao(edital_a, monkeypatch):
    """A linha de elaboração e a Etapa publicada podem divergir — e é o publicado que vale.

    Apagar as linhas de `EtapaAvaliacao` não pode mudar a resposta: o resolvedor lê o snapshot.
    """
    from processo_seletivo.editais.models.etapas import EtapaAvaliacao

    EtapaAvaliacao.objects.filter(edital=edital_a).delete()

    assert len(etapas_vigentes(edital_a)) == 2


def test_edital_sem_versao_publicada_recusa(db, api_client, manager_headers):
    """FR-032 e EC-014: sem conteúdo vigente não há o que alocar."""
    from processo_seletivo.processos.models import Edital

    criado = api_client.post(
        "/api/v1/admin/processos",
        {
            "institutionalCode": "PS-2026-009",
            "title": "Em elaboração",
            "firstEdital": {"number": "09", "year": 2026, "title": "Rascunho"},
        },
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "sem-publicacao-1"},
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])

    with pytest.raises(DomainError) as recusa:
        etapas_vigentes(edital)

    assert recusa.value.code == "edital_sem_versao_vigente"
    assert recusa.value.status == 409


def test_etapa_vigente_devolve_none_para_identidade_desconhecida(edital_a):
    assert etapa_vigente(edital_a, "00000000-0000-0000-0000-000000000999") is None
