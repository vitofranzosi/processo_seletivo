"""Quem ocupa pela ampla, sem banco (095, T004, D-005).

A função saiu de `selectors.ocupantes_da_ampla`, e o que está aqui é o comportamento que ela tinha
lá — inclusive o que a `095` registrou como pendente (R-002): a habilitação decide a recusa do
empate, e **não** tira o titular eliminado do conjunto.
"""

import pytest

from processo_seletivo.ocupacao.domain import apuracao, nomes
from processo_seletivo.ocupacao.domain.apuracao import ocupantes_pela_ampla

FAIXA = ["a1", "a2", "a3", "a4", "a5"]


class TestTitulares:
    def test_sao_as_primeiras_vagas_da_sequencia(self):
        assert ocupantes_pela_ampla(progrediram_em_ordem=FAIXA, publicadas=3) == {"a1", "a2", "a3"}

    def test_o_suplente_da_faixa_nao_ocupa(self):
        assert "a4" not in ocupantes_pela_ampla(progrediram_em_ordem=FAIXA, publicadas=3)

    def test_sem_vagas_ninguem_ocupa(self):
        assert ocupantes_pela_ampla(progrediram_em_ordem=FAIXA, publicadas=0) == set()

    def test_o_titular_eliminado_continua_no_conjunto(self):
        """**R-002 da `095`, preso como está**: `habilitadas` não filtra os ocupantes."""
        assert ocupantes_pela_ampla(
            progrediram_em_ordem=FAIXA, publicadas=3, habilitadas={"a2", "a3"}
        ) == {"a1", "a2", "a3"}


class TestMovimentosEEfeitos:
    def test_vaga_recebida_pela_reversao_aumenta_a_janela(self):
        recebida = (nomes.MOVIMENTO_REVERSAO, True, 2)

        assert ocupantes_pela_ampla(
            progrediram_em_ordem=FAIXA, publicadas=2, movimentos_lidos=[recebida]
        ) == {"a1", "a2", "a3", "a4"}

    def test_vaga_cedida_diminui(self):
        cedida = (nomes.MOVIMENTO_REVERSAO, False, 1)

        assert ocupantes_pela_ampla(
            progrediram_em_ordem=FAIXA, publicadas=3, movimentos_lidos=[cedida]
        ) == {"a1", "a2"}

    def test_desistencia_e_aceite_da_019(self):
        efeitos = [(nomes.EFEITO_EXCLUSAO, "a1"), (nomes.EFEITO_INCLUSAO, "a4")]

        assert ocupantes_pela_ampla(
            progrediram_em_ordem=FAIXA, publicadas=3, efeitos_lidos=efeitos
        ) == {"a2", "a3", "a4"}


class TestEmpateNaFronteira:
    def test_empate_que_atravessa_as_vagas_recusa(self):
        with pytest.raises(apuracao.EmpateNaFronteiraDoAlvo) as erro:
            ocupantes_pela_ampla(
                progrediram_em_ordem=FAIXA, publicadas=3, empates_residuais={"a3": 3, "a4": 3}
            )

        assert (erro.value.posicao, erro.value.quantas) == (3, 2)

    def test_empate_entre_eliminados_nao_recusa(self):
        """A habilitação age aqui: o empate que não muda o número não para a conta."""
        assert ocupantes_pela_ampla(
            progrediram_em_ordem=FAIXA,
            publicadas=3,
            empates_residuais={"a3": 3, "a4": 3},
            habilitadas={"a1", "a2"},
        ) == {"a1", "a2", "a3"}


def test_e_a_mesma_conta_que_a_apuracao_da_ampla_faz_quando_todos_habilitaram():
    """Com todos habilitados, o número de ocupantes é o `ocupadas` da apuração da ampla."""
    _, _, ocupadas = apuracao.apurar(publicadas=3, progrediram_em_ordem=FAIXA, habilitadas=FAIXA)

    assert len(ocupantes_pela_ampla(progrediram_em_ordem=FAIXA, publicadas=3)) == ocupadas
