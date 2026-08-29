"""FR-016 a FR-018 da 003: produção não sobe insegura.

Cada pressuposto de segurança vira precondição de inicialização. O teste carrega o módulo de
produção com variáveis de ambiente controladas e verifica que a falta ou o valor inseguro de
cada uma impede o processo de iniciar, nomeando a variável a corrigir.
"""

import importlib
import os
from unittest import mock

import pytest
from django.core.exceptions import ImproperlyConfigured

CHAVE_VALIDA = "8f2a-Kq7!zR3wLpX9nB6vT1yU4sE0mHdC5gJiOaZrQ2fW.tYuNbVcXlPkMjHgFdSa"
AMBIENTE_MINIMO = {
    "DJANGO_SECRET_KEY": CHAVE_VALIDA,
    "DJANGO_ALLOWED_HOSTS": "processos.cefor.ifes.edu.br",
    "API_AUTHENTICATION_CLASSES": "processo_seletivo.seguranca.ldap.LdapAuthentication",
    "DB_RUNTIME_PASSWORD": "segredo-do-runtime",
}
ADAPTADOR_PROVISORIO = (
    "processo_seletivo.seguranca.api.authentication.InstitutionalBearerAuthentication"
)


def _carregar(**alteracoes):
    """Recarrega a configuração de produção sob o ambiente informado.

    `base` precisa ser recarregado antes: `production` a importa do `sys.modules` e leria os
    valores da carga anterior, não os deste cenário.
    """
    ambiente = {**AMBIENTE_MINIMO, **alteracoes}
    ambiente = {chave: valor for chave, valor in ambiente.items() if valor is not None}
    with mock.patch.dict(os.environ, ambiente, clear=True):
        importlib.reload(importlib.import_module("config.settings.base"))
        return importlib.reload(importlib.import_module("config.settings.production"))


@pytest.fixture(autouse=True)
def restaurar_configuracao():
    """Devolve os módulos ao ambiente real do processo, para não contaminar os demais testes."""
    yield
    importlib.reload(importlib.import_module("config.settings.base"))


def test_ambiente_completo_carrega_com_transporte_seguro():
    producao = _carregar()
    assert producao.DEBUG is False
    assert producao.ALLOWED_HOSTS == ["processos.cefor.ifes.edu.br"]
    assert producao.SECURE_SSL_REDIRECT is True
    assert producao.SECURE_HSTS_SECONDS >= 31536000
    assert producao.SESSION_COOKIE_SECURE is True
    assert producao.CSRF_COOKIE_SECURE is True
    assert producao.X_FRAME_OPTIONS == "DENY"
    assert producao.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] == [
        "processo_seletivo.seguranca.ldap.LdapAuthentication"
    ]


@pytest.mark.parametrize(
    ("alteracoes", "variavel"),
    [
        ({"DJANGO_SECRET_KEY": None}, "DJANGO_SECRET_KEY"),
        ({"DJANGO_SECRET_KEY": "unsafe-development-key"}, "DJANGO_SECRET_KEY"),
        ({"DJANGO_SECRET_KEY": "curta-demais"}, "DJANGO_SECRET_KEY"),
        ({"DJANGO_SECRET_KEY": "a" * 60}, "DJANGO_SECRET_KEY"),
        ({"DJANGO_SECRET_KEY": f"django-insecure-{CHAVE_VALIDA}"}, "DJANGO_SECRET_KEY"),
        ({"DJANGO_ALLOWED_HOSTS": None}, "DJANGO_ALLOWED_HOSTS"),
        ({"DJANGO_ALLOWED_HOSTS": "*"}, "DJANGO_ALLOWED_HOSTS"),
        ({"API_AUTHENTICATION_CLASSES": None}, "API_AUTHENTICATION_CLASSES"),
        ({"API_AUTHENTICATION_CLASSES": ADAPTADOR_PROVISORIO}, "API_AUTHENTICATION_CLASSES"),
        ({"INTERFACE_SELETOR_IDENTIDADE": "true"}, "INTERFACE_SELETOR_IDENTIDADE"),
        ({"DB_RUNTIME_PASSWORD": None}, "DB_RUNTIME_PASSWORD"),
        ({"DJANGO_SECURE_SSL_REDIRECT": "false"}, "DJANGO_SECURE_SSL_REDIRECT"),
        ({"DJANGO_SECURE_HSTS_SECONDS": "60"}, "DJANGO_SECURE_HSTS_SECONDS"),
    ],
)
def test_configuracao_insegura_impede_a_inicializacao(alteracoes, variavel):
    with pytest.raises(ImproperlyConfigured) as recusa:
        _carregar(**alteracoes)
    assert variavel in str(recusa.value)


def test_o_adaptador_provisorio_nao_e_admitido_nem_acompanhado():
    """Declarar a autenticação institucional ao lado do adaptador não vale: ele continua aceito."""
    with pytest.raises(ImproperlyConfigured):
        _carregar(
            API_AUTHENTICATION_CLASSES=(
                f"processo_seletivo.seguranca.ldap.LdapAuthentication,{ADAPTADOR_PROVISORIO}"
            )
        )
