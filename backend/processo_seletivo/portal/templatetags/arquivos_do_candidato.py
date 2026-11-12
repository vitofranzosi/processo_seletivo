"""O limite de tamanho dito na tela é o limite que o servidor aplica.

Estava escrito "10 MB" em dois templates enquanto `ARQUIVOS_CANDIDATOS_LIMITE_BYTES` é
configurável: mudar o limite deixaria a tela mentindo para o candidato, e a recusa citaria um
número que a página não prometeu.
"""

from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def limite_de_arquivo() -> str:
    megabytes = settings.ARQUIVOS_CANDIDATOS_LIMITE_BYTES / (1024 * 1024)
    inteiro = int(megabytes)
    return f"{inteiro} MB" if megabytes == inteiro else f"{megabytes:.1f} MB".replace(".", ",")


@register.simple_tag
def limite_de_arquivo_em_bytes() -> int:
    """O mesmo limite, em bytes, para o envio de vários não mandar o que passa dele (150, R-009)."""
    return settings.ARQUIVOS_CANDIDATOS_LIMITE_BYTES
