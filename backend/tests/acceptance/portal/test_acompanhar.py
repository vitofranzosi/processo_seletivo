"""Entrega 5 — Maria acompanha, e distingue o que é dela do que é do processo.

O percurso da spec: ela abre a inscrição enviada pela lista, lê os dois blocos, e — depois de uma
Retificação — vê o aviso sem que nada da inscrição dela tenha mudado.
"""

import re

import pytest
from django.core import mail
from django.urls import reverse

from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, pdf, registrar
from tests.fixtures.edital import caminho_perfil
from tests.fixtures.publicacao import retify
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.acceptance]

VAGAS = caminho_perfil("immediateVacancies")


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
    for requisito, nome in ((DOCUMENTO_DE_TODOS, "rg.pdf"), (DOCUMENTO_DO_PERFIL, "d.pdf")):
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    return enviar_inscricao(
        identidade=MARIA,
        inscricao=inscricao,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key="envio-aceitacao-5",
    )


def test_percurso_da_entrega_5(client, canal, enviada, selecao, api_client):
    # 1. Entra pelo acesso sem senha.
    registrar(MARIA)
    client.post(reverse("portal:acesso"), {"email": MARIA.email})
    codigo = re.search(r"\b(\d{6})\b", canal[-1].body).group(1)
    client.post(reverse("portal:acesso-codigo"), {"codigo": codigo})

    # 2. A ação principal da inscrição enviada leva ao acompanhamento.
    lista = client.get(reverse("portal:inscricoes")).content.decode()
    assert reverse("portal:acompanhamento", args=[enviada.id]) in lista

    # 3. Os dois blocos, distintos.
    corpo = client.get(reverse("portal:acompanhamento", args=[enviada.id])).content.decode()
    assert "Sua participação" in corpo and "Inscrição enviada" in corpo
    assert "Cronograma do processo" in corpo and "Período de inscrições" in corpo
    assert "foi atualizado após sua inscrição" not in corpo

    # 4. O Edital é retificado. O aviso aparece; a inscrição não muda.
    antes = Inscricao.objects.values().get(pk=enviada.pk)
    retify(api_client, selecao, [{"targetPath": VAGAS, "operation": "REPLACE", "newValue": 9}])

    corpo = client.get(reverse("portal:acompanhamento", args=[enviada.id])).content.decode()
    assert "Este Edital foi atualizado após sua inscrição" in corpo
    assert Inscricao.objects.values().get(pk=enviada.pk) == antes

    # 5. E a conferência continua a um clique, lendo a versão que ela aceitou.
    assert reverse("portal:inscricao", args=[enviada.id]) in corpo
