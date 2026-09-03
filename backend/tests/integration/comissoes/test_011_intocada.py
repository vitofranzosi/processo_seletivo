"""A 011 segue idêntica (FR-059).

A `012` compõe com a 011 e não a reescreve. A única exceção admitida foi o **nome** de uma rota —
`atribuicao` virou `minha_etapa`, porque a palavra passou a ser entidade do domínio (D-003) —, e
ela não altera domínio, dado, autorização nem comportamento.

Este arquivo é a guarda: se algum dia a 012 precisar mudar o guard, a alocação ou a comissão, o
desenho de composição foi abandonado e a decisão volta à spec.
"""

import inspect

import pytest

from processo_seletivo.comissoes import models as comissoes_models
from processo_seletivo.comissoes.domain import autorizacao
from processo_seletivo.comissoes.domain.autorizacao import (
    etapas_autorizadas,
    pode_atuar_na_etapa,
    pode_gerir_comissao,
)
from tests.conftest import ator_institucional
from tests.fixtures.comissao import alocar_em, inscrever
from tests.fixtures.mesa import distribuir_para, montar_banca

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    return montar_banca(gestor, api_client, manager_headers, seed=19, codigo="J1")


def test_o_guard_nao_conhece_atribuicao(cenario):
    """A composição é da `012`: a 011 responde por Etapa, e nada além.

    Se `pode_atuar_na_etapa` passasse a olhar Atribuição, a alocação deixaria de abrir a Etapa —
    e o estado vazio da Mesa (FR-023) viraria um 404.
    """
    fonte = inspect.getsource(autorizacao)

    assert "Atribuicao" not in fonte
    assert "avaliacoes" not in fonte


def test_alocado_sem_atribuicao_continua_podendo_atuar_na_etapa(cenario):
    """O invariante da 011 que a 012 depende de **não** ter quebrado."""
    joao = ator_institucional("joao")

    assert pode_atuar_na_etapa(joao, cenario["edital"], cenario["etapa"]) is True
    assert cenario["etapa"] in {str(e) for e in etapas_autorizadas(joao, cenario["edital"])}


def test_distribuir_nao_altera_alocacao_nem_comissao(cenario, gestor):
    """A 012 escreve no app dela, e em nenhum outro (FR-059)."""
    from processo_seletivo.comissoes.models import AlocacaoEtapa, MembroComissao

    antes = (
        set(MembroComissao.objects.values_list("id", "funcao", "ativo")),
        set(AlocacaoEtapa.objects.values_list("id", "ativo")),
    )
    distribuir_para(cenario, gestor, ["joao"], inscrever(cenario["edital"], 3, primeiro=2700))

    assert (
        set(MembroComissao.objects.values_list("id", "funcao", "ativo")),
        set(AlocacaoEtapa.objects.values_list("id", "ativo")),
    ) == antes


def test_a_presidencia_continua_com_as_duas_bases(cenario, gestor):
    """FR-016 da 011: permissão sistêmica **ou** presidência deste Processo."""
    maria = ator_institucional("maria")

    assert pode_gerir_comissao(gestor, cenario["processo"]).e_sistemica
    assert pode_gerir_comissao(maria, cenario["processo"]).permissao == "comissao:presidir"
    assert pode_gerir_comissao(ator_institucional("joao"), cenario["processo"]) is None


def test_nenhum_modelo_da_011_ganhou_coluna(cenario):
    """A Atribuição é derivada da alocação, e não paralela a ela (D-004)."""
    membro = {campo.name for campo in comissoes_models.MembroComissao._meta.get_fields()}
    alocacao = {campo.name for campo in comissoes_models.AlocacaoEtapa._meta.get_fields()}

    for proibido in ("avaliacao", "atribuicoes_ativas", "carga", "impedimentos"):
        assert proibido not in membro
        assert proibido not in alocacao
    # As relações reversas que a `012` cria são as únicas novidades, e elas não são colunas.
    assert "atribuicoes" in membro


def test_a_rota_renomeada_mantem_o_caminho(client, seletor_ligado, cenario):
    """D-003: muda o nome interno, e não o endereço — nada fora do repositório quebra."""
    from django.urls import reverse

    from tests.interface.conftest import identificar

    identificar(client, "joao", [])
    caminho = reverse("interface:minha-etapa", args=[cenario["edital"].id, cenario["etapa"]])

    assert caminho.endswith(f"/minhas-etapas/{cenario['edital'].id}/{cenario['etapa']}")
    assert client.get(caminho).status_code == 200


def test_remover_alocacao_continua_sendo_inativar(cenario, gestor):
    """011, D-013: readicionar cria linha nova, e o histórico permanece."""
    from processo_seletivo.comissoes.application.alocacao import remover_alocacao
    from processo_seletivo.comissoes.models import AlocacaoEtapa

    alocacao = AlocacaoEtapa.objects.get(
        membro=cenario["membros"]["ana"], edital=cenario["edital"], ativo=True
    )

    remover_alocacao(
        actor=gestor,
        processo_id=cenario["processo"].id,
        alocacao_id=alocacao.id,
        idempotency_key="intocada",
        correlation_id="teste",
    )
    alocar_em(
        gestor,
        cenario["processo"],
        cenario["membros"]["ana"],
        cenario["edital"],
        cenario["etapa"],
        chave="de-volta",
    )

    assert AlocacaoEtapa.objects.filter(membro=cenario["membros"]["ana"]).count() == 2
