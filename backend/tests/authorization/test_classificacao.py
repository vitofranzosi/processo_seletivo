"""Quem consulta a ordem não ganha o ato, e cada recusa diz a verdade dela (015, T090).

**O "404 uniforme" deixou de ser uniforme** (033, `FR-478`). Escopo institucional alheio continua
sendo "não encontrado"; falta de base passou a ser recusa explicada. Quem atravessa cada rota é
exatamente quem atravessava, e nenhum ato passou a ser emitido por quem não o emitia.
"""

import pytest
from django.urls import reverse

from processo_seletivo.classificacao.models import AtoDeOrdenacao, PosicaoNaOrdem
from tests.fixtures.comissao import inscrever, rascunho_com_etapas
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.authorization, pytest.mark.django_db(transaction=True)]

MARCO = "00000000-0000-4000-8000-000000000491"


@pytest.fixture
def edital_com_marco(api_client, manager_headers, process_payload):
    rascunho = rascunho_com_etapas(avaliacoes=1)
    etapa = rascunho["stages"][1]
    etapa["weight"] = "1.0000"
    rascunho["profiles"][0]["classificationMilestones"] = [
        {
            "id": MARCO,
            "code": "FINAL",
            "name": "Classificação final",
            "stages": [etapa["id"]],
            "orderProduction": "POR_PONTUACAO",
            "operation": "SOMA_PONDERADA",
            "normalization": "NENHUMA",
            "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
            "tiebreakers": [],
        }
    ]
    return publish_original(api_client, manager_headers, process_payload, draft=rascunho)


def _consulta(edital):
    return reverse("interface:ordenacao", args=[edital.id, MARCO])


def _emissao(edital):
    return reverse("interface:emitir-ordenacao", args=[edital.id, MARCO])


@pytest.mark.parametrize(("subject", "papeis"), [("gestora", ["gestor"]), ("iris", ["auditor"])])
def test_gestao_e_auditoria_consultam(client, seletor_ligado, edital_com_marco, subject, papeis):
    identificar(client, subject, papeis)
    assert client.get(_consulta(edital_com_marco)).status_code == 200


def test_auditoria_consulta_e_nao_emite(client, seletor_ligado, edital_com_marco):
    identificar(client, "iris", ["auditor"])
    assert client.get(_consulta(edital_com_marco)).status_code == 200
    # Emitir chama a porta com `somente_gestao=True`, e ali a capacidade de auditoria **não** é
    # base aceita: a recusa é sobre o ator, e passou a dizê-lo (033).
    assert (
        client.post(_emissao(edital_com_marco), {"chave_idempotencia": "auditor"}).status_code
        == 403
    )
    assert AtoDeOrdenacao.objects.count() == 0


def test_sem_base_recebe_a_recusa_explicada(client, seletor_ligado, edital_com_marco):
    """O nome mudou porque ele afirmava a doutrina antiga (033).

    Era `test_sem_base_recebe_404_uniforme`. O ator é do **mesmo** escopo e não tem base nenhuma;
    a recusa é sobre ele, e dizer "não encontrado" fazia a tela mentir. As duas asserções de que
    ele não entra, e a de que nenhum ato nasceu, são as mesmas.
    """
    identificar(client, "estranho", [])
    assert client.get(_consulta(edital_com_marco)).status_code == 403
    assert (
        client.post(_emissao(edital_com_marco), {"chave_idempotencia": "intruso"}).status_code
        == 403
    )
    assert AtoDeOrdenacao.objects.count() == 0


def test_outro_escopo_recebe_404_uniforme(client, seletor_ligado, edital_com_marco):
    identificar(client, "gestora", ["gestor"], escopo="outra-unidade")
    assert client.get(_consulta(edital_com_marco)).status_code == 404
    assert (
        client.post(_emissao(edital_com_marco), {"chave_idempotencia": "fora"}).status_code == 404
    )
    assert AtoDeOrdenacao.objects.count() == 0


def test_o_formulario_nao_aceita_a_ordem_do_navegador(client, seletor_ligado, edital_com_marco):
    identificar(client, "gestora", ["gestor"])
    corpo = client.get(_consulta(edital_com_marco)).content.decode()
    assert 'name="chave_idempotencia"' in corpo
    for campo in ("posicao", "pontuacao", "desempate", "ordem"):
        assert f'name="{campo}"' not in corpo
    assert str(PROFILE_ID) not in corpo or "profile_id" not in corpo


def test_fato_usado_no_desempate_so_aparece_para_gestao_e_auditoria(
    client,
    seletor_ligado,
    edital_com_marco,
):
    from django.utils import timezone

    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

    inscricao = inscrever(edital_com_marco, 1, primeiro=990)[0]
    versao = VersaoConsolidada.objects.filter(edital=edital_com_marco).latest("materialized_at")
    ato = AtoDeOrdenacao.objects.create(
        edital=edital_com_marco,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        versao=versao,
        universo={
            "processoId": str(edital_com_marco.processo_id),
            "editalId": str(edital_com_marco.id),
            "profileId": str(PROFILE_ID),
            "milestoneId": MARCO,
            "versionId": str(versao.id),
            "participants": [str(inscricao.id)],
            "stageResults": [],
        },
        emitido_por="gestora",
        emitido_em=timezone.now(),
    )
    segredo = 137
    PosicaoNaOrdem.objects.create(
        ato=ato,
        inscricao=inscricao,
        posicao=1,
        pontuacao_combinada=80,
        consequencia="HABILITADA",
        desempate=[
            {
                "criterionId": "00000000-0000-4000-8000-000000000498",
                "order": 1,
                "type": "MAIOR_VALOR_DE_FATO",
                "value": segredo,
                "separated": True,
            }
        ],
    )
    url = reverse("interface:ato-de-ordenacao", args=[edital_com_marco.id, MARCO, ato.id])

    identificar(client, "iris", ["auditor"])
    autorizada = client.get(url)
    assert autorizada.status_code == 200
    assert str(segredo) in autorizada.content.decode()
    assert "private" in autorizada.headers["Cache-Control"]

    identificar(client, inscricao.identity_subject, [])
    negada = client.get(url)
    # O status mudou; **o que não vaza continua não vazando**, e é essa a asserção que importa
    # aqui. Uma recusa explicada que entregasse o valor de desempate junto seria pior do que o 404
    # mudo que ela substituiu (033).
    assert negada.status_code == 403
    assert str(segredo) not in negada.content.decode()
