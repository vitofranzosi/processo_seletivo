"""A irmã de `ordenar` que devolve o caminho da partição (094, D-011).

Duas garantias. A primeira é a que autoriza a irmã a existir: **`ordenar` é ela sem as duas chaves
novas**, em toda entrada da tabela-verdade do desempate. A prova não copia a tabela — ela roda os
próprios testes de `test_desempate.py` e `test_numeracao_e_ausencia.py` com `ordenar` trocado por
um espião que confere a igualdade em cada chamada. Caso novo que entrar lá entra aqui também.

A segunda é a trajetória em si: o que ela registra quando um critério separa, quando não separa
por valores iguais e quando não se aplica por ausência.
"""

import inspect
import itertools
from decimal import Decimal

import pytest

from processo_seletivo.classificacao.domain import desempate
from processo_seletivo.classificacao.domain.desempate import ordenar, ordenar_com_trajetoria
from tests.unit.classificacao import test_desempate, test_numeracao_e_ausencia

FATO = "00000000-0000-0000-0000-0000000009f1"
OUTRO = "00000000-0000-0000-0000-0000000009f2"


def sem_trajetoria(item):
    return {
        chave: valor
        for chave, valor in item.items()
        if chave not in ("trajetoria", "grupo_da_pontuacao")
    }


def _casos_da_tabela_verdade(modulo):
    """Cada teste do módulo, com cada combinação dos seus `parametrize` — sem fixture nenhuma."""
    for nome, funcao in sorted(vars(modulo).items()):
        if not nome.startswith("test_") or not inspect.isfunction(funcao):
            continue
        marcas = [m for m in getattr(funcao, "pytestmark", []) if m.name == "parametrize"]
        if not marcas:
            yield nome, funcao, {}
            continue
        combinacoes = []
        for marca in marcas:
            nomes, valores = marca.args[0], marca.args[1]
            nomes = [item.strip() for item in nomes.split(",")] if isinstance(nomes, str) else nomes
            combinacoes.append(
                [
                    dict(zip(nomes, valor if len(nomes) > 1 else (valor,), strict=True))
                    for valor in valores
                ]
            )
        for produto in itertools.product(*combinacoes):
            argumentos = {}
            for parte in produto:
                argumentos.update(parte)
            yield nome, funcao, argumentos


@pytest.mark.parametrize(
    "modulo", [test_desempate, test_numeracao_e_ausencia], ids=["desempate", "numeracao"]
)
def test_ordenar_e_a_irma_sem_as_duas_chaves_em_toda_a_tabela_verdade(modulo, monkeypatch):
    chamadas = []

    def espiao(participantes, criterios):
        oficial = desempate.ordenar(participantes, criterios)
        irma = ordenar_com_trajetoria(participantes, criterios)
        assert oficial == [sem_trajetoria(item) for item in irma]
        chamadas.append(len(participantes))
        return oficial

    monkeypatch.setattr(modulo, "ordenar", espiao)
    conferidos = 0
    for nome, funcao, argumentos in _casos_da_tabela_verdade(modulo):
        antes = len(chamadas)
        funcao(**argumentos)
        # Sem isto, um caso que deixasse de passar pelo espião — `ordenar` importado por outro
        # caminho, por exemplo — faria o teste passar sem conferir nada.
        if "ordenar(" in inspect.getsource(funcao):
            assert len(chamadas) > antes, f"{nome} chama `ordenar` e o espião não a viu"
            conferidos += 1

    assert conferidos > 0


# --- a trajetória --------------------------------------------------------------------------------


def participante(nome, pontuacao="8", *, fato=None, outro=None):
    fatos = {}
    if fato is not None:
        fatos[FATO] = fato
    if outro is not None:
        fatos[OUTRO] = outro
    return {"nome": nome, "pontuacao": Decimal(pontuacao), "pontuacoes": {}, "fatos": fatos}


def criterio(ordem, tipo="MAIOR_VALOR_DE_FATO", *, fato=FATO, quando_ausente="ULTIMO_NO_CRITERIO"):
    return {
        "id": f"c{ordem}",
        "order": ordem,
        "type": tipo,
        "parameters": {"factId": fato},
        "whenMissing": quando_ausente,
    }


def caminho(item):
    """A trajetória legível: `(passo, id do critério, nomes do grupo)`."""
    return [
        (passo, criterio["id"], sorted(membro["nome"] for membro in grupo))
        for passo, criterio, grupo in item["trajetoria"]
    ]


def por_nome(resultado):
    return {item["nome"]: item for item in resultado}


