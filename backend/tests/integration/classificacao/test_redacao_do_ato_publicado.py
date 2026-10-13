"""O ato de ordenação já publicado mostra a redação dele (069, FR-1397, R-004).

A página do ato **reconstrói** a frase do desempate na hora de exibir — o ato guarda identificadores
e valores, e não texto. Sem a redação registrada, um ato emitido sobre uma versão publicada antes
da `069` passaria a dizer, na tela, uma frase que nunca publicou. A redação é a da `Publicacao` da
versão que o ato cita (`ato.versao.source_publication.redacao_do_documento`).

A proposta de ordenação não é ato publicado: descreve a versão vigente agora, na redação vigente.

Dois níveis: o fluxo real, com o critério de Etapa da fixture de divulgação; e o seletor, com o
critério de data, que é o caso do contrato (T1).
"""

from types import SimpleNamespace

import pytest
from django.urls import reverse

from processo_seletivo.classificacao.application.selectors import (
    estado_do_marco,
    nomear_criterios,
)
from processo_seletivo.publicacoes.application import publish_edital
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import REDACAO_1, REDACAO_2
from processo_seletivo.publicacoes.models import Publicacao
from tests.fixtures.divulgacao import montar_ato_publicavel
from tests.fixtures.edital import identificador
from tests.interface.conftest import identificar

SEED = 92
ETAPA_DO_MARCO = identificador(411, SEED)
CRITERIO = "00000000-0000-4000-8000-000000000492"
CRITERIOS = [
    {
        "id": CRITERIO,
        "order": 1,
        "type": "MAIOR_PONTUACAO_NA_ETAPA",
        "parameters": {"stageId": ETAPA_DO_MARCO},
        "whenMissing": "ULTIMO_NO_CRITERIO",
    }
]
REDACAO_1_DA_ETAPA = "maior pontuação na Etapa Prova didática"
REDACAO_2_DA_ETAPA = "maior pontuação na Etapa “Prova didática”"


def _cenario(gestor, api_client, manager_headers, process_payload, codigo):
    return montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=SEED,
        codigo=codigo,
        pontuacoes=("90.0000", "70.0000"),
        primeiro=1951,
        criterios=CRITERIOS,
    )


def _pagina_do_ato(client, cenario):
    identificar(client, "maria", ["gestor"])
    ato = cenario["ato"]
    url = reverse("interface:ato-de-ordenacao", args=[cenario["edital"].id, ato.marco_id, ato.id])
    corpo = client.get(url).content.decode()
    return corpo[corpo.index("Posições e valores de desempate") :]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_ato_sobre_versao_de_redacao_1_mostra_a_frase_que_publicou(
    client, seletor_ligado, gestor, api_client, manager_headers, process_payload, monkeypatch
):
    """O Edital publicado antes da `069`: a Publicação registra a redação 1, e o ato a mostra."""
    monkeypatch.setattr(publish_edital, "REDACAO_VIGENTE", REDACAO_1)
    cenario = _cenario(gestor, api_client, manager_headers, process_payload, "0792")
    monkeypatch.undo()
    assert Publicacao.objects.get(edital=cenario["edital"]).redacao_do_documento == REDACAO_1

    pagina = _pagina_do_ato(client, cenario)

    assert REDACAO_1_DA_ETAPA in pagina
    assert REDACAO_2_DA_ETAPA not in pagina


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_ato_sobre_versao_de_redacao_2_mostra_a_redacao_2(
    client, seletor_ligado, gestor, api_client, manager_headers, process_payload
):
    cenario = _cenario(gestor, api_client, manager_headers, process_payload, "0793")
    assert Publicacao.objects.get(edital=cenario["edital"]).redacao_do_documento == REDACAO_2

    pagina = _pagina_do_ato(client, cenario)

    assert REDACAO_2_DA_ETAPA in pagina
    assert REDACAO_1_DA_ETAPA not in pagina


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_proposta_de_ordenacao_usa_a_redacao_vigente(
    gestor, api_client, manager_headers, process_payload, monkeypatch
):
    """A proposta descreve a versão vigente agora: mesmo sobre Edital de redação 1, diz a 2."""
    monkeypatch.setattr(publish_edital, "REDACAO_VIGENTE", REDACAO_1)
    cenario = _cenario(gestor, api_client, manager_headers, process_payload, "0794")
    monkeypatch.undo()

    # A tela da proposta só lista os critérios quando um empate chega ao fim; a frase é a do
    # seletor que ela lê, sobre a versão vigente.
    estado = estado_do_marco(edital=cenario["edital"], marco_id=cenario["marco"])

    assert estado["criterios_do_desempate"] == [REDACAO_2_DA_ETAPA]


# ---------------------------------------------------------------------------
# O seletor, com o critério de data do contrato (T1)
# ---------------------------------------------------------------------------

NASCIMENTO = "00000000-0000-4000-8000-0000000004a1"
CONTEUDO = {
    "stages": [],
    "profiles": [
        {
            "id": "perfil",
            "declaredFacts": [
                {"id": NASCIMENTO, "code": "NASC", "type": "DATA", "label": "Data de nascimento"}
            ],
            "classificationMilestones": [
                {
                    "id": "marco",
                    "tiebreakers": [
                        {
                            "id": "c1",
                            "order": 1,
                            "type": "MENOR_VALOR_DE_FATO",
                            "parameters": {"factId": NASCIMENTO},
                            "whenMissing": "ULTIMO_NO_CRITERIO",
                        }
                    ],
                }
            ],
        }
    ],
}


def _ato(redacao):
    publicacao = SimpleNamespace(redacao_do_documento=redacao)
    versao = SimpleNamespace(content=CONTEUDO, source_publication=publicacao)
    return SimpleNamespace(versao=versao, perfil_id="perfil", marco_id="marco")


@pytest.mark.parametrize(
    ("redacao", "frase"),
    [
        (REDACAO_1, "menor valor declarado em Data de nascimento"),
        (REDACAO_2, "data de nascimento mais antiga, informada na inscrição"),
    ],
)
def test_o_seletor_nomeia_o_criterio_na_redacao_da_publicacao(redacao, frase):
    linhas = [SimpleNamespace(desempate=[{"criterionId": "c1"}])]

    (linha,) = nomear_criterios(linhas, _ato(redacao))

    assert linha.desempate[0]["rotulo"] == frase


def test_versao_sem_publicacao_de_origem_le_a_vigente():
    """Uma versão sem Publicação de origem não existe no fluxo; se existir, não quebra a página."""
    ato = _ato(REDACAO_2)
    ato.versao.source_publication = None
    linhas = [SimpleNamespace(desempate=[{"criterionId": "c1"}])]

    (linha,) = nomear_criterios(linhas, ato)

    assert linha.desempate[0]["rotulo"] == "data de nascimento mais antiga, informada na inscrição"
