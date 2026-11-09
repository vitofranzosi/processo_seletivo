"""As barreiras que decidem se o gerador pode escrever neste banco (134, FR-4601 a FR-4605).

**Três, independentes, e nenhuma é o `DEBUG`.** A homologação do Cefor roda com as configurações
de desenvolvimento, e por isso "não é produção" não basta para autorizar: é preciso que alguém
tenha ligado a chave deste ambiente **e** digitado o nome do banco que vai receber os cenários. O
nome por extenso é o que impede o comando certo de rodar no terminal errado.
"""

import os

from django.conf import settings
from django.core.management.base import CommandError
from django.db import connection

CHAVE = "CENARIOS_DE_TREINAMENTO"


def banco_conectado():
    return str(connection.settings_dict.get("NAME") or "")


def descrever():
    """O destino, em palavras, para a pré-visualização e para o cabeçalho de toda escrita."""
    return {
        "banco": banco_conectado(),
        "servidor": str(connection.settings_dict.get("HOST") or "local"),
        "motor": connection.vendor,
        "configuracao": os.environ.get("DJANGO_SETTINGS_MODULE", ""),
        "chave": bool(getattr(settings, CHAVE, False)),
    }


def recusa(*, banco_informado=None, escrita=True):
    """O motivo de recusa, ou `None` quando o ambiente autoriza.

    A leitura — listar, verificar, pré-visualizar — exige só as duas primeiras barreiras: ela não
    muda nada, e é justamente o que se roda antes de decidir.
    """
    if getattr(settings, "AMBIENTE_DE_PRODUCAO", False):
        return "este é um ambiente de produção: cenários de treinamento nunca rodam aqui."
    if "production" in os.environ.get("DJANGO_SETTINGS_MODULE", ""):
        return (
            "DJANGO_SETTINGS_MODULE aponta para as configurações de produção: cenários de "
            "treinamento nunca rodam com elas."
        )
    if not getattr(settings, CHAVE, False):
        return (
            f"a chave {CHAVE} não está ligada neste ambiente. Ela é desligada por padrão; ligue-a "
            "só no ambiente de homologação ou num banco descartável."
        )
    if not escrita:
        return None
    if not banco_informado:
        return (
            "informe o banco de destino por extenso, com --banco "
            f"{banco_conectado() or '<nome>'}, para confirmar onde os cenários serão gravados."
        )
    if banco_informado != banco_conectado():
        return (
            f"o banco informado ({banco_informado}) não é o banco conectado "
            f"({banco_conectado()}). Nada foi gravado."
        )
    return None


def exigir(*, banco_informado=None, escrita=True):
    motivo = recusa(banco_informado=banco_informado, escrita=escrita)
    if motivo:
        raise CommandError(f"Recusado: {motivo}")
