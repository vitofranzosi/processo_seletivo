"""Acrescentar um endereço: prova de controle, e nada mais (FR-016, FR-017).

A feature existe para prevenir a perda de acesso **antes** que ela aconteça — quem troca de
provedor entre um certame e outro é o caso real, e a hora de resolver é com a caixa antiga ainda
funcionando.
"""

import re

import pytest
from django.core import mail
from django.urls import reverse

from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.models import CandidateEmail, DesafioDeAcesso
from processo_seletivo.portal import identidade as identidade_do_candidato

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

MEU = "meu@exemplo.test"
NOVO = "novo@exemplo.test"
ALHEIO = "de.outra.pessoa@exemplo.test"


@pytest.fixture
def canal(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    mail.outbox.clear()
    return mail.outbox


@pytest.fixture
def dentro(client):
    identidade = associacao.criar_identidade_com(MEU, MEU)
    sessao = client.session
    sessao[identidade_do_candidato.CHAVE_SESSAO] = str(identidade.pk)
    sessao.save()
    return identidade


def codigo(canal):
    return re.search(r"\b(\d{6})\b", canal[-1].body).group(1)


def test_adicionar_pede_codigo_e_nao_pede_cpf(client, dentro, canal):
    resposta = client.post(reverse("portal:conta-adicionar"), {"email": NOVO})

    assert resposta["Location"] == reverse("portal:acesso-codigo")
    corpo = client.get(reverse("portal:acesso-codigo")).content.decode()
    assert "CPF" not in corpo
    assert canal[-1].to == [NOVO]


def test_confirmado_o_codigo_o_endereco_passa_a_ser_credencial(client, dentro, canal):
    client.post(reverse("portal:conta-adicionar"), {"email": NOVO})
    resposta = client.post(reverse("portal:acesso-codigo"), {"codigo": codigo(canal)})

    assert resposta["Location"] == reverse("portal:conta")
    assert set(
        CandidateEmail.objects.filter(identidade=dentro).values_list("email_canonico", flat=True)
    ) == {MEU, NOVO}


def test_a_credencial_nova_nao_vira_principal_sozinha(client, dentro, canal):
    """Trocar o contato de um certame em andamento é decisão, e não efeito colateral (FR-013)."""
    client.post(reverse("portal:conta-adicionar"), {"email": NOVO})
    client.post(reverse("portal:acesso-codigo"), {"codigo": codigo(canal)})

    assert CandidateEmail.objects.get(identidade=dentro, principal=True).email_canonico == MEU


def test_a_credencial_nova_passa_a_autenticar(client, dentro, canal):
    client.post(reverse("portal:conta-adicionar"), {"email": NOVO})
    client.post(reverse("portal:acesso-codigo"), {"codigo": codigo(canal)})
    client.post(reverse("portal:sair"))
    DesafioDeAcesso.objects.all().delete()

    client.post(reverse("portal:acesso"), {"email": NOVO})
    resposta = client.post(reverse("portal:acesso-codigo"), {"codigo": codigo(canal)})

    assert resposta["Location"] == reverse("portal:inscricoes")
    atual = identidade_do_candidato.identidade_autenticada(
        type("R", (), {"session": client.session})()
    )
    assert atual.pk == dentro.pk


def test_endereco_de_outra_identidade_e_recusado_sem_dizer_de_quem(client, dentro, canal):
    associacao.criar_identidade_com(ALHEIO, ALHEIO)

    resposta = client.post(reverse("portal:conta-adicionar"), {"email": ALHEIO})

    assert resposta["Location"] == reverse("portal:conta")
    corpo = client.get(reverse("portal:conta")).content.decode()
    # A recusa é lida na própria mensagem, e não na página inteira: o `<style>` da base menciona
    # palavras que nada têm a ver com identidade, e afirmar sobre a página toda mediria o CSS.
    import re as _re

    mensagem = _re.search(r'class="aviso recusa-em-destaque">(.*?)</p>', corpo, _re.S).group(1)
    assert "Não foi possível usar este endereço" in mensagem
    # "Tente outro" é convite, não revelação — o que não pode aparecer é atribuição de dono.
    for revelador in ("pertence", "existe", "cadastrad", "outra conta", "outro candidato"):
        assert revelador not in mensagem.lower(), revelador
    assert ALHEIO not in mensagem


def test_a_recusa_acontece_antes_de_qualquer_mensagem(client, dentro, canal):
    """Enviar código para o endereço alheio já contaria a essa pessoa que alguém tentou."""
    associacao.criar_identidade_com(ALHEIO, ALHEIO)
    canal.clear()

    client.post(reverse("portal:conta-adicionar"), {"email": ALHEIO})

    assert canal == []


def test_adicionar_o_proprio_endereco_nao_duplica(client, dentro, canal):
    resposta = client.post(reverse("portal:conta-adicionar"), {"email": MEU})

    assert resposta["Location"] == reverse("portal:conta")
    assert CandidateEmail.objects.filter(identidade=dentro).count() == 1


def test_codigo_de_adicionar_nao_serve_para_entrar(client, dentro, canal):
    """Finalidades não se confundem (FR-028)."""
    from processo_seletivo.identidade.application import desafio as servico

    client.post(reverse("portal:conta-adicionar"), {"email": NOVO})
    valor = codigo(canal)

    assert (
        servico.validar(
            email_canonico=NOVO, finalidade=DesafioDeAcesso.Finalidade.ENTRAR, codigo=valor
        )
        is None
    )
