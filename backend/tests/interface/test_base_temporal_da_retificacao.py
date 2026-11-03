"""Ato futuro preservado não pode ser a base implícita de uma correção imediata (101)."""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.publicacao import publish_original, retify, try_publish_retification
from tests.interface.conftest import identificar
from tests.interface.test_retificar import campos

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def test_formulario_publica_imediata_sem_sobrescrever_ato_futuro(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    edital = publish_original(api_client, manager_headers, process_payload)
    original = effective_version(edital_id=edital.id)
    futura = timezone.now() + timedelta(days=3)
    ato_futuro = retify(
        api_client,
        edital,
        [{"targetPath": "/title", "operation": "REPLACE", "newValue": "Título futuro"}],
        effective_at=futura,
    )
    publicacao_futura = ato_futuro.publication
    bytes_futuros = bytes(publicacao_futura.canonical_content)
    versoes_anteriores = list(
        VersaoConsolidada.objects.filter(edital=edital).values_list("id", "content_hash")
    )
    identificar(client, "elaboradora.imediata", ["elaborador"])
    url = reverse("interface:retificar", args=[edital.id])
    tela = client.get(url)
    assert tela.context["base"].id == original.id
    assert effective_version(edital_id=edital.id).id == original.id
    resposta = client.post(
        url,
        {
            **campos(original, **{"/title": "Título imediato"}),
            "justificativa": "Correção imediata com ato futuro preservado",
            "confirmar": "1",
            "chave_idempotencia": "base-temporal-imediata-001",
        },
    )
    assert resposta.status_code == 302
    imediata = Retificacao.objects.exclude(pk=ato_futuro.id).get()
    assert effective_version(edital_id=edital.id).content["title"] == original.content["title"]
    publicada = try_publish_retification(api_client, imediata, suffix="imediata")
    assert publicada.status_code == 201, publicada.content
    assert effective_version(edital_id=edital.id).content["title"] == "Título imediato"
    assert effective_version(edital_id=edital.id, at=futura).content["title"] == "Título futuro"
    publicacao_futura.refresh_from_db()
    assert bytes(publicacao_futura.canonical_content) == bytes_futuros
    assert Publicacao.objects.filter(edital=edital).count() == 3
    assert all(
        VersaoConsolidada.objects.filter(pk=pk, content_hash=h).exists()
        for pk, h in versoes_anteriores
    )
