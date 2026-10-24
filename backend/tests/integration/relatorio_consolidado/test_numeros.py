"""Cada número do consolidado é a soma do que o relatório de cada Edital diz (100, SC-939).

E vagas, inscrições e razão são as da Visão Geral (040) para o mesmo universo: as três leituras —
consolidado, relatório do Edital e Visão Geral — não podem divergir.
"""

import pytest

from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.interface import relatorio_do_edital as rel
from processo_seletivo.interface import visao_geral
from processo_seletivo.publicacoes.application.selectors import versoes_vigentes
from tests.fixtures.relatorio import REFERENCIA
from tests.integration.relatorio_consolidado.conftest import conjunto, ler

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_cada_numero_e_a_soma_dos_relatorios_de_cada_edital(tres_editais):
    escolhido = conjunto("criterio=numero&ano=2026")
    assert [e.number for e in escolhido.incluidos] == ["62", "63", "61"]
    c = ler(escolhido)
    with rel.leitura_consistente():
        fatos = [rel.fatos_do_edital(e, agora=REFERENCIA) for e in escolhido.incluidos]
    universo = [f for f in fatos if f.edital.status != "CANCELADO"]
    assert c.editais == 3 and c.cancelados == 1 and c.universo == 2
    assert c.vagas == sum(f.vagas for f in universo)
    assert c.inscricoes.valor == sum(f.inscricoes for f in universo)
    assert c.vagas_habilitadas == sum(f.vagas_habilitadas or 0 for f in universo)
    assert c.convocacoes["realizadas"] == sum(f.convocacoes.realizadas for f in universo)
    assert c.convocacoes["aceitas"] == sum(f.convocacoes.aceitas for f in universo)
    assert c.recursos.apresentados == sum(f.recursos.apresentados for f in universo)
    assert c.marcos_definitivos == sum(f.marcos_definitivos for f in universo)
    assert c.retificacoes == sum(f.retificacoes for f in universo)
    # E a contagem independente, direto da tabela: inscrições enviadas, não pessoas.
    enviadas = Inscricao.objects.filter(
        edital__in=[f.edital for f in universo], status=Inscricao.Status.SUBMETIDA
    ).count()
    assert c.inscricoes.valor == enviadas == 76


def test_vagas_inscricoes_e_razao_sao_as_da_visao_geral(tres_editais):
    c = ler(conjunto("criterio=numero&ano=2026"))
    editais = [tres_editais[n].edital for n in ("61", "62")]
    versoes = versoes_vigentes(edital_ids=[e.pk for e in editais], at=REFERENCIA)
    conteudos = {e.pk: versoes[e.pk].content for e in editais}
    contagens = visao_geral.contagens_por_edital(editais)
    linhas = [
        visao_geral.linha_do_edital(e, conteudos[e.pk], contagens.get(e.pk), REFERENCIA)
        for e in editais
    ]
    da_visao = visao_geral._consolidar(linhas, conteudos, contagens)
    assert c.vagas == da_visao.vagas.valor
    assert c.inscricoes.valor == da_visao.submetidas.valor
    assert c.razao.valor == da_visao.razao.valor


def test_cadastro_de_reserva_e_listas_sobrepostas(tres_editais):
    """O Técnico é só cadastro de reserva: fora da razão. A lista reservada repete inscrições da
    ampla: cada inscrição conta uma vez."""
    c = ler(conjunto("criterio=numero&ano=2026"))
    assert c.perfis_so_reserva == 2
    assert c.numerador == 2 * 26, "só as inscrições do Professor disputam as vagas"
    assert c.vagas_reservadas == 2, "uma vaga reservada por Edital"
    linha = next(linha for linha in c.linhas if linha.edital.number == "61")
    assert linha.inscricoes.valor == 38, "26 + 12, e não 26 + 6 da reservada + 12"
