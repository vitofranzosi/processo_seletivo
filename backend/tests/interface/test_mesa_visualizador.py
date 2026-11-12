"""A Mesa do avaliador com o visualizador da 157 (FR-6545 a FR-6548; FR-112 da 012, acrescida).

A recusa da entrega legível no painel, a lista de documentos relida depois de uma abertura, e o
download na barra — sem exigência de abertura para avaliar, e com a abertura gravada como antes.
"""

import pytest
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.avaliacoes.application.distribuicao import distribuir
from processo_seletivo.inscricoes.models import DocumentoSubmetido
from tests.fixtures.comissao import DOCUMENTO_A, abrir_arquivo, alocar_em, inscrever
from tests.fixtures.edital import identificador
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def cenario(
    raiz_de_arquivos,
    gestor,
    processo_com_documentos,
    edital_com_documentos,
    comissao_com_documentos,
    etapa_a1,
):
    membro = comissao_com_documentos["joao"]
    alocar_em(gestor, processo_com_documentos, membro, edital_com_documentos, etapa_a1)
    inscricao = inscrever(edital_com_documentos, 1, documentos=[identificador(DOCUMENTO_A, 0)])[0]
    distribuir(
        actor=gestor,
        processo_id=processo_com_documentos.id,
        edital_id=edital_com_documentos.id,
        etapa_id=etapa_a1,
        membro_ids=[membro.id],
        inscricao_ids=[inscricao.id],
        idempotency_key="doc-157",
        correlation_id="teste",
    )
    return inscricao


@pytest.fixture
def como_joao(client, seletor_ligado):
    identificar(client, "joao", [])
    return client


def _rotas(edital, etapa_id, inscricao):
    return {
        "arquivo": reverse(
            "interface:mesa-documento",
            args=[edital.id, etapa_id, inscricao.id, identificador(DOCUMENTO_A, 0)],
        ),
        "lista": reverse("interface:mesa-documentos", args=[edital.id, etapa_id, inscricao.id]),
        "pagina": reverse("interface:mesa-inscricao", args=[edital.id, etapa_id, inscricao.id]),
    }


def _trocar_o_arquivo(inscricao):
    documento = DocumentoSubmetido.objects.get(inscricao=inscricao)
    with documento.arquivo.storage.open(documento.arquivo.name, "wb") as destino:
        destino.write(b"%PDF-1.4\nconteudo trocado")


def test_no_painel_a_recusa_por_integridade_e_legivel(
    como_joao, edital_com_documentos, etapa_a1, cenario
):
    rotas = _rotas(edital_com_documentos, etapa_a1, cenario)
    _trocar_o_arquivo(cenario)

    resposta = como_joao.get(rotas["arquivo"] + "?painel=1")

    assert resposta.status_code == 409
    assert resposta["X-Frame-Options"] == "SAMEORIGIN"
    corpo = resposta.content.decode()
    assert "data-recusa-no-painel" in corpo
    assert "não confere com o que foi recebido" in corpo
    assert RegistroAuditoria.objects.filter(operation="INTEGRIDADE").count() == 1
    assert not RegistroAuditoria.objects.filter(operation="CONSULTAR_DOCUMENTO").exists()


def test_fora_do_painel_a_recusa_continua_a_de_hoje(
    como_joao, edital_com_documentos, etapa_a1, cenario
):
    rotas = _rotas(edital_com_documentos, etapa_a1, cenario)
    _trocar_o_arquivo(cenario)

    resposta = como_joao.get(rotas["arquivo"])

    assert resposta.status_code == 409
    assert "data-recusa-no-painel" not in resposta.content.decode()


def test_a_lista_relida_traz_a_marca_aberto(como_joao, edital_com_documentos, etapa_a1, cenario):
    rotas = _rotas(edital_com_documentos, etapa_a1, cenario)

    antes = como_joao.get(rotas["lista"]).content.decode()
    abrir_arquivo(como_joao, rotas["arquivo"])
    depois = como_joao.get(rotas["lista"]).content.decode()

    assert 'id="documentos-da-inscricao"' in antes
    assert "data-aberto" not in antes
    assert "data-aberto" in depois and ">aberto<" in depois
    assert RegistroAuditoria.objects.filter(operation="CONSULTAR_DOCUMENTO").count() == 1


def test_a_pagina_usa_o_visualizador_com_o_download(
    como_joao, edital_com_documentos, etapa_a1, cenario
):
    pagina = _rotas(edital_com_documentos, etapa_a1, cenario)["pagina"]
    corpo = como_joao.get(pagina).content.decode()

    assert "visualizador.js" in corpo and "mesa.js" not in corpo
    assert "data-visualizador" in corpo and "data-abrir-documento" in corpo
    assert "?baixar=1" in corpo
    assert 'data-prefixo-do-retorno="Voltar ao documento "' in corpo


def test_a_lista_de_outro_avaliador_nao_se_le(
    client, seletor_ligado, edital_com_documentos, etapa_a1, cenario
):
    identificar(client, "estranho", [])
    resposta = client.get(_rotas(edital_com_documentos, etapa_a1, cenario)["lista"])
    assert resposta.status_code in (302, 403, 404)
