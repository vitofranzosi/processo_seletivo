"""A Retificação de um Edital publicado com o catálogo anterior (069, R-016, quickstart §5).

O consolidado de um Edital publicado antes da `069` sai na **apresentação plana**: a ordem, os
títulos em caixa alta, a numeração e a divisão do original, sem resumo e sem seções reunidas — e
com a redação 2, a fonte embutida e o sumário, que não mudam número nem destino de remissão
(FR-1394, FR-1399, D-003, D-007). A tela de Retificação mostra os números do PDF original.

O Edital "publicado antes" é publicado aqui com o catálogo da `054` no lugar do vigente, que é o
que o snapshot dele carrega: a apresentação se reconhece pela assinatura do catálogo copiado na
submissão (R-001).
"""

import json
import re

import pytest
from django.urls import reverse

from processo_seletivo.editais.domain import secoes, validation
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.infrastructure import pdf
from processo_seletivo.publicacoes.models import Publicacao
from tests.fixtures.edital import complete_draft
from tests.fixtures.publicacao import levar_a_publicacao, retify
from tests.interface.conftest import identificar
from tests.unit.publicacoes.test_pdf import texto_de

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

TEXTOS = {
    "disposicoes-preliminares": "O processo seletivo será conduzido pela Comissão.",
    "publico-alvo": "Graduados em qualquer área.",
    "inscricao": "A inscrição será feita pela internet.",
    "recursos": "Os recursos seguem o disposto no item 1.",
    "disposicoes-finais": "Os casos omissos serão resolvidos pela Comissão.",
}
TITULO_NUMERADO = re.compile(r"^(\d+)\. ([A-ZÀ-Ý][^a-zà-ÿ]*)$")


def _conteudo(publicacao):
    """O conteúdo publicado no ato: o canônico que ele gravou."""
    return json.loads(bytes(publicacao.canonical_content))


def _titulos(documento):
    """Os títulos de seção do corpo, em ordem — sem as linhas do sumário."""
    return [
        (int(casado[1]), casado[2])
        for linha in texto_de(documento).splitlines()
        if " . ." not in linha and (casado := TITULO_NUMERADO.match(linha.strip()))
    ]


@pytest.fixture
def antigo(api_client, manager_headers, process_payload, monkeypatch):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    edital = Edital.objects.get()
    rascunho = complete_draft()
    rascunho["sections"] = [{"key": chave, "content": texto} for chave, texto in TEXTOS.items()]
    with monkeypatch.context() as antes:
        antes.setattr(secoes, "CATALOGO", secoes.CATALOGO_DA_054)
        antes.setattr(validation, "CATALOGO", secoes.CATALOGO_DA_054)
        levar_a_publicacao(api_client, edital, draft=rascunho)
    edital.refresh_from_db()
    return edital


@pytest.fixture
def documentos(api_client, antigo):
    original = Publicacao.objects.get(edital=antigo)
    retify(
        api_client,
        antigo,
        [
            {
                "targetPath": (
                    f"/sections/id={secoes.identidade(antigo.id, 'disposicoes-finais')}/content"
                ),
                "operation": "REPLACE",
                "newValue": "Os casos omissos serão resolvidos pela Comissão de Seleção.",
            }
        ],
        suffix="antigo-069",
    )
    consolidado = Publicacao.objects.filter(edital=antigo).latest("publication_order")
    assert consolidado.id != original.id
    return original, consolidado


def test_o_original_carrega_o_catalogo_anterior(documentos):
    original, consolidado = documentos
    assert not pdf.por_perguntas(_conteudo(original))
    assert not pdf.por_perguntas(_conteudo(consolidado))


def test_o_consolidado_tem_a_ordem_os_titulos_e_a_numeracao_do_original(documentos):
    original, consolidado = documentos
    antes = _titulos(bytes(original.documento.bytes))
    depois = _titulos(bytes(consolidado.documento.bytes))
    assert antes, "o original tem títulos numerados em caixa alta"
    assert depois == antes
    assert (1, "DISPOSIÇÕES PRELIMINARES") in depois
    assert any(titulo == "PERFIS DE VAGA" for _, titulo in depois)
    assert any(titulo == "DOS RECURSOS" for _, titulo in depois)


def test_o_consolidado_tem_os_mesmos_itens_que_o_original(documentos):
    """FR-1399, D-007: cada remissão aponta para o mesmo número e o mesmo destino."""
    original, consolidado = documentos
    assert pdf.itens_do_documento(_conteudo(consolidado)) == pdf.itens_do_documento(
        _conteudo(original)
    )


def test_o_consolidado_sai_com_a_redacao_a_fonte_e_o_sumario_sem_resumo(documentos):
    _, consolidado = documentos
    documento = bytes(consolidado.documento.bytes)
    texto = texto_de(documento)
    corrido = " ".join(texto.split())
    assert b"/Subtype /TrueType" in documento
    assert "Sumário" in texto
    assert "Autenticidade — este documento corresponde integralmente" in corrido
    assert "Resumo deste Edital" not in texto
    assert "Quem pode se inscrever?" not in texto
    assert "Marcos classificatórios" not in corrido
    assert "Os casos omissos serão resolvidos pela Comissão de Seleção." in corrido


def test_a_tela_de_retificacao_mostra_os_numeros_do_original(
    client, seletor_ligado, antigo, documentos
):
    original, _ = documentos
    identificar(client, "ana.elaboradora", ["elaborador"])
    numeros = pdf.numeracao(_conteudo(original))
    corpo = client.get(reverse("interface:retificar", args=[antigo.id])).content.decode()
    for chave, titulo in (
        ("disposicoes-preliminares", "Disposições Preliminares"),
        ("inscricao", "Da Inscrição"),
        ("recursos", "Dos Recursos"),
    ):
        assert isinstance(numeros[chave], int)
        assert f"{numeros[chave]} — {titulo}" in corpo, chave
