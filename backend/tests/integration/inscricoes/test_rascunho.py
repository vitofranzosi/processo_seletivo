"""Abrir, retomar e preencher o rascunho (US3 da 009).

O rascunho é o que torna a jornada retomável — e é também onde a unicidade e a titularidade
passam a valer. As três coisas se provam juntas porque juntas é que elas falham: um rascunho
duplicado, um Perfil trocado no meio, ou uma inscrição alheia alcançada por endereço.
"""

from datetime import timedelta

import pytest
from django.db.utils import IntegrityError
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.inscricoes.application.rascunho import abrir_inscricao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.candidato import MARIA, registrar
from tests.fixtures.edital import identificador
from tests.fixtures.selecao import publicar_selecao, rascunho_de_selecao

PERFIL_DOCENTE = identificador(401, 0)
PERFIL_TECNICO = identificador(406, 0)


def _publicar(api_client, manager_headers, process_payload, *, inicio=None, fim=None):
    agora = timezone.now()
    rascunho = rascunho_de_selecao()
    rascunho["schedule"][0]["startAt"] = (inicio or agora - timedelta(days=1)).isoformat()
    rascunho["schedule"][0]["endAt"] = (fim or agora + timedelta(days=10)).isoformat()
    rascunho["schedule"][0]["isRegistrationPeriod"] = True
    return publicar_selecao(api_client, manager_headers, process_payload, rascunho=rascunho)


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_abrir_duas_vezes_leva_a_mesma_inscricao(api_client, manager_headers, process_payload):
    edital = _publicar(api_client, manager_headers, process_payload)

    primeira = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    segunda = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)

    assert primeira.id == segunda.id
    assert Inscricao.objects.count() == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_mesma_pessoa_pode_concorrer_a_outro_perfil(api_client, manager_headers, process_payload):
    """A Constituição admite Inscrições distintas para Perfis distintos do mesmo Edital."""
    edital = _publicar(api_client, manager_headers, process_payload)

    abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_TECNICO)

    assert Inscricao.objects.filter(identity_subject=MARIA.subject).count() == 2


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_banco_recusa_a_segunda_inscricao_no_mesmo_perfil(
    api_client, manager_headers, process_payload
):
    """A unicidade vale em qualquer estado, e é o banco que responde por ela (FR-028)."""
    edital = _publicar(api_client, manager_headers, process_payload)
    abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)

    with pytest.raises(IntegrityError):
        Inscricao.objects.create(
            identity_subject=MARIA.subject,
            edital=edital,
            profile_id=PERFIL_DOCENTE,
            created_at=timezone.now(),
        )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_perfil_nao_muda_dentro_da_inscricao(
    client, api_client, manager_headers, process_payload, settings
):
    """FR-030: é a decisão que dispensa reconciliação de documentos.

    Não existe caminho — nem pela tela, nem por POST forjado — que troque o Perfil. Concorrer a
    outro Perfil é abrir outra inscrição, e é por isso que o campo não aparece em formulário
    nenhum.
    """
    edital = _publicar(api_client, manager_headers, process_payload)
    inscricao = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)
    sessao = client.session
    sessao["portal_identidade"] = str(registrar(MARIA).pk)
    sessao.save()

    resposta = client.post(
        reverse("portal:inscricao", args=[inscricao.id]),
        {"telefone": "27999990000", "profile_id": PERFIL_TECNICO, "perfil": PERFIL_TECNICO},
    )

    assert resposta.status_code == 200
    inscricao.refresh_from_db()
    assert str(inscricao.profile_id) == PERFIL_DOCENTE


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_iniciar_fora_do_periodo_e_recusado(api_client, manager_headers, process_payload):
    """FR-019: ter o endereço da vaga não dá direito de começar antes ou depois do prazo."""
    agora = timezone.now()
    edital = _publicar(
        api_client,
        manager_headers,
        process_payload,
        inicio=agora + timedelta(days=5),
        fim=agora + timedelta(days=20),
    )

    with pytest.raises(DomainError) as recusa:
        abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)

    assert recusa.value.code == "registration_closed"
    assert Inscricao.objects.count() == 0


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_perfil_que_nao_esta_no_conteudo_publicado_nao_abre_inscricao(
    api_client, manager_headers, process_payload
):
    edital = _publicar(api_client, manager_headers, process_payload)

    with pytest.raises(DomainError) as recusa:
        abrir_inscricao(
            identidade=MARIA,
            edital_id=edital.id,
            profile_id="00000000-0000-0000-0000-0000000009fd",
        )

    assert recusa.value.status == 404


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_os_dados_da_identidade_chegam_ao_rascunho(api_client, manager_headers, process_payload):
    """FR-037: nada do que a identidade forneceu é digitado de novo."""
    edital = _publicar(api_client, manager_headers, process_payload)

    inscricao = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)

    assert (inscricao.nome, inscricao.email) == (MARIA.nome, MARIA.email)
    assert inscricao.cpf_normalizado == "12345678909", "normalizado para comparação (FR-073)"
    assert inscricao.status == Inscricao.Status.RASCUNHO
    assert inscricao.versao_reconhecida is not None, "a versão vista fica registrada (FR-059a)"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_criacao_da_inscricao_e_auditada(api_client, manager_headers, process_payload):
    """FR-077 e FR-078: o autor é a identidade externa; o escopo, o do Processo alvo."""
    from processo_seletivo.auditoria.models import RegistroAuditoria

    edital = _publicar(api_client, manager_headers, process_payload)
    inscricao = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL_DOCENTE)

    registro = RegistroAuditoria.objects.get(aggregate_id=inscricao.id)

    assert registro.actor_subject == MARIA.subject
    assert registro.institution_scope == edital.institution_scope
    assert registro.operation == "CRIAR"
    assert MARIA.cpf not in registro.reason, "CPF completo não entra na auditoria (FR-078)"
