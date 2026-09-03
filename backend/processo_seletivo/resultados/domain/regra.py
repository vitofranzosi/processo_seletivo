"""A regra da V1: de uma Avaliação concluída para uma consequência da Etapa.

Função pura. Recebe o dicionário da Etapa **no conteúdo publicado** e um decimal, devolve
consequência e motivo — ou, antes disso, diz que a Etapa não tem regra suficiente. Não consulta
banco, não conhece modelo, e é por isso que a tabela-verdade inteira cabe num teste unitário.

**O que ela não faz.** Não tira média, não soma, não pondera e não arredonda. Consolidar N
avaliações exigiria uma regra de combinação que o Edital não publica, e inventá-la aqui seria
aplicar ao candidato uma norma que ninguém escreveu. A V1 consolida leitura única e **impede** o
resto, dizendo por quê.

`classificatory` não entra: ele descreve o destino da nota na composição entre Etapas — feature
posterior — e não a consequência local. Peso, idem.
"""

from decimal import Decimal, InvalidOperation

from processo_seletivo.avaliacoes.domain.previsao import avaliacoes_previstas

HABILITADA = "HABILITADA"
ELIMINADA = "ELIMINADA"

REGRA_DE_COMBINACAO_AUSENTE = "regra_de_combinacao_ausente"
REGRA_INSUFICIENTE = "regra_insuficiente"


def _decimal_ou_none(valor):
    if valor is None:
        return None
    try:
        return Decimal(str(valor))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _numero(valor):
    """O decimal como o Edital o mostra: quatro casas, vírgula decimal."""
    return f"{valor:.4f}".replace(".", ",")


def nota_minima(etapa):
    """A nota mínima publicada da Etapa, ou `None` quando o Edital não a declarou."""
    if not isinstance(etapa, dict):
        return None
    return _decimal_ou_none(etapa.get("minimumScore"))


def eliminatoria(etapa):
    return bool(isinstance(etapa, dict) and etapa.get("eliminatory"))


def impedimento_da_regra(etapa):
    """`None` quando a Etapa pode ser consolidada; senão `(codigo, frase)`.

    Dois impedimentos, e os dois são da **Etapa inteira** — não de uma inscrição:

    - a Etapa prevê mais de uma avaliação, e o Edital não declara como combiná-las;
    - a Etapa é eliminatória e não publicou nota mínima, de modo que não há como eliminar por
      pontuação. Aceitar "eliminatória sem critério" seria deixar a consequência para quem
      implementa decidir.
    """
    previstas = avaliacoes_previstas(etapa)
    if previstas > 1:
        return (
            REGRA_DE_COMBINACAO_AUSENTE,
            f"o Edital prevê {previstas} avaliações para esta Etapa e não declara como combiná-las",
        )
    if eliminatoria(etapa) and nota_minima(etapa) is None:
        return (
            REGRA_INSUFICIENTE,
            "a Etapa é eliminatória e o Edital não publicou nota mínima",
        )
    return None


def consequencia(etapa, pontuacao):
    """`(consequencia, motivo)` para uma pontuação, sob uma Etapa com regra disponível.

    A comparação é decimal, e nunca de ponto flutuante: nota **exatamente igual** à mínima
    habilita, e é o caso em que o arredondamento binário decidiria a vida de alguém.
    """
    minima = nota_minima(etapa)
    if eliminatoria(etapa) and minima is not None and pontuacao < minima:
        return (
            ELIMINADA,
            f"pontuação inferior à nota mínima da Etapa ({_numero(pontuacao)} < {_numero(minima)})",
        )
    if eliminatoria(etapa) and minima is not None:
        return (
            HABILITADA,
            f"pontuação igual ou superior à nota mínima da Etapa "
            f"({_numero(pontuacao)} ≥ {_numero(minima)})",
        )
    # Etapa sem caráter eliminatório materializa o total e habilita. Uma nota mínima publicada aqui
    # não elimina: sem o caráter, ela não é critério de exclusão, e aplicá-la seria a 013 decidindo
    # o que o Edital não decidiu.
    return (HABILITADA, "a Etapa não tem caráter eliminatório")
