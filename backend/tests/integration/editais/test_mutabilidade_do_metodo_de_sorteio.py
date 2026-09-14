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
