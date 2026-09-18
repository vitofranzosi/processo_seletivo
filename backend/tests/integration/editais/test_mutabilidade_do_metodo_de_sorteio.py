"""Retificar o método não alcança relação congelada nem sorteio realizado (026, US4, FR-309).

**A garantia já é estrutural, e este arquivo a declara.** `RelacaoDeHabilitados.metodo_hash` grava
o método no instante do congelamento, e `Sorteio.metodo_hash` o copia e o confere na constituição:
a relação congelada **não relê** o método vigente, ela carrega o seu. Foi por isso que o canário 4
custou campos na tela e um teste de fronteira, e não trabalho de domínio.

O teste declara a fronteira; ele não a constrói. Se um dia alguém fizer o sorteio reler o conteúdo
vigente, é aqui que a suíte cai — e é essa a razão de o arquivo existir.
"""

import pytest

from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.sorteios.models import RelacaoDeHabilitados
from tests.fixtures.publicacao import retify
from tests.fixtures.sorteio import certame_de_sorteio

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload):
    return certame_de_sorteio(gestor, api_client, manager_headers, process_payload)


def _caminho_do_metodo(conteudo, sufixo):
    perfil = next(p for p in conteudo["profiles"] if p.get("classificationMilestones"))
    marco = perfil["classificationMilestones"][0]
    return (
        f"/profiles/id={perfil['id']}/classificationMilestones/id={marco['id']}/drawMethod/{sufixo}"
    )


def test_a_relacao_congelada_carrega_o_metodo_e_nao_o_rele(api_client, certame):
    """A fronteira, medida: o resumo gravado no congelamento não muda quando o método muda."""
    from processo_seletivo.sorteios.application.relacao import publicar_relacao
    from tests.fixtures.sorteio import presidente

    edital = certame["edital"]
    publicar_relacao(
        actor=presidente(),
        processo_id=certame["processo"].id,
        edital_id=edital.id,
        perfil_id=certame["perfil"],
        marco_id=certame["marco"],
        lista_id=None,
        idempotency_key="relacao-mutabilidade-0001",
        correlation_id="teste-026",
    )
    congelada = RelacaoDeHabilitados.objects.get(edital_id=edital.id)
    congelado = congelada.metodo_hash
    assert congelado, "a relação congelada grava o resumo do método que ela comprometeu"

    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    retify(
        api_client,
        edital,
        [
            {
                "operation": "REPLACE",
                "targetPath": _caminho_do_metodo(vigente.content, "derivation"),
                "newValue": "Outra prosa sobre como a ocorrência foi escolhida.",
            }
        ],
        suffix="metodo",
    )

    congelada.refresh_from_db()
    assert congelada.metodo_hash == congelado, (
        "a Retificação alcançou o método comprometido por uma relação já congelada — ela vale "
        "para o que vier, e não para o que já foi"
    )


def test_o_metodo_vigente_passa_a_ser_o_novo_para_o_que_vier(api_client, certame):
    """A outra metade: a correção vale, e vale para a relação seguinte."""
    edital = certame["edital"]
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    caminho = _caminho_do_metodo(vigente.content, "occurrence")

    retify(
        api_client,
        edital,
        [{"operation": "REPLACE", "targetPath": caminho, "newValue": "5999"}],
        suffix="ocorrencia",
    )

    depois = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    perfil = next(p for p in depois.content["profiles"] if p.get("classificationMilestones"))
    metodo = perfil["classificationMilestones"][0]["drawMethod"]
    assert metodo["occurrence"] == "5999"
    assert metodo["algorithm"] == "IFES-SORTEIO-SHA256-v1", "o resto do método atravessa intacto"


