"""A porta do serviço de inferência, e a parte comum dos dois adaptadores (071, `R-008`).

**Uma função, e não uma plataforma** (`FR-1504`, `D-004`). Dois serviços, escolhidos por
configuração — o Ollama na L4, o OpenRouter para a avaliação —, cada um num adaptador de algumas
dezenas de linhas. Acrescentar um terceiro é escrever código, e não configurar: não há registro de
provedores, nem camada genérica.

**Uma chamada por invocação, e nenhuma retentativa** (`FR-1505`). Diferente da fonte do sorteio,
que tem tentativas por configuração, aqui não há o que tentar de novo: cada tentativa no serviço
externo custa, e na L4 disputa a GPU. A falha volta como exceção com código, e a aplicação a traduz
em estado (data-model §4).

**Nenhuma troca de serviço** (`FR-1499`): o adaptador é o da configuração, e o Ollama fora do ar é
`INDISPONIVEL` — nunca uma chamada ao outro.

**A mensagem de erro é composta aqui**, com o código HTTP e o motivo, e **nunca** com o corpo
enviado, os cabeçalhos ou a credencial (`R-014`, `FR-1502`).

**Pela biblioteca padrão**, como a fonte do sorteio: dois `POST` não pedem cliente HTTP.
"""

from __future__ import annotations

import json
from urllib import error, request

from django.conf import settings

from processo_seletivo.duvidas.domain.estruturas_do_piloto import (
    INDISPONIVEL,
    LIMITE_DO_SERVICO,
    ORCAMENTO_ESGOTADO,
    RESPOSTA_MALFORMADA,
    TEMPO_ESGOTADO,
)

NAO_CONFIGURADO = "NAO_CONFIGURADO"
OLLAMA, OPENROUTER = "ollama", "openrouter"
ESGOTADO = "o serviço não respondeu no tempo-limite"


class FalhaDoServico(Exception):
    """Uma falha da chamada, com o código do estado que ela produz."""

    def __init__(self, codigo: str, motivo: str):
        super().__init__(f"{codigo}: {motivo}")
        self.codigo = codigo
        self.motivo = motivo


def parametros_configurados() -> dict:
    """Os parâmetros de geração, todos explícitos (`FR-1498`). É o que a troca registra."""
    return {
        "temperatura": settings.ASSISTENTE_TEMPERATURA,
        "top_p": settings.ASSISTENTE_TOP_P,
        "semente": settings.ASSISTENTE_SEMENTE,
        "contexto": settings.ASSISTENTE_CONTEXTO_TOKENS,
        "saida_maxima": settings.ASSISTENTE_SAIDA_MAXIMA_TOKENS,
        "raciocinio": settings.ASSISTENTE_RACIOCINIO,
    }


def externo() -> bool:
    """Se o serviço configurado sai da rede institucional (`FR-1503`)."""
    return settings.ASSISTENTE_SERVICO == OPENROUTER


def postar(url: str, corpo: dict, *, cabecalhos: dict | None = None) -> dict:
    """Um `POST` JSON com o tempo-limite configurado, e a tradução das falhas.

    Os cabeçalhos — inclusive a credencial — só existem dentro do `Request`; nenhuma mensagem de
    erro os lê.
    """
    return _pedir(
        request.Request(
            url,
            data=json.dumps(corpo).encode("utf-8"),
            headers={"Content-Type": "application/json", **(cabecalhos or {})},
            method="POST",
        )
    )


def obter(url: str, *, cabecalhos: dict | None = None) -> dict:
    """Um `GET` JSON: as leituras da verificação de conexão (`R-017`), com as mesmas falhas."""
    return _pedir(request.Request(url, headers=dict(cabecalhos or {}), method="GET"))


def _pedir(pedido) -> dict:
    try:
        with request.urlopen(pedido, timeout=settings.ASSISTENTE_TEMPO_LIMITE_SEGUNDOS) as resposta:
            bruto = resposta.read()
    except error.HTTPError as falha:
        raise _do_http(falha.code) from None
    except TimeoutError:
        raise FalhaDoServico(TEMPO_ESGOTADO, "o serviço não respondeu no tempo-limite") from None
    except error.URLError as falha:
        if isinstance(falha.reason, TimeoutError):
            raise FalhaDoServico(
                TEMPO_ESGOTADO, "o serviço não respondeu no tempo-limite"
            ) from None
        raise FalhaDoServico(INDISPONIVEL, "não foi possível falar com o serviço") from None
    try:
        return json.loads(bruto.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise FalhaDoServico(RESPOSTA_MALFORMADA, "o serviço não devolveu JSON") from None


def _do_http(codigo: int) -> FalhaDoServico:
    if codigo == 402:
        return FalhaDoServico(ORCAMENTO_ESGOTADO, "o serviço recusou por limite de gasto (402)")
    if codigo == 429:
        return FalhaDoServico(LIMITE_DO_SERVICO, "o serviço recusou por limite de uso (429)")
    return FalhaDoServico(INDISPONIVEL, f"o serviço respondeu com erro HTTP {codigo}")


def conversar(mensagens, esquema, parametros):
    """A porta: uma chamada ao serviço configurado, e a `Devolucao`.

    Levanta `FalhaDoServico`. Com serviço, endereço ou modelo vazios, `NAO_CONFIGURADO` — que é o
    que a suíte encontra sem a porta falsa, e por isso nenhum teste chega à rede por esquecimento.
    """
    servico = settings.ASSISTENTE_SERVICO
    if not (servico and settings.ASSISTENTE_ENDERECO and settings.ASSISTENTE_MODELO):
        raise FalhaDoServico(NAO_CONFIGURADO, "o piloto não tem serviço configurado")
    if servico == OPENROUTER:
        from processo_seletivo.duvidas.infrastructure.inferencia import openrouter

        return openrouter.conversar(mensagens, esquema, parametros)
    if servico == OLLAMA:
        from processo_seletivo.duvidas.infrastructure.inferencia import ollama

        return ollama.conversar(mensagens, esquema, parametros)
    raise FalhaDoServico(NAO_CONFIGURADO, f"serviço desconhecido: {servico!r}")
