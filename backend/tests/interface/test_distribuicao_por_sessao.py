"""A Distribuição por sessão da agenda: dia, banca, horário e o lote que a atribui (179, FR-8204).

O caso do pedido: 43 pessoas, 3 bancas, 2 dias, 6 avaliadores, dupla avaliação. Com o filtro de
sessão, cada banca de cada dia é uma submissão — seis ao todo —, e ninguém fica em dois lugares
(SC-2841). Sem agenda, a tela é a de antes.
"""

import re
from datetime import date, time

import pytest
from django.urls import reverse

from processo_seletivo.avaliacoes.application import programacao
from processo_seletivo.avaliacoes.models import Atribuicao
from tests.fixtures.avaliacoes_com_agenda import agenda, comissao, por_sessao
from tests.fixtures.comissao import inscrever
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def edital_dupla(db, api_client, manager_headers, process_payload):
    """O Processo A com dupla avaliação na Etapa: o caso do pedido. Não convive com `edital_a`.

    Duas avaliações sem regra de combinação só existem no acervo depois da `046` (`FR-746`), e é
    como acervo que a `012` as publica nos testes; a distribuição não muda por isso.
    """
    from tests.fixtures.comissao import publicar_processo_com_etapas

    return publicar_processo_com_etapas(
        api_client, manager_headers, process_payload, avaliacoes=2, como_acervo=True
    )


@pytest.fixture
def presidente(client, seletor_ligado):
    identificar(client, "carlos", ["gestor"])
    return client


def _tela(edital, etapa, **filtros):
    url = reverse("interface:distribuicao", args=[edital.id, etapa])
    if filtros:
        url += "?" + "&".join(f"{k}={v}" for k, v in filtros.items())
    return url


def _sessao(presidente, edital, etapa, dia, banca):
    corpo = presidente.get(_tela(edital, etapa, dia=dia, banca=banca)).content.decode()
    return corpo, re.findall(r'name="inscricao_id" value="([^"]+)"', corpo)


def test_sem_agenda_a_tela_nao_tem_filtro_de_sessao_nem_horario(presidente, edital_a, etapa_a2):
    inscrever(edital_a, 2)
    corpo = presidente.get(_tela(edital_a, etapa_a2)).content.decode()
    assert 'name="dia"' not in corpo and ">Horário<" not in corpo


def test_com_agenda_a_tela_tem_dia_banca_e_horario(presidente, gestor, edital_a, etapa_a2):
    inscrever(edital_a, 4)
    agenda(gestor, edital_a, etapa_a2, quantas_bancas=2)
    corpo = presidente.get(_tela(edital_a, etapa_a2)).content.decode()
    assert 'name="dia"' in corpo and 'name="banca"' in corpo
    assert ">Horário<" in corpo
    assert "Banca 01" in corpo and "08:00–08:10" in corpo
    assert "Horários da agenda em montagem" not in corpo


def test_em_montagem_a_tela_avisa(presidente, gestor, edital_a, etapa_a2):
    inscrever(edital_a, 2)
    agenda(gestor, edital_a, etapa_a2, publicar=False)
    corpo = presidente.get(_tela(edital_a, etapa_a2)).content.decode()
    assert "Horários da agenda em montagem" in corpo


def test_o_filtro_recorta_a_sessao_em_ordem_de_horario(presidente, gestor, edital_a, etapa_a2):
    inscrever(edital_a, 6)
    agenda(gestor, edital_a, etapa_a2, quantas_bancas=2)
    sessoes = por_sessao(edital_a, etapa_a2)
    (dia, banca_nome) = sorted(sessoes)[1]
    banca_id = re.search(
        rf'<option value="([^"]+)"[^>]*>{banca_nome}</option>',
        presidente.get(_tela(edital_a, etapa_a2)).content.decode(),
    ).group(1)
    _, ids = _sessao(presidente, edital_a, etapa_a2, dia.isoformat(), banca_id)
    assert ids == [str(i.id) for i in sessoes[(dia, banca_nome)]]


def test_quarenta_e_tres_por_sessao_sem_conflito(presidente, gestor, edital_dupla, etapa_a1):
    """SC-2841: o caso do pedido, pela tela — 43 pessoas, 3 bancas, 6 avaliadores, dupla.

    A dupla avaliação da fixture é da primeira Etapa, cujo Evento é um dia só (01/09/2026): por isso
    é um dia, com a manhã inteira, e três sessões. Com dois dias seriam seis; o gesto é o mesmo.
    """
    inscrever(edital_dupla, 43)
    agenda(
        gestor,
        edital_dupla,
        etapa_a1,
        quantas_bancas=3,
        dias=(date(2026, 9, 1),),
        janelas=((time(8), time(12)),),
    )
    membros = comissao(
        gestor, edital_dupla, etapa_a1, ["ana", "bruno", "carla", "davi", "elisa", "fabio"]
    )
    duplas = [("ana", "bruno"), ("carla", "davi"), ("elisa", "fabio")]
    corpo = presidente.get(_tela(edital_dupla, etapa_a1)).content.decode()
    bancas = {
        nome: valor
        for valor, nome in re.findall(
            r'<option value="([0-9a-f-]{36})"[^>]*>(Banca \d+)</option>', corpo
        )
    }
    sessoes = por_sessao(edital_dupla, etapa_a1)
    assert len(sessoes) == 3
    for dia, banca_nome in sorted(sessoes):
        dupla = duplas[int(banca_nome.split()[-1]) - 1]
        filtros = {"dia": dia.isoformat(), "banca": bancas[banca_nome]}
        pagina, ids = _sessao(presidente, edital_dupla, etapa_a1, **filtros)
        assert len(ids) == len(sessoes[(dia, banca_nome)])
        chave = re.search(r'name="chave_idempotencia" value="([^"]+)"', pagina).group(1)
        resposta = presidente.post(
            _tela(edital_dupla, etapa_a1, **filtros),
            {
                "acao": "distribuir",
                "chave_idempotencia": chave,
                "membro_id": [str(membros[s].id) for s in dupla],
                "inscricao_id": ids,
            },
        )
        assert resposta.status_code == 302
    assert (
        Atribuicao.objects.filter(edital=edital_dupla, etapa_id=etapa_a1, ativo=True).count() == 86
    )
    assert programacao.conflitos_da_etapa(edital_dupla, etapa_a1) == []


def test_a_paginacao_preserva_a_sessao(presidente, gestor, edital_a, etapa_a2):
    inscrever(edital_a, 2)
    agenda(gestor, edital_a, etapa_a2)
    corpo = presidente.get(_tela(edital_a, etapa_a2, dia="2026-11-23")).content.decode()
    assert 'value="2026-11-23" selected' in corpo


def test_sem_a_base_da_gestao_da_comissao_a_recusa_de_hoje(
    client, seletor_ligado, edital_a, etapa_a2, gestor
):
    inscrever(edital_a, 2)
    agenda(gestor, edital_a, etapa_a2)
    identificar(client, "joao", ["avaliador"])
    resposta = client.get(_tela(edital_a, etapa_a2, dia="2026-11-23"))
    assert resposta.status_code in (403, 404)
