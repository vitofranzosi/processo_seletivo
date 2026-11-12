"""O envio de vários documentos da convocação, ponta a ponta pelo cliente de teste (150).

`SC-1800`, `FR-5605`: cada documento do lote é um envio próprio, **idêntico** ao envio de um — a
mesma apresentação, a mesma trilha. E o que muda no meio do lote — o prazo que vence, o resultado
que a comissão registra — vale documento a documento, pela regra de hoje: os anteriores ficam, os
seguintes são recusados (Edge Cases da spec).

O que o script faz no navegador — a ordem, a espera de cada resposta, a frase quando o lote para —
está em `tests/javascript/varios.test.js`; aqui, só o servidor.
"""

import re
from datetime import timedelta
from unittest import mock

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.convocacao.application.documentos import APRESENTAR
from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.convocacao.models import ApresentacaoDeDocumento
from processo_seletivo.identidade.models import CandidateIdentity
from processo_seletivo.portal.identidade import CHAVE_SESSAO
from tests.fixtures import documentos_da_convocacao as cenarios
from tests.fixtures.documentos_da_convocacao import (
    CERTIDAO,
    CERTIFICADO_DO_MEDIO,
    HISTORICO,
    RESIDENCIA,
    comunicar,
    desfechar,
    item,
)

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

QUATRO = (CERTIDAO, HISTORICO, CERTIFICADO_DO_MEDIO, RESIDENCIA)


@pytest.fixture
def aluno(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_aluno(),
        prefixo="portal-varios-150",
    )


def entrar_como(client, inscricao):
    registro, _ = CandidateIdentity.objects.get_or_create(
        subject=inscricao.identity_subject, defaults={"created_at": timezone.now()}
    )
    sessao = client.session
    sessao[CHAVE_SESSAO] = str(registro.pk)
    sessao.save()


def enviar(client, pessoa, alvo, posicao, corpo):
    return client.post(
        reverse("portal:apresentar-documento-da-convocacao", args=[pessoa.id, alvo.id]),
        {"arquivo": cenarios.pdf(corpo)},
        HTTP_X_ENVIO_DE_VARIOS=posicao,
    ).json()


def trilha(pessoa):
    return list(
        RegistroAuditoria.objects.filter(
            actor_subject=pessoa.identity_subject, operation=APRESENTAR
        ).order_by("occurred_at", "event_id")
    )


def test_quatro_no_lote_sao_quatro_envios_como_os_de_um(aluno, gestor, client):
    pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
    entrar_como(client, pessoa)

    resultados = [
        enviar(client, pessoa, item(convocacao, requisito), f"{k}/4", f"doc-{k}".encode())
        for k, requisito in enumerate(QUATRO, start=1)
    ]
    volta = client.get(resultados[-1]["volta"].split("#")[0])

    assert [r["resultado"] for r in resultados] == ["recebido"] * 4
    assert volta.status_code == 200
    apresentacoes = ApresentacaoDeDocumento.objects.filter(item__inscricao=pessoa)
    assert apresentacoes.count() == 4
    assert {str(a.item.requisito_id) for a in apresentacoes} == set(QUATRO)
    assert all(a.numero == 1 and a.content_hash for a in apresentacoes)
    eventos = trilha(pessoa)
    assert len(eventos) == 4
    assert {e.aggregate_id for e in eventos} == {a.id for a in apresentacoes}
    texto = " ".join(re.sub(r"<[^>]+>", " ", volta.content.decode()).split())
    assert "Aguardando conferência: 4" in texto


def test_o_envio_de_um_deixa_a_mesma_trilha(aluno, gestor, client):
    """O mesmo documento, por fora do lote, produz o mesmo evento: o lote não é ato novo."""
    pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
    entrar_como(client, pessoa)
    client.post(
        reverse(
            "portal:apresentar-documento-da-convocacao",
            args=[pessoa.id, item(convocacao, CERTIDAO).id],
        ),
        {"arquivo": cenarios.pdf(b"um")},
    )
    enviar(client, pessoa, item(convocacao, HISTORICO), "1/2", b"dois")

    individual, do_lote = trilha(pessoa)
    assert (individual.operation, individual.aggregate_type) == (
        do_lote.operation,
        do_lote.aggregate_type,
    )
    assert individual.reason.startswith("Apresentação 1 do requisito")
    assert do_lote.reason.startswith("Apresentação 1 do requisito")


def test_o_prazo_que_vence_no_meio_recusa_so_os_seguintes(aluno, gestor, client):
    edital, _, _ = aluno
    pessoa, convocacao = cenarios.convocar_primeira(
        aluno, gestor, vencimento=timezone.now() + timedelta(hours=1)
    )
    comunicar(edital, gestor, convocacao)
    entrar_como(client, pessoa)

    antes = [
        enviar(client, pessoa, item(convocacao, requisito), f"{k}/4", f"a-{k}".encode())
        for k, requisito in enumerate(QUATRO[:2], start=1)
    ]
    with mock.patch("django.utils.timezone.now", return_value=timezone.now() + timedelta(days=2)):
        depois = [
            enviar(client, pessoa, item(convocacao, requisito), f"{k}/4", f"d-{k}".encode())
            for k, requisito in enumerate(QUATRO[2:], start=3)
        ]

    assert [r["resultado"] for r in antes] == ["recebido", "recebido"]
    assert [r["resultado"] for r in depois] == ["recusado", "recusado"]
    assert all(r["frase"].startswith("O prazo terminou em") for r in depois)
    assert depois[-1]["volta"].endswith("#confirmacao"), "algum chegou: a volta é a confirmação"
    assert ApresentacaoDeDocumento.objects.filter(item__inscricao=pessoa).count() == 2


def test_o_resultado_registrado_no_meio_recusa_so_os_seguintes(aluno, gestor, client):
    edital, _, _ = aluno
    pessoa, convocacao = cenarios.convocar_primeira(aluno, gestor)
    entrar_como(client, pessoa)

    primeiro = enviar(client, pessoa, item(convocacao, CERTIDAO), "1/2", b"a")
    desfechar(edital, gestor, convocacao, nomes.DESISTENCIA_EXPRESSA, "desistiu-150")
    segundo = enviar(client, pessoa, item(convocacao, HISTORICO), "2/2", b"b")

    assert primeiro["resultado"] == "recebido"
    assert segundo["resultado"] == "recusado"
    assert "não recebe mais documentos" in segundo["frase"]
    assert ApresentacaoDeDocumento.objects.filter(item__inscricao=pessoa).count() == 1
