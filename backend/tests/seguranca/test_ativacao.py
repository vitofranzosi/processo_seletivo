"""Produção só entra pela autenticação institucional, e nunca cai para a demonstração (106, US4).

Testes 2 e 10 do pedido, em execução. A recusa de inicialização — `production.py` carregado com
cada configuração — está em `tests/test_configuracao_producao.py`.
"""

import pytest
from django.conf import settings as configuracao
from django.contrib.auth import authenticate, get_user_model
from django.urls import reverse

from processo_seletivo.interface import identidade
from processo_seletivo.interface.identidade import CHAVE_SESSAO
from tests.interface.conftest import identificar
from tests.seguranca.apoio import ator_do_cliente, entrar, pessoa, vincular

pytestmark = pytest.mark.django_db


# --- Teste 2: o modo demonstração é recusado em produção -----------------------------------------


def test_sob_a_marca_de_producao_o_seletor_nao_existe_mesmo_ligado(client, settings):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    settings.AMBIENTE_DE_PRODUCAO = True

    assert identidade.seletor_disponivel() is False
    assert identidade.metodos_disponiveis() == []
    assert client.get(reverse("interface:identificar")).status_code == 503
    assert client.get(reverse("interface:identificar-demonstracao")).status_code == 503
    resposta = client.post(
        reverse("interface:identificar"), {"subject": "ana.gestora", "papeis": ["gestor"]}
    )
    assert resposta.status_code == 503
    assert CHAVE_SESSAO not in client.session


def test_sessao_de_demonstracao_aberta_cai_sob_a_marca_de_producao(client, settings):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    identificar(client, "ana.gestora", ["gestor"])
    assert ator_do_cliente(client) is not None

    settings.AMBIENTE_DE_PRODUCAO = True

    assert ator_do_cliente(client) is None
    assert client.get(reverse("interface:lista")).status_code == 302
    assert CHAVE_SESSAO not in client.session


# --- Teste 10: configuração incompleta não autentica por fallback --------------------------------


def test_producao_sem_provedor_bloqueia_sem_oferecer_demonstracao(client, settings):
    settings.AMBIENTE_DE_PRODUCAO = True
    settings.INTERFACE_SELETOR_IDENTIDADE = False
    settings.GESTAO_PROVEDOR_INSTITUCIONAL = ""

    pagina = client.get(reverse("interface:identificar"))

    assert pagina.status_code == 503
    assert "demonstração" not in pagina.content.decode().lower().replace("ambiente de", "")
    assert client.get(reverse("interface:entrar-institucional")).status_code == 503
    assert client.get(reverse("interface:retorno-institucional")).status_code == 503


def test_o_provedor_de_teste_nao_autentica_sob_a_marca_de_producao(client, settings, provedor):
    settings.AMBIENTE_DE_PRODUCAO = True
    vincular(pessoa("ana"), "cefor", "gestor")

    assert identidade.metodos_disponiveis() == []
    assert client.get(reverse("interface:entrar-institucional")).status_code == 503


def test_o_provedor_marcado_de_teste_fora_de_tests_tambem_nao(client, settings, provedor):
    """A segunda recusa: a classe que se declara de teste, more onde morar."""
    import sys
    import types

    modulo = types.ModuleType("provedor_copiado_para_fora")
    modulo.Provedor = provedor.ProvedorSimulado
    sys.modules[modulo.__name__] = modulo
    try:
        settings.GESTAO_PROVEDOR_INSTITUCIONAL = "provedor_copiado_para_fora.Provedor"
        settings.AMBIENTE_DE_PRODUCAO = True
        assert client.get(reverse("interface:entrar-institucional")).status_code == 503
    finally:
        del sys.modules[modulo.__name__]


def test_sessao_institucional_cai_quando_o_provedor_some(client, settings, provedor):
    vincular(pessoa("ana-2"), "cefor", "gestor")
    entrar(client, "ana-2")
    assert ator_do_cliente(client) is not None

    settings.GESTAO_PROVEDOR_INSTITUCIONAL = ""

    assert ator_do_cliente(client) is None
    assert client.get(reverse("interface:lista")).status_code in {302, 503}
    assert CHAVE_SESSAO not in client.session


def test_sessao_institucional_nao_vira_demonstracao_com_o_seletor_ligado(
    client, settings, provedor
):
    """Sem provedor e com o seletor: a sessão institucional não é lida pelo ramo da demonstração."""
    vincular(pessoa("ana-3"), "cefor", "gestor")
    entrar(client, "ana-3")
    settings.GESTAO_PROVEDOR_INSTITUCIONAL = ""
    settings.INTERFACE_SELETOR_IDENTIDADE = True

    assert ator_do_cliente(client) is None


# --- O `User` do Django não autoriza nada --------------------------------------------------------


def test_o_unico_backend_e_o_institucional():
    assert configuracao.AUTHENTICATION_BACKENDS == [
        "processo_seletivo.seguranca.autenticacao.BackendInstitucional"
    ]
    assert "django.contrib.admin" not in configuracao.INSTALLED_APPS
    assert not any("RemoteUser" in classe for classe in configuracao.MIDDLEWARE)


def test_usuario_e_senha_nao_autenticam():
    get_user_model().objects.create_superuser("root", "root@exemplo.test", "senha-forte-123")

    assert authenticate(username="root", password="senha-forte-123") is None


def test_superusuario_sem_vinculo_nao_tem_ator(client, provedor):
    entrar(client, "chefe")
    get_user_model().objects.update(is_superuser=True, is_staff=True)

    assert ator_do_cliente(client) is None
