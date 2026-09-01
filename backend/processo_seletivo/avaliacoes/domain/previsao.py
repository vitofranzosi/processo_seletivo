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
