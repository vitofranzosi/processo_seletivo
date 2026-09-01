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


def digitos(valor: str) -> str:
    return "".join(caractere for caractere in valor if caractere.isdigit())


def cpf_valido(valor: str) -> bool:
    """Os dígitos verificadores, e não só a contagem.

    Contar onze dígitos aceitava `11111111111` e qualquer número inventado — e o CPF é o que
    identifica a mesma pessoa entre visitas, decide de quem é a inscrição e alimenta o `subject`
    da auditoria. Um CPF digitado errado produz uma identidade que ninguém consegue reencontrar:
    a pessoa volta, digita certo, e sua inscrição "sumiu".

    Sequências de dígito repetido são recusadas explicitamente: elas passam no cálculo e nunca
    foram atribuídas a ninguém.

    Isto NÃO prova titularidade — só que o número é um CPF possível. Quem confere é o provedor de
    identidade real, que ainda não existe.
    """
    numero = digitos(valor)
    if len(numero) != 11 or numero == numero[0] * 11:
        return False
    for tamanho in (9, 10):
        soma = sum(int(numero[i]) * (tamanho + 1 - i) for i in range(tamanho))
        resto = (soma * 10) % 11
        if (0 if resto == 10 else resto) != int(numero[tamanho]):
            return False
    return True


def formatar_cpf(valor: str) -> str:
    """`12345678909` vira `123.456.789-09`.

    Uma forma só no banco: o CPF entra como a pessoa digitou — com pontos, sem pontos, com
    espaços — e sai daqui sempre igual. Sem isso, a mesma pessoa aparece de três jeitos nas telas
    de quem confere, e comparar dois registros vira trabalho manual.
    """
    numero = digitos(valor)
    if len(numero) != 11:
        return valor
    return f"{numero[:3]}.{numero[3:6]}.{numero[6:9]}-{numero[9:]}"


def telefone_valido(valor: str) -> bool:
    """Vazio ou um telefone brasileiro com DDD — dez dígitos, ou onze quando é celular."""
    numero = digitos(valor)
    if not valor.strip():
        return True
    return len(numero) in (10, 11)


def formatar_telefone(valor: str) -> str:
    """`27999990000` vira `(27) 99999-0000`; `2733334444` vira `(27) 3333-4444`."""
    numero = digitos(valor)
    if len(numero) == 11:
        return f"({numero[:2]}) {numero[2:7]}-{numero[7:]}"
    if len(numero) == 10:
        return f"({numero[:2]}) {numero[2:6]}-{numero[6:]}"
    return valor
