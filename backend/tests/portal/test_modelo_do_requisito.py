"""O modelo que o Edital fornece, ao lado do campo de envio (020, FR-044 a FR-047).

É o valor que o candidato recebe, e é o que hoje o manda para fora do sistema: o Edital exige o
documento em forma própria e o manda a um anexo que o documento publicado não contém.

O que estes testes **não** provam, e de propósito: que o arquivo devolvido corresponde ao modelo.
Não corresponde por construção — o PDF preenchido tem bytes diferentes — e o sistema não lê o que
há dentro dele. Conformidade é juízo da banca (D-004).
"""

import pytest
from django.urls import reverse

from processo_seletivo.editais.models import DocumentoExigido
from processo_seletivo.inscricoes.models import DocumentoSubmetido, Inscricao
from tests.fixtures.anexos import criar_anexo
from tests.fixtures.candidato import MARIA, PERFIL_DOCENTE, identificar, pdf
from tests.fixtures.selecao import DOCUMENTO_DE_TODOS

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


def inscrever(client, selecao):
    identificar(client, MARIA)
    client.post(reverse("portal:inscrever", args=[selecao.id, PERFIL_DOCENTE]))
    return Inscricao.objects.get(edital=selecao)


def vincular_modelo(selecao):
    """Liga o requisito de todos a um Anexo. O vínculo é do conteúdo publicado, então republica."""
    anexo = criar_anexo(selecao, rotulo="ANEXO I — REQUERIMENTO DE INSCRIÇÃO", order=1)
    DocumentoExigido.objects.filter(edital=selecao, id=DOCUMENTO_DE_TODOS).update(anexo=anexo)
    return anexo


def test_o_requisito_sem_modelo_continua_como_sempre_foi(client, selecao):
    """FR-024 — não fornecer forma própria é o caso mais comum, e não uma pendência."""
    inscricao = inscrever(client, selecao)

    corpo = client.get(reverse("portal:inscricao", args=[inscricao.id])).content.decode()

    assert "Baixar o modelo" not in corpo


def test_o_modelo_vigente_e_oferecido_ao_lado_do_campo_de_envio(client, selecao, api_client):
    """FR-044 e FR-045 — o modelo vem do conteúdo publicado que o candidato está vendo."""
    from tests.fixtures.publicacao import create_retification, publish_retification

    anexo = vincular_modelo(selecao)
    # O vínculo só existe para o candidato depois de publicado: é o conteúdo que ele lê, e não a
    # tabela de elaboração. E as **duas** alterações vão no mesmo ato porque a regra da referência
    # pendurada recusa a segunda sem a primeira — foi ela que reprovou a primeira redação deste
    # teste, e é o alcance da FR-023 na fronteira de vigência da Retificação.
    publish_retification(
        api_client,
        create_retification(
            api_client,
            selecao,
            [
                {
                    "targetPath": "/attachments/-",
                    "operation": "ADD",
                    "newValue": {
                        "id": str(anexo.id),
                        "label": anexo.rotulo,
                        "order": anexo.order,
                        "artifactId": str(anexo.artefato_id),
                        "artifactHash": anexo.artefato.document_hash,
                    },
                },
                {
                    "targetPath": f"/documentRequirements/id={DOCUMENTO_DE_TODOS}/attachmentId",
                    "operation": "REPLACE",
                    "newValue": str(anexo.id),
                },
            ],
        ),
        suffix="a",
    )
    inscricao = inscrever(client, selecao)

    corpo = client.get(reverse("portal:inscricao", args=[inscricao.id])).content.decode()

    assert "Baixar o modelo: ANEXO I — REQUERIMENTO DE INSCRIÇÃO" in corpo
    assert reverse("public-anexo", args=[anexo.artefato_id]) in corpo


def test_o_arquivo_devolvido_e_recebido_sem_ser_lido(client, selecao):
    """FR-047 — o que volta é documento do candidato, e o sistema não o abre para conferir."""
    inscricao = inscrever(client, selecao)

    client.post(
        reverse("portal:enviar-documento", args=[inscricao.id, DOCUMENTO_DE_TODOS]),
        {"arquivo": pdf("preenchido.pdf", b"requerimento preenchido e assinado")},
    )

    documento = DocumentoSubmetido.objects.get(inscricao=inscricao)
    assert documento.requirement_id == __import__("uuid").UUID(DOCUMENTO_DE_TODOS)
    assert documento.content_hash, "o resumo é do que chegou, e não comparação com modelo nenhum"


def test_substituir_o_modelo_nao_descarta_o_documento_ja_enviado(client, selecao, api_client):
    """FR-046 e D-012 — o enviado continua valendo, e decidir o contrário exigiria ler o arquivo.

    O aviso de versão que a `009` já dispara continua sendo o que informa o candidato; o descarte
    da FR-031 é para requisito que deixou de ser aplicável, e modelo substituído não torna nenhum
    requisito inaplicável.
    """
    from tests.fixtures.publicacao import create_retification, publish_retification

    inscricao = inscrever(client, selecao)
    client.post(
        reverse("portal:enviar-documento", args=[inscricao.id, DOCUMENTO_DE_TODOS]),
        {"arquivo": pdf("preenchido.pdf", b"requerimento preenchido")},
    )
    enviado = DocumentoSubmetido.objects.get(inscricao=inscricao)
    anexo = criar_anexo(selecao, rotulo="ANEXO I — REQUERIMENTO", order=1)

    publish_retification(
        api_client,
        create_retification(
            api_client,
            selecao,
            [
                {
                    "targetPath": "/attachments/-",
                    "operation": "ADD",
                    "newValue": {
                        "id": str(anexo.id),
                        "label": anexo.rotulo,
                        "order": anexo.order,
                        "artifactId": str(anexo.artefato_id),
                        "artifactHash": anexo.artefato.document_hash,
                    },
                }
            ],
        ),
        suffix="b",
    )

    ainda_la = DocumentoSubmetido.objects.get(inscricao=inscricao)
    assert ainda_la.pk == enviado.pk
    assert ainda_la.content_hash == enviado.content_hash
