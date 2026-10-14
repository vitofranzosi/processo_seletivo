"""O adaptador do Ollama: o serviço local, na L4 (071, servico-de-inferencia.md §2).

**O contexto vai explícito a cada chamada** (`FR-1498`). O `num_ctx` padrão do Ollama depende da
memória da GPU e da versão, e um contexto menor que o orçamento da aplicação faria o serviço
descartar mensagens antigas em silêncio — o pior corte possível, porque as fontes estão no começo.
A aplicação confere a contagem de qualquer modo (`FR-1482`); com `ASSISTENTE_OLLAMA_SEM_CORTE`, o
serviço também recusa cortar, mas só depois de a verificação confirmar que a versão instalada aceita
`truncate` e `shift`: uma versão que não os conhece os ignora, e a proteção pareceria existir.

**Nenhum caminho para o OpenRouter** (`FR-1499`). O Ollama fora do ar é `INDISPONIVEL`, e a
pergunta seguinte é de alguém — este módulo não sabe que existe outro serviço.
"""

from __future__ import annotations

from django.conf import settings

from processo_seletivo.duvidas.domain.estruturas_do_piloto import RESPOSTA_MALFORMADA, Devolucao
from processo_seletivo.duvidas.infrastructure.inferencia import FalhaDoServico, postar


def corpo(mensagens, esquema, parametros) -> dict:
    enviado = {
        "model": settings.ASSISTENTE_MODELO,
        "messages": list(mensagens),
        "stream": False,
        "format": esquema,
        "think": bool(parametros["raciocinio"]),
        "options": {
            "num_ctx": parametros["contexto"],
            "num_predict": parametros["saida_maxima"],
            "temperature": parametros["temperatura"],
            "top_p": parametros["top_p"],
            "seed": parametros["semente"],
        },
    }
    if settings.ASSISTENTE_OLLAMA_SEM_CORTE:
        enviado.update({"truncate": False, "shift": False})
    return enviado


def conversar(mensagens, esquema, parametros) -> Devolucao:
    resposta = postar(
        f"{settings.ASSISTENTE_ENDERECO}/api/chat", corpo(mensagens, esquema, parametros)
    )
    try:
        mensagem = resposta["message"]
        return Devolucao(
            texto=mensagem.get("content") or "",
            modelo=resposta.get("model") or "",
            tokens_de_entrada=resposta.get("prompt_eval_count"),
            tokens_de_saida=resposta.get("eval_count"),
            termino=resposta.get("done_reason") or "",
            raciocinio=mensagem.get("thinking") or "",
        )
    except (KeyError, TypeError, AttributeError):
        raise FalhaDoServico(RESPOSTA_MALFORMADA, "a resposta não tem a forma esperada") from None