def test_metodo_declarado_pela_metade_e_recusado_na_retificacao(api_client, certame):
    """Mesma lacuna da janela recursal, pelo mesmo caminho.

    `validate_classification_milestones` cobra o método completo na elaboração, e a publicação
    nunca o conferia: uma Retificação podia esvaziar a regra de substituição e publicar — e no dia
    da indisponibilidade a escolha da ocorrência voltaria para a mesa, que é o que a `021` proíbe.
    """
    from tests.fixtures.publicacao import create_retification

    edital = certame["edital"]
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")

    problema = create_retification(
        api_client,
        edital,
        [
            {
                "operation": "REPLACE",
                "targetPath": _caminho_do_metodo(vigente.content, "substitutionRule"),
                "newValue": None,
            }
        ],
        esperar=422,
        suffix="metade",
    )
    assert "substitutionRule" in problema["detail"] or "substituição" in problema["detail"]


def test_fonte_que_o_sistema_nao_consulta_e_recusada_na_retificacao(api_client, certame):
    """Declarar uma fonte que o sistema não consulta faria o manifesto publicar uma origem que a
    semente não teve — e quem reimplementasse chegaria a outra ordem."""
    from tests.fixtures.publicacao import create_retification

    edital = certame["edital"]
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")

    problema = create_retification(
        api_client,
        edital,
        [
            {
                "operation": "REPLACE",
                "targetPath": _caminho_do_metodo(vigente.content, "source"),
                "newValue": "Random.org",
            }
        ],
        esperar=422,
        suffix="fonte",
    )
    assert "Random.org" in problema["detail"]


# --- O método comum do Edital, retificável pelo endereçamento novo (030, FR-429) -------------


def _publicado_com_metodo_comum(api_client, manager_headers, process_payload):
    """Um Edital publicado com o método comum declarado, e um marco que o referencia."""
    import copy

    from tests.fixtures.publicacao import publish_original
    from tests.fixtures.snapshot import PERFIL, rascunho_completo

    rascunho = copy.deepcopy(rascunho_completo())
    perfil = next(item for item in rascunho["profiles"] if item["id"] == PERFIL["A"])
    perfil["classificationMilestones"][0]["drawMethod"] = None
    return publish_original(api_client, manager_headers, process_payload, draft=rascunho, anexos=1)


def test_o_metodo_comum_se_retifica_pelo_caminho_da_raiz(
    api_client, manager_headers, process_payload
):
    """FR-429 e o contrato: as nove entradas `(raiz, "drawMethod/…")` são alcançáveis.

    **Da raiz, e não do Perfil**: o método comum é do Edital, e `/drawMethod/occurrence` já resolve
    — é objeto, e em objeto o segmento do caminho é nome de chave literal, que é a mesma gramática
    que as dez entradas do marco usam desde a `026`.
    """
    edital = _publicado_com_metodo_comum(api_client, manager_headers, process_payload)

    retify(
        api_client,
        edital,
        [{"operation": "REPLACE", "targetPath": "/drawMethod/occurrence", "newValue": "6001"}],
        suffix="comum",
    )

    depois = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    assert depois.content["drawMethod"]["occurrence"] == "6001"
    assert depois.content["drawMethod"]["algorithm"] == "IFES-SORTEIO-SHA256-v1", (
        "o resto do método atravessa intacto"
    )


def test_a_retificacao_do_comum_alcanca_o_marco_que_o_referencia(
    api_client, manager_headers, process_payload
):
    """A consequência que torna a FR-429 útil: uma correção, e não sete.

    O marco não é tocado pela Retificação — ele continua sem método próprio —, e a resolução
    devolve o comum corrigido. É o oposto do estado anterior, em que a mesma correção teria de ser
    endereçada a cada um dos sete marcos, um por um.
    """
    from processo_seletivo.editais.domain import marcos
    from tests.fixtures.snapshot import MARCO, PERFIL

    edital = _publicado_com_metodo_comum(api_client, manager_headers, process_payload)

    retify(
        api_client,
        edital,
        [{"operation": "REPLACE", "targetPath": "/drawMethod/occurrence", "newValue": "6002"}],
        suffix="comum-alcanca",
    )

    depois = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    marco = depois.content["profiles"][0]["classificationMilestones"][0]

    assert marco["drawMethod"] is None, "o marco continua referenciando, e não copiando"
    assert (
        marcos.metodo_que_governa(depois.content, perfil_id=PERFIL["A"], marco_id=MARCO)[
            "occurrence"
        ]
        == "6002"
    )
