"""A cadeia `versão histórica → identidade → resumo publicado → bytes` (020, FR-053, FR-054).

É garantia **interna**: o sistema precisa saber que o que ele entrega é o que a versão afirma. Não
é funcionalidade — expor verificação ao usuário final é decisão de produto e está fora de escopo
(FR-054), e a ausência dessa exposição tem teste próprio aqui.
"""

import hashlib

import pytest
from django.urls import reverse

from processo_seletivo.editais.models import ArtefatoAnexo
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.publicacao import publish_original
from tests.fixtures.snapshot import rascunho_completo

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def publicado(api_client, manager_headers, process_payload):
    return publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_completo(), anexos=2
    )


def test_a_cadeia_fecha_da_versao_ate_os_bytes(client, publicado):
    """Cada elo é conferido contra o seguinte, e o último contra o que a rota entrega."""
    versao = VersaoConsolidada.objects.filter(edital=publicado).latest("materialized_at")

    for anexo in versao.content["attachments"]:
        artefato = ArtefatoAnexo.objects.get(pk=anexo["artifactId"])
        entregue = client.get(reverse("public-anexo", args=[artefato.id]))

        assert anexo["artifactHash"] == artefato.document_hash, "versão → resumo"
        assert artefato.document_hash == hashlib.sha256(bytes(artefato.bytes)).hexdigest(), (
            "resumo → bytes guardados"
        )
        assert hashlib.sha256(entregue.content).hexdigest() == anexo["artifactHash"], (
            "e os bytes entregues são os que a versão afirma"
        )
        assert entregue["ETag"] == f'"{anexo["artifactHash"]}"'


def test_nenhuma_rota_publica_oferece_verificacao_de_integridade():
    """FR-054 — a garantia é interna, e não vira funcionalidade por conta própria.

    Uma rota de "conferir o resumo" mudaria a promessa do sistema: ele passaria a dizer ao público
    que a verificação é dele, e não da instituição. Se um dia for decisão de produto, entra pela
    porta da spec.
    """
    from processo_seletivo.publicacoes.api import public_urls

    caminhos = [str(rota.pattern) for rota in public_urls.urlpatterns]

    for caminho in caminhos:
        assert "verificar" not in caminho
        assert "integridade" not in caminho
        assert "conferir" not in caminho
