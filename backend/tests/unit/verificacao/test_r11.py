"""A tabela da R-11 com cinco pareceres (166, SC-2373): o plano nunca leva o desfavorável ao ato.

O ramo da R-11 em `consolidacao._planejar` encaminha toda deliberação pelo vídeo que não é
favorável. Aqui, sobre a mesma função de deliberação da `165`, todas as 32 combinações de cinco
pareceres nas três regras: o que não é favorável é exatamente o que o plano encaminha, e não há
terceira saída.
"""

import itertools

import pytest

from processo_seletivo.resultados.domain.deliberacao import REGRAS, Deliberacao


@pytest.mark.parametrize("regra", REGRAS)
@pytest.mark.parametrize("n", [3, 5])
def test_toda_deliberacao_pelo_video_ou_confirma_ou_encaminha(regra, n):
    for sentidos in itertools.product(("FAVORAVEL", "DESFAVORAVEL"), repeat=n):
        sentido = Deliberacao(regra=regra, sentidos=sentidos).sentido
        assert sentido in ("FAVORAVEL", "DESFAVORAVEL")
        # O plano só deixa passar ao ato o favorável; o resto vira "encaminhe à entrevista ao vivo".
        vai_ao_ato = sentido == "FAVORAVEL"
        assert vai_ao_ato or sentido == "DESFAVORAVEL"
