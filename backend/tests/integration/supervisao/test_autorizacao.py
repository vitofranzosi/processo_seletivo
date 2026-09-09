"""A porta da supervisão, e a recusa que não distingue o que não pode do que não existe.

`FR-002`, `FR-003` e `SC-012`. A negação faz parte da entrega: sem o 404 uniforme demonstrado, a
feature não entregou o que promete.
"""

from uuid import uuid4

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import ProcessoSeletivo
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def url(processo):
    return reverse("interface:supervisao", args=[processo.id])


def test_quem_preside_abre_a_supervisao(client, seletor_ligado, processo_a, comissao_de_a):
    """A presidência **deste** Processo basta sozinha, sem papel sistêmico nenhum (`FR-002`)."""
    identificar(client, "maria", [])

    resposta = client.get(url(processo_a))

    assert resposta.status_code == 200


def test_a_permissao_sistemica_de_gerir_comissao_tambem_basta(
    client, seletor_ligado, processo_a, comissao_de_a
):
    """A outra base, também suficiente sozinha — é como a administração superior intervém."""
    identificar(client, "carlos", ["gestor"])

    resposta = client.get(url(processo_a))

    assert resposta.status_code == 200


def test_escopo_institucional_distinto_nao_alcanca(
    client, seletor_ligado, processo_a, comissao_de_a
):
    identificar(client, "maria", [], escopo="outra-unidade")

    assert client.get(url(processo_a)).status_code == 404


def test_quem_nao_tem_vinculo_nem_permissao_nao_alcanca(
    client, seletor_ligado, processo_a, comissao_de_a
):
    """Integrar a comissão não basta: a base é presidir, e joão é membro (`FR-002`)."""
    identificar(client, "joao", [])

    assert client.get(url(processo_a)).status_code == 404


def test_a_recusa_e_literalmente_igual_a_de_um_processo_inexistente(
    client, seletor_ligado, processo_a, comissao_de_a
):
    """`SC-012`: quem não alcança não consegue inferir que o Processo existe.

    A comparação é do corpo inteiro, e não só do status: uma página que dissesse "você não tem
    permissão para este Processo" responderia 404 e entregaria a existência dele mesmo assim.
    """
    identificar(client, "estranho", [])

    sem_autorizacao = client.get(url(processo_a))
    inexistente = client.get(
        reverse("interface:supervisao", args=[uuid4()]),
    )

    assert sem_autorizacao.status_code == inexistente.status_code == 404
    assert sem_autorizacao.content == inexistente.content


def test_processo_cancelado_continua_legivel_para_quem_preside(
    client, seletor_ligado, processo_a, comissao_de_a
):
    """Os fatos permanecem, e alguém responde por eles (`SC-012`, `FR-003`).

    Cancelar interrompe o certame; não apaga o que aconteceu nele. Fechar a leitura tiraria a
    supervisão justamente de quem ainda responde pelo que foi feito.
    """
    ProcessoSeletivo.objects.filter(pk=processo_a.pk).update(
        status=ProcessoSeletivo.Status.CANCELADO
    )
    identificar(client, "maria", [])

    assert client.get(url(processo_a)).status_code == 200
