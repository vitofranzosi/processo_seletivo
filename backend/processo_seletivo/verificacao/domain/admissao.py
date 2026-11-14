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


FRASE = (
    "O candidato alcançado por esta Etapa pode escolher entre gravar um vídeo curto, na página do "
    "sistema, e a entrevista ao vivo; as duas formas valem igual. O vídeo só confirma a "
    "autodeclaração: quem o vídeo não confirmar fará a entrevista ao vivo, e só ela pode concluir "
    "pela não confirmação."
)


def frase(etapa) -> str:
    """A frase do documento e da Revisão (FR-7106); vazia onde a Etapa não admite o vídeo.

    Vazia, e não "não admite": o acervo inteiro se recompõe byte a byte sem ela.
    """
    return FRASE if admite_video(etapa) else ""
