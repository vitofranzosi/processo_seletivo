"""A contagem de tokens pelo tokenizer publicado do modelo (071, `R-006`).

**Contar antes de enviar é o que impede o corte silencioso** (`FR-1479`). O Ollama, excedido o
contexto, descarta mensagens antigas sem erro; uma fonte cortada é uma condição omitida que
ninguém vê. Por isso a contagem é a do modelo — e não por caracteres nem por palavras, que a spec
proíbe —, e, sem ela, o piloto não chama o serviço.

**O molde de conversa não é reproduzido.** Cada mensagem soma os tokens do conteúdo e um
acréscimo fixo, `ASSISTENTE_TOKENS_POR_MENSAGEM`, que a verificação de conexão mede contra a
contagem do próprio serviço. Reproduzir o molde Jinja do modelo pediria a biblioteca
`transformers`. A margem do orçamento (`R-007`) cobre o erro dessa calibração, e a conferência
depois da resposta acusa o corte.

**A biblioteca é do grupo opcional `assistente`**, que a produção não instala. Sem ela, ou sem o
arquivo, `SemTokenizer` — e a pergunta fica com esse estado, sem chamada.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from django.conf import settings


class SemTokenizer(Exception):
    """Falta a biblioteca `tokenizers` ou o `tokenizer.json` configurado."""


@lru_cache(maxsize=2)
def _tokenizer(caminho: str):
    # Uma vez por processo e por arquivo: carregar o tokenizer leva centenas de milissegundos.
    try:
        from tokenizers import Tokenizer
    except ImportError as falta:
        raise SemTokenizer("a biblioteca `tokenizers` não está instalada") from falta
    if not caminho or not Path(caminho).is_file():
        raise SemTokenizer("o `tokenizer.json` do modelo não foi encontrado")
    return Tokenizer.from_file(caminho)


def contar_texto(texto: str) -> int:
    tokenizer = _tokenizer(getattr(settings, "ASSISTENTE_TOKENIZER", ""))
    return len(tokenizer.encode(texto, add_special_tokens=False).ids)


def contar(mensagens) -> int:
    """Os tokens de uma lista de mensagens, com o acréscimo por mensagem."""
    acrescimo = int(getattr(settings, "ASSISTENTE_TOKENS_POR_MENSAGEM", 8))
    return sum(contar_texto(mensagem["content"]) + acrescimo for mensagem in mensagens)
