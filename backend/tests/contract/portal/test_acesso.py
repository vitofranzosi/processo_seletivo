"""As rotas de acesso, conforme `contracts/acesso.md`.

O que se fixa aqui é a superfície: método, estado e destino. O comportamento por trás está nos
testes de integração; o que este arquivo impede é a rota mudar de forma sem que ninguém perceba.
"""

import pytest
from django.urls import reverse

from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.application import desafio as servico
from processo_seletivo.identidade.models import DesafioDeAcesso
from processo_seletivo.portal import identidade as identidade_do_candidato

pytestmark = [pytest.mark.django_db, pytest.mark.contract]

ENDERECO = "maria@exemplo.test"


def test_a_tela_de_endereco_responde(client):
    assert client.get(reverse("portal:acesso")).status_code == 200


def test_o_pedido_redireciona_para_o_codigo(client):
    resposta = client.post(reverse("portal:acesso"), {"email": ENDERECO})
    assert resposta.status_code == 302
    assert resposta["Location"] == reverse("portal:acesso-codigo")


def test_endereco_malformado_responde_200_com_a_recusa(client):
    """Caso distinto dos demais, e legitimamente: a recusa fala da forma do que foi digitado.

    Ela é anterior a qualquer consulta, e por isso não revela nada sobre quem existe.
    """
    resposta = client.post(reverse("portal:acesso"), {"email": "maria"})
    assert resposta.status_code == 200
    assert "Informe um e-mail válido" in resposta.content.decode()


def test_a_tela_do_codigo_exige_ter_informado_o_endereco(client):
    resposta = client.get(reverse("portal:acesso-codigo"))
    assert resposta.status_code == 302
    assert resposta["Location"] == reverse("portal:acesso")


def test_codigo_valido_leva_a_minhas_inscricoes(client):
    client.post(reverse("portal:acesso"), {"email": ENDERECO})
    codigo = DesafioDeAcesso.objects.get()
    _, valor = servico.solicitar(email_canonico="outro@exemplo.test", finalidade="ENTRAR")
    # O código real é o do primeiro desafio; recria-se um conhecido para o mesmo endereço.
    DesafioDeAcesso.objects.filter(pk=codigo.pk).delete()
    _, conhecido = servico.solicitar(
        email_canonico=ENDERECO, finalidade=DesafioDeAcesso.Finalidade.ENTRAR
    )
    resposta = client.post(reverse("portal:acesso-codigo"), {"codigo": conhecido})
    assert resposta.status_code == 302
    assert resposta["Location"] == reverse("portal:inscricoes")


def test_codigo_invalido_responde_200_sem_revelar_quem_existe(client):
    """A recusa nomeia a causa **do desafio**, e nunca diz nada sobre a identidade.

    A frase única cobria quatro motivos e, com isso, mentia no pior deles: esgotadas as tentativas,
    o código certo era recusado como se estivesse errado (ver `test_recusa_do_codigo`). O que a
    FR-031 proíbe é outra coisa — distinguir código errado de endereço inexistente —, e é isso que
    continua verificado aqui e em `test_a_recusa_nao_distingue_quem_existe`.
    """
    client.post(reverse("portal:acesso"), {"email": ENDERECO})
    resposta = client.post(reverse("portal:acesso-codigo"), {"codigo": "000000"})
    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert "Código incorreto" in corpo
    for revelador in ("não encontrado", "não existe", "não cadastrado", "sem identidade"):
        assert revelador not in corpo


def test_quem_ja_entrou_nao_volta_para_a_tela_de_acesso(client):
    identidade = associacao.criar_identidade_com(ENDERECO, ENDERECO)
    sessao = client.session
    sessao[identidade_do_candidato.CHAVE_SESSAO] = str(identidade.pk)
    sessao.save()
    resposta = client.get(reverse("portal:acesso"))
    assert resposta.status_code == 302
    assert resposta["Location"] == reverse("portal:inscricoes")


def test_minhas_inscricoes_exige_sessao(client):
    resposta = client.get(reverse("portal:inscricoes"))
    assert resposta.status_code == 302
    assert resposta["Location"] == reverse("portal:acesso")
