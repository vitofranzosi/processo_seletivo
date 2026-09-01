"""Quais respostas o navegador pode guardar, e quais não (T110, FR-075, FR-075a).

A distinção é o ponto: marcar tudo como privado seria perder a marcação, porque a vitrine é
conteúdo institucional e deve ser barata de servir. O que não pode ficar no histórico de uma
máquina compartilhada é o que carrega nome, CPF, documento — ou o simples fato de que aquela
pessoa se inscreveu.
"""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, identificar, pdf
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL
from tests.interface.conftest import identificar as identificar_servidor


@pytest.fixture
def enviada(inscricao_de_maria):
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao_de_maria, dados={"modality_id": MODALIDADE_AC}
    )
    for requisito, nome in ((DOCUMENTO_DE_TODOS, "rg.pdf"), (DOCUMENTO_DO_PERFIL, "diploma.pdf")):
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    return enviar_inscricao(
        identidade=MARIA,
        inscricao=inscricao,
        declaracoes={"veracidade": True, "ciencia": True},
        idempotency_key="envio-privacidade",
    )


def _privada(resposta):
    return "no-store" in resposta.headers.get("Cache-Control", "")


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_as_paginas_publicas_continuam_cacheaveis(client, selecao):
    """Sem identidade, a vitrine e o detalhe não falam de ninguém."""
    for endereco in (reverse("portal:vitrine"), reverse("portal:selecao", args=[selecao.id])):
        assert not _privada(client.get(endereco)), endereco


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_toda_tela_do_candidato_com_dado_pessoal_e_privada(client, enviada, selecao):
    identificar(client, MARIA)
    enderecos = (
        reverse("portal:identificar"),
        reverse("portal:inscricao", args=[enviada.id]),
        reverse("portal:revisao", args=[enviada.id]),
        reverse("portal:comprovante", args=[enviada.id]),
        # A seleção deixa de ser genérica quando diz que **esta** pessoa já se inscreveu.
        reverse("portal:selecao", args=[selecao.id]),
    )

    for endereco in enderecos:
        resposta = client.get(endereco, follow=True)
        assert _privada(resposta), endereco


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_arquivo_do_candidato_e_privado(client, enviada):
    identificar(client, MARIA)

    resposta = client.get(
        reverse("portal:documento-do-candidato", args=[enviada.id, DOCUMENTO_DE_TODOS])
    )

    assert _privada(resposta)
    resposta.close()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_as_telas_administrativas_de_inscricao_sao_privadas(client, settings, enviada, selecao):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    identificar_servidor(client, "bruno.gestor", ["gestor"])
    enderecos = (
        reverse("interface:inscricoes", args=[selecao.id]),
        reverse("interface:inscricao-recebida", args=[enviada.id]),
    )

    for endereco in enderecos:
        assert _privada(client.get(endereco)), endereco

    arquivo = client.get(
        reverse("interface:documento-da-inscricao", args=[enviada.id, DOCUMENTO_DE_TODOS])
    )
    assert _privada(arquivo)
    arquivo.close()
