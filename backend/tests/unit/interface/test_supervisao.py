"""O catálogo de sinais é fechado, e o fechamento é executável.

`D-002` diz que sinal fora do catálogo não existe, e que acrescentar um é revisar a spec. Uma regra
que ninguém verifica é uma intenção: este teste é o que a torna cobrável.
"""

from processo_seletivo.interface import supervisao


def test_a_enumeracao_tem_exatamente_dez_especies():
    """`FR-565`: acrescentar uma décima primeira quebra aqui, antes de chegar à tela.

    O número é escrito à mão de propósito. Derivá-lo da própria enumeração faria o teste concordar
    com qualquer tamanho — que é o oposto de fechar um catálogo.

    **O guarda já ficou vermelho duas vezes, e as duas por serviço prestado.** A sexta chegou pela
    `027` — o `UX-046`, do acervo que publica vaga imediata e não publica a linha do quadro. As
    quatro desta leva são da `038`, e levam a Atenção à cauda do certame: `UX-063`, avaliação
    distribuída e não concluída; `UX-064`, recurso aguardando julgamento com julgador disponível;
    `UX-065`, recorte com ordem vigente e ocupação não apurada; `UX-066`, ato de ordenação vigente
    sem divulgação vigente. Fechar o catálogo nunca foi proibir que ele cresça; foi exigir que
    crescer seja uma decisão escrita.

    **A `FR-024` da `022` dizia cinco enquanto o produto tinha seis**, porque a `027` não a
    revisou. Quem a substitui é a `FR-565`, e é por ela que este teste passa a citar.
    """
    assert len(supervisao.ESPECIES) == 10
    assert supervisao.ESPECIES == (
        supervisao.UX_001,
        supervisao.UX_002,
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
