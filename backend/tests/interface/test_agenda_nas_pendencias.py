"""A agenda como pendência no Centro e em Minhas atividades (167, entrega D, T083, T-023).

"Montar a agenda" enquanto falta horário a quem participa — ou sobra a quem não participa mais —, e
"Publicar a agenda" quando a montagem está completa; nada depois de publicada, e nada na Etapa que
não tem agenda. A regra é pura (`situacao_da_agenda`) e se prova sem banco; a leitura se prova pelas
duas telas, como a presidência as lê, e pelo custo: as agendas custam uma consulta por Edital, e o
Edital sem participante não paga nem essa.
"""

from datetime import date

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.agendamento.application import configurar
from processo_seletivo.agendamento.application.leitura import EstadoDaAgenda
from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.interface import andamento as a
from processo_seletivo.interface import centro as cc
from tests.fixtures.agenda_da_etapa import (
    UMA_HORA,
    configuracao,
    montar_completa,
    publicar_agenda,
)
from tests.fixtures.comissao import constituir, inscrever
from tests.interface.conftest import identificar

MONTAR = "/montar"
#: A primeira Etapa da fixture tem Evento num dia só, 01/09/2026; a segunda não tem Evento.
DIA_DA_A1 = ((date(2026, 9, 1), UMA_HORA),)
CONFERIR = "/conferir"


def fatos(participantes, agenda, **campos):
    return {
        "participantes": set(participantes),
        "agenda": agenda,
        "url_de_montar": MONTAR,
        "url_de_conferir": CONFERIR,
        **campos,
    }


# --- a regra, pura ------------------------------------------------------------------------------


def test_sem_agenda_nao_ha_providencia():
    """A Etapa que não pede comparecimento não tem agenda, e não é cobrada (D-001)."""
    assert a.situacao_da_agenda(fatos({"i1"}, None)) is None


def test_publicada_nao_ha_providencia():
    assert a.situacao_da_agenda(fatos({"i1"}, EstadoDaAgenda(publicada=True))) is None


def test_sem_participante_nao_ha_providencia():
    assert a.situacao_da_agenda(fatos(set(), EstadoDaAgenda(False, frozenset()))) is None


def test_falta_horario_e_montar_com_o_link_da_montagem():
    celula = a.situacao_da_agenda(
        fatos({"i1", "i2", "i3"}, EstadoDaAgenda(False, frozenset({"i1"})))
    )
    assert celula.situacao == a.PENDENTE
    assert celula.natureza == a.AGENDA
    assert celula.ato == a.ATO_DE_MONTAR_A_AGENDA
    assert celula.responsavel == a.CONDUZ
    assert celula.url == MONTAR
    assert celula.nota == "1 de 3 com horário"
    assert celula.contagem == 2


def test_horario_de_quem_nao_participa_mais_tambem_e_montar():
    """A conferência recusa os dois (`conferir._impedimentos`); os dois se resolvem na montagem."""
    celula = a.situacao_da_agenda(fatos({"i1"}, EstadoDaAgenda(False, frozenset({"i1", "i9"}))))
    assert celula.ato == a.ATO_DE_MONTAR_A_AGENDA
    assert celula.url == MONTAR
    assert celula.nota == "1 de 1 com horário · 1 horário de quem não participa mais"


def test_montada_e_publicar_com_o_link_da_conferencia():
    celula = a.situacao_da_agenda(
        fatos({"i1", "i2"}, EstadoDaAgenda(False, frozenset({"i1", "i2"})))
    )
    assert celula.ato == a.ATO_DE_PUBLICAR_A_AGENDA
    assert celula.url == CONFERIR
    assert celula.nota == "2 de 2 com horário"


def test_a_agenda_mora_na_fase_da_etapa():
    """Na Avaliação, e nas vagas quando a Etapa é governada pelo corte, como os outros atos dela."""
    assert a.AGENDA in cc.NATUREZAS_CONHECIDAS
    celula = a.situacao_da_agenda(fatos({"i1"}, EstadoDaAgenda(False, frozenset())))
    from processo_seletivo.interface.providencias import Providencia

    providencia = Providencia.da_celula(
        celula, onde="Entrevista", sua=True, chave=("etapa", "e1", a.AGENDA)
    )
    assert cc.fase_da_providencia(providencia, set()) == "avaliacao"
    assert cc.fase_da_providencia(providencia, {"e1"}) == "vagas"


# --- pelas telas ------------------------------------------------------------------------------


@pytest.fixture
def presidencia(gestor, edital_a, client, seletor_ligado):
    """`maria` preside o Processo A, que tem três inscrições enviadas nas duas Etapas."""
    constituir(gestor, edital_a.processo, [("maria", Funcao.PRESIDENTE)], prefixo="agenda-d")
    inscrever(edital_a, 3)
    identificar(client, "maria", [])
    return client


def _rota(segmento, edital, etapa):
    return reverse(f"interface:agenda-{segmento}", args=[edital.id, etapa])


