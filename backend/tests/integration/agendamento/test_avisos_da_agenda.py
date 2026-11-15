"""Os avisos da agenda (167, T068, FR-7230 a FR-7233, SC-2395, SC-2396, US4, `D-011`).

Um `Aviso` e um `DestinatarioDoAviso` por pessoa publicada, ligados ao `HorarioPublicado`; a
confirmação não envia; o despacho envia uma mensagem por pessoa; a confirmação repetida não cria
aviso; com a chave da `066` desligada, nenhum aviso — nem depois de ligá-la; o reenvio da `066`
recusa a origem nova, e o da agenda repete o texto da pessoa num aviso filho. FR-7232: uma pessoa,
um aviso por ato — o `uq_horario_publicado_por_ato` e o `uq_horario_publicado_aviso`.
"""

import pytest
from django.core import mail
from django.db import IntegrityError, connection, transaction
from django.utils import timezone

from processo_seletivo.agendamento.application import avisos_da_agenda, reenviar
from processo_seletivo.agendamento.domain import nomes
from processo_seletivo.agendamento.models import HorarioPublicado
from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.avisos.application.confirmar import recusar_reenvio_da_pendencia
from processo_seletivo.avisos.application.despacho import despachar
from processo_seletivo.avisos.domain import nomes as nomes_dos_avisos
from processo_seletivo.avisos.models import (
    Aviso,
    DestinatarioDoAviso,
    ResultadoDaTentativa,
    TentativaDeEnvio,
)
from processo_seletivo.shared.api.problems import DomainError
from tests.fixtures.agenda_da_etapa import montar_completa, publicar_agenda

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def test_a_publicacao_cria_um_aviso_por_pessoa_ligado_ao_horario(edital_a, inscricoes, publicada):
    horarios = list(HorarioPublicado.objects.filter(ato=publicada).select_related("aviso"))
    assert len(horarios) == len(inscricoes)
    assert all(h.aviso is not None for h in horarios)
    avisos = Aviso.objects.filter(origem=nomes_dos_avisos.AGENDA)
    assert avisos.count() == len(inscricoes)
    for horario in horarios:
        aviso = horario.aviso
        assert aviso.marco_id is None
        assert aviso.motivo == nomes_dos_avisos.PRIMEIRO_AVISO
        assert aviso.referencia_da_publicacao.startswith("Agenda da ")
        assert aviso.perfil_id == horario.inscricao.profile_id
        destinatario = DestinatarioDoAviso.objects.get(aviso=aviso)
        assert destinatario.inscricao_id == horario.inscricao_id
        assert destinatario.endereco == horario.inscricao.email
        assert horario.inscricao.protocolo in aviso.corpo


def test_a_sala_de_cada_aviso_e_a_da_pessoa(gestor, edital_a, etapa_a2, inscricoes):
    from processo_seletivo.agendamento.domain.horarios import Banca
    from tests.fixtures.agenda_da_etapa import DUAS_HORAS, SEG, configuracao

    config = configuracao(
        dias=((SEG, DUAS_HORAS),),
        bancas=(
            Banca("nova-1", "Banca 1", "https://sala.exemplo/um", 1),
            Banca("nova-2", "Banca 2", "https://sala.exemplo/dois", 2),
        ),
    )
    montar_completa(gestor, edital_a, etapa_a2, config=config)
    ato = publicar_agenda(gestor, edital_a, etapa_a2)
    for horario in HorarioPublicado.objects.filter(ato=ato).select_related("aviso", "banca"):
        outra = "dois" if horario.banca.nome == "Banca 1" else "um"
        assert horario.banca.acesso in horario.aviso.corpo
        assert f"https://sala.exemplo/{outra}" not in horario.aviso.corpo


def test_a_confirmacao_nao_envia_e_o_despacho_envia_uma_por_pessoa(inscricoes, publicada):
    mail.outbox.clear()
    assert mail.outbox == []
    despachar()
    assert len(mail.outbox) == len(inscricoes)
    destinos = sorted(m.to[0] for m in mail.outbox)
    assert destinos == sorted(i.email for i in inscricoes)
    assert len(set(destinos)) == len(destinos)
    assert all(m.subject.startswith("Seu horário:") for m in mail.outbox)


def test_a_confirmacao_repetida_nao_cria_aviso(gestor, edital_a, etapa_a2, inscricoes, publicada):
    antes = Aviso.objects.count()
    # A segunda confirmação leva a assinatura que a tela tinha, com a mesma chave e com outra.
    assinatura = publicada.assinatura_conferida
    for chave in ("publicar-agenda", "outra-chave"):
        assert publicar_agenda(gestor, edital_a, etapa_a2, chave=chave, assinatura=assinatura) == (
            publicada
        )
    assert Aviso.objects.count() == antes


def test_a_trilha_conta_os_avisos_e_nao_os_destinatarios(inscricoes, publicada):
    registro = RegistroAuditoria.objects.get(operation=nomes.PUBLICACAO_DA_AGENDA)
    assert registro.detalhe["avisos"] == len(inscricoes)
    texto = str(registro.detalhe)
    assert "@" not in texto
    assert "sala.exemplo" not in texto


