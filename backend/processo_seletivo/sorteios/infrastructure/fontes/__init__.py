"""A porta da fonte externa da semente, e os seus adaptadores (021, R-005).

**A fronteira que este módulo desenha.** A *identidade* da fonte, a ocorrência, a derivação, a
normalização e a regra de substituição são **conteúdo normativo publicado**: vivem no `drawMethod`
do marco, e alterá-las é Retificação. O *acesso* à fonte é implementação — qual biblioteca, qual
tempo limite, quantas tentativas —, e é o que mora aqui, configurado por ambiente.

Confundir as duas coisas seria deixar uma implantação de software mudar o sentido de um Edital já
publicado, que é exatamente o que a FR-014 proíbe.

O adaptador devolve **material bruto**, e nada mais: nem semente normalizada — normalizar é regra do
método (D-016) —, nem juízo sobre o que fazer quando a ocorrência falta. A ausência é um desfecho
declarado, e quem decide o que fazer com ela é a regra publicada.
"""

from dataclasses import dataclass

from django.conf import settings
from django.utils.module_loading import import_string


@dataclass(frozen=True)
class Observacao:
    """O que a fonte devolveu sobre uma ocorrência.

    `indisponivel` não é erro: é desfecho previsto, e é ele que aciona a regra de substituição
    publicada. `evidencia` é o que se observou — o que a fonte respondeu, e quando —, porque
    aplicar a substituição sem registrar o que a motivou seria afirmar indisponibilidade sem lastro
    (FR-015, R-006).

    **`ocorrida_em` é quando o evento externo aconteceu**, e não quando nós o lemos. A distinção é a
    feature inteira: a FR-016 exige que a ocorrência que fixa a semente seja **posterior ao
    congelamento**, e comparar o instante da leitura permitiria congelar a relação já sabendo o
    resultado da extração e só depois registrá-la no sistema. O adaptador que não souber dizer
    quando a ocorrência aconteceu não serve para semear sorteio, e o comando o recusa.
    """

    material_bruto: str = ""
    ocorrida_em: object = None
    indisponivel: bool = False
    evidencia: str = ""


class FonteExterna:
    """A porta. Um método, e ele não decide nada."""

    def observar(self, *, fonte: str, referencia: str) -> Observacao:  # pragma: no cover - contrato
        raise NotImplementedError


def fonte_configurada():
    """O adaptador declarado em `settings`. Trocá-lo é operação, e nunca norma."""
    return import_string(settings.SORTEIO_FONTE_ADAPTADOR)()


__all__ = ["FonteExterna", "Observacao", "fonte_configurada"]
