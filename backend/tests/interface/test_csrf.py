"""FR-008/FR-009 da 003: a sessão administrativa não pratica atos que a pessoa não pediu.

A interface autentica por sessão. Sem verificação anti-falsificação, os `{% csrf_token %}` dos
formulários não são fiscalizados por ninguém e qualquer página externa alcança, em nome de quem
estiver logado, atos irreversíveis como publicar, homologar e encerrar.
"""

import pytest
from django.test import Client
from django.urls import reverse

from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from tests.fixtures.publicacao import publish_original


@pytest.fixture
def cliente_rigoroso():
    """Cliente que aplica a verificação anti-falsificação, como um navegador de terceiros."""
    return Client(enforce_csrf_checks=True)


@pytest.mark.django_db
def test_post_sem_token_e_recusado(cliente_rigoroso, seletor_ligado):
    resposta = cliente_rigoroso.post(
        reverse("interface:identificar"), {"subject": "alguem", "papeis": ["gestor"]}
    )
    assert resposta.status_code == 403
    assert cliente_rigoroso.session.get("interface_identidade") is None


@pytest.mark.django_db
def test_post_vindo_do_formulario_da_interface_e_aceito(cliente_rigoroso, seletor_ligado):
    """O token que a própria tela emite continua valendo — a proteção não quebra o fluxo."""
    formulario = cliente_rigoroso.get(reverse("interface:identificar"))
    token = formulario.context["csrf_token"]
    resposta = cliente_rigoroso.post(
        reverse("interface:identificar"),
        {"subject": "alguem", "papeis": ["gestor"], "csrfmiddlewaretoken": str(token)},
    )
    assert resposta.status_code == 302
    assert cliente_rigoroso.session["interface_identidade"]["subject"] == "alguem"


@pytest.mark.django_db(transaction=True)
def test_ato_irreversivel_sem_token_nao_produz_efeito(
    cliente_rigoroso, seletor_ligado, api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    processo = edital.processo
    # A sessão é aberta legitimamente, pelo formulário da própria interface: o que se verifica
    # aqui é que ter sessão aberta não basta para praticar o ato a partir de fora.
    formulario = cliente_rigoroso.get(reverse("interface:identificar"))
    cliente_rigoroso.post(
        reverse("interface:identificar"),
        {
            "subject": "gestor",
            "papeis": ["gestor"],
            "csrfmiddlewaretoken": str(formulario.context["csrf_token"]),
        },
    )
    assert cliente_rigoroso.session["interface_identidade"]["subject"] == "gestor"

    resposta = cliente_rigoroso.post(
        reverse("interface:processo-ato", args=[processo.id, "encerrar"]),
        {"motivo": "Conclusão"},
    )

    assert resposta.status_code == 403
    processo.refresh_from_db()
    assert processo.status != ProcessoSeletivo.Status.ENCERRADO
    assert Edital.objects.get(pk=edital.pk).status == Edital.Status.PUBLICADO


@pytest.mark.django_db
def test_resposta_html_impede_exibicao_em_moldura(client, seletor_ligado):
    resposta = client.get(reverse("interface:identificar"))
    assert resposta.headers["X-Frame-Options"] == "DENY"


@pytest.mark.django_db(transaction=True)
def test_api_autenticada_por_cabecalho_nao_passa_a_exigir_token_de_sessao(
    api_client, manager_headers, process_payload
):
    """FR-010: a proteção é da sessão; o contrato da API não muda."""
    resposta = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert resposta.status_code == 201, resposta.content
