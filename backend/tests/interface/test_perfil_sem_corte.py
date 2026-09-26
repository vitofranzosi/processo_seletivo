"""O Perfil que não convoca ninguém não atravessa a publicação (046, `FR-752`, `FR-753`, `SC-277`).

**O `RC-30` da auditoria de consolidação, e a `D-G1` que ele cobrava.** O Perfil cujo único marco
não declara regra de corte publicava com um aviso: classificava, publicava a ordem, e só na
convocação se descobria que ninguém podia ser chamado — sem corte não há faixa, e a convocação só
chama dentro de faixa.

**A invariante é do Perfil, e não do marco** (`D-002`). O marco que legitimamente não corta — o
preliminar de um Perfil que corta no final — continua publicável, com o aviso da `032`. É o que o
segundo caso prende, e é o que impede esta família de virar *"todo marco precisa de corte"*.
"""

import copy

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import Edital
from tests.fixtures.edital import actor_headers, complete_draft
from tests.fixtures.publicacao import levar_a_publicacao
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

# Sem as aspas do rótulo do Perfil, que o template escapa (`&#x27;`).
RECUSA = "declara regra de corte: sem corte não há faixa"
AVISO_DO_MARCO = "não declara regra de corte. Sem corte não há geração"
PRELIMINAR = "aaaaaaaa-0000-4000-8000-0000000046b1"


def _criar(api_client, manager_headers, process_payload):
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert criado.status_code == 201, criado.content
    return Edital.objects.get(processo_id=criado.json()["id"])


def _gravar(api_client, edital, rascunho):
    gravado = api_client.put(
        f"/api/v1/admin/editais/{edital.id}/rascunho",
        rascunho,
        format="json",
        **{
            **actor_headers("preparador", ["edital:elaborar"], key="046-perfil-sem-corte"),
            "HTTP_IF_MATCH": f'"{edital.revision}"',
        },
    )
    assert gravado.status_code == 200, gravado.content
    return Edital.objects.get(pk=edital.pk)


def _sem_corte():
    """O rascunho mínimo com o único marco em *"Este marco não corta"*: a regra sai inteira."""
    rascunho = complete_draft()
    rascunho["profiles"][0]["classificationMilestones"][0].pop("cutRule")
    return rascunho


def _com_preliminar_sem_corte():
    """O mesmo Perfil, com um marco preliminar que não corta antes do final que corta."""
    rascunho = complete_draft()
    final = rascunho["profiles"][0]["classificationMilestones"][0]
    preliminar = copy.deepcopy(final)
    preliminar.update({"id": PRELIMINAR, "code": "PRELIM", "name": "Classificação preliminar"})
    preliminar.pop("cutRule")
    rascunho["profiles"][0]["classificationMilestones"] = [preliminar, final]
    return rascunho


def _revisao(client, edital):
    resposta = client.get(reverse("interface:compor-etapa", args=[edital.id, "revisao"]))
    assert resposta.status_code == 200
    return resposta.content.decode()


def test_o_perfil_de_marco_unico_sem_corte_e_recusado_na_revisao_e_na_submissao(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    edital = _gravar(api_client, _criar(api_client, manager_headers, process_payload), _sem_corte())
    identificar(client, "ana.elaboradora", ["elaborador"])

    revisao = _revisao(client, edital)
    assert RECUSA in revisao
    trecho = revisao[: revisao.index(RECUSA)]
    assert trecho.rfind("p-erro") > trecho.rfind("p-aviso"), "dita como impedimento"
    destino = reverse("interface:compor-etapa", args=[edital.id, "classificacao"])
    assert f'href="{destino}#titulo-classificacao"' in revisao, "e corrige-se na Classificação"
    assert AVISO_DO_MARCO not in revisao, "um relato só para a mesma causa (FR-753)"

    client.post(reverse("interface:ato", args=[edital.id, "submeter"]), {})

    assert Edital.objects.get(pk=edital.pk).status == Edital.Status.EM_ELABORACAO


def test_o_marco_sem_corte_num_perfil_que_corta_continua_publicavel(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """O Cenário D do briefing: marco que legitimamente não corta não vira impedimento."""
    edital = _gravar(
        api_client,
        _criar(api_client, manager_headers, process_payload),
        _com_preliminar_sem_corte(),
    )
    identificar(client, "ana.elaboradora", ["elaborador"])

    revisao = _revisao(client, edital)
    assert RECUSA not in revisao
    assert revisao.count(AVISO_DO_MARCO) == 1, "um aviso, e só para o marco preliminar"
    assert "PRELIM" in revisao

    publicado = levar_a_publicacao(api_client, edital, draft=_com_preliminar_sem_corte())

    assert publicado.status == Edital.Status.PUBLICADO