def test_quem_esta_sozinho_na_pontuacao_nao_tem_trajetoria():
    resultado = por_nome(
        ordenar_com_trajetoria(
            [participante("a", "9"), participante("b", "8")], [criterio(1), criterio(2)]
        )
    )

    assert resultado["a"]["trajetoria"] == []
    assert [membro["nome"] for membro in resultado["a"]["grupo_da_pontuacao"]] == ["a"]


def test_o_criterio_que_particiona_e_registrado_como_separou():
    resultado = por_nome(
        ordenar_com_trajetoria(
            [participante("a", fato=1), participante("b", fato=2)], [criterio(1)]
        )
    )

    assert caminho(resultado["a"]) == [("separou", "c1", ["a", "b"])]
    assert caminho(resultado["b"]) == [("separou", "c1", ["a", "b"])]
    assert resultado["b"]["posicao"] == 1


def test_valores_iguais_nao_separam_e_o_proximo_criterio_e_oferecido():
    resultado = por_nome(
        ordenar_com_trajetoria(
            [participante("a", fato=1, outro=1), participante("b", fato=1, outro=2)],
            [criterio(1), criterio(2, fato=OUTRO)],
        )
    )

    assert caminho(resultado["a"]) == [
        ("nao_separou", "c1", ["a", "b"]),
        ("separou", "c2", ["a", "b"]),
    ]
    assert resultado["a"]["separado_por"]["id"] == "c2"


def test_criterio_que_nao_se_aplica_por_ausencia_e_registrado_como_nao_separou():
    resultado = por_nome(
        ordenar_com_trajetoria(
            [participante("a", fato=1, outro=1), participante("b", outro=2)],
            [criterio(1, quando_ausente="CRITERIO_NAO_SE_APLICA"), criterio(2, fato=OUTRO)],
        )
    )

    assert caminho(resultado["b"]) == [
        ("nao_separou", "c1", ["a", "b"]),
        ("separou", "c2", ["a", "b"]),
    ]


def test_a_trajetoria_segue_a_ordem_publicada_e_nao_a_da_lista():
    resultado = por_nome(
        ordenar_com_trajetoria(
            [participante("a", fato=1, outro=1), participante("b", fato=1, outro=2)],
            [criterio(2, fato=OUTRO), criterio(1)],
        )
    )

    assert [passo[1] for passo in caminho(resultado["a"])] == ["c1", "c2"]


def test_o_subgrupo_herda_o_caminho_e_recebe_so_os_criterios_seguintes():
    """O critério que já separou não é oferecido de novo ao subgrupo que ele produziu."""
    resultado = por_nome(
        ordenar_com_trajetoria(
            [
                participante("a", fato=2, outro=1),
                participante("b", fato=2, outro=1),
                participante("c", fato=1, outro=5),
            ],
            [criterio(1), criterio(2, fato=OUTRO)],
        )
    )

    assert caminho(resultado["a"]) == [
        ("separou", "c1", ["a", "b", "c"]),
        ("nao_separou", "c2", ["a", "b"]),
    ]
    assert resultado["a"]["empate_residual"] is True
    assert resultado["a"]["separado_por"]["id"] == "c1", "o último que separou o caminho dele"
    assert caminho(resultado["c"]) == [("separou", "c1", ["a", "b", "c"])]


def test_o_empate_residual_tem_todos_os_criterios_como_nao_separou():
    resultado = ordenar_com_trajetoria(
        [participante("a", fato=1), participante("b", fato=1)],
        [criterio(1), criterio(2, fato=OUTRO)],
    )

    assert [caminho(item) for item in resultado] == [
        [("nao_separou", "c1", ["a", "b"]), ("nao_separou", "c2", ["a", "b"])]
    ] * 2
    assert all(item["separado_por"] is None for item in resultado)


def test_o_grupo_da_pontuacao_e_o_dos_empatados_na_combinada():
    resultado = por_nome(
        ordenar_com_trajetoria(
            [
                participante("a", "9", fato=1),
                participante("b", "8", fato=2),
                participante("c", "8", fato=1),
            ],
            [criterio(1)],
        )
    )

    assert [membro["nome"] for membro in resultado["c"]["grupo_da_pontuacao"]] == ["b", "c"]
    assert [membro["nome"] for membro in resultado["a"]["grupo_da_pontuacao"]] == ["a"]


def test_ordenar_nao_carrega_as_chaves_da_trajetoria():
    """A saída de `ordenar` chega ao ato; o caminho da partição é só da prévia."""
    (item,) = ordenar([participante("a")], [criterio(1)])

    assert "trajetoria" not in item
    assert "grupo_da_pontuacao" not in item
