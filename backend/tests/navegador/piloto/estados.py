"""O catálogo dos 63 estados que o piloto fotografa (172, D-004).

Cada estado é uma função que monta o cenário pelas *fixtures* da suíte e devolve uma `Montagem`: o
endereço da tela, o cliente já identificado com o papel do estado e, nos retornos de gesto, o que
clicar para chegar lá. A função recebe o `request` do pytest e pede as *fixtures* por
`request.getfixturevalue`, para que cada estado peça só as suas.

**Um estado por caso.** Dois cenários de ocupação no mesmo banco colidem pelos identificadores fixos
de linha do quadro, e a identidade não repete Perfil: a jornada monta um estado, fotografa as cinco
larguras e o banco do caso some.

A `prova` é o trecho literal que só aparece no estado pedido. A jornada falha sem ele (FR-7718): uma
fixture que mudasse em silêncio produziria a foto do estado errado, e a comparação aprovaria a foto
errada contra ela mesma.
"""

from collections.abc import Callable
from dataclasses import dataclass, field

from django.test import Client

CATALOGO = {}


@dataclass
class Montagem:
    url: str
    cliente: Client
    # Nos retornos (R-NN) e nas recusas das conferências: o que fazer na página aberta em `url` para
    # chegar ao estado. Recebe a página do Playwright.
    gesto: Callable | None = None


@dataclass
class Estado:
    codigo: str
    tela: str
    papel: str
    prova: str
    montar: Callable
    acao_principal: str | None = None
    # A prova pode estar num trecho que o navegador mostra noutra forma (o `&nbsp;`, a quebra);
    # quando for preciso, ela se confere no HTML da resposta, e não no texto visível.
    observacao: str = ""
    extras: dict = field(default_factory=dict)


def estado(codigo, *, tela, papel, prova, acao_principal=None, observacao=""):
    def registrar(funcao):
        assert codigo not in CATALOGO, f"{codigo} repetido no catálogo"
        CATALOGO[codigo] = Estado(
            codigo=codigo,
            tela=tela,
            papel=papel,
            prova=prova,
            montar=funcao,
            acao_principal=acao_principal,
            observacao=observacao,
        )
        return funcao

    return registrar


def carregar():
    """Importa os quatro catálogos, que se registram ao serem lidos."""
    from tests.navegador.piloto import conferencias, confirmacao, lista, ocupacao  # noqa: F401

    return CATALOGO
