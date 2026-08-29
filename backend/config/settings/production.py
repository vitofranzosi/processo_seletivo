"""Configuração de produção que se recusa a subir insegura (FR-016 a FR-018 da 003).

A segurança de um sistema que publica atos normativos não pode depender de alguém lembrar de
exportar uma variável. Este módulo transforma cada pressuposto em precondição de inicialização:
falta de segredo, hosts abertos, HTTPS desligado, banco sem senha, seletor de identidade ligado
ou adaptador provisório de autenticação impedem o processo de iniciar, com mensagem que nomeia
a variável a corrigir.

O adaptador `InstitutionalBearerAuthentication` aceita `subject|escopo|permissões` sem assinatura:
qualquer cliente declara a própria identidade e as próprias permissões. Enquanto a integração com
o diretório institucional não existir, esta barreira é o que impede implantar sem fronteira de
segurança alguma.
"""

import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .base import DATABASES, INTERFACE_SELETOR_IDENTIDADE, REST_FRAMEWORK, SECRET_KEY

ADAPTADOR_PROVISORIO = (
    "processo_seletivo.seguranca.api.authentication.InstitutionalBearerAuthentication"
)
SEGREDOS_INADMISSIVEIS = frozenset({"", "unsafe-development-key", "change-me"})

DEBUG = False


def _exigir(condicao, variavel, motivo):
    if not condicao:
        raise ImproperlyConfigured(f"{variavel}: {motivo}")


def _booleano(nome, padrao="true"):
    return os.getenv(nome, padrao).lower() == "true"


# Os mesmos limites que `check --deploy` fiscaliza (security.W009), aplicados antes de subir:
# descobrir a chave fraca por aviso de comando é descobrir tarde demais.
_exigir(
    SECRET_KEY not in SEGREDOS_INADMISSIVEIS
    and len(SECRET_KEY) >= 50
    and len(set(SECRET_KEY)) >= 5
    and not SECRET_KEY.startswith("django-insecure-"),
    "DJANGO_SECRET_KEY",
    "é obrigatória em produção, com ao menos 50 caracteres e 5 caracteres distintos, e não pode "
    "ser o valor de desenvolvimento nem uma chave gerada com o prefixo 'django-insecure-'.",
)

ALLOWED_HOSTS = [v.strip() for v in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if v.strip()]
_exigir(
    ALLOWED_HOSTS and "*" not in ALLOWED_HOSTS,
    "DJANGO_ALLOWED_HOSTS",
    "deve listar explicitamente os hosts institucionais; vazio ou '*' não é admissível.",
)

_exigir(
    not INTERFACE_SELETOR_IDENTIDADE,
    "INTERFACE_SELETOR_IDENTIDADE",
    "o seletor de identidade permite escolher quem se é e não pode existir em produção.",
)

# A autenticação institucional é incremento próprio; até lá, produção não sobe.
API_AUTHENTICATION_CLASSES = [
    v.strip() for v in os.getenv("API_AUTHENTICATION_CLASSES", "").split(",") if v.strip()
]
_exigir(
    API_AUTHENTICATION_CLASSES and ADAPTADOR_PROVISORIO not in API_AUTHENTICATION_CLASSES,
    "API_AUTHENTICATION_CLASSES",
    "deve apontar para a autenticação institucional; o adaptador de desenvolvimento aceita "
    "identidade e permissões declaradas pelo próprio cliente.",
)
REST_FRAMEWORK = {**REST_FRAMEWORK, "DEFAULT_AUTHENTICATION_CLASSES": API_AUTHENTICATION_CLASSES}

_exigir(
    DATABASES["default"]["PASSWORD"],
    "DB_RUNTIME_PASSWORD",
    "o usuário de runtime do banco precisa de senha em produção.",
)

# Transporte: o SecurityMiddleware já está na cadeia; aqui só se liga o que ele fiscaliza.
SECURE_SSL_REDIRECT = _booleano("DJANGO_SECURE_SSL_REDIRECT")
SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = _booleano("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS")
SECURE_HSTS_PRELOAD = _booleano("DJANGO_SECURE_HSTS_PRELOAD")
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
X_FRAME_OPTIONS = "DENY"

_exigir(
    SECURE_SSL_REDIRECT and SECURE_HSTS_SECONDS >= 31536000,
    "DJANGO_SECURE_SSL_REDIRECT/DJANGO_SECURE_HSTS_SECONDS",
    "produção exige HTTPS obrigatório e HSTS de ao menos um ano; desligá-los é decisão "
    "explícita de quem opera, não padrão.",
)

# Atrás de proxy institucional, o cabeçalho é a única evidência de que a origem foi HTTPS.
if os.getenv("DJANGO_TRUST_PROXY_SSL_HEADER", "false").lower() == "true":
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
