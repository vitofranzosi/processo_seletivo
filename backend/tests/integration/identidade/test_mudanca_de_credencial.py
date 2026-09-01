"""Mexer em quem alcança a conta pergunta antes e avisa depois.

Sem senha, a lista de credenciais **é** a conta: quem consegue anexar um endereço a ela entra por
ele para sempre, e quem remove um endereço tira uma via de acesso. Nenhum dos dois atos deixava
sinal — "Remover" ficava ao lado de "Tornar principal" e apagava no primeiro clique, e a caixa
principal, que é por onde a instituição fala com a pessoa, nunca ficava sabendo de nada.

A mensagem do código também não distinguia as duas finalidades, e dizia o **oposto** do risco: em
"adicionar credencial", quem obtém o código não entra na conta de quem recebeu — anexa a caixa de
quem recebeu à conta dele.
"""

import re

import pytest
from django.core import mail
from django.urls import reverse

from processo_seletivo.identidade.application import desafio as servico
from processo_seletivo.identidade.application.mensagem import enviar_codigo
from processo_seletivo.identidade.models import CandidateEmail, DesafioDeAcesso
from tests.fixtures.candidato import MARIA, identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

SEGUNDO = "segunda.caixa@exemplo.test"


@pytest.fixture
def caixa(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    settings.PORTAL_ATENDIMENTO = "selecao@cefor.ifes.edu.br"
    mail.outbox.clear()
    return mail.outbox


@pytest.fixture
def com_duas(client, caixa, candidatos_registrados):
    identificar(client, MARIA)
    client.post(reverse("portal:conta-adicionar"), {"email": SEGUNDO})
    codigo = re.search(r"\b(\d{6})\b", mail.outbox[-1].body).group(1)
    client.post(reverse("portal:acesso-codigo"), {"codigo": codigo})
    return CandidateEmail.objects.get(email_canonico=SEGUNDO)


def test_remover_pergunta_antes(client, com_duas):
    pergunta = client.get(reverse("portal:conta-remover", args=[com_duas.id]))

    corpo = pergunta.content.decode()
    assert "Remover este e-mail?" in corpo
    assert SEGUNDO in corpo
    assert "Voltar sem remover" in corpo
    assert CandidateEmail.objects.filter(pk=com_duas.pk).exists()


def test_a_pergunta_sobre_a_ultima_explica_em_vez_de_perguntar(
    client, caixa, candidatos_registrados
):
    identificar(client, MARIA)
    unica = CandidateEmail.objects.get(email_canonico=MARIA.email)

    corpo = client.get(reverse("portal:conta-remover", args=[unica.id])).content.decode()

    assert "é por ele que você entra" in corpo
    assert "Remover este e-mail</button>" not in corpo, "não se oferece o que não pode acontecer"


def test_a_credencial_alheia_nao_tem_nem_pergunta(client, caixa, candidatos_registrados):
    from tests.fixtures.candidato import JOAO

    identificar(client, MARIA)
    do_joao = CandidateEmail.objects.get(email_canonico=JOAO.email)

    assert client.get(reverse("portal:conta-remover", args=[do_joao.id])).status_code == 404


def test_adicionar_avisa_a_caixa_principal(client, caixa, com_duas):
    aviso = [m for m in caixa if "Mudança no acesso" in m.subject]

    assert len(aviso) == 1
    assert aviso[0].to == [MARIA.email], "quem precisa saber é quem já usava a conta"
    assert SEGUNDO in aviso[0].body
    assert "adicionado" in aviso[0].body
    assert "selecao@cefor.ifes.edu.br" in aviso[0].body, "e diz onde reclamar"


def test_remover_avisa_a_caixa_que_fica(client, caixa, com_duas):
    caixa.clear()

    client.post(reverse("portal:conta-remover", args=[com_duas.id]))

    aviso = [m for m in caixa if "Mudança no acesso" in m.subject]
    assert len(aviso) == 1
    assert aviso[0].to == [MARIA.email]
    assert "removido" in aviso[0].body


def test_remover_a_principal_avisa_a_que_foi_promovida(client, caixa, com_duas):
    """Lido depois do ato: ler antes mandaria o aviso para a caixa que acabou de sair."""
    principal = CandidateEmail.objects.get(email_canonico=MARIA.email)
    caixa.clear()

    client.post(reverse("portal:conta-remover", args=[principal.id]))

    aviso = [m for m in caixa if "Mudança no acesso" in m.subject]
    assert aviso[0].to == [SEGUNDO]


def test_falha_do_aviso_nao_custa_o_ato(client, caixa, com_duas, monkeypatch):
    from processo_seletivo.identidade.application import mensagem

    monkeypatch.setattr(
        mensagem, "send_mail", lambda **_: (_ for _ in ()).throw(RuntimeError("smtp fora"))
    )

    client.post(reverse("portal:conta-remover", args=[com_duas.id]))

    assert not CandidateEmail.objects.filter(pk=com_duas.pk).exists(), "a remoção aconteceu"


def test_o_codigo_de_vincular_endereco_diz_o_risco_certo(caixa):
    enviar_codigo(
        para=SEGUNDO,
        codigo="123456",
        finalidade=DesafioDeAcesso.Finalidade.ADICIONAR_CREDENCIAL,
    )

    corpo = caixa[-1].body
    assert "Confirme este e-mail" in caixa[-1].subject
    assert "não informe este código a ninguém" in corpo
    assert "entrar na conta dele\npor este endereço" in corpo
    # A frase do login está errada aqui: o risco não é alguém entrar na conta de quem recebeu.
    assert "ninguém entra sem ele" not in corpo


def test_o_codigo_de_entrar_continua_como_estava(caixa):
    enviar_codigo(para=MARIA.email, codigo="123456", finalidade=DesafioDeAcesso.Finalidade.ENTRAR)

    assert "Seu código de acesso" in caixa[-1].subject
    assert "ignore esta mensagem: ninguém entra sem ele" in caixa[-1].body


def test_a_finalidade_do_desafio_chega_a_mensagem(client, caixa, candidatos_registrados):
    """Guarda de fiação: a view precisa passar a finalidade, ou o texto volta a ser o do login."""
    identificar(client, MARIA)

    client.post(reverse("portal:conta-adicionar"), {"email": "terceira@exemplo.test"})

    assert servico.DesafioDeAcesso.objects.filter(
        email_canonico="terceira@exemplo.test",
        finalidade=DesafioDeAcesso.Finalidade.ADICIONAR_CREDENCIAL,
    ).exists()
    assert "Confirme este e-mail" in caixa[-1].subject
