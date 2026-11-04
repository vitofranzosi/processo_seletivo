"""O GPS não declara o que não aconteceu (117, US5, FR-3691, FR-3694 a FR-3698, FR-3703, FR-3714).

Arquivo ausente, divergência, limite e exceção inesperada: em nenhum caso a resposta é 500 genérico,
nada é servido pela metade e nenhum registro afirma um pacote que não foi gerado. Os logs não levam
nome, CPF nem nome de arquivo (FR-3703).
"""

import logging

import pytest
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.formalizacao.domain import nomes
from processo_seletivo.formalizacao.models import ExportacaoDeFormalizacao
from tests.fixtures.comissao import abrir_arquivo
from tests.fixtures.formalizacao import (
    definir_documentos,
    designar_direto,
    falhar_na_montagem,
    servido,
)
from tests.integration.formalizacao.apoio import (
    adulterar,
    apagar,
    baixar,
    comprovante_da,
    contar_leituras,
    documentos_de,
    verificar,
)
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def pronto(cenario, gestor, client, seletor):
    definir_documentos(cenario.edital, gestor)
    designar_direto(cenario.edital, "rui")
    identificar(client, "rui", ["formalizacao"])
    return cenario


def test_ausente_e_divergente_vao_para_a_trilha_sem_nome_de_arquivo(pronto, client):
    ausente = documentos_de(pronto.edital, pronto.inscricoes_aptas[0])[0]
    divergente = documentos_de(pronto.edital, pronto.inscricoes_aptas[1])[2]
    apagar(ausente)
    adulterar(divergente)

    resposta = verificar(client, pronto.edital)
    assert resposta.status_code == 200

    indisponivel = RegistroAuditoria.objects.get(operation=nomes.ARQUIVO_INDISPONIVEL)
    assert indisponivel.aggregate_id == ausente.objeto.pk
    integridade = RegistroAuditoria.objects.get(operation="INTEGRIDADE")
    assert integridade.aggregate_id == divergente.objeto.pk
    for evento in (indisponivel, integridade):
        assert "documento enviado.pdf" not in evento.reason
        assert evento.reason.startswith("requisito ")


def test_na_montagem_a_falha_tambem_e_registrada(pronto, client):
    apagar(documentos_de(pronto.edital, pronto.inscricoes_aptas[0])[0])
    comprovante = comprovante_da(verificar(client, pronto.edital))
    servido(baixar(client, pronto.edital, comprovante))

    assert RegistroAuditoria.objects.filter(operation=nomes.ARQUIVO_INDISPONIVEL).count() == 2
    assert ExportacaoDeFormalizacao.objects.get().resultado == nomes.PARCIAL


def test_o_arquivo_ausente_na_pagina_do_setor_e_indisponivel_e_nao_500(pronto, client):
    documento = documentos_de(pronto.edital, pronto.inscricoes_aptas[0])[0]
    apagar(documento)
    url = reverse(
        "interface:formalizacao-documento",
        args=[
            pronto.edital.id,
            pronto.inscricoes_aptas[0].id,
            documento.origem,
            documento.objeto_id,
        ],
    )
    resposta = abrir_arquivo(client, url)

    assert resposta.status_code == 409
    assert "Arquivo indisponível" in resposta.content.decode()
    assert RegistroAuditoria.objects.filter(operation=nomes.ARQUIVO_INDISPONIVEL).exists()


def test_o_limite_recusa_antes_de_ler_e_mostra_o_tamanho_por_pessoa(
    pronto, client, settings, monkeypatch
):
    """FR-3691: acima do limite configurado, recusa antes de qualquer leitura."""
    settings.EXPORTACAO_DE_FORMALIZACAO_LIMITE_MB = 0
    lidas = contar_leituras(monkeypatch)
    resposta = verificar(client, pronto.edital)

    assert resposta.status_code == 409
    corpo = resposta.content.decode()
    assert "acima do limite" in corpo
    assert "Tamanho de cada pessoa" in corpo
    for inscricao in pronto.inscricoes_aptas:
        assert inscricao.protocolo in corpo
    assert lidas == []
    assert RegistroAuditoria.objects.filter(
        operation=nomes.RECUSAR, reason=nomes.RECUSA_LIMITE
    ).exists()


def test_a_excecao_na_montagem_e_desfeita_e_dita(pronto, client, monkeypatch):
    """FR-3714: rollback, sem registro, página própria, e o evento em transação própria."""
    comprovante = comprovante_da(verificar(client, pronto.edital))
    falhar_na_montagem(monkeypatch)

    resposta = baixar(client, pronto.edital, comprovante)
    assert resposta.status_code == 500
    assert resposta["Content-Type"].startswith("text/html")
    assert nomes.INTERROMPIDA in resposta.content.decode()
    assert not ExportacaoDeFormalizacao.objects.exists()
    assert not RegistroAuditoria.objects.filter(operation=nomes.EXPORTAR).exists()
    interrompida = RegistroAuditoria.objects.get(operation=nomes.INTERROMPER)
    assert interrompida.reason == "RuntimeError"
    assert "falha injetada" not in interrompida.reason


def test_a_excecao_na_verificacao_tambem(pronto, client, monkeypatch):
    from processo_seletivo.formalizacao.application import exportar

    def quebrar(*args, **kwargs):
        raise OSError("disco")

    monkeypatch.setattr(exportar, "_ler", quebrar)
    resposta = verificar(client, pronto.edital)
    assert resposta.status_code == 500
    assert nomes.INTERROMPIDA in resposta.content.decode()
    assert RegistroAuditoria.objects.filter(operation=nomes.INTERROMPER).exists()
    assert not RegistroAuditoria.objects.filter(operation=nomes.VERIFICAR).exists()


def test_os_logs_das_falhas_nao_levam_dado_pessoal(pronto, client, monkeypatch, caplog):
    """FR-3703: nem nome, nem CPF, nem nome de arquivo, em nenhum log de aplicação ou de erro."""
    apagar(documentos_de(pronto.edital, pronto.inscricoes_aptas[0])[0])
    adulterar(documentos_de(pronto.edital, pronto.inscricoes_aptas[1])[1])
    # Os loggers do projeto e o de requisições não propagam (settings): o `caplog` se pendura nos
    # dois, e é o que o console de produção receberia.
    for nome in ("processo_seletivo", "django.request"):
        monkeypatch.setattr(logging.getLogger(nome), "handlers", [caplog.handler])
    with caplog.at_level(logging.DEBUG):
        comprovante = comprovante_da(verificar(client, pronto.edital))
        falhar_na_montagem(monkeypatch)
        baixar(client, pronto.edital, comprovante)
        apagar(documentos_de(pronto.edital, pronto.inscricoes_aptas[2])[0])
        client.post(
            reverse(
                "interface:formalizacao-exportar-pessoa",
                args=[pronto.edital.id, pronto.inscricoes_aptas[2].id],
            )
        )

    texto = caplog.text
    assert caplog.records, "a interrupção precisa deixar rastro no log"
    for inscricao in pronto.inscricoes_aptas:
        assert inscricao.nome not in texto
    assert "111.444.777-35" not in texto
    assert "11144477735" not in texto
    assert "documento enviado.pdf" not in texto
