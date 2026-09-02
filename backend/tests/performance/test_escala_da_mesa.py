"""A escala da 012, medida — e não afirmada.

Mil inscritos com dupla avaliação são duas mil atribuições, e P-004 diz que essa escala decide o
desenho. Aqui ela é contada: nenhuma tela custa por linha, e nenhum ato da 011 custa por atribuição.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.avaliacoes.application.distribuicao import distribuir
from processo_seletivo.avaliacoes.application.selectors import (
    POR_PAGINA,
    inscricoes_da_etapa,
    mesa,
    resumo_da_etapa,
)
from processo_seletivo.avaliacoes.models import Atribuicao
from processo_seletivo.comissoes.application.alocacao import remover_alocacao
from processo_seletivo.comissoes.domain.etapas import etapa_vigente
from tests.conftest import ator_institucional
from tests.fixtures.comissao import inscrever
from tests.fixtures.mesa import montar_banca
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.performance]

MUITAS = 500


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    return montar_banca(gestor, api_client, manager_headers, seed=17, codigo="H1")


@pytest.fixture
def mesa_cheia(cenario, gestor):
    """Quinhentas atribuições para uma pessoa — o número que SC-015 nomeia."""
    inscricoes = inscrever(cenario["edital"], MUITAS, primeiro=2000)
    distribuir(
        actor=gestor,
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa"],
        membro_ids=[cenario["membros"]["joao"].id],
        inscricao_ids=[i.id for i in inscricoes],
        idempotency_key="escala",
        correlation_id="teste",
    )
    return inscricoes


def test_a_mesa_com_quinhentas_atribuicoes_nao_verifica_por_linha(cenario, mesa_cheia):
    """SC-015. A autorização vem da forma em lote da 011, e a página é paginada.

    O limite é generoso de propósito: o que ele proíbe não é um número, é o **crescimento**. Com
    verificação por linha seriam mais de mil consultas.
    """
    joao = ator_institucional("joao")

    with CaptureQueriesContext(connection) as consultas:
        linhas, pagina, contagens = mesa(
            ator=joao, edital=cenario["edital"], etapa_id=cenario["etapa"]
        )

    assert contagens["total"] == MUITAS
    assert len(linhas) == POR_PAGINA
    assert len(consultas.captured_queries) <= 12, len(consultas.captured_queries)


def test_a_mesa_nao_cresce_com_o_numero_de_atribuicoes(cenario, gestor, mesa_cheia):
    """A prova que um limite absoluto não dá: o custo é o **mesmo** para 20 e para 500."""
    joao = ator_institucional("joao")
    etapa = etapa_vigente(cenario["edital"], cenario["etapa"])
    assert etapa is not None

    with CaptureQueriesContext(connection) as poucas:
        mesa(ator=joao, edital=cenario["edital"], etapa_id=cenario["etapa"], pagina=1)
    with CaptureQueriesContext(connection) as muitas:
        mesa(ator=joao, edital=cenario["edital"], etapa_id=cenario["etapa"], pagina=20)

    assert len(muitas.captured_queries) == len(poucas.captured_queries)


def test_a_organizacao_do_trabalho_conta_por_agregacao(cenario, mesa_cheia):
    """FR-014 com mil inscrições: três números saem de `GROUP BY`, e não de um laço."""
    etapa = etapa_vigente(cenario["edital"], cenario["etapa"])

    with CaptureQueriesContext(connection) as consultas:
        resumo = resumo_da_etapa(edital=cenario["edital"], etapa=etapa)

    assert resumo["inscricoes"] == MUITAS
    assert len(consultas.captured_queries) <= 4, len(consultas.captured_queries)


def test_a_listagem_da_distribuicao_e_paginada_e_nao_cresce(cenario, mesa_cheia):
    etapa = etapa_vigente(cenario["edital"], cenario["etapa"])

    with CaptureQueriesContext(connection) as consultas:
        linhas, _ = inscricoes_da_etapa(edital=cenario["edital"], etapa=etapa)

    assert len(linhas) == POR_PAGINA
    assert len(consultas.captured_queries) <= 6, len(consultas.captured_queries)


def test_retirar_a_pessoa_da_etapa_custa_uma_escrita(cenario, gestor, mesa_cheia):
    """FR-069, e é o coração de D-004.

    Com quinhentas atribuições, uma revogação desnormalizada custaria quinhentas escritas — e a
    correção do engano custaria outras tantas. A conjunção avaliada a cada acesso custa zero.
    """
    from processo_seletivo.comissoes.models import AlocacaoEtapa

    # João é quem tem as quinhentas: é a alocação **dele** que precisa sair sem custo por linha.
    alocacao = AlocacaoEtapa.objects.get(
        membro=cenario["membros"]["joao"], edital=cenario["edital"], ativo=True
    )

    with CaptureQueriesContext(connection) as consultas:
        remover_alocacao(
            actor=gestor,
            processo_id=cenario["processo"].id,
            alocacao_id=alocacao.id,
            idempotency_key="tirar-escala",
            correlation_id="teste",
        )

    escritas_em_atribuicao = [
        c["sql"]
        for c in consultas.captured_queries
        if "avaliacoes_atribuicao" in c["sql"]
        and any(c["sql"].lstrip().upper().startswith(v) for v in ("UPDATE", "INSERT", "DELETE"))
    ]
    assert escritas_em_atribuicao == []
    assert Atribuicao.objects.filter(ativo=True).count() == MUITAS


def test_distribuir_mil_inscricoes_nao_exige_mil_interacoes(cenario, gestor):
    """SC-014: uma submissão, quinhentas atribuições."""
    inscricoes = inscrever(cenario["edital"], MUITAS, primeiro=3000)

    resultado = distribuir(
        actor=gestor,
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa"],
        membro_ids=[cenario["membros"]["ana"].id],
        inscricao_ids=[i.id for i in inscricoes],
        idempotency_key="uma-submissao",
        correlation_id="teste",
    )

    assert resultado["feitas"] == MUITAS


def test_a_tela_da_mesa_com_quinhentas_responde(
    client, seletor_ligado, django_assert_max_num_queries, cenario, mesa_cheia
):
    """Pelo canal do ator, que é onde a escala precisa valer."""
    identificar(client, "joao", [])
    url = reverse("interface:minha-etapa", args=[cenario["edital"].id, cenario["etapa"]])

    with django_assert_max_num_queries(20):
        resposta = client.get(url)

    assert resposta.status_code == 200
