"""O recorte transversal no envio: o documento da PPP é pedido em todo Perfil que tem a PPP (044).

É o caso do 903/2026 ao contrário. Lá, o documento publicado exigia o laudo de todo PcD, e o portal
o pediu só no C1: o PcD do C2 enviou sem ele, e o analista o indeferiu por um documento que o
sistema nunca pediu. Aqui, o recorte diz "PPP em todos os Perfis", e o portal pede exatamente isso
(FR-709 a FR-711, SC-262).
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from processo_seletivo.inscricoes.application.rascunho import (
    abrir_inscricao,
    anexar_documento,
    descartes_por_mudanca_de_modalidade,
    gravar_dados,
)
from processo_seletivo.inscricoes.application.submissao import enviar_inscricao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.portal.views import _documentos_anunciados
from processo_seletivo.publicacoes.application.selectors import selecao_publica
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.candidato import (
    MARIA,
    MODALIDADE_AC,
    MODALIDADE_PPP,
    PERFIL_DOCENTE,
    PERFIL_TECNICO,
    pdf,
)
from tests.fixtures.selecao import (
    DOCUMENTO_DA_MODALIDADE,
    DOCUMENTO_DE_TODOS,
    DOCUMENTO_DO_PERFIL,
    MODALIDADE_PPP_TECNICO,
    publicar_selecao,
    rascunho_com_ppp_nos_dois_perfis,
)

DECLARACOES = {"veracidade": True, "ciencia": True}


@pytest.fixture
def selecao_transversal(raiz_de_arquivos, api_client, manager_headers, process_payload):
    return publicar_selecao(
        api_client,
        manager_headers,
        process_payload,
        rascunho=rascunho_com_ppp_nos_dois_perfis(timezone.now() - timedelta(seconds=1)),
    )


def _inscrever(edital, perfil, modalidade, documentos):
    inscricao = abrir_inscricao(identidade=MARIA, edital_id=edital.id, profile_id=perfil)
    inscricao = gravar_dados(
        identidade=MARIA,
        inscricao=inscricao,
        dados={
            "nome": MARIA.nome,
            "cpf": MARIA.cpf,
            "email": MARIA.email,
            "modality_id": modalidade,
        },
    )
    for requisito in documentos:
        anexar_documento(
            identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf()
        )
    inscricao.refresh_from_db()
    return inscricao


def _enviar(inscricao):
    return enviar_inscricao(
        identidade=MARIA, inscricao=inscricao, declaracoes=DECLARACOES, idempotency_key="envio-1"
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_ppp_do_perfil_tecnico_nao_envia_sem_a_autodeclaracao(
    selecao_transversal, candidatos_registrados
):
    inscricao = _inscrever(
        selecao_transversal, PERFIL_TECNICO, MODALIDADE_PPP_TECNICO, [DOCUMENTO_DE_TODOS]
    )

    with pytest.raises(DomainError) as recusa:
        _enviar(inscricao)

    assert recusa.value.code == "missing_required_documents"
    assert "Autodeclaração étnico-racial" in str(recusa.value.detail)


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_ppp_do_perfil_tecnico_envia_com_a_autodeclaracao(
    selecao_transversal, candidatos_registrados
):
    inscricao = _inscrever(
        selecao_transversal,
        PERFIL_TECNICO,
        MODALIDADE_PPP_TECNICO,
        [DOCUMENTO_DE_TODOS, DOCUMENTO_DA_MODALIDADE],
    )

    assert _enviar(inscricao).status == Inscricao.Status.SUBMETIDA


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_ampla_nao_recebe_o_pedido_da_ppp(selecao_transversal, candidatos_registrados):
    inscricao = _inscrever(
        selecao_transversal,
        PERFIL_DOCENTE,
        MODALIDADE_AC,
        [DOCUMENTO_DE_TODOS, DOCUMENTO_DO_PERFIL],
    )

    assert _enviar(inscricao).status == Inscricao.Status.SUBMETIDA


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_cartao_dos_dois_perfis_anuncia_o_documento_da_ppp(selecao_transversal):
    conteudo = selecao_publica(edital_id=selecao_transversal.id).content

    for perfil in conteudo["profiles"]:
        anunciados = _documentos_anunciados(conteudo, perfil)
        acrescimos = {
            grupo["modalidade"]: grupo["documentos"] for grupo in anunciados["por_modalidade"]
        }
        assert acrescimos.get("Pessoas pretas, pardas e indígenas") == [
            "Autodeclaração étnico-racial"
        ], perfil["code"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_trocar_de_ppp_para_ampla_descarta_a_autodeclaracao(
    selecao_transversal, candidatos_registrados
):
    inscricao = _inscrever(
        selecao_transversal,
        PERFIL_DOCENTE,
        MODALIDADE_PPP,
        [DOCUMENTO_DE_TODOS, DOCUMENTO_DA_MODALIDADE],
    )
    conteudo = selecao_publica(edital_id=selecao_transversal.id).content

    descartes = descartes_por_mudanca_de_modalidade(conteudo, inscricao, MODALIDADE_AC)

    assert [str(item["id"]) for item in descartes] == [DOCUMENTO_DA_MODALIDADE]
