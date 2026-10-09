"""A numeração digitada nas portas do Edital, no Edital publicado e na Retificação (065).

O conflito comprovado impede a submissão e a publicação do Edital (D-001, User Story 3); o Edital já
publicado não é reavaliado nem recomposto (FR-1218, User Story 4); e na Retificação tudo é aviso —
inclusive o conflito que ela mesma introduz, que a confirmação mostra e não bloqueia (D-002, D-006).
"""

import pytest
from django.urls import reverse

from processo_seletivo.editais.domain import secoes, validation
from processo_seletivo.editais.domain.validation import (
    ATO_DE_PUBLICACAO,
    CODIGOS_DA_NUMERACAO_DIGITADA,
    CONFLITO_DE_NUMERACAO,
    CONFLITO_DE_NUMERACAO_NA_RETIFICACAO,
    REMISSAO_SEM_DESTINO,
    blocking_findings,
    validate_for_publication,
)
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.retificacoes import advertencias_do_ato
from processo_seletivo.publicacoes.models import DocumentoPublicado
from tests.fixtures.edital import actor_headers, complete_draft
from tests.fixtures.publicacao import (
    create_retification,
    levar_a_publicacao,
    publish_retification,
)

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

# Com o rascunho mínimo, as seções que saem são: Disposições Preliminares (1), Informações Gerais
# (2), Perfis de Vaga (3) e Da Inscrição (4) — e o Cronograma depois.
COERENTE = {
    "disposicoes-preliminares": "O processo seletivo será conduzido pela Comissão.",
    "informacoes-gerais": "O curso é a distância.",
    "inscricao": (
        "4.1 A inscrição será feita pela internet.\n4.2 O candidato anexará os documentos."
    ),
}


def _rascunho(**textos):
    rascunho = complete_draft()
    rascunho["sections"] = [{"key": chave, "content": texto} for chave, texto in textos.items()]
    return rascunho


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    return Edital.objects.get()


def _gravar_e_submeter(api_client, edital, rascunho):
    preparador = actor_headers("preparador", ["edital:elaborar", "edital:submeter"])
    gravado = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        rascunho,
        format="json",
        **{**preparador, "HTTP_IF_MATCH": f'"{edital.revision}"'},
    )
    assert gravado.status_code < 400, gravado.content
    edital.refresh_from_db()
    return api_client.post(
        f"/api/v1/admin/editais/{edital.id}/submissoes",
        format="json",
        **{**preparador, "HTTP_IF_MATCH": f'"{edital.revision}"'},
    )


# --- as portas do Edital (User Story 3) ------------------------------------------------------


def test_a_submissao_com_conflito_e_recusada_nomeando_secao_e_paragrafos(api_client, edital):
    texto = "9.1 A inscrição será feita pela internet.\n9.2 O candidato anexará os documentos."
    resposta = _gravar_e_submeter(api_client, edital, _rascunho(**{**COERENTE, "inscricao": texto}))
    assert resposta.status_code == 422, resposta.content
    corpo = resposta.content.decode()
    assert "blocking_findings" in corpo
    assert "«Da Inscrição»" in corpo
    assert "como 4" in corpo
    assert "«9.1 A inscrição será feita pela internet.»" in corpo
    edital.refresh_from_db()
    assert edital.status == Edital.Status.EM_ELABORACAO


def test_a_submissao_so_com_aviso_e_aceita_e_o_aviso_volta_na_resposta(api_client, edital):
    textos = {**COERENTE, "informacoes-gerais": "Vale o disposto no item 7.3."}
    resposta = _gravar_e_submeter(api_client, edital, _rascunho(**textos))
    assert resposta.status_code < 400, resposta.content
    codigos = {achado["code"] for achado in resposta.json()["validationFindings"]}
    assert REMISSAO_SEM_DESTINO in codigos
    assert CONFLITO_DE_NUMERACAO not in codigos


