"""O adaptador do Ollama, com `urlopen` substituído (071, T054, servico-de-inferencia.md §2).

O contexto, a saída e a amostragem vão explícitos; `truncate` e `shift` só depois da verificação; e
o Ollama fora do ar é `INDISPONIVEL`, com um pedido só, ao endereço dele (US4, cenário 1).
"""

import io
import json
import urllib.error
import urllib.request

import pytest

from processo_seletivo.duvidas.domain.estruturas_do_piloto import (
    INDISPONIVEL,
    RESPOSTA_MALFORMADA,
)
from processo_seletivo.duvidas.domain.mensagens import ESQUEMA_DA_SAIDA
from processo_seletivo.duvidas.infrastructure import inferencia

ENDERECO = "http://l4.invalid:11434"
MENSAGENS = [{"role": "system", "content": "i"}, {"role": "user", "content": "p"}]


@pytest.fixture
def ollama(settings):
    settings.ASSISTENTE_SERVICO = "ollama"
    settings.ASSISTENTE_ENDERECO = ENDERECO
    settings.ASSISTENTE_MODELO = "qwen3.8:27b"
    # Uma credencial configurada por engano não pode sair para lugar nenhum.
    settings.ASSISTENTE_CREDENCIAL = "sk-or-credencial-que-o-ollama-nao-usa"


class Servico:
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
        "model": "qwen3.8:27b",
        "message": {"role": "assistant", "content": "{}", "thinking": "pensei"},
        "done": True,
        "done_reason": "stop",
        "prompt_eval_count": 1200,
        "eval_count": 80,
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


def test_o_corpo_leva_o_contexto_e_os_parametros(monkeypatch, ollama, settings):
    _devolucao, servico = _chamar(monkeypatch, _resposta())
    pedido, timeout = servico.pedidos[0]
    corpo = json.loads(pedido.data)

    assert pedido.full_url == f"{ENDERECO}/api/chat"
    assert timeout == settings.ASSISTENTE_TEMPO_LIMITE_SEGUNDOS
    assert corpo["stream"] is False
    assert corpo["format"] == ESQUEMA_DA_SAIDA
    assert corpo["think"] is False
    assert corpo["options"] == {
        "num_ctx": settings.ASSISTENTE_CONTEXTO_TOKENS,
        "num_predict": settings.ASSISTENTE_SAIDA_MAXIMA_TOKENS,
        "temperature": settings.ASSISTENTE_TEMPERATURA,
        "top_p": settings.ASSISTENTE_TOP_P,
        "seed": settings.ASSISTENTE_SEMENTE,
    }
    # Sem a verificação confirmar, nada de `truncate` nem `shift`: a versão que não os conhece os
    # ignoraria, e a proteção pareceria existir.
    assert "truncate" not in corpo and "shift" not in corpo
    assert pedido.get_header("Authorization") is None


def test_sem_corte_so_quando_configurado(monkeypatch, ollama, settings):
    settings.ASSISTENTE_OLLAMA_SEM_CORTE = True

    _devolucao, servico = _chamar(monkeypatch, _resposta())
    corpo = json.loads(servico.pedidos[0][0].data)

    assert corpo["truncate"] is False and corpo["shift"] is False


def test_a_devolucao_e_lida(monkeypatch, ollama):
    devolucao, _ = _chamar(monkeypatch, _resposta())

    assert devolucao.modelo == "qwen3.8:27b"
    assert devolucao.tokens_de_entrada == 1200
    assert devolucao.tokens_de_saida == 80
    assert devolucao.termino == "stop"
    assert devolucao.raciocinio == "pensei"
    assert devolucao.custo is None


def test_o_limite_de_saida_volta_como_termino(monkeypatch, ollama):
    """`length` chega à aplicação como está, e ela a trata como `INCOMPLETA` (`FR-1483`)."""
    devolucao, _ = _chamar(monkeypatch, _resposta(done_reason="length"))

    assert devolucao.termino == "length"


def test_fora_do_ar_e_indisponivel_e_nada_sai_para_outro_endereco(monkeypatch, ollama):
    with pytest.raises(inferencia.FalhaDoServico) as recusa:
        _chamar(monkeypatch, urllib.error.URLError(ConnectionRefusedError()))
    pedidos = urllib.request.urlopen.pedidos

    assert recusa.value.codigo == INDISPONIVEL
    assert [pedido.full_url for pedido, _ in pedidos] == [f"{ENDERECO}/api/chat"]
    assert "credencial" not in str(recusa.value)


def test_resposta_sem_a_forma_esperada(monkeypatch, ollama):
    with pytest.raises(inferencia.FalhaDoServico) as recusa:
        _chamar(monkeypatch, {"error": "model not found"})

    assert recusa.value.codigo == RESPOSTA_MALFORMADA
