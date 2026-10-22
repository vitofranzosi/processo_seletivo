"""A conta da vaga acrescida, pura: o saldo, o que resta de um acréscimo, e a trava (097).

**Nada aqui toca banco**, pela razão de `apuracao.py`: a reprodução de uma apuração antiga tem de
ser testável alimentando a função com o que o ato congelou.
"""

from processo_seletivo.ocupacao.domain import nomes


def saldo(lidos):
    """Acréscimos menos desfazimentos, sobre `(especie, quantidade)` na ordem congelada."""
    total = 0
    for especie, quantidade in lidos:
        if especie == nomes.ACRESCIMO:
            total += int(quantidade)
        elif especie == nomes.DESFAZIMENTO:
            total -= int(quantidade)
    return total


def restante(*, quantidade, desfeitas):
    """O que um acréscimo ainda tem para desfazer: a quantidade dele menos os desfazimentos que o
    citam. Nunca abaixo de zero — a trava do ato é o que impede passar dele (`FR-2462`)."""
    return max(int(quantidade) - sum(int(q) for q in desfeitas), 0)


def recusa_do_desfazimento(*, efetivas, quantidade, chamadas):
    """O código da recusa, ou `None`, quando o desfazimento tiraria a vaga de quem foi chamado.

    **Conta pessoas chamadas, e não ocupantes** (`T-005`). Pela contagem da `016`, o titular ocupa
    vaga desde a emissão da apuração, antes de ser chamado: com 1 vaga acrescida e o 1º habilitado,
    `ocupadas` é 1 no mesmo instante, e uma trava por ocupantes recusaria todo desfazimento. O que
    o desfazimento não pode é deixar sem vaga quem já recebeu a chamada — quem só está na janela de
    titulares sai dela, e ninguém lhe disse nada.
    """
    if int(efetivas) - int(quantidade) < int(chamadas):
        return nomes.DESFAZIMENTO_COM_PESSOAS_CHAMADAS
    return None


__all__ = ["recusa_do_desfazimento", "restante", "saldo"]
