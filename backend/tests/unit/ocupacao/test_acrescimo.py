"""A conta da vaga acrescida, pura: o saldo, o que resta, e a trava do desfazimento (097).

**Sem banco.** A apuração recebe o saldo pronto, como já recebe os movimentos; o que se prova aqui é
que a soma entra no lugar certo — antes do recorte da janela de titulares — e que a trava do
desfazimento conta quem foi chamado, e não quem a conta alcança (`T-005`).
"""

import pytest

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


class TestOPerfilAceita:
    """`impedimento`, puro: a resposta única que a tela e o ato leem (`FR-2463`, `FR-2464`)."""

    PERFIL = "aaaaaaaa-0000-4000-8000-000000000971"
    AMPLA = "aaaaaaaa-0000-4000-8000-000000000972"
    PPI = "aaaaaaaa-0000-4000-8000-000000000973"

    def conteudo(self, **perfil):
        base = {
            "id": self.PERFIL,
            "reserveType": "UNLIMITED",
            "vacancyTable": [{"id": "l1", "modalityId": None, "immediateVacancies": 0}],
        }
        return {"profiles": [{**base, **perfil}]}

    def codigo(self, conteudo, lista_id=None):
        from processo_seletivo.ocupacao.application.acrescimo import impedimento

        recusa = impedimento(conteudo, perfil_id=self.PERFIL, lista_id=lista_id)
        return recusa[0] if recusa else None

    def test_so_reserva_e_so_a_linha_geral_aceita(self):
        assert self.codigo(self.conteudo()) is None
        assert self.codigo(self.conteudo(reserveType="LIMITED")) is None

    def test_sem_reserva_recusa(self):
        assert (
            self.codigo(self.conteudo(reserveType="NONE"))
            == nomes.ACRESCIMO_SEM_CADASTRO_DE_RESERVA
        )

    def test_linha_de_modalidade_ate_com_zero_recusa(self):
        linhas = [
            {"id": "l1", "modalityId": None, "immediateVacancies": 0},
            {"id": "l2", "modalityId": self.PPI, "immediateVacancies": 0},
        ]

        assert (
            self.codigo(self.conteudo(vacancyTable=linhas)) == nomes.ACRESCIMO_FORA_DA_LINHA_GERAL
        )

    def test_reversao_declarada_recusa(self):
        conteudo = self.conteudo(vacancyReversion={"kind": "ON_BALANCE"})

        assert self.codigo(conteudo) == nomes.ACRESCIMO_FORA_DA_LINHA_GERAL

    def test_a_modalidade_declarada_como_ampla_le_a_linha_geral(self):
        """As duas grafias da ampla: o recorte nulo e a Modalidade que o Perfil aponta como ela."""
        conteudo = self.conteudo(generalCompetitionModalityId=self.AMPLA)

        assert self.codigo(conteudo, lista_id=self.AMPLA) is None
        assert self.codigo(conteudo, lista_id=self.PPI) == nomes.ACRESCIMO_FORA_DA_LINHA_GERAL


class TestAsRecusasDoRecorte:
    """`FR-2459`, e a ordem do contrato: a mais específica primeiro."""

    def recusa(self, **previa):
        from processo_seletivo.ocupacao.application.acrescimo import conferir_recorte
        from processo_seletivo.shared.api.problems import DomainError

        base = {"impedimento": None, "temOrdem": True, "temQuadro": True}
        with pytest.raises(DomainError) as erro:
            conferir_recorte({**base, **previa})
        return erro.value.code

    def test_sem_ordem_vigente(self):
        assert self.recusa(temOrdem=False) == nomes.ORDEM_NAO_VIGENTE

    def test_sem_linha_no_quadro(self):
        assert self.recusa(temQuadro=False) == nomes.SEM_QUADRO_PUBLICADO

    def test_o_impedimento_do_perfil_vem_antes(self):
        impedido = (nomes.ACRESCIMO_SEM_CADASTRO_DE_RESERVA, "frase")

        assert (
            self.recusa(impedimento=impedido, temOrdem=False)
            == nomes.ACRESCIMO_SEM_CADASTRO_DE_RESERVA
        )

    def test_o_recorte_completo_passa(self):
        from processo_seletivo.ocupacao.application.acrescimo import conferir_recorte

        assert conferir_recorte({"impedimento": None, "temOrdem": True, "temQuadro": True}) is None
