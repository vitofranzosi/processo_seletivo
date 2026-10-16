"""A verificação de conexão, com `urlopen` respondendo como o Ollama (071, T056, `R-017`).

Sem banco: o comando não grava nada (`FR-1520`), e um caso unitário que tocasse o banco falharia.
"""

import io
import json
import urllib.request
from io import StringIO

import pytest
from django.core.management import call_command

from processo_seletivo.duvidas.infrastructure import tokens

ENDERECO = "http://l4.invalid:11434"
MODELO = "qwen3.8:27b"


@pytest.fixture
def configuracao(settings, monkeypatch):
    settings.ASSISTENTE_SERVICO = "ollama"
    settings.ASSISTENTE_ENDERECO = ENDERECO
    settings.ASSISTENTE_MODELO = MODELO
    settings.ASSISTENTE_QUANTIZACAO = "Q4_K_M"
    settings.ASSISTENTE_CONTEXTO_TOKENS = 32768
    settings.ASSISTENTE_TOKENS_POR_MENSAGEM = 8
    settings.ASSISTENTE_TOKENS_POR_CHAMADA = 0
    # Um token a cada quatro caracteres: o tokenizer real não é dependência da suíte.
    monkeypatch.setattr(tokens, "contar_texto", lambda texto: len(texto) // 4)


def _respostas(**sobre):
    respostas = {
        "/api/version": {"version": "0.12.3"},
        "/api/tags": {"models": [{"name": MODELO}, {"name": "outro:7b"}]},
        "/api/show": {
            "details": {"family": "qwen3", "parameter_size": "27B", "quantization_level": "Q4_K_M"},
            "model_info": {"general.architecture": "qwen3", "qwen3.context_length": 40960},
        },
        "/api/chat": {
            "model": MODELO,
            "message": {"role": "assistant", "content": "{}"},
            "done_reason": "stop",
            "prompt_eval_count": 0,  # calculado em `Ollama`, pela contagem falsa
            "eval_count": 12,
        },
        "/api/ps": {
            "models": [{"name": MODELO, "size": 17_300_000_000, "size_vram": 17_300_000_000}]
        },
    }
    respostas.update(sobre)
    return respostas


class Ollama:
    """Responde por caminho, e guarda os pedidos."""

    def __init__(self, respostas, *, por_mensagem=6, fixo=0):
        self.respostas = respostas
        self.por_mensagem = por_mensagem
        self.fixo = fixo
        self.pedidos = []

    def __call__(self, pedido, timeout=None):
        caminho = pedido.full_url.removeprefix(ENDERECO)
        self.pedidos.append((pedido.get_method(), caminho))
        resposta = dict(self.respostas[caminho])
        if caminho == "/api/chat" and not resposta["prompt_eval_count"]:
            mensagens = json.loads(pedido.data)["messages"]
            resposta["prompt_eval_count"] = self.fixo + sum(
                len(mensagem["content"]) // 4 + self.por_mensagem for mensagem in mensagens
            )
        return io.BytesIO(json.dumps(resposta).encode("utf-8"))


def _verificar(monkeypatch, servico):
    monkeypatch.setattr(urllib.request, "urlopen", servico)
    saida = StringIO()
    codigo = 0
    try:
        call_command("verificar_servico_de_inferencia", stdout=saida)
    except SystemExit as saiu:
        codigo = saiu.code
    return codigo, saida.getvalue()


def test_sem_divergencia_imprime_o_que_o_servico_informa(monkeypatch, configuracao):
    servico = Ollama(_respostas())

    codigo, saida = _verificar(monkeypatch, servico)

    assert codigo == 0, saida
    assert "Versão do Ollama: 0.12.3" in saida
    assert f"Modelo configurado: {MODELO} — instalado: sim" in saida
    assert "quantização: Q4_K_M" in saida and "contexto do modelo: 40960" in saida
    assert "carregado: sim, 100% na GPU (17,3 GB)" in saida
    assert "Acréscimo além do texto: medido 12 tokens em 2 mensagens; configurado 16" in saida
    assert "término stop" in saida
    assert "A confirmar com a infraestrutura: OLLAMA_NUM_PARALLEL" in saida
    assert "truncate e shift" in saida
    assert saida.rstrip().endswith("Divergências: nenhuma")
    # Uma conversa sintética, e só uma; a ocupação lida depois dela, que é o que carrega o modelo.
    assert [caminho for _, caminho in servico.pedidos] == [
        "/api/version",
        "/api/tags",
        "/api/show",
        "/api/chat",
        "/api/ps",
    ]


def test_o_modelo_que_nao_esta_instalado_diverge(monkeypatch, configuracao):
    servico = Ollama(_respostas(**{"/api/tags": {"models": [{"name": "outro:7b"}]}}))

    codigo, saida = _verificar(monkeypatch, servico)

    assert codigo == 1
    assert "instalado: não" in saida
    assert f"o modelo {MODELO} não está instalado" in saida
    assert "/api/chat" not in [caminho for _, caminho in servico.pedidos]


def test_a_quantizacao_diferente_diverge(monkeypatch, configuracao):
    mostrado = _respostas()["/api/show"]
    mostrado = {**mostrado, "details": {**mostrado["details"], "quantization_level": "Q8_0"}}

    codigo, saida = _verificar(monkeypatch, Ollama(_respostas(**{"/api/show": mostrado})))

    assert codigo == 1
    assert "a quantização servida é Q8_0, e a configurada, Q4_K_M" in saida


def test_sem_quantizacao_configurada_diverge(monkeypatch, configuracao, settings):
    settings.ASSISTENTE_QUANTIZACAO = ""

    codigo, saida = _verificar(monkeypatch, Ollama(_respostas()))

    assert codigo == 1
    assert "ASSISTENTE_QUANTIZACAO" in saida


def test_o_modelo_parcialmente_na_cpu_diverge(monkeypatch, configuracao):
    ps = {"models": [{"name": MODELO, "size": 20_000_000_000, "size_vram": 15_000_000_000}]}

    codigo, saida = _verificar(monkeypatch, Ollama(_respostas(**{"/api/ps": ps})))

    assert codigo == 1
    assert "carregado: sim, 75% na GPU" in saida
    assert "o modelo está 25% na CPU" in saida


def test_o_acrescimo_subestimado_diverge(monkeypatch, configuracao):
    codigo, saida = _verificar(monkeypatch, Ollama(_respostas(), por_mensagem=12))

    assert codigo == 1
    assert "o acréscimo configurado (16) é menor que o medido (24)" in saida


def test_o_acrescimo_fixo_da_chamada_entra_na_conta(monkeypatch, configuracao, settings):
    """O ensaio de 14/10: ~250 tokens por chamada, e quase nada por mensagem (`R-006`)."""
    servico = Ollama(_respostas(), por_mensagem=3, fixo=257)

    codigo, saida = _verificar(monkeypatch, servico)
    assert codigo == 1
    assert "o acréscimo configurado (16) é menor que o medido (263)" in saida

    settings.ASSISTENTE_TOKENS_POR_CHAMADA = 250
    settings.ASSISTENTE_TOKENS_POR_MENSAGEM = 7
    codigo, saida = _verificar(monkeypatch, Ollama(_respostas(), por_mensagem=3, fixo=257))
    assert codigo == 0, saida
    assert (
        "medido 263 tokens em 2 mensagens; configurado 264 (ASSISTENTE_TOKENS_POR_CHAMADA 250 + "
        "2 × ASSISTENTE_TOKENS_POR_MENSAGEM 7)"
    ) in saida


def test_contexto_menor_que_o_configurado_diverge(monkeypatch, configuracao, settings):
    settings.ASSISTENTE_CONTEXTO_TOKENS = 65536

    codigo, saida = _verificar(monkeypatch, Ollama(_respostas()))

    assert codigo == 1
    assert "o contexto do modelo é 40960, menor que o configurado (65536)" in saida


class OpenRouter:
    """Responde a `/key` com o limite dado e a `/chat/completions`, e guarda os caminhos."""

    def __init__(self, limite):
        self.limite = limite
        self.caminhos = []

    def __call__(self, pedido, timeout=None):
        caminho = pedido.full_url.removeprefix("https://openrouter.invalid/api/v1")
        self.caminhos.append(caminho)
        if caminho == "/key":
            resposta = {"data": {"limit": self.limite, "usage": 0.5}}
        else:
            resposta = {
                "model": "qwen/qwen3.8-27b",
                "choices": [{"message": {"content": "{}"}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 52, "completion_tokens": 12},
            }
        return io.BytesIO(json.dumps(resposta).encode("utf-8"))


@pytest.fixture
def openrouter(settings, monkeypatch):
    settings.ASSISTENTE_SERVICO = "openrouter"
    settings.ASSISTENTE_ENDERECO = "https://openrouter.invalid/api/v1"
    settings.ASSISTENTE_MODELO = "qwen/qwen3.8-27b"
    settings.ASSISTENTE_CREDENCIAL = "sk-or-credencial-de-teste"
    monkeypatch.setattr(tokens, "contar_texto", lambda texto: len(texto) // 4)


def test_a_chave_sem_limite_de_gasto_diverge_e_nada_sai(monkeypatch, openrouter):
    """O limite da chave é a única barreira de gasto (`FR-1507`): sem ele, nada sai."""
    servico = OpenRouter(limite=None)

    codigo, saida = _verificar(monkeypatch, servico)

    assert codigo == 1
    assert "a chave não tem limite de gasto" in saida
    assert servico.caminhos == ["/key"]


def test_com_limite_de_gasto_a_conversa_sintetica_sai(monkeypatch, openrouter):
    servico = OpenRouter(limite=5)

    codigo, saida = _verificar(monkeypatch, servico)

    assert codigo == 0, saida
    assert "Limite de gasto da chave: 5" in saida
    assert servico.caminhos == ["/key", "/chat/completions"]


# ---- O valor do serviço (073, `FR-1661`) ------------------------------------------------------


@pytest.mark.parametrize("valor", ["Ollama", "ollama ", "openai"])
def test_o_servico_fora_do_vocabulario_e_desconhecido_e_nada_sai(
    monkeypatch, configuracao, settings, valor
):
    """Com maiúscula ou espaço, o valor existe: "nenhum serviço" mandava procurar a variável."""
    settings.ASSISTENTE_SERVICO = valor
    servico = Ollama(_respostas())

    codigo, saida = _verificar(monkeypatch, servico)

    assert codigo == 1
    assert f"serviço desconhecido: {valor!r} (ASSISTENTE_SERVICO)" in saida
    assert "os aceitos são ollama e openrouter, e em produção só ollama" in saida
    assert "nenhum serviço configurado" not in saida
    assert servico.pedidos == []


def test_o_servico_vazio_continua_nao_configurado(monkeypatch, configuracao, settings):
    settings.ASSISTENTE_SERVICO = ""
    servico = Ollama(_respostas())

    codigo, saida = _verificar(monkeypatch, servico)

    assert codigo == 1
    assert "nenhum serviço configurado (ASSISTENTE_SERVICO)" in saida
    assert "desconhecido" not in saida
    assert servico.pedidos == []
