"""A Retificação da regra não muda a decisão no meio do caminho (165, US6).

A regra e o número de avaliações se retificam até o primeiro Resultado por avaliação, favorável ou
desfavorável, vigente ou superado (FR-7073, D-008). A Etapa que o ato compõe ou recompõe como
colegiada precisa declarar a regra, e a do acervo, que o ato não toca, não trava nada (FR-7051).
"""

import pytest

from processo_seletivo.comissoes.domain.etapas import conteudo_vigente
from processo_seletivo.resultados.application.prontidao import PRONTA, panorama_da_etapa
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.deliberacao import (
    concluir_pareceres,
    consolidar_na,
    distribuir_na_hetero,
    montar_colegiada,
)
from tests.fixtures.publicacao import (
    create_retification,
    publish_retification,
    try_publish_retification,
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

F, D = "FAVORAVEL", "DESFAVORAVEL"


def _troca(cenario, campo, valor):
    return [
        {
            "targetPath": f"/stages/id={cenario['hetero']}/{campo}",
            "operation": "REPLACE",
            "newValue": valor,
        }
    ]


def _estado(cenario, inscricao):
    conteudo = conteudo_vigente(cenario["edital"])
    vigentes = {str(etapa["id"]): etapa for etapa in conteudo["stages"]}
    panorama = panorama_da_etapa(
        edital=cenario["edital"],
        etapa=vigentes[str(cenario["hetero"])],
        etapas_vigentes=vigentes,
        conteudo=conteudo,
    )
    return panorama["estados"][inscricao.id][0]


def _deliberar(cenario, gestor, inscricao, *, seed):
    distribuir_na_hetero(cenario, gestor, [inscricao], chave=f"hetero-{seed}")
    concluir_pareceres(cenario, inscricao, {"ana": D, "bruno": D, "carla": F})
    consolidar_na(cenario, cenario["hetero"], [inscricao], chave=f"consolidar-{seed}")


def test_a_regra_se_retifica_antes_do_primeiro_resultado(gestor, api_client, manager_headers):
    """FR-7073, cenário 1 da US6: os pareceres concluídos continuam, e a regra nova se aplica."""
    cenario = montar_colegiada(gestor, api_client, manager_headers, seed=1691)
    maria = cenario["inscricoes"][0]
    distribuir_na_hetero(cenario, gestor, [maria], chave="hetero-1691")
    concluir_pareceres(cenario, maria, {"ana": D, "bruno": D, "carla": F})

    publish_retification(
        api_client,
        create_retification(
            api_client,
            cenario["edital"],
            _troca(cenario, "deliberationRule", "UNANIMOUS_FOR_UNFAVORABLE"),
        ),
    )

    assert _estado(cenario, maria) == PRONTA
    consolidar_na(cenario, cenario["hetero"], [maria], chave="consolidar-1691")
    resultado = ResultadoEtapa.vigentes.get(etapa_id=cenario["hetero"], inscricao=maria)
    assert resultado.sentido == F
    assert resultado.regra_de_deliberacao == "UNANIMOUS_FOR_UNFAVORABLE"


@pytest.mark.parametrize(
    "campo, valor",
    [("deliberationRule", "UNANIMOUS_FOR_FAVORABLE"), ("evaluationsPerRegistration", 5)],
    ids=["regra", "número"],
)
def test_depois_do_primeiro_resultado_nao_se_retifica(
    gestor, api_client, manager_headers, campo, valor
):
    """FR-7073, SC-2354: a mensagem nomeia a Etapa e conta os Resultados."""
    seed = 1692 if campo == "deliberationRule" else 1693
    cenario = montar_colegiada(gestor, api_client, manager_headers, seed=seed)
    _deliberar(cenario, gestor, cenario["inscricoes"][0], seed=seed)

    resposta = create_retification(
        api_client, cenario["edital"], _troca(cenario, campo, valor), esperar=422
    )

    assert resposta["code"] == "stage_deliberation_changed_after_result"
    assert "Heteroidentificação" in resposta["detail"]
    assert "1 resultado por avaliação" in resposta["detail"]


def test_a_retificacao_elaborada_antes_e_recusada_na_publicacao(
    gestor, api_client, manager_headers
):
    """FR-7074, cenário 3: a consolidação entra entre elaborar e publicar, e prevalece."""
    cenario = montar_colegiada(gestor, api_client, manager_headers, seed=1694)
    retificacao = create_retification(
        api_client,
        cenario["edital"],
        _troca(cenario, "deliberationRule", "UNANIMOUS_FOR_FAVORABLE"),
    )
    _deliberar(cenario, gestor, cenario["inscricoes"][0], seed=1694)

    resposta = try_publish_retification(api_client, retificacao)

    assert resposta.status_code == 422, resposta.content
    assert resposta.json()["code"] == "stage_deliberation_changed_after_result"


def test_a_reducao_abaixo_das_conclusoes_e_recusada(gestor, api_client, manager_headers):
    """FR-7073: com três pareceres concluídos, a Etapa não cai para um."""
    cenario = montar_colegiada(
        gestor, api_client, manager_headers, seed=1695, regra="UNANIMOUS_FOR_FAVORABLE"
    )
    maria = cenario["inscricoes"][0]
    distribuir_na_hetero(cenario, gestor, [maria], chave="hetero-1695")
    concluir_pareceres(cenario, maria, {"ana": D, "bruno": D})

    resposta = create_retification(
        api_client,
        cenario["edital"],
        _troca(cenario, "evaluationsPerRegistration", 1)
        + _troca(cenario, "deliberationRule", None),
        esperar=422,
    )

    assert resposta["code"] == "stage_evaluations_below_concluded"
    assert "1 inscrição já tem mais pareceres concluídos" in resposta["detail"]


def test_a_colegiada_recomposta_sem_regra_e_recusada(gestor, api_client, manager_headers):
    """FR-7051: tirar a regra da Etapa colegiada é recompô-la sem regra."""
    cenario = montar_colegiada(gestor, api_client, manager_headers, seed=1696)

    resposta = create_retification(
        api_client, cenario["edital"], _troca(cenario, "deliberationRule", None), esperar=422
    )

    assert resposta["code"] == "stage_deliberation_without_rule"


@pytest.mark.django_db
def test_o_acervo_sem_regra_nao_trava_outra_correcao():
    """FR-7051, FR-7054, research T-003: a Etapa colegiada publicada antes do degrau 24, sem regra,
    não trava a Retificação que não a toca; a que a recompõe precisa da regra, e a que a declara
    passa. A publicação de hoje recusa a Etapa colegiada sem regra, e por isso o acervo se monta
    aqui, como conteúdo, e não por publicação."""
    from processo_seletivo.publicacoes.application.retificacoes import _recusar_colegiada_sem_regra
    from processo_seletivo.shared.api.problems import DomainError

    acervo = {
        "id": "hetero",
        "name": "Heteroidentificação",
        "forma": "DECISORIA",
        "evaluationsPerRegistration": 3,
        "deliberationRule": None,
    }
    base = {"stages": [acervo]}

    _recusar_colegiada_sem_regra(base, {"stages": [{**acervo, "name": "Hetero racial"}]})
    _recusar_colegiada_sem_regra(base, {"stages": [{**acervo, "deliberationRule": "MAJORITY"}]})
    with pytest.raises(DomainError) as recusa:
        _recusar_colegiada_sem_regra(
            base, {"stages": [{**acervo, "evaluationsPerRegistration": 5}]}
        )
    assert recusa.value.code == "stage_deliberation_without_rule"


def test_a_reducao_na_etapa_pontuada_nao_e_recusada():
    """FR-7073, revisão de código: a recusa da redução é só da Etapa decisória."""
    from processo_seletivo.publicacoes.application.retificacoes import (
        _recusar_reducao_abaixo_das_conclusoes,
    )

    prova = {"id": "prova", "name": "Prova", "forma": "PONTUADA", "evaluationsPerRegistration": 2}
    _recusar_reducao_abaixo_das_conclusoes(
        None, {"stages": [prova]}, {"stages": [{**prova, "evaluationsPerRegistration": 1}]}
    )


def test_gravar_um_explicito_onde_havia_nulo_nao_e_mudanca():
    """FR-7073, revisão de código: `null` e `1` são o mesmo número de avaliações."""
    from processo_seletivo.publicacoes.application.retificacoes import (
        _recusar_deliberacao_mudada_apos_resultado,
    )

    etapa = {"id": "hetero", "name": "Hetero", "forma": "DECISORIA", "deliberationRule": None}
    _recusar_deliberacao_mudada_apos_resultado(
        None,
        {"stages": [{**etapa, "evaluationsPerRegistration": None}]},
        {"stages": [{**etapa, "evaluationsPerRegistration": 1}]},
    )
