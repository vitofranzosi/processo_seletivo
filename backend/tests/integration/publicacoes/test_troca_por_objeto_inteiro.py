"""O objeto inteiro não troca o campo que não se retifica (RC-130; A-6 da `048`; DP-13).

A gramática recusa o campo não retificável endereçado sozinho — `REPLACE .../cutRule/targetKind` —,
e aceitava o `REPLACE` do objeto que o contém: a regra de corte inteira, o critério inteiro, o
Perfil inteiro. Pela API, uma Retificação trocava assim a espécie do alvo, a Etapa governada e a
continuação de um corte, o tipo de um critério e a espécie do cadastro reserva, contra o contrato
da `026`. A `DP-13` decidiu a regra: na Retificação a substituição é campo a campo, e nunca a troca
do objeto inteiro.

A tela não usa essa porta — ela só monta o objeto inteiro quando ele está ausente, e nascer não é
trocar. Por isso o caso é da API, e é por ela que ele se prova.
"""

import copy
from unittest import mock

import pytest

from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.publicacao import create_retification, publish_original, publish_retification
from tests.fixtures.snapshot import CRITERIO, ETAPA, MARCO, PERFIL, rascunho_completo

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

PRINCIPAL = f"/profiles/id={PERFIL['A']}"
DO_MARCO = f"{PRINCIPAL}/classificationMilestones/id={MARCO}"
CORTE = f"{DO_MARCO}/cutRule"
CRITERIO_DE_FATO = f"{DO_MARCO}/tiebreakers/id={CRITERIO['FATO']}"
CRITERIO_DE_ETAPA = f"{DO_MARCO}/tiebreakers/id={CRITERIO['ETAPA']}"


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    return publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_completo(), anexos=1
    )


def _vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at").content


def _perfil(conteudo):
    return next(p for p in conteudo["profiles"] if p["id"] == PERFIL["A"])


def _marco(conteudo):
    return _perfil(conteudo)["classificationMilestones"][0]


def _criterio(conteudo, identidade):
    return next(c for c in _marco(conteudo)["tiebreakers"] if c["id"] == identidade)


def _com(objeto, **campos):
    return {**copy.deepcopy(objeto), **campos}


# Cada troca é o objeto publicado com **um** campo não retificável diferente, e todo o resto igual:
# é o `REPLACE` que a tela nunca emite e que a API aceitava. O campo nomeado é o que a recusa tem de
# nomear, porque é ele que quem retifica precisa deixar como estava.
TROCAS = {
    "a espécie do alvo do corte": (
        CORTE,
        lambda c: _com(_marco(c)["cutRule"], targetKind="FROM_VACANCY_TABLE", targetCount=None),
        f"{CORTE}/targetKind",
    ),
    "a Etapa governada do corte": (
        CORTE,
        lambda c: _com(_marco(c)["cutRule"], governedStage=ETAPA["B"]),
        f"{CORTE}/governedStage",
    ),
    "a continuação do corte": (
        CORTE,
        lambda c: _com(_marco(c)["cutRule"], continuation="NONE"),
        f"{CORTE}/continuation",
    ),
    "o tipo do critério": (
        CRITERIO_DE_FATO,
        lambda c: _com(_criterio(c, CRITERIO["FATO"]), type="MENOR_VALOR_DE_FATO"),
        f"{CRITERIO_DE_FATO}/type",
    ),
    "a Etapa que o critério compara, pelo objeto dos parâmetros": (
        f"{CRITERIO_DE_ETAPA}/parameters",
        lambda c: {"stageId": ETAPA["B"]},
        f"{CRITERIO_DE_ETAPA}/parameters/stageId",
    ),
    "a espécie do cadastro reserva": (
        PRINCIPAL,
        lambda c: _com(_perfil(c), reserveType="UNLIMITED"),
        f"{PRINCIPAL}/reserveType",
    ),
}


@pytest.mark.parametrize("troca", TROCAS.values(), ids=TROCAS.keys())
def test_o_objeto_inteiro_nao_troca_campo_que_nao_se_retifica(api_client, edital, troca):
    caminho, novo, campo = troca
    antes = _vigente(edital)

    recusa = create_retification(
        api_client,
        edital,
        [{"targetPath": caminho, "operation": "REPLACE", "newValue": novo(antes)}],
        esperar=422,
    )

    assert recusa["code"] == "invalid_change"
    # O que, por quê e o que fazer (FR-801 da `048`): o campo e os dois valores, a razão escrita no
    # contrato e o caminho que continua aberto.
    assert campo in recusa["detail"]
    assert "não altera no lugar" in recusa["detail"]
    assert "cada um pelo próprio caminho" in recusa["detail"]
    assert _vigente(edital) == antes, "nada foi retificado"


