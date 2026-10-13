"""O aviso de remissão pelo título, pelo caminho de quem elabora (069, FR-1400, R-013).

O texto entra pela etapa Conteúdo, como entraria colado do Word, citando a seção pelo título do
original. O aviso aparece onde a pessoa o lê — no topo da etapa e na Revisão —, com o link para a
legenda da seção em que a remissão está, e não impede nada.
"""

import pytest
from django.urls import reverse

from processo_seletivo.editais.domain.validation import REMISSAO_PELO_TITULO
from tests.interface.conftest import compor_rascunho, identificar
from tests.interface.test_compor import eventos, perfis

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

TEXTO = "Havendo mais inscritos, vale o método publicado na seção Perfis de Vaga."


def _etapa(edital, chave):
    return reverse("interface:compor-etapa", args=[edital.id, chave])


@pytest.fixture
def composto(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, perfis(), eventos())
    edital.refresh_from_db()
    resposta = client.post(
        _etapa(edital, "conteudo"),
        {"secao-classificacao": TEXTO, "secao-publico-alvo": "Graduados."},
    )
    assert resposta.status_code == 302, resposta.content
    edital.refresh_from_db()
    return edital


def test_o_aviso_aparece_na_revisao_com_a_ancora_da_secao(client, composto):
    revisao = client.get(_etapa(composto, "revisao"))
    [pendencia] = [p for p in revisao.context["pendencias"] if p["codigo"] == REMISSAO_PELO_TITULO]
    assert pendencia["severidade"] != "erro", "aviso, e não impeditivo"
    assert (pendencia["etapa"], pendencia["ancora"], pendencia["corrigivel"]) == (
        "conteudo",
        "#titulo-classificacao",
        True,
    )
    assert "«seção Perfis de Vaga»" in pendencia["mensagem"]
    assert "repartida" in pendencia["mensagem"]
    for interno in ("cross_reference", "/sections", "id=", "content"):
        assert interno not in pendencia["mensagem"]


def test_o_aviso_aparece_no_topo_da_etapa_conteudo(client, composto):
    etapa = client.get(_etapa(composto, "conteudo"))
    assert [p for p in etapa.context["pendencias_aqui"] if p["codigo"] == REMISSAO_PELO_TITULO]
    # A âncora leva à legenda da seção, que existe na etapa.
    assert 'id="titulo-classificacao"' in etapa.content.decode()


def test_o_texto_continua_o_que_foi_escrito(client, composto):
    etapa = client.get(_etapa(composto, "conteudo"))
    [classificacao] = [s for s in etapa.context["secoes"] if s["key"] == "classificacao"]
    assert classificacao["content"] == TEXTO
