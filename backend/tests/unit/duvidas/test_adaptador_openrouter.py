"""O adaptador do OpenRouter, com `urlopen` substituído (071, `R-008`).

O corpo enviado é o contrato com o serviço: cada parâmetro explícito, nenhuma troca de provedor nem
de modelo, a credencial só no cabeçalho. E cada falha volta como um código, com uma chamada só.
"""

import io
import json
import urllib.error
import urllib.request

import pytest

from processo_seletivo.duvidas.domain.estruturas_do_piloto import (
    INDISPONIVEL,
    LIMITE_DO_SERVICO,
    ORCAMENTO_ESGOTADO,
    RESPOSTA_MALFORMADA,
    TEMPO_ESGOTADO,
)
from processo_seletivo.duvidas.domain.mensagens import ESQUEMA_DA_SAIDA
from processo_seletivo.duvidas.infrastructure import inferencia

CREDENCIAL = "sk-or-credencial-de-teste-071"
MENSAGENS = [{"role": "system", "content": "i"}, {"role": "user", "content": "p"}]


@pytest.fixture
def openrouter(settings):
    settings.ASSISTENTE_SERVICO = "openrouter"
    settings.ASSISTENTE_ENDERECO = "https://openrouter.invalid/api/v1"
    settings.ASSISTENTE_MODELO = "qwen/qwen3.8-27b"
    settings.ASSISTENTE_CREDENCIAL = CREDENCIAL


class Servico:
    """Substitui `urlopen`: guarda o pedido e devolve a resposta ou a falha dada."""

    def __init__(self, resposta):
        self.resposta = resposta
        self.pedidos = []

    def __call__(self, pedido, timeout=None):
        self.pedidos.append((pedido, timeout))
        if isinstance(self.resposta, Exception):
            raise self.resposta
        return io.BytesIO(json.dumps(self.resposta).encode("utf-8"))


def _resposta(**sobre):
    resposta = {
        "model": "qwen/qwen3.8-27b",
        "provider": "Provedor",
        "choices": [{"message": {"content": "{}", "reasoning": "pensei"}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 120, "completion_tokens": 30, "cost": 0.0012},
    }
    resposta.update(sobre)
    return resposta


def _chamar(monkeypatch, resposta):
    servico = Servico(resposta)
    monkeypatch.setattr(urllib.request, "urlopen", servico)
    try:
        devolucao = inferencia.conversar(
            MENSAGENS, ESQUEMA_DA_SAIDA, inferencia.parametros_configurados()
        )
    finally:
        assert len(servico.pedidos) == 1, "uma chamada, e nenhuma retentativa"
    return devolucao, servico


def test_o_corpo_e_explicito_e_sem_troca(monkeypatch, openrouter, settings):
    _devolucao, servico = _chamar(monkeypatch, _resposta())
    pedido, timeout = servico.pedidos[0]
    corpo = json.loads(pedido.data)

    assert pedido.full_url == "https://openrouter.invalid/api/v1/chat/completions"
    assert timeout == settings.ASSISTENTE_TEMPO_LIMITE_SEGUNDOS
    assert corpo["model"] == "qwen/qwen3.8-27b"
    assert "models" not in corpo
    assert corpo["provider"] == {
        "allow_fallbacks": False,
        "require_parameters": True,
        "data_collection": "deny",
        "zdr": False,
    }
    for campo in ("temperature", "top_p", "seed", "max_tokens"):
        assert corpo[campo] is not None
    assert corpo["response_format"]["json_schema"]["strict"] is True
    assert corpo["stream"] is False
    assert pedido.get_header("Authorization") == f"Bearer {CREDENCIAL}"
    assert CREDENCIAL not in pedido.data.decode("utf-8")


def test_a_devolucao_e_lida(monkeypatch, openrouter):
    devolucao, _ = _chamar(monkeypatch, _resposta())

    assert devolucao.modelo == "qwen/qwen3.8-27b"
    assert devolucao.tokens_de_entrada == 120
    assert devolucao.termino == "stop"
    assert devolucao.custo == 0.0012
    assert devolucao.raciocinio == "pensei"


def _http(codigo):
    return urllib.error.HTTPError("https://openrouter.invalid", codigo, "x", {}, None)


@pytest.mark.parametrize(
    ("falha", "codigo"),
    [
        (_http(402), ORCAMENTO_ESGOTADO),
        (_http(429), LIMITE_DO_SERVICO),
        (_http(503), INDISPONIVEL),
        (urllib.error.URLError(ConnectionRefusedError()), INDISPONIVEL),
        (urllib.error.URLError(TimeoutError()), TEMPO_ESGOTADO),
        (TimeoutError(), TEMPO_ESGOTADO),
    ],
)
def test_cada_falha_e_um_codigo_e_uma_chamada(monkeypatch, openrouter, falha, codigo):
    with pytest.raises(inferencia.FalhaDoServico) as recusa:
        _chamar(monkeypatch, falha)

    assert recusa.value.codigo == codigo
    assert CREDENCIAL not in str(recusa.value)


def test_resposta_sem_a_forma_esperada(monkeypatch, openrouter):
    with pytest.raises(inferencia.FalhaDoServico) as recusa:
        _chamar(monkeypatch, {"erro": "nada"})

    assert recusa.value.codigo == RESPOSTA_MALFORMADA


def test_sem_configuracao_nenhum_pedido_sai(settings):
    settings.ASSISTENTE_SERVICO = ""

    with pytest.raises(inferencia.FalhaDoServico) as recusa:
        inferencia.conversar(MENSAGENS, ESQUEMA_DA_SAIDA, inferencia.parametros_configurados())

    assert recusa.value.codigo == inferencia.NAO_CONFIGURADO


def test_o_provedor_fixo_vai_sem_troca(monkeypatch, openrouter, settings):
    """Um provedor só (`FR-1499`): o roteamento pelo mais barato recusava com 429 (14/10)."""
    settings.ASSISTENTE_PROVEDOR = "parasail"

    _devolucao, servico = _chamar(monkeypatch, _resposta())
    provedor = json.loads(servico.pedidos[0][0].data)["provider"]

    assert provedor["order"] == ["parasail"]
    assert provedor["allow_fallbacks"] is False


def test_a_recusa_diz_qual_provedor_recusou(monkeypatch, openrouter):
    corpo = {"error": {"code": 429, "metadata": {"provider_name": "Darkbloom", "raw": "x"}}}
    recusa_429 = urllib.error.HTTPError(
        "https://openrouter.invalid", 429, "x", {}, io.BytesIO(json.dumps(corpo).encode("utf-8"))
    )

    with pytest.raises(inferencia.FalhaDoServico) as recusa:
        _chamar(monkeypatch, recusa_429)

    assert recusa.value.codigo == LIMITE_DO_SERVICO
    assert recusa.value.provedor == "Darkbloom"
    assert CREDENCIAL not in str(recusa.value)
