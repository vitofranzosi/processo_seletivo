"""A credencial do serviço externo não aparece em lugar nenhum (071, `FR-1502`, `SC-549`).

O adaptador real do OpenRouter, com `urlopen` substituído, em cada falha e na resposta de outro
modelo. A credencial conhecida é procurada no log capturado, nas mensagens das exceções, nas trocas
gravadas e na página que as mostra. Ela só pode existir no cabeçalho do pedido.
"""

import io
import json
import urllib.error
import urllib.request

import pytest
from django.urls import reverse

from processo_seletivo.duvidas.infrastructure import tokens
from processo_seletivo.duvidas.models import TrocaDoPiloto
from tests.fixtures.corpus import publicar_do_corpus
from tests.fixtures.inferencia import log_do_projeto  # noqa: F401
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

CREDENCIAL = "sk-or-v1-CREDENCIAL-QUE-NAO-PODE-VAZAR-071"


def _http(codigo):
    return urllib.error.HTTPError("https://openrouter.invalid", codigo, "erro", {}, None)


def _corpo(dados):
    return io.BytesIO(json.dumps(dados).encode("utf-8"))


OUTRO_MODELO = {
    "model": "provedor/outro",
    "choices": [{"message": {"content": "{}"}, "finish_reason": "stop"}],
    "usage": {"prompt_tokens": 10, "completion_tokens": 1},
}


@pytest.mark.parametrize(
    "resposta",
    [
        _http(401),
        _http(402),
        _http(429),
        _http(500),
        urllib.error.URLError(ConnectionRefusedError()),
        TimeoutError(),
        "nao-e-json",
        OUTRO_MODELO,
    ],
    ids=["401", "402", "429", "500", "recusada", "tempo", "malformada", "outro-modelo"],
)
def test_a_credencial_nao_vaza(
    client,
    api_client,
    settings,
    seletor_ligado,
    monkeypatch,
    log_do_projeto,  # noqa: F811
    resposta,  # noqa: F811
):
    monkeypatch.setattr(tokens, "contar", lambda mensagens: 1000)
    settings.ASSISTENTE_SERVICO = "openrouter"
    settings.ASSISTENTE_ENDERECO = "https://openrouter.invalid/api/v1"
    settings.ASSISTENTE_MODELO = "qwen/qwen3.8-27b"
    settings.ASSISTENTE_CREDENCIAL = CREDENCIAL
    pedidos = []

    def servico(pedido, timeout=None):
        pedidos.append(pedido)
        if isinstance(resposta, Exception):
            raise resposta
        if isinstance(resposta, str):
            return io.BytesIO(resposta.encode("utf-8"))
        return _corpo(resposta)

    monkeypatch.setattr(urllib.request, "urlopen", servico)
    edital, _ = publicar_do_corpus(api_client, "91", chave="credencial91")
    identificar(client, "pessoa", ["gestor", "participante-piloto-assistente"])
    url = reverse("interface:assistente", args=[edital.id])

    client.post(url, {"pergunta": "Quantas vagas há?"})
    pagina = client.get(url).content.decode()

    assert len(pedidos) == 1
    assert pedidos[0].get_header("Authorization") == f"Bearer {CREDENCIAL}"
    assert any("troca_do_piloto" in linha for linha in log_do_projeto), "o coletor lê o log"
    assert not any(CREDENCIAL in linha for linha in log_do_projeto)
    assert CREDENCIAL not in pagina
    for troca in TrocaDoPiloto.objects.values():
        assert CREDENCIAL not in repr(troca)
