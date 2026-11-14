"""A Etapa restrita não decide o que vale para todas as inscrições (163, FR-6986, FR-6987).

Duas leituras olhavam para "a Etapa" sem perguntar a quem ela se aplica:

- a **publicação das inscrições** (148) escolhe a análise entre as Etapas decisórias e
  eliminatórias — e a Heteroidentificação é uma delas. Escolhida, a ampla ficaria pendente para
  sempre, e a homologação nunca sairia;
- o **reingresso pendente** cobra Resultado de quem foi reabilitado por recurso em toda Etapa que o
  marco enumera — e a ampla nunca terá Resultado na Heteroidentificação.
"""

import pytest

from processo_seletivo.divulgacao.domain import inscricoes as dominio
from processo_seletivo.divulgacao.domain.publicabilidade import reingressos_pendentes
from processo_seletivo.publicacoes.application.selectors import effective_version
from tests.fixtures.alcance import MODALIDADE_PPI, montar_com_alcance
from tests.fixtures.comissao import inscrever

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def _etapa(identificador, *, alcance=None, ordem=1):
    return {
        "id": identificador,
        "order": ordem,
        "forma": "DECISORIA",
        "eliminatory": True,
        "modalityCodes": alcance,
    }


def test_a_restrita_nao_e_candidata_a_analise_das_inscricoes():
    """FR-6987: com uma análise para todas e uma restrita, a escolha automática continua a mesma."""
    conteudo = {"stages": [_etapa("analise"), _etapa("hetero", alcance=["PPI"], ordem=2)]}

    assert [etapa["id"] for etapa in dominio.etapas_de_analise(conteudo)] == ["analise"]


def test_a_mesma_etapa_para_todas_continua_candidata():
    conteudo = {"stages": [_etapa("analise"), _etapa("hetero", ordem=2)]}

    assert [etapa["id"] for etapa in dominio.etapas_de_analise(conteudo)] == ["analise", "hetero"]


def test_o_reingresso_nao_cobra_resultado_da_etapa_que_nao_alcanca(
    gestor, api_client, manager_headers, monkeypatch
):
    """FR-6986: a reabilitada da ampla não está pendente na Heteroidentificação; a PPI está."""
    cenario = montar_com_alcance(gestor, api_client, manager_headers, seed=1639, codigo="1639")
    ppi, ampla = inscrever(
        cenario["edital"], 2, primeiro=1, modalidades={0: MODALIDADE_PPI}, perfil=cenario["perfil"]
    )
    reabilitadas = {ppi.id: "resultado-ppi", ampla.id: "resultado-ampla"}
    monkeypatch.setattr(
        "processo_seletivo.resultados.application.selectors.reabilitadas_por_recurso",
        lambda *, edital: reabilitadas,
    )
    marco = {"stages": [str(cenario["hetero"])]}

    pendentes = reingressos_pendentes(edital=cenario["edital"], marco=marco)

    assert pendentes == {ppi.id: "resultado-ppi"}


def test_sem_restrita_o_reingresso_e_o_de_antes(gestor, api_client, manager_headers, monkeypatch):
    """A contraprova: com a Etapa para todas, as duas reabilitadas estão pendentes."""
    cenario = montar_com_alcance(
        gestor, api_client, manager_headers, seed=1640, codigo="1640", alcance=None
    )
    ppi, ampla = inscrever(
        cenario["edital"], 2, primeiro=1, modalidades={0: MODALIDADE_PPI}, perfil=cenario["perfil"]
    )
    reabilitadas = {ppi.id: "resultado-ppi", ampla.id: "resultado-ampla"}
    monkeypatch.setattr(
        "processo_seletivo.resultados.application.selectors.reabilitadas_por_recurso",
        lambda *, edital: reabilitadas,
    )
    conteudo = effective_version(edital_id=cenario["edital"].id).content
    assert conteudo["stages"][1]["modalityCodes"] is None

    pendentes = reingressos_pendentes(
        edital=cenario["edital"], marco={"stages": [str(cenario["hetero"])]}
    )

    assert pendentes == reabilitadas
