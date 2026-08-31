"""Onde os documentos do candidato ficam — fora da árvore do código, e nunca servidos direto.

O projeto não tinha armazenamento de arquivo. A coluna binária de `DocumentoPublicado` foi
considerada e recusada: lá é um documento por publicação, imutável e pequeno; aqui são até dez
megabytes por requisito, por candidato, substituíveis durante o rascunho e lidos em streaming.

`base_url=None` é deliberado: pedir a URL de um arquivo destes levanta erro em vez de devolver um
endereço. Não há endereço — todo acesso passa pela aplicação, que confere titularidade ou
permissão antes de entregar um byte (FR-051).

**A raiz é resolvida a cada uso, e não na definição do campo.** Django chama um `storage` que seja
função no momento em que a classe é construída, isto é, no import — e um armazenamento que lê a
configuração no import é um armazenamento que ignora `override_settings` no teste e obriga a
declarar a raiz para rodar `manage.py check`. Resolver por propriedade custa uma consulta a
`settings` por operação e devolve as duas coisas.
"""

import os
import uuid

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class ArmazenamentoPrivado(FileSystemStorage):
    def __init__(self):
        super().__init__(base_url=None)

    def _raiz(self):
        raiz = getattr(settings, "ARQUIVOS_CANDIDATOS_RAIZ", "")
        if not raiz:
            raise ImproperlyConfigured(
                "ARQUIVOS_CANDIDATOS_RAIZ: sem raiz declarada, o sistema não recebe documentos de "
                "candidato. Declare um diretório absoluto, fora da árvore do código."
            )
        return str(raiz)

    # As duas são `cached_property` na classe base, e é justamente o cache que não serve aqui.
    @property
    def base_location(self):
        return self._raiz()

    @property
    def location(self):
        return os.path.abspath(self.base_location)

    def url(self, name):
        """Não há endereço, e pedir um levanta erro em vez de devolver caminho.

        `base_url=None` sozinho não bastava: a classe base cai em `MEDIA_URL`, que é vazio por
        padrão, e devolvia o próprio caminho do arquivo como se fosse endereço. Recusar aqui é o
        que garante que nenhum template consiga, por engano, publicar o caminho de um documento
        de candidato (FR-051).
        """
        raise ValueError(
            "Documento de candidato não tem endereço público. O acesso passa pela aplicação, "
            "que confere titularidade ou permissão antes de entregar."
        )


def caminho_do_documento(instancia, nome_enviado):
    """O nome físico, que **não** é o nome enviado (FR-052).

    O nome do candidato vira metadado exibível e não toca o disco: nome de arquivo carrega dado
    pessoal com frequência — "cpf-maria.pdf" — e viaja em log, em backup e em listagem de
    diretório. O componente aleatório é defesa em profundidade: nada serve este diretório, e ainda
    assim adivinhar o caminho não deve ser possível.
    """
    return f"inscricoes/{instancia.inscricao_id}/{uuid.uuid4().hex}.pdf"
