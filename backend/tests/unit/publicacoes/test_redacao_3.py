"""A redação 3 do Edital: a 2 sem o masculino genérico, e a 2 continuando como foi (2026-11-13).

Decisão do usuário, na auditoria dos e-mails (`doc/auditoria-dos-emails-2026-11-13.md`, achado 9):
o Edital publicado daqui em diante nomeia a pessoa sem presumir o gênero — "pessoa", "quem se
inscreve", os numerais no feminino. **O publicado antes não muda**: ele gravou a redação 2 em
`redacao_do_documento`, e o compositor, chamado com ela, devolve as frases da 2.

O mesmo Edital, composto nas duas redações, é a prova das duas pontas.
"""

import pytest

from processo_seletivo.publicacoes.infrastructure import pdf
from tests.unit.publicacoes.test_pdf import documento, texto_de
from tests.unit.publicacoes.test_redacao_no_documento import _completo, _normal

#: As frases da 2 que a 3 reescreve, e como a 3 as diz — no Edital completo da suíte, que tem toda
#: variante que gera frase.
PARES = [
    (
        "os primeiros classificados de cada lista de concorrência",
        "as primeiras pessoas classificadas de cada lista de concorrência",
    ),
    ("mais 3 (três) suplentes.", "mais 3 (três) pessoas suplentes."),
    ("os 10 (dez) primeiros classificados", "as 10 (dez) primeiras pessoas classificadas"),
    ("passam todos os empatados", "passam todas as pessoas empatadas"),
    (
        "Depois, poderão ser chamados outros candidatos, além desses",
        "Depois, poderão ser chamadas outras pessoas, além dessas",
    ),
    ("Não serão chamados candidatos além desses.", "Não serão chamadas pessoas além dessas."),
    (
        "A convocação dos classificados será feita por publicação.",
        "A convocação das pessoas classificadas será feita por publicação.",
    ),
    ("Cada candidato pode enviar", "Cada pessoa pode enviar"),
    ("Ao enviá-lo, o candidato declara:", "Ao enviá-lo, a pessoa declara:"),
]


@pytest.fixture(scope="module")
def na_redacao_2():
    return _normal(texto_de(documento(_completo(), redacao=pdf.REDACAO_2)))


@pytest.fixture(scope="module")
def na_vigente():
    return _normal(texto_de(documento(_completo())))


def test_a_vigente_e_a_3():
    assert pdf.REDACAO_VIGENTE == 3


@pytest.mark.parametrize(("da_2", "da_3"), PARES, ids=[par[1][:40] for par in PARES])
def test_o_edital_novo_diz_a_frase_da_3_e_nao_a_da_2(na_vigente, da_2, da_3):
    assert da_3 in na_vigente
    assert da_2 not in na_vigente


@pytest.mark.parametrize(("da_2", "da_3"), PARES, ids=[par[0][:40] for par in PARES])
def test_o_edital_da_2_continua_dizendo_o_que_disse(na_redacao_2, da_2, da_3):
    assert da_2 in na_redacao_2
    assert da_3 not in na_redacao_2
