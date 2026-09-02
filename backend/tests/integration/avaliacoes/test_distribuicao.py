"""Distribuir em lote, e o que o lote recusa sem derrubar (US1).

A distribuição é ato administrativo com autoria: cada Atribuição gera seu evento, e o resultado é
declarado — quantas foram, quantas não, e por quê.
"""

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.avaliacoes.application.distribuicao import ATRIBUIR, distribuir
from processo_seletivo.avaliacoes.models import Atribuicao, Impedimento
from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.comissao import alocar_em, constituir, inscrever

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def banca(gestor, processo_a, edital_a, comissao_de_a, etapa_a1):
    """Maria preside; João e Ana avaliam a Etapa A1."""
    ana = constituir(gestor, processo_a, [("ana", Funcao.MEMBRO)], prefixo="banca")["ana"]
    for membro in (comissao_de_a["joao"], ana):
        alocar_em(gestor, processo_a, membro, edital_a, etapa_a1)
    return {"joao": comissao_de_a["joao"], "ana": ana, "maria": comissao_de_a["maria"]}


@pytest.fixture
def inscricoes(edital_a):
    return inscrever(edital_a, 4)


def lote(gestor, edital, etapa_id, membros, inscricoes, chave="lote-1"):
    return distribuir(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=etapa_id,
        membro_ids=[m.id for m in membros],
        inscricao_ids=[i.id for i in inscricoes],
        idempotency_key=chave,
        correlation_id="teste",
    )


def test_uma_submissao_atribui_muitas_inscricoes(gestor, edital_a, etapa_a1, banca, inscricoes):
    criadas, recusas = lote(gestor, edital_a, etapa_a1, [banca["joao"]], inscricoes)

    assert len(criadas) == 4
    assert recusas == []
    assert Atribuicao.objects.filter(ativo=True).count() == 4


def test_o_teto_alcanca_o_segundo_avaliador_quando_a_etapa_declara_uma(
    gestor, edital_a, etapa_a1, banca, inscricoes
):
    """Etapa sem declaração recebe **uma** avaliação, e a segunda é recusada (FR-009, FR-065)."""
    criadas, recusas = lote(
        gestor, edital_a, etapa_a1, [banca["joao"], banca["ana"]], inscricoes[:2]
    )

    assert len(criadas) == 2
    assert len(recusas) == 2
    for inscricao in inscricoes[:2]:
        assert Atribuicao.objects.filter(inscricao=inscricao, ativo=True).count() == 1


def test_cada_atribuicao_gera_seu_evento(gestor, edital_a, etapa_a1, banca, inscricoes):
    """A trilha responde por agregado: "quem passou a avaliar esta inscrição" (FR-016)."""
    criadas, _ = lote(gestor, edital_a, etapa_a1, [banca["joao"]], inscricoes)

    eventos = RegistroAuditoria.objects.filter(operation=ATRIBUIR)
    assert eventos.count() == len(criadas)
    assert set(eventos.values_list("aggregate_id", flat=True)) == {c.id for c in criadas}


def test_o_teto_recusa_a_excedente_nomeando_o_numero(gestor, edital_a, etapa_a1, banca, inscricoes):
    """A Etapa não declara quantidade: a ausência é uma avaliação por inscrição (FR-009)."""
    lote(gestor, edital_a, etapa_a1, [banca["joao"]], inscricoes[:1], chave="a")

    _, recusas = lote(gestor, edital_a, etapa_a1, [banca["ana"]], inscricoes[:1], chave="b")

    assert len(recusas) == 1
    assert "1 avaliaç" in recusas[0].motivo


def test_impedimento_e_ja_atribuida_nao_derrubam_o_lote(
    gestor, edital_a, etapa_a1, banca, inscricoes
):
    """Regra sobre a linha é relatada; o restante é distribuído (FR-085)."""
    from django.utils import timezone

    Impedimento.objects.create(
        identity_subject="joao",
        inscricao=inscricoes[0],
        motivo="Parentesco",
        criado_em=timezone.now(),
        criado_por="maria",
    )
    lote(gestor, edital_a, etapa_a1, [banca["joao"]], inscricoes[1:2], chave="a")

    criadas, recusas = lote(gestor, edital_a, etapa_a1, [banca["joao"]], inscricoes, chave="b")

    assert len(criadas) == 2
    assert {r.inscricao.id for r in recusas} == {inscricoes[0].id, inscricoes[1].id}
    assert any("impedimento" in r.motivo.lower() for r in recusas)
    assert any("já estava atribuída" in r.motivo for r in recusas)


