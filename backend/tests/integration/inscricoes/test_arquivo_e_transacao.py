"""Disco e banco não são a mesma transação — e a ordem entre eles é regra (US4 da 009).

O sistema de arquivos não volta atrás. Um rollback depois de o arquivo ter sido apagado devolve o
registro apontando para o vazio; um rollback depois de o arquivo novo ter sido escrito deixa
órfão o que ninguém mais alcança. Nenhum dos dois quebra nada visível no momento — aparecem
depois, quando alguém abre o documento.

Estes testes injetam falha **depois** da escrita para provar as duas garantias: o que foi escrito
e não confirmado é removido, e o que foi confirmado permanece.
"""

from unittest import mock

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.application import rascunho
from processo_seletivo.inscricoes.models import DocumentoSubmetido
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, MODALIDADE_PPP, identificar, pdf
from tests.fixtures.selecao import DOCUMENTO_DA_MODALIDADE, DOCUMENTO_DE_TODOS


def _arquivos_em(raiz):
    return sorted(caminho for caminho in raiz.rglob("*.pdf"))


def _anexar(inscricao, requisito=DOCUMENTO_DE_TODOS, nome="rg.pdf"):
    return rascunho.anexar_documento(
        identidade=MARIA, inscricao=inscricao, requirement_id=requisito, arquivo=pdf(nome)
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_falha_apos_a_escrita_nao_deixa_arquivo_orfao(
    inscricao_de_maria, raiz_de_arquivos
):
    """Primeiro envio: se a transação não chega ao fim, o arquivo escrito não fica para trás."""
    with mock.patch.object(rascunho, "record_event", side_effect=RuntimeError("falha injetada")):
        with pytest.raises(RuntimeError):
            _anexar(inscricao_de_maria)

    assert DocumentoSubmetido.objects.count() == 0
    assert _arquivos_em(raiz_de_arquivos) == [], "nada de arquivo sem registro"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_falha_na_substituicao_preserva_o_arquivo_anterior(
    inscricao_de_maria, raiz_de_arquivos
):
    """Substituição: o registro que volta pelo rollback aponta para um arquivo que existe."""
    _anexar(inscricao_de_maria, nome="primeiro.pdf")
    original = DocumentoSubmetido.objects.get()
    caminho_original = raiz_de_arquivos / original.arquivo.name

    with mock.patch.object(rascunho, "record_event", side_effect=RuntimeError("falha injetada")):
        with pytest.raises(RuntimeError):
            _anexar(inscricao_de_maria, nome="segundo.pdf")

    preservado = DocumentoSubmetido.objects.get()
    assert preservado.nome_original == "primeiro.pdf"
    assert caminho_original.exists(), "o arquivo do registro que sobreviveu continua no disco"
    assert _arquivos_em(raiz_de_arquivos) == [caminho_original], "e o novo não ficou órfão"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_substituicao_confirmada_apaga_o_anterior_do_disco(
    inscricao_de_maria, raiz_de_arquivos
):
    _anexar(inscricao_de_maria, nome="primeiro.pdf")
    caminho_original = raiz_de_arquivos / DocumentoSubmetido.objects.get().arquivo.name

    _anexar(inscricao_de_maria, nome="segundo.pdf")

    assert not caminho_original.exists()
    assert len(_arquivos_em(raiz_de_arquivos)) == 1
    assert DocumentoSubmetido.objects.get().nome_original == "segundo.pdf"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_falha_na_remocao_preserva_o_arquivo(inscricao_de_maria, raiz_de_arquivos):
    _anexar(inscricao_de_maria)
    caminho = raiz_de_arquivos / DocumentoSubmetido.objects.get().arquivo.name

    with mock.patch.object(rascunho, "record_event", side_effect=RuntimeError("falha injetada")):
        with pytest.raises(RuntimeError):
            rascunho.remover_documento(
                identidade=MARIA,
                inscricao=inscricao_de_maria,
                requirement_id=DOCUMENTO_DE_TODOS,
            )

    assert DocumentoSubmetido.objects.count() == 1
    assert caminho.exists(), "o registro voltou pelo rollback, e o arquivo dele também"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_retificacao_nao_apaga_documento_a_cada_continuar(
    client, inscricao_de_maria, raiz_de_arquivos
):
    """O descarte é da mudança de modalidade confirmada — e de nada além.

    Um requisito que deixou de se aplicar por outro motivo não pode desaparecer só porque a pessoa
    apertou `Continuar`: seria apagar arquivo em silêncio, sem que ela tivesse mudado nada.
    """
    identificar(client, MARIA)
    _anexar(inscricao_de_maria)

    for _ in range(3):
        client.post(
            reverse("portal:inscricao", args=[inscricao_de_maria.id]),
            {"modalidade": MODALIDADE_AC},
        )

    assert DocumentoSubmetido.objects.count() == 1
    assert len(_arquivos_em(raiz_de_arquivos)) == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_confirmacao_velha_e_recusada_em_vez_de_apagar(client, inscricao_de_maria):
    """A lista recomputada sob trava tem de coincidir com a que a pessoa viu."""
    identificar(client, MARIA)
    client.post(
        reverse("portal:inscricao", args=[inscricao_de_maria.id]),
        {"modalidade": MODALIDADE_PPP, "confirmar_descarte": "1"},
    )
    rascunho.anexar_documento(
        identidade=MARIA,
        inscricao=inscricao_de_maria,
        requirement_id=DOCUMENTO_DA_MODALIDADE,
        arquivo=pdf("autodeclaracao.pdf"),
    )
    inscricao_de_maria.refresh_from_db()

    with pytest.raises(Exception) as recusa:
        rascunho.gravar_dados(
            identidade=MARIA,
            inscricao=inscricao_de_maria,
            dados={"modality_id": MODALIDADE_AC},
            descartes_confirmados=[],
        )

    assert "descartar" in str(recusa.value)
    assert DocumentoSubmetido.objects.count() == 1, "nada foi apagado sem confirmação"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_mudanca_e_o_descarte_acontecem_juntos(client, inscricao_de_maria, raiz_de_arquivos):
    """Um comando, uma transação: não existe modalidade nova com descarte pela metade."""
    identificar(client, MARIA)
    client.post(
        reverse("portal:inscricao", args=[inscricao_de_maria.id]),
        {"modalidade": MODALIDADE_PPP, "confirmar_descarte": "1"},
    )
    rascunho.anexar_documento(
        identidade=MARIA,
        inscricao=inscricao_de_maria,
        requirement_id=DOCUMENTO_DA_MODALIDADE,
        arquivo=pdf("autodeclaracao.pdf"),
    )

    client.post(
        reverse("portal:inscricao", args=[inscricao_de_maria.id]),
        {"modalidade": MODALIDADE_AC, "confirmar_descarte": "1"},
    )

    inscricao_de_maria.refresh_from_db()
    assert str(inscricao_de_maria.modality_id) == MODALIDADE_AC
    assert DocumentoSubmetido.objects.count() == 0
    assert _arquivos_em(raiz_de_arquivos) == [], "o disco seguiu o banco"
