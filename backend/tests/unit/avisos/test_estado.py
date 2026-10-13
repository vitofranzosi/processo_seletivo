"""O estado do destinatário, derivado dos registros e do relógio (data-model §2, `R-016`).

**Um caso por linha da tabela**, e o limite exato da janela: um minuto antes ainda sai, no instante
da janela já não. É o limite que decide se religar a chave dispara uma mensagem antiga.
"""

from datetime import UTC, datetime, timedelta

import pytest

from processo_seletivo.avisos.domain import nomes
from processo_seletivo.avisos.domain.estado import (
    EM_ENVIO_ATE_MIN,
    Tentativa,
    concluido,
    elegivel_ao_despacho,
    estado_do_destinatario,
    proxima_tentativa_em,
)

SOLICITADO = datetime(2026, 10, 9, 12, 0, tzinfo=UTC)
JANELA = 24


def estado(
    *, tentativas=(), agora=None, interrompido=False, elegibilidade=nomes.ELEGIVEL, end="a@x"
):
    return estado_do_destinatario(
        elegibilidade=elegibilidade,
        endereco=end,
        tentativas=list(tentativas),
        interrompido=interrompido,
        solicitado_em=SOLICITADO,
        agora=agora or SOLICITADO + timedelta(minutes=1),
        max_tentativas=3,
        janela_horas=JANELA,
    )


def tentativa(numero, resultado, minutos=1):
    inicio = SOLICITADO + timedelta(minutes=minutos)
    return Tentativa(
        numero, inicio, resultado, inicio + timedelta(seconds=2) if resultado else None
    )


class TestCadaLinhaDaTabela:
    def test_nao_elegivel_vence_tudo(self):
        assert estado(elegibilidade=nomes.NAO_ELEGIVEL_DESFECHO, end="") == nomes.NAO_ELEGIVEL

    def test_sem_endereco(self):
        assert estado(end="") == nomes.SEM_ENDERECO

    def test_interrompido_antes_do_envio(self):
        assert estado(interrompido=True) == nomes.INTERROMPIDO_ANTES_DO_ENVIO

    def test_pendente(self):
        assert estado() == nomes.PENDENTE

    def test_em_envio_quando_recente(self):
        inicio = tentativa(1, None)
        agora = inicio.iniciada_em + timedelta(minutes=EM_ENVIO_ATE_MIN - 1)

        assert estado(tentativas=[inicio], agora=agora) == nomes.EM_ENVIO

    def test_tentativa_sem_resultado_antiga_e_indeterminada(self):
        inicio = tentativa(1, None)
        agora = inicio.iniciada_em + timedelta(minutes=EM_ENVIO_ATE_MIN)

        assert estado(tentativas=[inicio], agora=agora) == nomes.ESTADO_INDETERMINADA

    def test_aceita(self):
        assert estado(tentativas=[tentativa(1, nomes.ACEITA)]) == nomes.ESTADO_ACEITA

    def test_falha_temporaria_abaixo_do_limite(self):
        assert (
            estado(tentativas=[tentativa(1, nomes.FALHA_TEMPORARIA)])
            == nomes.ESTADO_FALHA_TEMPORARIA
        )

    def test_falha_temporaria_no_limite_e_definitiva(self):
        tres = [tentativa(n, nomes.FALHA_TEMPORARIA, minutos=n * 20) for n in (1, 2, 3)]

        assert estado(tentativas=tres, agora=SOLICITADO + timedelta(hours=2)) == (
            nomes.ESTADO_FALHA_DEFINITIVA
        )

    def test_falha_definitiva(self):
        assert (
            estado(tentativas=[tentativa(1, nomes.FALHA_DEFINITIVA)])
            == nomes.ESTADO_FALHA_DEFINITIVA
        )

    def test_indeterminada_registrada(self):
        assert estado(tentativas=[tentativa(1, nomes.INDETERMINADA)]) == nomes.ESTADO_INDETERMINADA

    def test_falha_temporaria_de_aviso_interrompido_para(self):
        assert (
            estado(tentativas=[tentativa(1, nomes.FALHA_TEMPORARIA)], interrompido=True)
            == nomes.INTERROMPIDO_ANTES_DO_ENVIO
        )

    def test_a_aceita_continua_aceita_depois_da_interrupcao(self):
        assert (
            estado(tentativas=[tentativa(1, nomes.ACEITA)], interrompido=True)
            == nomes.ESTADO_ACEITA
        )


