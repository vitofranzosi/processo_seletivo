"""Os impedimentos ditos antes de alguém bater neles.

O modelo é a tela da Comissão, que diz "esta comissão ainda não tem presidente" **antes** de
alguém tentar alocar. Estes três diziam depois do clique, com o trabalho já montado — e a recusa
correta, chegando tarde, custa tanto quanto a recusa ausente.

A frase é **a mesma** que a recusa usa, lida da mesma função: duas redações do mesmo impedimento
divergem no dia em que uma delas muda, e é isso que estes testes guardam.
"""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from tests.fixtures.comissao import alocar_em, inscrever, rascunho_com_etapas
from tests.fixtures.edital import actor_headers
from tests.fixtures.publicacao import publish_original
from tests.fixtures.recursos_us4 import cenario_julgavel
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]


# ---------------------------------------------------------------- distribuir com o prazo aberto


@pytest.fixture
def com_inscricoes_abertas(db, api_client, manager_headers, process_payload):
    """O mesmo Processo A, mas com o período de inscrições em curso.

    `edital_a` não declara período — e **ausência de prazo não é prazo aberto**: a regra não se
    aplica e distribuir é admitido. É por isso que o cenário precisa ser montado aqui.
    """
    agora = timezone.now()
    rascunho = rascunho_com_etapas()
    rascunho["schedule"][0]["isRegistrationPeriod"] = True
    rascunho["schedule"][0]["startAt"] = (agora - timedelta(days=1)).isoformat()
    rascunho["schedule"][0]["endAt"] = (agora + timedelta(days=10)).isoformat()
    return publish_original(api_client, manager_headers, process_payload, draft=rascunho)


def test_a_distribuicao_anuncia_o_prazo_aberto_antes_do_clique(
    client, seletor_ligado, gestor, com_inscricoes_abertas, etapa_a1
):
    from tests.fixtures.comissao import constituir

    edital = com_inscricoes_abertas
    membros = constituir(gestor, edital.processo, [("carlos", "PRESIDENTE"), ("joao", "MEMBRO")])
    alocar_em(gestor, edital.processo, membros["joao"], edital, etapa_a1)
    inscrever(edital, 2)
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(
        reverse("interface:distribuicao", args=[edital.id, etapa_a1])
    ).content.decode()

    assert "Ainda não é possível distribuir esta Etapa" in corpo
    assert "deixaria sem avaliador quem se inscrever depois" in corpo
    # A saída faz parte do aviso: "não pode" sem dizer por onde sair é metade da informação, e o
    # ato cujo nome sugere a solução — Encerrar — é outro, mais amplo e irreversível.
    assert "ato de Retificação" in corpo


def test_sem_prazo_em_curso_a_tela_nao_inventa_aviso(
    client, seletor_ligado, gestor, edital_a, processo_a, comissao_de_a, etapa_a1
):
    """Ausência de prazo não é prazo aberto — e aviso que aparece sempre não é aviso."""
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(
        reverse("interface:distribuicao", args=[edital_a.id, etapa_a1])
    ).content.decode()

    assert "Ainda não é possível distribuir esta Etapa" not in corpo


# ------------------------------------------------------- homologar o que a própria pessoa fez


def test_homologar_avisa_que_a_publicacao_ficara_com_outra_pessoa(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """A conferência de segregação só corria em `publicar` (FR-021 da 001).

    Quem elaborava e homologava a mesma revisão descobria na terceira tela que não podia
    publicá-la — com a homologação já praticada, e ela não se desfaz pela via comum.
    """
    from processo_seletivo.processos.models import Edital
    from tests.fixtures.edital import complete_draft

    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert criado.status_code == 201, criado.content
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    quem = actor_headers(
        "carla", ["edital:elaborar", "edital:submeter"], key="segregacao-em-homologar-a"
    )
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        complete_draft(),
        format="json",
        **{**quem, "HTTP_IF_MATCH": f'"{edital.revision}"'},
    )
    edital.refresh_from_db()
    submetido = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/submissoes",
        format="json",
        **{**quem, "HTTP_IF_MATCH": f'"{edital.revision}"'},
    )
    assert submetido.status_code < 400, submetido.content

    identificar(client, "carla", ["homologador"])
    corpo = client.get(reverse("interface:ato", args=[edital.id, "homologar"])).content.decode()

    assert "Depois de homologar, você não poderá publicar esta revisão" in corpo
    # Aviso, e não impedimento: acumular os dois papéis é permitido, e o ato continua oferecido.
    assert "Homologar é permitido" in corpo


def test_quem_nao_elaborou_nao_le_o_aviso_ao_homologar(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """O aviso é sobre **esta** pessoa: quem não elaborou continuará podendo publicar."""
    from processo_seletivo.processos.models import Edital
    from tests.fixtures.edital import complete_draft

    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    quem = actor_headers(
        "carla", ["edital:elaborar", "edital:submeter"], key="segregacao-em-homologar-b"
    )
    api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        complete_draft(),
        format="json",
        **{**quem, "HTTP_IF_MATCH": f'"{edital.revision}"'},
    )
    edital.refresh_from_db()
    api_client.post(
        f"/api/v1/admin/editais/{edital.id}/submissoes",
        format="json",
        **{**quem, "HTTP_IF_MATCH": f'"{edital.revision}"'},
    )

    identificar(client, "bruno", ["homologador"])
    corpo = client.get(reverse("interface:ato", args=[edital.id, "homologar"])).content.decode()

    assert "Depois de homologar" not in corpo


# --------------------------------------------- publicar como definitivo com a disputa em curso


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_previa_anuncia_o_que_impede_a_definitiva(
    client, seletor_ligado, gestor, api_client, manager_headers, process_payload
):
    """O `select` oferecia "Resultado definitivo" sem condição, e o 422 vinha depois do clique.

    A verificação de publicabilidade cobria o que vale para as duas naturezas; os fatos da
    definitividade — aqui, o recurso pendente — não chegavam à tela (FR-005, FR-081).
    """
    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=931, codigo="0931"
    )
    cenario = peca["cenario"]
    identificar(client, "paula.publicadora", ["publicador"])

    corpo = client.get(
        reverse(
            "interface:previa-de-publicacao",
            args=[cenario["edital"].id, cenario["marco"], cenario["ato"].id],
        )
    ).content.decode()

    assert "ainda não pode ser publicado como definitivo" in corpo
    assert "recurso pendente de julgamento sobre este marco" in corpo
    # O preliminar continua sendo o caminho normal: o aviso informa, e não impede.
    assert "Publicar este resultado" in corpo
