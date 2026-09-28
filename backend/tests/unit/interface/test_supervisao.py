"""O catálogo de sinais é fechado, e o fechamento é executável.

`D-002` diz que sinal fora do catálogo não existe, e que acrescentar um é revisar a spec. Uma regra
que ninguém verifica é uma intenção: este teste é o que a torna cobrável.
"""

from processo_seletivo.interface import supervisao


def test_a_enumeracao_tem_exatamente_oito_especies():
    """`FR-744` (045): uma nona espécie quebra aqui, antes de chegar à tela — e uma a menos também.

    O número é escrito à mão de propósito. Derivá-lo da própria enumeração faria o teste concordar
    com qualquer tamanho — que é o oposto de fechar um catálogo.

    **O guarda já ficou vermelho três vezes, e as três por serviço prestado.** A sexta espécie
    chegou pela `027` — o `UX-046`. As quatro da `038` levaram a Atenção à cauda do certame:
    `UX-063`, `UX-064`, `UX-065` e `UX-066`. E a `045` **tirou duas**: o `UX-001`, a Etapa sem
    marco, que passou a aviso da validação do conteúdo, onde tem remédio; e o `UX-002`, que
    comparava o `status` declarado com o relógio, e deixou de ter o que comparar quando a fase
    passou a ser derivada. Fechar o catálogo nunca foi proibir que ele mude; foi exigir que mudar
    seja uma decisão escrita.

    **A `FR-024` da `022` dizia cinco enquanto o produto tinha seis**, porque a `027` não a revisou.
    A `038` a substituiu pela `FR-565`, e a `045` substituiu a `FR-565` pela `FR-744`.
    """
    assert len(supervisao.ESPECIES) == 8
    assert supervisao.ESPECIES == (
        supervisao.UX_003,
        supervisao.UX_004,
        supervisao.UX_005,
        supervisao.UX_046,
        supervisao.UX_063,
        supervisao.UX_064,
        supervisao.UX_065,
        supervisao.UX_066,
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
