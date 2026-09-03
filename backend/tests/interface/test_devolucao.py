"""O caminho de volta, pela tela de quem revisa (FR-006, FR-028).

**Por que existe.** Uma auditoria de percurso abriu a tela de homologação e não encontrou recusa
nenhuma: quem revisava e discordava tinha "Homologar" e mais nada. As duas saídas restantes eram
cancelar — estado final, que queima o número no escopo — ou homologar o que se recusa, para
retificar depois de publicar o defeito de propósito.

A FR-006 já dizia que "antes da Publicação, a revisão PODE devolver o Edital a Em elaboração".
Faltava o ato. O que estes testes prendem é a volta pelo canal do ator (Princípio VI): a oferta
aparece para quem revisa, diz a quem entrega o bastão, e o formulário volta a aceitar depois.
"""

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models import RevisaoEdital
from tests.interface.conftest import compor_rascunho, identificar
from tests.interface.test_fluxo import EVENTOS, PERFIS, praticar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

MOTIVO = "O Cronograma não confere com a portaria: corrija as datas da prova."


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    return Edital.objects.get()


@pytest.fixture
def submetido(client, seletor_ligado, edital):
    """Um Edital em revisão, composto e submetido pela própria tela."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, PERFIS, EVENTOS)
    praticar(client, Edital.objects.get(), "submeter")
    assert Edital.objects.get().status == Edital.Status.EM_REVISAO
    return Edital.objects.get()


def test_quem_revisa_encontra_a_devolucao_na_tela(client, submetido):
    """A oferta existe onde a discordância acontece — e não só no domínio."""
    identificar(client, "bruno.homologador", ["homologador"])

    corpo = client.get(reverse("interface:detalhe", args=[submetido.id])).content.decode()

    assert "Devolver para elaboração" in corpo


def test_a_confirmacao_diz_o_que_provoca_e_para_quem_o_bastao_volta(client, submetido):
    """FR-028: devolver é o único ato que anda para trás, e dizer isso antes é o que o separa
    de uma recusa muda."""
    identificar(client, "bruno.homologador", ["homologador"])

    corpo = client.get(reverse("interface:ato", args=[submetido.id, "devolver"])).content.decode()

    assert "volta para elaboração e pode ser editado novamente" in corpo
    assert "aguardando quem elabora" in corpo
    assert "Motivo da devolução" in corpo


def test_devolver_pela_tela_reabre_a_elaboracao(client, submetido):
    """A volta inteira, pelo canal do ator: devolve, edita de novo, submete de novo."""
    identificar(client, "bruno.homologador", ["homologador"])
    resposta, _ = praticar(client, submetido, "devolver", motivo=MOTIVO)
    assert resposta.status_code == 302

    identificar(client, "ana.elaboradora", ["elaborador"])
    atual = Edital.objects.get()
    assert atual.status == Edital.Status.EM_ELABORACAO
    compor_rascunho(client, atual, PERFIS, EVENTOS)
    praticar(client, Edital.objects.get(), "submeter")

    assert Edital.objects.get().status == Edital.Status.EM_REVISAO
    assert RevisaoEdital.objects.filter(edital=submetido).count() == 2, (
        "a revisão devolvida é preservada, e a nova submissão acrescenta outra"
    )


def test_o_motivo_e_exigido_antes_do_command(client, submetido):
    """A recusa aparece na tela que a provocou, e o Edital não sai do lugar."""
    identificar(client, "bruno.homologador", ["homologador"])
    url = reverse("interface:ato", args=[submetido.id, "devolver"])
    chave = client.get(url).context["chave_idempotencia"]

    resposta = client.post(url, {"chave_idempotencia": chave, "motivo": "   "})

    assert resposta.status_code == 422
    assert "Motivo da devolução é obrigatório." in resposta.content.decode()
    assert Edital.objects.get().status == Edital.Status.EM_REVISAO


def test_quem_elabora_nao_recebe_a_oferta_nem_o_ato(client, submetido):
    """Devolver desfaz a revisão de outra pessoa: é ato de quem revisa (FR-012)."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    url = reverse("interface:ato", args=[submetido.id, "devolver"])

    corpo = client.get(reverse("interface:detalhe", args=[submetido.id])).content.decode()
    recusa = client.post(url, {"chave_idempotencia": "ui-" + "0" * 29, "motivo": MOTIVO})

    assert "Devolver para elaboração" not in corpo
    assert recusa.status_code == 403
    assert Edital.objects.get().status == Edital.Status.EM_REVISAO


def test_o_edital_em_elaboracao_nao_oferece_devolucao(client, seletor_ligado, edital):
    """Não há o que devolver antes de alguém submeter."""
    identificar(client, "bruno.homologador", ["homologador"])

    corpo = client.get(reverse("interface:detalhe", args=[edital.id])).content.decode()

    assert "Devolver para elaboração" not in corpo
