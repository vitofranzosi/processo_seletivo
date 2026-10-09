"""A chave de habilitação e a janela de despacho (066, `D-009`, `FR-1282`, `FR-1283`).

**Religar a chave não dispara o que ficou para trás.** A chave é configuração do ambiente e o banco
não a vê mudar; o que ele vê é a idade do aviso. Dentro da janela, o pendente sai; fora dela, expira
sem envio, e só um aviso filho, confirmado por uma pessoa, o reenvia. A mesma regra cobre o timer
parado por dias.
"""

from datetime import timedelta

import pytest
from django.core import mail
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.avisos.application import selectors
from processo_seletivo.avisos.application.confirmar import confirmar_reenvio
from processo_seletivo.avisos.application.despacho import despachar
from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.models import Aviso, TentativaDeEnvio
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures import correio
from tests.fixtures.avisos import PUBLICADORA, avisar_resultado
from tests.fixtures.divulgacao import montar_ato_publicavel, publicar_o_ato

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def avisado(gestor, api_client, manager_headers, process_payload, settings):
    cenario = montar_ato_publicavel(
        gestor, api_client, manager_headers, process_payload, pontuacoes=("90.0000", "70.0000")
    )
    publicacao = publicar_o_ato(cenario)
    correio.usar(settings)
    return Aviso.objects.get(pk=avisar_resultado(cenario["edital"], publicacao.marco_id)["aviso"])


@pytest.fixture
def relogio(monkeypatch):
    real = timezone.now

    def avancar(**intervalo):
        monkeypatch.setattr(timezone, "now", lambda: real() + timedelta(**intervalo))

    return avancar


def _estados(aviso):
    return {estado for _, estado, _ in selectors.estados_do_aviso(aviso, agora=timezone.now())}


def test_desligada_o_despacho_nao_tenta_nada(avisado, settings):
    settings.AVISOS_AOS_CANDIDATOS = False

    resumo = despachar()

    assert resumo.desabilitado
    assert TentativaDeEnvio.objects.count() == 0
    assert mail.outbox == []


def test_desligada_o_reenvio_e_recusado(avisado, settings, relogio):
    relogio(hours=settings.AVISOS_JANELA_DE_DESPACHO_HORAS, minutes=1)
    settings.AVISOS_AOS_CANDIDATOS = False

    with pytest.raises(DomainError) as erro:
        confirmar_reenvio(
            actor=PUBLICADORA,
            aviso_id=avisado.id,
            motivo=nomes.REENVIO_DE_FALHAS,
            assinatura="",
            enderecos={},
            idempotency_key="reenvio-desligado",
            correlation_id="teste-066",
        )

    assert erro.value.code == nomes.AVISO_ENVIO_DESABILITADO


def test_religada_dentro_da_janela_o_pendente_sai(avisado, settings, relogio):
    settings.AVISOS_AOS_CANDIDATOS = False
    despachar()
    relogio(hours=settings.AVISOS_JANELA_DE_DESPACHO_HORAS - 1)
    settings.AVISOS_AOS_CANDIDATOS = True

    despachar()

    assert len(mail.outbox) == 2


def test_religada_fora_da_janela_expira_sem_envio(avisado, settings, relogio):
    settings.AVISOS_AOS_CANDIDATOS = False
    despachar()
    relogio(hours=settings.AVISOS_JANELA_DE_DESPACHO_HORAS, minutes=1)
    settings.AVISOS_AOS_CANDIDATOS = True

    resumo = despachar()

    assert resumo.tentadas == 0
    assert mail.outbox == []
    assert _estados(avisado) == {nomes.EXPIRADA_SEM_ENVIO}


def test_o_timer_parado_por_dias_nao_dispara_o_antigo(avisado, relogio):
    relogio(days=3)

    assert despachar().tentadas == 0
    assert mail.outbox == []


def test_o_expirado_so_volta_por_aviso_filho(avisado, relogio):
    """O reenvio de falhas alcança o expirado, com o texto do anterior e prévia nova (`R-011`)."""
    from processo_seletivo.avisos.application import destinatarios, previa

    relogio(hours=25)
    universo = destinatarios.universo_do_reenvio(
        avisado, motivo=nomes.REENVIO_DE_FALHAS, agora=timezone.now()
    )

    declarado = confirmar_reenvio(
        actor=PUBLICADORA,
        aviso_id=avisado.id,
        motivo=nomes.REENVIO_DE_FALHAS,
        assinatura=previa.assinatura(universo, motivo=nomes.REENVIO_DE_FALHAS),
        enderecos={},
        idempotency_key="reenvio-expirado",
        correlation_id="teste-066",
    )

    filho = Aviso.objects.get(pk=declarado["aviso"])
    assert filho.aviso_anterior_id == avisado.id
    assert filho.corpo == avisado.corpo
    despachar()
    assert len(mail.outbox) == 2


def test_desligada_o_historico_continua_legivel(avisado, client, settings):
    from tests.interface.conftest import identificar

    settings.INTERFACE_SELETOR_IDENTIDADE = True
    settings.AVISOS_AOS_CANDIDATOS = False
    identificar(client, "publicadora", ["publicador"])

    assert client.get(reverse("interface:aviso", args=[avisado.id])).status_code == 200
    assert client.get(reverse("interface:modelos-de-aviso")).status_code == 200
