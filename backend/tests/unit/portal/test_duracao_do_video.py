"""A duração do vídeo por extenso no comprovante (174, FR-7883).

Os mesmos casos de `duracaoPorExtenso` em `tests/javascript/gravacao.test.js`: a revisão no aparelho
e o comprovante no servidor dizem a mesma duração do mesmo jeito.
"""

from decimal import Decimal

import pytest

from processo_seletivo.portal.templatetags.duracao_do_video import duracao_por_extenso


@pytest.mark.parametrize(
    ("segundos", "esperado"),
    [
        (72.3, "1 min 12 s"),
        (Decimal("72.300"), "1 min 12 s"),
        (45, "45 s"),
        (180, "3 min"),
        (4.5, "5 s"),
        (0, "0 s"),
        (None, ""),
        ("abc", ""),
    ],
)
def test_a_duracao_sai_em_minutos_e_segundos(segundos, esperado):
    assert duracao_por_extenso(segundos) == esperado
