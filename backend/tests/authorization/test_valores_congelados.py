"""Os fatos congelados são dado pessoal, e o acesso a eles é restrito (015, FR-053).

O valor que uma pessoa informou — data de nascimento, tempo de experiência — não é público nem
compartilhado entre candidatos. A recusa é 404 uniforme, como em toda a família: dizer "existe, mas
você não pode" já entrega informação.
"""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.application.rascunho import (
    abrir_inscricao,
    anexar_documento,
    gravar_dados,
)
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.models import ValorDeFato
from tests.fixtures.candidato import (
    JOAO,
    MARIA,
    MODALIDADE_AC,
    PERFIL_DOCENTE,
    identificar,
    pdf,
)
from tests.fixtures.publicacao import retify
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

pytestmark = [pytest.mark.authorization, pytest.mark.django_db(transaction=True)]

FATO = "00000000-0000-0000-0000-0000000005c1"
DECLARACOES = {"veracidade": True, "ciencia": True}


@pytest.fixture
def inscricao_enviada_de_maria(api_client, selecao, candidatos_registrados):
    retify(
        api_client,
        selecao,
        [
            {
                "targetPath": f"/profiles/id={PERFIL_DOCENTE}/declaredFacts/-",
                "operation": "ADD",
                "newValue": {
                    "id": FATO,
                    "code": "NASCIMENTO",
                    "label": "Data de nascimento",
                    "type": "DATA",
                },
            }
        ],
        suffix="fato-auth",
    )
    inscricao = abrir_inscricao(identidade=MARIA, edital_id=selecao.id, profile_id=PERFIL_DOCENTE)
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao, dados={"modality_id": MODALIDADE_AC}
    )
    for requisito, nome in ((DOCUMENTO_DE_TODOS, "rg.pdf"), (DOCUMENTO_DO_PERFIL, "dip.pdf")):
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    return enviar_inscricao(
        identidade=MARIA,
        inscricao=inscricao,
        declaracoes=DECLARACOES,
        idempotency_key="envio-auth",
        fatos={FATO: "1990-05-20"},
    )


def test_o_valor_congelado_existe_e_pertence_a_quem_o_informou(inscricao_enviada_de_maria):
    """A contraprova: sem ela, as recusas abaixo poderiam ser sobre um valor que nunca existiu."""
    valor = ValorDeFato.objects.get(inscricao=inscricao_enviada_de_maria)

    assert valor.valor_data.isoformat() == "1990-05-20"
    assert valor.inscricao.identity_subject == MARIA.subject


def test_outro_candidato_nao_alcanca_a_inscricao_alheia(client, inscricao_enviada_de_maria):
    """404 uniforme: dizer que existe já entregaria informação."""
    identificar(client, JOAO)

    resposta = client.get(
        reverse("portal:comprovante", args=[inscricao_enviada_de_maria.id])
    )

    assert resposta.status_code == 404
    assert "1990-05-20" not in resposta.content.decode()


def test_quem_nao_se_identificou_nao_alcanca_nada(client, inscricao_enviada_de_maria):
    resposta = client.get(reverse("portal:comprovante", args=[inscricao_enviada_de_maria.id]))

    assert resposta.status_code in (302, 404)
    if resposta.status_code == 302:
        assert "1990-05-20" not in str(resposta.get("Location", ""))
