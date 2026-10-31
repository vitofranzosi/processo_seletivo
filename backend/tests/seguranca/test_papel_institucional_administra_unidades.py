"""O Administrador institucional também administra unidades — o mesmo papel, renomeado (110, D-002).

Nenhum papel novo, nenhuma opção nova nos comandos de implantação: o que muda é uma permissão e um
rótulo. O resto da `106` e da `107` — a concessão só pela implantação, a recusa pela tela, a
suspensão — fica como estava, e os testes delas passam sem mudança.
"""

import pytest
from django.core.management import call_command
from django.utils import timezone

from processo_seletivo.seguranca.acessos import (
    ADMINISTRADOR_INSTITUCIONAL,
    ESCOPO_INSTITUCIONAL,
    PAPEIS_INSTITUCIONAIS,
)
from processo_seletivo.seguranca.application import acessos
from processo_seletivo.seguranca.domain import Actor
from processo_seletivo.shared.api.problems import DomainError
from tests.seguranca.apoio import ator_do_cliente, entrar, pessoa

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_o_papel_institucional_tem_as_duas_permissoes_e_o_rotulo_novo():
    """FR-3308."""
    rotulo, permissoes = PAPEIS_INSTITUCIONAIS[ADMINISTRADOR_INSTITUCIONAL]

    assert rotulo == "Administrador institucional"
    assert set(permissoes) == {"acesso:administrar", "unidade:administrar"}
    assert list(PAPEIS_INSTITUCIONAIS) == [ADMINISTRADOR_INSTITUCIONAL], "nenhum papel novo"


def test_concedido_pelo_comando_de_sempre_alcanca_as_duas_capacidades(client, provedor):
    """FR-3310: o comando não mudou, e a pessoa entra com as duas permissões."""
    call_command(
        "conceder_administracao_institucional",
        "--provedor",
        provedor.NOME,
        "--identificador",
        "ines",
        "--nome",
        "Inês",
        "--motivo",
        "Portaria nº 1/2026",
    )

    entrar(client, "ines", nome="Inês")
    ator = ator_do_cliente(client)

    assert ator.institution_scope == ESCOPO_INSTITUCIONAL
    assert ator.can("acesso:administrar") and ator.can("unidade:administrar")


def test_a_aplicacao_continua_recusando_conceder_o_papel():
    """FR-3339, EC-18: a permissão nova não abre esse caminho."""
    administradora = Actor(
        "pessoa-administradora",
        ESCOPO_INSTITUCIONAL,
        frozenset({"acesso:administrar", "unidade:administrar"}),
    )
    with pytest.raises(DomainError) as recusa:
        acessos.conceder(
            administradora,
            pessoa=pessoa("outra"),
            escopo=ESCOPO_INSTITUCIONAL,
            papel=ADMINISTRADOR_INSTITUCIONAL,
            motivo="Tentativa",
            now=timezone.now(),
        )
    assert recusa.value.code == acessos.PAPEL_SO_POR_IMPLANTACAO
