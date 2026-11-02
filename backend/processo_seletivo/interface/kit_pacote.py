"""O PNG da peça: a única camada que pede algo de fora do projeto (111, D-007).

**O rasterizador é o `resvg-py`**, dependência de execução desde a P-4 (aprovada em 01/11), com a
verificação em `specs/111-kit-de-divulgacao/verificacao-do-motor.md`. `disponivel()` sobra como
defesa: num ambiente montado sem ele, a tela diz que a peça não tem PNG, e o SVG e os textos
continuam.

**As fontes são as do Edital, e só elas.** `skip_system_fonts=True` impede que o resvg
complete um glifo com a fonte da máquina — uma no Mac da equipe, outra no servidor —, e o PNG
mudaria de um para o outro. Nenhum recurso externo é resolvido: a marca vai no SVG, em `data:`.
"""

import importlib.metadata
import importlib.util

from processo_seletivo.publicacoes.infrastructure import fonte

FONTES = tuple(str(fonte.PASTA / arquivo) for arquivo in fonte.ARQUIVOS.values())


def disponivel():
    return importlib.util.find_spec("resvg_py") is not None


def versao_do_rasterizador():
    try:
        return f"resvg-py {importlib.metadata.version('resvg-py')}"
    except importlib.metadata.PackageNotFoundError:
        return ""


def rasterizar(svg):
    """Os bytes do PNG. O SVG é sempre o que o compositor gerou, nunca entrada de quem pede."""
    import resvg_py

    return bytes(
        resvg_py.svg_to_bytes(svg_string=svg, font_files=list(FONTES), skip_system_fonts=True)
    )
