"""A revisão mostra a data do cadastro e leva até onde informá-la (180, FR-8303).

Quem chega à revisão sem data lê "Falta informar", vai a "Seus dados" e volta para a revisão; o
envio pela tela é recusado com a frase do comando, e passa depois que a data é informada.
"""

from datetime import date

import pytest
from django.urls import reverse

from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, identificar, pdf
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def pronta(inscricao_de_maria):
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao_de_maria, dados={"modality_id": MODALIDADE_AC}
    )
    for requisito, nome in ((DOCUMENTO_DE_TODOS, "rg.pdf"), (DOCUMENTO_DO_PERFIL, "diploma.pdf")):
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
        )
    inscricao.refresh_from_db()
    return inscricao


def _sem_data():
    CandidateIdentity.objects.filter(subject=MARIA.subject).update(data_nascimento=None)


def _enviar_pela_tela(client, inscricao):
    inscricao.refresh_from_db()
    return client.post(
        reverse("portal:revisao", args=[inscricao.id]),
        {"veracidade": "on", "ciencia": "on"},
    )


def test_a_revisao_mostra_a_data_do_cadastro(client, pronta):
    identificar(client, MARIA)
    corpo = client.get(reverse("portal:revisao", args=[pronta.id])).content.decode()

    assert "Data de nascimento" in corpo
    assert MARIA.data_nascimento.strftime("%d/%m/%Y") in corpo


def test_sem_data_a_revisao_diz_que_falta_e_leva_a_seus_dados(client, pronta):
    _sem_data()
    identificar(client, MARIA)
    revisao = reverse("portal:revisao", args=[pronta.id])

    corpo = client.get(revisao).content.decode()

    assert "Falta" in corpo
    assert f"{reverse('portal:meus-dados')}?destino={revisao}" in corpo


def test_o_envio_pela_tela_sem_data_e_recusado_com_a_frase(client, pronta):
    _sem_data()
    identificar(client, MARIA)

    resposta = _enviar_pela_tela(client, pronta)

    assert resposta.status_code == 200
    assert "Falta informar sua data de nascimento em Seus dados." in resposta.content.decode()
    pronta.refresh_from_db()
    assert pronta.status == Inscricao.Status.RASCUNHO


def test_informar_em_seus_dados_volta_a_revisao_e_o_envio_passa(client, pronta):
    _sem_data()
    identificar(client, MARIA)
    revisao = reverse("portal:revisao", args=[pronta.id])

    client.get(f"{reverse('portal:meus-dados')}?destino={revisao}")
    resposta = client.post(
        reverse("portal:meus-dados"),
        {"nome": MARIA.nome, "cpf": MARIA.cpf, "data_nascimento": "07/03/1998"},
    )

    assert resposta["Location"] == revisao
    _enviar_pela_tela(client, pronta)
    pronta.refresh_from_db()
    assert pronta.status == Inscricao.Status.SUBMETIDA
    assert pronta.data_nascimento == date(1998, 3, 7)


def test_destino_que_nao_e_a_revisao_nao_e_guardado(client, pronta):
    """A lista fechada de destinos continua a de `_de_volta_a_vaga`."""
    _sem_data()
    identificar(client, MARIA)

    client.get(f"{reverse('portal:meus-dados')}?destino=https://exemplo.test/fora")
    resposta = client.post(
        reverse("portal:meus-dados"),
        {"nome": MARIA.nome, "cpf": MARIA.cpf, "data_nascimento": "07/03/1998"},
    )

    assert resposta["Location"] == reverse("portal:inscricoes")


def test_a_volta_a_revisao_nao_sobrevive_a_outra_visita(client, pronta):
    """Quem desistiu e volta depois a "Seus dados" por outro caminho não é levado à revisão."""
    _sem_data()
    identificar(client, MARIA)
    revisao = reverse("portal:revisao", args=[pronta.id])

    client.get(f"{reverse('portal:meus-dados')}?destino={revisao}")
    client.get(reverse("portal:meus-dados"))
    resposta = client.post(
        reverse("portal:meus-dados"),
        {"nome": MARIA.nome, "cpf": MARIA.cpf, "data_nascimento": "07/03/1998"},
    )

    assert resposta["Location"] == reverse("portal:inscricoes")
