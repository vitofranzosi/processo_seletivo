"""Tela de situação e atos do Edital (US3 da 002).

É onde a interface passa a ter efeito jurídico. O que se verifica: confirmação antes de ato
irreversível com as consequências ditas, segregação de funções comunicada antes da tentativa,
e o duplo clique não praticando dois atos.
"""

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models import Publicacao
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar

DRAFT = {
    "perfil-0-id": "cccccccc-0000-4000-8000-00000000f001",
    "perfil-0-code": "P1",
    "perfil-0-name": "Perfil",
    "perfil-0-immediateVacancies": "1",
    "perfil-0-reserveType": "NONE",
    "evento-0-id": "cccccccc-0000-4000-8000-00000000f002",
    "evento-0-type": "INSCRICAO",
    "evento-0-description": "Inscrições",
    "evento-0-startAt": "2026-10-01T09:00",
}
SIGNATARIO = {
    "signatario_nome": "Reitora",
    "signatario_cargo": "Reitora",
    "signatario_id": "00000000-0000-0000-0000-0000000000a1",
}


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    return Edital.objects.get()


def praticar(client, edital, acao, **campos):
    """Percorre o caminho real: abre a confirmação, pega a chave e confirma."""
    url = reverse("interface:ato", args=[edital.id, acao])
    confirmacao = client.get(url)
    assert confirmacao.status_code == 200, confirmacao.content
    chave = confirmacao.context["chave_idempotencia"]
    return client.post(url, {"chave_idempotencia": chave, **campos}), chave


