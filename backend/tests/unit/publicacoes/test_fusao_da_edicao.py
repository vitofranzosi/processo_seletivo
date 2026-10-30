"""A fusão da edição de uma Retificação, caso a caso (103, R-006, FR-2718, FR-2719).

Função pura sobre conteúdo. O que se prende aqui é o que erraria em silêncio: a Alteração gravada
que a edição não tocou e sumisse; a tocada que ficasse com o valor antigo; a que volta ao vigente e
continuasse no ato; o acréscimo removido que virasse remoção de algo que nunca existiu; e a fusão
que gravasse um ato diferente do conferido.
"""

import pytest

from processo_seletivo.publicacoes.domain import fusao
from processo_seletivo.publicacoes.domain.fusao import FusaoInconsistente, fundir
from tests.unit.publicacoes.test_aplicacao_na_retificacao import _id, _perfil

P1, P2, P3 = _id("p", 1), _id("p", 2), _id("p", 3)


@pytest.fixture
def base():
    return {"profiles": [_perfil(1), _perfil(2)]}


def nome(perfil, valor):
    return {"targetPath": f"/profiles/id={perfil}/name", "operation": "REPLACE", "newValue": valor}


def acrescimo(n):
    return {"targetPath": "/profiles/-", "operation": "ADD", "newValue": _perfil(n)}


def remocao(perfil):
    return {"targetPath": f"/profiles/id={perfil}", "operation": "REMOVE"}


def nomes(conteudo):
    return {perfil["id"]: perfil["name"] for perfil in conteudo["profiles"]}


def test_sem_diferenca_o_ato_e_o_mesmo(base):
    existentes = [nome(P1, "Novo 1"), acrescimo(3), remocao(P2)]

    fundidas, _ = fundir(base, existentes, [])

    assert fundidas == existentes


def test_a_alteracao_intocada_continua_e_a_nova_entra_depois(base):
    fundidas, conferido = fundir(base, [nome(P1, "Novo 1")], [nome(P2, "Novo 2")])

    assert fundidas == [nome(P1, "Novo 1"), nome(P2, "Novo 2")]
    assert nomes(conferido) == {P1: "Novo 1", P2: "Novo 2"}


def test_a_alteracao_tocada_passa_a_ter_o_valor_novo_sem_duplicar(base):
    fundidas, _ = fundir(base, [nome(P1, "Novo 1")], [nome(P1, "Outro 1")])

    assert fundidas == [nome(P1, "Outro 1")]


def test_a_que_volta_ao_vigente_sai_do_ato(base):
    fundidas, conferido = fundir(base, [nome(P1, "Novo 1")], [nome(P1, "Perfil 1")])

    assert fundidas == []
    assert conferido == base


def test_o_acrescimo_editado_leva_o_campo_novo_dentro_dele(base):
    fundidas, conferido = fundir(base, [acrescimo(3)], [nome(P3, "Terceiro")])

    assert len(fundidas) == 1
    assert fundidas[0]["targetPath"] == "/profiles/-"
    assert fundidas[0]["newValue"]["name"] == "Terceiro"
    assert nomes(conferido)[P3] == "Terceiro"


def test_o_acrescimo_removido_sai_sem_virar_remocao(base):
    fundidas, conferido = fundir(base, [acrescimo(3), nome(P1, "Novo 1")], [remocao(P3)])

    assert fundidas == [nome(P1, "Novo 1")]
    assert P3 not in nomes(conferido)


def test_remover_o_que_tinha_alteracao_leva_a_alteracao_junto(base):
    fundidas, _ = fundir(base, [nome(P2, "Novo 2")], [remocao(P2)])

    assert fundidas == [remocao(P2)]


def test_a_remocao_desfeita_sai_do_ato(base):
    fundidas, conferido = fundir(base, [nome(P1, "Novo 1"), remocao(P2)], [], desfeitas=[1])

    assert fundidas == [nome(P1, "Novo 1")]
    assert P2 in nomes(conferido)


def test_desfazer_so_vale_para_remocao(base):
    """O índice de uma substituição nas desfeitas não a apaga: só remoção se desfaz pela lista."""
    fundidas, _ = fundir(base, [nome(P1, "Novo 1")], [], desfeitas=[0])

    assert fundidas == [nome(P1, "Novo 1")]


def test_o_caminho_da_entidade_acrescentada_e_o_seletor_da_chave():
    assert fusao.caminho_da_entidade(acrescimo(3)) == f"/profiles/id={P3}"
    assert fusao.caminho_da_entidade(nome(P1, "x")) == f"/profiles/id={P1}/name"


def test_a_diferenca_que_nao_se_aplica_ao_proposto_e_recusada(base):
    with pytest.raises(ValueError):
        fundir(base, [remocao(P2)], [nome(P2, "Fantasma")])


def test_a_fusao_que_nao_reproduz_o_conferido_e_recusada(base, monkeypatch):
    """A rede de segurança: se a regra sobre caminhos errar, nada é gravado."""
    original = fusao.aplicar
    chamadas = []

    def aplicar_que_diverge(conteudo, alteracoes):
        chamadas.append(1)
        resultado = original(conteudo, alteracoes)
        if len(chamadas) == 3:  # proposto, conferido, e a conferência final
            resultado["profiles"][0]["name"] = "outra coisa"
        return resultado

    monkeypatch.setattr(fusao, "aplicar", aplicar_que_diverge)

    with pytest.raises(FusaoInconsistente):
        fundir(base, [nome(P1, "Novo 1")], [nome(P2, "Novo 2")])
