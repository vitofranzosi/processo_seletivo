import os

from .base import *  # noqa: F403
from .base import liberacao_do_kit

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

# A peça do kit (111) ligada, e fixada aqui pela razão do painel acima: o `.env` não decide a suíte.
# Os casos da chave desligada a desligam por `settings` (EC-21).
KIT_DE_DIVULGACAO_PECA = True

# Todos os templates do registro, com a versão e o resumo do código (119, `D-010`): a suíte confere
# que esta lista é o registro inteiro, e uma família nova, ou uma versão nova, reprova até entrar
# aqui.
KIT_DE_DIVULGACAO_TEMPLATES = liberacao_do_kit(
    "institucional/post@1#d7ab660ea755,"
    "pos-lato-sensu/post@1#bfcb25490b8e,"
    "pos-lato-sensu/story@2#8a16aef0abbd,"
    "pos-lato-sensu/banner@1#1badbdf0cb93,"
    "fic/post@1#48c8b8c71eb3,"
    "fic/story@1#795eb249d0c1,"
    "fic/banner@1#dedce5f30536,"
    "aperfeicoamento/post@1#973b8dd70eb1,"
    "aperfeicoamento/story@1#089ea18ee6e7,"
    "aperfeicoamento/banner@1#4f26004ae0ba,"
    "libras/post@1#db26f4737c4b,"
    "libras/story@1#6d699167abba,"
    "libras/banner@1#a9ad7cba0bd6,"
    "uab/post@1#34c0c7073af8,"
    "uab/story@1#00f01d3909fd,"
    "uab/banner@1#fca039587c97,"
    "internos/post@1#9818523a0de0,"
    "internos/story@1#c9737cbea0fd,"
    "internos/banner@1#ecf22fd996e9"
)
