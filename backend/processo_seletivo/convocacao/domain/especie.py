"""A espécie da convocação, pela posição da pessoa — e não pela escolha de quem convoca (050).

**A espécie é consequência, e não decisão** (`D-004` e `D-008` da `050`). Quem ocupa vaga pela
contagem da apuração vigente é chamado *para vaga inicial*: a `016` já o conta como titular antes de
qualquer chamada. Quem não ocupa e é chamado acrescenta alguém à contagem, e só pode sê-lo *para
vaga que vagou*. E quem a faixa alcançou com Resultado indeferido é chamado *para regularizar*.

**Puro, e com os conjuntos já lidos.** A pergunta "quem ocupa" é da `016`, e chega aqui como
conjunto de chaves; reimplementá-la daria duas respostas — que é o que a `UX-035` proíbe.
"""

from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.ocupacao.domain.apuracao import chave_da_inscricao


def derivada(inscricao, *, ocupando, alcancados, regularizaveis):
    """A espécie que a posição determina, ou `None` quando a pessoa não é chamável por nenhuma.

    **A faixa habilitada vem antes da fila dos indeferidos.** As duas são disjuntas pela construção
    da `019` — quem habilitou não está indeferido —, mas a ordem da pergunta fica explícita: ocupar
    vaga é o fato mais forte, e é ele que decide a espécie.

    `None` não é recusa: quem convoca fora da faixa recebe a recusa própria (`fora_da_faixa`), que
    diz o que fazer. Esta função só responde qual seria a espécie.
    """
    alvo = chave_da_inscricao(inscricao)
    if alvo in {chave_da_inscricao(i) for i in ocupando}:
        return nomes.VAGA_INICIAL
    if any(chave_da_inscricao(i) == alvo for i in alcancados):
        return nomes.SUPLENCIA
    if any(chave_da_inscricao(i) == alvo for i in regularizaveis):
        return nomes.PARA_REGULARIZAR
    return None


def especie_da_sucessora(inscricao, *, ocupando, alcancados, regularizaveis, anterior):
    """A espécie que a sucessora levará: a da posição, e, sem ela, a da convocação que corrige.

    **Corrigir não muda a posição da pessoa.** Quem tem chamada em aberto saiu da fila dos
    regularizáveis justamente por ter sido chamado, e a espécie da raiz é a dela. Mas a contagem
    pode ter mudado desde a chamada — o suplente que passou a ocupar é chamado *para vaga
    inicial* —, e a sucessora diz o que vale no instante dela (`D-006` da `120`).

    **Uma regra só para a tela e para o comando** (`R-004` da `120`): a prévia assina a espécie, e a
    confirmação recusa quando a do ato for outra. Escrita duas vezes, ela divergiria na primeira
    mudança, e a assinatura nunca casaria.
    """
    return (
        derivada(inscricao, ocupando=ocupando, alcancados=alcancados, regularizaveis=regularizaveis)
        or anterior.especie
    )


__all__ = ["derivada", "especie_da_sucessora"]
