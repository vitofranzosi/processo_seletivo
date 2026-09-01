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
    # A jornada do candidato (009): o domínio em `inscricoes`, o canal do ator externo em
    # `portal`. São dois apps porque são duas coisas — e `portal` não é uma tela a mais de
    # `interface`: a autenticação, a sessão, a base visual e o alvo de dispositivo são outros.
    "processo_seletivo.inscricoes",
    "processo_seletivo.portal",
    # A identidade do candidato (010): domínio próprio, pela mesma linha que separa `inscricoes`
    # de `portal`. Os modelos e a reconciliação com o legado moram aqui; o `portal` continua
    # sendo o canal, e não ganha `models.py` — pôr a identidade lá o transformaria em canal e
    # domínio ao mesmo tempo, que é o que a separação anterior evitou.
    "processo_seletivo.identidade",
    # A organização do trabalho (011): quem integra a comissão do Processo e quem atua em cada
    # Etapa. App próprio porque é autorização operacional sobre Processo e Edital, e não o ciclo
    # de vida normativo deles — as telas continuam em `interface`, que já é o canal dos dois atores.
    "processo_seletivo.comissoes",
]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # `shared/templates` não pertence a app nenhum: guarda o que os dois canais compartilham
        # sem que um dependa do outro — hoje, os tokens visuais. `APP_DIRS` continua encontrando
        # o resto.
        "DIRS": [BASE_DIR / "processo_seletivo" / "shared" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "processo_seletivo.interface.identidade.contexto_identidade",
                "processo_seletivo.portal.identidade.contexto_candidato",
            ]
        },
    }
]
STATIC_URL = "static/"

# Seletor de identidade: substitui a autenticação institucional enquanto ela não existe.
# Nunca deve estar ligado em produção — ver specs/002-frontend-administrativo/plan.md, Decisão 4.
INTERFACE_SELETOR_IDENTIDADE = os.getenv("INTERFACE_SELETOR_IDENTIDADE", "false").lower() == "true"

# Identidade do candidato (009): eixo próprio, e enquanto o provedor institucional não existir,
# um de demonstração. Como o seletor acima, nunca em produção — ver `production.py`.
PORTAL_IDENTIDADE_DEMO = os.getenv("PORTAL_IDENTIDADE_DEMO", "false").lower() == "true"

# O canal de e-mail que a 010 inaugura: até ela, o projeto não enviava mensagem nenhuma. O
# mecanismo vem do ambiente porque desenvolvimento imprime no terminal e produção entrega de
# verdade — e é justamente por isso que `production.py` recusa subir com um mecanismo que não
# entrega: seria imprimir o código de acesso no log e chamar isso de autenticação.
EMAIL_BACKEND = os.getenv(
    "DJANGO_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "")
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"

# Existe um proxy à frente da aplicação? (010) Só com isto ligado o cabeçalho `X-Forwarded-For` é
# lido para distinguir origens no limite de solicitações de código. Ele é escrito pelo cliente:
# confiar nele sem um proxy que o sobrescreva torna o limite por origem contornável com um
# cabeçalho aleatório por requisição. O padrão é não confiar.
PORTAL_ATRAS_DE_PROXY = os.getenv("PORTAL_ATRAS_DE_PROXY", "false").lower() == "true"

# Para onde mandar quem o sistema não consegue mais atender sozinho (010). Duas telas dizem
# "procure o atendimento institucional" — o CPF congelado depois da primeira inscrição enviada, e a
# participação anterior que a pessoa não conseguiu confirmar —, e ambas eram becos sem saída: nem
# e-mail, nem telefone, nem link. São justamente os dois pontos em que ela já está travada.
# Vazio em desenvolvimento; em produção a ausência impede subir.
PORTAL_ATENDIMENTO = os.getenv("PORTAL_ATENDIMENTO", "").strip()

# Documentos do candidato (009). A raiz é privada: fica fora da árvore estática e nunca é servida
# pelo servidor web — todo acesso passa pela aplicação, que confere titularidade ou permissão
# (FR-051). Vazia em desenvolvimento significa "esta máquina não recebe arquivo"; em produção a
# ausência impede subir.
ARQUIVOS_CANDIDATOS_RAIZ = os.getenv("ARQUIVOS_CANDIDATOS_RAIZ", "")
# O limite é da aplicação, e não do documento exigido (FR-046): um Edital não negocia tamanho de
# arquivo. Lê-se daqui para que mudá-lo não seja mexer em código.
ARQUIVOS_CANDIDATOS_LIMITE_BYTES = int(
    os.getenv("ARQUIVOS_CANDIDATOS_LIMITE_BYTES", str(10 * 1024 * 1024))
)

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
