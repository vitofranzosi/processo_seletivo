import os

from .base import *  # noqa: F403

if os.getenv("TEST_DB_ENGINE") != "postgresql":
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# A suíte sorteia contra a fonte de demonstração, pelo nome publicado, sem rede (046, `R-6`). Os
# casos que exercitam produção a desligam por `override_settings`.
SORTEIO_FONTE_DE_DEMONSTRACAO = True
