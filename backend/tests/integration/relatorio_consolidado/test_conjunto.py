"""O conjunto: critério, partição, escolha e escopo (100, FR-2555 a FR-2565)."""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from processo_seletivo.interface import relatorio_consolidado as rc
from processo_seletivo.processos.models import Edital
from processo_seletivo.unidades.models import Unidade
from tests.conftest import ator_institucional
from tests.fixtures.relatorio import REFERENCIA, dia, montar_cenario
from tests.integration.relatorio_consolidado.conftest import conjunto, ler, texto_do_documento

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def _numeros(c):
    return [e.number for e in c.incluidos]


def test_os_semestres_particionam_pela_primeira_publicacao(tres_editais):
    primeiro = conjunto("atalho=s1&ano=2026")
    segundo = conjunto("atalho=s2&ano=2026")
    ano = conjunto("atalho=ano&ano=2026")
    assert _numeros(primeiro) == ["62"]
    assert sorted(_numeros(segundo)) == ["61", "63"]
    assert sorted(_numeros(primeiro) + _numeros(segundo)) == sorted(_numeros(ano))


def test_a_situacao_e_a_do_instante_e_nao_a_do_fim_do_periodo(tres_editais):
    """FR-2565: o 62 é do 1º semestre, e o resultado definitivo dele, de outubro, está aqui."""
    c = ler(conjunto("atalho=s1&ano=2026"))
    assert c.marcos_definitivos == 2
    texto = texto_do_documento(c)
    assert "O período escolheu os Editais. A situação de cada um é a de 24/10/2026, 13h10" in texto
    assert rc.TITULO_DA_SERIE in texto and "podem passar do período" in texto
    assert "no semestre" not in texto


def test_ano_do_numero_e_primeira_publicacao_sao_criterios_diferentes(tres_editais):
    """O 62 renumerado para 2025 segue publicado em 2026: entra por publicação, não por número."""
    Edital.objects.filter(pk=tres_editais["62"].edital.pk).update(year=2025)
    assert "62" in _numeros(conjunto("atalho=ano&ano=2026"))
    assert "62" not in _numeros(conjunto("criterio=numero&ano=2026"))
    assert "62" in _numeros(conjunto("criterio=numero&ano=2025"))


def test_edital_nao_publicado_fica_fora_com_o_motivo(tres_editais, em_elaboracao):
    c = conjunto(f"criterio=numero&ano={em_elaboracao.year}")
    assert em_elaboracao not in c.incluidos
    assert (em_elaboracao, "em elaboração") in c.fora


def test_desmarcar_retira_e_o_relatorio_diz_quais(tres_editais):
    e61, e63 = tres_editais["61"].edital, tres_editais["63"].edital
    c = conjunto(f"atalho=s2&ano=2026&escolha=1&edital={e61.pk}")
    assert _numeros(c) == ["61"] and list(c.retirados) == [e63]
    assert "Retirados por escolha 63/2026" in texto_do_documento(ler(c))


def test_escolha_manual_e_identificador_de_outro_escopo(tres_editais):
    e62 = tres_editais["62"].edital
    alheio = "00000000-0000-0000-0000-000000000099"
    c = conjunto(f"criterio=manual&busca=xyz&edital={e62.pk}&edital={alheio}")
    assert _numeros(c) == ["62"], "o marcado vale fora da busca, e o alheio não volta"
    outra = ator_institucional("o", "visao:consultar", escopo="outra-unidade")
    assert conjunto(f"criterio=manual&edital={e62.pk}", ator=outra).incluidos == ()


@pytest.mark.django_db(transaction=True)
def test_a_leitura_do_conjunto_ve_um_instante_so():
    """FR-2564: todos os Editais lidos na mesma transação em `REPEATABLE READ`."""
    montar_cenario(final="sem-pendencia", numero="62", publicado_em=dia(10, 2, 9))
    escolhido = conjunto("atalho=s1&ano=2026")
    unidade = Unidade.objects.get(codigo="cefor")
    with CaptureQueriesContext(connection) as consultas:
        rc.ler(escolhido, agora=REFERENCIA, unidade=unidade)
    comandos = [q["sql"] for q in consultas.captured_queries]
    assert comandos[:2] == ["BEGIN", "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"]
    assert sum(1 for sql in comandos if sql == "BEGIN") == 1
