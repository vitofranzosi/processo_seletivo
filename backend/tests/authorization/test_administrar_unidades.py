"""Quem administra o registro de Unidades: o Administrador institucional, e só ele (110).

A matriz de quem **não** pode, em cada caso de uso, chamado sem tela (FR-3309, SC-1043): a recusa é
da aplicação, e a tela é a segunda barreira. E a permissão não abre nada além do registro
(FR-3310).
"""

import pytest

from processo_seletivo.interface import identidade
from processo_seletivo.seguranca.acessos import (
    ADMINISTRADOR_INSTITUCIONAL,
    ESCOPO_INSTITUCIONAL,
    PAPEIS_DE_ACESSO,
    PAPEIS_INSTITUCIONAIS,
)
from processo_seletivo.seguranca.application.acessos import catalogo, permissoes_dos_papeis
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.unidades.application import registro
from processo_seletivo.unidades.domain import nomes
from processo_seletivo.unidades.models import Unidade

pytestmark = [pytest.mark.django_db, pytest.mark.authorization]

SERRA = {
    "codigo": "serra",
    "sigla": "Serra",
    "nome": "Campus Serra",
    "cabecalho": ["Campus Serra"],
    "local": "Serra (ES)",
}
EDITAVEIS = {k: v for k, v in SERRA.items() if k != "codigo"}


def _atores_sem_a_base():
    """Todo papel do sistema que não é o institucional, no escopo onde ele age; mais os dois casos
    do institucional fora do lugar: a permissão em escopo de unidade (EC-8), e o escopo sem ela."""
    atores = {}
    for papel, (_, permissoes) in identidade.PAPEIS.items():
        atores[papel] = Actor(f"pessoa-{papel}", "cefor", frozenset(permissoes))
    for papel, (_, permissoes) in PAPEIS_DE_ACESSO.items():
        atores[papel] = Actor(f"pessoa-{papel}", "cefor", frozenset(permissoes))
    atores["institucional-em-unidade"] = Actor(
        "pessoa-institucional", "cefor", frozenset({nomes.ADMINISTRAR})
    )
    atores["institucional-so-de-acessos"] = Actor(
        "pessoa-acessos", ESCOPO_INSTITUCIONAL, frozenset({"acesso:administrar"})
    )
    return atores


ATORES = _atores_sem_a_base()

CASOS = {
    "listar": lambda ator: registro.listar(ator),
    "ficha": lambda ator: registro.ficha(ator, codigo="cefor"),
    "conferir_registro": lambda ator: registro.conferir_registro(ator, campos=SERRA),
    "registrar": lambda ator: registro.registrar(ator, campos=SERRA, motivo="x"),
    "conferir_alteracao": lambda ator: registro.conferir_alteracao(
        ator, codigo="cefor", campos={**EDITAVEIS, "nome": "Outro"}
    ),
    "alterar": lambda ator: registro.alterar(
        ator, codigo="cefor", campos={**EDITAVEIS, "nome": "Outro"}, versao="", motivo="x"
    ),
    "consequencias": lambda ator: registro.consequencias(ator, codigo="cefor", ato="desativar"),
    "desativar": lambda ator: registro.desativar(ator, codigo="cefor", versao="", motivo="x"),
    "reativar": lambda ator: registro.reativar(ator, codigo="cefor", versao="", motivo="x"),
}


@pytest.mark.parametrize("papel", sorted(ATORES))
@pytest.mark.parametrize("caso", sorted(CASOS))
def test_cada_caso_de_uso_recusa_sem_a_permissao(papel, caso):
    """FR-3309, FR-3311, EC-8, SC-1043: recusa explicada (403), antes de ler ou gravar."""
    antes = list(Unidade.objects.values_list("codigo", "nome", "ativa"))

    with pytest.raises(DomainError) as recusa:
        CASOS[caso](ATORES[papel])

    assert (recusa.value.code, recusa.value.status) == ("forbidden", 403)
    assert list(Unidade.objects.values_list("codigo", "nome", "ativa")) == antes


def test_papel_de_unidade_e_recusado_inclusive_na_propria():
    """FR-3311, decisão de produto 4: nenhuma unidade altera o próprio cadastro."""
    gestor_do_cefor = Actor(
        "pessoa-gestor", "cefor", frozenset(identidade.PAPEIS["gestor"][1]) | {nomes.ADMINISTRAR}
    )
    with pytest.raises(DomainError):
        CASOS["alterar"](gestor_do_cefor)


def test_a_grafia_da_permissao_e_a_mesma():
    """`seguranca/acessos.py` a escreve por extenso, como o `PAPEIS` escreve as dele."""
    assert nomes.ADMINISTRAR == "unidade:administrar"
    assert nomes.ADMINISTRAR in PAPEIS_INSTITUCIONAIS[ADMINISTRADOR_INSTITUCIONAL][1]


def test_nenhum_outro_papel_tem_a_permissao():
    """FR-3308: nem papel de unidade, nem papel do seletor de demonstração."""
    com_a_permissao = [
        papel for papel, (_, permissoes) in catalogo().items() if nomes.ADMINISTRAR in permissoes
    ]
    assert com_a_permissao == [ADMINISTRADOR_INSTITUCIONAL]


def test_a_permissao_nao_abre_processo_edital_nem_acesso():
    """FR-3310: o Administrador institucional não conduz certame nem concede papel de unidade."""
    permissoes = permissoes_dos_papeis([ADMINISTRADOR_INSTITUCIONAL])

    assert permissoes == {"acesso:administrar", nomes.ADMINISTRAR}
    assert not {p for p in permissoes if p.split(":")[0] in {"processo", "edital", "resultado"}}
