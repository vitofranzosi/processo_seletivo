"""As configurações de desenvolvimento, com os templates, a folha e as rotas do protótipo."""

from pathlib import Path

from config.settings.development import *  # noqa: F403
from config.settings.development import STATICFILES_DIRS, TEMPLATES

AQUI = Path(__file__).resolve().parent

ROOT_URLCONF = "rotas_do_prototipo"
TEMPLATES[0]["DIRS"] = [AQUI / "templates", *TEMPLATES[0]["DIRS"]]
STATICFILES_DIRS = [AQUI / "static", *STATICFILES_DIRS]
