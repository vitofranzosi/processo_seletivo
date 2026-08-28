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
    "rest_framework",
    "processo_seletivo.processos",
    "processo_seletivo.editais",
    "processo_seletivo.publicacoes",
    "processo_seletivo.seguranca",
    "processo_seletivo.auditoria",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "processo_seletivo.shared.api.middleware.CorrelationIdMiddleware",
    "django.middleware.common.CommonMiddleware",
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
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "processo_seletivo.seguranca.api.authentication.InstitutionalBearerAuthentication"
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "EXCEPTION_HANDLER": "processo_seletivo.shared.api.problems.problem_exception_handler",
}
