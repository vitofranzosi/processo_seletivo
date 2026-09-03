"""A regra que governou o ato — e o que acontece quando ela muda no meio (FR-071, FR-073, FR-096).

A Constituição exige que, para cada Avaliação, seja possível determinar a versão e as regras
**então vigentes**, e que regra atual não substitua regra histórica. Daí a Avaliação apontar para a
Versão Consolidada — e **não** copiar máxima, mínima e caráter, que a versão já reproduz.
"""

from decimal import Decimal

import pytest

from processo_seletivo.avaliacoes.application.avaliacao import concluir, gravar
from processo_seletivo.avaliacoes.application.distribuicao import distribuir
from processo_seletivo.avaliacoes.domain.autorizacao import pode_avaliar_inscricao
from processo_seletivo.avaliacoes.models import Avaliacao
from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.comissao import ETAPA_A1, alocar_em, constituir, inscrever
from tests.fixtures.edital import identificador
from tests.fixtures.publicacao import create_retification, publish_retification

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def edital_com_regra(db, api_client, manager_headers):
    from tests.fixtures.comissao import publicar_processo_com_etapas

    return publicar_processo_com_etapas(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "mvp-test-key-0041"},
        {
            "institutionalCode": "PS-2026-041",
            "title": "Processo retificável",
            "firstEdital": {"number": "41", "year": 2026, "title": "Edital retificável"},
        },
        seed=4,
        avaliacoes=2,
        maxima="100.0000",
    )


@pytest.fixture
def etapa(edital_com_regra):
    return identificador(ETAPA_A1, 4)


@pytest.fixture
def cenario(gestor, edital_com_regra, etapa):
    processo = edital_com_regra.processo
    membros = constituir(
        gestor, processo, [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO)], prefixo="ver"
    )
    alocar_em(gestor, processo, membros["joao"], edital_com_regra, etapa)
    inscricoes = inscrever(edital_com_regra, 1, primeiro=400)
    distribuir(
        actor=gestor,
        processo_id=processo.id,
        edital_id=edital_com_regra.id,
        etapa_id=etapa,
        membro_ids=[membros["joao"].id],
        inscricao_ids=[inscricoes[0].id],
        idempotency_key="ver",
        correlation_id="teste",
    )
    return inscricoes[0]


def vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def baixar_a_maxima(api_client, edital, etapa, *, para="50.0000", sufixo="a"):
    """Uma Retificação que muda a pontuação máxima da Etapa."""
    atual = next(e for e in vigente(edital).content["stages"] if e["id"] == str(etapa))
    return publish_retification(
        api_client,
        create_retification(
            api_client,
            edital,
            [
                {
                    "targetPath": f"/stages/id={etapa}",
                    "operation": "REPLACE",
                    "newValue": {**atual, "maximumScore": para},
                }
            ],
            suffix=sufixo,
        ),
        suffix=sufixo,
    )


def test_a_conclusao_grava_a_versao_contra_a_qual_foi_validada(edital_com_regra, etapa, cenario):
    avaliacao, _ = concluir(
        ator=ator_institucional("joao"),
        edital=edital_com_regra,
        etapa_id=etapa,
        inscricao_id=cenario.id,
        pontuacao="90",
        parecer="Atende",
        expected_revision=1,
        versao_reconhecida=vigente(edital_com_regra).id,
        correlation_id="teste",
    )

    assert avaliacao.versao_id == vigente(edital_com_regra).id


def test_retificacao_no_intervalo_e_anunciada_antes_de_concluir(
    api_client, edital_com_regra, etapa, cenario
):
    """FR-073: descobrir a Retificação depois, no parecer de outra pessoa, é o que isto impede."""
    joao = ator_institucional("joao")
    versao_que_ele_viu = vigente(edital_com_regra).id
    gravar(
        ator=joao,
        edital=edital_com_regra,
        etapa_id=etapa,
        inscricao_id=cenario.id,
        pontuacao="90",
        parecer="Atende",
        expected_revision=1,
        correlation_id="teste",
    )
    baixar_a_maxima(api_client, edital_com_regra, etapa)

    with pytest.raises(DomainError) as recusa:
        concluir(
            ator=joao,
            edital=edital_com_regra,
            etapa_id=etapa,
            inscricao_id=cenario.id,
            pontuacao="90",
            parecer="Atende",
            expected_revision=2,
            versao_reconhecida=versao_que_ele_viu,
            correlation_id="teste",
        )

    assert recusa.value.code == "versao_mudou"
    assert Avaliacao.objects.get(inscricao_id=cenario.id).estado == Avaliacao.Estado.RASCUNHO


def test_reconhecida_a_mudanca_a_validacao_e_contra_a_regra_nova(
    api_client, edital_com_regra, etapa, cenario
):
    """A versão validada é a versão gravada (FR-096): 90 passava, e depois da Retificação não."""
    joao = ator_institucional("joao")
    gravar(
        ator=joao,
        edital=edital_com_regra,
        etapa_id=etapa,
        inscricao_id=cenario.id,
        pontuacao="90",
        parecer="Atende",
        expected_revision=1,
        correlation_id="teste",
    )
    baixar_a_maxima(api_client, edital_com_regra, etapa)
    nova = vigente(edital_com_regra)

    with pytest.raises(DomainError) as recusa:
        concluir(
            ator=joao,
            edital=edital_com_regra,
            etapa_id=etapa,
            inscricao_id=cenario.id,
            pontuacao="90",
            parecer="Atende",
            expected_revision=2,
            versao_reconhecida=nova.id,
            correlation_id="teste",
        )

    assert recusa.value.status == 422
    assert "50.0000" in recusa.value.detail


def test_a_avaliacao_nao_copia_a_regra(edital_com_regra, etapa, cenario):
    """FR-072: duplicar máxima e mínima criaria a segunda fonte divergente."""
    campos = {campo.name for campo in Avaliacao._meta.get_fields()}

    for copiado in ("maximum_score", "minimum_score", "eliminatory", "maxima", "minima"):
        assert copiado not in campos


def test_retificacao_que_remove_a_etapa_nao_apaga_a_avaliacao(
    api_client, edital_com_regra, etapa, cenario
):
    """EC-004: a Etapa deixa de conceder acesso; o que foi afirmado permanece."""
    joao = ator_institucional("joao")
    avaliacao, _ = concluir(
        ator=joao,
        edital=edital_com_regra,
        etapa_id=etapa,
        inscricao_id=cenario.id,
        pontuacao="90",
        parecer="Atende",
        expected_revision=1,
        versao_reconhecida=vigente(edital_com_regra).id,
        correlation_id="teste",
    )

    publish_retification(
        api_client,
        create_retification(
            api_client,
            edital_com_regra,
            [{"targetPath": f"/stages/id={etapa}", "operation": "REMOVE"}],
            suffix="r",
        ),
        suffix="r",
    )

    avaliacao.refresh_from_db()
    assert avaliacao.estado == Avaliacao.Estado.CONCLUIDA
    assert avaliacao.pontuacao == Decimal("90.0000")
    # A regra da época continua reproduzível pela versão gravada, ainda que a Etapa já não exista
    # no conteúdo vigente.
    assert avaliacao.versao is not None
    assert pode_avaliar_inscricao(joao, edital_com_regra, etapa, cenario.id) is None