def test_a_publicacao_aplica_a_mesma_regra():
    """A publicação reconfere com `validate_for_publication(ato=publicação)` — a mesma chamada.

    Entre a homologação e a publicação o rascunho não muda, e não há como produzir pela API um
    conflito que só a publicação veja; por isso a regra é presa pela chamada que `publish_edital`
    faz, sobre um conteúdo com conflito.
    """
    conteudo = {
        "schemaVersion": 17,
        "sections": [
            {
                "id": f"00000000-0000-0000-0000-{secao.order:012d}",
                "key": secao.key,
                "title": secao.title,
                "order": secao.order,
                "type": secao.type,
                **(
                    {"source": secao.source}
                    if secao.gerada
                    else {"content": "9.1 Texto." if secao.key == "inscricao" else ""}
                ),
            }
            for secao in secoes.CATALOGO
        ],
    }
    impeditivos = blocking_findings(validate_for_publication(conteudo, ato=ATO_DE_PUBLICACAO))
    assert CONFLITO_DE_NUMERACAO in {achado.code for achado in impeditivos}


# --- o Edital publicado (User Story 4, FR-1218) ----------------------------------------------


def test_o_edital_publicado_com_conflito_nao_e_reavaliado_nem_recomposto(
    api_client, edital, monkeypatch
):
    """Publicado antes da regra: a conferência é desligada só no instante de publicar."""
    from processo_seletivo.interface.views import _pendencias

    texto = "9.1 A inscrição será feita pela internet."
    with monkeypatch.context() as remendo:
        remendo.setattr(validation, "_numeracao_e_remissoes", lambda snapshot, *, ato: [])
        publicado = levar_a_publicacao(
            api_client, edital, draft=_rascunho(**{**COERENTE, "inscricao": texto})
        )
    documento = DocumentoPublicado.objects.get(publicacao__edital=publicado)
    bytes_de_antes = bytes(documento.bytes)

    assert publicado.status == Edital.Status.PUBLICADO
    pendencias = _pendencias(publicado)
    assert not [p for p in pendencias if p["codigo"] in CODIGOS_DA_NUMERACAO_DIGITADA]
    documento.refresh_from_db()
    assert bytes(documento.bytes) == bytes_de_antes


# --- a Retificação (User Story 4, FR-1213, D-002, D-006, SC-470) ------------------------------


def _esvaziar_informacoes_gerais(edital):
    identidade = secoes.identidade(edital.id, "informacoes-gerais")
    return [
        {"operation": "REPLACE", "targetPath": f"/sections/id={identidade}/content", "newValue": ""}
    ]


def test_a_retificacao_que_desloca_a_numeracao_avisa_e_publica(
    api_client, edital, client, settings
):
    from tests.interface.conftest import identificar

    publicado = levar_a_publicacao(api_client, edital, draft=_rascunho(**COERENTE))
    retificacao = create_retification(
        api_client, publicado, _esvaziar_informacoes_gerais(publicado)
    )

    codigos = {achado.code for achado in advertencias_do_ato(retificacao)}
    assert CONFLITO_DE_NUMERACAO_NA_RETIFICACAO in codigos, "o aviso não é subtraído (D-006)"
    assert CONFLITO_DE_NUMERACAO not in codigos

    settings.INTERFACE_SELETOR_IDENTIDADE = True
    identificar(client, "ana.elaboradora", ["elaborador"])
    tela = client.get(reverse("interface:retificacao-ato", args=[retificacao.id, "submeter"]))
    assert "Conflito de numeração" in tela.content.decode()
    assert "não impede o ato" in tela.content.decode()

    publish_retification(api_client, retificacao)
    assert retificacao.status == retificacao.Status.PUBLICADA


def test_a_retificacao_de_edital_que_ja_tinha_conflito_publica_com_aviso(
    api_client, edital, monkeypatch
):
    texto = "9.1 A inscrição será feita pela internet."
    with monkeypatch.context() as remendo:
        remendo.setattr(validation, "_numeracao_e_remissoes", lambda snapshot, *, ato: [])
        publicado = levar_a_publicacao(
            api_client, edital, draft=_rascunho(**{**COERENTE, "inscricao": texto})
        )
    mudanca = [{"operation": "REPLACE", "targetPath": "/description", "newValue": "Corrigida."}]
    retificacao = create_retification(api_client, publicado, mudanca)
    assert CONFLITO_DE_NUMERACAO_NA_RETIFICACAO in {
        achado.code for achado in advertencias_do_ato(retificacao)
    }
    publish_retification(api_client, retificacao)
    assert retificacao.status == retificacao.Status.PUBLICADA
