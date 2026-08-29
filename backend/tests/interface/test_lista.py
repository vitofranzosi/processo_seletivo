"""Tela de lista de Processos e Editais (US1 da 002).

Verifica o que a tela promete: escopo institucional respeitado, ações filtradas por permissão,
e o mínimo de acessibilidade estrutural exigido por FR-023 e FR-024 desde a primeira tela.
"""

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import ProcessoSeletivo
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar


@pytest.fixture
def cenario(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload)


@pytest.mark.django_db
@pytest.mark.integration
def test_lista_exige_identificacao(client, seletor_ligado):
    resposta = client.get(reverse("interface:lista"))
    assert resposta.status_code == 302
    assert resposta["Location"] == reverse("interface:identificar")


@pytest.mark.django_db
@pytest.mark.integration
def test_lista_mostra_processos_e_editais_do_escopo(client, seletor_ligado, cenario):
    identificar(client, "bruno.homologador", ["homologador"])
    corpo = client.get(reverse("interface:lista")).content.decode()

    processo = ProcessoSeletivo.objects.get()
    assert processo.institutional_code in corpo
    assert processo.title in corpo
    assert f"{cenario.number}/{cenario.year}" in corpo
    assert cenario.title in corpo
    assert "Publicado" in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_lista_nao_revela_processo_de_outro_escopo(client, seletor_ligado, cenario, settings):
    """Anti-IDOR: a listagem não pode ser a brecha por onde se enxerga o que não se alcança."""
    identificar(client, "gestor.externo", ["gestor"])
    sessao = client.session
    sessao["interface_identidade"] = {
        "subject": "gestor.externo",
        "escopo": "outra-instituicao",
        "papeis": ["gestor"],
    }
    sessao.save()

    corpo = client.get(reverse("interface:lista")).content.decode()
    assert ProcessoSeletivo.objects.get().institutional_code not in corpo
    assert "Nenhum Processo Seletivo no seu escopo" in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_acoes_seguem_a_permissao_de_quem_olha(client, seletor_ligado, cenario):
    """FR-002: a tela oferece só o que a pessoa pode fazer — sem que isso substitua o backend."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    elaborador = client.get(reverse("interface:lista")).content.decode()
    assert "Retificar" in elaborador
    assert "Encerrar" not in elaborador

    client.post(reverse("interface:sair"))
    identificar(client, "marcia.gestora", ["gestor"])
    gestor = client.get(reverse("interface:lista")).content.decode()
    assert "Encerrar" in gestor
    assert "Retificar" not in gestor


@pytest.mark.django_db
@pytest.mark.integration
def test_pessoa_sem_papel_recebe_orientacao_e_nao_area_vazia(client, seletor_ligado, cenario):
    """FR-028: sem papel reconhecido, orientar a quem pedir acesso."""
    resposta = client.post(
        reverse("interface:identificar"), {"subject": "servidor.novo", "papeis": []}
    )
    assert resposta.status_code == 422
    assert "ao menos um papel" in resposta.content.decode()


@pytest.mark.django_db
@pytest.mark.integration
def test_estrutura_acessivel_da_lista(client, seletor_ligado, cenario):
    """FR-023 e FR-024 desde a primeira tela, não como retrabalho no fim."""
    identificar(client, "bruno.homologador", ["homologador"])
    corpo = client.get(reverse("interface:lista")).content.decode()

    assert 'lang="pt-BR"' in corpo
    assert 'class="pular" href="#conteudo"' in corpo, "link de pular para o conteúdo"
    assert corpo.count("<h1>") == 1, "exatamente um h1 por página"
    assert 'scope="col"' in corpo and 'scope="row"' in corpo, "cabeçalhos de tabela associados"
    assert "<caption>" in corpo, "tabela precisa de legenda"
    assert "aria-label" in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_ambiente_de_demonstracao_e_anunciado(client, seletor_ligado, cenario):
    """A pessoa precisa saber que a identidade não veio do diretório institucional."""
    identificar(client, "bruno.homologador", ["homologador"])
    corpo = client.get(reverse("interface:lista")).content.decode()
    assert "Ambiente de demonstração" in corpo
    assert "não pode ser usada em produção" in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_seletor_de_identidade_nao_existe_com_a_configuracao_desligada(client, settings):
    """Fora de desenvolvimento o seletor não existe: ele substitui a autenticação."""
    settings.INTERFACE_SELETOR_IDENTIDADE = False
    resposta = client.get(reverse("interface:identificar"))
    assert resposta.status_code == 503
    corpo = resposta.content.decode()
    assert "Autenticação institucional não configurada" in corpo
    assert "checkbox" not in corpo, "nenhum papel pode ser escolhido"


@pytest.mark.django_db
@pytest.mark.integration
def test_plural_de_edital_em_portugues(
    client, seletor_ligado, cenario, api_client, manager_headers
):
    """Plural em português não sai de sufixo: 'Editalis' apareceu na tela antes disto."""
    identificar(client, "bruno.homologador", ["homologador"])
    corpo = client.get(reverse("interface:lista")).content.decode()
    assert "1 Edital neste Processo" in corpo
    assert "Editalis" not in corpo

    api_client.post(
        f"/api/v1/admin/processos/{cenario.processo_id}/editais",
        {"number": "31", "year": 2026, "title": "Segundo"},
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "plural-key-00000001"},
    )
    corpo = client.get(reverse("interface:lista")).content.decode()
    assert "2 Editais neste Processo" in corpo
