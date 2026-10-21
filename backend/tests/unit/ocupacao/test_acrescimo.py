"""A conta da vaga acrescida, pura: o saldo, o que resta, e a trava do desfazimento (097).

**Sem banco.** A apuração recebe o saldo pronto, como já recebe os movimentos; o que se prova aqui é
que a soma entra no lugar certo — antes do recorte da janela de titulares — e que a trava do
desfazimento conta quem foi chamado, e não quem a conta alcança (`T-005`).
"""

from processo_seletivo.ocupacao.domain import acrescimo, nomes
from processo_seletivo.ocupacao.domain import apuracao as calculo

ORDEM = ["a", "b", "c", "d"]


class TestAApuracaoSomaOSaldo:
    def test_zero_publicada_com_duas_acrescidas_da_duas_efetivas(self):
        publicadas, efetivas, ocupadas = calculo.apurar(
            publicadas=0,
            progrediram_em_ordem=ORDEM,
            habilitadas=set(ORDEM),
            acrescidas=2,
        )

        assert (publicadas, efetivas, ocupadas) == (0, 2, 2)

    def test_os_titulares_sao_os_primeiros_da_ordem(self):
        """**O saldo entra antes da janela**: é por isso que o 1º do sorteio passa a ser titular."""
        titulares = calculo.titulares_iniciais(progrediram_em_ordem=ORDEM, efetivas=0 + 2)

        assert titulares == ["a", "b"]

    def test_sem_acrescimo_nada_muda(self):
        """O padrão é zero, e nenhuma apuração anterior à `097` muda de número."""
        assert calculo.apurar(
            publicadas=3, progrediram_em_ordem=ORDEM, habilitadas={"a"}
        ) == calculo.apurar(
            publicadas=3, progrediram_em_ordem=ORDEM, habilitadas={"a"}, acrescidas=0
        )

    def test_soma_com_os_movimentos(self):
        _, efetivas, _ = calculo.apurar(
            publicadas=1,
            progrediram_em_ordem=ORDEM,
            habilitadas=set(),
            movimentos_lidos=[(nomes.MOVIMENTO_REVERSAO, True, 1)],
            acrescidas=2,
        )

        assert efetivas == 4


class TestOSaldo:
    def test_acrescimos_somam_e_desfazimentos_subtraem(self):
        lidos = [
            (nomes.ACRESCIMO, 2),
            (nomes.ACRESCIMO, 1),
            (nomes.DESFAZIMENTO, 1),
        ]

        assert acrescimo.saldo(lidos) == 2

    def test_sem_lidos_o_saldo_e_zero(self):
        assert acrescimo.saldo([]) == 0

    def test_o_que_resta_de_um_acrescimo(self):
        assert acrescimo.restante(quantidade=3, desfeitas=[1, 1]) == 1
        assert acrescimo.restante(quantidade=1, desfeitas=[]) == 1
        assert acrescimo.restante(quantidade=2, desfeitas=[2]) == 0


class TestATravaDoDesfazimento:
    def test_quem_so_esta_na_conta_nao_impede(self):
        """**Titular sem chamada sai da conta, e ninguém lhe disse nada** (`FR-2462`).

        Pela contagem da `016`, ocupadas é 1 no instante da emissão. Contar ocupantes aqui recusaria
        todo desfazimento — a redação que o plano corrigiu.
        """
        assert acrescimo.recusa_do_desfazimento(efetivas=1, quantidade=1, chamadas=0) is None

    def test_quem_foi_chamado_impede(self):
        assert (
            acrescimo.recusa_do_desfazimento(efetivas=1, quantidade=1, chamadas=1)
            == nomes.DESFAZIMENTO_COM_PESSOAS_CHAMADAS
        )

    def test_sobrando_vaga_para_os_chamados_passa(self):
        assert acrescimo.recusa_do_desfazimento(efetivas=3, quantidade=1, chamadas=2) is None
        assert (
            acrescimo.recusa_do_desfazimento(efetivas=3, quantidade=2, chamadas=2)
            == nomes.DESFAZIMENTO_COM_PESSOAS_CHAMADAS
        )
