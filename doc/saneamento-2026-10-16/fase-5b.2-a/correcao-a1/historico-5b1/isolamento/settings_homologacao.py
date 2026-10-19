"""Settings novos, exclusivos do laboratório; nenhum módulo existente é modificado."""

import os

from contrato import exigir_selecao

exigir_selecao()

from config.settings.development import *  # noqa: E402,F403

# Valores fechados prevalecem sobre defaults ou variáveis herdadas.
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = ""
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
ASSISTENTE_PILOTO = False
ASSISTENTE_SERVICO = ""
ASSISTENTE_NA_PAGINA_DO_EDITAL = False
SORTEIO_FONTE_DE_DEMONSTRACAO = True
INTERFACE_SELETOR_IDENTIDADE = True
ARQUIVOS_CANDIDATOS_RAIZ = "/var/lib/processo-seletivo/arquivos"
DATABASES = {"default": {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": "ps_homologacao_f4_20261016",
    "HOST": "banco-homologacao", "PORT": "5432",
    "USER": "ps_f4_runtime", "PASSWORD": os.environ["DB_RUNTIME_PASSWORD"],
}}