@pytest.mark.django_db
@pytest.mark.integration
def test_fluxo_completo_ate_a_publicacao(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    client.post(reverse("interface:compor", args=[edital.id]), DRAFT)
    praticar(client, Edital.objects.get(), "submeter")
    assert Edital.objects.get().status == Edital.Status.EM_REVISAO

    identificar(client, "bruno.homologador", ["homologador"])
    praticar(client, Edital.objects.get(), "homologar", motivo="Conferido pela comissão")
    assert Edital.objects.get().status == Edital.Status.HOMOLOGADO

    identificar(client, "carla.publicadora", ["publicador"])
    praticar(client, Edital.objects.get(), "publicar", **SIGNATARIO)
    assert Edital.objects.get().status == Edital.Status.PUBLICADO
    assert Publicacao.objects.filter(edital=edital).count() == 1


@pytest.mark.django_db
@pytest.mark.integration
def test_confirmacao_diz_o_que_o_ato_provoca_antes_de_praticar(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """FR-010 e FR-011: consequências e irreversibilidade ditas antes da confirmação."""
    publicado = publish_original(api_client, manager_headers, process_payload)
    identificar(client, "marcia.gestora", ["gestor"])
    corpo = client.get(
        reverse("interface:ato", args=[publicado.id, "encerrar"])
    ).content.decode()

    assert "Este ato não pode ser desfeito" in corpo
    assert "conclusão regular" in corpo
    assert "permanecem disponíveis na consulta pública" in corpo
    assert "Confirmar: Encerrar" in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_confirmar_duas_vezes_pratica_um_ato_so(client, seletor_ligado, edital):
    """A chave de idempotência nasce no formulário: duplo clique não publica duas vezes."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    client.post(reverse("interface:compor", args=[edital.id]), DRAFT)
    praticar(client, Edital.objects.get(), "submeter")
    identificar(client, "bruno.homologador", ["homologador"])
    praticar(client, Edital.objects.get(), "homologar", motivo="OK")

    identificar(client, "carla.publicadora", ["publicador"])
    atual = Edital.objects.get()
    url = reverse("interface:ato", args=[atual.id, "publicar"])
    chave = client.get(url).context["chave_idempotencia"]
    primeira = client.post(url, {"chave_idempotencia": chave, **SIGNATARIO})
    segunda = client.post(url, {"chave_idempotencia": chave, **SIGNATARIO})

    assert primeira.status_code == segunda.status_code == 302
    assert Publicacao.objects.filter(edital=edital).count() == 1


@pytest.mark.django_db
@pytest.mark.integration
def test_segregacao_e_avisada_antes_da_tentativa(client, seletor_ligado, edital):
    """FR-012: comunicar a exigência antes, e não apenas depois da recusa."""
    identificar(client, "joao.sozinho", ["elaborador", "homologador", "publicador"])
    client.post(reverse("interface:compor", args=[edital.id]), DRAFT)
    praticar(client, Edital.objects.get(), "submeter")
    praticar(client, Edital.objects.get(), "homologar", motivo="OK")

    detalhe = client.get(reverse("interface:detalhe", args=[edital.id])).content.decode()
    assert "Você não poderá publicar este Edital" in detalhe

    confirmacao = client.get(
        reverse("interface:ato", args=[edital.id, "publicar"])
    ).content.decode()
    assert "Segregação de funções" in confirmacao
    assert "não pode publicá-la sozinho" in confirmacao

    resposta, _ = praticar(client, Edital.objects.get(), "publicar", **SIGNATARIO)
    assert resposta.status_code == 403, "e o domínio recusa de fato"
    assert not Publicacao.objects.filter(edital=edital).exists()


@pytest.mark.django_db
@pytest.mark.integration
def test_motivo_obrigatorio_e_exigido_antes_do_command(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    client.post(reverse("interface:compor", args=[edital.id]), DRAFT)
    praticar(client, Edital.objects.get(), "submeter")
    identificar(client, "bruno.homologador", ["homologador"])

    resposta, _ = praticar(client, Edital.objects.get(), "homologar", motivo="   ")
    assert resposta.status_code == 422
    assert "é obrigatório" in resposta.content.decode()
    assert Edital.objects.get().status == Edital.Status.EM_REVISAO


@pytest.mark.django_db
@pytest.mark.integration
def test_publicar_exige_autoridade_signataria(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    client.post(reverse("interface:compor", args=[edital.id]), DRAFT)
    praticar(client, Edital.objects.get(), "submeter")
    identificar(client, "bruno.homologador", ["homologador"])
    praticar(client, Edital.objects.get(), "homologar", motivo="OK")
    identificar(client, "carla.publicadora", ["publicador"])

    resposta, _ = praticar(client, Edital.objects.get(), "publicar", signatario_nome="Reitora")
    assert resposta.status_code == 422
    assert "Autoridade Signatária" in resposta.content.decode()
    assert not Publicacao.objects.exists()


@pytest.mark.django_db
@pytest.mark.integration
def test_detalhe_mostra_a_trilha_e_quem_atuou(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    publicado = publish_original(api_client, manager_headers, process_payload)
    identificar(client, "auditor", ["auditor"])
    corpo = client.get(reverse("interface:detalhe", args=[publicado.id])).content.decode()

    assert 'class="e-atual"' in corpo
    assert corpo.count('class="e-concluida"') == 3, "elaboração, revisão e homologação concluídas"
    assert "preparador" in corpo and "homologador" in corpo and "publicador" in corpo
    assert "Diretora-Geral" in corpo, "Autoridade Signatária aparece"


@pytest.mark.django_db
@pytest.mark.integration
def test_edital_publicado_anuncia_imutabilidade(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """FR-013: publicado é imutável, e a Retificação é o caminho."""
    publicado = publish_original(api_client, manager_headers, process_payload)
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(reverse("interface:detalhe", args=[publicado.id])).content.decode()
    assert "Conteúdo imutável" in corpo
    assert "Retificação" in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_ato_sem_permissao_nao_e_oferecido_nem_aceito(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    client.post(reverse("interface:compor", args=[edital.id]), DRAFT)
    praticar(client, Edital.objects.get(), "submeter")

    corpo = client.get(reverse("interface:detalhe", args=[edital.id])).content.decode()
    assert "Homologar</a>" not in corpo, "o Elaborador não vê o ato de homologar"

    resposta, _ = praticar(client, Edital.objects.get(), "homologar", motivo="Tentativa")
    assert resposta.status_code == 403
    assert Edital.objects.get().status == Edital.Status.EM_REVISAO


@pytest.mark.django_db
@pytest.mark.integration
def test_cancelado_sai_da_trilha_em_vez_de_avancar(client, seletor_ligado, edital):
    identificar(client, "marcia.gestora", ["gestor"])
    praticar(client, edital, "cancelar", motivo="Desistência institucional")

    corpo = client.get(reverse("interface:detalhe", args=[edital.id])).content.decode()
    assert Edital.objects.get().status == Edital.Status.CANCELADO
    assert 'class="e-fora"' in corpo
    assert "não é o mesmo que encerramento" in corpo
