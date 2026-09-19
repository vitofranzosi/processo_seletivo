"""A composição e o motor respondem **a mesma coisa** sobre a forma da ocorrência (035, SC-177).

**Este arquivo compara respostas, e não implementações.** A `FR-515` proíbe que a conferência da
composição reimplemente a regra que o motor aplica, e a razão é o tamanho dela: *termina em número*
cabe numa linha, e copiá-la custa menos do que importá-la. Uma cópia não quebra nada no dia em que
é escrita — ela diverge na primeira vez que uma das duas mudar, e a divergência aparece do pior
jeito possível: a composição aceitando o que o sorteio recusa, com o Edital já publicado.

Ler as duas implementações e concluir que dizem o mesmo é justamente o que não prova nada. O que
prova é passar o mesmo conjunto de referências pelas duas portas e exigir que os desfechos
coincidam — que é o que `test_a_consulta_e_a_derivacao_nunca_discordam` faz, referência a
referência.
"""

import pytest

from processo_seletivo.shared.api.problems import DomainError
from processo_seletivo.sorteios.domain import substituicao

#: As referências que a regra publicada **sabe** derivar, e o que ela deriva de cada uma.
#:
#: `0099` está aqui porque a quantidade de dígitos é preservada, e é a forma que a fonte real usa
#: quando o concurso ainda não chegou a cinco casas. `Concurso 5900` está porque o prefixo é
#: preservado, e é a forma que um Edital escreve quando nomeia o concurso por extenso.
DERIVAVEIS = [
    ("5900", "5901"),
    ("Concurso 5900", "Concurso 5901"),
    ("0099", "0100"),
    ("6100", "6101"),
    ("9", "10"),
]

#: As que ela **não** sabe derivar. A primeira é a forma que uma pessoa escreve — e é literalmente
#: a que três fixtures deste repositório tinham (`research.md` `R-6`): o número está lá, e só não
#: está onde a regra o procura, porque a fonte foi repetida depois dele.
NAO_DERIVAVEIS = [
    "concurso 6100 da Loteria Federal",
    "concurso 6100 de 2026 da Caixa",
    "a extração de sábado anterior ao sorteio",
    "",
    "Concurso",
]


@pytest.mark.parametrize("referencia,seguinte", DERIVAVEIS)
def test_a_consulta_aceita_o_que_a_derivacao_deriva(referencia, seguinte):
    assert substituicao.derivavel(referencia) is True
    assert substituicao.REGRAS[substituicao.OCORRENCIA_SEGUINTE_DA_MESMA_FONTE](referencia) == (
        seguinte
    )


@pytest.mark.parametrize("referencia", NAO_DERIVAVEIS)
def test_a_consulta_recusa_o_que_a_derivacao_recusa(referencia):
    assert substituicao.derivavel(referencia) is False


@pytest.mark.parametrize("referencia", [r for r, _ in DERIVAVEIS] + NAO_DERIVAVEIS)
def test_a_consulta_e_a_derivacao_nunca_discordam(referencia):
    """O `SC-177`, dito como comparação: a mesma referência, as duas portas, o mesmo desfecho.

    Se alguém reimplementar a forma na composição, é aqui que aparece — e aparece antes de um
    Edital ser publicado sobre a divergência.
    """
    try:
        substituicao.REGRAS[substituicao.OCORRENCIA_SEGUINTE_DA_MESMA_FONTE](referencia)
    except DomainError:
        derivou = False
    else:
        derivou = True

    assert substituicao.derivavel(referencia) is derivou


def test_a_recusa_da_derivacao_traz_o_codigo_que_distingue_a_causa():
    """A tela do sorteio precisa separar *não soube derivar* de *a fonte não publicou* (FR-516).

    O código é o que distingue as duas, e ele tem nome de módulo justamente para que quem
    distingue não repita a string.
    """
    with pytest.raises(DomainError) as recusa:
        substituicao.REGRAS[substituicao.OCORRENCIA_SEGUINTE_DA_MESMA_FONTE](
            "concurso 6100 da Loteria Federal"
        )

    assert recusa.value.code == substituicao.RECUSA_POR_FORMA_DA_REFERENCIA
    assert "deriva do número" in recusa.value.detail


def test_regra_fora_do_vocabulario_responde_que_nao_deriva_e_nao_estoura():
    """Quem recusa a regra não publicada é `regra_publicada`, e a consulta não duplica a recusa."""
    assert substituicao.derivavel("5900", regra="REGRA_QUE_NINGUEM_PUBLICOU") is False


def test_a_cadeia_inteira_segue_da_declarada():
    """A consulta responde sobre a declarada, e a cadeia toda segue dela — não há meio-termo."""
    metodo = {
        "occurrence": "5900",
        "substitutionRule": {"rule": substituicao.OCORRENCIA_SEGUINTE_DA_MESMA_FONTE},
    }

    assert substituicao.derivavel(metodo["occurrence"]) is True
    assert substituicao.cadeia(metodo) == ["5900", "5901", "5902", "5903", "5904", "5905"]
