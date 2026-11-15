"""O horário publicado na tela da Ocorrência, só como informação (167, entrega D, T084, R-23).

A agenda nunca registra ausência (FR-7250): quem faltou continua tendo a Ocorrência, e o horário ao
lado do nome é para a presidência conferir o que a pessoa perdeu, sem abrir outra tela. Os casos
provam que a coluna só existe com agenda publicada, que diz o horário vigente — e "sem horário" de
quem teve o seu cancelado —, e que registrar a Ocorrência não toca nada da agenda.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.agendamento.application import atos_individuais, leitura
from processo_seletivo.agendamento.domain.horarios import horario_curto
from processo_seletivo.agendamento.models import AtoDaAgenda, HorarioPublicado
from processo_seletivo.resultados.models import ResultadoEtapa
from tests.fixtures.agenda_da_etapa import montar_completa, publicar_agenda
from tests.fixtures.comissao import inscrever
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]

COLUNA = '<th scope="col">Horário publicado</th>'


@pytest.fixture
def presidente(client, seletor_ligado):
    identificar(client, "carlos", ["gestor"])
    return client


@pytest.fixture
def inscritas(edital_a):
    return inscrever(edital_a, 3)


def url(edital, etapa):
    return reverse("interface:registrar-ocorrencia", args=[edital.id, etapa])


def _celula_da(corpo, inscricao):
    linha = re.search(rf'id="ocorrencia-{inscricao.id}".*?</tr>', corpo, flags=re.S).group(0)
    return re.findall(r"<td>(.*?)</td>", linha, flags=re.S)[-1]


def test_sem_agenda_publicada_nao_ha_coluna(presidente, gestor, edital_a, etapa_a2, inscritas):
    """Montada e não publicada ainda não é horário de ninguém: o rascunho não aparece."""
    montar_completa(gestor, edital_a, etapa_a2)
    corpo = presidente.get(url(edital_a, etapa_a2)).content.decode()
    assert COLUNA not in corpo
    assert "Horário publicado" not in corpo


def test_a_coluna_diz_o_horario_vigente_de_cada_pessoa(
    presidente, gestor, edital_a, etapa_a2, inscritas
):
    montar_completa(gestor, edital_a, etapa_a2)
    ato = publicar_agenda(gestor, edital_a, etapa_a2)
    corpo = presidente.get(url(edital_a, etapa_a2)).content.decode()
    assert COLUNA in corpo
    assert "Ele não registra nada: a ausência se registra aqui, como ocorrência." in corpo
    for horario in HorarioPublicado.objects.filter(ato=ato).select_related("inscricao"):
        assert horario_curto(horario.inicio) in _celula_da(corpo, horario.inscricao)


def test_quem_passou_a_participar_depois_aparece_sem_horario(
    presidente, gestor, edital_a, etapa_a2, inscritas
):
    montar_completa(gestor, edital_a, etapa_a2)
    publicar_agenda(gestor, edital_a, etapa_a2)
    (nova,) = inscrever(edital_a, 1, primeiro=90)
    corpo = presidente.get(url(edital_a, etapa_a2)).content.decode()
    assert "Sem horário publicado" in _celula_da(corpo, nova)
    assert "Sem horário publicado" not in _celula_da(corpo, inscritas[0])


def test_o_horario_cancelado_nao_e_mais_horario(gestor, edital_a, etapa_a1, etapa_a2, inscritas):
    """O vigente é o que vale: cancelado o agendamento, a leitura não devolve horário à pessoa.

    Pela leitura, e não pela tela: para cancelar, a pessoa precisa ter deixado de participar, e a
    Ocorrência na primeira Etapa, que a tira, dá Resultado à primeira — e as outras passam a
    aguardá-lo, e a tela da segunda fica vazia (a partição da entrega A).
    """
    from tests.fixtures.agenda_da_etapa import eliminar_na_primeira

    montar_completa(gestor, edital_a, etapa_a2)
    publicar_agenda(gestor, edital_a, etapa_a2)
    ids = [inscricao.id for inscricao in inscritas]
    assert set(leitura.horarios_na_ocorrencia(edital_a, etapa_a2, ids)) == {str(i) for i in ids}
    eliminar_na_primeira(gestor, edital_a, etapa_a1, [inscritas[0]])
    atos_individuais.cancelar(
        actor=gestor,
        edital=edital_a,
        etapa_id=etapa_a2,
        inscricao_id=inscritas[0].id,
        motivo="eliminada na primeira",
        idempotency_key="cancelar-d",
    )
    depois = leitura.horarios_na_ocorrencia(edital_a, etapa_a2, ids)
    assert str(inscritas[0].id) not in depois
    assert str(inscritas[1].id) in depois


def test_a_confirmacao_mostra_o_horario_e_a_ocorrencia_nao_toca_a_agenda(
    presidente, gestor, edital_a, etapa_a2, inscritas
):
    montar_completa(gestor, edital_a, etapa_a2)
    ato = publicar_agenda(gestor, edital_a, etapa_a2)
    pessoa = inscritas[0]
    horario = HorarioPublicado.objects.get(ato=ato, inscricao=pessoa)
    antes = (AtoDaAgenda.objects.count(), HorarioPublicado.objects.count())

    revisar = presidente.post(
        url(edital_a, etapa_a2),
        {"motivo": "não compareceu", "inscricao_id": [str(pessoa.id)], "chave_idempotencia": "k"},
    )
    corpo = revisar.content.decode()
    assert f"horário publicado: {horario_curto(horario.inicio)}" in corpo

    chave = re.search(r'name="chave_idempotencia" value="([^"]+)"', corpo).group(1)
    resposta = presidente.post(
        url(edital_a, etapa_a2),
        {
            "motivo": "não compareceu",
            "inscricao_id": [str(pessoa.id)],
            "confirmar": "1",
            "chave_idempotencia": chave,
        },
    )
    assert resposta.status_code == 302
    assert ResultadoEtapa.vigentes.filter(inscricao=pessoa, etapa_id=etapa_a2).exists()
    # Nenhum ato, nenhum horário: a agenda não registra ausência, e a Ocorrência não a muda.
    assert (AtoDaAgenda.objects.count(), HorarioPublicado.objects.count()) == antes
    assert leitura.horarios_na_ocorrencia(edital_a, etapa_a2, [pessoa.id])[str(pessoa.id)]


def test_a_banca_so_se_diz_quando_ha_mais_de_uma(presidente, gestor, edital_a, etapa_a2, inscritas):
    """Como na página pública e na área do candidato: com uma banca só, a banca não distingue."""
    from processo_seletivo.agendamento.domain.horarios import Banca
    from tests.fixtures.agenda_da_etapa import DUAS_HORAS, SEG, configuracao

    duas = (
        Banca("nova-1", "Banca 1", "https://sala.exemplo/1", 1),
        Banca("nova-2", "Banca 2", "https://sala.exemplo/2", 2),
    )
    montar_completa(
        gestor, edital_a, etapa_a2, config=configuracao(dias=((SEG, DUAS_HORAS),), bancas=duas)
    )
    ato = publicar_agenda(gestor, edital_a, etapa_a2)
    corpo = presidente.get(url(edital_a, etapa_a2)).content.decode()
    for horario in HorarioPublicado.objects.filter(ato=ato).select_related("inscricao"):
        assert f"· {horario.banca_nome}" in _celula_da(corpo, horario.inscricao)


def test_com_uma_banca_so_o_horario_vem_sem_ela(presidente, gestor, edital_a, etapa_a2, inscritas):
    montar_completa(gestor, edital_a, etapa_a2)
    publicar_agenda(gestor, edital_a, etapa_a2)
    corpo = presidente.get(url(edital_a, etapa_a2)).content.decode()
    assert "Banca 1" not in _celula_da(corpo, inscritas[0])
