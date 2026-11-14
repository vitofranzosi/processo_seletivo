"""A admissão do vídeo pela Etapa, no conteúdo publicado (166, degrau 25, D-001).

Função pura sobre o item de `stages`. O campo é `videoOption`, booleano; o acervo anterior ao degrau
25 se lê `false` — a capacidade não existia, e ler outra coisa daria ao candidato um meio que nenhum
Edital publicou.
"""

CAMPO = "videoOption"


def admite_video(etapa) -> bool:
    """A Etapa publicada admite o vídeo gravado pelo candidato."""
    return bool(isinstance(etapa, dict) and etapa.get(CAMPO) is True)


def publicar(coluna) -> dict:
    """O campo como a publicação o grava: sempre presente, `true` ou `false`."""
    return {CAMPO: bool(coluna)}


def ler(valor) -> bool:
    """O valor que a gravação do rascunho aceita: só `True` admite; `None`, ausência e `False`, não."""
    return valor is True
