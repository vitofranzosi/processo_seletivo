"""O que o documento oficial consegue imprimir, e o que se faz com o resto.

O achado e a decisão estão em `doc/achado-documento-troca-caractere-por-interrogacao.md`.

As fontes do PDF são a Helvetica base-14 em `WinAnsiEncoding`, e o repertório delas é o do cp1252:
cobre o português inteiro, e não cobre o que o Word cola junto com ele. O renderizador codificava
com `"replace"`, e todo caractere fora do repertório virava `?` **em silêncio** — o Edital 90/2026
saiu na prévia com uma interrogação no lugar de cada marcador das atribuições, coladas do Word com
`●` e espaço de largura zero. A Constituição (Princípio II) pede que o PDF corresponda exatamente à
versão homologada, e que a divergência entre os dois impeça a publicação.

Por isso há duas respostas, e só duas (decisão do responsável pelo produto, 08/10/2026):

- **O texto é composto em NFC, e a lista fechada abaixo é normalizada**, porque o significado
  sobrevive à troca: marcador de lista continua marcador, caractere invisível continua invisível,
  espaço continua espaço.
- **Todo o resto é recusado na validação**, com o campo e o caractere nomeados. Quem decide como
  reescrever `≥` num ato oficial é quem o assina, e não o renderizador.

A composição vem primeiro, e é a mesma equivalência que `shared/canonical.py` já aplica antes do
resumo: texto colado do macOS chega decomposto — `ç` como `c` seguido da cedilha combinante —, a
cedilha solta não está no cp1252, e "Seleção" saía "Selec?a?o". Para o resumo as duas grafias já
eram o mesmo conteúdo homologado; imprimir a composta é imprimir exatamente o que o resumo
identifica.

A lista é deliberadamente curta. Ficaram de fora, e são recusados: o marcador vazado `◦`, porque
trocá-lo por `•` apagaria a diferença de nível entre uma lista e a lista dentro dela; `≥ ≤ ≠`,
porque `>=` não é como um Edital escreve; setas, `✓`, `№`, primas, emoji e outros alfabetos.

O módulo é de domínio, e não do renderizador, porque as duas pontas precisam da mesma resposta: o
PDF normaliza com ela, e a validação recusa o que ela não resolve. Duas tabelas divergiriam, e a
primeira divergência seria um `?` que a validação deixou passar.
"""

import unicodedata

_MARCADOR = "•"  # U+2022, que o WinAnsi tem

# Ordem por grupo, e cada linha com o nome Unicode: a tabela é lida por quem vai acrescentar a ela,
# e o código do caractere sozinho não diz o que ele é.
NORMALIZACAO = {
    # Marcadores de lista cheios. Os dois da área privada são os que o Word cola: U+F0B7 é o
    # marcador da fonte Symbol, o do primeiro nível; U+F0A7 é o quadrado da Wingdings, o do
    # terceiro. Cheio vira cheio — o vazado `◦` não está aqui, de propósito.
    "\u25cf": _MARCADOR,  # BLACK CIRCLE ●
    "\uf0b7": _MARCADOR,  # marcador da fonte Symbol, área privada
    "\uf0a7": _MARCADOR,  # quadrado da fonte Wingdings, área privada
    "\u25aa": _MARCADOR,  # BLACK SMALL SQUARE ▪
    "\u25a0": _MARCADOR,  # BLACK SQUARE ■
    "\u2023": _MARCADOR,  # TRIANGULAR BULLET ‣
    "\u2043": _MARCADOR,  # HYPHEN BULLET ⁃
    "\u2219": _MARCADOR,  # BULLET OPERATOR ∙
    # Invisíveis: a pessoa não os vê na tela, e o documento também não deve vê-los. O hífen
    # condicional está **dentro** do cp1252, e por isso nunca virou `?` — mas o WinAnsi o desenha
    # como `-` visível no meio da palavra, que é o mesmo defeito por outro caminho.
    "\u200b": "",  # ZERO WIDTH SPACE
    "\u200c": "",  # ZERO WIDTH NON-JOINER
    "\u200d": "",  # ZERO WIDTH JOINER
    "\u2060": "",  # WORD JOINER
    "\ufeff": "",  # ZERO WIDTH NO-BREAK SPACE (BOM)
    "\u00ad": "",  # SOFT HYPHEN
    # Espaços tipográficos: todos são espaço, de larguras diferentes, e o documento justifica.
    **{chr(codigo): " " for codigo in range(0x2000, 0x200B)},  # EN QUAD … HAIR SPACE
    "\u202f": " ",  # NARROW NO-BREAK SPACE
    "\u205f": " ",  # MEDIUM MATHEMATICAL SPACE
    "\u3000": " ",  # IDEOGRAPHIC SPACE
    # Hífens e o sinal de menos: o mesmo traço curto, com outra semântica tipográfica.
    "\u2010": "-",  # HYPHEN
    "\u2011": "-",  # NON-BREAKING HYPHEN
    "\u2212": "-",  # MINUS SIGN
    # Separadores de linha e de parágrafo: o Word e o Pages os usam onde se esperaria `\n`.
    "\u2028": "\n",  # LINE SEPARATOR
    "\u2029": "\n",  # PARAGRAPH SEPARATOR
}

_TABELA = str.maketrans(NORMALIZACAO)

# Tabulação e quebras de linha são controle, mas o refluxo as consome como espaço em branco antes
# de o texto chegar ao papel. Os demais controles não têm glifo no WinAnsi.
_CONTROLES_CONSUMIDOS = frozenset("\t\n\r")


def normalizar(texto: str) -> str:
    """O texto composto em NFC e com a lista fechada aplicada. O que não está nela passa intacto."""
    return unicodedata.normalize("NFC", str(texto)).translate(_TABELA)


def representavel(caractere: str) -> bool:
    """Se o documento desenha este caractere tal como ele é."""
    if unicodedata.category(caractere) == "Cc":
        return caractere in _CONTROLES_CONSUMIDOS
    try:
        caractere.encode("cp1252")
    except UnicodeEncodeError:
        return False
    return True


def sem_grafia(texto) -> list[str]:
    """Os caracteres que, mesmo normalizados, o documento não imprime — na ordem, sem repetir."""
    vistos = []
    for caractere in normalizar(texto or ""):
        if caractere not in vistos and not representavel(caractere):
            vistos.append(caractere)
    return vistos


def codigo(caractere: str) -> str:
    """`U+2265`: o que a pessoa procura no mapa de caracteres para achar o que colou."""
    return f"U+{ord(caractere):04X}"


def descrever(caractere: str) -> str:
    """O caractere como a mensagem o nomeia: o próprio, quando se vê, e sempre o código.

    Um invisível entre aspas seria `«»`, que não diz nada: nesse caso só o código e o nome.
    """
    nome = unicodedata.name(caractere, "")
    visivel = unicodedata.category(caractere)[0] not in "CZ"
    partes = [f"«{caractere}»"] if visivel else []
    partes.append(f"({codigo(caractere)}{', ' + nome if nome and not visivel else ''})")
    return " ".join(partes)
