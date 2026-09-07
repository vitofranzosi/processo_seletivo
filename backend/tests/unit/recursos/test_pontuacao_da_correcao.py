"""A pontuação que o julgador fixa passa pela **mesma** validação que a do avaliador (FR-059).

A revisão do PR encontrou a assimetria: `avaliacoes/domain/pontuacao.py` recusa negativo,
`Infinity`, `NaN`, casas em excesso, estouro da coluna e a máxima publicada — e a correção fixada
por recurso só recusava o que `Decimal()` não construía.

O efeito é o mesmo Resultado, gravado pela mesma coluna e lido pela mesma classificação. Duas
validações diferentes para o mesmo campo produzem, mais cedo ou mais tarde, um Resultado que uma
porta aceitou e a outra recusaria — e é a porta do recurso que grava sob decisão irreversível.

```text
o avaliador conclui 8,5  →  normalizar + máxima publicada
o julgador corrige  8,5  →  a MESMA coisa, e é o que faltava
```
"""

from decimal import Decimal

import pytest

from processo_seletivo.recursos.domain.consequencia import derivar
from processo_seletivo.shared.api.problems import DomainError


class VersaoFalsa:
    """A versão citada pela decisão, reduzida ao que `etapa_publicada` lê."""

    def __init__(self, etapa):
        self.content = {"stages": [etapa]}


ETAPA_ID = "11111111-1111-4111-8111-111111111111"


def versao(**alteracoes):
    etapa = {
        "id": ETAPA_ID,
        "name": "Prova didática",
        "forma": "PONTUADA",
        "weight": "1.0000",
        "minimumScore": "6.0000",
        "maximumScore": "10.0000",
        "eliminatory": True,
        "classificatory": True,
        **alteracoes,
    }
    return VersaoFalsa(etapa)


def corrigir(pontuacao, **alteracoes):
    return derivar(versao=versao(**alteracoes), etapa_id=ETAPA_ID, pontuacao=pontuacao)


@pytest.mark.parametrize(
    ("valor", "trecho"),
    [
        ("-1", "não pode ser negativa"),
        ("Infinity", "precisa ser um número"),
        ("-Infinity", "precisa ser um número"),
        ("NaN", "precisa ser um número"),
        ("sNaN", "precisa ser um número"),
        ("1E+100", "máximo que o registro comporta"),
        ("8.00001", "quatro casas decimais"),
        ("oitenta", "precisa ser um número"),
        ("10.0001", "máxima publicada"),
        ("999.9999", "máxima publicada"),
    ],
)
def test_a_correcao_recusa_o_que_a_avaliacao_recusaria(valor, trecho):
    with pytest.raises(DomainError) as recusa:
        corrigir(valor)

    assert trecho in recusa.value.detail
    assert recusa.value.status == 422


def test_sem_maxima_publicada_o_teto_e_o_da_coluna():
    """Não declarada é "o Edital não disse", e não "sem limite" — a mesma leitura da 013."""
    _efeito, _motivo, conclusao = corrigir("500.0000", maximumScore=None)
    assert conclusao.pontuacao == Decimal("500.0000")

    with pytest.raises(DomainError) as recusa:
        corrigir("1000", maximumScore=None)
    assert "máximo que o registro comporta" in recusa.value.detail


def test_a_pontuacao_valida_atravessa_normalizada():
    """A vírgula **não** chega até aqui: traduzi-la é trabalho da interface, e o domínio recebe
    número. Cobrir os dois separadores no domínio faria a regra do país virar regra de negócio."""
    _efeito, _motivo, conclusao = corrigir("8.5")

    assert conclusao.pontuacao == Decimal("8.5")


@pytest.mark.parametrize("vazio", [None, "", "   "])
def test_a_ausencia_continua_sendo_recusa_de_correcao_incompleta(vazio):
    """Não é pontuação inválida: é decisão que saiu pela metade, e a mensagem precisa dizer isso.

    A diferença importa para quem lê: "Informe a pontuação" é o que a Avaliação diz a quem está
    preenchendo um formulário; aqui quem lê é o julgador, e o que falta é a **conclusão** que a
    forma da Etapa exige — o campo vazio e o campo ausente são o mesmo caso.
    """
    with pytest.raises(DomainError) as recusa:
        derivar(versao=versao(), etapa_id=ETAPA_ID, pontuacao=vazio)

    assert recusa.value.code == "appeal_correction_incomplete"
    assert "precisa fixar a pontuação" in recusa.value.detail


@pytest.mark.parametrize("bruto", ["FAVORAVEL", "DESFAVORAVEL"])
def test_o_sentido_da_decisoria_passa_pelo_mesmo_normalizador(bruto):
    _efeito, _motivo, conclusao = derivar(
        versao=versao(forma="DECISORIA", minimumScore=None, maximumScore=None),
        etapa_id=ETAPA_ID,
        sentido=bruto,
    )

    assert conclusao.sentido == bruto


def test_o_sentido_invalido_e_recusado_em_vez_de_gravado():
    """Antes, qualquer texto virava sentido — inclusive o **rótulo publicado** que a tela mostra."""
    with pytest.raises(DomainError) as recusa:
        derivar(
            versao=versao(forma="DECISORIA", minimumScore=None, maximumScore=None),
            etapa_id=ETAPA_ID,
            sentido="Indeferido",
        )

    assert recusa.value.code == "sentido_invalido"
