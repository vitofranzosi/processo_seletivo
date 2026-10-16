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

# O piloto do assistente (071) ligado e **sem serviço**: os casos injetam a porta falsa, e nenhum
# caminho chega à rede sem ela (`R-019`, `FR-1519`).
ASSISTENTE_PILOTO = True
ASSISTENTE_SERVICO = ""

# O painel na página pública (074) **desligado**, e fixado aqui: o `make test-pg` exporta o `.env`,
# e quem liga a chave lá para subir o servidor ligaria o painel em toda página de seleção da suíte.
# Os casos da `074` a ligam por `settings`.
ASSISTENTE_NA_PAGINA_DO_EDITAL = False
