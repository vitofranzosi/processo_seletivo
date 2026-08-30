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

Sobre o alcance dessa barreira, para que ninguém a leia como mais do que é: ela **recusa o que
sabe ser inseguro** — o módulo de autenticação de desenvolvimento e os esquemas do DRF que não
carregam identidade institucional — e exige que a classe escolhida exista e seja importável. Ela
**não prova** que a classe declarada fale com o diretório do Ifes; nenhuma configuração pode
provar isso. Quem implanta continua respondendo pela escolha; o que o módulo garante é que a
escolha seja explícita, exista, e não seja um dos caminhos conhecidamente inseguros.
"""

import os

from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from .base import *  # noqa: F403
from .base import DATABASES, INTERFACE_SELETOR_IDENTIDADE, REST_FRAMEWORK, SECRET_KEY

# Módulo inteiro, não uma classe: qualquer adaptador de desenvolvimento que nasça ao lado do
# atual herdaria a mesma recusa sem precisar lembrar de atualizar esta lista.
MODULO_DE_DESENVOLVIMENTO = "processo_seletivo.seguranca.api.authentication."
# Esquemas do DRF que autenticam, mas não contra o diretório institucional: senha no cabeçalho,
# sessão do próprio Django e token emitido por esta aplicação não são identidade do Ifes.
ESQUEMAS_NAO_INSTITUCIONAIS = frozenset(
    {
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    }
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
    bool(API_AUTHENTICATION_CLASSES),
    "API_AUTHENTICATION_CLASSES",
    "deve declarar explicitamente a autenticação institucional; sem ela não há fronteira de "
    "segurança e o backend autoriza contra permissões que o próprio cliente declara.",
)
_recusadas = [
    classe
    for classe in API_AUTHENTICATION_CLASSES
    if classe.startswith(MODULO_DE_DESENVOLVIMENTO) or classe in ESQUEMAS_NAO_INSTITUCIONAIS
]
_exigir(
    not _recusadas,
    "API_AUTHENTICATION_CLASSES",
    f"{', '.join(_recusadas)} não autentica contra o diretório institucional. O adaptador de "
    "desenvolvimento aceita identidade e permissões declaradas pelo próprio cliente; os esquemas "
    "do DRF autenticam contra esta aplicação, não contra o Ifes.",
)
for _classe in API_AUTHENTICATION_CLASSES:
    # Nome inexistente falharia só na primeira requisição autenticada, em produção, com 500.
    try:
        import_string(_classe)
    except ImportError as _erro:
        raise ImproperlyConfigured(
            f"API_AUTHENTICATION_CLASSES: {_classe} não pôde ser importada ({_erro})."
        ) from _erro
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
