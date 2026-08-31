"""Quem pode ler o que o candidato enviou (US6 da 009, FR-072).

Dado pessoal e documento comprobatório têm acesso restrito por exigência constitucional. A
permissão é própria — `inscricao:consultar` — porque nenhuma das existentes significa "pode ler
dado pessoal de candidato", e reaproveitar uma delas seria decidir por omissão.
"""

import pytest
from django.urls import reverse

from processo_seletivo.inscricoes.application.rascunho import anexar_documento, gravar_dados
from tests.fixtures.candidato import MARIA, MODALIDADE_AC, pdf
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS
from tests.interface.conftest import identificar

TELAS = ("interface:inscricoes",)


@pytest.fixture
def com_documento(inscricao_de_maria):
    inscricao = gravar_dados(
        identidade=MARIA, inscricao=inscricao_de_maria, dados={"modality_id": MODALIDADE_AC}
    )
    anexar_documento(
        identidade=MARIA,
        inscricao=inscricao,
        requirement_id=DOCUMENTO_DE_TODOS,
        arquivo=pdf("rg.pdf"),
    )
    inscricao.refresh_from_db()
    return inscricao


@pytest.mark.django_db(transaction=True)
@pytest.mark.authorization
@pytest.mark.parametrize("papel", ["elaborador", "homologador", "publicador", "auditor"])
def test_papel_sem_a_permissao_nao_alcanca_a_lista(
    client, settings, selecao, com_documento, papel
):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    identificar(client, f"pessoa.{papel}", [papel])

    resposta = client.get(reverse("interface:inscricoes", args=[selecao.id]))

    assert resposta.status_code == 403


@pytest.mark.django_db(transaction=True)
@pytest.mark.authorization
def test_o_gestor_alcanca(client, settings, selecao, com_documento):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    identificar(client, "bruno.gestor", ["gestor"])

    assert client.get(reverse("interface:inscricoes", args=[selecao.id])).status_code == 200


@pytest.mark.django_db(transaction=True)
@pytest.mark.authorization
def test_sem_permissao_o_detalhe_e_o_arquivo_tambem_sao_recusados(
    client, settings, com_documento
):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    identificar(client, "ana.elaboradora", ["elaborador"])

    detalhe = client.get(reverse("interface:inscricao-recebida", args=[com_documento.id]))
    arquivo = client.get(
        reverse("interface:documento-da-inscricao", args=[com_documento.id, DOCUMENTO_DE_TODOS])
    )

    assert detalhe.status_code == 403
    assert arquivo.status_code == 403
    assert b"%PDF" not in arquivo.content


@pytest.mark.django_db(transaction=True)
@pytest.mark.authorization
def test_escopo_institucional_diferente_nao_enxerga(client, settings, selecao, com_documento):
    """Edital de outro escopo não é "sem permissão": é inexistente para quem pergunta."""
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    identificar(client, "gestor.de.outro", ["gestor"], escopo="outra-unidade")

    lista = client.get(reverse("interface:inscricoes", args=[selecao.id]))
    detalhe = client.get(reverse("interface:inscricao-recebida", args=[com_documento.id]))

    assert lista.status_code == 404
    assert detalhe.status_code == 404


@pytest.mark.django_db(transaction=True)
@pytest.mark.authorization
def test_sem_identificar_se_a_consulta_leva_a_identificacao(client, settings, selecao):
    settings.INTERFACE_SELETOR_IDENTIDADE = True

    resposta = client.get(reverse("interface:inscricoes", args=[selecao.id]))

    assert resposta.status_code == 302
    assert reverse("interface:identificar") in resposta["Location"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.authorization
def test_o_candidato_nao_alcanca_a_consulta_administrativa(
    client, settings, selecao, com_documento
):
    """Os dois eixos não se emprestam: a sessão do portal não vale no `/gestao/`."""
    from tests.fixtures.candidato import identificar as identificar_candidato

    settings.INTERFACE_SELETOR_IDENTIDADE = True
    identificar_candidato(client, MARIA)

    resposta = client.get(reverse("interface:inscricoes", args=[selecao.id]))

    assert resposta.status_code == 302, "a gestão manda identificar-se"
