"""Os atos da agenda são append-only nas três camadas (167, T040, FR-7224, FR-7241).

A classe recusa `save` de linha existente e `delete`; o gatilho recusa `UPDATE` e `DELETE` mesmo de
quem tem privilégio; o papel de runtime não tem `UPDATE` nem `DELETE`. E o gatilho de coerência
recusa o que `CHECK` não alcança: o item que substitui outro de outra inscrição ou de outra agenda,
a banca de outra agenda, e o cancelado fora de um ato de cancelamento.
"""

import pytest
from django.db import DatabaseError, connection, transaction
from django.utils import timezone

from processo_seletivo.agendamento.domain import nomes
from processo_seletivo.agendamento.models import AtoDaAgenda, BancaDaAgenda, HorarioPublicado
from tests.fixtures.agenda_da_etapa import montar_completa, publicar_agenda
from tests.fixtures.papel_de_producao import como_producao  # noqa: F401

pytestmark = [
    pytest.mark.integration,
    pytest.mark.django_db,
    pytest.mark.skipif(connection.vendor != "postgresql", reason="os gatilhos são do PostgreSQL"),
]

IMUTAVEL = "schedule acts are append-only"


def _sql(texto, parametros=()):
    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute(texto, parametros)


@pytest.mark.parametrize(
    "tabela",
    [
        "agendamento_atodaagenda",
        "agendamento_horariopublicado",
        "agendamento_documentodoatodaagenda",
    ],
)
def test_update_e_delete_recusados_pelo_gatilho(publicada, tabela):
    alvo = {
        "agendamento_atodaagenda": publicada.id,
        "agendamento_horariopublicado": publicada.horarios.first().id,
        "agendamento_documentodoatodaagenda": publicada.documento.id,
    }[tabela]
    with pytest.raises(DatabaseError, match=IMUTAVEL):
        _sql(f"UPDATE {tabela} SET id = id WHERE id = %s", [alvo])
    with pytest.raises(DatabaseError, match=IMUTAVEL):
        _sql(f"DELETE FROM {tabela} WHERE id = %s", [alvo])


def test_save_de_linha_existente_e_delete_recusados_pela_classe(publicada):
    horario = publicada.horarios.first()
    for linha in (publicada, horario, publicada.documento):
        with pytest.raises(TypeError, match="append-only"):
            linha.save()
        with pytest.raises(TypeError, match="append-only"):
            linha.delete()


def test_o_papel_de_runtime_publica_e_nao_reescreve(
    gestor,
    edital_a,
    etapa_a2,
    inscricoes,
    como_producao,  # noqa: F811
):
    """Publicar sob a role de produção prova que nada trava o append-only com `FOR UPDATE`."""
    montar_completa(gestor, edital_a, etapa_a2)
    with como_producao():
        ato = publicar_agenda(gestor, edital_a, etapa_a2)
        with pytest.raises(DatabaseError, match="permission denied"):
            _sql(
                "UPDATE agendamento_horariopublicado SET banca_nome = 'x' WHERE ato_id = %s",
                [ato.id],
            )
    assert ato.horarios.count() == len(inscricoes)


def _ato(publicada, especie, **campos):
    """Um ato individual gravado à mão: a C os produz pelo comando; aqui só o banco é testado."""
    return AtoDaAgenda.objects.create(
        agenda=publicada.agenda,
        edital=publicada.edital,
        especie=especie,
        praticado_por="teste",
        praticado_em=timezone.now(),
        motivo="Conflito de horário.",
        conteudo_publico=b"{}",
        conteudo_publico_hash="0" * 64,
        **campos,
    )


