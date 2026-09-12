"""Uma relação vigente por recorte, e a garantia é do banco (FR-070, D-014).

**O que a versão anterior do modelo deixava passar.** A sucessão ordenava uma cadeia — a vigente é
a última sem sucessora — e nada impedia que nascessem **duas** cadeias no mesmo recorte, cada uma
com a sua raiz e nenhuma com sucessora. Duas relações vivas são duas escolhas possíveis, e escolher
qual sortear depois de conhecida a semente é exatamente a fresta que esta feature existe para
fechar.

A correção é a mesma cirurgia já aceita para o `AtoDeOrdenacao`: a unicidade de raiz parte em duas
constraints parciais, e a primeira mantém palavra por palavra a garantia de quem não tem lista.
"""

import pytest
from django.db import IntegrityError, transaction

from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.comissao import inscrever, publicar_processo_com_etapas
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.sorteio import LISTA_PCD, LISTA_PPI, relacao

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def cenario(api_client, manager_headers, process_payload):
    edital = publicar_processo_com_etapas(api_client, manager_headers, process_payload)
    versao = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    return edital, versao, inscrever(edital, 3)


def test_duas_raizes_de_ampla_concorrencia_no_mesmo_recorte_sao_recusadas(cenario):
    edital, versao, inscricoes = cenario
    relacao(edital, versao=versao, perfil_id=PROFILE_ID, inscricoes=inscricoes)
    with pytest.raises(IntegrityError, match="uq_relacao_raiz_por_marco"):
        with transaction.atomic():
            relacao(edital, versao=versao, perfil_id=PROFILE_ID, inscricoes=inscricoes)


def test_tres_listas_distintas_do_mesmo_marco_sao_aceitas(cenario):
    edital, versao, inscricoes = cenario
    criadas = [
        relacao(edital, versao=versao, perfil_id=PROFILE_ID, lista_id=lista, inscricoes=inscricoes)
        for lista in (None, LISTA_PPI, LISTA_PCD)
    ]
    assert len({r.id for r in criadas}) == 3
    for gravada in criadas:
        gravada.refresh_from_db()
    assert {str(r.lista_id) if r.lista_id else None for r in criadas} == {
        None,
        LISTA_PPI,
        LISTA_PCD,
    }


def test_duas_raizes_da_mesma_lista_sao_recusadas(cenario):
    edital, versao, inscricoes = cenario
    relacao(edital, versao=versao, perfil_id=PROFILE_ID, lista_id=LISTA_PPI, inscricoes=inscricoes)
    with pytest.raises(IntegrityError, match="uq_relacao_raiz_por_marco_e_lista"):
        with transaction.atomic():
            relacao(
                edital,
                versao=versao,
                perfil_id=PROFILE_ID,
                lista_id=LISTA_PPI,
                inscricoes=inscricoes,
            )


def test_a_cadeia_de_sucessao_continua_admitindo_quantas_sucessoes_o_certame_precisar(cenario):
    edital, versao, inscricoes = cenario
    atual = relacao(edital, versao=versao, perfil_id=PROFILE_ID, inscricoes=inscricoes)
    for volta in range(3):
        atual = relacao(
            edital,
            versao=versao,
            perfil_id=PROFILE_ID,
            inscricoes=inscricoes,
            anterior=atual,
            motivo=f"Resultado de origem sucedido, {volta + 1}ª correção.",
        )
    vigentes = [r for r in edital.relacoes_de_sorteio.all() if not r.sucessoras.exists()]
    assert len(vigentes) == 1
    assert vigentes[0].id == atual.id


def test_sucessora_sem_motivo_e_recusada(cenario):
    edital, versao, inscricoes = cenario
    raiz = relacao(edital, versao=versao, perfil_id=PROFILE_ID, inscricoes=inscricoes)
    with pytest.raises(IntegrityError, match="ck_relacao_sucessao_com_motivo"):
        with transaction.atomic():
            relacao(
                edital, versao=versao, perfil_id=PROFILE_ID, inscricoes=inscricoes, anterior=raiz
            )


def test_uma_relacao_tem_no_maximo_uma_sucessora(cenario):
    edital, versao, inscricoes = cenario
    raiz = relacao(edital, versao=versao, perfil_id=PROFILE_ID, inscricoes=inscricoes)
    relacao(
        edital,
        versao=versao,
        perfil_id=PROFILE_ID,
        inscricoes=inscricoes,
        anterior=raiz,
        motivo="primeira",
    )
    with pytest.raises(IntegrityError, match="uq_relacao_sucessora_unica"):
        with transaction.atomic():
            relacao(
                edital,
                versao=versao,
                perfil_id=PROFILE_ID,
                inscricoes=inscricoes,
                anterior=raiz,
                motivo="segunda",
            )
