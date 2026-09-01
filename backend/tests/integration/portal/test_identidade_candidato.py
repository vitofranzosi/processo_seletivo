"""A identidade do candidato é um eixo próprio (US3 da 009, FR-020 a FR-025).

O que se prova aqui é uma separação, e separações falham em silêncio: o dia em que as duas
identidades compartilharem chave de sessão, tudo continua funcionando — até alguém identificado
no `/gestao/` ser tratado como candidato, ou o contrário.
"""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.interface import identidade as institucional
from processo_seletivo.portal import identidade as candidato
from tests.fixtures.selecao import publicar_selecao, rascunho_de_selecao
from tests.interface.conftest import identificar as identificar_servidor


@pytest.fixture
def provedor_ligado(settings):
    settings.PORTAL_IDENTIDADE_DEMO = True
    settings.INTERFACE_SELETOR_IDENTIDADE = True


def identificar_candidato(client, *, nome="Maria Silva", cpf="123.456.789-09", email="m@ex.br"):
    resposta = client.post(
        reverse("portal:identificar"), {"nome": nome, "cpf": cpf, "email": email}
    )
    assert resposta.status_code == 302, resposta.content
    return resposta


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_as_duas_identidades_usam_chaves_de_sessao_distintas(client, provedor_ligado):
    identificar_candidato(client)

    assert candidato.CHAVE_SESSAO in client.session
    assert institucional.CHAVE_SESSAO not in client.session


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_quem_e_servidor_no_gestao_nao_e_candidato_no_portal(client, provedor_ligado):
    identificar_servidor(client, "ana.elaboradora", ["elaborador"])

    assert institucional.CHAVE_SESSAO in client.session
    assert candidato.CHAVE_SESSAO not in client.session


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_quem_e_candidato_nao_vira_ator_institucional(client, provedor_ligado):
    identificar_candidato(client)

    resposta = client.get(reverse("interface:lista"))

    assert resposta.status_code == 302, "a gestão manda identificar-se; a sessão do portal não vale"
    assert reverse("interface:identificar") in resposta["Location"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_subject_deriva_do_cpf_e_nao_do_nome(client, provedor_ligado):
    """Propriedade de inscrição não pode depender de dado editável (FR-022)."""
    identificar_candidato(client, nome="Maria Silva", cpf="123.456.789-09")
    primeiro = client.session[candidato.CHAVE_SESSAO]["subject"]

    identificar_candidato(client, nome="Maria S. Silva", cpf="123.456.789-09")

    assert client.session[candidato.CHAVE_SESSAO]["subject"] == primeiro


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_apos_identificar_se_a_pessoa_volta_para_a_vaga(
    client, provedor_ligado, api_client, manager_headers, process_payload
):
    """FR-025: voltar para a página inicial obrigaria a refazer o caminho inteiro."""
    agora = timezone.now()
    rascunho = rascunho_de_selecao()
    rascunho["schedule"][0]["startAt"] = (agora - timedelta(days=1)).isoformat()
    rascunho["schedule"][0]["endAt"] = (agora + timedelta(days=10)).isoformat()
    rascunho["schedule"][0]["isRegistrationPeriod"] = True
    edital = publicar_selecao(api_client, manager_headers, process_payload, rascunho=rascunho)
    vaga = reverse(
        "portal:inscrever",
        args=[edital.id, "00000000-0000-0000-0000-000000000401"],
    )

    formulario = client.get(f"{reverse('portal:identificar')}?destino={vaga}")
    assert vaga in formulario.content.decode()

    resposta = client.post(
        reverse("portal:identificar"),
        {"nome": "Maria Silva", "cpf": "12345678909", "email": "m@ex.br", "destino": vaga},
    )

    # O retorno é GET e o convite é POST: em vez de devolver a pessoa a uma rota que recusaria o
    # método, a identificação conclui a intenção que ela já havia declarado e abre a inscrição.
    from processo_seletivo.inscricoes.models import Inscricao

    inscricao = Inscricao.objects.get()
    assert resposta["Location"] == reverse("portal:inscricao", args=[inscricao.id])
    assert str(inscricao.profile_id) == "00000000-0000-0000-0000-000000000401"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_destino_para_fora_do_sistema_e_ignorado(client, provedor_ligado):
    """O destino vem da requisição, e por isso é conferido: seria uma ponte para fora."""
    resposta = client.post(
        reverse("portal:identificar"),
        {
            "nome": "Maria Silva",
            "cpf": "12345678909",
            "email": "m@ex.br",
            "destino": "https://exemplo-malicioso.invalid/",
        },
    )

    assert resposta["Location"] == reverse("portal:vitrine")


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_sem_provedor_de_demonstracao_a_tela_nao_existe(client, settings):
    settings.PORTAL_IDENTIDADE_DEMO = False

    assert client.get(reverse("portal:identificar")).status_code == 404


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_tela_diz_que_e_demonstracao(client, provedor_ligado):
    corpo = client.get(reverse("portal:identificar")).content.decode()

    assert "demonstração" in corpo.lower()
    assert "não" in corpo.lower() and "verifica" in corpo.lower()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_identificacao_nao_e_armazenavel_pelo_navegador(client, provedor_ligado):
    """FR-075a: a tela carrega nome, CPF e e-mail."""
    resposta = client.get(reverse("portal:identificar"))

    assert "no-store" in resposta.headers["Cache-Control"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_cpf_inventado_e_recusado_na_identificacao(client, settings):
    """Contar onze dígitos aceitava `11111111111`.

    O CPF decide de quem é a inscrição e alimenta o `subject` da auditoria: digitado errado,
    produz uma identidade que ninguém reencontra — a pessoa volta, digita certo, e sua inscrição
    "sumiu".
    """
    settings.PORTAL_IDENTIDADE_DEMO = True

    resposta = client.post(
        reverse("portal:identificar"),
        {"nome": "Joao Souza", "cpf": "111.111.111-11", "email": "j@ex.br"},
    )

    corpo = resposta.content.decode()
    assert resposta.status_code == 200
    assert "Este CPF não existe" in corpo
    assert "111.111.111-11" in corpo, "o que foi digitado volta ao campo"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_primeiro_nome_sozinho_e_recusado(client, settings):
    """O rótulo pede o nome completo, e `Joao` passava.

    O nome vai no comprovante, e é por ele que a comissão confere o documento apresentado.
    """
    settings.PORTAL_IDENTIDADE_DEMO = True

    resposta = client.post(
        reverse("portal:identificar"),
        {"nome": "Joao", "cpf": "123.456.789-09", "email": "j@ex.br"},
    )

    assert "Informe o nome completo, com sobrenome." in resposta.content.decode()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_cpf_e_guardado_numa_forma_so(client, settings):
    """Digitado sem pontuação, guardado com ela: a mesma pessoa não aparece de dois jeitos."""
    settings.PORTAL_IDENTIDADE_DEMO = True

    client.post(
        reverse("portal:identificar"),
        {"nome": "Maria Silva", "cpf": "12345678909", "email": "m@ex.br"},
    )

    assert client.session["portal_identidade"]["cpf"] == "123.456.789-09"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_quem_se_identificou_encontra_a_saida(client, provedor_ligado):
    """Sem `Sair`, um computador compartilhado guarda a identidade de quem passou.

    Laboratório, biblioteca, lan house: a pessoa seguinte começava a inscrição dela com o CPF de
    quem estava antes — e a inscrição ia para a identidade errada.
    """
    identificar_candidato(client)

    corpo = client.get(reverse("portal:vitrine")).content.decode()
    assert "Maria Silva" in corpo, "quem está identificado aparece"
    assert reverse("portal:sair") in corpo

    client.post(reverse("portal:sair"))

    depois = client.get(reverse("portal:vitrine")).content.decode()
    assert "Maria Silva" not in depois
    assert "portal_identidade" not in client.session


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_quem_nao_se_identificou_nao_ve_saida_nenhuma(client, provedor_ligado):
    corpo = client.get(reverse("portal:vitrine")).content.decode()

    assert reverse("portal:sair") not in corpo
