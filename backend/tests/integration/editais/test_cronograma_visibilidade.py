"""Ocultar do PDF, de ponta a ponta: publicação, documento, API, Kit, Retificação e cópia (144).

O Edital aqui é publicado pelo caminho real — rascunho, submissão, homologação, publicação — e o
que se afirma sobre o documento é lido dos bytes que a publicação guardou (SC-1588). O período de
inscrições é o Evento oculto de propósito: é o caso em que ocultar "parece" desativar, e a prova de
que não desativa é o Kit e a API continuarem com ele.
"""

import copy

import pytest
from django.utils import timezone

from processo_seletivo.editais.application.reaproveitamento import reaproveitar_edital
from processo_seletivo.editais.models.cronograma import EventoCronograma
from processo_seletivo.portal import ficha as fichas
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.publicacoes.models import DocumentoPublicado
from processo_seletivo.shared.canonical import SCHEMA_VERSION
from tests.conftest import ator_institucional
from tests.fixtures.edital import complete_draft
from tests.fixtures.papel_de_producao import como_producao  # noqa: F401
from tests.fixtures.publicacao import publish_original, retify
from tests.interface.test_fluxo import texto_de_pdf_bytes

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

PERIODO = "aaaaaaaa-0000-4000-8000-000000014401"
OCULTO = "aaaaaaaa-0000-4000-8000-000000014402"
EXIBIDO = "aaaaaaaa-0000-4000-8000-000000014403"


def rascunho():
    """O rascunho mínimo publicável, com três Eventos: o período e um interno ocultos."""
    draft = complete_draft()
    draft["schedule"] = [
        {
            "id": PERIODO,
            "type": "INSCRICAO",
            "description": "PeriodoDeInscricoes",
            "startAt": "2027-03-01T09:00:00-03:00",
            "endAt": "2027-03-10T23:59:00-03:00",
            "order": 1,
            "isRegistrationPeriod": True,
            "shownInPdf": False,
        },
        {
            "id": OCULTO,
            "type": "AVALIACAO",
            "description": "AvaliacaoInterna",
            "startAt": "2027-03-15T08:00:00-03:00",
            "order": 2,
            "shownInPdf": False,
        },
        {
            "id": EXIBIDO,
            "type": "RESULTADO",
            "description": "ResultadoFinal",
            "startAt": "2027-03-30T14:00:00-03:00",
            "order": 3,
        },
    ]
    return draft


@pytest.fixture
def publicado(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload, draft=rascunho())


def visibilidade(conteudo):
    return {evento["id"]: evento["shownInPdf"] for evento in conteudo["schedule"]}


def test_o_conteudo_publicado_leva_a_visibilidade_de_todo_evento(publicado):
    """FR-5105: sempre presente; o omitido no rascunho chega verdadeiro."""
    conteudo = effective_version(edital_id=publicado.id).content
    assert conteudo["schemaVersion"] == SCHEMA_VERSION

    assert visibilidade(conteudo) == {PERIODO: False, OCULTO: False, EXIBIDO: True}


def test_o_pdf_publicado_nao_imprime_os_ocultos_e_numera_de_um(publicado):
    """FR-5106, SC-1581, SC-1588: os bytes que o ato guardou, e não a prévia."""
    documento = DocumentoPublicado.objects.get(publicacao__edital=publicado)
    linhas = texto_de_pdf_bytes(bytes(documento.bytes)).splitlines()

    assert "AvaliacaoInterna" not in linhas
    assert "PeriodoDeInscricoes" not in linhas
    posicao = linhas.index("ResultadoFinal")
    assert linhas[posicao - 1] == "1", "o único exibido é o primeiro da tabela"


def test_os_eventos_ocultos_continuam_no_rascunho_e_no_banco(publicado):
    """FR-5103, SC-1581: ocultar não apaga, não cancela e não desmarca o período."""
    eventos = {str(e.id): e for e in EventoCronograma.objects.filter(cronograma__edital=publicado)}

    assert set(eventos) == {PERIODO, OCULTO, EXIBIDO}
    assert eventos[PERIODO].is_registration_period is True
    assert eventos[PERIODO].shown_in_pdf is False
    assert eventos[OCULTO].status == EventoCronograma.Status.PLANEJADO


def test_a_leitura_pela_api_traz_o_oculto(api_client, publicado):
    """FR-5112: a versão vigente pela API pública tem os três Eventos."""
    resposta = api_client.get(f"/api/v1/public/editais/{publicado.id}/versao-vigente")

    assert resposta.status_code == 200
    assert visibilidade(resposta.json()["content"]) == {
        PERIODO: False,
        OCULTO: False,
        EXIBIDO: True,
    }


