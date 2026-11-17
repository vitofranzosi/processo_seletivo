"""Como o dado pessoal do candidato aparece para quem não é ele.

Uma função, e ela existe para que a decisão de produto tenha **um** lugar: quanto do CPF a equipe
vê numa listagem. Espalhada pelos templates, a mesma pergunta seria respondida de formas diferentes
em cada tela, e ninguém teria decidido nada (FR-073).
"""

from datetime import date

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


# --- Data de nascimento (180) -------------------------------------------------------------------
# A data é **declarada**, como o CPF: o que se confere aqui é que ela é uma data possível, e não
# que é a verdadeira. O teto de idade protege contra erro de digitação ("1898" no lugar de "1998"),
# e não é regra de quem pode se inscrever — essa é do Edital, e por isso não há idade mínima
# (FR-8306).
IDADE_MAXIMA = 120

RECUSA_VAZIA = "Informe sua data de nascimento."
RECUSA_FORMATO = "Informe a data como dia/mês/ano, com o ano completo — por exemplo, 07/03/1998."
RECUSA_INEXISTENTE = "Esta data não existe. Confira o dia e o mês."
RECUSA_FUTURA = "A data de nascimento precisa ser anterior a hoje."
RECUSA_ANTIGA = f"Confira o ano: a data indica mais de {IDADE_MAXIMA} anos."


class DataDeNascimentoRecusada(ValueError):
    """A recusa, com a frase que a pessoa lê. Nunca uma exceção sem frase subindo pela pilha."""


def ler_data_de_nascimento(texto: str, hoje):
    """`dd/mm/aaaa` — ou `aaaa-mm-dd`, que é como alguns navegadores preenchem `bday` — vira `date`.

    O ano tem de vir com quatro dígitos: "01/02/03" pode ser 1903 ou 2003, e adivinhar seria gravar
    uma data que a pessoa não informou. `hoje` vem de quem chama, na data de Brasília: lida em
    UTC, a regra "anterior a hoje" erraria entre 21h e meia-noite.
    """
    valor = (texto or "").strip()
    if not valor:
        raise DataDeNascimentoRecusada(RECUSA_VAZIA)
    if "/" in valor:
        partes = valor.split("/")
        ordem = (2, 1, 0)
    elif "-" in valor:
        partes = valor.split("-")
        ordem = (0, 1, 2)
    else:
        raise DataDeNascimentoRecusada(RECUSA_FORMATO)
    if len(partes) != 3 or not all(parte.isdigit() for parte in partes):
        raise DataDeNascimentoRecusada(RECUSA_FORMATO)
    ano, mes, dia = (partes[indice] for indice in ordem)
    if len(ano) != 4 or not (1 <= len(mes) <= 2) or not (1 <= len(dia) <= 2):
        raise DataDeNascimentoRecusada(RECUSA_FORMATO)
    try:
        lida = date(int(ano), int(mes), int(dia))
    except ValueError as erro:
        raise DataDeNascimentoRecusada(RECUSA_INEXISTENTE) from erro
    if lida >= hoje:
        raise DataDeNascimentoRecusada(RECUSA_FUTURA)
    if _anos_completos(lida, hoje) > IDADE_MAXIMA:
        raise DataDeNascimentoRecusada(RECUSA_ANTIGA)
    return lida


def _anos_completos(nascimento, hoje) -> int:
    aniversario_ainda_nao_chegou = (hoje.month, hoje.day) < (nascimento.month, nascimento.day)
    return hoje.year - nascimento.year - int(aniversario_ainda_nao_chegou)


def formatar_data(valor) -> str:
    """`date` vira `dd/mm/aaaa`; nada vira vazio."""
    return valor.strftime("%d/%m/%Y") if valor else ""