class TestAJanela:
    def test_um_minuto_antes_ainda_pendente(self):
        agora = SOLICITADO + timedelta(hours=JANELA) - timedelta(minutes=1)

        assert estado(agora=agora) == nomes.PENDENTE

    def test_no_instante_da_janela_expira(self):
        assert estado(agora=SOLICITADO + timedelta(hours=JANELA)) == nomes.EXPIRADA_SEM_ENVIO

    def test_falha_temporaria_fora_da_janela_expira(self):
        agora = SOLICITADO + timedelta(hours=JANELA, minutes=1)

        assert (
            estado(tentativas=[tentativa(1, nomes.FALHA_TEMPORARIA)], agora=agora)
            == nomes.EXPIRADA_SEM_ENVIO
        )

    def test_a_aceita_nao_expira(self):
        agora = SOLICITADO + timedelta(days=30)

        assert estado(tentativas=[tentativa(1, nomes.ACEITA)], agora=agora) == nomes.ESTADO_ACEITA


class TestODespacho:
    def test_chave_desligada_ninguem(self):
        assert not elegivel_ao_despacho(
            estado=nomes.PENDENTE,
            tentativas=[],
            agora=SOLICITADO,
            intervalos=(5,),
            habilitado=False,
        )

    def test_pendente_pode(self):
        assert elegivel_ao_despacho(
            estado=nomes.PENDENTE, tentativas=[], agora=SOLICITADO, intervalos=(5,), habilitado=True
        )

    @pytest.mark.parametrize(
        ("minutos", "pode"), [(4, False), (5, True)], ids=["antes-do-intervalo", "no-intervalo"]
    )
    def test_falha_temporaria_so_depois_do_intervalo(self, minutos, pode):
        falha = tentativa(1, nomes.FALHA_TEMPORARIA)
        agora = falha.registrado_em + timedelta(minutes=minutos)

        assert (
            elegivel_ao_despacho(
                estado=nomes.ESTADO_FALHA_TEMPORARIA,
                tentativas=[falha],
                agora=agora,
                intervalos=(5, 15),
                habilitado=True,
            )
            is pode
        )

    def test_o_intervalo_cresce(self):
        primeira = tentativa(1, nomes.FALHA_TEMPORARIA, minutos=1)
        segunda = tentativa(2, nomes.FALHA_TEMPORARIA, minutos=10)

        assert proxima_tentativa_em([primeira], intervalos=(5, 15)) == primeira.registrado_em + (
            timedelta(minutes=5)
        )
        assert proxima_tentativa_em(
            [primeira, segunda], intervalos=(5, 15)
        ) == segunda.registrado_em + timedelta(minutes=15)

    @pytest.mark.parametrize(
        "estado_",
        [
            nomes.ESTADO_INDETERMINADA,
            nomes.ESTADO_ACEITA,
            nomes.EXPIRADA_SEM_ENVIO,
            nomes.INTERROMPIDO_ANTES_DO_ENVIO,
            nomes.EM_ENVIO,
            nomes.SEM_ENDERECO,
            nomes.NAO_ELEGIVEL,
        ],
    )
    def test_indeterminada_e_demais_nunca(self, estado_):
        """**A indeterminada nunca sai sozinha** (`FR-1267`): a mensagem pode ter saído."""
        assert not elegivel_ao_despacho(
            estado=estado_, tentativas=[], agora=SOLICITADO, intervalos=(5,), habilitado=True
        )


def test_concluido_quando_nada_mais_pode_sair():
    assert concluido([nomes.ESTADO_ACEITA, nomes.SEM_ENDERECO, nomes.EXPIRADA_SEM_ENVIO])
    assert not concluido([nomes.ESTADO_ACEITA, nomes.PENDENTE])
    assert not concluido([nomes.ESTADO_FALHA_TEMPORARIA])
    assert not concluido([nomes.EM_ENVIO])
