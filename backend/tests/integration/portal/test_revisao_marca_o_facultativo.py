"""A Revisão marca o documento facultativo, como a tela anterior já marcava.

Na conferência de 25/09/2026, a autodeclaração facultativa que o candidato não mandou saía na
Revisão como "Ainda não enviado.", na mesma grafia de alerta do obrigatório que falta
(doc/conferencia-envio-e-analise-documental.md).
"""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.inscricoes.application.rascunho import (
    abrir_inscricao,
    anexar_documento,
    gravar_dados,
)
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, PERFIL_DOCENTE, identificar, pdf
from tests.fixtures.edital import identificador
from tests.fixtures.selecao import (
    DOCUMENTO_DE_TODOS,
    publicar_selecao,
    rascunho_aberto_com_documentos,
)

FACULTATIVO = identificador(411, 0)


@pytest.fixture
def com_facultativo(raiz_de_arquivos, api_client, manager_headers, process_payload):
    rascunho = rascunho_aberto_com_documentos(timezone.now() - timedelta(seconds=1))
    rascunho["documentRequirements"].append(
        {
            "id": FACULTATIVO,
            "key": "autodeclaracao-deficiencia",
            "name": "Autodeclaração de deficiência",
            "instructions": "Apenas para quem concorre na modalidade PcD.",
            "required": False,
            "order": 4,
        }
    )
    return publicar_selecao(api_client, manager_headers, process_payload, rascunho=rascunho)


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_facultativo_nao_enviado_nao_se_le_como_falta(
    client, com_facultativo, candidatos_registrados
):
    inscricao = abrir_inscricao(
        identidade=MARIA, edital_id=com_facultativo.id, profile_id=PERFIL_DOCENTE
    )
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao, dados={"modality_id": MODALIDADE_AC}
    )
    anexar_documento(
        identidade=MARIA, inscricao=inscricao, requirement_id=DOCUMENTO_DE_TODOS, arquivo=pdf()
    )
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:revisao", args=[inscricao.id])).content.decode()
    facultativo = corpo[corpo.index("Autodeclaração de deficiência") :][:300]
    diploma = corpo[corpo.index("Diploma de graduação") :][:300]

    assert "(facultativo)" in facultativo
    assert "Não enviado." in facultativo
    assert "Ainda não enviado." not in facultativo
    # O obrigatório que falta continua dito como falta.
    assert "Ainda não enviado." in diploma
