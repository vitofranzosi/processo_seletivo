from .base import *  # noqa: F403
from .base import liberacao_do_kit

DEBUG = True

# Ligada pelo módulo, e não pelo `.env`: é ela que deixa `seed_demo` e o `quickstart` sortearem sem
# rede, e nada carrega o `.env` sozinho (046, `R-6`). Produção nunca carrega este módulo.
SORTEIO_FONTE_DE_DEMONSTRACAO = True

# Os avisos da 066 ligados em desenvolvimento, como o sorteio de demonstração: a demonstração pela
# interface (Princípio VI) precisa deles, e o correio daqui não entrega a ninguém.
AVISOS_AOS_CANDIDATOS = True

# A peça do kit de divulgação (111) ligada, como os avisos: a revisão da comunicação (SC-1054) é
# feita olhando a peça, e é aqui que ela existe antes da aprovação.
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
    "tmd/post@1#9a544f2f3d14,"
    "tmd/story@1#82ecc2986f98,"
    "tmd/banner@1#19a61ab2cb53"
)
