"""O prazo apresentado: uma função para o portal e o e-mail, no fuso da instalação (121).

`FR-3873` a `FR-3875`, `SC-1154`, `SC-1155`. Sem banco: a função é pura, recebe o vencimento, o
instante de referência e o fuso, e não lê relógio nem `settings`.

**Por que o ano inteiro.** O dia da semana sai de tabela própria (R-003), e uma tabela fora de ordem
erraria seis dias em sete sem que um caso isolado notasse. Conferir os 365 dias de 2027 contra a
biblioteca padrão é o que torna a tabela verificável.
"""

import calendar
import os
import time
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from processo_seletivo.convocacao.domain.prazo_apresentado import (
    DIAS_DA_SEMANA,
    apresentar,
)

SP = ZoneInfo("America/Sao_Paulo")


def local(*args):
    return datetime(*args, tzinfo=SP)


class TestODiaDaSemana:
    def test_confere_com_o_calendario_em_todos_os_dias_de_2027(self):
        """`SC-1154`: o dia da semana confere com a data em todos os dias de um ano."""
        dia = date(2027, 1, 1)
        conferidos = 0
        while dia.year == 2027:
            vencimento = datetime(dia.year, dia.month, dia.day, 17, 0, tzinfo=SP)
            prazo = apresentar(vencimento, vencimento - timedelta(days=10), SP)
            esperado = DIAS_DA_SEMANA[calendar.weekday(dia.year, dia.month, dia.day)]
            assert prazo.dia_da_semana == esperado, dia
            assert prazo.data == dia.strftime("%d/%m/%Y")
            conferidos += 1
            dia += timedelta(days=1)
        assert conferidos == 365

    def test_por_extenso_e_em_minusculas(self):
        prazo = apresentar(local(2026, 11, 10, 17, 0), local(2026, 11, 1, 9, 0), SP)

        assert prazo.dia_da_semana == "terça-feira"
        assert prazo.dia_da_semana == prazo.dia_da_semana.lower()


class TestODiaLocal:
    def test_vencimento_as_23h30_locais_e_o_dia_local(self):
        """`FR-3873`: 23h30 em São Paulo é 02h30 UTC do dia seguinte, e a pessoa lê o dia dela."""
        vencimento = datetime(2026, 11, 13, 2, 30, tzinfo=UTC)
        agora = datetime(2026, 11, 10, 15, 0, tzinfo=UTC)

        prazo = apresentar(vencimento, agora, SP)

        assert prazo.data == "12/11/2026"
        assert prazo.hora == "23h30"
        assert prazo.dia_da_semana == "quinta-feira"
        assert prazo.contagem == "faltam 2 dias"
        assert prazo.linha == "quinta-feira · faltam 2 dias"

    def test_vencimento_a_meia_noite_e_o_instante_no_fuso(self):
        """Caso-limite: 00h00 de 11/11 é quarta-feira, 11/11/2026, às 00h00, não "fim de 10/11"."""
        prazo = apresentar(local(2026, 11, 11, 0, 0), local(2026, 11, 9, 10, 0), SP)

        assert prazo.data == "11/11/2026"
        assert prazo.hora == "00h00"
        assert prazo.dia_da_semana == "quarta-feira"
        assert prazo.contagem == "faltam 2 dias"
        assert prazo.por_extenso == "quarta-feira, 11/11/2026, às 00h00"


