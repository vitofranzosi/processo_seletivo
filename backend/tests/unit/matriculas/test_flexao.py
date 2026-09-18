"""Os 4 estados civis × 2 sexos, percorridos (`FR-442`, `D-004`, `T012`).

**Percorridos, e não amostrados.** São oito strings escritas à mão justamente para que o valor que
faltar apareça aqui — uma regra de sufixo passaria neste teste e erraria no primeiro estado civil
que não terminasse em `o`.
"""

import pytest

from processo_seletivo.matriculas.domain import flexao
from processo_seletivo.requerimentos.domain import nomes


@pytest.mark.parametrize("estado_civil", nomes.ESTADOS_CIVIS)
@pytest.mark.parametrize("sexo", nomes.SEXOS)
def test_a_flexao_e_total(estado_civil, sexo):
    """Não há caso sem resposta: `SEXO` é binário dos dois lados."""
    assert flexao.flexionar(estado_civil, sexo)


def test_as_oito_palavras_sao_as_do_destino():
    """O destino escreve `Casada`; este sistema guarda `CASADO` e **exibe** `Casado(a)`."""
    assert flexao.flexionar(nomes.CASADO, nomes.FEMININO) == "Casada"
    assert flexao.flexionar(nomes.CASADO, nomes.MASCULINO) == "Casado"
    assert flexao.flexionar(nomes.VIUVO, nomes.FEMININO) == "Viúva"
    assert flexao.flexionar(nomes.SOLTEIRO, nomes.MASCULINO) == "Solteiro"
    assert flexao.flexionar(nomes.DIVORCIADO, nomes.FEMININO) == "Divorciada"


def test_valor_fora_da_tabela_nao_e_flexionado():
    """O que não está na tabela é **ausente**, e não uma palavra inventada por regra de sufixo."""
    assert flexao.flexionar("SEPARADO", nomes.FEMININO) == ""
    assert flexao.flexionar(nomes.CASADO, "") == ""
