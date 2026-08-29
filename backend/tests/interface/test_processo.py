"""Tela de desfecho do Processo Seletivo (US5 da 002).

O cenário que dá nome à história: quando o cancelamento é impedido, a tela precisa identificar
o que impede e permitir alcançar cada pendência — antes da tentativa, não depois da recusa.
"""

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import Edital, ProcessoSeletivo
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar

GESTOR = ["gestor"]


@pytest.fixture
def cenario(api_client, manager_headers, process_payload):
    edital = publish_original(api_client, manager_headers, process_payload)
    return ProcessoSeletivo.objects.get(), edital


def ato(client, processo, acao, motivo="Ato motivado"):
    url = reverse("interface:processo-ato", args=[processo.id, acao])
    chave = client.get(url).context["chave_idempotencia"]
    return client.post(url, {"chave_idempotencia": chave, "motivo": motivo})


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_detalhe_mostra_a_trilha_e_os_editais(client, seletor_ligado, cenario):
    processo, edital = cenario
    identificar(client, "marcia.gestora", GESTOR)
    corpo = client.get(reverse("interface:processo-detalhe", args=[processo.id])).content.decode()

    assert processo.institutional_code in corpo
    assert f"{edital.number}/{edital.year}" in corpo
    assert 'class="e-atual"' in corpo
    assert "Ativar Processo" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_impedimento_do_cancelamento_e_mostrado_antes_da_tentativa(
    client, seletor_ligado, cenario
):
    """FR-018: identificar o que impede e permitir alcançar cada pendência."""
    processo, edital = cenario
    identificar(client, "marcia.gestora", GESTOR)

    detalhe = client.get(reverse("interface:processo-detalhe", args=[processo.id])).content.decode()
    assert "O cancelamento do Processo está impedido" in detalhe
    assert f"{edital.number}/{edital.year}" in detalhe
    assert reverse("interface:detalhe", args=[edital.id]) in detalhe, "link para a pendência"

    confirmacao = client.get(
        reverse("interface:processo-ato", args=[processo.id, "cancelar"])
    ).content.decode()
    assert "Este ato será recusado" in confirmacao
    assert "Encerrado ou Cancelado" in confirmacao


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_cancelamento_e_recusado_pelo_dominio_e_explicado(client, seletor_ligado, cenario):
    processo, _ = cenario
    identificar(client, "marcia.gestora", GESTOR)
    resposta = ato(client, processo, "cancelar", "Tentativa prematura")

    assert resposta.status_code == 409
    assert "Cancele ou encerre cada Edital" in resposta.content.decode()
    assert ProcessoSeletivo.objects.get().status == processo.status


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_cancelamento_e_admitido_quando_os_editais_sao_finalizados(
    client, seletor_ligado, cenario
):
    processo, edital = cenario
    identificar(client, "marcia.gestora", ["gestor"])
    # Encerrar o Edital exige permissão própria; o gestor a possui.
    url = reverse("interface:ato", args=[edital.id, "encerrar"])
    chave = client.get(url).context["chave_idempotencia"]
    client.post(url, {"chave_idempotencia": chave, "motivo": "Etapas concluídas"})
    assert Edital.objects.get().status == Edital.Status.ENCERRADO

    processo.refresh_from_db()
    detalhe = client.get(reverse("interface:processo-detalhe", args=[processo.id])).content.decode()
    assert "está impedido" not in detalhe

    assert ato(client, processo, "cancelar", "Todos finalizados").status_code == 302
    assert ProcessoSeletivo.objects.get().status == ProcessoSeletivo.Status.CANCELADO


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_ativar_e_encerrar_seguem_o_fluxo_ordinario(client, seletor_ligado, cenario):
    processo, _ = cenario
    identificar(client, "marcia.gestora", GESTOR)

    assert ato(client, processo, "ativar", "Abertura formal").status_code == 302
    assert ProcessoSeletivo.objects.get().status == ProcessoSeletivo.Status.ATIVO

    processo.refresh_from_db()
    corpo = client.get(reverse("interface:processo-detalhe", args=[processo.id])).content.decode()
    assert "Encerrar Processo" in corpo
    assert "Ativar Processo" not in corpo, "não se ativa o que já está ativo"

    assert ato(client, processo, "encerrar", "Certame concluído").status_code == 302
    assert ProcessoSeletivo.objects.get().status == ProcessoSeletivo.Status.ENCERRADO


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_encerrar_avisa_que_os_editais_deixam_de_aceitar_alteracao(
    client, seletor_ligado, cenario
):
    processo, _ = cenario
    identificar(client, "marcia.gestora", GESTOR)
    ato(client, processo, "ativar", "Abertura")
    processo.refresh_from_db()

    corpo = client.get(
        reverse("interface:processo-ato", args=[processo.id, "encerrar"])
    ).content.decode()
    assert "Este ato não pode ser desfeito" in corpo
    assert "deixam de aceitar qualquer alteração" in corpo
    assert "permanecem disponíveis na consulta pública" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_cancelamento_avisa_que_nao_propaga_para_os_editais(client, seletor_ligado, cenario):
    """FR-034: cancelar o Processo não cancela Editais; cada um exige ato próprio."""
    processo, _ = cenario
    identificar(client, "marcia.gestora", GESTOR)
    corpo = client.get(
        reverse("interface:processo-ato", args=[processo.id, "cancelar"])
    ).content.decode()
    assert "Nenhum Edital é cancelado por consequência" in corpo
    assert "não é o mesmo que encerramento regular" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_motivo_e_obrigatorio_em_todo_ato_do_processo(client, seletor_ligado, cenario):
    processo, _ = cenario
    identificar(client, "marcia.gestora", GESTOR)
    resposta = ato(client, processo, "ativar", motivo="   ")
    assert resposta.status_code == 422
    assert "é obrigatório" in resposta.content.decode()
    assert ProcessoSeletivo.objects.get().status == ProcessoSeletivo.Status.EM_ELABORACAO


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_ato_do_processo_exige_permissao(client, seletor_ligado, cenario):
    processo, _ = cenario
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(reverse("interface:processo-detalhe", args=[processo.id])).content.decode()
    assert "Ativar Processo" not in corpo

    resposta = ato(client, processo, "ativar", "Tentativa")
    assert resposta.status_code == 403
    assert ProcessoSeletivo.objects.get().status == ProcessoSeletivo.Status.EM_ELABORACAO


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_processo_de_outro_escopo_nao_e_alcancavel(client, seletor_ligado, cenario):
    processo, _ = cenario
    identificar(client, "marcia.gestora", GESTOR)
    sessao = client.session
    sessao["interface_identidade"] = {
        "subject": "marcia.gestora",
        "escopo": "outra-instituicao",
        "papeis": ["gestor"],
    }
    sessao.save()
    assert client.get(
        reverse("interface:processo-detalhe", args=[processo.id])
    ).status_code == 404
