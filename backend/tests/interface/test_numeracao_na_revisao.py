"""O conflito de numeração pelo caminho de quem elabora (065, User Stories 1 a 3).

O texto entra pelo formulário da etapa Conteúdo, como entraria colado do Word, e o achado é lido
onde a pessoa o lê: no topo da etapa, na Revisão e na página do Edital (FR-1212). O link leva à
legenda da seção, que mostra o mesmo número que o achado nomeia (UX-160).
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.editais.domain.validation import (
    CONFLITO_DE_NUMERACAO,
    REMISSAO_AMBIGUA,
    REMISSAO_SEM_DESTINO,
    REMISSAO_SUSPEITA,
)
from processo_seletivo.editais.models import SecaoEdital
from processo_seletivo.processos.models import Edital
from tests.interface.conftest import compor_rascunho, identificar
from tests.interface.test_compor import eventos, perfis
from tests.interface.test_fluxo import EVENTOS, MARCOS, PERFIS, praticar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

INSCRICAO = "9.1 A inscrição será feita pela internet.\n9.2 O candidato anexará os documentos."


def _etapa(edital, chave):
    return reverse("interface:compor-etapa", args=[edital.id, chave])


def _escrever(client, edital, **secoes_):
    resposta = client.post(
        _etapa(edital, "conteudo"),
        {f"secao-{chave.replace('_', '-')}": texto for chave, texto in secoes_.items()},
    )
    assert resposta.status_code == 302, resposta.content
    edital.refresh_from_db()


def _numero_da_legenda(html, chave):
    legenda = re.search(rf'<legend id="titulo-{chave}">(.*?)</legend>', html, re.S)[1]
    return re.search(r"(\d+)\.", re.sub(r"<[^>]+>", "", legenda))[1]


@pytest.fixture
def composto(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, perfis(), eventos())
    edital.refresh_from_db()
    return edital


def test_o_conflito_aparece_na_etapa_na_revisao_e_no_edital(client, composto):
    _escrever(client, composto, publico_alvo="Graduados.", inscricao=INSCRICAO)

    etapa = client.get(_etapa(composto, "conteudo"))
    numero = _numero_da_legenda(etapa.content.decode(), "inscricao")
    assert numero != "9", "o cenário precisa da seção saindo com outro número"
    no_topo = [p for p in etapa.context["pendencias_aqui"] if p["codigo"] == CONFLITO_DE_NUMERACAO]
    assert len(no_topo) == 1

    revisao = client.get(_etapa(composto, "revisao"))
    [pendencia] = [p for p in revisao.context["pendencias"] if p["codigo"] == CONFLITO_DE_NUMERACAO]
    assert pendencia["severidade"] == "erro"
    assert (pendencia["etapa"], pendencia["ancora"], pendencia["corrigivel"]) == (
        "conteudo",
        "#titulo-inscricao",
        True,
    )
    # UX-160: o número que o achado nomeia é o que a legenda mostra.
    assert f"como {numero}," in pendencia["mensagem"]
    # UX-159: nada de código, caminho ou nome de campo.
    for interno in ("typed_numbering", "/sections", "id=", "content"):
        assert interno not in pendencia["mensagem"]

    detalhe = client.get(reverse("interface:detalhe", args=[composto.id]))
    assert any(p["codigo"] == CONFLITO_DE_NUMERACAO for p in detalhe.context["pendencias"])


def test_o_texto_gravado_e_o_que_foi_escrito(client, composto):
    """FR-1203: o sistema não renumera nem reescreve."""
    _escrever(client, composto, inscricao=INSCRICAO)
    assert SecaoEdital.objects.get(edital=composto, key="inscricao").content == INSCRICAO


def test_o_link_do_achado_leva_a_legenda_da_secao(client, composto):
    _escrever(client, composto, inscricao=INSCRICAO)
    html = client.get(_etapa(composto, "revisao")).content.decode()
    assert f"{_etapa(composto, 'conteudo')}#titulo-inscricao" in html


def test_a_remissao_ambigua_vem_depois_do_conflito_da_mesma_secao(client, composto):
    """UX-161, D-007: os achados de uma seção ficam juntos, e a numeração vem primeiro."""
    texto = INSCRICAO + "\n9.3 Vale o disposto no item 9.1."
    _escrever(client, composto, inscricao=texto)
    codigos = [
        p["codigo"]
        for p in client.get(_etapa(composto, "revisao")).context["pendencias"]
        if p["codigo"]
        in {CONFLITO_DE_NUMERACAO, REMISSAO_AMBIGUA, REMISSAO_SEM_DESTINO, REMISSAO_SUSPEITA}
    ]
    assert codigos[0] == CONFLITO_DE_NUMERACAO
    assert len(codigos) >= 2


def test_remissoes_repetidas_se_dobram_e_o_conflito_nunca(client, composto):
    """D-016: três avisos de remissão viram uma linha que se abre; o impeditivo fica à vista."""
    texto = INSCRICAO + "\nVer o item 7.7.\nVer o item 7.8.\nVer o item 7.9."
    _escrever(client, composto, inscricao=texto)
    html = client.get(_etapa(composto, "revisao")).content.decode()
    assert "3 avisos de remissão" in html
    assert html.count("Conflito de numeração") == 1


def test_a_submissao_e_recusada_e_corrigir_libera(client, seletor_ligado, edital):
    """User Story 3 pela interface: a recusa traz a mesma mensagem, e o número certo submete."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, PERFIS, EVENTOS, marcos=MARCOS)
    edital.refresh_from_db()
    _escrever(client, edital, inscricao=INSCRICAO)

    praticar(client, edital, "submeter")
    assert Edital.objects.get(pk=edital.pk).status == Edital.Status.EM_ELABORACAO

    numero = _numero_da_legenda(
        client.get(_etapa(edital, "conteudo")).content.decode(), "inscricao"
    )
    _escrever(
        client,
        edital,
        inscricao=f"{numero}.1 A inscrição será feita pela internet.\n"
        f"{numero}.2 O candidato anexará os documentos.",
    )
    revisao = client.get(_etapa(edital, "revisao"))
    assert not [p for p in revisao.context["pendencias"] if p["codigo"] == CONFLITO_DE_NUMERACAO]
    praticar(client, edital, "submeter")
    assert Edital.objects.get(pk=edital.pk).status == Edital.Status.EM_REVISAO
