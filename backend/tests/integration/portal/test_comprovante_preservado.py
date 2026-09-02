"""O comprovante e as evidências de integridade da `009` continuam exatamente como estavam.

A `010` não produz comprovante nenhum: ela oferece o que já existia, a um clique da conferência
(FR-074). Um segundo comprovante seria um segundo documento a explicar — e dois documentos que
provam o mesmo ato acabam divergindo.
"""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.domain.autenticidade import codigo_de_verificacao
from processo_seletivo.inscricoes.models import DocumentoSubmetido
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, identificar, pdf
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


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
        idempotency_key="envio-preservado",
    )


def test_o_comprovante_continua_disponivel(client, enviada):
    identificar(client, MARIA)
    assert client.get(reverse("portal:comprovante", args=[enviada.id])).status_code == 200


def test_o_pdf_continua_deterministico(client, enviada):
    """Bytes determinísticos são o que permite publicar o resumo do próprio documento."""
    identificar(client, MARIA)
    endereco = reverse("portal:comprovante-pdf", args=[enviada.id])

    primeiro = client.get(endereco)
    segundo = client.get(endereco)

    assert primeiro.content == segundo.content
    assert primeiro.content.startswith(b"%PDF")


def test_o_codigo_de_verificacao_e_o_mesmo_na_conferencia_e_no_comprovante(client, enviada):
    identificar(client, MARIA)
    enviados = DocumentoSubmetido.objects.filter(inscricao=enviada)
    esperado = codigo_de_verificacao(enviada, enviados)

    conferencia = client.get(reverse("portal:inscricao", args=[enviada.id])).content.decode()
    comprovante = client.get(reverse("portal:comprovante", args=[enviada.id])).content.decode()

    assert esperado in conferencia, "a conferência mostra o mesmo código"
    assert esperado in comprovante


def test_os_resumos_dos_anexos_permanecem(client, enviada):
    identificar(client, MARIA)
    corpo = client.get(reverse("portal:inscricao", args=[enviada.id])).content.decode()

    for documento in DocumentoSubmetido.objects.filter(inscricao=enviada):
        assert len(documento.content_hash) == 64, "SHA-256 continua sendo gravado"
        assert documento.content_hash in corpo


def test_a_conferencia_nao_gera_segundo_comprovante(client, enviada):
    """Ela **oferece** o que já existe; a rota do comprovante continua sendo uma só (FR-074)."""
    identificar(client, MARIA)
    corpo = client.get(reverse("portal:inscricao", args=[enviada.id])).content.decode()

    assert corpo.count(reverse("portal:comprovante", args=[enviada.id])) == 1
