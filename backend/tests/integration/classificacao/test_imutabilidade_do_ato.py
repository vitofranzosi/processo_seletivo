"""O ato e suas posições nascem coerentes e não são reinterpretados depois (015, T078-T081)."""

import uuid

import pytest
from django.db import DatabaseError, IntegrityError, connection, transaction
from django.utils import timezone

from processo_seletivo.classificacao.models import AtoDeOrdenacao, PosicaoNaOrdem
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.comissao import inscrever
from tests.fixtures.publicacao import publish_original

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]

SOMENTE_POSTGRES = pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="As triggers são de PostgreSQL; em sqlite a garantia não existe.",
)


@pytest.fixture
def cenario(api_client, manager_headers, process_payload):
    edital = publish_original(api_client, manager_headers, process_payload)
    inscricao = inscrever(edital)[0]
    versao = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    ato = AtoDeOrdenacao.objects.create(
        edital=edital,
        perfil_id=inscricao.profile_id,
        marco_id=uuid.uuid4(),
        versao=versao,
        universo={"resultados": []},
        emitido_por="maria",
        emitido_em=timezone.now(),
    )
    return edital, inscricao, versao, ato


def test_o_modelo_recusa_atualizacao_e_exclusao_do_ato(cenario):
    *_, ato = cenario
    ato.emitido_por = "outra-pessoa"
    with pytest.raises(TypeError, match="append-only"):
        ato.save()
    with pytest.raises(TypeError, match="append-only"):
        ato.delete()


@SOMENTE_POSTGRES
@pytest.mark.parametrize(
    ("sql", "parametros"),
    [
        (
            "UPDATE classificacao_atodeordenacao SET emitido_por = %s WHERE id = %s",
            lambda ato: ["outra-pessoa", str(ato.id)],
        ),
        (
            "DELETE FROM classificacao_atodeordenacao WHERE id = %s",
            lambda ato: [str(ato.id)],
        ),
    ],
)
def test_a_trigger_recusa_mutacao_do_ato_por_sql_cru(cenario, sql, parametros):
    *_, ato = cenario
    with (
        pytest.raises(DatabaseError, match="append-only"),
        transaction.atomic(),
        connection.cursor() as cursor,
    ):
        cursor.execute(sql, parametros(ato))


def test_dois_atos_raiz_do_mesmo_marco_sao_recusados(cenario):
    edital, _, versao, ato = cenario
    with pytest.raises(IntegrityError), transaction.atomic():
        AtoDeOrdenacao.objects.create(
            edital=edital,
            perfil_id=ato.perfil_id,
            marco_id=ato.marco_id,
            versao=versao,
            universo={"resultados": []},
            emitido_por="maria",
            emitido_em=timezone.now(),
        )


def test_sucessor_sem_motivo_e_recusado(cenario):
    edital, _, versao, ato = cenario
    with pytest.raises(IntegrityError), transaction.atomic():
        AtoDeOrdenacao.objects.create(
            edital=edital,
            perfil_id=ato.perfil_id,
            marco_id=ato.marco_id,
            versao=versao,
            ato_anterior=ato,
            motivo_da_sucessao="",
            universo={"resultados": []},
            emitido_por="maria",
            emitido_em=timezone.now(),
        )


def test_dois_sucessores_do_mesmo_ato_sao_recusados(cenario):
    edital, _, versao, ato = cenario
    campos = {
        "edital": edital,
        "perfil_id": ato.perfil_id,
        "marco_id": ato.marco_id,
        "versao": versao,
        "ato_anterior": ato,
        "motivo_da_sucessao": "Resultado tardio",
        "universo": {"resultados": []},
        "emitido_por": "maria",
        "emitido_em": timezone.now(),
    }
    AtoDeOrdenacao.objects.create(**campos)

    with pytest.raises(IntegrityError), transaction.atomic():
        AtoDeOrdenacao.objects.create(**campos)


def test_posicao_exige_posicao_positiva_ou_motivo(cenario):
    _, inscricao, _, ato = cenario
    with pytest.raises(IntegrityError), transaction.atomic():
        PosicaoNaOrdem.objects.create(
            ato=ato,
            inscricao=inscricao,
            posicao=None,
            consequencia="ELIMINADA",
            motivo="",
        )


def test_a_mesma_inscricao_nao_ocupa_duas_linhas_do_ato(cenario):
    _, inscricao, _, ato = cenario
    campos = {
        "ato": ato,
        "inscricao": inscricao,
        "posicao": 1,
        "pontuacao_combinada": "10.0000",
        "consequencia": "HABILITADA",
    }
    PosicaoNaOrdem.objects.create(**campos)

    with pytest.raises(IntegrityError), transaction.atomic():
        PosicaoNaOrdem.objects.create(**campos)


@SOMENTE_POSTGRES
def test_a_trigger_recusa_inscricao_de_outro_perfil(cenario):
    edital, _, _, ato = cenario
    alheia = Inscricao.objects.create(
        identity_subject="cpf:outro-perfil",
        edital=edital,
        profile_id=uuid.uuid4(),
        created_at=timezone.now(),
    )

    with (
        pytest.raises(DatabaseError, match="does not match its act scope"),
        transaction.atomic(),
    ):
        PosicaoNaOrdem.objects.create(
            ato=ato,
            inscricao=alheia,
            posicao=1,
            pontuacao_combinada="10.0000",
            consequencia="HABILITADA",
        )
