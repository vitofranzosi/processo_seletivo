"""O que cada fonte diz publicar é o que o adaptador dela devolve (102, FR-2647–FR-2649, FR-2665).

**Por que a declaração e o adaptador são conferidos um contra o outro.** A regra da publicação lê a
declaração ("esta fonte publica só a data") e não chama a fonte; o sorteio lê o que o adaptador
devolveu. Se as duas divergirem, a publicação recusa um Edital que sortearia, ou deixa passar um
que nunca sorteará — o Edital 72/2026 de novo, agora com o sistema afirmando que avisou.
"""

import io
import json
from datetime import datetime, time

import pytest
from django.test import override_settings
from django.utils import timezone

from processo_seletivo.shared.tempo import ZONA
from processo_seletivo.sorteios.infrastructure.fontes import (
    fonte_declarada,
    fontes_publicadas,
    loteria_federal,
    publica_so_a_data,
)

SO_A_DATA = "Fonte de demonstração (só a data)"


class _RespostaDaCaixa(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


@pytest.fixture
def caixa(monkeypatch):
    """A Caixa sem rede: `dataApuracao` como ela publica, data sem horário."""
    corpo = {"listaDezenas": ["012345", "678901", "234567", "890123", "456789"]}
    corpo["dataApuracao"] = "28/10/2026"

    def responder(endereco, timeout):
        return _RespostaDaCaixa(json.dumps(corpo).encode("utf-8"))

    monkeypatch.setattr(loteria_federal.request, "urlopen", responder)


def _meia_noite(instante):
    local = timezone.localtime(instante, ZONA)
    return local.time() == time.min


@pytest.mark.usefixtures("caixa")
@pytest.mark.parametrize("nome", sorted(fontes_publicadas()))
def test_a_declaracao_de_cada_fonte_bate_com_o_que_o_adaptador_devolve(nome):
    observacao = fonte_declarada(nome).observar(fonte=nome, referencia="6113")

    assert observacao.material_bruto
    if publica_so_a_data(nome):
        assert _meia_noite(observacao.ocorrida_nao_antes_de), nome
    else:
        # A fonte com horário devolve um instante que **não é, por construção**, o início do dia: a
        # de demonstração devolve agora. Agora pode cair à meia-noite exata, e por isso o teste
        # confere a construção, e não o relógio.
        agora = timezone.now()
        assert abs((observacao.ocorrida_nao_antes_de - agora).total_seconds()) < 60, nome


def test_a_loteria_federal_publica_so_a_data():
    assert publica_so_a_data("Loteria Federal") is True


def test_a_demonstracao_atual_publica_a_hora():
    """FR-2648, D-006: é ela que a suíte e o `seed_demo` usam, e por isso eles não mudam."""
    assert publica_so_a_data("Fonte de demonstração") is False


def test_a_demonstracao_so_a_data_devolve_o_inicio_do_dia_corrente():
    """FR-2665: congelar e sortear no mesmo dia reproduz a recusa do servidor, sem rede."""
    observacao = fonte_declarada(SO_A_DATA).observar(fonte=SO_A_DATA, referencia="6113")

    hoje = timezone.localdate(timezone.now(), ZONA)
    assert observacao.ocorrida_nao_antes_de == datetime.combine(hoje, time.min, tzinfo=ZONA)
    assert publica_so_a_data(SO_A_DATA) is True
    assert (
        observacao.material_bruto
        == fonte_declarada("Fonte de demonstração")
        .observar(fonte="Fonte de demonstração", referencia="6113")
        .material_bruto
    ), "o material é o da demonstração atual"


def test_fonte_fora_do_vocabulario_nao_tem_granularidade():
    """Quem acusa a fonte desconhecida é a conferência de fonte; esta pergunta se cala."""
    assert publica_so_a_data("Random.org") is None


@override_settings(SORTEIO_FONTE_DE_DEMONSTRACAO=False)
def test_em_producao_nenhuma_das_duas_demonstracoes_existe():
    """FR-2666: a chave que produção recusa ligar é a mesma para as duas."""
    assert set(fontes_publicadas()) == {"Loteria Federal"}
    assert publica_so_a_data(SO_A_DATA) is None
    assert publica_so_a_data("Fonte de demonstração") is None
