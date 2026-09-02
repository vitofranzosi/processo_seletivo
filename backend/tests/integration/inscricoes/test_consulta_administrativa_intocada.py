"""SC-017, nas **duas** direções — a fronteira entre a porta da 009 e a da 012.

A `012` reutiliza a mecânica de arquivo da 009 inteira e **não** reutiliza a permissão dela.
Provar isso exige os dois sentidos: a porta administrativa continua exatamente como era, e a
autorização da Mesa não a abre.

A razão é FR-055: `inscricao:consultar` pertence ao Gestor e alcança o Edital inteiro. Entregá-la
ao avaliador daria a ele o acervo — que é o oposto do que a feature promete (D-005).
"""

import pytest
from django.urls import reverse

from processo_seletivo.avaliacoes.application.distribuicao import distribuir
from processo_seletivo.inscricoes.application.consulta import (
    CONSULTAR,
    inscricoes_do_edital,
)
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.comissao import DOCUMENTO_A, alocar_em, inscrever
from tests.fixtures.edital import identificador
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def cenario(raiz_de_arquivos, gestor, processo_a, edital_com_documentos, comissao_de_a, etapa_a1):
    membro = comissao_de_a["joao"]
    alocar_em(gestor, processo_a, membro, edital_com_documentos, etapa_a1)
    inscricao = inscrever(edital_com_documentos, 1, documentos=[identificador(DOCUMENTO_A, 0)])[0]
    distribuir(
        actor=gestor,
        processo_id=processo_a.id,
        edital_id=edital_com_documentos.id,
        etapa_id=etapa_a1,
        membro_ids=[membro.id],
        inscricao_ids=[inscricao.id],
        idempotency_key="fronteira",
        correlation_id="teste",
    )
    return inscricao


def test_a_porta_da_009_continua_exatamente_como_era(edital_com_documentos, cenario):
    """Quem tem a permissão da consulta administrativa segue listando o Edital inteiro."""
    gestor_da_009 = ator_institucional("conferente", CONSULTAR)

    _, linhas = inscricoes_do_edital(actor=gestor_da_009, edital_id=edital_com_documentos.id)

    assert len(linhas) == 1
    assert linhas[0]["candidato"] == cenario.nome


def test_a_autorizacao_da_mesa_nao_abre_a_consulta_administrativa(edital_com_documentos, cenario):
    """O sentido que faltava.

    João tem alocação **e** Atribuição — ele abre aquela inscrição na Mesa. Isso não lhe dá a
    listagem do Edital: o avaliador vê o que lhe cabe, e não o acervo (FR-055, FR-028).
    """
    joao = ator_institucional("joao")

    with pytest.raises(DomainError) as recusa:
        inscricoes_do_edital(actor=joao, edital_id=edital_com_documentos.id)

    assert recusa.value.status == 403


def test_o_avaliador_nao_alcanca_a_tela_administrativa_de_inscricoes(
    client, seletor_ligado, edital_com_documentos, cenario
):
    """Pelo canal do ator, que é onde a fronteira precisa valer (princípio VI)."""
    identificar(client, "joao", [])

    resposta = client.get(reverse("interface:inscricoes", args=[edital_com_documentos.id]))

    assert resposta.status_code in (403, 404)


def test_a_rota_da_mesa_nao_aceita_a_permissao_da_009(
    client, seletor_ligado, edital_com_documentos, etapa_a1, cenario
):
    """E o simétrico: ter a permissão do Gestor não abre a Mesa de ninguém (D-005)."""
    identificar(client, "conferente", ["gestor"])

    resposta = client.get(
        reverse("interface:mesa-inscricao", args=[edital_com_documentos.id, etapa_a1, cenario.id])
    )

    assert resposta.status_code == 404
