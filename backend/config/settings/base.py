import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-development-key")
DEBUG = False
ALLOWED_HOSTS = [v for v in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost").split(",") if v]
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
USE_TZ = True
TIME_ZONE = "America/Sao_Paulo"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "rest_framework",
    "processo_seletivo.processos",
    "processo_seletivo.editais",
    "processo_seletivo.publicacoes",
    "processo_seletivo.seguranca",
    "processo_seletivo.auditoria",
    "processo_seletivo.interface",
]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "processo_seletivo.interface.identidade.contexto_identidade",
            ]
        },
    }
]
STATIC_URL = "static/"

# Seletor de identidade: substitui a autenticação institucional enquanto ela não existe.
# Nunca deve estar ligado em produção — ver specs/002-frontend-administrativo/plan.md, Decisão 4.
INTERFACE_SELETOR_IDENTIDADE = os.getenv("INTERFACE_SELETOR_IDENTIDADE", "false").lower() == "true"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # A interface administrativa autentica por sessão: sem esta verificação os `{% csrf_token %}`
    # dos formulários não são fiscalizados por ninguém e uma página externa pratica atos
    # irreversíveis em nome de quem estiver com a sessão aberta. As views da API são
    # `csrf_exempt` por construção do DRF e continuam autenticando por cabeçalho.
    "django.middleware.csrf.CsrfViewMiddleware",
    "processo_seletivo.shared.api.middleware.CorrelationIdMiddleware",
    "processo_seletivo.interface.erros.RecusaDoDominioMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
database_role = os.getenv("DB_ROLE", "runtime")
database_user = os.getenv(
    "DB_MIGRATION_USER" if database_role == "migration" else "DB_RUNTIME_USER",
    os.getenv("DB_USER", "processo_seletivo_runtime"),
)
database_password = os.getenv(
    "DB_MIGRATION_PASSWORD" if database_role == "migration" else "DB_RUNTIME_PASSWORD",
    os.getenv("DB_PASSWORD", ""),
)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "processo_seletivo"),
        "USER": database_user,
        "PASSWORD": database_password,
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}
REST_FRAMEWORK = {
    # Só JSON: o contrato declara application/json e a Browsable API do DRF exigiria
    # engine de template e staticfiles, superfície que uma API institucional não precisa.
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_CONTENT_NEGOTIATION_CLASS": (
        "processo_seletivo.shared.api.negotiation.JsonAlwaysNegotiation"
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "processo_seletivo.seguranca.api.authentication.InstitutionalBearerAuthentication"
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "EXCEPTION_HANDLER": "processo_seletivo.shared.api.problems.problem_exception_handler",
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {"()": "processo_seletivo.shared.observability.JsonFormatter"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "json"},
    },
    "loggers": {
        "processo_seletivo": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.request": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}
