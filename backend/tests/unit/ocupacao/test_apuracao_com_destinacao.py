"""A conta pura da apuração com a destinação e a vaga não preenchida (155, R-002, R-005).

**Duas mudanças, e nenhuma mexe no que já existia.** O desfazimento da reversão é lido como
movimento — mesma quantidade, sentido invertido —, e a vaga não preenchida sai do "a ocupar" sem
tocar as efetivas. Sem nenhuma das duas linhas, a conta é a de antes, e os casos de
`test_apuracao.py` continuam a prová-lo.
"""

import pytest

from processo_seletivo.ocupacao.domain import apuracao, nomes

CEDIDA = (nomes.MOVIMENTO_REVERSAO, False, 2)
RECEBIDA = (nomes.MOVIMENTO_REVERSAO, True, 2)
# O desfazimento grava origem e destino trocados: na reserva ele chega como recebido.
DESFEITA_NA_RESERVA = (nomes.MOVIMENTO_DESFAZIMENTO, True, 2)
DESFEITA_NA_AMPLA = (nomes.MOVIMENTO_DESFAZIMENTO, False, 2)


def efetivas(publicadas, lidos):
    _, efetivas_, _ = apuracao.apurar(
        publicadas=publicadas,
        progrediram_em_ordem=[],
        habilitadas=set(),
        movimentos_lidos=lidos,
    )
    return efetivas_


class TestODesfazimentoELidoComoMovimento:
    def test_a_reserva_recebe_de_volta_o_que_cedeu(self):
        assert efetivas(2, [CEDIDA]) == 0
        assert efetivas(2, [CEDIDA, DESFEITA_NA_RESERVA]) == 2

    def test_a_ampla_devolve_o_que_recebeu(self):
        assert efetivas(3, [RECEBIDA]) == 5
        assert efetivas(3, [RECEBIDA, DESFEITA_NA_AMPLA]) == 3

    def test_a_soma_do_perfil_nao_muda_em_nenhum_dos_dois_atos(self):
        """FR-6311: a destinação e o desfazimento movem, e nenhum cria ou apaga vaga."""
        antes = efetivas(2, []) + efetivas(3, [])
        destinada = efetivas(2, [CEDIDA]) + efetivas(3, [RECEBIDA])
        desfeita = efetivas(2, [CEDIDA, DESFEITA_NA_RESERVA]) + efetivas(
            3, [RECEBIDA, DESFEITA_NA_AMPLA]
        )

        assert antes == destinada == desfeita == 5

    def test_a_janela_da_ampla_volta_ao_tamanho_publicado(self):
        """Quem ocupa pela ampla usa a mesma conta: o desfazimento estreita a janela outra vez."""
        faixa = ["a1", "a2", "a3", "a4", "a5"]

        assert (
            len(
                apuracao.ocupantes_pela_ampla(
                    progrediram_em_ordem=faixa, publicadas=3, movimentos_lidos=[RECEBIDA]
                )
            )
            == 5
        )
        assert (
            len(
                apuracao.ocupantes_pela_ampla(
                    progrediram_em_ordem=faixa,
                    publicadas=3,
                    movimentos_lidos=[RECEBIDA, DESFEITA_NA_AMPLA],
                )
            )
            == 3
        )

    def test_especie_desconhecida_e_recusada_e_nao_contada_em_silencio(self):
        with pytest.raises(ValueError, match="espécie de movimento desconhecida"):
            efetivas(2, [("OUTRA", True, 1)])


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
