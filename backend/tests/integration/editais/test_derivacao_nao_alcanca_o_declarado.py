"""Padrão e derivação são começo de conversa, e nunca correção de quem já falou (030, FR-421).

Este arquivo é o contraponto de `test_derivacao_persistida.py`, que afirma o caso oposto: lá, a
linha geral do quadro **precisa** nascer derivada, porque ela é projeção de um número que o Perfil
já publica. Aqui, o arredondamento e a identidade do marco **não podem** nascer sobre o que alguém
declarou — eles são valor inicial de um campo que ninguém respondeu ainda.

A distinção é a que a FR-421 fixa, e ela tem uma consequência prática que só se vê no acervo: um
Edital publicado antes desta feature entra em Retificação com o arredondamento que ele publicou, e
a tela não pode fazer `2` e `meio para cima` chegarem por conta própria. Se chegassem, a Retificação
proporia corrigir um campo que ninguém pediu para corrigir — e a autoridade assinaria a mudança.
"""

import pytest

from processo_seletivo.editais.domain import marcos
from processo_seletivo.editais.models.perfis import MarcoClassificatorio
from processo_seletivo.interface import retificacao as retificacao_ui
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.publicacao import publish_original
from tests.fixtures.snapshot import PERFIL, rascunho_completo

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

#: Um arredondamento que **não** é o padrão de FR-419, de propósito: com o par padrão, um teste que
#: falhasse continuaria verde.
DECLARADO = {"scale": 4, "mode": "TRUNCAR"}


@pytest.fixture
def publicado(api_client, manager_headers, process_payload):
    rascunho = rascunho_completo()
    perfil = next(item for item in rascunho["profiles"] if item["id"] == PERFIL["A"])
    perfil["classificationMilestones"][0]["rounding"] = DECLARADO
    return publish_original(api_client, manager_headers, process_payload, draft=rascunho, anexos=1)


def test_o_padrao_nao_reescreve_o_arredondamento_declarado(publicado):
    """O marco publicado com quatro casas e truncamento continua com as quatro e o truncamento."""
    assert MarcoClassificatorio.objects.get(perfil_id=PERFIL["A"]).arredondamento == DECLARADO
    assert DECLARADO != marcos.ARREDONDAMENTO_PADRAO


def test_a_retificacao_nao_ve_o_padrao_chegar_por_conta_propria(publicado):
    """FR-421 na tela onde a autoridade assina: o que se propõe corrigir é o que está publicado."""
    vigente = VersaoConsolidada.objects.filter(edital=publicado).latest("materialized_at")

    marco = vigente.content["profiles"][0]["classificationMilestones"][0]
    grupos = retificacao_ui.campos_editaveis(vigente.content)

    campos = {
        campo["chave"]: campo["valor"]
        for grupo in grupos
        if grupo["caminho"].endswith(f"classificationMilestones/id={marco['id']}")
        for campo in grupo["campos"]
    }

    assert campos["rounding/scale"] == str(DECLARADO["scale"])
    assert campos["rounding/mode"] == DECLARADO["mode"]


def test_a_derivacao_da_identidade_nao_alcanca_marco_que_ja_tem_codigo(publicado):
    """A derivação entrega um começo, e não corrige quem já escolheu o próprio nome."""
    marco = MarcoClassificatorio.objects.get(perfil_id=PERFIL["A"])
    perfil = marco.perfil

    codigo, nome = marcos.identidade_derivada(
        codigo_do_perfil=perfil.code,
        nome_do_perfil=perfil.name,
        codigos_em_uso=perfil.marcos.values_list("code", flat=True),
    )

    assert marco.code == "FINAL", "o publicado é o que a elaboração declarou"
    assert codigo != marco.code, "e a derivação do marco seguinte não colide com ele"
    assert nome.startswith("Classificação final")


def test_a_retificacao_nao_acrescenta_marco_e_por_isso_nao_deriva_nada(publicado):
    """A garantia é estrutural, e este teste a declara.

    Nada em `interface/retificacao` cria marco: a tela alcança os campos do que já existe, e o
    fragmento que acrescenta linha existe para Perfil, Evento, Anexo e linha do quadro — nunca para
    marco. É por isso que padrão e derivação não têm por onde entrar numa Retificação.

    Se um dia alguém acrescentar esse fragmento, é aqui que a suíte cai — e é essa a razão de o
    teste existir.
    """
    from processo_seletivo.interface import urls

    nomes = {padrao.name for padrao in urls.urlpatterns if getattr(padrao, "name", None)}
    acrescentam = {nome for nome in nomes if nome.startswith("fragmento-retificacao")}

    assert "fragmento-retificacao-marco" not in acrescentam
    assert acrescentam == {
        "fragmento-retificacao-perfil",
        "fragmento-retificacao-evento",
        "fragmento-retificacao-anexo",
        "fragmento-retificacao-linha-do-quadro",
    }
