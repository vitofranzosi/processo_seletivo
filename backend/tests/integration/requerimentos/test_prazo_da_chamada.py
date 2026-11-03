"""O Requerimento de Matrícula respeita o prazo da chamada (115, FR-3622; FR-374 e FR-408 revistas).

**Uma regra só**, haja ou não documento na chamada: decorrido o vencimento, pela mesma leitura que
admite o não atendimento, o preenchimento, o envio e o sucessor se recusam com a frase dos
documentos. A leitura e o rascunho ficam; o prazo que não começou a correr não fecha nada; e a
correção da convocação com vencimento novo reabre (SC-1093).
"""

from datetime import timedelta
from unittest import mock

import pytest
from django.utils import timezone

from processo_seletivo.convocacao.domain import nomes as nomes_da_convocacao
from processo_seletivo.requerimentos.application import preencher
from processo_seletivo.requerimentos.application.selectors import leitura
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.convocacao import convocar

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def _publicar_declarando(api_client, manager_headers, process_payload, *, draft=None):
    from tests.fixtures.publicacao import publish_original
    from tests.fixtures.requerimento import declarar

    return publish_original(
        api_client,
        manager_headers,
        process_payload,
        draft=draft,
        antes_de_submeter=declarar("AT_CALL"),
    )


@pytest.fixture(params=["com documentos", "sem documentos"])
def certame(request, db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    documentos = (
        cenarios.documentos_do_aluno()
        if request.param == "com documentos"
        else [cenarios.documentos_do_aluno()[0]]
    )
    return cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=documentos,
        prefixo=f"prazo-115-{request.param[:3]}",
        publicar=_publicar_declarando,
    )


def _convocada(certame, gestor, *, comunicar=True):
    edital, _, _ = certame
    pessoa, convocacao = cenarios.convocar_primeira(
        certame, gestor, vencimento=timezone.now() + timedelta(minutes=1)
    )
    if comunicar:
        cenarios.comunicar(edital, gestor, convocacao)
    return pessoa, convocacao


DEPOIS = timedelta(days=2)


def test_depois_do_vencimento_o_requerimento_nao_se_abre_nem_se_envia(certame, gestor):
    pessoa, _ = _convocada(certame, gestor)

    with mock.patch("django.utils.timezone.now", return_value=timezone.now() + DEPOIS):
        apurado = preencher.apurar(pessoa)
        lido = leitura(apurado)
        with pytest.raises(DomainError) as recusa:
            preencher.abrir_rascunho(inscricao=pessoa)

    assert apurado.prazo_decorrido
    assert not lido.pode_escrever
    assert "A comissão vai decidir" in lido.explicacao
    assert recusa.value.code == nomes_da_convocacao.PRAZO_DA_CONVOCACAO_DECORRIDO
    assert "A comissão vai decidir" in recusa.value.detail


def test_o_rascunho_feito_no_prazo_continua_legivel_e_nao_se_envia(certame, gestor):
    pessoa, _ = _convocada(certame, gestor)
    rascunho = preencher.abrir_rascunho(inscricao=pessoa)

    with mock.patch("django.utils.timezone.now", return_value=timezone.now() + DEPOIS):
        with pytest.raises(DomainError) as recusa:
            preencher.gravar(
                inscricao=pessoa, dados={"nome_social": "Maria"}, expected_revision=None
            )
        apurado = preencher.apurar(pessoa)

    assert recusa.value.code == nomes_da_convocacao.PRAZO_DA_CONVOCACAO_DECORRIDO
    rascunho.refresh_from_db()
    assert rascunho.status == "RASCUNHO", "o rascunho não é apagado nem convertido"
    from processo_seletivo.requerimentos.domain import nomes

    assert apurado.estado_de_leitura == nomes.EM_PREENCHIMENTO, "um dos cinco estados da FR-405"


def test_sem_a_comunicacao_o_prazo_nao_corre(certame, gestor):
    pessoa, _ = _convocada(certame, gestor, comunicar=False)

    with mock.patch("django.utils.timezone.now", return_value=timezone.now() + DEPOIS):
        apurado = preencher.apurar(pessoa)
        rascunho = preencher.abrir_rascunho(inscricao=pessoa)

    assert not apurado.prazo_decorrido
    assert rascunho is not None


def test_a_correcao_com_vencimento_novo_reabre(certame, gestor):
    edital, _, _ = certame
    pessoa, _ = _convocada(certame, gestor)
    depois = timezone.now() + DEPOIS

    with mock.patch("django.utils.timezone.now", return_value=depois):
        declarado = convocar(
            edital,
            gestor,
            pessoa.id,
            idempotency_key="prazo-novo",
            motivo="Prazo reaberto pela comissão.",
            vencimento=depois + timedelta(days=3),
        )
        from processo_seletivo.convocacao.models import Convocacao

        cenarios.comunicar(
            edital, gestor, Convocacao.objects.get(id=declarado["id"]), chave="de-novo"
        )
        rascunho = preencher.abrir_rascunho(inscricao=pessoa)

    assert rascunho is not None
