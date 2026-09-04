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

from processo_seletivo.avaliacoes.domain.formas import Sentido
from processo_seletivo.avaliacoes.domain.previsao import pontuacao_maxima
from processo_seletivo.shared.api.problems import DomainError

# `decimal(7,4)`: no máximo três dígitos inteiros e quatro casas — a mesma forma que a persistência
# materializa para os outros decimais da Etapa.
CASAS = Decimal("0.0001")
TETO_DA_PERSISTENCIA = Decimal("999.9999")


def _recusa(mensagem, codigo="pontuacao_invalida"):
    return DomainError(codigo, mensagem, 422, campo="pontuacao")


def normalizar(bruta):
    """A pontuação na **forma** que o registro comporta, ou recusa nomeando o campo.

    Quatro verificações, e as duas primeiras existem porque `Decimal` aceita mais do que um número
    de verdade: `Infinity`, `NaN` e `1E+100` atravessam o construtor e explodem depois — no
    `quantize`, ou no banco. Recusar aqui é o que impede que um valor impossível vire erro
    interno em vez de recusa legível.

    A **máxima publicada** não entra aqui: ela é regra normativa, e é cobrada na conclusão
    (`validar`). Esta função é o que o rascunho exige.
    """
    if bruta is None or bruta == "":
        raise _recusa("Informe a pontuação.")
    try:
        valor = Decimal(str(bruta))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise _recusa("A pontuação precisa ser um número.") from exc
    if not valor.is_finite():
        raise _recusa("A pontuação precisa ser um número.")
    if valor < 0:
        raise _recusa("A pontuação não pode ser negativa.")
    # O teto da **coluna**, e não uma regra normativa: `decimal(7,4)` comporta três dígitos
    # inteiros. Deixar passar produziria erro de banco no lugar de uma recusa que a pessoa lê.
    if valor > TETO_DA_PERSISTENCIA:
        raise _recusa(
            f"A pontuação não pode superar {TETO_DA_PERSISTENCIA:f}, que é o máximo que o "
            "registro comporta."
        )
    try:
        if valor != valor.quantize(CASAS):
            raise _recusa("A pontuação admite no máximo quatro casas decimais.")
    except InvalidOperation as exc:
        raise _recusa("A pontuação precisa ser um número.") from exc
    return valor


def validar(bruta, etapa):
    """A forma **mais** a regra publicada — o que a conclusão exige.

    Salvar sem concluir cobra só `normalizar`: quem está no meio do trabalho pode gravar um valor
    que ainda não decidiu, e cobrar a máxima ali obrigaria a concluir para descobrir se o número
    passa. A regra normativa é cobrada no ato que tem efeito (FR-031, FR-032, FR-033).
    """
    valor = normalizar(bruta)
    maxima = pontuacao_maxima(etapa)
    if maxima is not None and valor > maxima:
        raise _recusa(
            f"A pontuação não pode superar {maxima:f}, que é a máxima publicada para esta Etapa."
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


# ---------------------------------------------------------------- a forma decisória (D-008)


def _recusa_do_sentido(mensagem):
    return DomainError("sentido_invalido", mensagem, 422, campo="sentido")


def normalizar_sentido(bruto, *, exigir):
    """O sentido como o registro o comporta, ou recusa nomeando o campo.

    A assimetria com `normalizar` é a mesma que separa rascunho de conclusão: `exigir=False` aceita
    o vazio, porque quem está no meio do trabalho ainda não decidiu; `exigir=True` é a conclusão, e
    ali a ausência é recusada — como "Informe a pontuação." faz do outro lado (FR-103).
    """
    valor = (bruto or "").strip()
    if not valor:
        if exigir:
            raise _recusa_do_sentido("Informe o sentido da decisão.")
        return ""
    if valor not in Sentido.values:
        # Inclui o caso em que chega o **rótulo publicado** no lugar do enum: a tela mostra
        # "Indeferido" e envia `DESFAVORAVEL`, e aceitar o rótulo faria o domínio guardar o
        # vocabulário de um Edital no lugar do juízo (FR-118).
        raise _recusa_do_sentido("O sentido da decisão precisa ser favorável ou desfavorável.")
    return valor


def exige_parecer_do_sentido(sentido):
    """Desfavorável exige parecer, e **não** depende do caráter da Etapa (FR-123).

    A assimetria com `exige_parecer` é deliberada: na forma pontuada é a nota abaixo do mínimo em
    Etapa eliminatória que torna o parecer obrigatório, porque é ali que a avaliação elimina. Na
    decisória, o desfavorável é sempre o caso em que o candidato mais precisará da fundamentação —
    é contra o parecer que o recurso responderá —, e condicioná-lo ao caráter deixaria sem
    justificativa registrada justamente a Etapa que ainda não declarou o que faz com a decisão.
    """
    return sentido == Sentido.DESFAVORAVEL
