"""Nenhuma superfície da `019` afirma contagem de ocupação, recebimento, nem direito à vaga.

Três proibições, e cada uma existe porque a frase é fácil de escrever sem perceber:

- **`UX-035` e `SC-092`** — esta feature não conta vaga. Quem responde *"quantas estão ocupadas"* é
  a `016`, e a resposta precisa continuar sendo uma só. Uma tela que dissesse "3 ocupadas" por conta
  própria criaria a segunda, e a `Q-1` recusou isso por escrito.
- **`UX-039` e `FR-288a`** — o sistema registra que **enviou**, e não que chegou. A distância entre
  os dois é real, e é ela que o Edital resolve dando prazo em dias úteis a partir do recebimento.
  O campo que não existe é metade da garantia; esta varredura é a outra, porque prosa mente sem
  precisar de coluna.
- **`FR-292c`** — convocar chama para cumprir uma etapa, e não entrega a vaga. Prometê-la cria
  expectativa que o Edital não sustenta, e o desmentido vem quando já não tem conserto.

É o irmão simétrico de `test_vocabulario_da_ocupacao.py`: lá a `016` não pode falar de convocação;
aqui a `019` não pode falar de contagem. **A fronteira vale nos dois sentidos**, e uma varredura só
guardaria metade dela.

**Comentário não é afirmação.** Explicar por que uma palavra está proibida exige escrevê-la, e por
isso a varredura lê o texto **sem** comentário e sem docstring — o mesmo critério do precedente.

**A proibição estrutural não mora aqui.** Varredura de texto prova que a tela não *diz* que contou;
não prova que nenhum caminho *conta*. Isso é prova de import, e está em
`test_dependencia_da_convocacao.py`.
"""

import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1] / "processo_seletivo"
TEMPLATES = RAIZ / "interface/templates/interface"
PORTAL = RAIZ / "portal/templates/portal"

# As telas da feature e os módulos que produzem o que elas e as mensagens dizem.
DA_019 = [
    TEMPLATES / "convocacao.html",
    TEMPLATES / "convocacao_historico.html",
    PORTAL / "convocacao.html",
    RAIZ / "convocacao/application/convocar.py",
    RAIZ / "convocacao/application/desfechar.py",
    RAIZ / "convocacao/application/comunicar.py",
    RAIZ / "convocacao/application/atestar.py",
    RAIZ / "convocacao/application/selectors.py",
    RAIZ / "convocacao/domain/fila.py",
    RAIZ / "convocacao/domain/prazo.py",
]

# Cada termo com o que ele afirmaria indevidamente. A mensagem entra na falha, para que quem a
# receba entenda a fronteira em vez de só remover a palavra.
PROIBIDOS = {
    r"recebid[oa] em": "o sistema registra que enviou, e não que chegou (UX-039)",
    r"lid[oa] em": "idem — e 'lido' é ainda mais forte que 'recebido'",
    r"entregue em": "idem — entrega é fato do serviço de correio, não deste sistema",
    r"confirmado o recebimento": "o sistema não observa recebimento nenhum",
    r"direito [àa] vaga": "convocar chama para cumprir uma etapa; a vaga é do que vier depois "
    "(FR-292c)",
    r"vaga garantida": "idem — e esta é a formulação que mais promete",
    r"vagas ocupadas s[ãa]o": "contar ocupação é da 016; esta feature lê o número dela (UX-035)",
    r"esta feature conta": "idem — a pergunta tem uma resposta só",
}

# **O padrão de docstring não pode atravessar código**, e é a diferença desta varredura para a da
# `016`: `""".*?"""` com `re.S` casa do fim de uma docstring até o início da seguinte, engolindo
# tudo o que estiver entre as duas — inclusive strings que a tela exibe. A classe negada abaixo
# impede que o casamento atravesse outra aspa tripla.
SEM_COMENTARIO = re.compile(
    r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}"
    r"|^[ \t]*#.*$"
    r"|\"\"\"(?:(?!\"\"\").)*\"\"\"",
    re.S | re.M,
)


def visivel(caminho):
    """O arquivo sem comentário e sem docstring: o que ele de fato afirma a quem o lê na tela."""
    return SEM_COMENTARIO.sub(" ", caminho.read_text())


@pytest.mark.parametrize("caminho", DA_019, ids=lambda item: item.name)
def test_nenhuma_superficie_da_019_afirma_o_que_ela_nao_conhece(caminho):
    corpo = visivel(caminho).lower()
    achados = [
        f"{termo!r} — {porque}" for termo, porque in PROIBIDOS.items() if re.search(termo, corpo)
    ]
    assert achados == [], f"{caminho.name}: " + "; ".join(achados)


def test_a_tela_da_019_nao_calcula_o_numero_que_exibe():
    """`SC-092`: os quatro números vêm da `016`, e a tela não faz aritmética sobre eles.

    **Somar ou subtrair aqui seria a segunda resposta nascendo.** A tela lê `leitura.ocupacao`, que
    é o que a apuração gravou; qualquer `add`, `sub` ou contagem própria sobre essas quantidades
    produziria um número que ato nenhum sustenta.
    """
    corpo = visivel(TEMPLATES / "convocacao.html")

    for filtro in ("|add:", "|sub:", "|divisibleby", "widthratio"):
        assert filtro not in corpo, f"{filtro} sobre número de ocupação faria a 019 contar vaga"


def test_a_019_nomeia_o_envio_positivamente():
    """A ausência das palavras proibidas não basta: a frase certa precisa estar lá.

    Uma tela vazia passaria na varredura acima — e não diria à pessoa de onde o prazo dela corre.
    """
    gestao = visivel(TEMPLATES / "convocacao.html").lower()
    portal = visivel(PORTAL / "convocacao.html").lower()

    assert "enviada em" in gestao
    assert "enviada em" in portal
    assert "contado do envio" in gestao or "contado do envio" in portal


# --- A acentuação do que a tela diz -------------------------------------------------------------
# **Por que existe.** A convenção deste repositório de escrever comentário de template sem acento
# vaza para o texto visível, onde não vale — foi o que a `016` encontrou no percurso conduzido, com
# um teste que afirmava a mesma grafia errada e prendia o defeito em vez de acusá-lo.
TEMPLATES_DA_019 = [caminho for caminho in DA_019 if caminho.suffix == ".html"]

SEM_MARCACAO = re.compile(r"\{\{.*?\}\}|\{%.*?%\}|<[^>]*>", re.S)

# A forma sem acento de cada palavra que o texto desta feature usa. Nenhuma delas é palavra
# portuguesa por si: encontrá-la no texto visível é sempre erro de digitação.
SEM_ACENTO = (
    "convocacao",
    "comunicacao",
    "apuracao",
    "ocupacao",
    "sucessao",
    "reclassificacao",
    "regularizacao",
    "inercia",
    "atestado de fato externo nao",
    "numero",
    "historico",
    "irreversivel",
    "voce",
    "matricula",
)


def texto_visivel(caminho):
    """Só os nós de texto: sem comentário, sem tag e sem expressão de template."""
    return SEM_MARCACAO.sub(" ", SEM_COMENTARIO.sub(" ", caminho.read_text())).lower()


@pytest.mark.parametrize("caminho", TEMPLATES_DA_019, ids=lambda item: item.name)
def test_o_texto_visivel_da_019_sai_acentuado(caminho):
    corpo = texto_visivel(caminho)
    achados = [termo for termo in SEM_ACENTO if termo in corpo]

    assert achados == [], f"{caminho.name}: grafia sem acento no texto visível — {achados}"