def test_etapa_inexistente_derruba_o_lote(gestor, edital_a, banca, inscricoes):
    """Erro sobre o pedido: distribuir a parte válida seria adivinhar a intenção (FR-085)."""
    with pytest.raises(DomainError) as recusa:
        lote(
            gestor,
            edital_a,
            "00000000-0000-0000-0000-000000000999",
            [banca["joao"]],
            inscricoes,
        )

    assert recusa.value.status == 404
    assert Atribuicao.objects.count() == 0


def test_avaliador_sem_alocacao_derruba_o_lote(
    gestor, processo_a, edital_a, etapa_a2, banca, inscricoes
):
    with pytest.raises(DomainError) as recusa:
        lote(gestor, edital_a, etapa_a2, [banca["joao"]], inscricoes)

    assert recusa.value.code == "avaliador_sem_alocacao"
    assert Atribuicao.objects.count() == 0


def test_inscricao_em_rascunho_derruba_o_lote(gestor, edital_a, etapa_a1, banca, inscricoes):
    """Só inscrição **submetida** é atribuível (FR-012)."""
    rascunho = inscrever(edital_a, 1, primeiro=99)[0]
    Inscricao.objects.filter(pk=rascunho.pk).update(status=Inscricao.Status.RASCUNHO)

    with pytest.raises(DomainError) as recusa:
        lote(gestor, edital_a, etapa_a1, [banca["joao"]], [*inscricoes, rascunho])

    assert recusa.value.code == "inscricao_nao_atribuivel"
    assert Atribuicao.objects.count() == 0


def test_inscricao_de_outro_edital_derruba_o_lote(
    gestor, edital_a, edital_b, etapa_a1, banca, inscricoes
):
    de_outro = inscrever(edital_b, 1, primeiro=50)[0]

    with pytest.raises(DomainError) as recusa:
        lote(gestor, edital_a, etapa_a1, [banca["joao"]], [*inscricoes, de_outro])

    assert recusa.value.code == "inscricao_nao_atribuivel"


def test_quem_nao_gere_a_comissao_nao_distribui(edital_a, etapa_a1, banca, inscricoes):
    estranho = ator_institucional("estranho")

    with pytest.raises(DomainError) as recusa:
        lote(estranho, edital_a, etapa_a1, [banca["joao"]], inscricoes)

    assert recusa.value.status == 404


@pytest.fixture
def edital_com_dupla(db, api_client, manager_headers):
    """Um Edital cuja Etapa **declara** duas avaliações por inscrição (FR-007)."""
    from tests.fixtures.comissao import publicar_processo_com_etapas

    return publicar_processo_com_etapas(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "mvp-test-key-0009"},
        {
            "institutionalCode": "PS-2026-009",
            "title": "Processo com dupla avaliação",
            "firstEdital": {"number": "09", "year": 2026, "title": "Edital da dupla"},
        },
        seed=2,
        avaliacoes=2,
        maxima="100.0000",
    )


def test_a_combinacao_e_uniforme_quando_a_etapa_declara_duas(
    gestor, api_client, manager_headers, edital_com_dupla
):
    """Cada inscrição selecionada vai para cada avaliador selecionado.

    O lote não **reparte**: ele combina. Dividir cem entre dois avaliadores é decisão sobre quem
    avalia quem, e decisão tem autoria — são duas submissões de cinquenta, e as duas são atos da
    presidência (FR-013, FR-017, P-002).
    """
    from tests.fixtures.comissao import ETAPA_A1
    from tests.fixtures.edital import identificador as ident

    etapa_id = ident(ETAPA_A1, 2)
    processo = edital_com_dupla.processo
    membros = constituir(
        gestor,
        processo,
        [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO), ("ana", Funcao.MEMBRO)],
    )
    for nome in ("joao", "ana"):
        alocar_em(gestor, processo, membros[nome], edital_com_dupla, etapa_id)
    inscricoes = inscrever(edital_com_dupla, 2, primeiro=200)

    criadas, recusas = lote(
        gestor, edital_com_dupla, etapa_id, [membros["joao"], membros["ana"]], inscricoes
    )

    assert len(criadas) == 4
    assert recusas == []
    for inscricao in inscricoes:
        assert Atribuicao.objects.filter(inscricao=inscricao, ativo=True).count() == 2
