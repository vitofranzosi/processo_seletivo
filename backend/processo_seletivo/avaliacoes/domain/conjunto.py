"""Distribuir exige que o conjunto de inscrições já esteja fechado (E2E-017).

**O que a regra impede.** A distribuição parte das inscrições **submetidas até agora**, e nada a
liga ao prazo: distribuir com o período aberto reparte um conjunto que ainda cresce, e quem se
inscrever em seguida não é alcançado por ato nenhum. A pessoa não some — a participação da Etapa é
todas as submetidas, então ela aparece como participante sem conclusão e fica retida —, mas fica
esperando que alguém repare e volte à tela.

**Por que é invariante, e não aviso.** A alternativa a fechar o conjunto seria distribuição
incremental: cada inscrição nova entrando numa fila de pendência com dono. Isso é capacidade nova,
e ninguém a pediu. Enquanto ela não existir, a única forma de o sistema não produzir candidato sem
avaliador é recusar o ato que o produz — e recusar cedo, dizendo por quê.

**Onde a regra corre.** Nos três pontos, e não só nos dois que a tela usa: a distribuição manual,
a proposta do rodízio e **a confirmação dela**. A proposta recusa para não convidar a presidência
a montar o que será negado; a confirmação recusa porque é ela que grava, e regra que decide
direito precisa correr no caminho que produz o efeito — a assinatura da proposta carrega os pares
inscrição–membro e nada diz sobre o prazo, de modo que uma Retificação que reabra as inscrições
entre ver e confirmar deixaria a proposta válida sobre um conjunto que voltou a crescer.

**A ausência de prazo não é prazo aberto.** Edital sem Evento designado não recebe inscrição por
este sistema, e não há o que esperar: a regra não se aplica, e distribuir é admitido.
"""

from processo_seletivo.inscricoes.domain.periodo import (
    ABERTO,
    FUTURO,
    periodo_de_inscricoes,
)
from processo_seletivo.shared.api.problems import DomainError

# As duas situações em que ainda pode chegar inscrição. `ENCERRADO` e `NAO_DESIGNADO` não podem
# receber mais nada — a primeira porque o prazo passou, a segunda porque nunca houve prazo aqui.
EM_CURSO = frozenset({ABERTO, FUTURO})


def conjunto_fechado(conteudo, agora):
    """O conjunto de inscrições deste Edital ainda pode crescer?"""
    return periodo_de_inscricoes(conteudo, agora).estado not in EM_CURSO


def recusa_por_inscricoes_em_curso(conteudo, agora):
    """A recusa, ou `None` — e ela diz **quando** o conjunto fecha, não só que está aberto.

    Quem distribui está tentando começar o trabalho da comissão. Dizer "não pode" sem dizer até
    quando esperar transformaria a regra em obstáculo sem saída aparente.
    """
    periodo = periodo_de_inscricoes(conteudo, agora)
    if periodo.estado not in EM_CURSO:
        return None
    if periodo.estado == FUTURO:
        detalhe = "O período de inscrições ainda não começou"
    elif periodo.fim is not None:
        detalhe = f"As inscrições ficam abertas até {periodo.fim:%d/%m/%Y às %H:%M}"
    else:
        detalhe = "As inscrições estão abertas e o Edital não declarou término"
    return DomainError(
        "inscricoes_em_curso",
        f"{detalhe}. Distribuir agora deixaria sem avaliador quem se inscrever depois.",
        409,
    )
