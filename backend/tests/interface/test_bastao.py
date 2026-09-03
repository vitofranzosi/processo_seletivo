"""T058 a T060 — passagem de bastão: quem entrega sabe a quem entregou (FR-028 a FR-031).

Era a limitação estrutural que a auditoria registrou como "nenhuma noção de passagem de bastão":
submetido, o Edital ficava "aguardando" sem dizer quem deveria agir.

**O que estes testes protegem é a diferença entre duas derivações.** Derivar do mapa de permissões
diria "é você" a quem elaborou *e* homologou o mesmo Edital — exatamente a pessoa que a publicação
vai recusar. A indicação precisa consultar também a segregação de funções.
"""

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import Edital
from tests.fixtures.edital import actor_headers, complete_draft
from tests.interface.conftest import identificar

pytestmark = pytest.mark.django_db(transaction=True)


def _ate(api_client, manager_headers, process_payload, *, parar_em, quem_homologa="bruno"):
    """Leva o Edital até `submetido` ou `homologado`, com quem se indicar."""
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    preparer = actor_headers("ana", ["edital:elaborar", "edital:submeter"])
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        complete_draft(),
        format="json",
        **{**preparer, "HTTP_IF_MATCH": '"1"'},
    )
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/submissoes",
        format="json",
        **{**preparer, "HTTP_IF_MATCH": '"2"'},
    )
    if parar_em == "homologado":
        api_client.post(
            f"/api/v1/admin/editais/{edital.id}/homologacoes",
            {"reason": "Conferido."},
            format="json",
            **{**actor_headers(quem_homologa, ["edital:homologar"]), "HTTP_IF_MATCH": '"3"'},
        )
    return Edital.objects.get(pk=edital.pk)


def bastao(client, edital):
    resposta = client.get(reverse("interface:detalhe", args=[edital.id]))
    return resposta.context["proximo_passo"], resposta.content.decode()


def test_submetido_aguarda_quem_homologa(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    edital = _ate(api_client, manager_headers, process_payload, parar_em="submetido")
    identificar(client, "ana", ["elaborador"])

    passo, corpo = bastao(client, edital)

    assert passo["papel"] == "quem homologa"
    assert passo["sou_eu"] is False
    assert "Aguardando quem homologa" in corpo


def test_homologado_aponta_quem_publica_como_responsavel(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    edital = _ate(api_client, manager_headers, process_payload, parar_em="homologado")
    identificar(client, "carla", ["publicador"])

    passo, corpo = bastao(client, edital)

    assert passo["papel"] == "quem publica"
    assert passo["sou_eu"] is True
    assert "O próximo ato é seu" in corpo


def test_quem_elaborou_e_homologou_nao_e_apontado_como_quem_publica(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """O caso que separa "derivar do mapa de permissões" de "derivar do que o domínio aceitaria".

    `ana` elaborou, submeteu **e** homologou. Ainda que tenha a permissão de publicar, a publicação
    a recusará por segregação de funções — e apontá-la seria mandar a pessoa para uma recusa.
    """
    edital = _ate(
        api_client, manager_headers, process_payload, parar_em="homologado", quem_homologa="ana"
    )
    identificar(client, "ana", ["elaborador", "homologador", "publicador"])

    passo, corpo = bastao(client, edital)

    assert passo["papel"] == "quem publica"
    assert passo["sou_eu"] is False, "a segregação de funções tem de entrar no cálculo"
    assert "outra pessoa autorizada" in passo["observacao"]
    assert "O próximo ato é seu" not in corpo


def test_publicado_nao_tem_proximo_responsavel(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """Depois de publicado o Edital é público: não há bastão a passar."""
    from tests.fixtures.publicacao import publish_original

    edital = publish_original(api_client, manager_headers, process_payload)
    identificar(client, "ana", ["elaborador"])

    passo, corpo = bastao(client, edital)

    assert passo is None
    assert "Aguardando" not in corpo


def test_a_confirmacao_diz_a_quem_o_ato_entrega(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """Antes de submeter, quem confirma precisa saber a quem está entregando."""
    edital = _ate(api_client, manager_headers, process_payload, parar_em="submetido")
    identificar(client, "bruno", ["homologador"])

    resposta = client.get(reverse("interface:ato", args=[edital.id, "homologar"]))

    assert "aguardando quem publica" in resposta.content.decode()


def test_nada_de_fila_notificacao_ou_atribuicao_nasce(api_client, manager_headers, process_payload):
    """FR-030: a indicação é leitura derivada. Nenhum estado novo é persistido.

    Se algum dia isto virar tabela, este teste é o que acusa — e a conversa passa a ser sobre
    workflow engine, que a `007` declarou fora de escopo.
    """
    from django.apps import apps

    _ate(api_client, manager_headers, process_payload, parar_em="homologado")

    # `avaliacoes.Atribuicao` é a exceção **nomeada**, e não uma folga: a `012` promoveu a palavra
    # a entidade do domínio com outro significado — o vínculo avaliador→inscrição —, e o que este
    # guard persegue é estado de workflow sobre o Edital (D-003 da `012`). Excluir a classe pelo
    # nome completo mantém o dente: um `TarefaAtribuicao` novo, em qualquer app, continua caindo.
    LEGITIMOS = {("avaliacoes", "atribuicao")}
    nomes = {
        modelo.__name__.lower()
        for modelo in apps.get_models()
        if (modelo._meta.app_label, modelo.__name__.lower()) not in LEGITIMOS
    }
    for proibido in ("fila", "notificacao", "atribuicao", "designacao", "tarefa", "pendenciaator"):
        assert proibido not in nomes, f"{proibido} indica mecanismo que FR-030 proíbe"

    campos = {campo.name for campo in Edital._meta.get_fields()}
    assert "responsavel_atual" not in campos
    assert "proximo_responsavel" not in campos
