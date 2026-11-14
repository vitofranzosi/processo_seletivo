"""Só as inscrições alcançadas passam pela Etapa — e quem não é alcançado a atravessa (163).

Seis inscrições num Perfil: duas `PPI`, duas `PCD` e duas sem Modalidade (a ampla). A Etapa do meio,
a Heteroidentificação, só alcança `PPI`.

```text
FR-6971  participação       só as duas PPI participam da Heteroidentificação
FR-6973  distribuição       atribuir uma AC é recusado, com o motivo do alcance
FR-6975  Ocorrência         registrar ausência de uma AC é recusado pelo mesmo motivo
FR-6976  prontidão          a partição soma as seis, e quatro estão "fora do alcance"
FR-6972  progressão         a AC habilitada na Análise documental participa da Prova sem esperar
                            a Heteroidentificação; a PPI espera
FR-6977  Etapa sem alcançado não exige consolidação e não trava a seguinte
```
"""

from uuid import UUID

import pytest

from processo_seletivo.comissoes.domain.etapas import etapas_vigentes
from processo_seletivo.resultados.application.consolidacao import consolidar
from processo_seletivo.resultados.application.ocorrencia import registrar_ocorrencia
from processo_seletivo.resultados.application.prontidao import (
    AGUARDANDO_ANTERIOR,
    FORA_DO_ALCANCE,
    FORA_DO_ALCANCE_RECUSA,
    panorama_da_etapa,
    participa_da_etapa,
    participacao,
)
from processo_seletivo.resultados.models import ResultadoEtapa
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.alcance import MODALIDADE_PCD, MODALIDADE_PPI, montar_com_alcance
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import concluir_como, distribuir_para

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

# Posição → Modalidade: 0 e 1 PPI, 2 e 3 PCD, 4 e 5 sem Modalidade.
MODALIDADES = {0: MODALIDADE_PPI, 1: MODALIDADE_PPI, 2: MODALIDADE_PCD, 3: MODALIDADE_PCD}


def _montar(gestor, api_client, manager_headers, *, seed, alcance=("PPI",)):
    cenario = montar_com_alcance(
        gestor, api_client, manager_headers, seed=seed, codigo=str(seed), alcance=alcance
    )
    cenario["inscricoes"] = inscrever(
        cenario["edital"], 6, primeiro=1, modalidades=MODALIDADES, perfil=cenario["perfil"]
    )
    return cenario


def _panorama(cenario, etapa_id):
    vigentes = etapas_vigentes(cenario["edital"])
    return panorama_da_etapa(
        edital=cenario["edital"], etapa=vigentes[UUID(str(etapa_id))], etapas_vigentes=vigentes
    )


def _na_etapa(cenario, etapa):
    return {**cenario, "etapa": etapa}


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


def _habilitar_na_analise(cenario, gestor, *, seed):
    """Todas as seis passam pela Análise documental, com nota acima da mínima."""
    inscricoes = cenario["inscricoes"]
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave=f"analise-{seed}")
    for inscricao in inscricoes:
        concluir_como(cenario, "joao", inscricao, pontuacao="80")
    _consolidar(cenario, cenario["analise"], inscricoes, chave=f"consolidar-analise-{seed}")


def test_so_as_alcancadas_participam_e_a_particao_fecha(gestor, api_client, manager_headers):
    """FR-6971, FR-6976, UX-732: duas participam, quatro estão fora do alcance, e somam seis."""
    cenario = _montar(gestor, api_client, manager_headers, seed=1631)
    ppi = {i.id for i in cenario["inscricoes"][:2]}

    participantes, _, _ = participacao(edital=cenario["edital"], etapa_id=cenario["hetero"])
    panorama = _panorama(cenario, cenario["hetero"])

    assert participantes == ppi
    assert panorama["contagens"]["fora_do_alcance"] == 4
    assert panorama["contagens"]["alcancadas"] == 2
    assert panorama["contagens"]["total"] == 6
    for inscricao in cenario["inscricoes"][2:]:
        assert panorama["estados"][inscricao.id][0] == FORA_DO_ALCANCE


def test_a_etapa_para_todas_continua_como_antes(gestor, api_client, manager_headers):
    """FR-6961: sem alcance declarado, ninguém fica fora dele."""
    cenario = _montar(gestor, api_client, manager_headers, seed=1632, alcance=None)

    panorama = _panorama(cenario, cenario["hetero"])

    assert panorama["contagens"]["fora_do_alcance"] == 0
    assert panorama["contagens"]["alcancadas"] == 6


def test_atribuir_quem_esta_fora_do_alcance_e_recusado(gestor, api_client, manager_headers):
    """FR-6973: a recusa é do servidor, e diz o motivo do alcance — não "eliminada"."""
    cenario = _montar(gestor, api_client, manager_headers, seed=1633)
    ampla = cenario["inscricoes"][4]

    with pytest.raises(DomainError) as recusa:
        distribuir_para(
            _na_etapa(cenario, cenario["hetero"]), gestor, ["joao"], [ampla], chave="fora-1633"
        )

    assert recusa.value.code == "inscricao_fora_da_etapa"
    assert recusa.value.detail == FORA_DO_ALCANCE_RECUSA


