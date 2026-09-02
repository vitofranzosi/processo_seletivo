"""O código de acesso: como nasce, como é guardado e como é conferido.

**Nasce de fonte criptograficamente segura** (FR-023). Seis dígitos só valem um milhão de
tentativas contra quem adivinha às cegas se forem mesmo um milhão: gerador previsível encolhe o
espaço sem que nada mude na tela.

**É guardado por resumo salgado da própria plataforma** (D-003). A alternativa — HMAC com a
`SECRET_KEY` — seria mais barata e amarraria os desafios vivos à rotação da chave, reintroduzindo
em escala menor a dependência que esta feature existe para encerrar. O custo do resumo é pago no
máximo cinco vezes por desafio, e some no percurso.

**A conferência é de tempo constante**, herdada do verificador de senha: comparar textos por
igualdade vaza, pela duração, quantos dígitos iniciais estavam certos.
"""

import secrets

from django.contrib.auth.hashers import check_password, make_password

DIGITOS = 6
INTERVALO = 10**DIGITOS


def gerar() -> str:
    """Um valor uniforme sobre todo o intervalo, com os zeros à esquerda preservados.

    `secrets.randbelow` e não `random`: o segundo é reprodutível a partir do estado, e estado de
    gerador reprodutível é o tipo de coisa que ninguém percebe faltando.
    """
    return f"{secrets.randbelow(INTERVALO):0{DIGITOS}d}"


def resumir(codigo: str) -> str:
    return make_password(codigo)


def confere(codigo: str, resumo: str) -> bool:
    return check_password(codigo, resumo)


def formato_aceitavel(valor: str) -> bool:
    """Seis dígitos, depois de tirar o que a colagem costuma trazer junto.

    Espaços e separadores são removidos porque a pessoa cola o código como ele aparece na
    mensagem, e recusá-lo por causa de um espaço seria transformar apresentação em erro (UX-005).
    """
    return len(normalizar(valor)) == DIGITOS and normalizar(valor).isdigit()


def normalizar(valor: str) -> str:
    return "".join(caractere for caractere in valor if caractere.isdigit())