def test_o_kit_de_divulgacao_le_o_periodo_oculto(publicado):
    """FR-5112, FR-5103: o Kit anuncia as inscrições pelo período, oculto da tabela ou não."""
    ficha = fichas.ler(publicado, agora=timezone.now(), base_url=None)

    assert ficha.inicio_data == "01/03/2027"
    assert ficha.fim_data == "10/03/2027"


def test_a_retificacao_alcanca_a_visibilidade(api_client, publicado):
    """FR-5113, P-1: o Evento oculto por engano volta à tabela por Retificação."""
    retify(
        api_client,
        publicado,
        [
            {
                "targetPath": f"/schedule/id={OCULTO}/shownInPdf",
                "operation": "REPLACE",
                "newValue": True,
            }
        ],
    )

    vigente = effective_version(edital_id=publicado.id).content
    assert visibilidade(vigente) == {PERIODO: False, OCULTO: True, EXIBIDO: True}


def test_reaproveitar_preserva_o_oculto(
    api_client,
    manager_headers,
    publicado,
    como_producao,  # noqa: F811
):
    """FR-5111, D-008, SC-1586: copiar o Edital copia o que ele decidiu publicar."""
    criado = api_client.post(
        "/api/v1/admin/processos",
        {
            "institutionalCode": "PS-2027-144",
            "title": "Processo Seletivo 2027",
            "firstEdital": {"number": "44", "year": 2027, "title": "Edital reaproveitado"},
        },
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "destino-144-0001"},
    )
    assert criado.status_code == 201, criado.content
    destino = Edital.objects.get(processo_id=criado.json()["id"])

    with como_producao():
        reaproveitar_edital(
            actor=ator_institucional("preparadora", "edital:elaborar"),
            edital_id=destino.id,
            origem_id=publicado.id,
            expected_revision=destino.revision,
            idempotency_key="reaproveitar-144-0001",
            correlation_id="correlacao-144",
        )

    copiados = EventoCronograma.objects.filter(cronograma__edital=destino).order_by("order")
    assert [(e.description, e.shown_in_pdf) for e in copiados] == [
        ("PeriodoDeInscricoes", False),
        ("AvaliacaoInterna", False),
        ("ResultadoFinal", True),
    ]
    assert [e.is_registration_period for e in copiados] == [True, False, False]


def test_rascunho_sem_a_chave_grava_exibido(api_client, manager_headers, process_payload):
    """FR-5104: o cliente da API que não conhece o campo não oculta nada."""
    draft = copy.deepcopy(rascunho())
    for evento in draft["schedule"]:
        evento.pop("shownInPdf", None)

    publicado = publish_original(api_client, manager_headers, process_payload, draft=draft)

    assert set(
        EventoCronograma.objects.filter(cronograma__edital=publicado).values_list(
            "shown_in_pdf", flat=True
        )
    ) == {True}


@pytest.mark.django_db(transaction=True)
def test_a_migration_deixa_exibido_o_evento_que_ja_existia(
    api_client, manager_headers, process_payload
):
    """SC-1580, FR-5100: o Evento gravado antes da `editais/0026` sai na tabela, como saía.

    Volta-se a `0026`, com um Evento já gravado, e reaplica-se. A coluna renasce com o padrão, e a
    linha antiga, que nunca teve o campo, fica exibida.

    **Reaplica-se até a última de `editais`, e não só até a `0026`.** Desde a `146` a `0027` (o
    barema) depende dela, e voltar à `0025` a desfaz junto: parar na `0026` deixava o banco do
    worker sem a tabela dos critérios, e todo caso seguinte nele desabava — a limpeza dos
    transacionais não conseguia truncar a Etapa, e o resto era cascata.
    """
    from django.db import connection
    from django.db.migrations.executor import MigrationExecutor

    publicado = publish_original(api_client, manager_headers, process_payload, draft=rascunho())
    executor = MigrationExecutor(connection)
    executor.migrate([("editais", "0025_condicao_do_documento_exigido")])
    executor.loader.build_graph()
    executor.migrate(executor.loader.graph.leaf_nodes("editais"))

    assert set(
        EventoCronograma.objects.filter(cronograma__edital=publicado).values_list(
            "shown_in_pdf", flat=True
        )
    ) == {True}
