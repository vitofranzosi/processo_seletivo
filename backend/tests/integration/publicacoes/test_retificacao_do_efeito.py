"""A Retificação do efeito não muda a regra no meio do caminho (164, US5).

O efeito se retifica até o primeiro Resultado desfavorável da Etapa, e não depois — ainda que todos
tenham sido superados por recurso (FR-7020, D-008). O que não muda o efeito, como ampliar o alcance,
passa (FR-7021). A recusa roda na elaboração **e** na publicação (FR-7022).
"""

import pytest

from processo_seletivo.resultados.application.consolidacao import consolidar
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
from tests.fixtures.recursos import admitir, decidir, interpor, superar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

RECUSA = "stage_effect_changed_after_unfavorable"


def _montar(gestor, api_client, manager_headers, *, seed):
    cenario = montar_com_alcance(gestor, api_client, manager_headers, seed=seed, codigo=str(seed))
    cenario["inscricoes"] = inscrever(
        cenario["edital"],
        3,
        primeiro=1,
        modalidades={0: MODALIDADE_PPI, 1: MODALIDADE_PCD},
        perfil=cenario["perfil"],
    )
    return cenario


def _consolidar(cenario, etapa, inscricoes, *, chave):
    return consolidar(
        actor=ator_institucional("maria"),
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=etapa,
        inscricao_ids=[i.id for i in inscricoes],
        idempotency_key=chave,
        correlation_id="teste",
    )


def _desfavoravel_na_hetero(cenario, gestor, *, seed):
    """A PPI passa pela Análise e é retirada na Heteroidentificação."""
    ppi = cenario["inscricoes"][0]
    distribuir_para(cenario, gestor, ["joao"], [ppi], chave=f"analise-{seed}")
    concluir_como(cenario, "joao", ppi, pontuacao="80")
    _consolidar(cenario, cenario["analise"], [ppi], chave=f"consolidar-analise-{seed}")
    na_hetero = {**cenario, "etapa": cenario["hetero"]}
    distribuir_para(na_hetero, gestor, ["joao"], [ppi], chave=f"hetero-{seed}")
    concluir_como(na_hetero, "joao", ppi, sentido="DESFAVORAVEL")
    _consolidar(cenario, cenario["hetero"], [ppi], chave=f"consolidar-hetero-{seed}")
    return ResultadoEtapa.vigentes.get(etapa_id=cenario["hetero"], inscricao=ppi)


def _efeito(cenario, valor, campo="unfavorableOutcomeEffect"):
    return [
        {
            "targetPath": f"/stages/id={cenario['hetero']}/{campo}",
            "operation": "REPLACE",
            "newValue": valor,
        }
    ]


def test_sem_desfavoravel_o_efeito_se_retifica(gestor, api_client, manager_headers):
    """FR-7020, cenário 1 da US5: a cláusula diz "elimina", e a composição dizia "retira"."""
    cenario = _montar(gestor, api_client, manager_headers, seed=1661)

    publish_retification(
        api_client,
        create_retification(api_client, cenario["edital"], _efeito(cenario, "ELIMINATION")),
    )


def test_com_desfavoravel_o_efeito_nao_se_retifica(gestor, api_client, manager_headers):
    """FR-7020, cenário 2: a recusa diz a Etapa e quantos desfavoráveis ela já registrou."""
    cenario = _montar(gestor, api_client, manager_headers, seed=1662)
    _desfavoravel_na_hetero(cenario, gestor, seed=1662)

    resposta = create_retification(
        api_client, cenario["edital"], _efeito(cenario, "ELIMINATION"), esperar=422
    )

    assert resposta["code"] == RECUSA
    assert "1 resultado desfavorável" in resposta["detail"]


def test_o_efeito_da_ausencia_tambem_se_trava(gestor, api_client, manager_headers):
    """FR-7020: a troca do efeito do não comparecimento é mudança de efeito também."""
    cenario = _montar(gestor, api_client, manager_headers, seed=1663)
    _desfavoravel_na_hetero(cenario, gestor, seed=1663)

    resposta = create_retification(
        api_client,
        cenario["edital"],
        _efeito(cenario, "ELIMINATION", campo="absenceEffect"),
        esperar=422,
    )

    assert resposta["code"] == RECUSA


def test_o_desfavoravel_superado_continua_travando(gestor, api_client, manager_headers):
    """FR-7020, SC-2334, D-008: o impedimento é histórico — o recurso deferido não o levanta."""
    cenario = _montar(gestor, api_client, manager_headers, seed=1664)
    retirada = _desfavoravel_na_hetero(cenario, gestor, seed=1664)
    recurso = interpor(inscricao=retirada.inscricao, versao=retirada.versao, resultado=retirada)
    admitir(recurso)
    decisao = decidir(
        recurso,
        protegido=retirada,
        consequencia=ResultadoEtapa.Consequencia.HABILITADA,
        forma="DECISORIA",
        sentido="FAVORAVEL",
    )
    superar(retirada, decisao, consequencia=ResultadoEtapa.Consequencia.HABILITADA)
    assert not ResultadoEtapa.vigentes.filter(
        etapa_id=cenario["hetero"], consequencia=ResultadoEtapa.Consequencia.RETIRADA_DA_RESERVA
    ).exists()

    resposta = create_retification(
        api_client, cenario["edital"], _efeito(cenario, "ELIMINATION"), esperar=422
    )

    assert resposta["code"] == RECUSA


def test_a_retificacao_elaborada_antes_e_recusada_na_publicacao(
    gestor, api_client, manager_headers
):
    """FR-7022, cenário 4: a consolidação entra entre elaborar e publicar, e prevalece."""
    cenario = _montar(gestor, api_client, manager_headers, seed=1665)
    retificacao = create_retification(
        api_client, cenario["edital"], _efeito(cenario, "ELIMINATION")
    )
    retirada = _desfavoravel_na_hetero(cenario, gestor, seed=1665)

    resposta = try_publish_retification(api_client, retificacao)

    assert resposta.status_code == 422, resposta.content
    assert resposta.json()["code"] == RECUSA
    assert retirada.consequencia == ResultadoEtapa.Consequencia.RETIRADA_DA_RESERVA


def test_ampliar_o_alcance_nao_muda_o_efeito(gestor, api_client, manager_headers):
    """FR-7021: acrescentar PCD ao alcance passa, com desfavorável registrado."""
    cenario = _montar(gestor, api_client, manager_headers, seed=1666)
    _desfavoravel_na_hetero(cenario, gestor, seed=1666)

    publish_retification(
        api_client,
        create_retification(
            api_client,
            cenario["edital"],
            [
                {
                    "targetPath": f"/stages/id={cenario['hetero']}/modalityCodes",
                    "operation": "REPLACE",
                    "newValue": ["PCD", "PPI"],
                }
            ],
        ),
    )
