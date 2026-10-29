"""A extração declarada ainda pode semear o sorteio? Pergunta feita antes da observação (102).

**O defeito que isto fecha.** O Edital 72/2026 foi publicado com as inscrições terminando em 28/10
às 9h e a extração da Loteria Federal declarada para o mesmo dia, às 20h05. A Caixa publica só a
data, e a data vale a partir de 00h00 (`loteria_federal._nao_antes_de`). Como a relação só se
congela depois do fim das inscrições, nenhum congelamento possível era anterior à extração, e o
sorteio estava condenado desde a publicação. Ninguém foi avisado: a recusa só apareceu no dia,
com o certame em curso.

**Uma regra só, perguntada em quatro lugares** (FR-2650): a publicação, a Retificação, a tela do
sorteio antes de congelar e a tela da relação já congelada. Escrita em cada lugar, ela divergiria na
primeira mudança, e a tela diria "viável" a um Edital que a publicação recusa.

**Pura, e sem saber de onde vem a granularidade.** Se a fonte publica só a data é uma propriedade do
adaptador, que mora na infraestrutura (`fontes.publica_so_a_data`). O domínio não a importa: quem
pergunta resolve e passa o resultado. A recusa no sorteio **não** usa esta regra — ela compara o
limite que a fonte de fato devolveu (FR-2664); esta é a previsão, feita antes de a fonte falar.
"""

from datetime import datetime, time

from django.utils.dateparse import parse_datetime

from processo_seletivo.shared.tempo import ZONA


def limite_previsto(ocorre_em, *, so_a_data):
    """O instante mais cedo em que a fonte vai situar a ocorrência declarada, ou `None`.

    Só existe para fonte que publica só a data: 00h00 do dia de `occurrenceAt`, **tomado no fuso
    institucional**, que é como a Caixa e o adaptador entendem a data dela. Para fonte que publica a
    hora não há previsão a fazer aqui (D-006), e para granularidade desconhecida — fonte fora do
    vocabulário — o achado é outro, e esta regra se cala para não empilhar dois sobre uma causa.

    Texto ilegível ou sem fuso também devolve `None`: quem o acusa é a conferência de forma de
    `occurrenceAt`, e o recuo silencioso aqui é o mesmo que `validation._instante` pratica.
    """
    if so_a_data is not True:
        return None
    lido = parse_datetime(str(ocorre_em or ""))
    if lido is None or lido.utcoffset() is None:
        return None
    return datetime.combine(lido.astimezone(ZONA).date(), time.min, tzinfo=ZONA)


def inviavel(limite, congelamento_mais_cedo):
    """Verdadeiro quando nenhum congelamento possível vem antes do limite previsto.

    **`<=`, e não `<`**, porque é a comparação que a constituição do sorteio faz: um limite igual ao
    congelamento não prova que a semente veio depois do compromisso. Sem um dos dois instantes não
    há o que afirmar, e a resposta é falso — o lado que não acusa, porque acusar sem base prenderia
    Edital que sortearia.
    """
    if limite is None or congelamento_mais_cedo is None:
        return False
    return limite <= congelamento_mais_cedo


def congelamento_mais_cedo(*, agora, fim_das_inscricoes):
    """Na tela do sorteio, o primeiro instante em que a relação **pode** ser congelada (FR-2651).

    Enquanto as inscrições correm, o congelamento é recusado; o primeiro possível é o fim delas, e
    não agora. Comparar só com agora deixava sem aviso justamente o Edital que uma Retificação de
    prorrogação levou até o dia da extração.
    """
    if fim_das_inscricoes is None:
        return agora
    return max(agora, fim_das_inscricoes)


__all__ = ["congelamento_mais_cedo", "inviavel", "limite_previsto"]
