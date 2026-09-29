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


__all__ = ["derivada"]
