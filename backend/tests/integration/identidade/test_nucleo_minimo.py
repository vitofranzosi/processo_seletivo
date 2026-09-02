"""Nome e CPF: pedidos uma vez, reusados sempre, e nunca a quem veio da `009`.

A `009` os coletava a cada identificação, porque a identidade era efêmera. Com ela persistida, pedir
de novo seria cobrar duas vezes o mesmo — e é o tipo de atrito que esta feature existe para tirar.
"""

import uuid

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.identidade.application import associacao
from processo_seletivo.identidade.application import credenciais as nucleo
from processo_seletivo.identidade.models import CandidateIdentity, novo_subject
from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import PERFIL_DOCENTE, PERFIL_TECNICO

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

CPF = "123.456.789-09"


@pytest.fixture
def nova(client):
    identidade = associacao.criar_identidade_com("nova@exemplo.test", "nova@exemplo.test")
    sessao = client.session
    sessao["portal_identidade"] = str(identidade.pk)
    sessao.save()
    return identidade


def test_a_identidade_nova_nao_tem_nucleo(nova):
    assert nucleo.falta_o_nucleo(nova)


def test_a_vaga_leva_ao_formulario_quando_falta_o_nucleo(client, nova, selecao):
    vaga = reverse("portal:inscrever", args=[selecao.id, PERFIL_DOCENTE])
    resposta = client.post(vaga)
    assert resposta["Location"] == reverse("portal:meus-dados")


def test_informados_uma_vez_nao_sao_pedidos_de_novo(client, nova, selecao):
    vaga = reverse("portal:inscrever", args=[selecao.id, PERFIL_DOCENTE])
    client.post(vaga)
    client.post(reverse("portal:meus-dados"), {"nome": "Maria Silva", "cpf": CPF})
    client.post(vaga)

    outra = reverse("portal:inscrever", args=[selecao.id, PERFIL_TECNICO])
    resposta = client.post(outra)

    assert reverse("portal:meus-dados") not in resposta["Location"]
    assert Inscricao.objects.count() == 2


def test_o_rascunho_recebe_o_nucleo_da_identidade(client, nova, selecao):
    client.post(reverse("portal:meus-dados"), {"nome": "Maria Silva", "cpf": CPF})
    client.post(reverse("portal:inscrever", args=[selecao.id, PERFIL_DOCENTE]))

    inscricao = Inscricao.objects.get()
    assert inscricao.nome == "Maria Silva"
    assert inscricao.cpf_normalizado == "12345678909"


def test_quem_veio_da_009_nunca_ve_o_formulario(client, selecao):
    """A reconciliação já trouxe nome e CPF: pedi-los seria pedir o que o sistema já sabe."""
    legada = CandidateIdentity.objects.create(
        subject=novo_subject(),
        nome="Maria Silva",
        cpf_normalizado="12345678909",
        created_at=timezone.now(),
    )
    associacao.associar_credencial(legada, "maria@exemplo.test", "maria@exemplo.test")
    sessao = client.session
    sessao["portal_identidade"] = str(legada.pk)
    sessao.save()

    resposta = client.post(reverse("portal:inscrever", args=[selecao.id, PERFIL_DOCENTE]))

    assert reverse("portal:meus-dados") not in resposta["Location"]


def test_cpf_invalido_e_recusado_com_explicacao(client, nova):
    resposta = client.post(
        reverse("portal:meus-dados"), {"nome": "Maria Silva", "cpf": "111.111.111-11"}
    )
    corpo = resposta.content.decode()
    # A recusa afirma o que o sistema confere — os dígitos verificadores —, e não a existência do
    # número: nenhuma consulta à Receita acontece aqui.
    assert "não formam um CPF válido" in corpo
    assert "não existe" not in corpo


def test_primeiro_nome_sozinho_e_recusado(client, nova):
    """O nome vai no comprovante, e é por ele que a conferência documental acontece."""
    resposta = client.post(reverse("portal:meus-dados"), {"nome": "Maria", "cpf": CPF})
    assert "nome completo" in resposta.content.decode()


def test_o_cpf_congela_depois_da_primeira_enviada(client, nova, selecao):
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

    client.post(reverse("portal:meus-dados"), {"nome": "Maria Silva", "cpf": CPF})
    Inscricao.objects.create(
        id=uuid.uuid4(),
        identity_subject=nova.subject,
        edital_id=selecao.id,
        profile_id=PERFIL_DOCENTE,
        nome="Maria Silva",
        cpf=CPF,
        cpf_normalizado="12345678909",
        email="nova@exemplo.test",
        created_at=timezone.now(),
    )
    Inscricao.objects.update(
        status="SUBMETIDA",
        submitted_at=timezone.now(),
        declaracoes_aceitas_em=timezone.now(),
        versao_aceita=VersaoConsolidada.objects.filter(edital_id=selecao.id).first(),
        protocolo="INS-2027-AAAA1111",
    )
    nova.refresh_from_db()

    assert nucleo.cpf_congelado(nova)
    client.post(reverse("portal:meus-dados"), {"nome": "Maria Silva", "cpf": "987.654.321-00"})
    nova.refresh_from_db()
    assert nova.cpf_normalizado == "12345678909", "o CPF que consta do comprovante não muda"


def test_corrigir_o_nome_alcanca_o_rascunho_e_nao_a_enviada(client, nova, selecao):
    """Uma regra só para os três campos do núcleo: rascunho acompanha, enviada congela (FR-014)."""
    client.post(reverse("portal:meus-dados"), {"nome": "Maria Silva", "cpf": CPF})
    client.post(reverse("portal:inscrever", args=[selecao.id, PERFIL_DOCENTE]))

    client.post(reverse("portal:meus-dados"), {"nome": "Maria S. Silva", "cpf": CPF})

    inscricao = Inscricao.objects.get()
    corpo = client.get(reverse("portal:inscricao", args=[inscricao.id])).content.decode()
    assert "Maria S. Silva" in corpo, "o rascunho aberto acompanha a identidade"