def test_registrar_ocorrencia_de_quem_esta_fora_do_alcance_e_recusado(
    gestor, api_client, manager_headers
):
    """FR-6975: nenhum Resultado nasce para quem a Etapa não alcança, por caminho nenhum."""
    cenario = _montar(gestor, api_client, manager_headers, seed=1634)
    pcd = cenario["inscricoes"][2]

    with pytest.raises(DomainError) as recusa:
        registrar_ocorrencia(
            actor=ator_institucional("maria"),
            processo_id=cenario["processo"].id,
            edital_id=cenario["edital"].id,
            etapa_id=cenario["hetero"],
            inscricao_ids=[pcd.id],
            motivo="Não compareceu.",
            idempotency_key="ocorrencia-1634",
            correlation_id="teste",
        )

    assert recusa.value.detail == FORA_DO_ALCANCE_RECUSA
    assert not ResultadoEtapa.objects.filter(etapa_id=cenario["hetero"]).exists()


def test_quem_nao_e_alcancado_atravessa_a_etapa_sem_esperar_por_ela(
    gestor, api_client, manager_headers
):
    """FR-6972, SC-2312: a anterior que conta é a última que alcança a inscrição.

    A Análise documental está consolidada, e a Heteroidentificação, não. Para a Prova, a anterior
    das PPI é a Heteroidentificação — elas aguardam; a das demais é a Análise documental — elas
    participam.
    """
    cenario = _montar(gestor, api_client, manager_headers, seed=1635)
    _habilitar_na_analise(cenario, gestor, seed=1635)
    # Uma PPI tem Resultado na Heteroidentificação; é o que acorda o gate dela.
    na_hetero = _na_etapa(cenario, cenario["hetero"])
    primeira_ppi = cenario["inscricoes"][0]
    distribuir_para(na_hetero, gestor, ["joao"], [primeira_ppi], chave="hetero-1635")
    concluir_como(na_hetero, "joao", primeira_ppi, sentido="FAVORAVEL")
    _consolidar(cenario, cenario["hetero"], [primeira_ppi], chave="consolidar-hetero-1635")

    participantes, _, aguardando = participacao(edital=cenario["edital"], etapa_id=cenario["prova"])
    panorama = _panorama(cenario, cenario["prova"])

    segunda_ppi = cenario["inscricoes"][1]
    nao_alcancadas = {i.id for i in cenario["inscricoes"][2:]}
    assert nao_alcancadas <= participantes
    assert primeira_ppi.id in participantes
    assert aguardando == {segunda_ppi.id}
    assert panorama["estados"][segunda_ppi.id][0] == AGUARDANDO_ANTERIOR
    for inscricao in cenario["inscricoes"][2:]:
        assert participa_da_etapa(
            edital=cenario["edital"], etapa_id=cenario["prova"], inscricao_id=inscricao.id
        )
    assert not participa_da_etapa(
        edital=cenario["edital"], etapa_id=cenario["prova"], inscricao_id=segunda_ppi.id
    )


def test_o_desfecho_desfavoravel_tira_so_quem_foi_avaliado(gestor, api_client, manager_headers):
    """O efeito de hoje (D-010): o `ELIMINADA` da restrita tira a PPI das seguintes, e só ela."""
    cenario = _montar(gestor, api_client, manager_headers, seed=1636)
    _habilitar_na_analise(cenario, gestor, seed=1636)
    na_hetero = _na_etapa(cenario, cenario["hetero"])
    ppis = cenario["inscricoes"][:2]
    distribuir_para(na_hetero, gestor, ["joao"], ppis, chave="hetero-1636")
    concluir_como(na_hetero, "joao", ppis[0], sentido="DESFAVORAVEL")
    concluir_como(na_hetero, "joao", ppis[1], sentido="FAVORAVEL")
    desfecho = _consolidar(cenario, cenario["hetero"], ppis, chave="consolidar-hetero-1636")

    participantes, eliminadas, _ = participacao(edital=cenario["edital"], etapa_id=cenario["prova"])

    assert desfecho["feitas"] == 2
    assert ResultadoEtapa.objects.filter(etapa_id=cenario["hetero"]).count() == 2
    assert eliminadas == {ppis[0].id}
    assert participantes == {i.id for i in cenario["inscricoes"]} - {ppis[0].id}


def test_a_etapa_sem_nenhum_alcancado_nao_trava_a_seguinte(gestor, api_client, manager_headers):
    """FR-6977: restrita a um código em que ninguém se inscreveu, ela não espera nada."""
    cenario = montar_com_alcance(
        gestor, api_client, manager_headers, seed=1637, codigo="1637", alcance=("PCD",)
    )
    cenario["inscricoes"] = inscrever(cenario["edital"], 3, primeiro=1, perfil=cenario["perfil"])
    _habilitar_na_analise(cenario, gestor, seed=1637)

    hetero = _panorama(cenario, cenario["hetero"])
    participantes, _, aguardando = participacao(edital=cenario["edital"], etapa_id=cenario["prova"])

    assert hetero["contagens"]["alcancadas"] == 0
    assert hetero["participantes"] == set()
    assert aguardando == set()
    assert participantes == {i.id for i in cenario["inscricoes"]}
