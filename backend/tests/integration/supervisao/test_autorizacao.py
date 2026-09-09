"""A porta da supervisão, e a recusa que não distingue o que não pode do que não existe.

`FR-002`, `FR-003` e `SC-012`. A negação faz parte da entrega: sem o 404 uniforme demonstrado, a
feature não entregou o que promete.
"""

import re
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


# ---------------------------------------------------------------------------
# Supressão por alcance, e o que ela **não** alcança (`US4`)
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_quem_nao_alcanca_os_recursos_nao_ve_o_sinal_nem_a_supressao(
    client, seletor_ligado, gestor, api_client, manager_headers, process_payload
):
    """`FR-004` e `SC-013`: a supressão é silenciosa, e a razão é vazamento por agregação.

    Anunciar que existe um sinal suprimido diria a quem não pode vê-lo que **há** algo para ver.
    A contraprova de `FR-004a` vem junto: os agregados do Pulso continuam visíveis para o mesmo
    ator, porque eles não têm destino nem dado pessoal.
    """
    from django.utils import timezone

    from processo_seletivo.avaliacoes.models import Impedimento
    from tests.fixtures.recursos_us4 import cenario_julgavel

    peca = cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=151, codigo="0511"
    )
    Impedimento.objects.create(
        identity_subject="maria",
        inscricao=peca["inscricao"],
        motivo="Parentesco declarado.",
        criado_em=timezone.now(),
        criado_por="carlos",
    )
    processo = peca["cenario"]["processo"]

    # Maria preside, e por isso a página abre; ela **não** detém a permissão de julgar recurso, e
    # por isso a tela dona daquele sinal está fora do alcance dela.
    identificar(client, "maria", [])
    corpo = client.get(url(processo)).content.decode()

    # O que a página **apresenta**, sem marcação: a folha de estilo define uma classe chamada
    # `oculto`, e procurar a palavra no HTML cru acusaria vazamento onde há CSS.
    apresentado = re.sub(r"<[^>]+>", " ", re.sub(r"(?s)<style>.*?</style>", " ", corpo)).lower()
    assert "impedidos de julgar" not in apresentado
    for vazamento in ("suprimid", "oculto", "sem permissão", "você não pode"):
        assert vazamento not in apresentado
    # O Pulso continua inteiro: ele não é suprimido por alcance.
    assert "Pulso" in corpo
    assert "Inscrições por Edital" in corpo


def test_processo_cancelado_le_e_nao_oferece_o_que_a_situacao_nao_admite(
    client, seletor_ligado, processo_a, edital_a, comissao_de_a
):
    """`FR-036`: a supervisão continua legível, e o beco não é oferecido.

    Processo em estado final não admite alteração dos seus Editais — é o domínio que diz —, e
    encaminhar para a composição seria mandar quem lê a uma tela onde não há o que fazer. A `007`
    passou uma feature inteira tirando exatamente isso.
    """
    from processo_seletivo.interface import supervisao
    from tests.conftest import ator_institucional

    presidenta = ator_institucional("maria")
    antes = supervisao.sinais(processo_a, presidenta)
    assert [sinal.especie for sinal in antes] == [supervisao.UX_001]
    assert antes[0].destino is not None

    ProcessoSeletivo.objects.filter(pk=processo_a.pk).update(
        status=ProcessoSeletivo.Status.CANCELADO
    )
    processo_a.refresh_from_db()

    identificar(client, "maria", [])
    assert client.get(url(processo_a)).status_code == 200

    depois = supervisao.sinais(processo_a, presidenta)
    assert [sinal.especie for sinal in depois] == [supervisao.UX_001]
    assert depois[0].destino is None, "o encaminhamento que a situação não admite não é oferecido"
