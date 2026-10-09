"""O despacho, pelo caminho feliz: uma mensagem por pessoa, e o que o servidor aceitou (066, US1).

**O correio da suíte é o de memória do Django**, que `setup_test_environment` impõe, e o despacho o
alcança porque abre a conexão por `get_connection()` — o mecanismo configurado, e nunca uma conexão
própria (`FR-1281`). Nenhum caso aqui alcança servidor de correio real.
"""

from datetime import timedelta

import pytest
from django.core import mail
from django.core.management import call_command
from django.utils import timezone

from processo_seletivo.avisos.application.despacho import despachar
from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.models import ResultadoDaTentativa, TentativaDeEnvio
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.avisos import avisar_resultado
from tests.fixtures.divulgacao import montar_ato_publicavel, publicar_o_ato

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def avisado(gestor, api_client, manager_headers, process_payload):
    cenario = montar_ato_publicavel(
        gestor, api_client, manager_headers, process_payload, pontuacoes=("90.0000", "70.0000")
    )
    publicacao = publicar_o_ato(cenario)
    mail.outbox.clear()
    cenario["aviso"] = avisar_resultado(cenario["edital"], publicacao.marco_id)
    return cenario


def test_uma_mensagem_por_destinatario_com_um_endereco_so(avisado):
    resumo = despachar()

    assert resumo.tentadas == 2
    assert resumo.resultados == {nomes.ACEITA: 2}
    assert len(mail.outbox) == 2
    for mensagem in mail.outbox:
        assert len(mensagem.to) == 1
        assert mensagem.cc == [] and mensagem.bcc == []
        assert mensagem.extra_headers.get("Auto-Submitted") == "auto-generated"
    enderecos = sorted(m.to[0] for m in mail.outbox)
    esperados = sorted(
        Inscricao.objects.filter(pk__in=[i.pk for i in avisado["inscricoes"]]).values_list(
            "email", flat=True
        )
    )
    assert enderecos == esperados


def test_o_texto_e_o_confirmado_com_o_nome_resolvido(avisado):
    despachar()

    nomes_ = {
        i.nome for i in Inscricao.objects.filter(pk__in=[i.pk for i in avisado["inscricoes"]])
    }
    for mensagem in mail.outbox:
        assert "{nome_do_candidato}" not in mensagem.body
        assert any(f"Olá, {nome}." in mensagem.body for nome in nomes_)
        assert mensagem.subject == "Processo Seletivo Ifes — Nova publicação disponível"


def test_aceita_e_registrada_e_nao_sai_de_novo(avisado):
    despachar()
    despachar()

    assert TentativaDeEnvio.objects.count() == 2
    assert set(ResultadoDaTentativa.objects.values_list("resultado", flat=True)) == {nomes.ACEITA}
    assert len(mail.outbox) == 2


def test_chave_desligada_nao_tenta(avisado, settings):
    settings.AVISOS_AOS_CANDIDATOS = False

    resumo = despachar()

    assert resumo.desabilitado
    assert TentativaDeEnvio.objects.count() == 0
    assert mail.outbox == []


def test_janela_vencida_expira_sem_envio(avisado, settings, monkeypatch):
    """`FR-1283`: o aviso mais velho que a janela não sai — religar a chave não o dispara."""
    real = timezone.now
    monkeypatch.setattr(
        timezone,
        "now",
        lambda: real() + timedelta(hours=settings.AVISOS_JANELA_DE_DESPACHO_HORAS, minutes=1),
    )

    resumo = despachar()

    assert resumo.tentadas == 0
    assert mail.outbox == []


def test_o_limite_por_execucao(avisado):
    resumo = despachar(limite=1)

    assert resumo.tentadas == 1
    assert len(mail.outbox) == 1


def test_o_comando_despacha_e_resume(avisado, capsys):
    call_command("despachar_avisos")

    saida = capsys.readouterr().out
    assert "2 tentativa(s) em 1 aviso(s)" in saida
    assert "@" not in saida, "o resumo não leva endereço"
