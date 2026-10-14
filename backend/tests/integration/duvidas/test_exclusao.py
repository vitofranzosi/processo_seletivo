"""A exclusão dos registros do piloto, 90 dias depois do relatório final (071, T061, `R-021`).

As datas são relativas a hoje, na zona institucional: o comando lê o relógio, e a suíte não tem
`freezegun`.
"""

import uuid
from datetime import datetime, time, timedelta
from io import StringIO

import pytest
from django.core.management import CommandError, call_command
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from processo_seletivo.duvidas.domain.estruturas_do_piloto import RESPONDIDA_E_CONFERIDA, TELA
from processo_seletivo.duvidas.models import TrocaDoPiloto
from processo_seletivo.processos.models import Edital
from processo_seletivo.shared.tempo import ZONA

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def _troca(edital, criada_em):
    troca = TrocaDoPiloto.objects.create(
        conversa=uuid.uuid4(),
        ordem=1,
        edital=edital,
        instante=criada_em,
        origem=TELA,
        pergunta="Quantas vagas há?",
        estado=RESPONDIDA_E_CONFERIDA,
        servico="ollama",
        modelo_configurado="modelo/de-teste",
        versao_das_instrucoes="1",
    )
    # `auto_now_add` não aceita a data na criação.
    TrocaDoPiloto.objects.filter(pk=troca.pk).update(criada_em=criada_em)
    return troca


@pytest.fixture
def hoje():
    return timezone.now().astimezone(ZONA).date()


@pytest.fixture
def edital(edital_a):
    return Edital.objects.first()


def _excluir(relatorio):
    saida = StringIO()
    call_command(
        "excluir_registros_do_piloto", "--relatorio-final-em", str(relatorio), stdout=saida
    )
    return saida.getvalue()


def test_antes_de_90_dias_recusa_e_nada_sai(edital, hoje):
    _troca(edital, timezone.now() - timedelta(days=200))

    with pytest.raises(CommandError, match="90 dias depois"):
        _excluir(hoje - timedelta(days=89))
    assert TrocaDoPiloto.objects.count() == 1


def test_depois_so_as_trocas_ate_a_data_e_so_a_tabela_do_piloto(edital, hoje):
    relatorio = hoje - timedelta(days=90)
    ultimo_instante = datetime.combine(relatorio, time(23, 59), tzinfo=ZONA)
    _troca(edital, ultimo_instante - timedelta(days=10))
    _troca(edital, ultimo_instante)
    depois = _troca(edital, ultimo_instante + timedelta(minutes=2))  # o dia seguinte

    with CaptureQueriesContext(connection) as consultas:
        saida = _excluir(relatorio)

    assert saida.strip() == "2 trocas excluídas"
    assert list(TrocaDoPiloto.objects.values_list("pk", flat=True)) == [depois.pk]
    assert Edital.objects.filter(pk=edital.pk).exists()
    exclusoes = [c["sql"] for c in consultas.captured_queries if c["sql"].startswith("DELETE")]
    assert exclusoes and all('"duvidas_trocadopiloto"' in sql for sql in exclusoes)


def test_data_invalida_recusa(edital):
    with pytest.raises(CommandError, match="AAAA-MM-DD"):
        _excluir("13/10/2026")
