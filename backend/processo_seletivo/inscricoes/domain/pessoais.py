"""Como o dado pessoal do candidato aparece para quem não é ele.

Uma função, e ela existe para que a decisão de produto tenha **um** lugar: quanto do CPF a equipe
vê numa listagem. Espalhada pelos templates, a mesma pergunta seria respondida de formas diferentes
em cada tela, e ninguém teria decidido nada (FR-073).
"""

MASCARA = "***.{}.{}-**"


def mascarar_cpf(cpf: str) -> str:
    """`123.456.789-09` vira `***.456.789-**`.

    Visíveis os seis dígitos do meio, ocultos os três primeiros e os dois verificadores: o
    bastante para conferir identidade contra um documento em mãos, e não o bastante para reusar o
    número em outro lugar.

    O que não é CPF passa mascarado por inteiro — receber lixo aqui é defeito de outro lugar, e
    exibi-lo seria transformar o defeito em vazamento.
    """
    digitos = "".join(caractere for caractere in cpf if caractere.isdigit())
    if len(digitos) != 11:
        return "***.***.***-**"
    return MASCARA.format(digitos[3:6], digitos[6:9])
