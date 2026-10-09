"""O despacho quando o correio falha: o que se tenta de novo, o que nunca se tenta (066, US5).

**A assimetria que o usuário exigiu.** Recusa explícita do servidor tem resposta; queda, timeout e
resposta ilegível não. A primeira se classifica e, sendo temporária, se tenta de novo; a segunda
fica indeterminada e **nunca** sai sozinha de novo, porque a mensagem pode ter saído (`FR-1267`).
"""

import math
from datetime import timedelta

import pytest
from django.core import mail
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone

from processo_seletivo.avisos.application import selectors
from processo_seletivo.avisos.application.despacho import ConexaoNaoAbriu, despachar
from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.models import Aviso, ResultadoDaTentativa, TentativaDeEnvio
from tests.fixtures import correio
from tests.fixtures.avisos import avisar_resultado, engordar
from tests.fixtures.divulgacao import montar_ato_publicavel, publicar_o_ato

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def avisado(gestor, api_client, manager_headers, process_payload):
    cenario = montar_ato_publicavel(
        gestor, api_client, manager_headers, process_payload, pontuacoes=("90.0000", "70.0000")
    )
    cenario["publicacao"] = publicar_o_ato(cenario)
    cenario["aviso"] = Aviso.objects.get(
        pk=avisar_resultado(cenario["edital"], cenario["publicacao"].marco_id)["aviso"]
    )
    return cenario


@pytest.fixture
def relogio(monkeypatch):
    real = timezone.now

    def avancar(**intervalo):
        monkeypatch.setattr(timezone, "now", lambda: real() + timedelta(**intervalo))

    return avancar


def _estados(aviso):
    return sorted(
        estado for _, estado, _ in selectors.estados_do_aviso(aviso, agora=timezone.now())
    )


def test_conexao_que_nao_abre_nao_registra_tentativa(avisado, settings):
    """Fase 0: nada saiu, e a próxima execução tenta. O comando sai com erro, para o alerta."""
    import smtplib

    correio.usar(settings, abertura=smtplib.SMTPConnectError(421, b"busy"))

    with pytest.raises(ConexaoNaoAbriu):
        despachar()
    with pytest.raises(CommandError):
        call_command("despachar_avisos")

    assert TentativaDeEnvio.objects.count() == 0
    assert mail.outbox == []


def test_falha_temporaria_espera_o_intervalo_e_esgota_no_limite(avisado, settings, relogio):
    correio.usar(settings, *[correio.recusa(451)] * 10)

    despachar(limite=1)
    assert ResultadoDaTentativa.objects.get().resultado == nomes.FALHA_TEMPORARIA
    despachar(limite=1)
    assert TentativaDeEnvio.objects.count() == 2, "o outro destinatário, e não o mesmo de novo"

    relogio(minutes=6)
    despachar(limite=1)
    relogio(minutes=25)
    despachar(limite=1)
    despachar(limite=1)
    relogio(minutes=45)
    despachar()

    assert TentativaDeEnvio.objects.count() == 6, "três tentativas para cada um, e nenhuma a mais"
    assert _estados(avisado["aviso"]) == [nomes.ESTADO_FALHA_DEFINITIVA] * 2


def test_recusa_5xx_e_definitiva_e_nao_se_tenta(avisado, settings, relogio):
    correio.usar(settings, correio.recusa(550), correio.recusa(554, fase="data"))

    despachar()
    relogio(hours=1)
    despachar()

    assert TentativaDeEnvio.objects.count() == 2
    assert set(ResultadoDaTentativa.objects.values_list("resultado", flat=True)) == {
        nomes.FALHA_DEFINITIVA
    }


def test_aceita_e_derruba_e_indeterminada_para_a_execucao_e_nunca_se_repete(
    avisado, settings, relogio
):
    """O caso que o usuário nomeou: a mensagem saiu e a resposta não chegou."""
    correio.usar(settings, correio.aceita_e_derruba())

    resumo = despachar()

    assert resumo.tentadas == 1, "a execução para na primeira indeterminada"
    assert ResultadoDaTentativa.objects.get().resultado == nomes.INDETERMINADA
    assert len(mail.outbox) == 1

    relogio(hours=2)
    despachar()

    assert len(mail.outbox) == 2, "o outro destinatário sai; o indeterminado, não"
    assert _estados(avisado["aviso"]) == sorted([nomes.ESTADO_ACEITA, nomes.ESTADO_INDETERMINADA])


def test_tentativa_orfa_e_marcada_indeterminada_e_nao_se_repete(avisado, settings):
    """A execução que morreu entre o início e o resultado: com a trava, a órfã é de ninguém vivo."""
    correio.usar(settings)
    destinatario = avisado["aviso"].destinatarios.order_by("id").first()
    TentativaDeEnvio.objects.create(
        destinatario=destinatario, numero=1, iniciada_em=timezone.now() - timedelta(minutes=10)
    )

    resumo = despachar()

    assert resumo.orfas == 1
    orfa = ResultadoDaTentativa.objects.get(tentativa__destinatario=destinatario)
    assert orfa.resultado == nomes.INDETERMINADA
    assert len(mail.outbox) == 1, "só o outro destinatário recebe"
    assert TentativaDeEnvio.objects.filter(destinatario=destinatario).count() == 1


def test_zero_aceitas_e_falha_temporaria(avisado, settings):
    correio.usar(settings, 0)

    despachar(limite=1)

    assert ResultadoDaTentativa.objects.get().resultado == nomes.FALHA_TEMPORARIA


def test_o_detalhe_tecnico_nao_leva_endereco_nem_nome(avisado, settings):
    """`FR-1279`: o servidor ecoa o endereço, e o detalhe vai para a tela da gestão."""
    destinatarios = list(avisado["aviso"].destinatarios.select_related("inscricao"))
    correio.usar(
        settings,
        correio.recusa(550, endereco=destinatarios[0].endereco),
        correio.recusa(451, endereco=destinatarios[1].endereco),
    )

    despachar()

    for resultado in ResultadoDaTentativa.objects.all():
        for destinatario in destinatarios:
            assert destinatario.endereco not in resultado.detalhe_tecnico
            assert destinatario.inscricao.nome not in resultado.detalhe_tecnico


def test_quinhentos_com_o_limite_inicial_terminam_em_nove_execucoes(
    gestor, api_client, manager_headers, process_payload, settings
):
    """SC-483: 500 destinatários a 60 por execução, uma por minuto — dentro de 15 minutos."""
    cenario = montar_ato_publicavel(
        gestor, api_client, manager_headers, process_payload, pontuacoes=("90.0000", "70.0000")
    )
    publicacao = publicar_o_ato(cenario)
    engordar(publicacao, 498)
    aviso = Aviso.objects.get(
        pk=avisar_resultado(cenario["edital"], publicacao.marco_id, chave="quinhentos")["aviso"]
    )
    correio.usar(settings)
    execucoes = math.ceil(500 / settings.AVISOS_LIMITE_POR_MINUTO)

    for _ in range(execucoes - 1):
        assert despachar().tentadas == settings.AVISOS_LIMITE_POR_MINUTO
    despachar()

    assert execucoes <= 15
    assert len(mail.outbox) == 500
    assert set(_estados(aviso)) == {nomes.ESTADO_ACEITA}
    assert despachar().tentadas == 0, "e nada mais sai depois"
