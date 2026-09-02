"""A tela da distribuição: o que falta antes do detalhe, e o lote que cabe numa submissão.

Mil inscrições não cabem numa tela, e a pergunta operacional quase nunca é "todas" — é "quais ainda
não têm ninguém". Daí paginação e filtro serem requisito, e não conforto (FR-049).
"""

import pytest
from django.urls import reverse

from processo_seletivo.avaliacoes.application.selectors import POR_PAGINA
from processo_seletivo.avaliacoes.models import Atribuicao
from tests.fixtures.comissao import alocar_em, inscrever
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def tela(edital_a, etapa_a1):
    return reverse("interface:distribuicao", args=[edital_a.id, etapa_a1])


@pytest.fixture
def banca(gestor, processo_a, edital_a, comissao_de_a, etapa_a1):
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    return comissao_de_a["joao"]


@pytest.fixture
def presidente(client, seletor_ligado):
    identificar(client, "carlos", ["gestor"])
    return client


def test_a_tela_diz_o_que_falta_antes_do_detalhe(presidente, tela, edital_a, banca):
    inscrever(edital_a, 3)

    corpo = presidente.get(tela).content.decode()

    assert "sem avaliador suficiente" in corpo
    assert "avaliação por inscrição" in corpo or "avaliações por inscrição" in corpo


def test_a_lista_e_paginada(presidente, tela, edital_a, banca):
    inscrever(edital_a, POR_PAGINA + 5)

    corpo = presidente.get(tela).content.decode()

    assert "Próxima" in corpo
    assert "Página 1 de 2" in corpo


def test_o_filtro_por_cobertura_encontra_as_carentes(
    presidente, tela, edital_a, banca, gestor, etapa_a1
):
    from processo_seletivo.avaliacoes.application.distribuicao import distribuir

    inscricoes = inscrever(edital_a, 3)
    distribuir(
        actor=gestor,
        processo_id=edital_a.processo_id,
        edital_id=edital_a.id,
        etapa_id=etapa_a1,
        membro_ids=[banca.id],
        inscricao_ids=[inscricoes[0].id],
        idempotency_key="filtro",
        correlation_id="teste",
    )

    corpo = presidente.get(f"{tela}?cobertura=sem_nenhum").content.decode()

    assert inscricoes[0].protocolo not in corpo
    assert inscricoes[1].protocolo in corpo


def test_o_filtro_por_avaliador_mostra_so_o_dele(
    presidente, tela, edital_a, banca, gestor, etapa_a1
):
    from processo_seletivo.avaliacoes.application.distribuicao import distribuir

    inscricoes = inscrever(edital_a, 2)
    distribuir(
        actor=gestor,
        processo_id=edital_a.processo_id,
        edital_id=edital_a.id,
        etapa_id=etapa_a1,
        membro_ids=[banca.id],
        inscricao_ids=[inscricoes[0].id],
        idempotency_key="filtro-2",
        correlation_id="teste",
    )

    corpo = presidente.get(f"{tela}?avaliador=joao").content.decode()

    assert inscricoes[0].protocolo in corpo
    assert inscricoes[1].protocolo not in corpo


def test_o_lote_cabe_numa_submissao_e_declara_o_resultado(presidente, tela, edital_a, banca):
    """FR-097: quantas foram, quantas não, e por quê — sem conferir mil linhas."""
    inscricoes = inscrever(edital_a, 3)

    presidente.post(
        tela,
        {
            "acao": "distribuir",
            "chave_idempotencia": "tela-1",
            "membro_id": [str(banca.id)],
            "inscricao_id": [str(i.id) for i in inscricoes],
        },
    )
    corpo = presidente.get(tela).content.decode()

    assert Atribuicao.objects.filter(ativo=True).count() == 3
    assert "3</strong> atribuídas" in corpo


def test_o_resultado_nomeia_a_linha_recusada(presidente, tela, edital_a, banca):
    inscricoes = inscrever(edital_a, 2)
    envio = {
        "acao": "distribuir",
        "membro_id": [str(banca.id)],
        "inscricao_id": [str(i.id) for i in inscricoes],
    }
    presidente.post(tela, {**envio, "chave_idempotencia": "a"})

    presidente.post(tela, {**envio, "chave_idempotencia": "b"})
    corpo = presidente.get(tela).content.decode()

    assert "2</strong> recusada" in corpo
    assert "já estava atribuída" in corpo


def test_a_resposta_nao_e_armazenavel_pelo_navegador(presidente, tela, edital_a, banca):
    """A tela lista protocolo de candidato: é dado pessoal, e não fica no cache (FR-056)."""
    inscrever(edital_a, 1)

    resposta = presidente.get(tela)

    assert "no-store" in resposta["Cache-Control"]
