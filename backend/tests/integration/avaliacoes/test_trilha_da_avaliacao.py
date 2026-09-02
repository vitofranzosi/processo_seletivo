"""Cada gravação e cada conclusão são auditáveis — e a trilha não guarda o que foi avaliado.

FR-038 exige o registro; FR-054 exige que ele **não** carregue pontuação nem parecer. A trilha
guarda que o ato aconteceu; o conteúdo vive na Avaliação, que é o registro do domínio. Um evento
com a nota dentro tornaria a trilha uma segunda fonte da avaliação — e ela é append-only, de modo
que a divergência com a Avaliação reaberta seria permanente.
"""

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.avaliacoes.application.avaliacao import (
    BASE_DA_MESA,
    CONCLUIR,
    GRAVAR,
    concluir,
    gravar,
)
from processo_seletivo.avaliacoes.application.distribuicao import distribuir
from processo_seletivo.comissoes.domain.funcoes import Funcao
from tests.conftest import ator_institucional
from tests.fixtures.comissao import ETAPA_A1, alocar_em, constituir, inscrever
from tests.fixtures.edital import identificador

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

PONTUACAO = "87.5000"
PARECER = "Documentação completa e compatível com o exigido no item 4.2 do Edital."


@pytest.fixture
def edital_com_regra(db, api_client, manager_headers):
    from tests.fixtures.comissao import publicar_processo_com_etapas

    return publicar_processo_com_etapas(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "mvp-test-key-0051"},
        {
            "institutionalCode": "PS-2026-051",
            "title": "Processo auditado",
            "firstEdital": {"number": "51", "year": 2026, "title": "Edital auditado"},
        },
        seed=5,
        maxima="100.0000",
    )


@pytest.fixture
def cenario(gestor, edital_com_regra):
    etapa = identificador(ETAPA_A1, 5)
    processo = edital_com_regra.processo
    membros = constituir(
        gestor, processo, [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO)], prefixo="tri"
    )
    alocar_em(gestor, processo, membros["joao"], edital_com_regra, etapa)
    inscricao = inscrever(edital_com_regra, 1, primeiro=500)[0]
    distribuir(
        actor=gestor,
        processo_id=processo.id,
        edital_id=edital_com_regra.id,
        etapa_id=etapa,
        membro_ids=[membros["joao"].id],
        inscricao_ids=[inscricao.id],
        idempotency_key="tri",
        correlation_id="teste",
    )
    return {"etapa": etapa, "inscricao": inscricao}


@pytest.fixture
def avaliada(edital_com_regra, cenario):
    joao = ator_institucional("joao")
    comum = {
        "ator": joao,
        "edital": edital_com_regra,
        "etapa_id": cenario["etapa"],
        "inscricao_id": cenario["inscricao"].id,
        "pontuacao": PONTUACAO,
        "parecer": PARECER,
        "correlation_id": "teste",
    }
    gravar(**comum, expected_revision=1)
    avaliacao, _ = concluir(
        **comum,
        expected_revision=2,
        versao_reconhecida=edital_com_regra.versoes_consolidadas.latest("materialized_at").id,
    )
    return avaliacao


def test_gravar_e_concluir_geram_evento(avaliada):
    eventos = RegistroAuditoria.objects.filter(aggregate_id=avaliada.pk).order_by("occurred_at")

    assert [e.operation for e in eventos] == [GRAVAR, CONCLUIR]
    assert {e.actor_subject for e in eventos} == {"joao"}
    assert {e.permission for e in eventos} == {BASE_DA_MESA}


def test_o_evento_identifica_a_inscricao_sem_carregar_o_que_foi_avaliado(avaliada, cenario):
    """FR-053 diz o que precisa estar; FR-054 diz o que não pode."""
    evento = RegistroAuditoria.objects.filter(operation=CONCLUIR).get()

    assert cenario["inscricao"].protocolo in evento.reason
    assert PONTUACAO not in evento.reason
    assert PARECER not in evento.reason


def test_nenhum_evento_da_012_contem_pontuacao_ou_parecer(avaliada):
    """A varredura, e não a inspeção de um evento: o que se proíbe vale para todos eles."""
    for evento in RegistroAuditoria.objects.all():
        conteudo = " ".join([evento.reason, evento.new_state or "", evento.previous_state or ""])
        assert PARECER not in conteudo
        assert PONTUACAO not in conteudo
        assert "87,5" not in conteudo


def test_a_trilha_nao_ganhou_coluna_para_isso(avaliada):
    """FR-070: nada foi acrescentado ao registrador para acomodar esta feature."""
    campos = {campo.name for campo in RegistroAuditoria._meta.get_fields()}

    for proibido in ("pontuacao", "parecer", "score", "avaliacao"):
        assert proibido not in campos
