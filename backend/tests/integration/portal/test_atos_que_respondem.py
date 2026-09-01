"""Todo ato do candidato deixa uma frase na tela em que ele cai.

Quatro atos mudavam a página em silêncio: reconciliar a participação anterior — o momento mais
aliviante da jornada —, corrigir o nome, adicionar um e-mail e esgotar as tentativas de CPF. Cada um
sozinho é pequeno. Juntos formam a impressão de um sistema que não responde, que é exatamente o que
faz alguém clicar de novo, desconfiar e desistir.

Silêncio depois de uma ação é indistinguível de falha — é a mesma razão do reenvio
(`test_reenvio.py`), aqui aplicada ao resto da área.
"""

import re

import pytest
from django.core import mail
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.application import desafio as servico
from processo_seletivo.identidade.models import CandidateEmail, DesafioDeAcesso
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import MARIA, identificar, registrar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ENTRAR = DesafioDeAcesso.Finalidade.ENTRAR


def aviso(corpo):
    achado = re.search(r'class="aviso" role="status">(.*?)</p>', corpo, re.S)
    return re.sub(r"\s+", " ", achado.group(1)).strip() if achado else ""


def entrar_com(client, endereco):
    client.post(reverse("portal:acesso"), {"email": endereco})
    codigo = re.search(
        r"\b(\d{6})\b", mail.outbox[-1].body
    ).group(1)
    return client.post(reverse("portal:acesso-codigo"), {"codigo": codigo}, follow=True)


@pytest.fixture
def caixa(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    mail.outbox.clear()
    return mail.outbox


@pytest.fixture
def participacao_anterior(selecao):
    """Uma inscrição da `009`: identidade reconciliada, com CPF e sem credencial nenhuma."""
    anterior = registrar(MARIA)
    CandidateEmail.objects.filter(identidade=anterior).delete()
    Inscricao.objects.create(
        identity_subject=anterior.subject,
        edital=selecao,
        profile_id="00000000-0000-0000-0000-000000000401",
        nome=MARIA.nome,
        cpf=MARIA.cpf,
        cpf_normalizado="".join(c for c in MARIA.cpf if c.isdigit()),
        email=MARIA.email,
        created_at=timezone.now(),
    )
    return anterior


def test_vincular_a_participacao_anterior_diz_que_deu_certo(client, caixa, participacao_anterior):
    entrar_com(client, MARIA.email)

    resposta = client.post(
        reverse("portal:acesso-reconciliar"), {"cpf": MARIA.cpf}, follow=True
    )

    assert "sua participação anterior está aqui" in aviso(resposta.content.decode())


def test_esgotar_as_tentativas_de_cpf_explica_o_que_houve(client, caixa, participacao_anterior):
    """O desfecho mais confuso do percurso: a pessoa confirmava o CPF e caía noutra tela, sem
    nenhuma palavra sobre o que tinha acontecido."""
    entrar_com(client, MARIA.email)
    for _ in range(4):
        client.post(reverse("portal:acesso-reconciliar"), {"cpf": "111.444.777-35"})

    resposta = client.post(
        reverse("portal:acesso-reconciliar"), {"cpf": "111.444.777-35"}, follow=True
    )
    dito = aviso(resposta.content.decode())

    assert "Não conseguimos confirmar o CPF" in dito
    assert "tentar vincular a participação anterior de novo" in dito
    assert "Vincular participação anterior" in resposta.content.decode(), "e a oferta está lá"


def test_recusar_o_convite_diz_que_ainda_dá_para_voltar_atrás(client, caixa, participacao_anterior):
    entrar_com(client, MARIA.email)

    resposta = client.post(
        reverse("portal:acesso-reconciliar"), {"acao": "continuar"}, follow=True
    )

    assert "Se mudar de ideia" in aviso(resposta.content.decode())


def test_corrigir_o_nome_confirma(client, caixa):
    entrar_com(client, "novata@exemplo.test")

    resposta = client.post(
        reverse("portal:meus-dados"),
        {"nome": "Rita Pereira Nunes", "cpf": "111.444.777-35"},
        follow=True,
    )

    assert "Seus dados foram guardados" in aviso(resposta.content.decode())


def test_adicionar_e_remover_e_promover_confirmam(client, caixa, candidatos_registrados):
    identificar(client, MARIA)
    client.post(reverse("portal:conta-adicionar"), {"email": "segunda@exemplo.test"})
    codigo = re.search(r"\b(\d{6})\b", mail.outbox[-1].body).group(1)

    adicionou = client.post(reverse("portal:acesso-codigo"), {"codigo": codigo}, follow=True)
    assert "segunda@exemplo.test foi adicionado" in aviso(adicionou.content.decode())

    segunda = CandidateEmail.objects.get(email_canonico="segunda@exemplo.test")
    promoveu = client.post(reverse("portal:conta-principal", args=[segunda.id]), follow=True)
    assert "por este endereço que a instituição vai falar" in aviso(promoveu.content.decode())

    antiga = CandidateEmail.objects.filter(identidade=segunda.identidade).exclude(
        pk=segunda.pk
    ).get()
    removeu = client.post(reverse("portal:conta-remover", args=[antiga.id]), follow=True)
    assert "foi removido" in aviso(removeu.content.decode())


def test_a_recusa_e_a_confirmacao_nao_se_confundem(client, caixa, candidatos_registrados):
    """Uma é `status`, a outra é `alert`: confirmar não interrompe; recusar precisa interromper."""
    identificar(client, MARIA)

    corpo = client.post(
        reverse("portal:conta-adicionar"), {"email": "nao-e-email"}, follow=True
    ).content.decode()

    assert 'class="aviso recusa-em-destaque" role="alert"' in corpo
    assert aviso(corpo) == "", "recusa não vira confirmação"


def test_o_aviso_e_lido_uma_vez_so(client, caixa):
    entrar_com(client, "efemera@exemplo.test")
    client.post(
        reverse("portal:meus-dados"), {"nome": "Rita Pereira", "cpf": "111.444.777-35"}
    )

    primeira = client.get(reverse("portal:inscricoes")).content.decode()
    segunda = client.get(reverse("portal:inscricoes")).content.decode()

    assert aviso(primeira)
    assert aviso(segunda) == "", "recarregar a página não repete a confirmação"


def test_o_desafio_continua_criado_para_quem_nao_existe(client, caixa):
    """Guarda de regressão: nada aqui pode passar a depender de existir identidade."""
    servico.solicitar(email_canonico="ninguem@exemplo.test", finalidade=ENTRAR)

    assert associacao.identidade_da_credencial("ninguem@exemplo.test") is None
    assert DesafioDeAcesso.objects.filter(email_canonico="ninguem@exemplo.test").exists()
