"""As correções de norma da `067` nas portas do Edital, no Edital publicado e na Retificação.

O aviso de conferência de recurso aparece e não impede ato nenhum (D-002, FR-1309); o marco por
sorteio sem arredondamento publica (SC-503); o Edital publicado antes não é recomposto nem
reavaliado (FR-1325, FR-1328); e o consolidado de uma Retificação publicada depois sai pelas regras
novas (FR-1326), sem mudar a forma do conteúdo (FR-1327).
"""

import pytest

from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.retificacoes import advertencias_do_ato
from processo_seletivo.publicacoes.infrastructure import pdf
from processo_seletivo.publicacoes.models import DocumentoPublicado, Publicacao
from tests.fixtures.edital import actor_headers, complete_draft
from tests.fixtures.publicacao import (
    create_retification,
    levar_a_publicacao,
    publish_retification,
)
from tests.unit.publicacoes.test_pdf import texto_de

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

CODIGO = "appeal_schedule_review"
RECURSO = {
    "id": "00000000-0000-4000-8000-000000067e01",
    "type": "Recurso",
    "description": "Prazo para interposição de recurso",
    "startAt": "2030-11-26T03:00:00+00:00",
    "endAt": "2030-11-28T02:59:00+00:00",
    "order": 9,
    "status": "PLANEJADO",
    "location": "",
    "isRegistrationPeriod": False,
}


def _rascunho():
    """O rascunho completo da suíte: marco por sorteio que admite recurso, sem arredondamento."""
    rascunho = complete_draft()
    (marco,) = rascunho["profiles"][0]["classificationMilestones"]
    assert marco["orderProduction"] == "POR_SORTEIO"
    marco["appealWindow"] = {"admits": True, "durationDays": 2, "unit": "DIAS_CORRIDOS"}
    marco["rounding"] = {}
    rascunho["schedule"] = [*rascunho["schedule"], RECURSO]
    return rascunho


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    return Edital.objects.get()


def _corrido(publicacao):
    return " ".join(texto_de(bytes(publicacao.documento.bytes)).split())


def test_a_submissao_devolve_o_aviso_e_o_edital_publica(api_client, edital):
    preparador = actor_headers("preparador", ["edital:elaborar", "edital:submeter"])
    gravado = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        _rascunho(),
        format="json",
        **{**preparador, "HTTP_IF_MATCH": f'"{edital.revision}"'},
    )
    assert gravado.status_code < 400, gravado.content
    edital.refresh_from_db()
    resposta = api_client.post(
        f"/api/v1/admin/editais/{edital.id}/submissoes",
        format="json",
        **{**preparador, "HTTP_IF_MATCH": f'"{edital.revision}"'},
    )
    assert resposta.status_code < 400, resposta.content
    achados = resposta.json()["validationFindings"]
    assert [a["code"] for a in achados].count(CODIGO) == 1
    assert "milestone_rounding_invalid" not in {a["code"] for a in achados}, "SC-503"


def test_o_edital_com_o_aviso_e_o_sorteio_sem_arredondamento_publica_e_imprime_o_novo(
    api_client, edital
):
    publicado = levar_a_publicacao(api_client, edital, draft=_rascunho())
    assert publicado.status == Edital.Status.PUBLICADO

    texto = _corrido(Publicacao.objects.get(edital=publicado))
    assert "Caberá recurso contra o resultado de “" in texto
    assert "Arredondamento" not in texto
    assert "Empate no corte" not in texto


def test_a_pagina_do_edital_publicado_nao_mostra_o_aviso(api_client, edital):
    """FR-1328: o publicado não é reavaliado fora de uma Retificação."""
    from processo_seletivo.interface.views import _pendencias

    publicado = levar_a_publicacao(api_client, edital, draft=_rascunho())
    assert not [p for p in _pendencias(publicado) if p["codigo"] == CODIGO]


def _frase_de_antes(marco, *, objeto=None):
    """A frase sem objeto, como o renderizador da `main` a escrevia antes desta feature."""
    janela = marco.get("appealWindow") or {}
    if janela.get("admits") is False:
        return "Não caberá recurso contra o resultado deste marco."
    prazo = pdf.prazo_do_recurso(marco)
    if not prazo:
        return ""
    return f"Caberá recurso no prazo de {prazo}, contados da divulgação do resultado."


def test_o_publicado_antes_nao_muda_e_a_retificacao_sai_pelas_regras_novas(
    api_client, edital, monkeypatch
):
    with monkeypatch.context() as remendo:
        remendo.setattr(pdf, "_janela_recursal", _frase_de_antes)
        publicado = levar_a_publicacao(api_client, edital, draft=_rascunho())
    original = Publicacao.objects.get(edital=publicado)
    documento = DocumentoPublicado.objects.get(publicacao=original)
    bytes_de_antes = bytes(documento.bytes)
    assert "contados da divulgação do resultado" in _corrido(original)

    # FR-1325: servido como foi gravado, sem recompor.
    servido = api_client.get(f"/api/v1/public/publicacoes/{original.id}/documento")
    assert b"".join(servido.streaming_content if servido.streaming else [servido.content]) == (
        bytes_de_antes
    )

    mudanca = [{"operation": "REPLACE", "targetPath": "/description", "newValue": "Corrigida."}]
    retificacao = create_retification(api_client, publicado, mudanca)
    assert CODIGO in {achado.code for achado in advertencias_do_ato(retificacao)}, "FR-1309"
    publish_retification(api_client, retificacao)
    assert retificacao.status == retificacao.Status.PUBLICADA

    consolidado = Publicacao.objects.filter(edital=publicado).latest("publication_order")
    assert consolidado.pk != original.pk
    texto = _corrido(consolidado)
    assert "Caberá recurso contra o resultado de “" in texto, "FR-1326"
    assert "contados da divulgação do resultado" not in texto
    documento.refresh_from_db()
    assert bytes(documento.bytes) == bytes_de_antes

    # FR-1327: a forma do conteúdo não mudou.
    assert consolidado.canonical_schema_version == original.canonical_schema_version
