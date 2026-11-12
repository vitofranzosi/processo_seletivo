"""A conta pura da apuração com a vaga não preenchida (155, R-002).

**Uma mudança, e ela não mexe no que já existia.** A vaga não preenchida sai do "a ocupar" sem tocar
as efetivas. Sem declaração, a conta é a de antes, e os casos de `test_apuracao.py` continuam a
prová-lo.
"""

import pytest

from processo_seletivo.ocupacao.domain import apuracao, nomes


class TestAVagaNaoPreenchidaSaiDoAOcupar:
    def test_o_saldo_e_declaracoes_menos_desfazimentos(self):
        lidas = [
            (nomes.NAO_PREENCHIDA_DECLARACAO, 2),
            (nomes.NAO_PREENCHIDA_DESFAZIMENTO, 1),
            (nomes.NAO_PREENCHIDA_DECLARACAO, 1),
        ]

        assert apuracao.saldo_das_nao_preenchidas(lidas) == 2
        assert apuracao.saldo_das_nao_preenchidas([]) == 0

    def test_especie_desconhecida_e_recusada(self):
        with pytest.raises(ValueError, match="vaga não preenchida desconhecida"):
            apuracao.saldo_das_nao_preenchidas([("OUTRA", 1)])

    def test_faltando_desconta_e_tem_piso_em_zero(self):
        assert apuracao.faltando(efetivas=3, ocupadas=1, nao_preenchidas=1) == 1
        assert apuracao.faltando(efetivas=3, ocupadas=1, nao_preenchidas=2) == 0
        assert apuracao.faltando(efetivas=3, ocupadas=3, nao_preenchidas=1) == 0

    def test_sem_declaracao_a_conta_e_a_de_antes(self):
        """O padrão é zero: a prévia da classificação e toda chamada anterior não mudam."""
        assert apuracao.faltando(efetivas=3, ocupadas=1) == 2

    def test_as_efetivas_nao_mudam_com_a_declaracao(self):
        """A vaga existe e ninguém a preencheu (D-003 da spec): não é acréscimo negativo."""
        publicadas, efetivas_, ocupadas = apuracao.apurar(
            publicadas=3, progrediram_em_ordem=[], habilitadas=set()
        )

        assert (publicadas, efetivas_, ocupadas) == (3, 3, 0)
        assert apuracao.faltando(efetivas=efetivas_, ocupadas=ocupadas, nao_preenchidas=1) == 2
