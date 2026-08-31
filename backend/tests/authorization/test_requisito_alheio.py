"""Envio forjado para requisito que não é da inscrição (US4 da 009, FR-044).

A tela nunca oferece um requisito inaplicável. Isto é o que responde ao POST montado à mão — e é
onde a regra vale, porque a tela não é fronteira de segurança.
"""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.application.rascunho import abrir_inscricao
from processo_seletivo.inscricoes.models import DocumentoSubmetido
from tests.fixtures.candidato import (
    MARIA,
    PERFIL_TECNICO,
    identificar,
    pdf,
)
from tests.fixtures.selecao import DOCUMENTO_DA_MODALIDADE, DOCUMENTO_DO_PERFIL


def _enviar(client, inscricao, requisito):
    return client.post(
        reverse("portal:enviar-documento", args=[inscricao.id, requisito]), {"arquivo": pdf()}
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.authorization
def test_requisito_de_outro_perfil_e_recusado(client, selecao):
    """O diploma é exigido do Perfil docente; quem se inscreveu no técnico não o envia."""
    inscricao = abrir_inscricao(identidade=MARIA, edital_id=selecao.id, profile_id=PERFIL_TECNICO)
    identificar(client, MARIA)

    resposta = _enviar(client, inscricao, DOCUMENTO_DO_PERFIL)

    assert resposta.status_code == 404
    assert DocumentoSubmetido.objects.count() == 0


@pytest.mark.django_db(transaction=True)
@pytest.mark.authorization
def test_requisito_de_modalidade_nao_escolhida_e_recusado(client, inscricao_de_maria):
    identificar(client, MARIA)

    resposta = _enviar(client, inscricao_de_maria, DOCUMENTO_DA_MODALIDADE)

    assert resposta.status_code == 404
    assert DocumentoSubmetido.objects.count() == 0


@pytest.mark.django_db(transaction=True)
@pytest.mark.authorization
def test_requisito_inexistente_e_recusado(client, inscricao_de_maria):
    identificar(client, MARIA)

    resposta = _enviar(client, inscricao_de_maria, "00000000-0000-0000-0000-0000000009fc")

    assert resposta.status_code == 404
    assert DocumentoSubmetido.objects.count() == 0
