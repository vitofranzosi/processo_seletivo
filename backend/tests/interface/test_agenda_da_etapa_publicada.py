"""A agenda publicada, a remarcação, a inclusão e o cancelamento na gestão (167, T069, T075).

O resumo dos avisos num número só, a falha nomeada com "Reenviar o aviso", e a frase dos avisos
desligados; "Remarcar" em cada linha, "Agendar esta pessoa" e "Cancelar o agendamento" nas seções;
a remarcação com o seletor de horário, o "de → para" e o motivo; o dia trocado sem gravar; e a
recusa sem motivo, que volta à mesma tela com a frase (FR-7233, FR-7240, UX-766, US5 1 e 8).
"""

import re

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.agendamento.application import leitura
from processo_seletivo.agendamento.models import AtoDaAgenda, HorarioPublicado
from processo_seletivo.avisos.domain import nomes as nomes_dos_avisos
from processo_seletivo.avisos.models import (
    DestinatarioDoAviso,
    ResultadoDaTentativa,
    TentativaDeEnvio,
)
from tests.fixtures.agenda_da_etapa import eliminar_na_primeira, montar_completa, publicar_agenda
from tests.fixtures.comissao import inscrever
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def presidente(client, seletor_ligado):
    identificar(client, "carlos", ["gestor"])
    return client


@pytest.fixture
def inscritas(edital_a):
    return inscrever(edital_a, 5)


@pytest.fixture
def publicada(gestor, edital_a, etapa_a2, inscritas):
    montar_completa(gestor, edital_a, etapa_a2)
    return publicar_agenda(gestor, edital_a, etapa_a2)


def url(nome, edital, etapa, *extra):
    return reverse(f"interface:{nome}", args=[edital.id, etapa, *extra])


def _campo(corpo, nome):
    return re.search(rf'name="{nome}" value="([^"]*)"', corpo).group(1)


def test_a_publicada_resume_os_avisos_e_oferece_remarcar(
    presidente, edital_a, etapa_a2, inscritas, publicada
):
    corpo = presidente.get(url("agenda-publicada", edital_a, etapa_a2)).content.decode()
    assert "0 avisos enviados. 5 na fila." in corpo
    assert "Os avisos estão na fila e saem em até um minuto" in corpo
    assert corpo.count(">Remarcar<") == 5
    assert "Documento da publicação (PDF)" in corpo


def test_a_falha_e_nomeada_com_o_reenvio(presidente, edital_a, etapa_a2, inscritas, publicada):
    horario = HorarioPublicado.objects.filter(ato=publicada).select_related("inscricao").first()
    destinatario = DestinatarioDoAviso.objects.get(aviso_id=horario.aviso_id)
    agora = timezone.now()
    tentativa = TentativaDeEnvio.objects.create(
        destinatario=destinatario, numero=1, iniciada_em=agora
    )
    ResultadoDaTentativa.objects.create(
        tentativa=tentativa, resultado=nomes_dos_avisos.FALHA_DEFINITIVA, registrado_em=agora
    )
    corpo = presidente.get(url("agenda-publicada", edital_a, etapa_a2)).content.decode()
    assert "1 não entregue" in corpo
    assert f"O aviso de {horario.inscricao.nome} não foi entregue" in corpo
    assert "A agenda vale para essa pessoa do mesmo jeito" in corpo
    assert "Reenviar o aviso" in corpo
    resposta = presidente.post(
        url("agenda-reenviar", edital_a, etapa_a2),
        {"aviso": str(horario.aviso_id), "chave_idempotencia": "ui-reenvio"},
    )
    assert resposta.status_code == 302
    corpo = presidente.get(url("agenda-publicada", edital_a, etapa_a2)).content.decode()
    assert "posto de novo na fila" in corpo
    assert "não foi entregue" not in corpo


def test_com_os_avisos_desligados_a_frase_no_lugar_do_resumo(
    presidente, edital_a, etapa_a2, inscritas, publicada, settings
):
    settings.AVISOS_AOS_CANDIDATOS = False
    corpo = presidente.get(url("agenda-publicada", edital_a, etapa_a2)).content.decode()
    assert "avisos por e-mail estão desligados" in corpo
    assert "na fila" not in corpo
    pessoa = inscritas[0]
    remarcar = presidente.get(url("agenda-remarcar", edital_a, etapa_a2, pessoa.id))
    texto = remarcar.content.decode()
    assert "Remarcar esta pessoa" in texto and "Remarcar e avisar" not in texto