def test_com_a_chave_desligada_publica_sem_aviso_nem_depois(
    gestor, edital_a, etapa_a2, inscricoes, settings
):
    settings.AVISOS_AOS_CANDIDATOS = False
    montar_completa(gestor, edital_a, etapa_a2)
    ato = publicar_agenda(gestor, edital_a, etapa_a2)
    assert HorarioPublicado.objects.filter(ato=ato).count() == len(inscricoes)
    assert not HorarioPublicado.objects.filter(ato=ato, aviso__isnull=False).exists()
    assert not Aviso.objects.exists()
    # Ligar a chave depois não cria aviso de ato anterior: não há varredura que os procure.
    settings.AVISOS_AOS_CANDIDATOS = True
    mail.outbox.clear()
    despachar()
    assert mail.outbox == []
    assert not Aviso.objects.exists()


def test_o_reenvio_da_066_recusa_o_aviso_de_agenda(publicada):
    aviso = Aviso.objects.filter(origem=nomes_dos_avisos.AGENDA).first()
    with pytest.raises(DomainError) as recusa:
        recusar_reenvio_da_pendencia(aviso)
    assert recusa.value.code == nomes_dos_avisos.AVISO_DE_AGENDA_SEM_REENVIO


def _falhar(aviso):
    destinatario = DestinatarioDoAviso.objects.get(aviso=aviso)
    agora = timezone.now()
    tentativa = TentativaDeEnvio.objects.create(
        destinatario=destinatario, numero=1, iniciada_em=agora
    )
    ResultadoDaTentativa.objects.create(
        tentativa=tentativa,
        resultado=nomes_dos_avisos.FALHA_DEFINITIVA,
        registrado_em=agora,
        detalhe_tecnico="550 caixa inexistente",
    )


def test_a_situacao_resume_os_avisos_e_nomeia_a_falha(inscricoes, publicada):
    primeiro = HorarioPublicado.objects.filter(ato=publicada).select_related("inscricao").first()
    _falhar(primeiro.aviso)
    situacao = avisos_da_agenda.situacao_dos_avisos(publicada.agenda, agora=timezone.now())
    assert situacao.total == len(inscricoes)
    assert situacao.na_fila == len(inscricoes) - 1
    assert [f.protocolo for f in situacao.falhas] == [primeiro.inscricao.protocolo]
    falha = situacao.falhas[0]
    assert falha.reenviavel
    assert "A agenda vale para essa pessoa do mesmo jeito" in falha.frase
    assert "na fila" in situacao.resumo


def test_o_reenvio_repete_o_texto_num_aviso_filho_uma_vez(
    gestor, edital_a, etapa_a2, inscricoes, publicada
):
    primeiro = HorarioPublicado.objects.filter(ato=publicada).select_related("aviso").first()
    _falhar(primeiro.aviso)
    filho = reenviar.reenviar(
        actor=gestor,
        edital=edital_a,
        etapa_id=etapa_a2,
        aviso_id=primeiro.aviso_id,
        idempotency_key="reenvio-1",
    )
    assert filho.aviso_anterior_id == primeiro.aviso_id
    assert filho.motivo == nomes_dos_avisos.REENVIO_DE_FALHAS
    assert (filho.assunto, filho.corpo) == (primeiro.aviso.assunto, primeiro.aviso.corpo)
    assert DestinatarioDoAviso.objects.get(aviso=filho).inscricao_id == primeiro.inscricao_id
    situacao = avisos_da_agenda.situacao_dos_avisos(publicada.agenda, agora=timezone.now())
    assert situacao.falhas == []
    # O pai já tem filho, e o filho ainda não falhou: nenhum dos dois se reenvia agora.
    for alvo in (primeiro.aviso_id, filho.id):
        with pytest.raises(DomainError) as recusa:
            reenviar.reenviar(
                actor=gestor,
                edital=edital_a,
                etapa_id=etapa_a2,
                aviso_id=alvo,
                idempotency_key=f"reenvio-de-{alvo}",
            )
        assert recusa.value.code == nomes.AVISO_NAO_REENVIAVEL
    assert RegistroAuditoria.objects.filter(operation=nomes.REENVIO_DO_AVISO_DA_AGENDA).count() == 1


@pytest.mark.skipif(connection.vendor != "postgresql", reason="o CHECK é do banco")
def test_o_banco_recusa_aviso_sem_marco_fora_da_agenda(edital_a, inscricoes, publicada):
    modelo = Aviso.objects.filter(origem=nomes_dos_avisos.AGENDA).first()
    with pytest.raises(IntegrityError, match="ck_aviso_marco_da_origem"), transaction.atomic():
        Aviso.objects.create(
            edital=edital_a,
            institution_scope=edital_a.institution_scope,
            origem=nomes_dos_avisos.CHAMADA,
            motivo=nomes_dos_avisos.PRIMEIRO_AVISO,
            perfil_id=modelo.perfil_id,
            marco_id=None,
            referencia_da_publicacao="Chamada de 01/11",
            assunto="a",
            corpo="b",
            solicitado_por="x",
            solicitado_em=timezone.now(),
            idempotency_key="k",
        )
    with pytest.raises(IntegrityError, match="ck_aviso_ato_da_origem"), transaction.atomic():
        Aviso.objects.create(
            edital=edital_a,
            institution_scope=edital_a.institution_scope,
            origem=nomes_dos_avisos.AGENDA,
            motivo=nomes_dos_avisos.PRIMEIRO_AVISO,
            perfil_id=modelo.perfil_id,
            marco_id=None,
            referencia_da_publicacao="",
            assunto="a",
            corpo="b",
            solicitado_por="x",
            solicitado_em=timezone.now(),
            idempotency_key="k",
        )
