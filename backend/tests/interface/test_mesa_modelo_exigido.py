"""O modelo que estava valendo, na mesa de quem avalia (020, FR-048, FR-050).

A banca confere o que voltou contra a forma que **foi pedida**, e a forma pedida é a da versão que
aquela Inscrição aceitou. Mostrar a vigente faria uma Retificação posterior reescrever, na tela, o
que se exigiu de quem já enviou.

O que a tela **não** afirma é qual arquivo o candidato baixou. Ele pode ter baixado sob outra
versão, e os bytes devolvidos não dizem de onde vieram: conformidade é juízo de quem avalia
(D-004, FR-049).
"""

import pytest
from django.urls import reverse

from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.editais.domain.documentos import modelo_do_requisito
from processo_seletivo.editais.models import AnexoEdital, DocumentoExigido
from tests.fixtures.comissao import (
    DOCUMENTO_A,
    ETAPA_A1,
    alocar_em,
    constituir,
    publicar_processo_com_etapas,
)
from tests.fixtures.edital import identificador
from tests.fixtures.mesa import distribuir_para, inscricoes_de
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

SEED = 91


def test_o_modelo_e_resolvido_dentro_da_versao_que_o_conteudo_declara():
    """A resolução é por conteúdo — é o que faz mesa e portal responderem versões diferentes."""
    aceita = {
        "attachments": [
            {"id": "a" * 8, "label": "ANEXO I — ANTIGO", "order": 1, "artifactId": "1" * 8}
        ]
    }
    vigente = {
        "attachments": [
            {"id": "a" * 8, "label": "ANEXO I — NOVO", "order": 1, "artifactId": "2" * 8}
        ]
    }
    requisito = {"id": "r", "attachmentId": "a" * 8}

    assert modelo_do_requisito(aceita, requisito)["artefato_id"] == "1" * 8
    assert modelo_do_requisito(vigente, requisito)["artefato_id"] == "2" * 8


def test_o_requisito_sem_modelo_nao_resolve_nada():
    conteudo = {"attachments": [{"id": "a" * 8, "label": "X", "order": 1, "artifactId": "1" * 8}]}

    assert modelo_do_requisito(conteudo, {"id": "r", "attachmentId": None}) is None
    assert modelo_do_requisito(conteudo, {"id": "r"}) is None


def test_o_vinculo_pendurado_nao_quebra_a_tela():
    """A validação recusa a referência pendurada; versão publicada antes dela não pode derrubar."""
    conteudo = {"attachments": []}

    assert modelo_do_requisito(conteudo, {"id": "r", "attachmentId": "a" * 8}) is None


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    def vincular(edital):
        anexo = AnexoEdital.objects.filter(edital=edital).order_by("order").first()
        DocumentoExigido.objects.filter(edital=edital, id=identificador(DOCUMENTO_A, SEED)).update(
            anexo=anexo
        )

    edital = publicar_processo_com_etapas(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": f"modelo-mesa-{SEED:04d}"},
        {
            "institutionalCode": f"PS-2026-{SEED}",
            "title": "Processo com modelo",
            "firstEdital": {"number": "91", "year": 2026, "title": "Edital 91/2026"},
        },
        seed=SEED,
        com_documentos=True,
        avaliacoes=2,
        maxima="100.0000",
        anexos=1,
        antes_de_submeter=vincular,
    )
    etapa = identificador(ETAPA_A1, SEED)
    membros = constituir(
        gestor,
        edital.processo,
        [("maria", Funcao.PRESIDENTE), ("joao", Funcao.MEMBRO)],
        prefixo=f"modelo-{SEED}",
    )
    alocar_em(gestor, edital.processo, membros["joao"], edital, etapa, chave=f"aloc-{SEED}")
    return {
        "edital": edital,
        "etapa": etapa,
        "processo": edital.processo,
        "membros": membros,
    }


def test_a_mesa_oferece_o_modelo_da_versao_aceita(client, seletor_ligado, cenario, gestor):
    inscricoes = inscricoes_de(cenario, 1, primeiro=9100)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="modelo")
    identificar(client, "joao", [])
    anexo = AnexoEdital.objects.get(edital=cenario["edital"])

    corpo = client.get(
        reverse(
            "interface:mesa-inscricao",
            args=[cenario["edital"].id, cenario["etapa"], inscricoes[0].id],
        )
    ).content.decode()

    assert "Modelo exigido" in corpo
    assert reverse("public-anexo", args=[anexo.artefato_id]) in corpo


def test_a_mesa_nao_afirma_qual_versao_o_candidato_usou(client, seletor_ligado, cenario, gestor):
    """FR-049 — a tela mostra a forma pedida, e não a origem do arquivo que voltou."""
    inscricoes = inscricoes_de(cenario, 1, primeiro=9110)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="origem")
    identificar(client, "joao", [])

    corpo = client.get(
        reverse(
            "interface:mesa-inscricao",
            args=[cenario["edital"].id, cenario["etapa"], inscricoes[0].id],
        )
    ).content.decode()

    for frase in ("baixou", "corresponde ao modelo", "confere com o modelo", "versão utilizada"):
        assert frase not in corpo.lower()
