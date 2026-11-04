"""O desfecho da conferência aparece onde o do ato já aparece (116, FR-3646).

Sem tela nova: a recusa vem na confirmação, como as demais; a advertência e a informação vêm na
faixa "Ato registrado" do detalhe, lidas do `detalhe` do registro de auditoria do ato — e não de
sessão nem de consulta nova. No congelamento, a advertência vem no desfecho que a tela do sorteio já
guarda.
"""

import copy
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.processos.models import Edital
from processo_seletivo.sorteios.domain import conferencia as dominio
from tests.fixtures.edital import DRAW_METHOD, actor_headers, complete_draft
from tests.fixtures.sorteio import METODO, certame_de_sorteio
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.integration]


def _metodo(ocorrencia):
    metodo = copy.deepcopy(DRAW_METHOD)
    metodo.update(
        {
            "source": "Loteria Federal",
            "occurrence": ocorrencia,
            "occurrenceAt": (timezone.now() + timedelta(days=40)).isoformat(),
        }
    )
    return metodo


@pytest.fixture
def em_elaboracao(api_client, manager_headers, process_payload):
    def criar(ocorrencia):
        criado = api_client.post(
            "/api/v1/admin/processos", process_payload, format="json", **manager_headers
        )
        assert criado.status_code == 201, criado.content
        edital = Edital.objects.get(processo_id=criado.json()["id"])
        rascunho = complete_draft()
        rascunho["profiles"][0]["classificationMilestones"][0]["drawMethod"] = _metodo(ocorrencia)
        gravado = api_client.put(
            f"/api/v1/admin/editais/{edital.id}/rascunho",
            rascunho,
            format="json",
            **{
                **actor_headers("preparador", ["edital:elaborar"]),
                "HTTP_IF_MATCH": f'"{edital.revision}"',
            },
        )
        assert gravado.status_code < 400, gravado.content
        return Edital.objects.get(pk=edital.pk)

    return criar


def _submeter_pela_tela(client, edital):
    url = reverse("interface:ato", args=[edital.id, "submeter"])
    confirmacao = client.get(url)
    assert confirmacao.status_code == 200, confirmacao.content
    return client.post(url, {"chave_idempotencia": confirmacao.context["chave_idempotencia"]})


@pytest.mark.django_db
def test_a_informacao_aparece_no_detalhe_depois_de_submeter(
    client, seletor_ligado, em_elaboracao, caixa
):
    caixa.usar_gravacao()
    edital = em_elaboracao("6116")
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = _submeter_pela_tela(client, edital)

    assert resposta.status_code == 302
    corpo = client.get(resposta["Location"]).content.decode()
    trecho = corpo.split('class="conferencia-do-ato"', 1)[1].split("</ul>", 1)[0]
    assert 'class="nota"' in trecho
    assert "Concurso 6116: ainda não realizado na consulta de" in trecho
    assert "não é verificada pela Caixa" in trecho


@pytest.mark.django_db
def test_a_advertencia_aparece_no_detalhe(client, seletor_ligado, em_elaboracao, caixa):
    caixa.fora_do_ar()
    edital = em_elaboracao("6116")
    identificar(client, "ana.elaboradora", ["elaborador"])

    corpo = client.get(_submeter_pela_tela(client, edital)["Location"]).content.decode()

    trecho = corpo.split('class="conferencia-do-ato"', 1)[1].split("</ul>", 1)[0]
    assert 'class="aviso"' in trecho
    assert dominio.SEM_RESPOSTA_A_TEMPO in trecho


@pytest.mark.django_db
def test_sem_o_parametro_do_ato_o_detalhe_nao_repete_a_conferencia(
    client, seletor_ligado, em_elaboracao, caixa
):
    edital = em_elaboracao("6116")
    identificar(client, "ana.elaboradora", ["elaborador"])
    _submeter_pela_tela(client, edital)

    corpo = client.get(reverse("interface:detalhe", args=[edital.id])).content.decode()

    assert "conferencia-do-ato" not in corpo


@pytest.mark.django_db
def test_a_recusa_aparece_na_confirmacao(client, seletor_ligado, em_elaboracao, caixa):
    caixa.usar_gravacao()
    edital = em_elaboracao("5000")
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = _submeter_pela_tela(client, edital)

    assert resposta.status_code == 422
    corpo = resposta.content.decode()
    assert "O concurso 5000 da Loteria Federal já foi realizado, em 26/08/2015" in corpo
    assert Edital.objects.get(pk=edital.pk).status == Edital.Status.EM_ELABORACAO


@pytest.mark.django_db(transaction=True)
def test_a_advertencia_do_congelamento_aparece_na_tela_do_sorteio(
    client, seletor_ligado, gestor, api_client, manager_headers, process_payload, caixa
):
    metodo = copy.deepcopy(METODO)
    metodo.update(_metodo("6116"))
    certame = certame_de_sorteio(
        gestor, api_client, manager_headers, process_payload, metodo=metodo
    )
    identificar(client, "maria", [])
    caixa.fora_do_ar(dominio.SEM_CONEXAO)

    resposta = client.post(
        reverse(
            "interface:publicar-relacao-do-sorteio", args=[certame["edital"].id, certame["marco"]]
        ),
        {"chave_idempotencia": "tela-116"},
    )

    assert resposta.status_code == 302
    corpo = client.get(resposta["Location"]).content.decode()
    assert "Relação publicada e congelada" in corpo
    assert "não foi possível falar com a Caixa" in corpo
    assert "A relação foi publicada." in corpo


@pytest.mark.django_db(transaction=True)
def test_a_recusa_do_congelamento_aparece_na_tela_do_sorteio(
    client, seletor_ligado, gestor, api_client, manager_headers, process_payload, caixa
):
    from datetime import date

    metodo = copy.deepcopy(METODO)
    metodo.update(_metodo("6116"))
    certame = certame_de_sorteio(
        gestor, api_client, manager_headers, process_payload, metodo=metodo
    )
    identificar(client, "maria", [])
    caixa.realizado_ate(6116, date(2026, 11, 7))

    resposta = client.post(
        reverse(
            "interface:publicar-relacao-do-sorteio", args=[certame["edital"].id, certame["marco"]]
        ),
        {"chave_idempotencia": "tela-116-recusa"},
    )

    corpo = client.get(resposta["Location"]).content.decode()
    assert "Não é possível congelar a relação: o concurso 6116" in corpo
