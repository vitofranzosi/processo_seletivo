"""O método comum do Edital, e o que ele promete não tocar (030, US3, FR-429, FR-431, SC-142).

Irmão de `test_mutabilidade_do_metodo_de_sorteio.py`, que guarda a fronteira do congelamento. Aqui
a fronteira é outra, e é a do acervo: um Edital composto antes desta feature publica, depois dela,
**exatamente** o mesmo conteúdo normativo — cada marco com o seu método literal, e nenhuma chave
nova no nível do Edital.

**Por que a promessa precisa de teste próprio.** A resolução é silenciosa por construção: ela
devolve o método do marco quando ele existe, e ninguém percebe se um dia passar a devolver outra
coisa. O que quebraria o acervo não é a resolução errar — é ela passar a **escrever**.
"""

import copy

import pytest

from processo_seletivo.editais.domain import marcos
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.publish_edital import edital_snapshot
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.publicacao import publish_original
from tests.fixtures.snapshot import MARCO, PERFIL, rascunho_completo

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def rascunho(*, com_metodo_comum, com_metodo_no_marco):
    base = copy.deepcopy(rascunho_completo())
    if not com_metodo_comum:
        base.pop("drawMethod", None)
    perfil = next(item for item in base["profiles"] if item["id"] == PERFIL["A"])
    if not com_metodo_no_marco:
        perfil["classificationMilestones"][0]["drawMethod"] = None
    return base


@pytest.fixture
def anterior_a_feature(api_client, manager_headers, process_payload):
    """O Edital do acervo: método literal em cada marco, e nada no nível do Edital."""
    return publish_original(
        api_client,
        manager_headers,
        process_payload,
        draft=rascunho(com_metodo_comum=False, com_metodo_no_marco=True),
        anexos=1,
    )


def test_o_edital_do_acervo_nao_ganha_chave_no_nivel_do_edital(anterior_a_feature):
    """SC-142 — a ausência **é** o que ele afirma, e os leitores derivam dela o de sempre."""
    conteudo = VersaoConsolidada.objects.get(edital=anterior_a_feature).content

    assert "drawMethod" not in conteudo
    assert conteudo["profiles"][0]["classificationMilestones"][0]["drawMethod"], (
        "cada marco continua carregando o método literal que publicou"
    )


def test_a_resolucao_devolve_o_metodo_literal_do_marco_do_acervo(anterior_a_feature):
    """A resolução só alcança marco **sem** método próprio — estado que nenhum acervo tem."""
    conteudo = VersaoConsolidada.objects.get(edital=anterior_a_feature).content

    resolvido = marcos.metodo_que_governa(conteudo, perfil_id=PERFIL["A"], marco_id=MARCO)

    assert resolvido == conteudo["profiles"][0]["classificationMilestones"][0]["drawMethod"]


def test_o_marco_sem_metodo_proprio_referencia_o_comum(
    api_client, manager_headers, process_payload
):
    """FR-429 — a outra ponta: declarado uma vez, referenciado por quem não diverge."""
    edital = publish_original(
        api_client,
        manager_headers,
        process_payload,
        draft=rascunho(com_metodo_comum=True, com_metodo_no_marco=False),
        anexos=1,
    )
    conteudo = VersaoConsolidada.objects.get(edital=edital).content

    assert conteudo["profiles"][0]["classificationMilestones"][0]["drawMethod"] is None
    assert (
        marcos.metodo_que_governa(conteudo, perfil_id=PERFIL["A"], marco_id=MARCO)
        == (conteudo["drawMethod"])
    )
    assert marcos.marco_ordena_por_sorteio(conteudo, perfil_id=PERFIL["A"], marco_id=MARCO)


def test_o_edital_sem_sorteio_nao_publica_a_chave(api_client, manager_headers, process_payload):
    """`{}` significa não declarado, e não declarado não vira chave nula no documento."""
    edital = publish_original(
        api_client,
        manager_headers,
        process_payload,
        draft=rascunho(com_metodo_comum=False, com_metodo_no_marco=False),
        anexos=1,
    )

    assert "drawMethod" not in VersaoConsolidada.objects.get(edital=edital).content


def test_o_metodo_comum_nao_reescreve_o_marco_no_banco(
    api_client, manager_headers, process_payload
):
    """A resolução **lê**, e não escreve: o marco que referencia continua vazio no modelo.

    Se um dia ela materializasse o comum dentro do marco, a divergência da FR-430 deixaria de ser
    legível — todo marco passaria a ter método próprio, e "diverge" não se distinguiria de
    "referencia".
    """
    from processo_seletivo.editais.models.perfis import MarcoClassificatorio

    edital = publish_original(
        api_client,
        manager_headers,
        process_payload,
        draft=rascunho(com_metodo_comum=True, com_metodo_no_marco=False),
        anexos=1,
    )

    assert MarcoClassificatorio.objects.get(pk=MARCO).metodo_de_sorteio == {}
    assert Edital.objects.get(pk=edital.pk).metodo_de_sorteio_comum
    assert edital_snapshot(Edital.objects.get(pk=edital.pk))["drawMethod"]