def _centro(client, edital):
    resposta = client.get(reverse("interface:detalhe", args=[edital.id]))
    assert resposta.status_code == 200
    return resposta.context["centro"], resposta.content.decode()


def _minhas(client):
    resposta = client.get(reverse("interface:minhas-etapas"))
    assert resposta.status_code == 200
    return resposta.context["atividades"], resposta.content.decode()


def _da_agenda(itens):
    return {(i.p.onde, i.p.ato, i.p.url) for i in itens if i.p.natureza == a.AGENDA}


@pytest.mark.django_db(transaction=True)
def test_sem_montar_e_montada_aparecem_no_centro_e_em_minhas_atividades(
    presidencia, gestor, edital_a, etapa_a1, etapa_a2
):
    """O critério da entrega: uma Etapa com a agenda por montar, outra montada e não publicada."""
    configurar.salvar(
        actor=gestor, edital=edital_a, etapa_id=etapa_a1, configuracao=configuracao(DIA_DA_A1)
    )
    montar_completa(gestor, edital_a, etapa_a2)
    montar = _rota("montar", edital_a, etapa_a1)
    conferir = _rota("conferir", edital_a, etapa_a2)

    centro, html = _centro(presidencia, edital_a)
    atos = {(ato, url) for _onde, ato, url in _da_agenda(centro.itens)}
    assert atos == {(a.ATO_DE_MONTAR_A_AGENDA, montar), (a.ATO_DE_PUBLICAR_A_AGENDA, conferir)}
    assert all(i.fase_chave == "avaliacao" for i in centro.itens if i.p.natureza == a.AGENDA)
    assert f'href="{montar}"' in html and f'href="{conferir}"' in html

    atividades, html = _minhas(presidencia)
    linhas = {
        (grupo.ato, grupo.providencia.url)
        for grupo in atividades.para_fazer
        if grupo.providencia.natureza == a.AGENDA
    }
    assert linhas == {(a.ATO_DE_MONTAR_A_AGENDA, montar), (a.ATO_DE_PUBLICAR_A_AGENDA, conferir)}
    assert f'href="{montar}"' in html and f'href="{conferir}"' in html


@pytest.mark.django_db(transaction=True)
def test_publicada_sai_das_pendencias(presidencia, gestor, edital_a, etapa_a2):
    montar_completa(gestor, edital_a, etapa_a2)
    publicar_agenda(gestor, edital_a, etapa_a2, chave="publicar-agenda-d")

    centro, _ = _centro(presidencia, edital_a)
    assert not _da_agenda(centro.itens)
    atividades, _ = _minhas(presidencia)
    assert not [g for g in atividades.para_fazer if g.providencia.natureza == a.AGENDA]


@pytest.mark.django_db(transaction=True)
def test_sem_agenda_nenhuma_etapa_pede_agenda(presidencia, edital_a):
    centro, _ = _centro(presidencia, edital_a)
    assert not _da_agenda(centro.itens)


@pytest.mark.django_db(transaction=True)
def test_quem_nao_conduz_ve_a_pendencia_sem_o_link(presidencia, gestor, edital_a, etapa_a2, client):
    """Quem só consulta lê que falta a agenda, de quem é, e não recebe a porta (FR-4055)."""
    configurar.salvar(actor=gestor, edital=edital_a, etapa_id=etapa_a2, configuracao=configuracao())
    identificar(client, "auditora", ["auditor"])
    centro, html = _centro(client, edital_a)
    itens = [i for i in centro.itens if i.p.natureza == a.AGENDA]
    assert [i.p.ato for i in itens] == [a.ATO_DE_MONTAR_A_AGENDA]
    assert not itens[0].p.sua and itens[0].p.url == ""
    assert _rota("montar", edital_a, etapa_a2) not in html


@pytest.mark.django_db(transaction=True)
def test_as_agendas_custam_uma_consulta_por_edital(gestor, edital_a, etapa_a1, etapa_a2):
    """Duas agendas sem publicar: uma consulta para as agendas, outra para os agendamentos."""
    inscrever(edital_a, 3)
    configurar.salvar(
        actor=gestor, edital=edital_a, etapa_id=etapa_a1, configuracao=configuracao(DIA_DA_A1)
    )
    montar_completa(gestor, edital_a, etapa_a2)
    with CaptureQueriesContext(connection) as capturadas:
        andamento = a.do_edital(edital_a, gestor)
    assert andamento is not None
    das_agendas = [q["sql"] for q in capturadas if '"agendamento_' in q["sql"]]
    assert len(das_agendas) == 2, das_agendas


@pytest.mark.django_db(transaction=True)
def test_o_edital_sem_participante_nao_le_a_agenda(gestor, edital_a):
    with CaptureQueriesContext(connection) as capturadas:
        a.do_edital(edital_a, gestor)
    assert not [q["sql"] for q in capturadas if '"agendamento_' in q["sql"]]
