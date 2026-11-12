"""A versão vigente lida uma vez por Edital na requisição (160, R-009, T030, FR-6879).

**Reler dentro da requisição não é cache** (D-009 da `160`): fora do contexto nada se guarda, e
dentro dele a versão guardada vale para todo instante entre a abertura do bloco e a próxima
vigência do Edital. Antes da abertura é a leitura de um ato pela norma que ele citou, e vai ao
banco; depois da próxima vigência, também.
"""

import uuid
from datetime import timedelta

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from processo_seletivo.publicacoes.application import selectors as s
from processo_seletivo.shared.api.problems import DomainError
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


def test_dentro_do_contexto_o_vigente_e_lido_uma_vez_e_cada_um_usa_o_seu_agora(edital):
    with s.versao_vigente_da_requisicao():
        primeira = consultas(lambda: s.effective_version(edital_id=edital.id))
        sem_at = consultas(lambda: s.effective_version(edital_id=edital.id))
        agora_proprio = consultas(
            lambda: s.effective_version(edital_id=edital.id, at=timezone.now())
        )
    assert primeira > 0
    assert sem_at == agora_proprio == 0


def test_instante_anterior_a_abertura_vai_ao_banco(edital):
    with s.versao_vigente_da_requisicao():
        abertura = s._VERSOES_DA_REQUISICAO.get()["abertura"]
        s.effective_version(edital_id=edital.id)
        historico = consultas(
            lambda: s.effective_version(
                edital_id=edital.id, at=abertura - timedelta(microseconds=1)
            )
        )
    assert historico > 0


def test_depois_da_proxima_vigencia_vai_ao_banco(edital, monkeypatch):
    with s.versao_vigente_da_requisicao():
        abertura = s._VERSOES_DA_REQUISICAO.get()["abertura"]
        monkeypatch.setattr(s, "_proxima_vigencia", lambda *_: abertura + timedelta(seconds=1))
        s.effective_version(edital_id=edital.id)
        antes = consultas(lambda: s.effective_version(edital_id=edital.id, at=abertura))
        depois = consultas(
            lambda: s.effective_version(edital_id=edital.id, at=abertura + timedelta(seconds=2))
        )
    assert antes == 0
    assert depois > 0


def test_a_falta_de_versao_tambem_se_guarda():
    inexistente = uuid.uuid4()
    with s.versao_vigente_da_requisicao():
        with pytest.raises(DomainError):
            s.effective_version(edital_id=inexistente)

        def de_novo():
            with pytest.raises(DomainError):
                s.effective_version(edital_id=inexistente)

        assert consultas(de_novo) == 0


def test_quem_altera_o_conteudo_nao_contamina_a_leitura_seguinte(edital):
    with s.versao_vigente_da_requisicao():
        primeira = s.effective_version(edital_id=edital.id)
        primeira.content["alterado_em_memoria"] = True
        segunda = s.effective_version(edital_id=edital.id)
    assert "alterado_em_memoria" not in segunda.content
