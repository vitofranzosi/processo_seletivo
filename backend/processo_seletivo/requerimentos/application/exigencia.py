"""A metade do requerimento que a **submissão da inscrição** alcança — e que não toca `convocacao`.

**Este módulo existe pela sua lista de imports, e não pelo seu tamanho.** `convocacao` importa
`inscricoes`, porque a `Convocacao` aponta a `Inscricao`. Se `inscricoes.submissao` importasse
`preencher.py` — que consulta `chamada_em_aberto` — o ciclo `inscricoes → requerimentos →
convocacao → inscricoes` se fecharia. Uma redação anterior desta feature deixava o predicado lá
dentro e chamava a separação de "política repartida": a repartição estava na *função*, e não no
*módulo*, e um import basta para fechar ciclo — a função chamada não é a unidade que o interpretador
carrega.

A separação real é esta: aqui moram a vigência e a pergunta estreita; em `preencher.py`, que importa
daqui, mora tudo que precisa da convocação. O sentido corre num só lado, e nenhum módulo daqui
importa `inscricoes.submissao` de volta.

**O que este módulo evita, dito com precisão**: `convocacao.application`. Ele **alcança**
`convocacao.models`, porque `RequerimentoDeMatricula` aponta a `Convocacao` numa chave estrangeira —
e isso é inevitável e inofensivo: modelos Django se referenciam entre si por construção, e o grafo
de migrations já registra essa direção. O que a repartição impede é a dependência de **regra**:
`inscricoes` decidir a submissão consultando a fila de chamada, que é a leitura cara e é a que
inverteria o sentido entre as camadas de aplicação.

**A pergunta é estreita porque o instante é estreito.** No momento em que alguém submete uma
inscrição, o ramo da convocação nunca se aplica: não há chamada para quem ainda não se inscreveu.
"""

from processo_seletivo.publicacoes.application import selectors
from processo_seletivo.requerimentos.domain import disponibilidade, nomes
from processo_seletivo.requerimentos.models import RequerimentoDeMatricula


def versao_vigente(inscricao):
    return selectors.selecao_publica(edital_id=inscricao.edital_id)


def _sucedidos():
    """Os requerimentos que já têm sucessor — por **subconsulta**, e não por junção.

    `sucessores__isnull=True` seria a forma óbvia e produz um *outer join*; o PostgreSQL recusa
    `FOR UPDATE` sobre o lado anulável de uma junção externa, e a leitura sob trava quebraria com
    `FeatureNotSupported`. A subconsulta responde a mesma pergunta sem junção nenhuma.
    """
    return RequerimentoDeMatricula.objects.filter(requerimento_anterior__isnull=False).values(
        "requerimento_anterior"
    )


def vigentes(inscricao):
    return (
        RequerimentoDeMatricula.objects.filter(inscricao=inscricao)
        .exclude(pk__in=_sucedidos())
        .order_by("-created_at")
    )


def vigente_de(inscricao):
    """O requerimento que ninguém sucedeu, ou `None`. Vigência é derivada, e não coluna."""
    return vigentes(inscricao).first()


def falta_requerimento(inscricao) -> bool:
    """Esta Inscrição não pode ser submetida porque o requerimento dela ainda não foi enviado?

    **A recusa é do comando, e a tela apenas a antecipa** (Princípio IV). Quem chamar `submeter`
    direto, sem passar por tela nenhuma, encontra aqui a mesma resposta.

    **Vale somente para o momento *na inscrição***: Edital que coleta na convocação submete a
    inscrição normalmente, sem requerimento nenhum — exigi-lo ali inverteria a ordem do certame.
    """
    conteudo = versao_vigente(inscricao).content
    if not disponibilidade.exigido_na_inscricao(conteudo):
        return False
    vigente = vigente_de(inscricao)
    return vigente is None or vigente.status != nomes.ENVIADO


# O nome longo é o que `inscricoes` importa: lá dentro, `falta_requerimento(inscricao)` diria pouco
# no meio de doze conferências de submissão, e o nome tem de dizer **qual** exigência é esta.
inscricao_exige_requerimento_enviado = falta_requerimento
