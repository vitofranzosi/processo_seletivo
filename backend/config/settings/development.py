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
    "uab/post@1#fefb76c4a72b,"
    "uab/story@1#540d91d5260b,"
    "uab/banner@1#0a742699553a"
)
