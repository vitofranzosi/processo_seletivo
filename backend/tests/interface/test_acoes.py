"""T051 a T054 — o conjunto único de ações, e os três becos que ele fecha.

Os achados 07, 08 e 09 da auditoria têm uma causa só: três lugares respondiam "o que se pode fazer
com este Edital" e não se falavam. Estes testes existem para que a próxima ação criada não volte a
divergir — e o primeiro deles é o que teria pego o defeito original.
"""

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import Edital
from tests.fixtures.edital import actor_headers, complete_draft
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    return Edital.objects.get()


def homologado(api_client, manager_headers, process_payload):
    """Até a homologação, sem publicar — o estado em que `publicar` fica oferecido."""
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    preparer = actor_headers("preparador", ["edital:elaborar", "edital:submeter"])
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
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/homologacoes",
        {"reason": "OK"},
        format="json",
        **{**actor_headers("homologador", ["edital:homologar"]), "HTTP_IF_MATCH": '"3"'},
    )
    return Edital.objects.get(pk=edital.pk)


def cartao_de_acoes(client, edital):
    resposta = client.get(reverse("interface:detalhe", args=[edital.id]))
    assert resposta.status_code == 200, resposta.content
    return resposta


def rotulos(resposta):
    return {acao.rotulo for acao in resposta.context["acoes"]}


# ---------------------------------------------------------------------------
# Achado 08 — oferecer uma ação e dizer que não há ação
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "papeis",
    [
        ["elaborador"],
        ["homologador"],
        ["publicador"],
        ["gestor"],
        ["auditor"],
        ["elaborador", "homologador", "publicador", "gestor", "auditor"],
        # Sem papel algum não entra: a tela de identificação exige ao menos um, e o caso deixaria
        # de testar o cartão para testar o seletor.
    ],
)
def test_a_mensagem_de_ausencia_nunca_convive_com_uma_acao(
    client, seletor_ligado, edital, papeis
):
    """A lista e o vazio saem do mesmo conjunto — é o que torna a contradição impossível.

    Antes, o `{% empty %}` observava apenas os atos, enquanto `Retificar`, `Elaborar`, `Visualizar`
    e a auditoria eram `<li>` independentes. Com papéis que não têm nenhum ato mas alcançam alguma
    dessas telas, o cartão listava a ação e, na linha seguinte, dizia que não havia nenhuma.
    """
    identificar(client, "pessoa", papeis)
    resposta = cartao_de_acoes(client, edital)
    corpo = resposta.content.decode()

    tem_acao = bool(resposta.context["acoes"])
    diz_que_nao_ha = "Nenhum ato disponível" in corpo

    assert not (tem_acao and diz_que_nao_ha), (
        f"papéis {papeis}: o cartão lista {rotulos(resposta)} e afirma que não há ação"
    )
    assert tem_acao or diz_que_nao_ha, "sem ação e sem mensagem, o cartão fica mudo"


@pytest.mark.parametrize(
    ("situacao", "papeis", "esperada"),
    [
        ("EM_ELABORACAO", ["elaborador"], "Elaborar o Edital"),
        ("EM_ELABORACAO", ["elaborador"], "Submeter para revisão"),
        ("EM_ELABORACAO", ["auditor"], "Ver trilha de auditoria"),
    ],
)
def test_cada_papel_recebe_as_acoes_que_lhe_cabem(
    client, seletor_ligado, edital, situacao, papeis, esperada
):
    identificar(client, "pessoa", papeis)
    assert esperada in rotulos(cartao_de_acoes(client, edital))


# ---------------------------------------------------------------------------
# Achado 07 — Retificar aberto para quem não pode retificar
# ---------------------------------------------------------------------------


def test_retificar_nao_e_oferecido_sem_a_permissao(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    identificar(client, "bruno.homologador", ["homologador", "publicador"])

    assert "Retificar" not in rotulos(cartao_de_acoes(client, edital))


def test_retificar_e_oferecido_a_quem_pode(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    identificar(client, "ana.elaboradora", ["elaborador"])

    assert "Retificar" in rotulos(cartao_de_acoes(client, edital))


def test_alcancada_por_url_a_tela_de_retificar_e_de_leitura(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """FR-026: sem a permissão, nada de campos nem de envio.

    Não há vazamento — o conteúdo vigente já é visível a quem alcança o Edital. O que se corrige é
    o caminho que não termina: antes, a pessoa preenchia a tela inteira e descobria no envio.
    """
    edital = publish_original(api_client, manager_headers, process_payload)
    identificar(client, "bruno.homologador", ["homologador", "publicador"])

    resposta = client.get(reverse("interface:retificar", args=[edital.id]))
    corpo = resposta.content.decode()

    assert resposta.status_code == 200
    assert "Somente leitura" in corpo
    assert "Conteúdo vigente" in corpo
    assert 'name="campo:' not in corpo, "nenhum campo editável"
    assert 'name="justificativa"' not in corpo
    assert "Ver o que vai mudar" not in corpo
    assert "Acrescentar Perfil" not in corpo


# ---------------------------------------------------------------------------
# Achado 09 — oferecer um ato sabendo que será recusado
# ---------------------------------------------------------------------------


def test_submeter_aparece_desabilitado_com_o_motivo_quando_ha_pendencia_impeditiva(
    client, seletor_ligado, edital
):
    """FR-024: desabilitado com o motivo — não oferecido, e também não escondido.

    Esconder devolve a pessoa ao mesmo beco, só que em silêncio.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = cartao_de_acoes(client, edital)

    submeter = next(a for a in resposta.context["acoes"] if a.chave == "submeter")
    assert not submeter.disponivel
    assert "pendência" in submeter.motivo or "pendências" in submeter.motivo

    corpo = resposta.content.decode()
    assert 'aria-disabled="true"' in corpo
    assert 'aria-describedby="motivo-submeter"' in corpo, (
        "o motivo precisa alcançar quem usa leitor de tela"
    )


def test_a_desabilitacao_nao_substitui_a_recusa_do_dominio(client, seletor_ligado, edital):
    """FR-025: a tela prevê; quem recusa é o command.

    Alcançar o ato por URL direta continua sendo recusado — a previsão é conveniência, não
    fronteira de segurança.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = client.post(
        reverse("interface:ato", args=[edital.id, "submeter"]),
        {"chave_idempotencia": "ui-teste-recusa"},
    )

    edital.refresh_from_db()
    assert edital.status == Edital.Status.EM_ELABORACAO, resposta.content


def test_ato_sem_impedimento_permanece_disponivel(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """A previsão não pode desabilitar o que o domínio aceitaria."""
    edital = homologado(api_client, manager_headers, process_payload)
    identificar(client, "carla.publicadora", ["publicador"])

    publicar = next(
        (a for a in cartao_de_acoes(client, edital).context["acoes"] if a.chave == "publicar"),
        None,
    )
    assert publicar is not None and publicar.disponivel, "publicar deveria estar oferecido"
