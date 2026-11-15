"""O documento da agenda no portal (167, T087, FR-7224, SC-2399, US3 cenário 10, `D-012`).

O servido é o gravado no ato — ainda que o compositor mude depois —, com `ETag` e `attachment`; o
ato de outra agenda, ou sem documento, é 404; e a página pública e a agenda publicada da gestão
levam ao documento da publicação.
"""

import hashlib

import pytest
from django.urls import reverse

from processo_seletivo.agendamento.infrastructure import documento as compositor
from processo_seletivo.agendamento.models import DocumentoDoAtoDaAgenda
from tests.fixtures.agenda_da_etapa import montar_completa, publicar_agenda
from tests.fixtures.comissao import inscrever

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def publicada(gestor, edital_a, etapa_a2):
    inscrever(edital_a, 3)
    montar_completa(gestor, edital_a, etapa_a2)
    return publicar_agenda(gestor, edital_a, etapa_a2)


def _endereco(ato, agenda_id=None):
    return reverse("portal:documento-da-agenda", args=[agenda_id or ato.agenda_id, ato.id])


def test_a_publicacao_grava_um_documento_e_o_portal_o_serve(client, publicada):
    documento = DocumentoDoAtoDaAgenda.objects.get(ato=publicada)
    assert bytes(documento.bytes).startswith(b"%PDF")
    assert documento.documento_hash == hashlib.sha256(bytes(documento.bytes)).hexdigest()

    resposta = client.get(_endereco(publicada))

    assert resposta.status_code == 200
    assert resposta["Content-Type"] == "application/pdf"
    assert resposta["ETag"] == f'"{documento.documento_hash}"'
    assert resposta["Content-Disposition"].startswith("attachment;")
    assert resposta.content == bytes(documento.bytes)


def test_o_servido_e_o_gravado_ainda_que_o_compositor_mude(client, publicada, monkeypatch):
    gravado = bytes(DocumentoDoAtoDaAgenda.objects.get(ato=publicada).bytes)
    monkeypatch.setattr(compositor, "render_agenda_pdf", lambda conteudo: b"%PDF-outro")

    assert client.get(_endereco(publicada)).content == gravado


def test_ato_de_outra_agenda_ou_sem_documento_e_404(client, publicada):
    from uuid import uuid4

    assert client.get(_endereco(publicada, agenda_id=uuid4())).status_code == 404
    outro = type(publicada)(id=uuid4(), agenda_id=publicada.agenda_id)
    assert client.get(_endereco(outro)).status_code == 404


def test_a_pagina_publica_lista_o_documento_da_publicacao(client, publicada):
    corpo = client.get(
        reverse("portal:agenda-da-etapa", args=[publicada.agenda_id])
    ).content.decode()

    assert "Documento da publicação (PDF)" in corpo
    assert _endereco(publicada) in corpo
