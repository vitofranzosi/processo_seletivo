"""Entrega 3 — nome e CPF uma vez, a lista, e o rascunho retomado de onde parou.

O percurso é o de quem chega novo: entra pela vaga, informa o núcleo mínimo uma única vez, e nas
inscrições seguintes não é perguntado de novo. É a promessa da `UX-005` exercida ponta a ponta.
"""

import re

import pytest
from django.core import mail
from django.urls import reverse

from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import PERFIL_DOCENTE, PERFIL_TECNICO

pytestmark = [pytest.mark.django_db, pytest.mark.acceptance]

ENDERECO = "candidata.nova@exemplo.test"
CPF = "123.456.789-09"


@pytest.fixture
def canal(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    mail.outbox.clear()
    return mail.outbox


def entrar(client, canal, destino=""):
    endereco = reverse("portal:acesso")
    client.post(f"{endereco}?destino={destino}" if destino else endereco, {"email": ENDERECO})
    codigo = re.search(r"\b(\d{6})\b", canal[-1].body).group(1)
    return client.post(reverse("portal:acesso-codigo"), {"codigo": codigo})


def test_percurso_da_entrega_3(client, canal, selecao):
    vaga = reverse("portal:inscrever", args=[selecao.id, PERFIL_DOCENTE])

    # 1. Entra a caminho da vaga e informa nome e CPF uma única vez.
    assert entrar(client, canal, destino=vaga)["Location"] == reverse("portal:meus-dados")
    dados = client.post(reverse("portal:meus-dados"), {"nome": "Maria Silva", "cpf": CPF})
    assert "Continuar inscrição" in dados.content.decode()

    # 2. Abre a inscrição, e ela já vem com o que a identidade sabe.
    client.post(vaga)
    inscricao = Inscricao.objects.get()
    assert inscricao.nome == "Maria Silva"
    assert inscricao.email == ENDERECO

    # 3. Numa segunda vaga, nada é perguntado de novo.
    outra = reverse("portal:inscrever", args=[selecao.id, PERFIL_TECNICO])
    assert reverse("portal:meus-dados") not in client.post(outra)["Location"]

    # 4. A lista mostra as duas, com a ação principal de cada uma.
    corpo = client.get(reverse("portal:inscricoes")).content.decode()
    assert corpo.count("Continuar inscrição") == 2
    assert "Você ainda não possui inscrições" not in corpo


def test_continuar_retoma_o_que_ficou(client, canal, selecao):
    vaga = reverse("portal:inscrever", args=[selecao.id, PERFIL_DOCENTE])
    entrar(client, canal, destino=vaga)
    client.post(reverse("portal:meus-dados"), {"nome": "Maria Silva", "cpf": CPF})
    client.post(vaga)
    inscricao = Inscricao.objects.get()
    client.post(reverse("portal:inscricao", args=[inscricao.id]), {"telefone": "(27) 99999-0000"})

    # Sai, entra de novo, e continua de onde parou.
    client.post(reverse("portal:sair"))
    from processo_seletivo.identidade.models import DesafioDeAcesso

    DesafioDeAcesso.objects.all().delete()
    entrar(client, canal)

    corpo = client.get(reverse("portal:inscricao", args=[inscricao.id])).content.decode()
    assert "99999-0000" in corpo, "o que ela deixou continua lá"


def test_a_identificacao_por_declaracao_nao_existe_mais(client):
    """A tela que deixava qualquer pessoa dizer quem era saiu com a `010` (FR-048)."""
    from django.urls import NoReverseMatch

    with pytest.raises(NoReverseMatch):
        reverse("portal:identificar")
    assert client.get("/selecoes/identificar").status_code == 404
