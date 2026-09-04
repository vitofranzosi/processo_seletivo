"""O que a ausência quer dizer — num lugar só.

O incremento da `012` é aditivo, e conteúdo publicado antes dele não carrega as duas chaves. Isso é
legítimo e vai continuar sendo: elevar no caminho de leitura pública faria a tela mostrar conteúdo
que o `content_hash` da Publicação não cobre, e a verificação de integridade da `005` passaria a
comparar coisas diferentes (012, T-002).

Convivem, portanto, Etapas com e sem as propriedades. **Quem lê não pode precisar saber disso**: se
cada consumidor testasse presença de chave por conta própria, a regra de FR-009 e FR-066 estaria
escrita em cinco lugares e divergiria no sexto. Estas duas funções são esse lugar.
"""

from decimal import Decimal, InvalidOperation

from processo_seletivo.avaliacoes.domain.formas import Forma

# Sem declaração, uma avaliação por inscrição (FR-009). Não é padrão de conveniência: é o que a
# spec diz que a ausência significa, e é o que a elevação escreve quando converte.
AVALIACOES_QUANDO_AUSENTE = 1


def avaliacoes_previstas(etapa):
    """Quantas avaliações a inscrição recebe nesta Etapa. Nunca `None`, nunca zero."""
    if not isinstance(etapa, dict):
        return AVALIACOES_QUANDO_AUSENTE
    declarado = etapa.get("evaluationsPerRegistration")
    if not isinstance(declarado, int) or isinstance(declarado, bool) or declarado < 1:
        return AVALIACOES_QUANDO_AUSENTE
    return declarado


def pontuacao_maxima(etapa):
    """O limite publicado, ou `None` quando o Edital não o declarou.

    `None` **não** é "sem limite prático": é "o Edital não disse". Quem valida pontuação trata os
    dois casos de formas diferentes, e a tela diz qual deles está diante de si — inventar um teto
    aqui seria aplicar regra que ninguém publicou (P-007, FR-066).
    """
    if not isinstance(etapa, dict):
        return None
    declarado = etapa.get("maximumScore")
    if declarado is None:
        return None
    try:
        return Decimal(str(declarado))
    except (InvalidOperation, ValueError, TypeError):
        return None


# Sem declaração, a Etapa pontua (FR-120). Não é padrão de conveniência: até a versão canônica 5 o
# domínio não admitia outra forma, e escrever `PONTUADA` no lugar da ausência não afirma nada que o
# conteúdo já não dissesse. A partir da 6 a chave existe sempre, e é a validação de publicação que
# recusa o nulo — este leitor continua defensivo porque ele também atravessa conteúdo antigo.
FORMA_QUANDO_AUSENTE = Forma.PONTUADA


def forma_publicada(etapa):
    """A forma de conclusão que esta Etapa exige. Nunca `None`.

    Valor fora do par declarado é lido como a ausência, e não estoura: o mesmo tratamento que
    `avaliacoes_previstas` dá a lixo, e pela mesma razão — quem lê conteúdo antigo não pode receber
    exceção de um campo que talvez nem exista ali.
    """
    if not isinstance(etapa, dict):
        return FORMA_QUANDO_AUSENTE
    declarada = etapa.get("forma")
    if declarada not in Forma.values:
        return FORMA_QUANDO_AUSENTE
    return Forma(declarada)


def decisoria(etapa):
    """Atalho legível para a pergunta que o domínio faz o tempo todo."""
    return forma_publicada(etapa) == Forma.DECISORIA


def rotulos(etapa):
    """`(favorável, desfavorável)` como o Edital os publicou, ou `(None, None)`.

    **Não há default institucional**, e a ausência não vira "Deferido/Indeferido": o domínio aplicar
    rótulo que o Edital não publicou é exatamente o que P-007 impede. Prefill de tela é outra coisa,
    e mora na tela (012, D-008).
    """
    if not isinstance(etapa, dict):
        return (None, None)
    return (_rotulo(etapa.get("rotuloFavoravel")), _rotulo(etapa.get("rotuloDesfavoravel")))


def _rotulo(valor):
    """Rótulo em branco não é rótulo: um PDF com `""` no lugar do indeferimento não diz nada."""
    if not isinstance(valor, str):
        return None
    limpo = valor.strip()
    return limpo or None


def conclusao_exibivel(forma, pontuacao, sentido, etapa):
    """O que a conclusão afirmou, dito no vocabulário sob o qual ela foi feita.

    **A forma é a da conclusão, e a Etapa é a da versão que a governou** — não a vigente. Ler a
    forma vigente para renderizar histórico faria uma conclusão pontuada aparecer como favorável
    depois de uma Retificação que tornasse a Etapa decisória, e uma decisória preservada aparecer
    como um traço. É o mesmo motivo pelo qual a conclusão guarda a forma (FR-117): preservar o
    registro sem preservar a leitura preserva metade.

    Devolve `None` na forma pontuada, porque ali quem exibe é o filtro de pontuação — esta função
    responde "há um rótulo a mostrar no lugar do número?".
    """
    if forma != Forma.DECISORIA:
        return None
    favoravel, desfavoravel = rotulos(etapa)
    if sentido == "DESFAVORAVEL":
        return desfavoravel or "desfavorável"
    if sentido == "FAVORAVEL":
        return favoravel or "favorável"
    return None


def etapa_do_conteudo(conteudo, etapa_id):
    """A Etapa daquela identidade no conteúdo publicado, ou `{}`.

    `{}` e não `None`: quem chama vai perguntar pelos rótulos, e a ausência de conteúdo histórico
    significa "sem rótulo a mostrar", não erro.
    """
    alvo = str(etapa_id)
    for etapa in (conteudo or {}).get("stages") or []:
        if isinstance(etapa, dict) and str(etapa.get("id")) == alvo:
            return etapa
    return {}
