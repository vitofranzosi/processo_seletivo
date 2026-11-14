"""A Retificação muda o alcance sem desfazer o que já foi avaliado (163, US5).

Ampliar passa e acrescenta pendentes (FR-6979). Estreitar é recusado enquanto alguma inscrição que
sairia tiver Atribuição ou Resultado na Etapa (FR-6980) — a decisão do usuário no clarify de 13/11.
A recusa roda na elaboração **e** na publicação: entre uma e outra, o mundo muda.
"""

import pytest

from processo_seletivo.avaliacoes.models import Atribuicao
from processo_seletivo.resultados.application.prontidao import participacao
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.conftest import ator_institucional
from tests.fixtures.alcance import MODALIDADE_PCD, MODALIDADE_PPI, montar_com_alcance
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para
from tests.fixtures.publicacao import (
    create_retification,
    publish_retification,
    try_publish_retification,
)

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

# 0 PPI, 1 PCD, 2 sem Modalidade.
MODALIDADES = {0: MODALIDADE_PPI, 1: MODALIDADE_PCD}


def _montar(gestor, api_client, manager_headers, *, seed, alcance=("PPI",)):
    cenario = montar_com_alcance(
        gestor, api_client, manager_headers, seed=seed, codigo=str(seed), alcance=alcance
    )
    cenario["inscricoes"] = inscrever(
        cenario["edital"], 3, primeiro=1, modalidades=MODALIDADES, perfil=cenario["perfil"]
    )
    return cenario


def _alcance(cenario, codigos):
    return [
        {
            "targetPath": f"/stages/id={cenario['hetero']}/modalityCodes",
            "operation": "REPLACE",
            "newValue": codigos,
        }
    ]


def _participantes_da_hetero(cenario):
    participantes, _, _ = participacao(edital=cenario["edital"], etapa_id=cenario["hetero"])
    return participantes


def _atribuir_na_hetero(cenario, gestor, inscricoes, *, chave):
    distribuir_para(
        {**cenario, "etapa": cenario["hetero"]}, gestor, ["joao"], inscricoes, chave=chave
    )


def test_ampliar_passa_e_acrescenta_pendentes(gestor, api_client, manager_headers):
    """FR-6979, FR-6970: a PCD passa a participar a partir da publicação, e não antes."""
    cenario = _montar(gestor, api_client, manager_headers, seed=1641)
    ppi, pcd, _ampla = cenario["inscricoes"]
    retificacao = create_retification(
        api_client, cenario["edital"], _alcance(cenario, ["PCD", "PPI"])
    )

    assert _participantes_da_hetero(cenario) == {ppi.id}

    publish_retification(api_client, retificacao)

    assert _participantes_da_hetero(cenario) == {ppi.id, pcd.id}


def test_ampliar_depois_de_consolidar_nao_muda_o_resultado_feito(
    gestor, api_client, manager_headers
):
    """FR-6981: o Resultado consolidado sob a versão anterior continua o mesmo."""
    from processo_seletivo.resultados.application.consolidacao import consolidar

    cenario = _montar(gestor, api_client, manager_headers, seed=1642)
    ppi = cenario["inscricoes"][0]
    na_hetero = {**cenario, "etapa": cenario["hetero"]}
    distribuir_para(na_hetero, gestor, ["joao"], [ppi], chave="hetero-1642")
    concluir_como(na_hetero, "joao", ppi, sentido="FAVORAVEL")
    consolidar(
        actor=ator_institucional("maria"),
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["hetero"],
        inscricao_ids=[ppi.id],
        idempotency_key="consolidar-1642",
        correlation_id="teste",
    )
    antes = ResultadoEtapa.objects.get(etapa_id=cenario["hetero"], inscricao=ppi)

    publish_retification(
        api_client,
        create_retification(api_client, cenario["edital"], _alcance(cenario, None)),
    )

    depois = ResultadoEtapa.vigentes.get(etapa_id=cenario["hetero"], inscricao=ppi)
    assert depois.pk == antes.pk
    assert len(_participantes_da_hetero(cenario)) == 3


def test_estreitar_sem_atribuicao_passa(gestor, api_client, manager_headers):
    """Trocar PPI por PCD antes de qualquer trabalho na Etapa é correção de composição."""
    cenario = _montar(gestor, api_client, manager_headers, seed=1643)
    _ppi, pcd, _ampla = cenario["inscricoes"]

    publish_retification(
        api_client,
        create_retification(api_client, cenario["edital"], _alcance(cenario, ["PCD"])),
    )

    assert _participantes_da_hetero(cenario) == {pcd.id}


def test_estreitar_sobre_atribuicao_e_recusado_na_elaboracao(gestor, api_client, manager_headers):
    """FR-6980, SC-2313: a recusa nomeia a Etapa, o código e quantas inscrições impedem."""
    cenario = _montar(gestor, api_client, manager_headers, seed=1644)
    ppi = cenario["inscricoes"][0]
    _atribuir_na_hetero(cenario, gestor, [ppi], chave="hetero-1644")
    atribuicoes = Atribuicao.objects.filter(etapa_id=cenario["hetero"]).count()

    recusa = create_retification(
        api_client, cenario["edital"], _alcance(cenario, ["PCD"]), esperar=422
    )

    assert recusa["code"] == "stage_scope_narrowed_over_assigned"
    assert "«Heteroidentificação»" in recusa["detail"]
    assert "«PPI»" in recusa["detail"]
    assert "1 inscrição dessas Modalidades já tem" in recusa["detail"]
    assert Atribuicao.objects.filter(etapa_id=cenario["hetero"]).count() == atribuicoes


def test_restringir_a_etapa_para_todas_e_estreitar(gestor, api_client, manager_headers):
    """A Etapa que alcançava todas e já tem a ampla atribuída não passa a só PPI."""
    cenario = _montar(gestor, api_client, manager_headers, seed=1645, alcance=None)
    ampla = cenario["inscricoes"][2]
    _atribuir_na_hetero(cenario, gestor, [ampla], chave="hetero-1645")

    recusa = create_retification(
        api_client, cenario["edital"], _alcance(cenario, ["PPI"]), esperar=422
    )

    assert recusa["code"] == "stage_scope_narrowed_over_assigned"


def test_devolver_a_etapa_a_todas_passa(gestor, api_client, manager_headers):
    cenario = _montar(gestor, api_client, manager_headers, seed=1646)
    _atribuir_na_hetero(cenario, gestor, [cenario["inscricoes"][0]], chave="hetero-1646")

    publish_retification(
        api_client,
        create_retification(api_client, cenario["edital"], _alcance(cenario, None)),
    )

    assert len(_participantes_da_hetero(cenario)) == 3


def test_atribuicao_feita_depois_da_elaboracao_recusa_a_publicacao(
    gestor, api_client, manager_headers
):
    """Cenário 6 da US5: entre elaborar e publicar, alguém atribuiu. Prevalece a Atribuição."""
    cenario = _montar(gestor, api_client, manager_headers, seed=1647)
    retificacao = create_retification(api_client, cenario["edital"], _alcance(cenario, ["PCD"]))
    _atribuir_na_hetero(cenario, gestor, [cenario["inscricoes"][0]], chave="hetero-1647")

    resposta = try_publish_retification(api_client, retificacao)

    assert resposta.status_code == 422, resposta.content
    assert resposta.json()["code"] == "stage_scope_narrowed_over_assigned"
    assert _participantes_da_hetero(cenario) == {cenario["inscricoes"][0].id}
