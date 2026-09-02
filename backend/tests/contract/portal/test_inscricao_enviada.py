"""A página da inscrição enviada, conforme `contracts/area.md`."""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, identificar, pdf
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.contract]


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
        idempotency_key="envio-contrato",
    )


def test_a_pagina_da_enviada_responde_200(client, enviada):
    identificar(client, MARIA)
    assert client.get(reverse("portal:inscricao", args=[enviada.id])).status_code == 200


def test_o_rascunho_continua_abrindo_a_jornada_existente(client, inscricao_de_maria):
    identificar(client, MARIA)
    corpo = client.get(reverse("portal:inscricao", args=[inscricao_de_maria.id])).content.decode()
    assert 'name="telefone"' in corpo, "rascunho ainda se preenche"


def test_a_pagina_da_enviada_nao_e_armazenavel_pelo_navegador(client, enviada):
    """Dado pessoal na tela não fica no cache de um computador compartilhado."""
    identificar(client, MARIA)
    resposta = client.get(reverse("portal:inscricao", args=[enviada.id]))
    assert "no-store" in resposta["Cache-Control"]


def test_o_documento_responde_200_para_o_titular(client, enviada):
    identificar(client, MARIA)
    resposta = client.get(
        reverse("portal:documento-do-candidato", args=[enviada.id, DOCUMENTO_DE_TODOS])
    )
    assert resposta.status_code == 200
    b"".join(resposta.streaming_content)
    resposta.close()


def test_requisito_sem_documento_responde_404(client, enviada):
    identificar(client, MARIA)
    inexistente = "00000000-0000-0000-0000-0000000009ff"
    resposta = client.get(reverse("portal:documento-do-candidato", args=[enviada.id, inexistente]))
    assert resposta.status_code == 404
