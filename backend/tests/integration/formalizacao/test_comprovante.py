"""O comprovante da verificação: assinado, de 15 minutos, do ator que verificou (117, FR-3689a).

Todos os casos recusam **sem ler arquivo**: o comprovante é conferido antes de qualquer leitura, e a
contagem de leituras é a prova (SC-1113). O reuso dentro da validade é outra exportação registrada.
"""

import hashlib
import time

import pytest
from django.core import signing
from django.utils import timezone

from processo_seletivo.formalizacao.application import comprovante as servico
from processo_seletivo.formalizacao.domain import nomes
from processo_seletivo.formalizacao.models import (
    ExportacaoDeFormalizacao,
    RevogacaoDaDesignacao,
)
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.formalizacao import definir_documentos, designar_direto
from tests.integration.formalizacao.apoio import (
    baixar,
    comprovante_da,
    contar_leituras,
    verificar,
)
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def emitido(cenario, gestor, client, seletor):
    definir_documentos(cenario.edital, gestor)
    designar_direto(cenario.edital, "rui")
    designar_direto(cenario.edital, "bia")
    identificar(client, "rui", ["formalizacao"])
    return comprovante_da(verificar(client, cenario.edital))


def _recusado_sem_ler(client, cenario, comprovante, monkeypatch, *, frase, status=409):
    lidas = contar_leituras(monkeypatch)
    resposta = baixar(client, cenario.edital, comprovante)
    assert resposta.status_code == status
    if frase:
        assert frase in resposta.content.decode()
    assert lidas == []
    assert not ExportacaoDeFormalizacao.objects.exists()
    return resposta


def test_adulterado_num_byte_e_invalido(cenario, client, emitido, monkeypatch):
    meio = len(emitido) // 2
    trocado = emitido[:meio] + ("A" if emitido[meio] != "A" else "B") + emitido[meio + 1 :]
    _recusado_sem_ler(client, cenario, trocado, monkeypatch, frase=nomes.INVALIDA)


def test_um_resumo_sha256_montado_a_mao_e_invalido(cenario, client, emitido, monkeypatch):
    fabricado = hashlib.sha256(b"edital, designacao, pessoas, definicao").hexdigest()
    _recusado_sem_ler(client, cenario, fabricado, monkeypatch, frase=nomes.INVALIDA)


def test_assinado_com_outro_sal_e_invalido(cenario, client, emitido, monkeypatch):
    payload = signing.loads(emitido, salt=nomes.SAL_DO_COMPROVANTE)
    outro = signing.dumps(payload, salt="outra.parte.do.sistema", compress=True)
    _recusado_sem_ler(client, cenario, outro, monkeypatch, frase=nomes.INVALIDA)


def test_expirado_depois_de_15_minutos(cenario, client, emitido, monkeypatch):
    class Adiante:
        @staticmethod
        def time():
            return time.time() + nomes.VALIDADE_DO_COMPROVANTE + 60

    monkeypatch.setattr(signing, "time", Adiante)
    resposta = _recusado_sem_ler(client, cenario, emitido, monkeypatch, frase=nomes.EXPIRADA)
    assert "Verificar de novo" in resposta.content.decode()


def test_emitido_para_outro_servidor_e_invalido(cenario, client, emitido, monkeypatch):
    """O comprovante de Rui, apresentado por Bia, também designada: inválido, nada lido."""
    identificar(client, "bia", ["formalizacao"])
    _recusado_sem_ler(client, cenario, emitido, monkeypatch, frase=nomes.INVALIDA)


def test_emitido_para_outra_unidade_e_invalido(emitido):
    de_outra_unidade = Actor("rui", "outra", frozenset({nomes.CAPACIDADE}))
    with pytest.raises(DomainError) as recusa:
        servico.conferir(de_outra_unidade, emitido)
    assert recusa.value.code == nomes.VERIFICACAO_INVALIDA


def test_depois_da_revogacao_do_papel_e_recusa_de_autorizacao(
    cenario, client, emitido, monkeypatch
):
    identificar(client, "rui", ["integrante-sem-papel"])
    _recusado_sem_ler(client, cenario, emitido, monkeypatch, frase="", status=403)


def test_depois_da_revogacao_da_designacao_e_inexistente(cenario, client, emitido, monkeypatch):
    RevogacaoDaDesignacao.objects.create(
        designacao=cenario.edital.designacoes_da_formalizacao.get(pessoa="rui"),
        motivo="Saiu",
        revogado_por="gil",
        unidade_de_atuacao="cefor",
        revogado_em=timezone.now(),
    )
    _recusado_sem_ler(client, cenario, emitido, monkeypatch, frase="", status=404)


def test_o_reuso_dentro_da_validade_e_outra_exportacao_registrada(cenario, client, emitido):
    """Sem tabela de comprovantes, repetir é clicar de novo: cada uso tem o seu registro."""
    from tests.fixtures.formalizacao import servido

    for _ in range(2):
        resposta = baixar(client, cenario.edital, emitido)
        assert resposta.status_code == 200
        servido(resposta)
    assert ExportacaoDeFormalizacao.objects.count() == 2


def test_o_comprovante_nao_leva_dado_pessoal(cenario, emitido):
    """Assinado, e não cifrado: quem o tem lê os campos, e por isso só há identificadores."""
    payload = signing.loads(emitido, salt=nomes.SAL_DO_COMPROVANTE)
    texto = str(payload)
    for inscricao in cenario.inscricoes_aptas:
        assert inscricao.nome not in texto
        assert inscricao.protocolo not in texto
    assert "111.444.777-35" not in texto
    assert set(payload) == {
        "v",
        "sujeito",
        "unidade",
        "edital",
        "designacao",
        "alcance",
        "perfil",
        "pessoas",
        "definicao",
        "resultado",
        "incluidas",
        "total",
        "resumo",
        "emitido_em",
    }
