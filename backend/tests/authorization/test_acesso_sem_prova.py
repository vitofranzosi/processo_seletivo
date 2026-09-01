"""Nenhuma rota do acesso concede coisa alguma a quem não provou o controle do endereço.

Este arquivo nasce de um desvio de autenticação real, encontrado em revisão. `/acesso/reconciliar`
criava identidade a partir do endereço guardado na sessão — que é apenas o que alguém digitou no
formulário, gravado **antes** de qualquer prova. Bastava informar o e-mail de outra pessoa e abrir
a rota diretamente para entrar em nome dela; e o endereço da vítima ficava preso à identidade do
atacante pela restrição de unicidade, impedindo a dona de usá-lo para sempre.

A suíte não o pegou porque todo teste **seguia o fluxo**. O atacante não segue: ele pula. Daí a
forma destes testes — alcançar cada tela do fluxo por fora e verificar que ela não concede nada.
"""

import pytest
from django.urls import reverse

from processo_seletivo.identidade.models import CandidateEmail, CandidateIdentity
from processo_seletivo.portal import identidade as identidade_do_candidato
from processo_seletivo.portal.views import CHAVE_DO_DESAFIO, CHAVE_DO_ENDERECO

pytestmark = [pytest.mark.django_db, pytest.mark.authorization]

DA_VITIMA = "vitima@exemplo.test"


def autenticado(client):
    return identidade_do_candidato.CHAVE_SESSAO in client.session


def test_informar_o_endereco_alheio_e_abrir_o_convite_nao_da_sessao(client):
    """O desvio, invertido em regressão."""
    client.post(reverse("portal:acesso"), {"email": DA_VITIMA})

    resposta = client.get(reverse("portal:acesso-reconciliar"))

    assert not autenticado(client), "entrou sem provar o controle do endereço"
    assert resposta["Location"] == reverse("portal:acesso")
    assert not CandidateIdentity.objects.filter(credenciais__email_canonico=DA_VITIMA).exists()
    assert not CandidateEmail.objects.filter(email_canonico=DA_VITIMA).exists()


def test_o_convite_tambem_nao_cede_por_post(client):
    client.post(reverse("portal:acesso"), {"email": DA_VITIMA})

    for corpo in ({"acao": "continuar"}, {"acao": "confirmar", "cpf": "123.456.789-09"}):
        resposta = client.post(reverse("portal:acesso-reconciliar"), corpo)
        assert not autenticado(client), corpo
        assert resposta["Location"] == reverse("portal:acesso")


def test_um_identificador_de_desafio_forjado_na_sessao_nao_serve(client):
    """Exigir `consumido_em` fecha a porta também contra sessão adulterada."""
    client.post(reverse("portal:acesso"), {"email": DA_VITIMA})
    sessao = client.session
    sessao[CHAVE_DO_DESAFIO] = "00000000-0000-0000-0000-0000000009ff"
    sessao.save()

    resposta = client.get(reverse("portal:acesso-reconciliar"))

    assert not autenticado(client)
    assert resposta["Location"] == reverse("portal:acesso")


def test_um_desafio_real_mas_nao_consumido_tambem_nao_serve(client):
    """Pedir o código e apontar para ele não é o mesmo que digitá-lo."""
    from processo_seletivo.identidade.models import DesafioDeAcesso

    client.post(reverse("portal:acesso"), {"email": DA_VITIMA})
    desafio = DesafioDeAcesso.objects.get()
    assert desafio.consumido_em is None
    sessao = client.session
    sessao[CHAVE_DO_DESAFIO] = str(desafio.pk)
    sessao.save()

    resposta = client.get(reverse("portal:acesso-reconciliar"))

    assert not autenticado(client)
    assert resposta["Location"] == reverse("portal:acesso")


def test_a_area_pessoal_nao_se_alcanca_por_fora(client):
    client.post(reverse("portal:acesso"), {"email": DA_VITIMA})
    for rota in ("portal:inscricoes", "portal:meus-dados"):
        resposta = client.get(reverse(rota))
        assert resposta.status_code == 302, rota
        assert resposta["Location"] == reverse("portal:acesso"), rota


def test_a_retomada_nao_se_alcanca_por_fora(client):
    client.post(reverse("portal:acesso"), {"email": DA_VITIMA})
    resposta = client.post(reverse("portal:acesso-retomar"))
    assert resposta["Location"] == reverse("portal:acesso")
    assert not autenticado(client)


def test_a_tela_do_codigo_sozinha_nao_autentica(client):
    sessao = client.session
    sessao[CHAVE_DO_ENDERECO] = DA_VITIMA
    sessao.save()

    resposta = client.post(reverse("portal:acesso-codigo"), {"codigo": "000000"})

    assert resposta.status_code == 200
    assert not autenticado(client)
