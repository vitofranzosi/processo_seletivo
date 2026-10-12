"""A etapa Conteúdo mostra o número que o documento imprime (054, UX-130 a UX-133; SC-363).

A regra da numeração é uma só (`pdf.numeracao`), e a tela a lê; a atualização enquanto se digita é
do `conteudo.js`, com a regra pura em `tests/javascript/conteudo.test.js` e o comportamento no
navegador pelo roteiro do quickstart, §4.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.interface.forms import rotulo_do_numero
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot
from processo_seletivo.publicacoes.infrastructure.pdf import numeracao
from tests.interface.conftest import compor_rascunho, identificar
from tests.interface.test_compor import eventos, perfis

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

DECLARACAO = "Declaro que as informações prestadas são verdadeiras."


def _etapa(edital):
    return reverse("interface:compor-etapa", args=[edital.id, "conteudo"])


@pytest.fixture
def composto(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, perfis(), eventos())
    edital.refresh_from_db()
    resposta = client.post(
        _etapa(edital),
        {
            "secao-apresentacao": "A Diretora do Cefor faz saber.",
            "secao-publico-alvo": "Graduados.",
            "secao-disposicoes-finais": "Casos omissos pela Comissão.",
        },
    )
    assert resposta.status_code == 302, resposta.content
    edital.refresh_from_db()
    return edital


def _legendas(html):
    return {
        chave: re.sub(r"<[^>]+>", "", legenda)
        for chave, legenda in re.findall(r'<legend id="titulo-([\w-]+)">(.*?)</legend>', html, re.S)
    }


def test_cada_secao_mostra_o_numero_do_documento_ou_que_nao_sai(client, composto):
    """UX-130 e SC-363: o número da tela é o de `numeracao`, a regra do compositor."""
    resposta = client.get(_etapa(composto))
    numeros = numeracao(edital_snapshot(Edital.objects.get(pk=composto.pk)))
    legendas = _legendas(resposta.content.decode())

    for secao in resposta.context["secoes"]:
        assert secao["numero"] == numeros[secao["key"]], secao["key"]
        legenda = legendas[secao["key"]]
        if secao["numero"] is None:
            assert legenda == f"{secao['title']} (vazia — não sai no documento)"
        elif secao["numero"] == 0:
            assert legenda == f"{secao['title']} (preâmbulo, sem número)"
        else:
            # "3. " para a seção e "3.1 " para a subseção, como o documento imprime (069, R-003);
            # a das Etapas diz os números delas, que saem como subseções da seleção.
            if secao["key"] != "etapas":
                assert secao["rotulo_do_numero"] == rotulo_do_numero(secao["numero"])
            assert legenda == f"{secao['rotulo_do_numero']}{secao['title']}"

    assert legendas["apresentacao"].endswith("(preâmbulo, sem número)")
    # Público-alvo sai reunido em "Quem pode se inscrever?", e a pergunta vem antes dele.
    assert legendas["publico-alvo"].startswith("1.1 ")
    assert "<h3>1. Quem pode se inscrever?</h3>" in resposta.content.decode()
    assert legendas["certificado"].endswith("(vazia — não sai no documento)")


def test_a_tela_nao_fala_em_redacao_padrao(client, composto):
    """UX-131."""
    html = client.get(_etapa(composto)).content.decode()
    assert "Redação institucional padrão" not in html
    assert "só sai no documento a seção que tiver texto" in html


def test_a_matricula_diz_o_que_o_documento_acrescentara(client, composto):
    """UX-132: com Requerimento, a Matrícula sai mesmo vazia, e a tela diz com o quê."""
    Edital.objects.filter(pk=composto.pk).update(
        requerimento_momento="AT_CALL", requerimento_declaracao=DECLARACAO
    )
    resposta = client.get(_etapa(composto))
    html = resposta.content.decode()

    matricula = next(s for s in resposta.context["secoes"] if s["key"] == "matricula")
    assert matricula["numero"] is not None
    assert DECLARACAO in html
    assert 'aria-describedby="ajuda-matricula"' in html
    assert re.search(r'data-secao="matricula"\s+data-estado="sai"', html)


def test_o_numero_e_o_estado_sao_lidos_com_o_titulo(client, composto):
    """UX-133: estão na legenda, que nomeia o campo."""
    html = client.get(_etapa(composto)).content.decode()
    assert 'aria-labelledby="titulo-certificado"' in html
    assert re.search(r'<legend id="titulo-certificado">.*vazia — não sai', html)


def test_a_reexibicao_nao_devolve_o_texto_da_secao_que_se_esvaziou(client, composto):
    """Code review do PR 233: ausente no envio é vazia, e não o texto gravado."""
    from processo_seletivo.interface.views import _reexibir_secoes

    edital = Edital.objects.get(pk=composto.pk)
    snapshot = edital_snapshot(edital)
    reexibidas = {
        secao["key"]: secao["content"]
        for secao in _reexibir_secoes(
            edital, [{"key": "apresentacao", "content": "Outro preâmbulo."}], snapshot
        )
    }
    assert reexibidas["apresentacao"] == "Outro preâmbulo."
    # Gravada com texto na fixture, e esvaziada neste envio.
    assert reexibidas["publico-alvo"] == ""
    assert reexibidas["disposicoes-finais"] == ""


def _estado_do_conteudo(client, edital):
    resposta = client.get(reverse("interface:compor-etapa", args=[edital.id, "perfis"]))
    return next(p for p in resposta.context["progresso"] if p["chave"] == "conteudo")["estado"]


def test_gravar_a_etapa_com_tudo_vazio_a_conclui(client, seletor_ligado, edital):
    """Code review do PR 233: o Edital só de dados estruturados é legítimo (FR-982), e gravar a
    etapa vazia é o sinal que a FR-040 da 007 pede — a gravação auditada, e não a linha."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, perfis(), eventos())
    edital.refresh_from_db()
    assert _estado_do_conteudo(client, edital) == "pronta"

    assert client.post(_etapa(edital), {}).status_code == 302
    edital.refresh_from_db()
    assert not edital.secoes.exists()
    assert _estado_do_conteudo(client, edital) == "concluida"


def test_a_pergunta_que_sai_pelo_gerado_nao_se_diz_vazia(client, composto):
    """069: "Como se inscrever?" sai pelo teto de inscrições, ainda que o texto esteja vazio."""
    Edital.objects.filter(pk=composto.pk).update(max_inscricoes_por_candidato=1)
    resposta = client.get(_etapa(composto))
    inscricao = next(s for s in resposta.context["secoes"] if s["key"] == "inscricao")
    assert inscricao["numero"] is not None
    assert inscricao["sai_sem_texto"]
    assert re.search(r'data-secao="inscricao"\s+data-estado="sai"', resposta.content.decode())
    legendas = _legendas(resposta.content.decode())
    assert "vazia" not in legendas["inscricao"]


def test_a_pergunta_vem_antes_do_primeiro_membro_mesmo_vazio(client, composto):
    """069: com Público-alvo vazio, "Quem pode se inscrever?" sai pelos requisitos dos Perfis."""
    edital = Edital.objects.get(pk=composto.pk)
    edital.secoes.filter(key="publico-alvo").delete()
    html = client.get(_etapa(composto)).content.decode()
    assert re.search(
        r"<h3>\d+\. Quem pode se inscrever\?</h3>\s*<fieldset[^>]*data-secao=\"publico-alvo\"", html
    )
