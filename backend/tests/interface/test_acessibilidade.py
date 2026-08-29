"""Acessibilidade verificável sem navegador: contraste, marcação nativa e link de salto.

A spec da 002 exige eMAG 3.1 e WCAG 2.1 AA, valendo a mais restritiva. O que um verificador
automatizado encontra em execução — e o que ele não encontra — está em `accessibility.md`;
aqui ficam as regras que dá para prender no repositório.
"""

import re
from pathlib import Path

import pytest

BASE = (
    Path(__file__).resolve().parents[2]
    / "processo_seletivo/interface/templates/interface/base.html"
)
FONTE = BASE.read_text()
MINIMO_AA = 4.5


def tokens():
    """Cada `--nome:#rrggbb` declarado no :root."""
    return dict(re.findall(r"(--[\w-]+):\s*(#[0-9a-fA-F]{3,6})", FONTE))


def luminancia(cor):
    cor = cor.lstrip("#")
    if len(cor) == 3:
        cor = "".join(c * 2 for c in cor)
    canais = []
    for i in (0, 2, 4):
        v = int(cor[i : i + 2], 16) / 255
        canais.append(v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * canais[0] + 0.7152 * canais[1] + 0.0722 * canais[2]


def contraste(frente, fundo):
    a, b = luminancia(frente), luminancia(fundo)
    claro, escuro = max(a, b), min(a, b)
    return (claro + 0.05) / (escuro + 0.05)


# Combinações que as telas realmente produzem. Manter explícito é o ponto: foi conflar dois
# papéis num token só que fez o rótulo da etapa e os links reprovarem.
PARES = [
    ("--verde-texto", "--branco", "links e rótulos sobre cartão"),
    ("--verde-texto", "--fundo", "links sobre o fundo da página"),
    ("--verde-texto", "--verde-claro", "rótulo da etapa atual e .acao no hover"),
    ("--verde-texto", "--vermelho-fundo", "link do Edital pendente dentro da recusa"),
    ("--verde-texto", "--amarelo-fundo", "links dentro de aviso"),
    ("--branco", "--verde", "texto do botão primário"),
    ("--branco", "--verde-escuro", "cabeçalho e botão no hover"),
    ("--branco", "--vermelho", "botão perigoso"),
    ("--verde-escuro", "--verde-claro", "chip de situação publicada"),
    ("--sucesso", "--verde-claro", "etapa concluída no assistente"),
    ("--amarelo", "--amarelo-fundo", "aviso"),
    ("--vermelho", "--vermelho-fundo", "erro e marcador irreversível"),
    ("#333", "--cinza-fundo", "chip de Edital em elaboração"),
    ("--texto-fraco", "--cinza-fundo", "chip encerrado e passo futuro do assistente"),
    ("--texto", "--fundo", "corpo do texto"),
    ("--texto-fraco", "--branco", "texto de apoio"),
    ("--texto-fraco", "--fundo", "texto de apoio sobre a página"),
]


def resolver(valor, declarados):
    """Aceita tanto `--token` quanto a cor literal que a folha usa direto."""
    if valor.startswith("#"):
        return valor
    assert valor in declarados, f"{valor} saiu da paleta"
    return declarados[valor]


@pytest.mark.parametrize(("frente", "fundo", "onde"), PARES)
def test_contraste_atende_wcag_aa(frente, fundo, onde):
    declarados = tokens()
    razao = contraste(resolver(frente, declarados), resolver(fundo, declarados))
    assert razao >= MINIMO_AA, (
        f"{onde}: {frente} sobre {fundo} dá {razao:.2f}:1, abaixo de {MINIMO_AA}:1"
    )


def test_link_de_salto_move_o_foco_e_nao_so_a_rolagem():
    """Sem tabindex, ativar o link rola a página e deixa o foco no BODY — a próxima tabulação
    volta ao cabeçalho, que é justamente o que o link existe para pular (WCAG 2.4.1)."""
    destino = re.search(r'<a class="pular" href="#([\w-]+)"', FONTE)
    assert destino, "o primeiro foco da página precisa ser o link de salto"
    alvo = destino.group(1)
    assert re.search(rf'<main id="{alvo}" tabindex="-1">', FONTE), (
        "o alvo do link de salto precisa poder receber foco"
    )


TELAS_CRITICAS = [
    ("interface:lista", None),
    ("interface:identificar", None),
]
NAO_NATIVOS = re.compile(
    r"<(?!a\b|button\b|input\b|select\b|textarea\b|main\b)[a-z]+[^>]*\s(?:onclick|hx-get|hx-post)=",
    re.IGNORECASE,
)


@pytest.mark.parametrize(
    "template",
    sorted(p.name for p in BASE.parent.glob("*.html")),
)
def test_controles_sao_nativos(template):
    """Enter e Espaço ativam `<button>` e `<a href>` por conta do navegador.

    Um `<div>` com onclick não é alcançável nem acionável por teclado, e nenhum verificador
    automatizado de contraste pega isso — é a marcação que decide.
    """
    corpo = (BASE.parent / template).read_text()

    assert not NAO_NATIVOS.search(corpo), "controle interativo fora de elemento nativo"
    # `<a(?=[\s>])` e não `<a`: sem isso, <article> casa e o teste acusa o que não existe.
    assert not re.search(r"<a(?=[\s>])(?![^>]*\bhref=)[^>]*>", corpo), (
        "âncora sem href não recebe foco"
    )
    assert not re.search(r'tabindex="[1-9]', corpo), (
        "tabindex positivo reordena a navegação e quebra a ordem visual"
    )
