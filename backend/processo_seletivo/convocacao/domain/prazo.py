"""O prazo da convocação: vencimento informado, envio, e o decurso que não decide nada (019).

**O sistema não calcula dias úteis e não mantém calendário** (`R-004`, `D-011`). Os Editais contam
em dias úteis a partir do recebimento — 77, 58 e 59, item 8.3 —, e sem calendário de expediente
calcular "2 dias úteis" seria inventar feriado. Errar por um dia num prazo que decide vaga é o tipo
de defeito que não tem conserto: quem perdeu a vaga já perdeu.

O que fica verificável sem calendário nenhum é o que este módulo faz:

- o prazo **não corre sem envio** (`FR-269a`) — o relógio parte de `enviado_em`, e não do ato;
- o vencimento **não precede o envio** (`FR-269b`) — prazo vencido ao nascer não é prazo;
- o decurso **não produz desfecho** (`FR-274`) — vencido é um estado de leitura, e quem desfecha é
  uma pessoa.

**Nenhuma função aqui pergunta se a mensagem chegou.** O sistema registra que enviou (`FR-288a`), e
o vocabulário desta feature não tem *"recebido em"* (`UX-039`). A distância entre o envio e o
recebimento é real, e é ela que o Edital resolve dando prazo em dias úteis — não o sistema.
"""

from processo_seletivo.convocacao.domain import nomes


def vencimento_precede_o_envio(*, vencimento, enviado_em):
    """O vencimento informado é anterior ou igual ao envio (`FR-269b`).

    **Igual também é recusado.** Um prazo que vence no mesmo instante em que a mensagem parte não é
    prazo curto: é prazo nenhum, e produziria desfecho de não atendimento contra alguém que nunca
    teve como atender.

    Sem vencimento informado não há o que conferir: o Edital que não publicou prazo não ganha um
    aqui.
    """
    if vencimento is None or enviado_em is None:
        return False
    return vencimento <= enviado_em


def prazo_corre(*, enviado_em):
    """O relógio partiu (`FR-269a`).

    **É o envio que o inicia, e não o ato de convocar.** Sem esta separação, falha de infraestrutura
    fica indistinguível de silêncio da pessoa — e o desfecho que decorre disso é perda de vaga
    (`R-009`).
    """
    return enviado_em is not None


def decorrido(*, vencimento, enviado_em, agora):
    """O vencimento informado já passou, **e o prazo chegou a correr**.

    Vencimento com envio pendente devolve `False`: um prazo que nunca começou não pode ter vencido,
    por mais antiga que seja a data informada.
    """
    if not prazo_corre(enviado_em=enviado_em) or vencimento is None or agora is None:
        return False
    return agora > vencimento


def estado(*, tem_desfecho, enviado_em, vencimento, agora):
    """Em qual dos quatro estados a convocação está, para a leitura (`R-009`).

    **Derivado, e não coluna**, pela mesma razão que a `016` calcula obsolescência em vez de
    guardá-la: coluna exigiria `UPDATE` em tabela append-only, e o relógio andaria dentro de um ato
    imutável.

    **`CONVOCADO_VENCIMENTO_DECORRIDO` é estado de leitura, e nunca desfecho** (`FR-274`). A tela o
    mostra para que quem conduz o certame saiba onde agir; nenhum desfecho nasce daqui, porque
    nenhum relógio tem competência para tirar vaga de ninguém.
    """
    if tem_desfecho:
        return nomes.DESFECHADO
    if not prazo_corre(enviado_em=enviado_em):
        return nomes.CONVOCADO_PRAZO_NAO_INICIADO
    if decorrido(vencimento=vencimento, enviado_em=enviado_em, agora=agora):
        return nomes.CONVOCADO_VENCIMENTO_DECORRIDO
    return nomes.CONVOCADO_PRAZO_EM_CURSO


__all__ = ["decorrido", "estado", "prazo_corre", "vencimento_precede_o_envio"]
