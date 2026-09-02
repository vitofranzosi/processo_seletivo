"""As rotas de conta, conforme `contracts/area.md`."""

import pytest
from django.urls import reverse

from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.models import CandidateEmail
from processo_seletivo.portal import identidade as identidade_do_candidato

pytestmark = [pytest.mark.django_db, pytest.mark.contract]

MEU = "meu@exemplo.test"
SEGUNDO = "segundo@exemplo.test"


@pytest.fixture
def dentro(client):
    identidade = associacao.criar_identidade_com(MEU, MEU)
    associacao.associar_credencial(identidade, SEGUNDO, SEGUNDO)
    sessao = client.session
    sessao[identidade_do_candidato.CHAVE_SESSAO] = str(identidade.pk)
    sessao.save()
    return identidade


def test_a_conta_responde_200(client, dentro):
    assert client.get(reverse("portal:conta")).status_code == 200


def test_a_conta_exige_sessao(client):
    resposta = client.get(reverse("portal:conta"))
    assert resposta.status_code == 302
    assert resposta["Location"] == reverse("portal:acesso")


def test_a_conta_nao_e_armazenavel_pelo_navegador(client, dentro):
    """Ela lista endereços da pessoa: não fica no cache de um computador compartilhado."""
    assert "no-store" in client.get(reverse("portal:conta"))["Cache-Control"]


def test_os_atos_sao_post(client, dentro):
    """Ato acontece em POST, sempre.

    `conta-remover` responde a `GET` desde que a remoção passou a perguntar antes — e o `GET` só
    pergunta: quem o abre encontra a confirmação, e a credencial continua onde estava.
    """
    credencial = CandidateEmail.objects.get(identidade=dentro, email_canonico=SEGUNDO)
    for rota, args in (
        ("portal:conta-adicionar", []),
        ("portal:conta-principal", [credencial.id]),
    ):
        assert client.get(reverse(rota, args=args)).status_code == 405, rota

    pergunta = client.get(reverse("portal:conta-remover", args=[credencial.id]))

    assert pergunta.status_code == 200
    assert "Remover este e-mail?" in pergunta.content.decode()
    assert CandidateEmail.objects.filter(pk=credencial.pk).exists(), "perguntar não remove"


def test_adicionar_redireciona_para_o_codigo(client, dentro):
    resposta = client.post(reverse("portal:conta-adicionar"), {"email": "terceiro@exemplo.test"})
    assert resposta.status_code == 302
    assert resposta["Location"] == reverse("portal:acesso-codigo")


def test_endereco_malformado_volta_para_a_conta(client, dentro):
    resposta = client.post(reverse("portal:conta-adicionar"), {"email": "isto-nao-e-email"})
    assert resposta["Location"] == reverse("portal:conta")
    assert "Informe um e-mail válido" in client.get(reverse("portal:conta")).content.decode()


def test_a_conta_exige_sessao_nas_acoes(client, dentro):
    credencial = CandidateEmail.objects.get(identidade=dentro, email_canonico=SEGUNDO)
    client.post(reverse("portal:sair"))
    for rota, args in (
        ("portal:conta-adicionar", []),
        ("portal:conta-principal", [credencial.id]),
        ("portal:conta-remover", [credencial.id]),
    ):
        resposta = client.post(reverse(rota, args=args))
        assert resposta["Location"] == reverse("portal:acesso"), rota
