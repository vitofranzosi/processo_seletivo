"""Quem habilita o assistente: o Administrador institucional, e só ele (170).

A matriz de quem **não** pode, em cada caso de uso, chamado sem tela (FR-7511, SC-2454): a recusa
é da aplicação, e a tela é a segunda barreira. E a permissão não abre nada além disto (FR-7512).
"""

import pytest

from processo_seletivo.duvidas.application import habilitacao
from processo_seletivo.duvidas.domain import habilitacao as nomes
from processo_seletivo.duvidas.models import HabilitacaoDoAssistente
from processo_seletivo.interface import identidade
from processo_seletivo.seguranca.acessos import (
    ADMINISTRADOR_INSTITUCIONAL,
    ESCOPO_INSTITUCIONAL,
    PAPEIS_DE_ACESSO,
    PAPEIS_INSTITUCIONAIS,
)
from processo_seletivo.seguranca.application.acessos import catalogo
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError

pytestmark = [pytest.mark.django_db, pytest.mark.authorization]


def _atores_sem_a_base():
    """Todo papel do sistema que não é o institucional, no escopo onde ele age; mais os dois casos
    do institucional fora do lugar: a permissão em escopo de unidade, e o escopo sem ela."""
    atores = {}
    for papel, (_, permissoes) in identidade.PAPEIS.items():
        atores[papel] = Actor(f"pessoa-{papel}", "cefor", frozenset(permissoes))
    for papel, (_, permissoes) in PAPEIS_DE_ACESSO.items():
        atores[papel] = Actor(f"pessoa-{papel}", "cefor", frozenset(permissoes))
    atores["institucional-em-unidade"] = Actor(
        "pessoa-institucional", "cefor", frozenset({nomes.HABILITAR})
    )
    atores["institucional-so-de-unidades"] = Actor(
        "pessoa-unidades", ESCOPO_INSTITUCIONAL, frozenset({"unidade:administrar"})
    )
    return atores


ATORES = _atores_sem_a_base()

CASOS = {
    "ler": lambda ator: habilitacao.ler(ator),
    "conferir": lambda ator: habilitacao.conferir(ator, frente=nomes.PILOTO, habilitar=True),
    "habilitar": lambda ator: habilitacao.habilitar(ator, frente=nomes.PILOTO, motivo="x"),
    "desabilitar": lambda ator: habilitacao.desabilitar(ator, frente=nomes.PILOTO, motivo="x"),
}


@pytest.mark.parametrize("papel", sorted(ATORES))
@pytest.mark.parametrize("caso", sorted(CASOS))
def test_cada_caso_de_uso_recusa_sem_a_permissao(papel, caso):
    """FR-7511, SC-2454: recusa explicada (403), antes de ler ou gravar."""
    with pytest.raises(DomainError) as recusa:
        CASOS[caso](ATORES[papel])

    assert (recusa.value.code, recusa.value.status) == ("forbidden", 403)
    assert not HabilitacaoDoAssistente.objects.exists()


def test_a_grafia_da_permissao_e_a_mesma():
    """`seguranca/acessos.py` a escreve por extenso, como o `PAPEIS` escreve as dele."""
    assert nomes.HABILITAR == "assistente:habilitar"
    assert nomes.HABILITAR in PAPEIS_INSTITUCIONAIS[ADMINISTRADOR_INSTITUCIONAL][1]


def test_nenhum_outro_papel_tem_a_permissao():
    """FR-7510: nem papel de unidade, nem papel do seletor de demonstração."""
    com_a_permissao = [
        papel for papel, (_, permissoes) in catalogo().items() if nomes.HABILITAR in permissoes
    ]
    assert com_a_permissao == [ADMINISTRADOR_INSTITUCIONAL]


def test_a_permissao_nao_da_o_uso_do_piloto():
    """FR-7512: habilitar não é conversar — o papel do piloto continua à parte."""
    assert "assistente:piloto" not in PAPEIS_INSTITUCIONAIS[ADMINISTRADOR_INSTITUCIONAL][1]
