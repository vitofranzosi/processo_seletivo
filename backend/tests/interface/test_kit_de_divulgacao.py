"""A tela do kit de divulgação: a ação, os modos, as faixas e a forma (111, FR-3401, FR-3443)."""

import pytest
from django.urls import reverse

from tests.fixtures import kit
from tests.interface.conftest import identificar

pytestmark = pytest.mark.django_db

PUBLICO = "gps.exemplo.ifes.edu.br"


@pytest.fixture
def host_publico(settings):
    settings.ALLOWED_HOSTS = [*settings.ALLOWED_HOSTS, PUBLICO]
    return PUBLICO


def _url(edital):
    return reverse("interface:kit-de-divulgacao", args=[edital.id])


def test_a_acao_aparece_so_com_a_capacidade(api_client, client, seletor_ligado):
    edital = kit.publicar(api_client, ate=1, chave="acao-do-kit")
    detalhe = reverse("interface:detalhe", args=[edital.id])
    identificar(client, "cora.comunicacao", ["comunicacao"])
    assert _url(edital) in client.get(detalhe).content.decode()
    identificar(client, "gustavo.gestor", ["gestor"])
    assert _url(edital) not in client.get(detalhe).content.decode()


def test_antes_da_publicacao_a_acao_e_indisponivel_com_motivo(client, seletor_ligado, edital):
    identificar(client, "cora.comunicacao", ["comunicacao"])
    corpo = client.get(reverse("interface:detalhe", args=[edital.id])).content.decode()
    assert "O kit de divulgação fica disponível quando o Edital for publicado." in corpo


def test_tela_com_periodo(api_client, client, seletor_ligado, host_publico):
    edital = kit.publicar(api_client, ate=1, chave="tela-do-kit")
    identificar(client, "cora.comunicacao", ["comunicacao"])
    resposta = client.get(_url(edital), HTTP_HOST=host_publico)
    corpo = resposta.content.decode()
    assert resposta.status_code == 200
    assert "no-store" in resposta["Cache-Control"]
    for trecho in (
        "Confira as informações oficiais",
        "Polo Bom Jesus do Norte: 40 vagas",
        "Legenda para rede social",
        "busque por 91/2026 – Cefor",
        # O esquema é o da requisição: `https` em produção, atrás do proxy, e `http` aqui.
        f"//{host_publico}/selecoes/{edital.id}/",
        'name="impressao"',
        "Copiar",
    ):
        assert trecho in corpo, trecho


def test_tela_neutra_e_sem_material(api_client, client, seletor_ligado):
    neutro = kit.publicar(api_client, chave="tela-neutra", mudar=kit.sem_periodo)
    identificar(client, "cora.comunicacao", ["comunicacao"])
    corpo = client.get(_url(neutro)).content.decode()
    assert "não recebe inscrições pelo GPS" in corpo


def test_host_local_sem_link_absoluto(api_client, client, seletor_ligado):
    edital = kit.publicar(api_client, ate=1, chave="tela-local")
    identificar(client, "cora.comunicacao", ["comunicacao"])
    corpo = client.get(_url(edital)).content.decode()  # testserver é host local
    assert "O endereço público não é conhecido neste acesso" in corpo
    assert "http://testserver/selecoes" not in corpo


def test_exportacoes_por_formulario(api_client, client, seletor_ligado):
    """Sem script, exportar funciona: são formulários comuns (EC-22)."""
    edital = kit.publicar(api_client, ate=1, chave="tela-formulario")
    identificar(client, "cora.comunicacao", ["comunicacao"])
    corpo = client.get(_url(edital)).content.decode()
    for formato in ("md", "txt"):
        assert reverse("interface:kit-de-divulgacao-exportar", args=[edital.id, formato]) in corpo
    assert 'method="post"' in corpo


def test_nenhum_estilo_nem_script_embutido(api_client, client, seletor_ligado):
    edital = kit.publicar(api_client, ate=1, chave="tela-csp")
    identificar(client, "cora.comunicacao", ["comunicacao"])
    corpo = client.get(_url(edital)).content.decode()
    assert ' style="' not in corpo and "<style" not in corpo
    assert "onclick=" not in corpo
    assert "interface/kit-de-divulgacao.js" in corpo
