"""Titularidade: a pergunta que a autorização institucional não responde (US3 da 009, FR-071).

`require_permission` decide o que um ator pode fazer e em que escopo. Ela não sabe de quem é um
registro — e escrever a segunda pergunta como se fosse a primeira é exatamente como se cria um
IDOR com aparência de autorização.
"""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.inscricoes.application.rascunho import abrir_inscricao
from processo_seletivo.portal.identidade import IdentidadeDoCandidato
from tests.fixtures.edital import identificador
from tests.fixtures.selecao import publicar_selecao, rascunho_de_selecao

MARIA = IdentidadeDoCandidato("demo:12345678909", "Maria Silva", "123.456.789-09", "m@ex.br")
JOAO = IdentidadeDoCandidato("demo:98765432100", "João Souza", "987.654.321-00", "j@ex.br")
PERFIL = identificador(401, 0)


@pytest.fixture
def inscricao_de_maria(api_client, manager_headers, process_payload, settings):
    settings.PORTAL_IDENTIDADE_DEMO = True
    agora = timezone.now()
    rascunho = rascunho_de_selecao()
    rascunho["schedule"][0]["startAt"] = (agora - timedelta(days=1)).isoformat()
    rascunho["schedule"][0]["endAt"] = (agora + timedelta(days=10)).isoformat()
    rascunho["schedule"][0]["isRegistrationPeriod"] = True
    edital = publicar_selecao(api_client, manager_headers, process_payload, rascunho=rascunho)
    return abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=PERFIL)


def _identificar(client, identidade):
    sessao = client.session
    sessao["portal_identidade"] = identidade.__dict__
    sessao.save()


@pytest.mark.django_db(transaction=True)
@pytest.mark.authorization
def test_a_titular_alcanca_a_propria_inscricao(client, inscricao_de_maria):
    _identificar(client, MARIA)

    resposta = client.get(reverse("portal:inscricao", args=[inscricao_de_maria.id]))

    assert resposta.status_code == 200


@pytest.mark.django_db(transaction=True)
@pytest.mark.authorization
def test_outra_identidade_nao_alcanca_a_inscricao_alheia(client, inscricao_de_maria):
    """404, e não 403: dizer "existe, mas não é seu" já entrega que existe."""
    _identificar(client, JOAO)

    resposta = client.get(reverse("portal:inscricao", args=[inscricao_de_maria.id]))

    assert resposta.status_code == 404
    assert MARIA.nome not in resposta.content.decode()


@pytest.mark.django_db(transaction=True)
@pytest.mark.authorization
def test_sem_identidade_a_inscricao_nao_e_alcancavel(client, inscricao_de_maria):
    """Conhecer o endereço não autoriza — o identificador público não confere direito nenhum."""
    resposta = client.get(reverse("portal:inscricao", args=[inscricao_de_maria.id]))

    assert resposta.status_code == 404


@pytest.mark.django_db(transaction=True)
@pytest.mark.authorization
def test_ator_institucional_nao_alcanca_a_inscricao_pelo_portal(
    client, inscricao_de_maria, settings
):
    """A sessão do `/gestao/` não vale no portal: são dois eixos, e nenhum empresta ao outro."""
    from tests.interface.conftest import identificar as identificar_servidor

    settings.INTERFACE_SELETOR_IDENTIDADE = True
    identificar_servidor(client, "ana.elaboradora", ["elaborador"])

    resposta = client.get(reverse("portal:inscricao", args=[inscricao_de_maria.id]))

    assert resposta.status_code == 404


@pytest.mark.django_db(transaction=True)
@pytest.mark.authorization
def test_outra_identidade_nao_grava_na_inscricao_alheia(client, inscricao_de_maria):
    _identificar(client, JOAO)

    resposta = client.post(
        reverse("portal:inscricao", args=[inscricao_de_maria.id]), {"telefone": "27999990000"}
    )

    assert resposta.status_code == 404
    inscricao_de_maria.refresh_from_db()
    assert inscricao_de_maria.telefone == ""


@pytest.mark.django_db(transaction=True)
@pytest.mark.authorization
def test_o_ator_do_candidato_nao_tem_permissao_nenhuma(inscricao_de_maria):
    """A propriedade que impede o candidato de praticar ato institucional por engano."""
    from processo_seletivo.inscricoes.application.rascunho import ator_do_candidato
    from processo_seletivo.seguranca.application.authorization import require_permission
    from processo_seletivo.shared.api.problems import DomainError

    ator = ator_do_candidato(MARIA, inscricao_de_maria.edital)

    assert ator.permissions == frozenset()
    institucionais = ("edital:elaborar", "edital:publicar", "processo:criar", "auditoria:consultar")
    for permissao in institucionais:
        with pytest.raises(DomainError) as recusa:
            require_permission(ator, permissao)
        assert recusa.value.status == 403
