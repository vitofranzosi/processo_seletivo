"""O roteiro da gravação, versionado, e a conferência das marcas (166, FR-7112, FR-7113).

**Um roteiro só nesta entrega**, o de referência do estudo (modelo da UFC): documento, perfil
esquerdo, perfil direito e frente com a fala. O roteiro por unidade é a P-8, aberta. A versão viaja
com o vídeo, para que a comissão leia os passos que o candidato viu, e não os de hoje.

**Não há tempo mínimo nem cronômetro por passo** (R-14): os instantes ajudam a comissão a achar o
trecho, e não servem para julgar ritmo. Há só o teto técnico, declarado antes de começar.
"""

from dataclasses import dataclass

VERSAO = "referencia-2026-11"
TETO_SEGUNDOS = 180


@dataclass(frozen=True)
class Passo:
    chave: str
    titulo: str
    instrucao: str


PASSOS = (
    Passo(
        "documento",
        "Documento",
        "Mostre o seu documento de identidade com foto perto da câmera, e depois o seu rosto.",
    ),
    Passo(
        "perfil-esquerdo",
        "Perfil esquerdo",
        "Vire o rosto devagar para a sua esquerda, até a câmera ver o seu perfil.",
    ),
    Passo(
        "perfil-direito",
        "Perfil direito",
        "Agora vire o rosto devagar para a sua direita.",
    ),
    Passo(
        "frente",
        "De frente",
        "Olhe para a câmera e diga o seu nome e a frase «Eu me autodeclaro pessoa preta» ou «pessoa "
        "parda», como declarou na inscrição. Não diga o seu CPF. Se preferir, mostre a frase escrita "
        "num papel, ou diga em Libras.",
    ),
)

CHAVES = tuple(passo.chave for passo in PASSOS)
TITULOS = {passo.chave: passo.titulo for passo in PASSOS}


class MarcasInvalidas(ValueError):
    pass


def conferir_marcas(marcas, duracao) -> list[dict]:
    """As marcas normalizadas, ou `MarcasInvalidas`.

    Uma por passo, na ordem do roteiro, todas presentes; instantes não decrescentes, a primeira em
    zero e nenhuma além da duração (com um segundo de folga, porque o relógio do aparelho e o do
    contêiner não batem no milissegundo).
    """
    if not isinstance(marcas, list) or len(marcas) != len(PASSOS):
        raise MarcasInvalidas("o vídeo precisa de uma marca por passo do roteiro")
    normalizadas = []
    anterior = 0.0
    for esperado, marca in zip(CHAVES, marcas, strict=True):
        if not isinstance(marca, dict) or marca.get("passo") != esperado:
            raise MarcasInvalidas("as marcas não seguem a ordem do roteiro")
        try:
            instante = round(float(marca.get("instante")), 3)
        except (TypeError, ValueError) as erro:
            raise MarcasInvalidas("o instante de uma marca não é um número") from erro
        if instante < anterior or instante > float(duracao) + 1:
            raise MarcasInvalidas("os instantes das marcas não cabem na duração do vídeo")
        normalizadas.append({"passo": esperado, "instante": instante})
        anterior = instante
    if normalizadas[0]["instante"] > 1:
        raise MarcasInvalidas("o primeiro passo começa com a gravação")
    return normalizadas


def marcas_com_titulo(marcas) -> list[dict]:
    """As marcas com o título do passo, para a Mesa saltar a ele (FR-7132)."""
    return [
        {
            "passo": marca.get("passo"),
            "titulo": TITULOS.get(marca.get("passo"), marca.get("passo")),
            "instante": marca.get("instante"),
        }
        for marca in marcas or []
    ]
