"""O Edital publicado sob o catálogo anterior continua retificável (054, FR-987, FR-988; SC-366).

É a armadilha que a DP-20 nomeou: a Retificação conferia a topologia contra o catálogo **vigente**,
e mudar o catálogo trancava a Retificação de todo Edital já publicado. Aqui o Edital é publicado com
o catálogo de 12 seções de antes da `054`, o catálogo volta a ser o de 22, e o Edital é retificado.
"""

import pytest

from processo_seletivo.editais.domain import secoes, validation
from processo_seletivo.editais.domain.secoes import GERADA, TEXTUAL, Secao
from processo_seletivo.editais.domain.validation import blocking_findings, validate_for_publication
from processo_seletivo.publicacoes.domain.conflicts import previous_hash
from processo_seletivo.publicacoes.models import Publicacao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.publicacao import (
    create_retification,
    publish_original,
    retify,
    try_publish_retification,
)
from tests.unit.publicacoes.test_pdf import texto_de

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

# O catálogo como era até a `053`: 12 entradas, a inscrição antes dos Perfis.
CATALOGO_ANTERIOR = (
    Secao("apresentacao", "Apresentação", 1, TEXTUAL),
    Secao("disposicoes-preliminares", "Disposições Preliminares", 2, TEXTUAL),
    Secao("requisitos-gerais", "Requisitos Gerais de Participação", 3, TEXTUAL),
    Secao("inscricao", "Da Inscrição", 4, TEXTUAL),
    Secao(
        "documentos-exigidos",
        "Documentos Exigidos para a Inscrição",
        5,
        GERADA,
        "documentRequirements",
    ),
    Secao("perfis", "Perfis de Vaga", 6, GERADA, "profiles"),
    Secao("etapas", "Etapas de Avaliação", 7, GERADA, "stages"),
    Secao("classificacao", "Critérios de Classificação", 8, TEXTUAL),
    Secao("cronograma", "Cronograma", 9, GERADA, "schedule"),
    Secao("recursos", "Dos Recursos", 10, TEXTUAL),
    Secao("anexos", "Anexos", 11, GERADA, "attachments"),
    Secao("disposicoes-finais", "Disposições Finais", 12, TEXTUAL),
)


@pytest.fixture
def edital_do_acervo(api_client, manager_headers, process_payload, monkeypatch):
    """Publicado com o catálogo anterior; devolvido com o catálogo da `054` de volta no lugar."""
    with monkeypatch.context() as antes:
        antes.setattr(secoes, "CATALOGO", CATALOGO_ANTERIOR)
        antes.setattr(validation, "CATALOGO", CATALOGO_ANTERIOR)
        edital = publish_original(api_client, manager_headers, process_payload)
    return edital


def _vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def _mudanca(edital, caminho, operacao, valor):
    mudanca = {"targetPath": caminho, "operation": operacao, "newValue": valor}
    if operacao == "REPLACE":
        mudanca["expectedPreviousHash"] = previous_hash(_vigente(edital).content, caminho)
    return [mudanca]


def _secao(edital, chave):
    return f"/sections/id={secoes.identidade(edital.id, chave)}"


def test_o_acervo_diverge_do_catalogo_vigente(edital_do_acervo):
    """A premissa: conferido contra o catálogo de hoje, o conteúdo publicado seria recusado."""
    conteudo = _vigente(edital_do_acervo).content
    assert len(conteudo["sections"]) == 12
    assert blocking_findings(validate_for_publication(conteudo))


def test_retificar_o_texto_de_uma_secao_do_acervo_e_aceito(api_client, edital_do_acervo):
    retify(
        api_client,
        edital_do_acervo,
        _mudanca(
            edital_do_acervo,
            f"{_secao(edital_do_acervo, 'recursos')}/content",
            "REPLACE",
            "Recurso em dois dias úteis.",
        ),
    )

    consolidado = _vigente(edital_do_acervo).content
    assert [item["key"] for item in consolidado["sections"]] == [
        secao.key for secao in CATALOGO_ANTERIOR
    ]
    ultima = Publicacao.objects.filter(edital=edital_do_acervo).latest("publication_order")
    texto = texto_de(bytes(ultima.documento.bytes))
    assert "Recurso em dois dias úteis." in texto
    # A forma do documento é a da publicação original: nenhuma seção do catálogo novo.
    assert "Versão consolidada" in texto


@pytest.mark.parametrize(
    ("operacao", "alvo", "valor", "motivo"),
    [
        ("REPLACE", "title", "Outro título", "diverge"),
        ("REPLACE", "order", 3, "diverge"),
    ],
)
def test_mexer_na_topologia_do_acervo_continua_recusado(
    api_client, edital_do_acervo, operacao, alvo, valor, motivo
):
    retificacao = create_retification(
        api_client,
        edital_do_acervo,
        _mudanca(
            edital_do_acervo, f"{_secao(edital_do_acervo, 'recursos')}/{alvo}", operacao, valor
        ),
        esperar=422,
    )
    assert motivo in retificacao["detail"]


def test_acrescentar_ao_acervo_uma_secao_do_catalogo_novo_e_recusado(api_client, edital_do_acervo):
    """A referência é o Edital, e não "qualquer catálogo que já existiu" (research, R-004)."""
    nova = {
        "id": str(secoes.identidade(edital_do_acervo.id, "certificado")),
        "key": "certificado",
        "title": "Do Certificado",
        "order": 19,
        "type": "TEXT",
        "content": "Certificado digital.",
    }
    resposta = create_retification(
        api_client,
        edital_do_acervo,
        [{"targetPath": "/sections/-", "operation": "ADD", "newValue": nova}],
        esperar=422,
    )
    assert "não pertence ao catálogo" in resposta["detail"]


def test_o_edital_novo_continua_conferido_contra_o_catalogo_vigente(
    api_client, manager_headers, process_payload
):
    """FR-987: sem Edital publicado, não há topologia de referência."""
    edital = publish_original(api_client, manager_headers, process_payload)
    assert len(_vigente(edital).content["sections"]) == len(secoes.CATALOGO)
    resposta = try_publish_retification(
        api_client,
        create_retification(
            api_client,
            edital,
            _mudanca(edital, f"{_secao(edital, 'certificado')}/content", "REPLACE", "Digital."),
        ),
    )
    assert resposta.status_code == 201, resposta.content
