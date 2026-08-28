import os

from .base import *  # noqa: F403

if os.getenv("TEST_DB_ENGINE") != "postgresql":
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
