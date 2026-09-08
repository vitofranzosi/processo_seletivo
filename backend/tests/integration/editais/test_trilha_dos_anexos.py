"""A trilha do que se fez com os Anexos, e o que ela não guarda (020, FR-038, FR-055).

Auditoria responde questionamento: quem, o quê, sobre qual Edital e quando. O que ela **não**
precisa é do nome do arquivo — ele é escolha de quem sobe, muda entre duas versões do mesmo
formulário, e não responde nada que alguém venha perguntar.
"""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.editais.application import anexos as comandos
from processo_seletivo.processos.models import Edital
from tests.conftest import ator_institucional
from tests.fixtures.anexos import pdf_de_teste

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    return Edital.objects.get(processo_id=criado.json()["id"])


def arquivo(nome="requerimento-de-inscricao-versao-final.pdf", marca="A"):
    return SimpleUploadedFile(nome, pdf_de_teste(marca), content_type="application/pdf")


def operacoes():
    return [registro.operation for registro in RegistroAuditoria.objects.all()]


def test_cada_operacao_sobre_o_anexo_deixa_o_seu_registro(edital):
    ator = ator_institucional("ana.elaboradora", "edital:elaborar")

    anexo = comandos.anexar(
        actor=ator, edital_id=edital.id, expected_revision=edital.revision, arquivo=arquivo()
    )
    edital.refresh_from_db()
    comandos.substituir(
        actor=ator,
        edital_id=edital.id,
        expected_revision=edital.revision,
        anexo_id=anexo.id,
        arquivo=arquivo(marca="B"),
    )
    edital.refresh_from_db()
    comandos.rotular(
        actor=ator,
        edital_id=edital.id,
        expected_revision=edital.revision,
        anexo_id=anexo.id,
        rotulo="ANEXO I — REQUERIMENTO",
    )
    edital.refresh_from_db()
    comandos.remover(
        actor=ator, edital_id=edital.id, expected_revision=edital.revision, anexo_id=anexo.id
    )

    assert operacoes() == [
        "CRIAR",
        "ANEXAR_AO_EDITAL",
        "SUBSTITUIR_ANEXO",
        "ROTULAR_ANEXO",
        "REMOVER_ANEXO",
    ]


def test_a_trilha_diz_quem_o_que_e_sobre_qual_edital(edital):
    ator = ator_institucional("ana.elaboradora", "edital:elaborar")

    anexo = comandos.anexar(
        actor=ator, edital_id=edital.id, expected_revision=edital.revision, arquivo=arquivo()
    )

    registro = RegistroAuditoria.objects.get(operation="ANEXAR_AO_EDITAL")
    assert registro.actor_subject == "ana.elaboradora"
    assert registro.permission == "edital:elaborar"
    assert registro.aggregate_id == edital.id
    assert str(anexo.id) in registro.reason
    assert registro.occurred_at is not None


def test_a_trilha_nao_guarda_o_nome_do_arquivo(edital):
    """O nome é escolha de quem sobe e não responde questionamento nenhum (FR-055).

    É a mesma decisão que a `009` tomou para o documento do candidato — lá, porque nome de arquivo
    carrega dado pessoal com frequência; aqui, porque ele simplesmente não é o fato.
    """
    ator = ator_institucional("ana.elaboradora", "edital:elaborar")

    comandos.anexar(
        actor=ator, edital_id=edital.id, expected_revision=edital.revision, arquivo=arquivo()
    )

    registro = RegistroAuditoria.objects.get(operation="ANEXAR_AO_EDITAL")
    assert "requerimento-de-inscricao-versao-final" not in registro.reason
