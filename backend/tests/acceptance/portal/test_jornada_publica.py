"""Da vaga ao rascunho sem perder de vista o que se escolheu (072, US2 e US3, SC-603).

**A identidade nova atravessa os formulários.** Nada é gravado direto: o e-mail é pedido, o
código é lido da caixa de saída de teste, "Seus dados" é **postado pelo formulário** com os valores
de teste do repositório, e só então a pessoa volta à vaga. Uma identidade cadastrada por fixture
pularia exatamente a tela que esta feature mudou.

**E a confirmação continua.** A volta da identificação mostra a vaga e explica que falta tocar
"Inscrever-se nesta vaga"; nenhum rascunho existe antes desse POST. É a garantia de que um endereço
compartilhado — `?destino=` colado por terceiro — não cria inscrição em nome de quem só se
identificou (009; a volta à vaga sem abrir rascunho, da 062).
"""

import re

import pytest
from django.core import mail
from django.urls import reverse

from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import CPF_JOAO, MARIA, PERFIL_DOCENTE, identificar, registrar

pytestmark = [pytest.mark.django_db, pytest.mark.acceptance]

NOVA = "visitante.nova@exemplo.test"


@pytest.fixture
def canal(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    mail.outbox.clear()
    return mail.outbox


def codigo(caixa):
    return re.search(r"\b(\d{6})\b", caixa[-1].body).group(1)


def main(resposta):
    corpo = resposta.content.decode()
    return re.search(r"<main[^>]*>(.*)</main>", corpo, re.S).group(1)


def texto(html):
    return " ".join(re.sub(r"<[^>]+>", " ", html).split())


def cartao_da_vaga(html, perfil=PERFIL_DOCENTE):
    """Do `<li class="perfil">` da vaga até o próximo — o cartão tem listas dentro."""
    (cartao,) = [
        trecho
        for trecho in html.split('<li class="perfil"')
        if trecho.startswith(f' id="vaga-{perfil}"')
    ]
    return cartao


def inscrever(client, selecao, perfil=PERFIL_DOCENTE, **extra):
    return client.post(reverse("portal:inscrever", args=[selecao.id, perfil]), **extra)


def test_identidade_nova_vai_da_vaga_ao_rascunho_pelos_formularios(client, selecao, canal):
    # 1. Na página da vaga, sem sessão, toca "Inscrever-se nesta vaga".
    resposta = inscrever(client, selecao, follow=True)
    assert "Confirme seu e-mail para se inscrever" in texto(main(resposta))

    # 2. Informa o e-mail; 3. digita o código que chegou.
    client.post(reverse("portal:acesso"), {"email": NOVA})
    resposta = client.post(reverse("portal:acesso-codigo"), {"codigo": codigo(canal)}, follow=True)
    assert resposta.redirect_chain[-1][0] == reverse("portal:meus-dados")
    assert "Professor de Informática" in texto(main(resposta))

    # 4. "Seus dados", pelo formulário — nome e CPF de teste do repositório.
    resposta = client.post(
        reverse("portal:meus-dados"), {"nome": "Ana Visitante", "cpf": CPF_JOAO}, follow=True
    )
    destino, _ = resposta.redirect_chain[-1]
    assert destino == f"{reverse('portal:selecao', args=[selecao.id])}#vaga-{PERFIL_DOCENTE}"
    identidade = CandidateIdentity.objects.get(nome="Ana Visitante")
    assert identidade.cpf_normalizado == "98765432100"

    # 5. A volta: a vaga escolhida, com a mensagem que explica a confirmação — e nenhum rascunho.
    vaga = cartao_da_vaga(main(resposta))
    mensagem = re.search(r'<p class="volta-da-identificacao" role="status">(.*?)</p>', vaga, re.S)
    assert mensagem, "a mensagem de volta mora no cartão da vaga escolhida"
    assert NOVA in texto(mensagem.group(1))
    assert "Inscrever-se nesta vaga" in texto(mensagem.group(1))
    assert "Seus dados foram guardados" in texto(mensagem.group(1)), "FR-1625: aqui, e não depois"
    assert "no-store" in resposta.headers.get("Cache-Control", ""), "a página leva o e-mail dela"
    assert not Inscricao.objects.exists(), "nenhum rascunho antes da confirmação"

    # 6. Confirma: o rascunho daquela vaga é aberto.
    resposta = inscrever(client, selecao, follow=True)
    inscricao = Inscricao.objects.get()
    assert str(inscricao.profile_id) == PERFIL_DOCENTE
    assert resposta.redirect_chain[-1][0] == reverse("portal:inscricao", args=[inscricao.id])
    assert "Seus dados foram guardados" not in texto(main(resposta)), "o aviso não sobra"


def test_a_mensagem_de_volta_aparece_uma_vez(client, selecao, canal):
    registrar(MARIA)
    inscrever(client, selecao, follow=True)
    client.post(reverse("portal:acesso"), {"email": MARIA.email})
    client.post(reverse("portal:acesso-codigo"), {"codigo": codigo(canal)})

    pagina = reverse("portal:selecao", args=[selecao.id])
    primeira = client.get(pagina).content.decode()
    segunda = client.get(pagina).content.decode()

    assert 'class="volta-da-identificacao"' in primeira
    assert 'class="volta-da-identificacao"' not in segunda


def test_destino_colado_por_terceiro_nao_abre_inscricao(client, selecao, canal):
    """O endereço com `?destino=` de uma vaga leva à vaga — e só a confirmação abre rascunho."""
    destino = reverse("portal:inscrever", args=[selecao.id, PERFIL_DOCENTE])
    registrar(MARIA)

    client.get(reverse("portal:acesso"), {"destino": destino})
    client.post(reverse("portal:acesso"), {"email": MARIA.email})
    resposta = client.post(reverse("portal:acesso-codigo"), {"codigo": codigo(canal)}, follow=True)

    assert resposta.status_code == 200
    assert not Inscricao.objects.exists()


def test_vaga_que_deixou_de_receber_inscricao_nao_e_convidada_na_volta(
    client, selecao, canal, api_client
):
    """FR-1623 — se o período fechou entre o clique e a volta, a mensagem não promete abrir nada."""
    from datetime import timedelta

    from django.utils import timezone

    from tests.fixtures.publicacao import encerrar_inscricoes

    registrar(MARIA)
    inscrever(client, selecao, follow=True)
    client.post(reverse("portal:acesso"), {"email": MARIA.email})
    encerrar_inscricoes(api_client, selecao, timezone.now() - timedelta(minutes=1), suffix="072")
    resposta = client.post(reverse("portal:acesso-codigo"), {"codigo": codigo(canal)}, follow=True)

    pagina = texto(main(resposta))
    assert "abrir sua inscrição" not in pagina
    assert not Inscricao.objects.exists()


# --- Quem já tem identidade (US3) ---


def test_identidade_com_nome_e_cpf_volta_a_vaga_sem_passar_por_seus_dados(client, selecao, canal):
    registrar(MARIA)
    inscrever(client, selecao, follow=True)
    client.post(reverse("portal:acesso"), {"email": MARIA.email})
    resposta = client.post(reverse("portal:acesso-codigo"), {"codigo": codigo(canal)}, follow=True)

    caminho = [endereco for endereco, _ in resposta.redirect_chain]
    assert reverse("portal:meus-dados") not in caminho
    vaga = cartao_da_vaga(main(resposta))
    assert 'class="volta-da-identificacao"' in vaga
    assert "Seus dados foram guardados" not in vaga, "nada foi guardado agora"


def test_com_sessao_aberta_o_botao_abre_o_rascunho_direto(client, selecao):
    identificar(client, MARIA)

    resposta = inscrever(client, selecao, follow=True)

    inscricao = Inscricao.objects.get()
    assert resposta.redirect_chain == [(reverse("portal:inscricao", args=[inscricao.id]), 302)]
    assert 'class="volta-da-identificacao"' not in resposta.content.decode()


def test_com_rascunho_aberto_o_convite_e_continuar_inscricao(client, selecao):
    identificar(client, MARIA)
    inscrever(client, selecao)

    pagina = client.get(reverse("portal:selecao", args=[selecao.id])).content.decode()

    assert "Continuar inscrição" in cartao_da_vaga(pagina)
