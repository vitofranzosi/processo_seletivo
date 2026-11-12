# ruff: noqa: F811 — `cenario` é a fixture da 134, importada; os testes a recebem como parâmetro.
"""O pedido de aviso de pendência de uma pessoa (157, D-008; FR-4603, FR-4605, FR-4620 da 134).

**O gesto da `134`, no recorte de uma pessoa.** A decisão do usuário de 11/11/2026: oferecido ao fim
da conferência da pessoa, com todas as pendências elegíveis dela, as mesmas autorizações, exclusões
e limite diário — sem exceção nem agendamento —, e registrar a pendência continua sem gravar aviso.
"""

import pytest
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.avisos.application import pendencias
from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.models import Aviso, DestinatarioDoAviso
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.corte import MARCO
from tests.fixtures.documentos_da_convocacao import HISTORICO, RESIDENCIA, apresentar
from tests.fixtures.edital import PROFILE_ID
from tests.integration.avisos.test_aviso_de_pendencia import (  # noqa: F401 — a fixture
    PORTAL,
    _avisar,
    _pendente,
    cenario,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def _pedir(ator, edital, convocacao, *, chave="pedido-157"):
    return pendencias.avisar_pendencias(
        actor=ator,
        edital_id=edital.id,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=None,
        endereco_do_portal=PORTAL,
        idempotency_key=chave,
        correlation_id="teste-157",
        convocacao_id=convocacao.id,
    )


def _com_duas_pendencias(cenario, gestor):
    pessoa, convocacao = cenario["pessoa_ampla"], cenario["ampla"]
    for requisito in (HISTORICO, RESIDENCIA):
        apresentar(pessoa, convocacao, requisito)
        _pendente(gestor, convocacao, requisito, chave=f"p-{requisito}")
    _pendente_outra = cenario["ppi"]
    apresentar(cenario["pessoa_ppi"], _pendente_outra, HISTORICO)
    _pendente(gestor, _pendente_outra, HISTORICO, chave="p-outra")
    return convocacao


def test_registrar_a_pendencia_nao_grava_aviso(cenario, gestor):
    _com_duas_pendencias(cenario, gestor)
    assert not Aviso.objects.exists()


def test_o_pedido_grava_o_mesmo_aviso_que_o_lote_gravaria_so_para_ela(cenario, gestor):
    convocacao = _com_duas_pendencias(cenario, gestor)

    declarado = _pedir(gestor, cenario["edital"], convocacao)

    assert declarado["alcancadas"] == 1
    destinatario = DestinatarioDoAviso.objects.get()
    assert destinatario.convocacao_id == convocacao.id
    aviso = destinatario.aviso
    assert aviso.origem == nomes.PENDENCIA
    # Todas as pendências elegíveis da pessoa no instante do pedido (FR-6539).
    assert "Histórico escolar do ensino médio" in aviso.corpo
    assert "Comprovante de residência" in aviso.corpo


def test_o_limite_do_dia_e_um_so_para_os_dois_gestos(cenario, gestor):
    convocacao = _com_duas_pendencias(cenario, gestor)
    _avisar(gestor, cenario["edital"], chave="lote-157")

    with pytest.raises(DomainError) as recusa:
        _pedir(gestor, cenario["edital"], convocacao)

    assert recusa.value.code == nomes.AVISO_SEM_PENDENCIA_A_AVISAR
    amanha = pendencias.proximo_dia_do_pedido(timezone.now())
    assert "já foi avisada hoje nesta chamada" in recusa.value.detail
    assert f"{amanha:%d/%m/%Y}" in recusa.value.detail
    assert Aviso.objects.count() == 2, "o lote avisou as duas; o pedido não acrescentou nada"


def test_depois_do_pedido_o_lote_deixa_a_pessoa_de_fora(cenario, gestor):
    convocacao = _com_duas_pendencias(cenario, gestor)
    _pedir(gestor, cenario["edital"], convocacao)

    declarado = _avisar(gestor, cenario["edital"], chave="lote-depois")

    assert declarado["alcancadas"] == 1, "só a outra pessoa"
    assert {"motivo": pendencias.JA_AVISADA_HOJE, "quantas": 1} in declarado["exclusoes"]


def test_sem_pendencia_a_recusa_diz_o_motivo_sem_data(cenario, gestor):
    with pytest.raises(DomainError) as recusa:
        _pedir(gestor, cenario["edital"], cenario["ampla"])

    assert "não há documento pendente" in recusa.value.detail
    assert "a partir de" not in recusa.value.detail
    assert not Aviso.objects.exists()


def test_a_chave_desligada_recusa_como_no_lote(cenario, gestor, settings):
    convocacao = _com_duas_pendencias(cenario, gestor)
    settings.AVISOS_AOS_CANDIDATOS = False

    with pytest.raises(DomainError) as recusa:
        _pedir(gestor, cenario["edital"], convocacao)

    assert recusa.value.code == nomes.AVISO_ENVIO_DESABILITADO


def test_a_trilha_diz_que_o_recorte_foi_de_uma_pessoa(cenario, gestor):
    convocacao = _com_duas_pendencias(cenario, gestor)

    _pedir(gestor, cenario["edital"], convocacao)

    gesto = RegistroAuditoria.objects.get(operation=nomes.OPERACAO_AVISAR_PENDENCIAS)
    assert gesto.detalhe["recorte"] == "pessoa"
    assert gesto.detalhe["convocacao"] == str(convocacao.id)
    assert "de uma pessoa" in gesto.reason