def test_a_coerencia_recusa_substituir_o_item_de_outra_inscricao(publicada):
    um, outro = list(publicada.horarios.order_by("inicio"))[:2]
    remarcacao = _ato(publicada, nomes.REMARCACAO)
    with pytest.raises(DatabaseError, match="another registration"), transaction.atomic():
        HorarioPublicado.objects.create(
            ato=remarcacao,
            inscricao_id=um.inscricao_id,
            situacao=nomes.AGENDADO,
            banca_id=um.banca_id,
            banca_nome=um.banca_nome,
            inicio=um.inicio,
            fim=um.fim,
            substitui=outro,
        )


def test_a_coerencia_recusa_a_banca_de_outra_agenda(publicada, gestor, edital_a, etapa_a1):
    from processo_seletivo.agendamento.models import AgendaDaEtapa

    agora = timezone.now()
    outra = AgendaDaEtapa.objects.create(
        edital=edital_a,
        etapa_id=etapa_a1,
        forma="REMOTA",
        duracao_minutos=10,
        intervalo_minutos=0,
        criada_por="t",
        criada_em=agora,
        atualizada_por="t",
        atualizada_em=agora,
    )
    alheia = BancaDaAgenda.objects.create(agenda=outra, nome="Alheia", acesso="x", ordem=1)
    um = publicada.horarios.order_by("inicio").first()
    remarcacao = _ato(publicada, nomes.REMARCACAO)
    with pytest.raises(DatabaseError, match="another schedule"), transaction.atomic():
        HorarioPublicado.objects.create(
            ato=remarcacao,
            inscricao_id=um.inscricao_id,
            situacao=nomes.AGENDADO,
            banca=alheia,
            banca_nome="Alheia",
            inicio=um.inicio,
            fim=um.fim,
            substitui=um,
        )


def test_a_coerencia_recusa_o_cancelado_fora_do_cancelamento(publicada):
    um = publicada.horarios.order_by("inicio").first()
    remarcacao = _ato(publicada, nomes.REMARCACAO)
    with pytest.raises(DatabaseError, match="only a cancellation cancels"), transaction.atomic():
        HorarioPublicado.objects.create(
            ato=remarcacao,
            inscricao_id=um.inscricao_id,
            situacao=nomes.CANCELADO,
            substitui=um,
        )


def test_a_coerencia_recusa_a_remarcacao_sem_o_item_substituido(publicada):
    um = publicada.horarios.order_by("inicio").first()
    remarcacao = _ato(publicada, nomes.REMARCACAO)
    with pytest.raises(DatabaseError, match="replaces a published slot"), transaction.atomic():
        HorarioPublicado.objects.create(
            ato=remarcacao,
            inscricao_id=um.inscricao_id,
            situacao=nomes.AGENDADO,
            banca_id=um.banca_id,
            banca_nome=um.banca_nome,
            inicio=um.inicio,
            fim=um.fim,
        )


def test_a_remarcacao_coerente_substitui_e_o_vigente_muda(publicada):
    """O caminho válido: o item substituído sai do vigente, e a marca "remarcado em" aparece."""
    from processo_seletivo.agendamento.application import leitura

    um, ultimo = (
        publicada.horarios.order_by("inicio").first(),
        publicada.horarios.order_by("-inicio").first(),
    )
    remarcacao = _ato(publicada, nomes.REMARCACAO)
    HorarioPublicado.objects.create(
        ato=remarcacao,
        inscricao_id=um.inscricao_id,
        situacao=nomes.AGENDADO,
        banca_id=um.banca_id,
        banca_nome=um.banca_nome,
        inicio=ultimo.fim + (ultimo.fim - ultimo.inicio),
        fim=ultimo.fim + 2 * (ultimo.fim - ultimo.inicio),
        substitui=um,
    )

    vigentes = leitura.vigentes_da_agenda(publicada.agenda)
    da_pessoa = [item for item in vigentes if item.inscricao_id == um.inscricao_id]
    assert len(vigentes) == publicada.horarios.count()
    assert len(da_pessoa) == 1 and da_pessoa[0].ato_id == remarcacao.id
    assert da_pessoa[0].remarcado_em == remarcacao.praticado_em
