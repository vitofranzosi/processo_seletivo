"""Os falsos do piloto do assistente (071, `R-008`, `R-019`).

**Só nos testes.** Não há falso de demonstração: uma tela que responde sem modelo confundiria a
avaliação, que é para o que o piloto existe. A porta falsa substitui a função da porta por
`monkeypatch` — como os testes da fonte do sorteio fazem — e **conta as chamadas**, porque "no
máximo uma chamada por pergunta" (`FR-1505`) é o que mais se verifica aqui.

**O contador falso** substitui o tokenizer: a biblioteca `tokenizers` não é dependência de
desenvolvimento, e a suíte não pode depender de um arquivo de modelo fora do repositório.
"""

from __future__ import annotations

import json
import logging
import urllib.request

import pytest

from processo_seletivo.duvidas.domain.estruturas_do_piloto import Devolucao
from processo_seletivo.duvidas.infrastructure import inferencia, tokens

MODELO = "modelo/de-teste"


def saida(tipo, *trechos):
    """O JSON do contrato (saida-do-modelo.md §2). Cada trecho: `(natureza, texto, fontes)`."""
    return json.dumps(
        {
            "tipo": tipo,
            "trechos": [
                {"natureza": natureza, "texto": texto, "fontes": list(fontes)}
                for natureza, texto, fontes in trechos
            ],
        },
        ensure_ascii=False,
    )


def devolucao(texto, *, modelo=MODELO, termino="stop", tokens_de_entrada=None, raciocinio=""):
    return Devolucao(
        texto=texto,
        modelo=modelo,
        tokens_de_entrada=tokens_de_entrada,
        tokens_de_saida=10,
        termino=termino,
        raciocinio=raciocinio,
    )


class PortaFalsa:
    """Devolve, em sequência, as devoluções ou falhas dadas — e guarda o que recebeu."""

    def __init__(self, respostas):
        self.respostas = list(respostas)
        self.chamadas = []

    def __call__(self, mensagens, esquema, parametros):
        self.chamadas.append({"mensagens": mensagens, "esquema": esquema, "parametros": parametros})
        if not self.respostas:
            raise AssertionError("a porta foi chamada mais vezes do que o caso previa")
        resposta = self.respostas.pop(0)
        if isinstance(resposta, Exception):
            raise resposta
        if callable(resposta):
            return resposta(mensagens)
        return resposta


@pytest.fixture
def porta_falsa(monkeypatch, settings):
    """`porta_falsa(*respostas)`: liga o serviço de teste e substitui a porta."""
    settings.ASSISTENTE_SERVICO = "ollama"
    settings.ASSISTENTE_ENDERECO = "http://servico.invalid"
    settings.ASSISTENTE_MODELO = MODELO

    def instalar(*respostas):
        porta = PortaFalsa(respostas)
        monkeypatch.setattr(inferencia, "conversar", porta)
        return porta

    return instalar


@pytest.fixture
def contador_falso(monkeypatch):
    """Um token a cada `caracteres_por_token` caracteres, mais o acréscimo por mensagem."""

    def instalar(caracteres_por_token=4, *, por_mensagem=8):
        def contar(mensagens):
            return sum(
                len(mensagem["content"]) // caracteres_por_token + por_mensagem
                for mensagem in mensagens
            )

        monkeypatch.setattr(tokens, "contar", contar)
        return contar

    return instalar


@pytest.fixture
def sem_rede(monkeypatch):
    """Nenhum caso do pacote alcança a rede, nem por esquecimento (`FR-1519`).

    Os testes dos adaptadores substituem `urlopen` por cima deste, de propósito.
    """

    def recusar(*args, **kwargs):
        raise AssertionError("um teste do assistente tentou falar com a rede")

    monkeypatch.setattr(urllib.request, "urlopen", recusar)


class _Coletor(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.linhas = []

    def emit(self, record):
        self.linhas.append(self.format(record))


@pytest.fixture
def log_do_projeto():
    """O que o logger `processo_seletivo` escreve, inclusive exceções — onde o `caplog` não chega.

    O logger do projeto não propaga até a raiz (a configuração de `LOGGING`), e por isso o `caplog`
    fica vazio: uma verificação de "a credencial não está no log" passaria sem ler nada.
    """
    coletor = _Coletor()
    coletor.setFormatter(logging.Formatter("%(name)s %(message)s"))
    alvos = [logging.getLogger("processo_seletivo"), logging.getLogger()]
    niveis = [alvo.level for alvo in alvos]
    for alvo in alvos:
        alvo.addHandler(coletor)
        alvo.setLevel(logging.DEBUG)
    yield coletor.linhas
    for alvo, nivel in zip(alvos, niveis, strict=True):
        alvo.removeHandler(coletor)
        alvo.setLevel(nivel)
