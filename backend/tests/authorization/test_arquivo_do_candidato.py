"""O arquivo do candidato só chega a quem tem direito a ele (US4 da 009, FR-051, FR-071).

Nada serve o diretório dos documentos. Chegar a um arquivo significa passar pela aplicação, e a
primeira coisa que ela faz é perguntar de quem é — conhecer o identificador não autoriza.
"""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.models import DocumentoSubmetido
from tests.fixtures.candidato import (
    JOAO,
    MARIA,
    identificar,
    pdf,
)
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL


@pytest.fixture
def documento_de_maria(client, inscricao_de_maria):
    identificar(client, MARIA)
    client.post(
        reverse("portal:enviar-documento", args=[inscricao_de_maria.id, DOCUMENTO_DE_TODOS]),
        {"arquivo": pdf("rg.pdf")},
    )
    return DocumentoSubmetido.objects.get()


@pytest.mark.django_db(transaction=True)
@pytest.mark.authorization
def test_a_titular_ve_o_que_enviou(client, inscricao_de_maria, documento_de_maria):
    identificar(client, MARIA)

    resposta = client.get(
        reverse("portal:documento-do-candidato", args=[inscricao_de_maria.id, DOCUMENTO_DE_TODOS])
    )

    assert resposta.status_code == 200
    assert resposta.headers["Content-Type"] == "application/pdf"
    assert "inline" in resposta.headers["Content-Disposition"]
    assert "no-store" in resposta.headers["Cache-Control"]
    # O servidor fecha o arquivo ao terminar de servir; o cliente de teste não chega a servir.
    resposta.close()


@pytest.mark.django_db(transaction=True)
@pytest.mark.authorization
def test_outro_candidato_nao_alcanca_o_arquivo(client, inscricao_de_maria, documento_de_maria):
    identificar(client, JOAO)

    resposta = client.get(
        reverse("portal:documento-do-candidato", args=[inscricao_de_maria.id, DOCUMENTO_DE_TODOS])
    )

    assert resposta.status_code == 404
    assert b"%PDF" not in resposta.content


@pytest.mark.django_db(transaction=True)
@pytest.mark.authorization
def test_sem_identidade_o_arquivo_nao_e_entregue(client, inscricao_de_maria, documento_de_maria):
    client.logout()
    sessao = client.session
    sessao.pop("portal_identidade", None)
    sessao.save()

    resposta = client.get(
        reverse("portal:documento-do-candidato", args=[inscricao_de_maria.id, DOCUMENTO_DE_TODOS])
    )

    assert resposta.status_code == 404


@pytest.mark.django_db(transaction=True)
@pytest.mark.authorization
def test_requisito_sem_arquivo_recusa_como_inexistente(client, inscricao_de_maria):
    identificar(client, MARIA)

    resposta = client.get(
        reverse("portal:documento-do-candidato", args=[inscricao_de_maria.id, DOCUMENTO_DO_PERFIL])
    )

    assert resposta.status_code == 404


@pytest.mark.django_db(transaction=True)
@pytest.mark.authorization
def test_o_arquivo_nao_tem_endereco_publico(documento_de_maria):
    """FR-051: pedir a URL levanta erro em vez de devolver um endereço — não há endereço."""
    with pytest.raises(ValueError):
        _ = documento_de_maria.arquivo.url
