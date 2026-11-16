"""A coerência entre a distribuição e a agenda, nas telas da gestão (179, FR-8208, FR-8215, UX-974).

Uma linha quando tudo está em ordem; o que resolver, com o caminho, quando não está. A agenda
publicada diz quem avalia cada pessoa; a conferência mostra o conflito como aviso, sem impedir.
"""

import re

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.avaliacoes.models import Atribuicao
from tests.fixtures.agenda_da_etapa import eliminar_na_primeira
from tests.fixtures.avaliacoes_com_agenda import agenda, atribuir, comissao, por_sessao
from tests.fixtures.comissao import inscrever
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def presidente(client, seletor_ligado):
    identificar(client, "carlos", ["gestor"])
    return client


def _publicada(cliente, edital, etapa):
    return cliente.get(
        reverse("interface:agenda-publicada", args=[edital.id, etapa])
    ).content.decode()


def _distribuicao(cliente, edital, etapa):
    return cliente.get(reverse("interface:distribuicao", args=[edital.id, etapa])).content.decode()


def _forcar(gestor, edital, etapa, membro, inscricoes):
    for inscricao in inscricoes:
        Atribuicao.objects.create(
            membro=membro,
            edital=edital,
            etapa_id=etapa,
            inscricao=inscricao,
            criado_em=timezone.now(),
            criado_por=gestor.subject,
        )


@pytest.fixture
def duas_bancas(gestor, edital_a, etapa_a2):
    inscrever(edital_a, 4)
    agenda(gestor, edital_a, etapa_a2, quantas_bancas=2)
    membros = comissao(gestor, edital_a, etapa_a2, ["ana", "bruno"])
    banca1, banca2 = (v for _, v in sorted(por_sessao(edital_a, etapa_a2).items()))
    return membros, banca1, banca2


def test_em_ordem_e_uma_linha_e_a_coluna_diz_quem_avalia(
    presidente, gestor, edital_a, etapa_a2, duas_bancas
):
    membros, banca1, banca2 = duas_bancas
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], banca1, chave="a")
    atribuir(gestor, edital_a, etapa_a2, [membros["bruno"]], banca2, chave="b")
    corpo = _publicada(presidente, edital_a, etapa_a2)
    assert '<h2 id="avaliadores-titulo">Quem avalia</h2>' in corpo
    assert "4 pessoas com horário, todas com quem as avalie · ninguém com duas entrevistas" in corpo
    assert ">Avaliam<" in corpo
    assert '<td class="avaliam">ana</td>' in corpo and '<td class="avaliam">bruno</td>' in corpo


def test_quem_falta_e_o_conflito_com_os_caminhos(
    presidente, gestor, edital_a, etapa_a2, duas_bancas
):
    membros, banca1, banca2 = duas_bancas
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], banca1, chave="a")
    _forcar(gestor, edital_a, etapa_a2, membros["ana"], banca2[:1])
    corpo = _publicada(presidente, edital_a, etapa_a2)
    assert "1 com avaliação distribuída a menos" in corpo
    assert "cobertura=carente" in corpo
    assert "1 conflito de horário" in corpo
    assert "ana, às 08:00 de 23/11 (Banca 01 e Banca 02)" in corpo
    assert "?dia=2026-11-23#inscricoes" in corpo
    assert "Ninguém ainda</a>" in corpo
    distribuicao = _distribuicao(presidente, edital_a, etapa_a2)
    assert "1 conflito de horário" in distribuicao
    # O detalhe fica no cartão, numa linha; em "Quem está alocado", só a marca (revisão de 16/11).
    assert '<p class="conflito-no-cartao"' in distribuicao
    assert "ana, às 08:00 de 23/11 (Banca 01 e Banca 02)" in distribuicao
    assert '<span class="marca-em-dois-lugares">em dois lugares</span>' in distribuicao
    assert "coerencia-da-agenda com-pendencia" not in distribuicao
    assert "Em dois lugares: ana tem outra entrevista às 08:00 (Banca 0" in distribuicao


def test_o_cancelamento_tira_a_pessoa_dos_conflitos(
    presidente, gestor, edital_a, etapa_a1, etapa_a2, duas_bancas
):
    from processo_seletivo.agendamento.application import atos_individuais

    membros, banca1, banca2 = duas_bancas
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], banca1, chave="a")
    _forcar(gestor, edital_a, etapa_a2, membros["ana"], banca2[:1])
    eliminar_na_primeira(gestor, edital_a, etapa_a1, banca2[:1])
    atos_individuais.cancelar(
        actor=gestor,
        edital=edital_a,
        etapa_id=etapa_a2,
        inscricao_id=banca2[0].id,
        motivo="eliminada",
        idempotency_key="cancelar",
    )
    assert "conflito de horário" not in _publicada(presidente, edital_a, etapa_a2)


def test_a_conferencia_avisa_o_conflito_sem_impedir(presidente, gestor, edital_a, etapa_a2):
    inscrever(edital_a, 4)
    agenda(gestor, edital_a, etapa_a2, quantas_bancas=2, publicar=False)
    membros = comissao(gestor, edital_a, etapa_a2, ["ana"])
    banca1, banca2 = (v for _, v in sorted(por_sessao(edital_a, etapa_a2).items()))
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], banca1[:1], chave="a")
    _forcar(gestor, edital_a, etapa_a2, membros["ana"], banca2[:1])
    corpo = presidente.get(
        reverse("interface:agenda-conferir", args=[edital_a.id, etapa_a2])
    ).content.decode()
    assert "dá a quem avalia 1 conflito de horário" in corpo
    assert "Isso não impede a publicação" in corpo
    assert "Antes de publicar, resolva" not in corpo


def test_quem_ja_nao_participa_nao_conta_como_pendencia_de_distribuicao(
    presidente, gestor, edital_a, etapa_a1, etapa_a2, duas_bancas
):
    """Revisão da 179: quem tem horário e deixou de participar se cancela, não se distribui."""
    membros, banca1, banca2 = duas_bancas
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], banca1, chave="a")
    atribuir(gestor, edital_a, etapa_a2, [membros["bruno"]], banca2[:1], chave="b")
    eliminar_na_primeira(gestor, edital_a, etapa_a1, banca2[1:])
    corpo = _publicada(presidente, edital_a, etapa_a2)
    assert "com avaliação distribuída a menos" not in corpo
    assert re.search(r"Tem horário e não participa mais \(\d+\)", corpo)


def test_a_distribuicao_mostra_so_o_conflito_e_nao_repete_a_cobertura(
    presidente, gestor, edital_a, etapa_a2, duas_bancas
):
    membros, banca1, _ = duas_bancas
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], banca1, chave="a")
    corpo = _distribuicao(presidente, edital_a, etapa_a2)
    assert "com avaliação distribuída a menos" not in corpo
    assert "todas com quem as avalie" not in corpo