def test_a_recusa_diz_a_razao_do_contrato(api_client, edital):
    """A razão vem do contrato, campo a campo, e não de uma frase fixa desta guarda."""
    antes = _vigente(edital)

    recusa = create_retification(
        api_client,
        edital,
        [{"targetPath": CORTE, "operation": "REPLACE", "newValue": TROCAS[
            "a Etapa governada do corte"
        ][1](antes)}],
        esperar=422,
    )

    assert "decide quem progride no certame" in recusa["detail"]
    assert '"NONE"' in recusa["detail"] and f'"{ETAPA["B"]}"' in recusa["detail"]


def test_remover_e_acrescentar_no_mesmo_ato_e_a_mesma_troca(api_client, edital):
    """A guarda compara o antes e o depois do ato, e não cada alteração.

    `REMOVE` do critério seguido de `ADD` com a mesma identidade faria o segundo parecer
    acréscimo; o resultado, porém, é o mesmo critério com outro tipo.
    """
    antes = _vigente(edital)
    trocado = _com(_criterio(antes, CRITERIO["FATO"]), type="MENOR_VALOR_DE_FATO")

    recusa = create_retification(
        api_client,
        edital,
        [
            {"targetPath": CRITERIO_DE_FATO, "operation": "REMOVE"},
            {"targetPath": f"{DO_MARCO}/tiebreakers/-", "operation": "ADD", "newValue": trocado},
        ],
        esperar=422,
    )

    assert f"{CRITERIO_DE_FATO}/type" in recusa["detail"]
    assert _vigente(edital) == antes


def test_o_objeto_inteiro_continua_corrigindo_o_que_se_retifica(api_client, edital):
    """Campo a campo, e não objeto proibido: a quantidade do alvo fixo é parâmetro, e se corrige.

    A guarda não fecha o `REPLACE` do objeto — fecha a troca do campo que o contrato exclui. O
    mesmo objeto, com só campos retificáveis diferentes, continua publicando.
    """
    antes = _vigente(edital)
    corrigido = _com(_marco(antes)["cutRule"], targetCount=5, surplusCount=2)

    publish_retification(
        api_client,
        create_retification(
            api_client,
            edital,
            [{"targetPath": CORTE, "operation": "REPLACE", "newValue": corrigido}],
        ),
    )

    assert _marco(_vigente(edital))["cutRule"] == corrigido


def test_um_ato_anterior_a_guarda_nao_impede_a_retificacao_seguinte(api_client, edital):
    """A guarda está no ato, e não no motor que reproduz atos publicados (R-1 da `048`).

    O primeiro ato é publicado com a guarda neutralizada — é o Edital que alguém retificou pela API
    antes do RC-130. O segundo é uma Retificação legítima de outro campo, e publicá-lo materializa
    de novo as versões, reproduzindo o primeiro: se a guarda morasse em `apply_changes`, a própria
    história recusaria toda Retificação futura deste Edital.
    """
    trocado = _com(_marco(_vigente(edital))["cutRule"], continuation="NONE")
    with mock.patch(
        "processo_seletivo.publicacoes.application.retificacoes."
        "recusar_troca_de_campo_nao_retificavel"
    ):
        publish_retification(
            api_client,
            create_retification(
                api_client,
                edital,
                [{"targetPath": CORTE, "operation": "REPLACE", "newValue": trocado}],
                suffix="antiga",
            ),
            suffix="antiga",
        )
    assert _marco(_vigente(edital))["cutRule"]["continuation"] == "NONE"

    publish_retification(
        api_client,
        create_retification(
            api_client,
            edital,
            [{"targetPath": "/title", "operation": "REPLACE", "newValue": "Título corrigido"}],
            suffix="nova",
        ),
        suffix="nova",
    )

    assert _vigente(edital)["title"] == "Título corrigido"
    assert _marco(_vigente(edital))["cutRule"]["continuation"] == "NONE"
