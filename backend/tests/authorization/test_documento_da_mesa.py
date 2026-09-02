"""A segunda pergunta da autorização, sobre a inscrição e sobre o arquivo (US3).

A alocação abre a Etapa; a Atribuição abre a inscrição. Aqui se demonstra a segunda metade — e
cada recusa responde como recurso inexistente, porque a existência de uma inscrição não é
enumerável por quem não a alcança (FR-044, FR-045, FR-055).
"""

import pytest
from django.urls import reverse

from processo_seletivo.avaliacoes.application.distribuicao import distribuir
from processo_seletivo.comissoes.application.alocacao import remover_alocacao
from processo_seletivo.comissoes.domain.funcoes import Funcao
from tests.fixtures.comissao import DOCUMENTO_A, alocar_em, constituir, inscrever
from tests.fixtures.comissao import abrir_arquivo as abrir
from tests.fixtures.edital import identificador
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.authorization]


@pytest.fixture
def cenario(raiz_de_arquivos, gestor, processo_a, edital_com_documentos, comissao_de_a, etapa_a1):
    """João avalia a inscrição 0001; Ana avalia a 0002. Cada uma com um documento."""
    ana = constituir(gestor, processo_a, [("ana", Funcao.MEMBRO)], prefixo="doc")["ana"]
    alocacao_do_joao = alocar_em(
        gestor, processo_a, comissao_de_a["joao"], edital_com_documentos, etapa_a1
    )
    alocar_em(gestor, processo_a, ana, edital_com_documentos, etapa_a1)
    do_joao, da_ana = inscrever(
        edital_com_documentos, 2, documentos=[identificador(DOCUMENTO_A, 0)]
    )
    for chave, membro, inscricao in (("j", comissao_de_a["joao"], do_joao), ("a", ana, da_ana)):
        distribuir(
            actor=gestor,
            processo_id=processo_a.id,
            edital_id=edital_com_documentos.id,
            etapa_id=etapa_a1,
            membro_ids=[membro.id],
            inscricao_ids=[inscricao.id],
            idempotency_key=f"doc-{chave}",
            correlation_id="teste",
        )
    return {"do_joao": do_joao, "da_ana": da_ana, "alocacao_do_joao": alocacao_do_joao}


def pagina(edital, etapa_id, inscricao):
    return reverse("interface:mesa-inscricao", args=[edital.id, etapa_id, inscricao.id])


def arquivo(edital, etapa_id, inscricao):
    return reverse(
        "interface:mesa-documento",
        args=[edital.id, etapa_id, inscricao.id, identificador(DOCUMENTO_A, 0)],
    )


def test_o_atribuido_abre_a_inscricao_e_o_documento(
    client, seletor_ligado, edital_com_documentos, etapa_a1, cenario
):
    identificar(client, "joao", [])

    assert (
        client.get(pagina(edital_com_documentos, etapa_a1, cenario["do_joao"])).status_code == 200
    )
    assert (
        abrir(client, arquivo(edital_com_documentos, etapa_a1, cenario["do_joao"])).status_code
        == 200
    )


def test_inscricao_de_outro_avaliador_e_inexistente(
    client, seletor_ligado, edital_com_documentos, etapa_a1, cenario
):
    """**E de nenhuma outra** (SC-004). Trocar o UUID na URL não alcança (FR-045)."""
    identificar(client, "joao", [])

    assert client.get(pagina(edital_com_documentos, etapa_a1, cenario["da_ana"])).status_code == 404
    assert (
        abrir(client, arquivo(edital_com_documentos, etapa_a1, cenario["da_ana"])).status_code
        == 404
    )


def test_alocado_sem_atribuicao_nao_abre_inscricao_alguma(
    client, seletor_ligado, gestor, processo_a, edital_com_documentos, etapa_a1, cenario
):
    """SC-003: alocação abre a porta da Etapa, e não as inscrições dela (FR-023)."""
    from tests.fixtures.comissao import constituir as constituir_outro

    constituir_outro(gestor, processo_a, [("bruno", Funcao.MEMBRO)], prefixo="sem-atrib")
    alocar_em(
        gestor,
        processo_a,
        constituir_outro(gestor, processo_a, [("bruno", Funcao.MEMBRO)], prefixo="sem-atrib")[
            "bruno"
        ],
        edital_com_documentos,
        etapa_a1,
        chave="bruno-a1",
    )
    identificar(client, "bruno", [])

    assert (
        client.get(pagina(edital_com_documentos, etapa_a1, cenario["do_joao"])).status_code == 404
    )
    assert (
        abrir(client, arquivo(edital_com_documentos, etapa_a1, cenario["do_joao"])).status_code
        == 404
    )


def test_remover_a_alocacao_revoga_o_acesso_ao_documento(
    client, seletor_ligado, gestor, processo_a, edital_com_documentos, etapa_a1, cenario
):
    """SC-010, na inscrição: a primeira condição falha, e a Atribuição fica inerte (FR-046)."""
    identificar(client, "joao", [])
    assert (
        abrir(client, arquivo(edital_com_documentos, etapa_a1, cenario["do_joao"])).status_code
        == 200
    )

    remover_alocacao(
        actor=gestor,
        processo_id=processo_a.id,
        alocacao_id=cenario["alocacao_do_joao"].id,
        idempotency_key="tirar-joao",
        correlation_id="teste",
    )

    assert (
        client.get(pagina(edital_com_documentos, etapa_a1, cenario["do_joao"])).status_code == 404
    )
    assert (
        abrir(client, arquivo(edital_com_documentos, etapa_a1, cenario["do_joao"])).status_code
        == 404
    )


def test_escopo_divergente_e_inexistente(
    client, seletor_ligado, edital_com_documentos, etapa_a1, cenario
):
    identificar(client, "joao", [], escopo="outra-unidade")

    assert (
        client.get(pagina(edital_com_documentos, etapa_a1, cenario["do_joao"])).status_code == 404
    )


def test_quem_gere_a_comissao_nao_alcanca_a_mesa_de_outro(
    client, seletor_ligado, edital_com_documentos, etapa_a1, cenario
):
    """Gerir não é atuar: a porta administrativa da 009 existe e é outra (D-005, D-006)."""
    identificar(client, "carlos", ["gestor"])

    assert (
        client.get(pagina(edital_com_documentos, etapa_a1, cenario["do_joao"])).status_code == 404
    )


def test_etapa_de_outro_edital_nao_alcanca_a_inscricao(
    client, seletor_ligado, edital_com_documentos, edital_b, etapa_b1, cenario
):
    identificar(client, "joao", [])

    resposta = client.get(pagina(edital_com_documentos, etapa_b1, cenario["do_joao"]))

    assert resposta.status_code == 404
