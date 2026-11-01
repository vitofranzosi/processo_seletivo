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

#: Hosts que só existem na máquina de quem acessa: um endereço montado sobre eles não vale para quem
#: recebe o documento ou a peça. Morava no relatório do Edital (099); o kit de divulgação (111) o lê
#: também, e a regra é da implantação, e não de uma feature.
HOSTS_LOCAIS = frozenset({"localhost", "127.0.0.1", "::1", "[::1]", "testserver"})


def host_local(request):
    host = request.get_host().rsplit(":", 1)[0] if "]" not in request.get_host() else "[::1]"
    return host in HOSTS_LOCAIS or host.endswith(".localhost")


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
