"""Tela de Retificação (US4 da 002).

O que se verifica: a pessoa edita o conteúdo vigente e o sistema deriva as Alterações
Normativas; o antes e o depois são apresentados; a vigência futura é dita explicitamente; e
nada muda para o público antes da Publicação.
"""

import pytest
from django.urls import reverse

from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar

TODOS = ["elaborador", "homologador", "publicador"]


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload)


@pytest.fixture
def vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def campos(vigente, **alteracoes):
    """Todos os campos como estão hoje, com as alterações pedidas por cima."""
    from processo_seletivo.interface.retificacao import campos_editaveis

    enviados = {
        f"campo:{campo['caminho']}": campo["valor"]
        for grupo in campos_editaveis(vigente.content)
        for campo in grupo["campos"]
    }
    enviados.update({f"campo:{caminho}": valor for caminho, valor in alteracoes.items()})
    return enviados


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_editar_o_vigente_deriva_as_alteracoes(client, seletor_ligado, edital, vigente):
    """A pessoa não digita caminho JSON Pointer; ela edita o conteúdo e o sistema deduz."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{"/profiles/0/immediateVacancies": "9"}),
            "justificativa": "Ampliação de vagas",
        },
    )
    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert "O que vai mudar (1)" in corpo
    assert "Vagas imediatas" in corpo
    assert not Retificacao.objects.exists(), "ver o que muda não cria a Retificação"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_confirmar_cria_a_retificacao_com_as_alteracoes_derivadas(
    client, seletor_ligado, edital, vigente
):
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{"/profiles/0/immediateVacancies": "9", "/title": "Novo título"}),
            "justificativa": "Ampliação de vagas e ajuste de título",
            "confirmar": "1",
        },
    )
    assert resposta.status_code == 302

    retificacao = Retificacao.objects.get()
    caminhos = {a.target_path: a.new_value for a in retificacao.alteracoes.all()}
    assert caminhos == {"/profiles/0/immediateVacancies": 9, "/title": "Novo título"}
    assert retificacao.status == Retificacao.Status.EM_ELABORACAO
    assert retificacao.justification == "Ampliação de vagas e ajuste de título"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_sem_alteracao_nenhuma_a_tela_recusa_antes_do_dominio(
    client, seletor_ligado, edital, vigente
):
    """Retificação sem efeito é recusada pelo domínio; a tela evita chegar até lá."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]),
        {**campos(vigente), "justificativa": "Nada muda", "confirmar": "1"},
    )
    assert resposta.status_code == 200
    assert "Nenhum campo foi alterado" in resposta.content.decode()
    assert not Retificacao.objects.exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_vigencia_futura_e_dita_explicitamente(client, seletor_ligado, edital, vigente):
    """FR-015: a tela precisa dizer a partir de quando o novo conteúdo passa a valer."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{"/profiles/0/immediateVacancies": "9"}),
            "justificativa": "Vigência futura",
            "vigencia": "2027-03-01T09:00",
            "confirmar": "1",
        },
    )
    retificacao = Retificacao.objects.get()
    assert retificacao.effective_at.year == 2027

    corpo = client.get(
        reverse("interface:retificacao-detalhe", args=[retificacao.id])
    ).content.decode()
    assert "01/03/2027" in corpo
    assert "o conteúdo atual continua valendo" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_detalhe_mostra_antes_e_depois_de_cada_alteracao(
    client, seletor_ligado, edital, vigente
):
    identificar(client, "ana.elaboradora", ["elaborador"])
    client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{"/profiles/0/immediateVacancies": "9"}),
            "justificativa": "Ampliação",
            "confirmar": "1",
        },
    )
    corpo = client.get(
        reverse("interface:retificacao-detalhe", args=[Retificacao.objects.get().id])
    ).content.decode()
    assert "/profiles/0/immediateVacancies" in corpo
    assert 'class="antes">1<' in corpo, "o valor vigente aparece como antes"
    assert 'class="depois">9<' in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_fluxo_da_retificacao_ate_a_publicacao(client, seletor_ligado, edital, vigente):
    identificar(client, "ana.elaboradora", ["elaborador"])
    client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{"/profiles/0/immediateVacancies": "9"}),
            "justificativa": "Ampliação",
            "confirmar": "1",
        },
    )
    retificacao = Retificacao.objects.get()
    antes = client.get(
        f"/api/v1/public/editais/{edital.id}/versao-vigente"
    ).json()["content"]["profiles"][0]["immediateVacancies"]
    assert antes == 1, "nada muda para o público antes da Publicação"

    def ato(acao, **campos_extra):
        url = reverse("interface:retificacao-ato", args=[retificacao.id, acao])
        chave = client.get(url).context["chave_idempotencia"]
        return client.post(url, {"chave_idempotencia": chave, **campos_extra})

    assert ato("submeter").status_code == 302
    identificar(client, "bruno.homologador", ["homologador"])
    retificacao.refresh_from_db()
    assert ato("homologar", motivo="Conferido").status_code == 302
    identificar(client, "carla.publicadora", ["publicador"])
    retificacao.refresh_from_db()
    resposta = ato(
        "publicar",
        signatario_nome="Reitora",
        signatario_cargo="Reitora",
        signatario_id="00000000-0000-0000-0000-0000000000a1",
    )
    assert resposta.status_code == 302

    depois = client.get(
        f"/api/v1/public/editais/{edital.id}/versao-vigente"
    ).json()["content"]["profiles"][0]["immediateVacancies"]
    assert depois == 9, "publicada, a Retificação passa a compor o conteúdo vigente"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_retificar_exige_edital_publicado(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    from processo_seletivo.processos.models import Edital

    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    em_elaboracao = Edital.objects.get()
    identificar(client, "ana.elaboradora", ["elaborador"])
    assert client.get(reverse("interface:retificar", args=[em_elaboracao.id])).status_code == 404


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_confirmacao_de_publicacao_mostra_o_que_passara_a_vigorar(
    client, seletor_ligado, edital, vigente
):
    identificar(client, "joao.completo", TODOS)
    client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{"/profiles/0/immediateVacancies": "9"}),
            "justificativa": "Ampliação",
            "confirmar": "1",
        },
    )
    retificacao = Retificacao.objects.get()
    corpo = client.get(
        reverse("interface:retificacao-ato", args=[retificacao.id, "publicar"])
    ).content.decode()
    assert "Este ato não pode ser desfeito" in corpo
    assert "Conteúdo que passará a vigorar" in corpo
    assert "continuam preservadas e consultáveis" in corpo
