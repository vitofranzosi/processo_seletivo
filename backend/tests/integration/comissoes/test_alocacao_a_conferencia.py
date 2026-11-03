"""Quem confere os documentos da convocação: o predicado único e a alocação (115, US5, D-010).

D-010, aprovada pelo usuário: a presidência e quem tem a autorização de gerir a comissão conferem e
desfecham; o membro alocado à conferência **só confere**, e a restrição por Perfil se preserva.
"""

import pytest

from processo_seletivo.comissoes.application.alocacao import (
    alocar_a_conferencia,
    revogar_alocacao_a_conferencia,
)
from processo_seletivo.comissoes.application.comissao import remover_membro
from processo_seletivo.comissoes.domain.autorizacao import (
    BASE_CONFERENCIA,
    perfis_da_conferencia,
    pode_conferir_documentos,
)
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.documentos_da_convocacao import CERTIDAO, apresentar, conferir, desfechar
from tests.fixtures.edital import PROFILE_ID

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

OUTRO_PERFIL = "00000000-0000-4000-8000-0000000115ff"


@pytest.fixture
def aluno(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_aluno(),
        prefixo="alocacao-115",
    )


MARIA = ator_institucional("maria")
JOAO = ator_institucional("joao")


def _alocar(edital, gestor, membro_subject, *, perfil=None, chave="alocar-115"):
    from processo_seletivo.comissoes.models import MembroComissao

    membro = MembroComissao.objects.get(
        processo=edital.processo, identity_subject=membro_subject, ativo=True
    )
    alocacao, _ = alocar_a_conferencia(
        actor=gestor,
        processo_id=edital.processo_id,
        membro_id=membro.id,
        edital_id=edital.id,
        perfil_id=perfil,
        idempotency_key=chave,
        correlation_id="teste-115",
    )
    return alocacao


def test_quem_desfecha_confere(aluno, gestor):
    edital, _, _ = aluno

    assert pode_conferir_documentos(gestor, edital, PROFILE_ID) is not None
    assert pode_conferir_documentos(MARIA, edital, PROFILE_ID) is not None, "a presidência"
    assert perfis_da_conferencia(MARIA, edital) is None, "todos os Perfis"


def test_o_membro_so_alocado_a_etapa_nao_confere(aluno):
    edital, _, _ = aluno

    assert pode_conferir_documentos(JOAO, edital, PROFILE_ID) is None
    assert perfis_da_conferencia(JOAO, edital) == set()


def test_o_membro_alocado_confere_e_nao_desfecha(aluno, gestor):
    edital, _, _ = aluno
    alocacao = _alocar(edital, gestor, "joao")
    pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
    apresentar(pessoa, convocacao, CERTIDAO)

    base = pode_conferir_documentos(JOAO, edital, PROFILE_ID)
    assert base is not None and base.permissao == BASE_CONFERENCIA
    conferencia = conferir(JOAO, convocacao, CERTIDAO, "CONFORME", chave="joao-confere")
    assert conferencia.conferido_por == "joao"
    assert alocacao.unidade_de_atuacao == gestor.institution_scope

    with pytest.raises(DomainError) as recusa:
        desfechar(edital, JOAO, convocacao, nomes.INDEFERIMENTO, "joao-desfecha", "Sem base.")
    assert recusa.value.status == 404


def test_a_alocacao_restrita_a_outro_perfil_nao_alcanca(aluno, gestor):
    edital, _, _ = aluno
    _alocar(edital, gestor, "joao", perfil=OUTRO_PERFIL)
    pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
    apresentar(pessoa, convocacao, CERTIDAO)

    assert pode_conferir_documentos(JOAO, edital, PROFILE_ID) is None
    assert perfis_da_conferencia(JOAO, edital) == {OUTRO_PERFIL}
    with pytest.raises(DomainError) as recusa:
        conferir(JOAO, convocacao, CERTIDAO, "CONFORME", chave="joao-fora")
    assert recusa.value.status == 404


def test_a_revogacao_e_a_saida_da_comissao_tiram_o_alcance_na_hora(aluno, gestor):
    edital, _, _ = aluno
    alocacao = _alocar(edital, gestor, "joao")
    revogar_alocacao_a_conferencia(
        actor=gestor,
        processo_id=edital.processo_id,
        alocacao_id=alocacao.id,
        idempotency_key="revogar-115",
        correlation_id="teste-115",
    )
    assert pode_conferir_documentos(JOAO, edital, PROFILE_ID) is None

    _alocar(edital, gestor, "joao", chave="alocar-de-novo")
    assert pode_conferir_documentos(JOAO, edital, PROFILE_ID) is not None
    remover_membro(
        actor=gestor,
        processo_id=edital.processo_id,
        membro_id=alocacao.membro_id,
        idempotency_key="remover-joao",
        correlation_id="teste-115",
    )
    assert pode_conferir_documentos(JOAO, edital, PROFILE_ID) is None


def test_ator_de_outra_unidade_nao_confere(aluno):
    edital, _, _ = aluno
    de_fora = ator_institucional("carlos", "comissao:gerir", escopo="campus-alegre")

    assert pode_conferir_documentos(de_fora, edital, PROFILE_ID) is None


def test_o_membro_alocado_nao_aloca(aluno, gestor):
    edital, _, _ = aluno
    _alocar(edital, gestor, "joao")

    with pytest.raises(DomainError) as recusa:
        _alocar(edital, JOAO, "maria", chave="joao-aloca")
    assert recusa.value.status == 404
