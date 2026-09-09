"""A chave recebe cinco campos, e não há sexto (FR-024).

Este é o teste que ataca a fresta que a feature existe para fechar: um valor escolhido por alguém
**depois** do congelamento entrando na chave. A defesa não é uma validação — é a assinatura da
função, que não tem `**kwargs` nem dicionário de extras —, e o teste prova que a defesa é essa
mesma, e não uma checagem que alguém possa remover sem quebrar nada.
"""

import inspect

import pytest

from processo_seletivo.sorteios.domain import chave as K

ENTRADAS = {
    "relation_hash": "a" * 64,
    "draw_scope_id": "perfil-1",
    "seed": "0 4 8 1 5",
    "public_number": 1,
}


def test_a_assinatura_e_fechada_e_so_por_palavra_chave():
    parametros = inspect.signature(K.chave).parameters
    assert set(parametros) == set(ENTRADAS)
    assert all(p.kind is inspect.Parameter.KEYWORD_ONLY for p in parametros.values())
    assert not any(
        p.kind in (inspect.Parameter.VAR_KEYWORD, inspect.Parameter.VAR_POSITIONAL)
        for p in parametros.values()
    )


def test_campo_extra_nao_entra_na_chave():
    with pytest.raises(TypeError):
        K.chave(**ENTRADAS, favorito=7)


def test_os_bytes_canonicos_tem_exatamente_as_cinco_chaves():
    import json

    corpo = json.loads(K.bytes_canonicos(**ENTRADAS).decode("utf-8"))
    assert sorted(corpo) == ["domain", "drawScopeId", "publicNumber", "relationHash", "seed"]
    assert corpo["domain"] == K.DOMINIO


@pytest.mark.parametrize("campo", sorted(ENTRADAS))
def test_alterar_qualquer_entrada_muda_o_resumo(campo):
    base = K.chave(**ENTRADAS)
    alteradas = dict(ENTRADAS)
    alteradas[campo] = 2 if campo == "public_number" else ENTRADAS[campo] + "x"
    assert K.chave(**alteradas) != base


def test_a_mesma_entrada_produz_sempre_o_mesmo_resumo():
    assert K.chave(**ENTRADAS) == K.chave(**ENTRADAS)
    assert len(K.chave(**ENTRADAS)) == 64
