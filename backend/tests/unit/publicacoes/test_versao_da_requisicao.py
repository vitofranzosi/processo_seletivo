"""A versão vigente lida uma vez por Edital na requisição (160, R-009, T030, FR-6879).

**Reler dentro da requisição não é cache** (D-009 da `160`): fora do contexto nada se guarda, e
dentro dele só a versão vigente do instante da requisição. A leitura de um ato pela norma que ele
citou, com outro `at`, vai ao banco.
"""

from datetime import timedelta

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from processo_seletivo.publicacoes.application import selectors as s
from tests.fixtures.comissao import publicar_processo_com_etapas

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publicar_processo_com_etapas(api_client, manager_headers, process_payload)


def consultas(funcao):
    with CaptureQueriesContext(connection) as capturadas:
        funcao()
    return len(capturadas)


def test_fora_do_contexto_cada_chamada_vai_ao_banco(edital):
    um = consultas(lambda: s.effective_version(edital_id=edital.id))
    dois = consultas(lambda: s.effective_version(edital_id=edital.id))
    assert um == dois > 0


def test_dentro_do_contexto_o_vigente_e_lido_uma_vez(edital):
    with s.versao_vigente_da_requisicao():
        agora = s.agora_da_requisicao()
        primeira = consultas(lambda: s.effective_version(edital_id=edital.id))
        sem_at = consultas(lambda: s.effective_version(edital_id=edital.id))
        com_o_mesmo_at = consultas(lambda: s.effective_version(edital_id=edital.id, at=agora))
    assert primeira > 0
    assert sem_at == com_o_mesmo_at == 0
    assert s.agora_da_requisicao() is None


def test_outro_instante_vai_ao_banco_mesmo_dentro_do_contexto(edital):
    with s.versao_vigente_da_requisicao():
        s.effective_version(edital_id=edital.id)
        historico = consultas(
            lambda: s.effective_version(edital_id=edital.id, at=timezone.now() + timedelta(days=1))
        )
    assert historico > 0


def test_quem_altera_o_conteudo_nao_contamina_a_leitura_seguinte(edital):
    with s.versao_vigente_da_requisicao():
        primeira = s.effective_version(edital_id=edital.id)
        primeira.content["alterado_em_memoria"] = True
        segunda = s.effective_version(edital_id=edital.id)
    assert "alterado_em_memoria" not in segunda.content
