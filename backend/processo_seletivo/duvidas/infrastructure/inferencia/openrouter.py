"""O adaptador do OpenRouter: desenvolvimento e avaliação inicial (071, servico-de-inferencia.md).

**Sem troca de provedor nem de modelo** (`FR-1499`). O OpenRouter, por padrão, passa a outro
provedor quando o primeiro falha, e com um vetor `models` passa a outro modelo. Os dois ficam
desligados: a avaliação precisa saber que modelo respondeu — e a aplicação confere o `model` da
resposta contra o configurado.

**Só provedores que aceitam o que se pediu** (`FR-1498`): com `require_parameters`, um provedor que
ignoraria o esquema da saída ou a semente não é escolhido.

**Retenção recusada onde se pode recusar** (`FR-1503`): `data_collection: deny`, e `zdr` por
configuração. Os nomes de campo foram lidos na documentação oficial em 12/10/2026, e a verificação
de conexão os confere contra o serviço real.
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
        "max_tokens": parametros["saida_maxima"],
        "temperature": parametros["temperatura"],
        "top_p": parametros["top_p"],
        "seed": parametros["semente"],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "resposta_do_assistente", "strict": True, "schema": esquema},
        },
        "reasoning": {"enabled": bool(parametros["raciocinio"])},
        "provider": {
            "allow_fallbacks": False,
            "require_parameters": True,
            "data_collection": "deny",
            "zdr": bool(settings.ASSISTENTE_ZDR),
        },
    }
    if settings.ASSISTENTE_PROVEDOR:
        # Um provedor só, e sem troca: a quantização do ensaio fica conhecida (`FR-1499`).
        enviado["provider"]["order"] = [settings.ASSISTENTE_PROVEDOR]
    return enviado


def conversar(mensagens, esquema, parametros) -> Devolucao:
    resposta = postar(
        f"{settings.ASSISTENTE_ENDERECO}/chat/completions",
        corpo(mensagens, esquema, parametros),
        cabecalhos={"Authorization": f"Bearer {settings.ASSISTENTE_CREDENCIAL}"},
    )
    try:
        escolha = resposta["choices"][0]
        mensagem = escolha["message"]
        uso = resposta.get("usage") or {}
        return Devolucao(
            texto=mensagem.get("content") or "",
            modelo=resposta.get("model") or "",
            tokens_de_entrada=uso.get("prompt_tokens"),
            tokens_de_saida=uso.get("completion_tokens"),
            termino=escolha.get("finish_reason") or "",
            custo=uso.get("cost"),
            provedor=resposta.get("provider") or "",
            raciocinio=mensagem.get("reasoning") or "",
        )
    except (KeyError, IndexError, TypeError, AttributeError):
        raise FalhaDoServico(RESPOSTA_MALFORMADA, "a resposta não tem a forma esperada") from None