class TestAContagem:
    """`FR-3874`: dias de calendário, nunca blocos de 24 horas, e nunca arredondando para cima."""

    VENCIMENTO = local(2026, 11, 12, 9, 0)

    @pytest.mark.parametrize(
        ("agora", "contagem"),
        [
            # Às 23h59 de 10/11: dois dias de calendário, embora faltem só 33 horas.
            (local(2026, 11, 10, 23, 59), "faltam 2 dias"),
            # Às 00h01 de 11/11: amanhã, embora faltem quase 33 horas.
            (local(2026, 11, 11, 0, 1), "termina amanhã"),
            (local(2026, 11, 11, 23, 59), "termina amanhã"),
            # Às 00h01 de 12/11: hoje, ainda que faltem quase nove horas.
            (local(2026, 11, 12, 0, 1), "termina hoje, às 09h00"),
            # A uma hora do vencimento: hoje, e nunca "falta 1 dia".
            (local(2026, 11, 12, 8, 0), "termina hoje, às 09h00"),
            # No próprio instante ainda não passou (`decorrido` é `agora > vencimento`).
            (local(2026, 11, 12, 9, 0), "termina hoje, às 09h00"),
        ],
    )
    def test_conta_dias_de_calendario(self, agora, contagem):
        prazo = apresentar(self.VENCIMENTO, agora, SP)

        assert prazo.contagem == contagem
        assert not prazo.vencido

    def test_hoje_sem_o_dia_da_semana(self):
        prazo = apresentar(self.VENCIMENTO, local(2026, 11, 12, 8, 0), SP)

        assert prazo.linha == "termina hoje, às 09h00"

    def test_amanha_com_o_dia_da_semana(self):
        prazo = apresentar(self.VENCIMENTO, local(2026, 11, 11, 10, 0), SP)

        assert prazo.linha == "quinta-feira · termina amanhã"

    def test_dois_ou_mais_dias(self):
        prazo = apresentar(self.VENCIMENTO, local(2026, 11, 5, 10, 0), SP)

        assert prazo.linha == "quinta-feira · faltam 7 dias"

    def test_vencido_nao_tem_linha(self):
        """Vencido é o estado encerrado (FR-3748 da 118): nenhuma linha abaixo da data."""
        prazo = apresentar(self.VENCIMENTO, local(2026, 11, 12, 9, 1), SP)

        assert prazo.vencido
        assert prazo.contagem == ""
        assert prazo.linha == ""

    def test_nunca_falta_1_dia(self):
        """A frase que arredonda para cima não existe em nenhum instante das 72 horas anteriores."""
        agora = self.VENCIMENTO - timedelta(hours=72)
        while agora <= self.VENCIMENTO:
            prazo = apresentar(self.VENCIMENTO, agora, SP)
            assert "falta 1" not in prazo.contagem
            assert "faltam 1 " not in prazo.contagem
            agora += timedelta(minutes=17)


class TestOFormatoDaHora:
    """`FR-3875`, `SC-1155`: *"às HHhMM"*, nunca *"às HH:MM"*."""

    def test_hhhmm(self):
        prazo = apresentar(local(2026, 11, 12, 7, 5), local(2026, 11, 1, 0, 0), SP)

        assert prazo.hora == "07h05"
        assert prazo.ate == "até 12/11/2026, às 07h05"
        assert prazo.data_e_hora == "12/11/2026, às 07h05"
        assert prazo.data_curta == "12/11"
        for campo in (prazo.hora, prazo.ate, prazo.por_extenso, prazo.linha):
            assert ":" not in campo


class TestOFusoDoServidorNaoMuda:
    """`SC-1154`: o fuso do teste é fixado, e outro fuso de servidor dá o mesmo resultado."""

    @pytest.fixture
    def tz_do_processo(self):
        anterior = os.environ.get("TZ")

        def trocar(nome):
            os.environ["TZ"] = nome
            time.tzset()

        yield trocar
        if anterior is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = anterior
        time.tzset()

    @pytest.mark.parametrize("fuso_do_servidor", ["UTC", "Asia/Tokyo"])
    def test_o_mesmo_resultado(self, tz_do_processo, fuso_do_servidor):
        vencimento = datetime(2026, 11, 13, 2, 30, tzinfo=UTC)
        agora = datetime(2026, 11, 11, 3, 30, tzinfo=UTC)
        esperado = apresentar(vencimento, agora, SP)

        tz_do_processo(fuso_do_servidor)

        assert apresentar(vencimento, agora, SP) == esperado
        assert esperado.data == "12/11/2026"
        assert esperado.linha == "quinta-feira · termina amanhã"
