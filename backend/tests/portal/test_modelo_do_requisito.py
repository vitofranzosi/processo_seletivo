"""O modelo que o Edital fornece, ao lado do campo de envio (020, FR-044 a FR-047).

É o valor que o candidato recebe, e é o que hoje o manda para fora do sistema: o Edital exige o
documento em forma própria e o manda a um anexo que o documento publicado não contém.

O que estes testes **não** provam, e de propósito: que o arquivo devolvido corresponde ao modelo.
Não corresponde por construção — o PDF preenchido tem bytes diferentes — e o sistema não lê o que
há dentro dele. Conformidade é juízo da banca (D-004).
"""

import pytest
from django.urls import reverse

from processo_seletivo.editais.models import AnexoEdital, DocumentoExigido
from processo_seletivo.inscricoes.models import DocumentoSubmetido, Inscricao
from tests.fixtures.candidato import MARIA, PERFIL_DOCENTE, identificar, pdf
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def selecao_com_modelo(raiz_de_arquivos, api_client, manager_headers, process_payload):
    """Seleção publicada **com** dois anexos e o requisito de todos apontando o primeiro.

    O vínculo é posto antes da submissão, e não por Retificação: é assim que um autor de verdade o
    faz, e é o que faz o artefato ser congelado pela publicação original — sem depender do
    congelamento na Retificação, que é da US3.
    """
    from datetime import timedelta

    from django.utils import timezone

    from tests.fixtures.selecao import publicar_selecao, rascunho_aberto_com_documentos

    def vincular(edital):
        primeiro = AnexoEdital.objects.filter(edital=edital).order_by("order").first()
        DocumentoExigido.objects.filter(edital=edital, id=DOCUMENTO_DE_TODOS).update(anexo=primeiro)

    return publicar_selecao(
        api_client,
        manager_headers,
        process_payload,
        rascunho=rascunho_aberto_com_documentos(timezone.now() - timedelta(seconds=1)),
        anexos=2,
        antes_de_submeter=vincular,
    )


def inscrever(client, selecao):
    identificar(client, MARIA)
    client.post(reverse("portal:inscrever", args=[selecao.id, PERFIL_DOCENTE]))
    return Inscricao.objects.get(edital=selecao)


def test_o_requisito_sem_modelo_continua_como_sempre_foi(client, selecao):
    """FR-024 — não fornecer forma própria é o caso mais comum, e não uma pendência."""
    inscricao = inscrever(client, selecao)

    corpo = client.get(reverse("portal:inscricao", args=[inscricao.id])).content.decode()

    assert "Baixar o modelo" not in corpo


def test_o_candidato_baixa_o_modelo_vigente_e_recebe_os_bytes(client, selecao_com_modelo):
    """FR-044 e FR-045 — e o teste **clica no link**, em vez de conferir que ele existe.

    A primeira redação afirmava a presença da URL no HTML e parava aí. O link apontava para um
    artefato acrescentado por Retificação, que nasce descongelado enquanto a US3 não chega — isto
    é, o teste passava com um botão que responderia 404 para o candidato.
    """
    from processo_seletivo.editais.models import ArtefatoAnexo

    inscricao = inscrever(client, selecao_com_modelo)
    anexo = AnexoEdital.objects.filter(edital=selecao_com_modelo).order_by("order").first()

    corpo = client.get(reverse("portal:inscricao", args=[inscricao.id])).content.decode()
    baixado = client.get(reverse("public-anexo", args=[anexo.artefato_id]))

    assert f"Baixar o modelo: {anexo.rotulo}" in corpo
    assert baixado.status_code == 200
    assert baixado.content == bytes(ArtefatoAnexo.objects.get(pk=anexo.artefato_id).bytes)


def test_o_arquivo_devolvido_e_recebido_sem_ser_lido(client, selecao_com_modelo):
    """FR-047 — o que volta é documento do candidato, e o sistema não o abre para conferir."""
    import uuid

    inscricao = inscrever(client, selecao_com_modelo)

    client.post(
        reverse("portal:enviar-documento", args=[inscricao.id, DOCUMENTO_DE_TODOS]),
        {"arquivo": pdf("preenchido.pdf", b"requerimento preenchido e assinado")},
    )

    documento = DocumentoSubmetido.objects.get(inscricao=inscricao)
    assert documento.requirement_id == uuid.UUID(DOCUMENTO_DE_TODOS)
    assert documento.content_hash, "o resumo é do que chegou, e não comparação com modelo nenhum"


def test_trocar_o_modelo_do_requisito_nao_descarta_o_documento_ja_enviado(
    client, selecao_com_modelo, api_client
):
    """FR-046 e D-012 — a troca é **de verdade**: o requisito passa a apontar o segundo Anexo.

    A primeira redação apenas acrescentava um anexo alheio ao requisito, e com isso provava outra
    coisa: que acrescentar anexo não apaga documento. A substituição do modelo é o caso que a
    D-012 decide, e é este.
    """
    from tests.fixtures.publicacao import create_retification, publish_retification

    inscricao = inscrever(client, selecao_com_modelo)
    client.post(
        reverse("portal:enviar-documento", args=[inscricao.id, DOCUMENTO_DE_TODOS]),
        {"arquivo": pdf("preenchido.pdf", b"requerimento preenchido")},
    )
    enviado = DocumentoSubmetido.objects.get(inscricao=inscricao)
    segundo = AnexoEdital.objects.filter(edital=selecao_com_modelo).order_by("order").last()

    publish_retification(
        api_client,
        create_retification(
            api_client,
            selecao_com_modelo,
            [
                {
                    "targetPath": f"/documentRequirements/id={DOCUMENTO_DE_TODOS}/attachmentId",
                    "operation": "REPLACE",
                    "newValue": str(segundo.id),
                }
            ],
        ),
        suffix="a",
    )

    ainda_la = DocumentoSubmetido.objects.get(inscricao=inscricao)
    assert ainda_la.pk == enviado.pk
    assert ainda_la.content_hash == enviado.content_hash
    corpo = client.get(reverse("portal:inscricao", args=[inscricao.id])).content.decode()
    assert f"Baixar o modelo: {segundo.rotulo}" in corpo, "e o modelo oferecido passa a ser o novo"


def test_retificar_so_o_vinculo_para_anexo_inexistente_e_recusado(api_client, selecao_com_modelo):
    """FR-023 na fronteira de vigência da Retificação — o caso negativo, explícito.

    É o defeito que a `020` veio corrigir entrando pela porta de trás: o Edital passaria a prometer
    um modelo que aquela versão não publica, e o candidato voltaria a ser mandado ao lugar vazio.
    """
    from tests.fixtures.publicacao import create_retification

    inexistente = "55555555-5555-5555-5555-555555555555"

    recusa = create_retification(
        api_client,
        selecao_com_modelo,
        [
            {
                "targetPath": f"/documentRequirements/id={DOCUMENTO_DE_TODOS}/attachmentId",
                "operation": "REPLACE",
                "newValue": inexistente,
            }
        ],
        esperar=422,
    )

    assert recusa["code"] == "blocking_findings"
    assert "aponta um Anexo que não existe" in recusa["detail"]
