"""O rascunho depois do prazo diz que o prazo acabou (009, FR-032).

*"Encerrado o período, um rascunho NÃO DEVE poder ser enviado, e DEVE permanecer acessível ao
próprio titular apenas para consulta."* O domínio já recusava gravar, anexar e enviar; as telas não
sabiam. "Minhas inscrições" oferecia *Continuar inscrição*, a tela do rascunho dizia que os dados
ficavam guardados para voltar depois, e a revisão convidava a reconhecer a Retificação que fechou o
prazo e a enviar — e a pessoa só descobria o encerramento pela recusa (RC-49 da auditoria de 26/09,
achado E2E15-007).

O prazo se fecha aqui como se fecha na realidade: por Retificação que declara o término no passado
(`028`, FR-355), porque o sistema recusa publicar Edital com o período já vencido.
"""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from tests.fixtures.candidato import MARIA, identificar
from tests.fixtures.publicacao import encerrar_inscricoes

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def prazo_encerrado(inscricao_de_maria, selecao, api_client):
    fim = timezone.now() - timedelta(hours=1)
    encerrar_inscricoes(api_client, selecao, fim)
    return timezone.localtime(fim).strftime("%d/%m/%Y")


def _principal(client, endereco):
    """Só o `<main>`: a folha de estilo embutida cita "Inscrições encerradas" num comentário."""
    return client.get(endereco).content.decode().split("<main", 1)[1]


def test_minhas_inscricoes_diz_que_o_prazo_acabou_e_nao_convida_a_continuar(
    client, inscricao_de_maria, prazo_encerrado
):
    identificar(client, MARIA)

    corpo = _principal(client, reverse("portal:inscricoes"))

    assert f"Inscrições encerradas em {prazo_encerrado}" in corpo
    assert "Continuar inscrição" not in corpo
    assert "Consultar inscrição" in corpo


def test_a_tela_do_rascunho_diz_que_o_prazo_acabou_e_nao_oferece_avancar(
    client, inscricao_de_maria, prazo_encerrado
):
    identificar(client, MARIA)

    corpo = _principal(client, reverse("portal:inscricao", args=[inscricao_de_maria.id]))

    assert f"O período de inscrições terminou em {prazo_encerrado}" in corpo
    assert "Revisar inscrição" not in corpo
    assert "continuar depois" not in corpo and "sair e voltar" not in corpo


def test_a_revisao_diz_que_o_prazo_acabou_e_nao_convida_a_reconhecer_nem_a_enviar(
    client, inscricao_de_maria, prazo_encerrado
):
    identificar(client, MARIA)

    corpo = _principal(client, reverse("portal:revisao", args=[inscricao_de_maria.id]))

    assert f"O período de inscrições terminou em {prazo_encerrado}" in corpo
    assert "Li as alterações e quero continuar" not in corpo
    assert "Enviar inscrição" not in corpo


def test_com_o_prazo_aberto_nada_muda(client, inscricao_de_maria):
    identificar(client, MARIA)

    lista = _principal(client, reverse("portal:inscricoes"))
    rascunho = _principal(client, reverse("portal:inscricao", args=[inscricao_de_maria.id]))

    assert "Continuar inscrição" in lista
    assert "Inscrições encerradas" not in lista
    assert "Revisar inscrição" in rascunho
    assert "O período de inscrições terminou" not in rascunho
