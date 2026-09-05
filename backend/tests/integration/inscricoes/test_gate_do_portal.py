"""A tela de revisão só oferece o envio quando a versão reconhecida já é a vigente (015, FR-059).

**Por que o gate existe.** Os campos exigidos vêm da versão que vai governar o envio. Mostrá-los
antes de a pessoa reconhecer a Retificação faria com que ela preenchesse dados que perderia ao
clicar no formulário separado de reconhecimento — e, pior, veria campos de uma norma enquanto o
congelamento aconteceria sob outra.

O ciclo é: reconhecer → redirect → GET novo, onde reconhecida e vigente coincidem.
"""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, PERFIL_DOCENTE, identificar, pdf
from tests.fixtures.publicacao import retify
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

FATO = "00000000-0000-0000-0000-0000000005b1"


def pronta_pelo_portal(client, selecao):
    identificar(client, MARIA)
    from processo_seletivo.inscricoes.application.rascunho import (
        abrir_inscricao,
        anexar_documento,
        gravar_dados,
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
    return inscricao


def test_edital_sem_fato_declarado_nao_acrescenta_campo(client, selecao, candidatos_registrados):
    """Um Edital que não declara fato nenhum continua sem campo nenhum (FR-061)."""
    inscricao = pronta_pelo_portal(client, selecao)

    pagina = client.get(reverse("portal:revisao", args=[inscricao.id])).content.decode()

    assert "Dados exigidos pelo Edital" not in pagina
    assert 'name="fato-' not in pagina


def test_o_gate_esconde_o_envio_ate_o_reconhecimento(client, api_client, selecao, candidatos_registrados):
    """As três fases do ciclo, na mesma ordem em que a pessoa as vive."""
    inscricao = pronta_pelo_portal(client, selecao)
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
        suffix="fato",
    )

    # 1. Antes de reconhecer: nem campos, nem botão de envio — só a ação de reconhecer.
    antes = client.get(reverse("portal:revisao", args=[inscricao.id])).content.decode()
    assert "O Edital foi atualizado" in antes
    assert 'name="reconhecer_versao"' in antes
    assert 'name="fato-' not in antes
    assert "Dados exigidos pelo Edital" not in antes

    # 2. Reconhecer redireciona para um GET novo, em vez de renderizar na mesma resposta.
    reconhecimento = client.post(
        reverse("portal:revisao", args=[inscricao.id]), {"reconhecer_versao": "1"}
    )
    assert reconhecimento.status_code == 302
    assert reconhecimento["Location"] == reverse("portal:revisao", args=[inscricao.id])

    # 3. No GET seguinte, reconhecida é a vigente: os campos e o envio aparecem.
    depois = client.get(reverse("portal:revisao", args=[inscricao.id])).content.decode()
    assert "Dados exigidos pelo Edital" in depois
    assert f'name="fato-{FATO}"' in depois
    assert "O Edital foi atualizado" not in depois


def test_o_valor_digitado_volta_apos_uma_recusa(client, api_client, selecao, candidatos_registrados):
    """Uma recusa não pode custar o que já estava certo (SC-UX-007)."""
    inscricao = pronta_pelo_portal(client, selecao)
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
        suffix="fato",
    )
    client.post(reverse("portal:revisao", args=[inscricao.id]), {"reconhecer_versao": "1"})

    # Sem as declarações: a recusa acontece, e o que foi digitado precisa voltar.
    recusada = client.post(
        reverse("portal:revisao", args=[inscricao.id]), {f"fato-{FATO}": "1990-05-20"}
    )

    assert Inscricao.objects.get(pk=inscricao.pk).status == Inscricao.Status.RASCUNHO
    assert 'value="1990-05-20"' in recusada.content.decode()
