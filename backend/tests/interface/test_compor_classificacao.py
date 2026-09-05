"""O passo que declara a classificação, e a regra que sai dele precisa rodar (015, T072-T075).

**Por que este passo é separado do de Perfis.** O marco enumera Etapas, e seus critérios apontam
Etapa ou fato declarado. No passo de Perfis, que vem antes das Etapas, isso seria oferecer uma lista
vazia e chamá-la de escolha — a mesma razão pela qual a Inscrição veio depois do Cronograma.

O teste que fecha a fatia não confere campos: confere que a regra que a tela produz é
**executável**.
Antes desta correção a tela publicava marco sem Etapa e critério sem alvo, e o cálculo não tinha o
que combinar.
"""

from decimal import Decimal

import pytest
from django.urls import reverse

from processo_seletivo.classificacao.domain.combinacao import SEM_PONTUACAO, combinar
from processo_seletivo.editais.models.perfis import MarcoClassificatorio
from processo_seletivo.processos.models import Edital
from tests.interface.conftest import compor_rascunho, identificar
from tests.interface.test_compor import EVENTO, PERFIL, eventos, perfis

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ETAPA_CLASSIFICATORIA = "aaaaaaaa-0000-4000-8000-00000000e021"
ETAPA_SO_ELIMINATORIA = "aaaaaaaa-0000-4000-8000-00000000e023"
MARCO = "aaaaaaaa-0000-4000-8000-00000000e051"
CRITERIO = "aaaaaaaa-0000-4000-8000-00000000e061"


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    return Edital.objects.get()


@pytest.fixture
def com_etapas(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, perfis=perfis(), eventos=eventos())
    edital.refresh_from_db()
    resposta = client.post(
        reverse("interface:compor-etapa", args=[edital.id, "etapas"]),
        {
            "etapa-0-id": ETAPA_CLASSIFICATORIA,
            "etapa-0-name": "Prova didática",
            "etapa-0-order": "1",
            "etapa-0-weight": "2",
            "etapa-0-classificatory": "on",
            "etapa-0-scheduleEventId": EVENTO,
            "etapa-1-id": ETAPA_SO_ELIMINATORIA,
            "etapa-1-name": "Análise documental",
            "etapa-1-order": "2",
            "etapa-1-weight": "1",
            "etapa-1-eliminatory": "on",
            "etapa-1-scheduleEventId": "",
        },
    )
    assert resposta.status_code == 302, resposta.content
    edital.refresh_from_db()
    return edital


def marco_form(**alteracoes):
    base = {
        "perfil_id": PERFIL,
        f"marco-{PERFIL}-0-id": MARCO,
        f"marco-{PERFIL}-0-code": "FINAL",
        f"marco-{PERFIL}-0-name": "Classificação final",
        f"marco-{PERFIL}-0-stages": ETAPA_CLASSIFICATORIA,
        f"marco-{PERFIL}-0-operation": "SOMA_PONDERADA",
        f"marco-{PERFIL}-0-normalization": "NENHUMA",
        f"marco-{PERFIL}-0-scale": "2",
        f"marco-{PERFIL}-0-mode": "MEIO_PARA_CIMA",
        f"criterio-{PERFIL}-0-0-id": CRITERIO,
        f"criterio-{PERFIL}-0-0-order": "1",
        f"criterio-{PERFIL}-0-0-type": "MAIOR_PONTUACAO_NA_ETAPA",
        f"criterio-{PERFIL}-0-0-target": ETAPA_CLASSIFICATORIA,
        f"criterio-{PERFIL}-0-0-whenMissing": "ULTIMO_NO_CRITERIO",
    }
    return {**base, **alteracoes}


def test_o_passo_vem_depois_das_etapas():
    from processo_seletivo.interface.views import CHAVES_ETAPA

    assert CHAVES_ETAPA.index("classificacao") > CHAVES_ETAPA.index("etapas")


def test_o_percurso_produz_regra_executavel(client, com_etapas):
    """Interface → rascunho → domínio: o que a tela grava, o cálculo consegue rodar.

    É a prova que faltava. Sem Etapa enumerada, `combinar` devolve `SEM_PONTUACAO` para todo mundo
    — e era exatamente isso que a tela publicava antes desta correção.
    """
    resposta = client.post(
        reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"]), marco_form()
    )

    assert resposta.status_code == 302, resposta.content
    marco = MarcoClassificatorio.objects.get(pk=MARCO)
    assert [str(item) for item in marco.etapas] == [ETAPA_CLASSIFICATORIA]
    assert marco.arredondamento == {"scale": 2, "mode": "MEIO_PARA_CIMA"}
    assert marco.criterios.get().parametros == {"stageId": ETAPA_CLASSIFICATORIA}

    combinada = combinar(
        {
            "stages": [str(item) for item in marco.etapas],
            "operation": marco.operacao,
            "normalization": marco.normalizacao,
            "rounding": marco.arredondamento,
        },
        {ETAPA_CLASSIFICATORIA: {"weight": "2.0000"}},
        {ETAPA_CLASSIFICATORIA: Decimal("8.5")},
    )

    assert combinada is not SEM_PONTUACAO
    assert combinada == Decimal("17.00")


def test_marco_sem_etapa_e_recusado(client, com_etapas):
    resposta = client.post(
        reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"]),
        marco_form(**{f"marco-{PERFIL}-0-stages": ""}),
    )

    assert resposta.status_code == 200, "recusa reexibe o formulário"
    assert not MarcoClassificatorio.objects.filter(pk=MARCO).exists()


def test_criterio_sem_alvo_e_recusado(client, com_etapas):
    resposta = client.post(
        reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"]),
        marco_form(**{f"criterio-{PERFIL}-0-0-target": ""}),
    )

    assert resposta.status_code == 200
    assert not MarcoClassificatorio.objects.filter(pk=MARCO).exists()


def test_gravar_a_classificacao_preserva_o_resto_do_perfil(client, com_etapas):
    """`replace_draft` substitui o rascunho inteiro: este passo funde marcos sobre o persistido."""
    perfil = com_etapas.perfis.get()
    antes = (perfil.name, perfil.locality, perfil.immediate_vacancies)

    client.post(
        reverse("interface:compor-etapa", args=[com_etapas.id, "classificacao"]), marco_form()
    )

    perfil.refresh_from_db()
    assert (perfil.name, perfil.locality, perfil.immediate_vacancies) == antes
