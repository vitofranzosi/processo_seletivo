"""A pontuação, validada contra o que o Edital **publicou** — e nada além disso.

Três verificações, e a ausência de uma quarta:

1. **a pontuação máxima publicada**, quando declarada. Não declarada é "o Edital não disse", e não
   "sem limite": inventar um teto aqui aplicaria regra que ninguém publicou (P-007, FR-066);
2. **a forma decimal** do conteúdo publicado — `decimal(7,4)`, a mesma de peso e nota mínima;
3. **a não-negatividade**, que é da grandeza.

**A nota mínima não recusa nada.** Nota abaixo do mínimo é registro válido — é justamente o que o
avaliador precisa poder afirmar —, e a consequência dela é da 013. O que ela produz aqui é uma
coisa só: torna o parecer obrigatório, porque é o parecer que responde recurso (FR-033, FR-034).
"""

from decimal import Decimal, InvalidOperation

from processo_seletivo.avaliacoes.domain.previsao import pontuacao_maxima
from processo_seletivo.shared.api.problems import DomainError

# `decimal(7,4)`: no máximo três dígitos inteiros e quatro casas — a mesma forma que a persistência
# materializa para os outros decimais da Etapa.
CASAS = Decimal("0.0001")
TETO_DA_PERSISTENCIA = Decimal("999.9999")


def _recusa(mensagem, codigo="pontuacao_invalida"):
    return DomainError(codigo, mensagem, 422, campo="pontuacao")


def normalizar(bruta):
    """A pontuação na forma canônica, ou recusa nomeando o campo."""
    if bruta is None or bruta == "":
        raise _recusa("Informe a pontuação.")
    try:
        valor = Decimal(str(bruta))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise _recusa("A pontuação precisa ser um número.") from exc
    if valor != valor.quantize(CASAS):
        raise _recusa("A pontuação admite no máximo quatro casas decimais.")
    if valor < 0:
        raise _recusa("A pontuação não pode ser negativa.")
    return valor


def validar(bruta, etapa):
    """A pontuação aceita para esta Etapa, contra a regra que o Edital publicou."""
    valor = normalizar(bruta)
    maxima = pontuacao_maxima(etapa)
    if maxima is not None and valor > maxima:
        raise _recusa(
            f"A pontuação não pode superar {maxima:f}, que é a máxima publicada para esta Etapa."
        )
    if maxima is None and valor > TETO_DA_PERSISTENCIA:
        # O Edital não declarou limite, e este não é um: é o que o campo comporta. A mensagem diz
        # isso, em vez de fingir uma regra normativa que ninguém publicou.
        raise _recusa(
            "O Edital não declara pontuação máxima para esta Etapa, e o valor informado excede o "
            f"que o registro comporta ({TETO_DA_PERSISTENCIA:f})."
        )
    return valor


def exige_parecer(valor, etapa):
    """Se o parecer é obrigatório para esta pontuação nesta Etapa (FR-034).

    Eliminatória com nota abaixo do mínimo: é o caso em que a avaliação elimina alguém, e é
    exatamente contra o parecer que um recurso é respondido. Sem ele, a instituição não teria o
    que dizer.
    """
    if not etapa.get("eliminatory"):
        return False
    minima = etapa.get("minimumScore")
    if minima is None:
        return False
    try:
        return valor < Decimal(str(minima))
    except (InvalidOperation, ValueError, TypeError):
        return False
