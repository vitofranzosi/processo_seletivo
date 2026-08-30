"""FR-016 a FR-018 da 003: produção não sobe insegura.

Cada pressuposto de segurança vira precondição de inicialização. O teste carrega o módulo de
produção com variáveis de ambiente controladas e verifica que a falta ou o valor inseguro de
cada uma impede o processo de iniciar, nomeando a variável a corrigir.
"""

import importlib
import os
import pathlib
from unittest import mock

import pytest
from django.core.exceptions import ImproperlyConfigured

CHAVE_VALIDA = "8f2a-Kq7!zR3wLpX9nB6vT1yU4sE0mHdC5gJiOaZrQ2fW.tYuNbVcXlPkMjHgFdSa"
AMBIENTE_MINIMO = {
    "DJANGO_SECRET_KEY": CHAVE_VALIDA,
    "DJANGO_ALLOWED_HOSTS": "processos.cefor.ifes.edu.br",
    # Classe real e importável: a barreira exige que exista, e um nome fictício aqui esconderia
    # justamente a falha que ela passou a detectar.
    "API_AUTHENTICATION_CLASSES": "rest_framework.authentication.RemoteUserAuthentication",
    "DB_RUNTIME_PASSWORD": "segredo-do-runtime",
}
ADAPTADOR_PROVISORIO = (
    "processo_seletivo.seguranca.api.authentication.InstitutionalBearerAuthentication"
)
INSTITUCIONAL = "rest_framework.authentication.RemoteUserAuthentication"


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
    assert producao.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] == [INSTITUCIONAL]


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
        (
            {"API_AUTHENTICATION_CLASSES": "rest_framework.authentication.BasicAuthentication"},
            "API_AUTHENTICATION_CLASSES",
        ),
        (
            {"API_AUTHENTICATION_CLASSES": "rest_framework.authentication.SessionAuthentication"},
            "API_AUTHENTICATION_CLASSES",
        ),
        (
            {"API_AUTHENTICATION_CLASSES": "processo_seletivo.seguranca.nao.Existe"},
            "API_AUTHENTICATION_CLASSES",
        ),
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
        _carregar(API_AUTHENTICATION_CLASSES=f"{INSTITUCIONAL},{ADAPTADOR_PROVISORIO}")


def test_a_barreira_recusa_o_modulo_de_desenvolvimento_inteiro():
    """Não é uma classe na lista negra: é o módulo, para que um adaptador novo herde a recusa."""
    with pytest.raises(ImproperlyConfigured) as recusa:
        _carregar(
            API_AUTHENTICATION_CLASSES=(
                "processo_seletivo.seguranca.api.authentication.QualquerOutroAdaptador"
            )
        )
    assert "diretório institucional" in str(recusa.value)


def test_deploy_check_nao_aponta_nada_no_modulo_de_producao():
    """FR-018/SC-004: a régua é o comando real, num processo com o módulo de produção.

    Recarregar o módulo em memória não exercita os checks do Django; só o comando exercita.
    """
    import subprocess
    import sys

    resultado = subprocess.run(
        [sys.executable, "manage.py", "check", "--deploy"],
        cwd=pathlib.Path(__file__).resolve().parents[1],
        env={
            **os.environ,
            **AMBIENTE_MINIMO,
            "DJANGO_SETTINGS_MODULE": "config.settings.production",
        },
        capture_output=True,
        text=True,
    )
    assert resultado.returncode == 0, resultado.stderr
    assert "no issues" in resultado.stdout + resultado.stderr
