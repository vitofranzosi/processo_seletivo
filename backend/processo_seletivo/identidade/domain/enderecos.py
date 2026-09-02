"""A forma canônica do endereço de e-mail — a chave que decide se duas credenciais são a mesma.

Conservadora por decisão (D-006). Baixa a caixa e nada mais: **não** remove pontos, **não** corta
sufixo `+alias`, **não** aplica regra de provedor. Essas equivalências valem no Gmail e são falsas
em outros servidores, e fundir dois endereços distintos numa credencial é indistinguível de tomada
de identidade — só que descoberta depois.

*A suposição que isto embute, declarada.* A RFC torna a parte anterior ao `@` sensível a caixa, e
baixá-la é equivalência que o padrão não garante. A aplicação assume a parte local insensível a
caixa porque nenhum provedor em uso prático distingue `Maria@` de `maria@`, e tratá-las como
credenciais distintas multiplicaria identidades por erro de digitação — um problema frequente
trocado por um problema teórico (FR-012).
"""

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

# O limite da coluna, conferido antes de a gravação chegar ao banco — a mesma razão pela qual a
# 009 confere os seus: em SQLite o valor passa truncado, em PostgreSQL estoura na gravação.
LIMITE = 254


def canonizar(valor: str) -> str:
    return valor.strip().lower()


def endereco_aceitavel(valor: str) -> bool:
    """Forma utilizável, e nada além disso.

    Não diz que o endereço existe nem que alguém o controla — quem prova isso é o desafio. Serve
    para recusar o que nem chega a ser endereço, **antes** de qualquer consulta: é o que mantém a
    recusa do formulário incapaz de revelar se alguém existe.
    """
    canonico = canonizar(valor)
    if not canonico or len(canonico) > LIMITE:
        return False
    try:
        validate_email(canonico)
    except ValidationError:
        return False
    return True
