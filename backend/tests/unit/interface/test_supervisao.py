"""O catálogo de sinais é fechado, e o fechamento é executável.

`D-002` diz que sinal fora dos cinco não existe, e que acrescentar um é revisar a spec. Uma regra
que ninguém verifica é uma intenção: este teste é o que a torna cobrável.
"""

from processo_seletivo.interface import supervisao


def test_a_enumeracao_tem_exatamente_cinco_especies():
    """`FR-024`: acrescentar uma sexta quebra aqui, antes de chegar à tela.

    O número é escrito à mão de propósito. Derivá-lo da própria enumeração faria o teste concordar
    com qualquer tamanho — que é o oposto de fechar um catálogo.
    """
    assert len(supervisao.ESPECIES) == 5
    assert supervisao.ESPECIES == (
        supervisao.UX_001,
        supervisao.UX_002,
        supervisao.UX_003,
        supervisao.UX_004,
        supervisao.UX_005,
    )


def test_nenhuma_especie_se_repete():
    assert len(set(supervisao.ESPECIES)) == len(supervisao.ESPECIES)


def test_o_sinal_nao_tem_campo_de_gravidade():
    """`D-002`: severidade pediria uma ordenação que o domínio não determina.

    Os cinco são igualmente acionáveis. Um campo de gravidade viraria juízo da tela — e o primeiro
    lugar onde ele apareceria é aqui, por conveniência de ordenar a região.
    """
    campos = {campo.name for campo in supervisao.Sinal.__dataclass_fields__.values()}

    assert "gravidade" not in campos
    assert "severidade" not in campos
