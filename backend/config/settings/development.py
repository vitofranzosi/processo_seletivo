from .base import *  # noqa: F403

DEBUG = True

# Ligada pelo módulo, e não pelo `.env`: é ela que deixa `seed_demo` e o `quickstart` sortearem sem
# rede, e nada carrega o `.env` sozinho (046, `R-6`). Produção nunca carrega este módulo.
SORTEIO_FONTE_DE_DEMONSTRACAO = True
