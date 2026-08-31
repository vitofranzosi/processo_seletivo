"""Respostas que o navegador não deve guardar.

`no-store` é o que separa uma tela com dado pessoal de uma tela institucional. A vitrine pública
é conteúdo de edital e pode ser guardada à vontade; a tela da inscrição, a revisão, o comprovante,
a lista administrativa e o próprio arquivo carregam nome, CPF e documento — e num computador
compartilhado, que num órgão público é a regra, o histórico do navegador entrega tudo isso a quem
sentar depois (FR-075, FR-075a).

**Por que decorador e não middleware.** Middleware global marcaria também a vitrine, que é
justamente o que se quer barato de servir. Marcar no ponto obriga quem escreve a view a responder
se aquela resposta tem dado pessoal — e a resposta fica escrita.
"""

from functools import wraps

SEM_ARMAZENAMENTO = "no-store, no-cache, must-revalidate, private"


def marcar_como_privada(resposta):
    resposta["Cache-Control"] = SEM_ARMAZENAMENTO
    resposta["Pragma"] = "no-cache"
    return resposta


def resposta_privada(view):
    """Marca a resposta da view como não armazenável pelo navegador."""

    @wraps(view)
    def envolvida(*args, **kwargs):
        return marcar_como_privada(view(*args, **kwargs))

    return envolvida