def test_a_remarcacao_pela_tela(presidente, edital_a, etapa_a2, inscritas, publicada):
    pessoa = inscritas[0]
    corpo = presidente.get(url("agenda-remarcar", edital_a, etapa_a2, pessoa.id)).content.decode()
    assert "<h1>Remarcar</h1>" in corpo
    assert "Agora:" in corpo
    assert "Remarcar e avisar esta pessoa" in corpo
    assert 'name="motivo"' in corpo and "Não aparece para o candidato" in corpo
    horario = re.search(r'name="horario" value="([^"]+)"', corpo).group(1)
    chave = _campo(corpo, "chave_idempotencia")

    # Sem motivo, a mesma tela volta com a frase, e nada se grava.
    sem_motivo = presidente.post(
        url("agenda-remarcar", edital_a, etapa_a2, pessoa.id),
        {"horario": horario, "motivo": "", "chave_idempotencia": chave},
    )
    assert sem_motivo.status_code == 422
    assert "Escreva o motivo" in sem_motivo.content.decode()
    assert not AtoDaAgenda.objects.filter(especie="REMARCACAO").exists()

    resposta = presidente.post(
        url("agenda-remarcar", edital_a, etapa_a2, pessoa.id),
        {"horario": horario, "motivo": "falha de conexão", "chave_idempotencia": f"{chave}-2"},
    )
    assert resposta.status_code == 302
    corpo = presidente.get(resposta["Location"]).content.decode()
    assert "Remarcação feita" in corpo
    assert "remarcado em" in corpo
    assert AtoDaAgenda.objects.filter(especie="REMARCACAO").count() == 1


def test_trocar_o_dia_do_seletor_nao_grava_e_guarda_o_motivo(
    presidente, gestor, edital_a, etapa_a2, inscritas
):
    from processo_seletivo.agendamento.domain.horarios import Banca
    from tests.fixtures.agenda_da_etapa import DUAS_HORAS, SEG, TER, configuracao

    config = configuracao(
        dias=((SEG, DUAS_HORAS), (TER, DUAS_HORAS)),
        bancas=(Banca("nova-1", "Banca 1", "https://sala.exemplo/1", 1),),
    )
    montar_completa(gestor, edital_a, etapa_a2, config=config)
    publicar_agenda(gestor, edital_a, etapa_a2)
    pessoa = inscritas[0]
    resposta = presidente.post(
        url("agenda-remarcar", edital_a, etapa_a2, pessoa.id),
        {"ver_dia": TER.isoformat(), "motivo": "pedido aceito", "chave_idempotencia": "k"},
    )
    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    assert "pedido aceito</textarea>" in corpo
    assert TER.isoformat() in corpo
    assert not AtoDaAgenda.objects.filter(especie="REMARCACAO").exists()


def test_quem_entrou_depois_e_quem_saiu_tem_a_acao_deles(
    presidente, gestor, edital_a, etapa_a1, etapa_a2, inscritas, publicada
):
    (nova,) = inscrever(edital_a, 1, primeiro=90)
    corpo = presidente.get(url("agenda-publicada", edital_a, etapa_a2)).content.decode()
    assert "Passou a participar depois da publicação (1)" in corpo
    agendar = url("agenda-remarcar", edital_a, etapa_a2, nova.id)
    assert agendar in corpo and "Agendar esta pessoa" in corpo
    tela = presidente.get(agendar).content.decode()
    assert "<h1>Agendar</h1>" in tela and "Agendar e avisar esta pessoa" in tela

    eliminar_na_primeira(gestor, edital_a, etapa_a1, [inscritas[1]])
    corpo = presidente.get(url("agenda-publicada", edital_a, etapa_a2)).content.decode()
    cancelar = url("agenda-cancelar", edital_a, etapa_a2, inscritas[1].id)
    assert cancelar in corpo and "Cancelar o agendamento" in corpo
    tela = presidente.get(cancelar).content.decode()
    resposta = presidente.post(
        cancelar,
        {"motivo": "eliminada", "chave_idempotencia": _campo(tela, "chave_idempotencia")},
    )
    assert resposta.status_code == 302
    corpo = presidente.get(resposta["Location"]).content.decode()
    assert "Agendamento cancelado" in corpo
    vigentes = {v.inscricao_id for v in leitura.vigentes_da_agenda(publicada.agenda)}
    assert inscritas[1].id not in vigentes


def test_sem_horario_livre_a_tela_leva_a_configuracao(presidente, gestor, edital_a, etapa_a2):
    from processo_seletivo.agendamento.domain.horarios import Banca
    from tests.fixtures.agenda_da_etapa import SEG, UMA_HORA, configuracao

    # Quatro horários e quatro pessoas: publicada, nenhum horário fica livre.
    quatro = inscrever(edital_a, 4)
    montar_completa(
        gestor,
        edital_a,
        etapa_a2,
        config=configuracao(
            dias=((SEG, UMA_HORA),),
            bancas=(Banca("nova-1", "Banca 1", "https://sala.exemplo/1", 1),),
        ),
    )
    publicar_agenda(gestor, edital_a, etapa_a2)
    tela = presidente.get(url("agenda-remarcar", edital_a, etapa_a2, quatro[0].id))
    corpo = tela.content.decode()
    assert "Não há horário livre" in corpo
    assert url("agenda-configurar", edital_a, etapa_a2) in corpo
    assert "Remarcar e avisar esta pessoa" not in corpo


def test_a_porta_nega_fora_do_escopo(client, seletor_ligado, edital_a, etapa_a2, publicada):
    identificar(client, "estranha", ["consulta"])
    pessoa = HorarioPublicado.objects.filter(ato=publicada).first().inscricao_id
    for nome in ("agenda-remarcar", "agenda-cancelar"):
        assert client.get(url(nome, edital_a, etapa_a2, pessoa)).status_code in (403, 404)
    assert client.post(url("agenda-reenviar", edital_a, etapa_a2), {}).status_code in (403, 404)
