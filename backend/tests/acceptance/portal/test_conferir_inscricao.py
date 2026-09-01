"""Entrega 4 — Maria abre o que enviou e confere, sem redigitar e sem reenviar nada.

É o percurso da demonstração emblemática da spec: ela vê os documentos com nome de arquivo,
tamanho e instante, abre cada um, e leva o comprovante.
"""

import re

import pytest
from django.core import mail
from django.urls import reverse

from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, pdf, registrar
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.acceptance]


@pytest.fixture
def canal(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "nao-responda@exemplo.test"
    mail.outbox.clear()
    return mail.outbox


@pytest.fixture
def enviada(inscricao_de_maria):
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao_de_maria, dados={"modality_id": MODALIDADE_AC}
    )
    for requisito, nome in (
        (DOCUMENTO_DE_TODOS, "rg.pdf"),
        (DOCUMENTO_DO_PERFIL, "diploma.pdf"),
    ):
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    return enviar_inscricao(
        identidade=MARIA,
        inscricao=inscricao,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key="envio-aceitacao-4",
    )


def test_percurso_da_entrega_4(client, canal, enviada):
    # 1. Maria entra pelo acesso sem senha, com a credencial que já é dela.
    registrar(MARIA)
    client.post(reverse("portal:acesso"), {"email": MARIA.email})
    codigo = re.search(r"\b(\d{6})\b", canal[-1].body).group(1)
    client.post(reverse("portal:acesso-codigo"), {"codigo": codigo})

    # 2. A lista traz a inscrição enviada, com o protocolo e a ação de acompanhar.
    lista = client.get(reverse("portal:inscricoes")).content.decode()
    assert enviada.protocolo in lista
    assert "Acompanhar" in lista

    # 3. Ela abre e confere o que o sistema recebeu.
    corpo = client.get(reverse("portal:inscricao", args=[enviada.id])).content.decode()
    assert "✓ Inscrição enviada" in corpo
    assert enviada.protocolo in corpo
    assert "rg.pdf" in corpo and "diploma.pdf" in corpo
    assert "Visualizar" in corpo and "Baixar" in corpo

    # 4. Abre um documento e leva o comprovante — nada foi reenviado.
    documento = client.get(
        reverse("portal:documento-do-candidato", args=[enviada.id, DOCUMENTO_DE_TODOS])
    )
    assert b"".join(documento.streaming_content).startswith(b"%PDF")
    documento.close()
    assert client.get(reverse("portal:comprovante-pdf", args=[enviada.id])).status_code == 200
