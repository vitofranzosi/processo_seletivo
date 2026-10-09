import os

from .base import *  # noqa: F403

if os.getenv("TEST_DB_ENGINE") != "postgresql":
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# A suíte sorteia contra a fonte de demonstração, pelo nome publicado, sem rede (046, `R-6`). Os
# casos que exercitam produção a desligam por `override_settings`.
SORTEIO_FONTE_DE_DEMONSTRACAO = True

# A suíte exercita os avisos da 066 com a chave ligada; os casos da chave desligada a desligam por
# `settings` (`FR-1282`). O correio é o de memória do Django, que `setup_test_environment` impõe.
AVISOS_AOS_CANDIDATOS = True
