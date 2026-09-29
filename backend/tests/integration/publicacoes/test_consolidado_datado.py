"""O consolidado da Retificação se diz consolidado, e de quando (054, FR-995; SC-367).

A marca é composta pelo compositor (`tests/unit/publicacoes/test_fecho_e_normas_da_054.py`); aqui o
que se prova é que `publish_retification` entrega as datas certas: a da publicação original, a de
cada Retificação que o conteúdo incorpora, e a vigência quando ela começa em outro dia.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.editais.domain import secoes
from processo_seletivo.publicacoes.domain.conflicts import previous_hash
from processo_seletivo.publicacoes.infrastructure.humano import data_por_extenso
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.shared.tempo import ZONA
from tests.fixtures.publicacao import publish_original, retify
from tests.unit.publicacoes.test_pdf import texto_de

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def _texto_da_secao(edital, chave, texto, base=None):
    base = base or VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    caminho = f"/sections/id={secoes.identidade(edital.id, chave)}/content"
    return [
        {
            "targetPath": caminho,
            "operation": "REPLACE",
            "newValue": texto,
            "expectedPreviousHash": previous_hash(base.content, caminho),
        }
    ]


def _documentos(edital):
    return [
        texto_de(bytes(publicacao.documento.bytes))
        for publicacao in Publicacao.objects.filter(edital=edital).order_by("publication_order")
    ]


def _hoje():
    return data_por_extenso(timezone.now().astimezone(ZONA).date())


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload)


def test_o_original_nao_tem_marca_e_o_consolidado_tem_as_duas_datas(api_client, edital):
    retify(api_client, edital, _texto_da_secao(edital, "certificado", "Certificado digital."))

    original, consolidado = _documentos(edital)
    assert "Versão consolidada" not in original
    assert f"Versão consolidada. Publicado em {_hoje()}; retificado em {_hoje()}." in consolidado
    # E a seção que a Retificação escreveu passa a sair (US4, cenário 3).
    assert "Certificado digital." in consolidado
    assert "Certificado digital." not in original


def test_a_segunda_retificacao_lista_as_duas(api_client, edital):
    retify(api_client, edital, _texto_da_secao(edital, "certificado", "Um."), suffix="a")
    retify(api_client, edital, _texto_da_secao(edital, "certificado", "Dois."), suffix="b")

    *_, ultimo = _documentos(edital)
    assert f"retificado em {_hoje()} e em {_hoje()}." in ultimo.replace("\n", " ")


def test_a_vigencia_em_outro_dia_e_declarada(api_client, edital):
    vigencia = timezone.now() + timedelta(days=3)
    retify(
        api_client,
        edital,
        _texto_da_secao(edital, "certificado", "Certificado digital."),
        effective_at=vigencia.isoformat(),
    )

    *_, consolidado = _documentos(edital)
    dia = data_por_extenso(vigencia.astimezone(ZONA).date())
    assert f"com vigência a partir de {dia}." in consolidado
    # O fecho é o da Retificação: a data dela, e não a da vigência.
    assert f"Vitória (ES), {_hoje()}." in consolidado
