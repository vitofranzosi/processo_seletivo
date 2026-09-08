"""O ciclo inteiro do 173/2025, pelos canais de cada ator (020, SC-005).

O teste que a spec exigiu antes de existir uma linha de código: *"se qualquer um dos sete passos não
couber, ela ainda não está pronta"*. Os sete estão aqui, e o sétimo é o emblemático — os dois
artefatos coexistindo, que é exatamente o que a prática atual perde ao substituir o arquivo no
mesmo caminho.

**São os anexos-formulário**, e não os nove. Quadro de perfil e ficha de avaliação são L-1 e barema,
que o fora de escopo desta feature exclui; o Cronograma, rotulado como anexo em cinco dos sete
Editais lidos, é Seção pela D-003.

Nenhum passo escreve no banco: o autor usa a interface administrativa, o candidato usa o portal, a
banca usa a mesa, e quem consulta usa a API pública. É o princípio VI da Constituição, e é ele que
separa "o domínio sustenta" de "está entregue".
"""

import re

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.editais.models import AnexoEdital, ArtefatoAnexo, DocumentoExigido
from processo_seletivo.inscricoes.models import DocumentoSubmetido, Inscricao
from processo_seletivo.publicacoes.models_retificacao import Retificacao
from tests.fixtures.candidato import (
    MARIA,
    MODALIDADE_PPP,
    PERFIL_DOCENTE,
    identificar,
    pdf,
)
from tests.fixtures.selecao import (
    DOCUMENTO_DA_MODALIDADE,
    DOCUMENTO_DE_TODOS,
    DOCUMENTO_DO_PERFIL,
)
from tests.interface.conftest import identificar as identificar_no_gestao

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.acceptance]

# Os três formulários do 173/2025 que o teste percorre. A autodeclaração é a que ganha modelo
# vinculado; as outras duas existem para que a coleção tenha mais de um item e a substituição de
# uma não possa passar por acidente de lista com um elemento só.
FORMULARIOS = [
    "ANEXO V — AUTODECLARAÇÃO ÉTNICO-RACIAL",
    "ANEXO VI — DECLARAÇÃO DE PERTENCIMENTO QUILOMBOLA",
    "ANEXO VII — ANUÊNCIA DA CHEFIA IMEDIATA",
]


@pytest.fixture
def selecao_do_173(raiz_de_arquivos, api_client, manager_headers, process_payload):
    """Passo 1 — o autor publica o Edital com os seus anexos-formulário."""
    from datetime import timedelta

    from tests.fixtures.selecao import publicar_selecao, rascunho_aberto_com_documentos

    def compor_anexos(edital):
        for ordem, rotulo in enumerate(FORMULARIOS, start=1):
            AnexoEdital.objects.filter(edital=edital, order=ordem).update(rotulo=rotulo)
        primeiro = AnexoEdital.objects.filter(edital=edital).order_by("order").first()
        DocumentoExigido.objects.filter(edital=edital, id=DOCUMENTO_DE_TODOS).update(anexo=primeiro)

    return publicar_selecao(
        api_client,
        manager_headers,
        process_payload,
        rascunho=rascunho_aberto_com_documentos(timezone.now() - timedelta(seconds=1)),
        anexos=len(FORMULARIOS),
        antes_de_submeter=compor_anexos,
    )


def test_o_ciclo_dos_sete_passos(client, api_client, seletor_ligado, selecao_do_173, gestor):
    edital = selecao_do_173
    autodeclaracao = AnexoEdital.objects.filter(edital=edital).order_by("order").first()
    artefato_de_entao = autodeclaracao.artefato_id

    # Passo 1 — o Edital publicado cita os três formulários, e a página pública os entrega.
    publica = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()
    assert "Anexos do Edital" in publica
    for rotulo in FORMULARIOS:
        assert rotulo in publica
    assert client.get(reverse("public-anexo", args=[artefato_de_entao])).status_code == 200

    # Passo 3 — o candidato baixa o vigente **na data em que se inscreve**. Antes da Retificação,
    # de propósito: é essa ordem que faz a versão aceita ser a de então.
    identificar(client, MARIA)
    client.post(reverse("portal:inscrever", args=[edital.id, PERFIL_DOCENTE]))
    inscricao = Inscricao.objects.get(edital=edital)
    inscricao_html = client.get(reverse("portal:inscricao", args=[inscricao.id])).content.decode()
    assert f"Baixar o modelo: {autodeclaracao.rotulo}" in inscricao_html
    baixado = client.get(reverse("public-anexo", args=[artefato_de_entao]))
    assert baixado.status_code == 200

    # Passo 4 — devolve preenchido e assinado, e **envia**. O envio importa para o passo 5: é ele
    # que fixa a versão aceita, e é dela que sai o modelo que a banca vai ver.
    client.post(
        reverse("portal:inscricao", args=[inscricao.id]),
        {"modalidade": MODALIDADE_PPP, "telefone": "(27) 99999-0000"},
    )
    for requisito, nome in (
        (DOCUMENTO_DE_TODOS, "autodeclaracao-preenchida.pdf"),
        (DOCUMENTO_DO_PERFIL, "diploma.pdf"),
        (DOCUMENTO_DA_MODALIDADE, "declaracao.pdf"),
    ):
        client.post(
            reverse("portal:enviar-documento", args=[inscricao.id, requisito]),
            {"arquivo": pdf(nome, b"assinada e digitalizada")},
        )
    envio = client.post(
        reverse("portal:revisao", args=[inscricao.id]), {"veracidade": "on", "ciencia": "on"}
    )
    assert envio["Location"] == reverse("portal:comprovante", args=[inscricao.id])
    inscricao.refresh_from_db()
    assert inscricao.status == Inscricao.Status.SUBMETIDA
    assert inscricao.versao_aceita_id is not None
    assert DocumentoSubmetido.objects.filter(inscricao=inscricao).count() == 3

    # Passo 2 — uma Retificação substitui um deles e preserva o anterior. Pela tela de quem
    # retifica, com o arquivo entrando na conferência e a identidade atravessando a confirmação.
    identificar_no_gestao(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(reverse("interface:retificar", args=[edital.id])).content.decode()
    base = re.search(r'name="base" value="([^"]+)"', corpo).group(1)
    referencia = re.search(
        rf'{re.escape(autodeclaracao.rotulo)}.*?name="arquivo:(g\d+c\d+)"', corpo, re.S
    ).group(1)
    client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            "base": base,
            "justificativa": "Formulário corrigido pela comissão",
            f"arquivo:{referencia}": SimpleUploadedFile(
                "autodeclaracao-v2.pdf",
                b"%PDF-1.4\n% versao corrigida\n%%EOF\n",
                content_type="application/pdf",
            ),
        },
    )
    artefato_novo = ArtefatoAnexo.objects.get(congelado_em__isnull=True)
    client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            "base": base,
            "justificativa": "Formulário corrigido pela comissão",
            "confirmar": "1",
            f"campo:{referencia}": str(artefato_novo.id),
        },
    )
    from tests.fixtures.publicacao import publish_retification

    publish_retification(api_client, Retificacao.objects.latest("created_at"), suffix="173")

    # Passo 5 — a banca lê o que voltou. O modelo que ela vê é o **de então**, e não o novo.
    from processo_seletivo.editais.domain.documentos import modelo_do_requisito

    conteudo_aceito = Inscricao.objects.get(pk=inscricao.pk).versao_aceita.content
    requisito = next(
        item
        for item in conteudo_aceito["documentRequirements"]
        if str(item["id"]) == DOCUMENTO_DE_TODOS
    )
    assert modelo_do_requisito(conteudo_aceito, requisito)["artefato_id"] == str(artefato_de_entao)

    # Passo 6 — a consulta pública, perguntada por um instante anterior, devolve o anexo de então.
    from urllib.parse import quote

    antes = inscricao.submitted_at or timezone.now()
    de_entao = api_client.get(
        f"/api/v1/public/editais/{edital.id}/versao-vigente?em={quote(antes.isoformat())}"
    ).json()["content"]["attachments"]
    vigente = api_client.get(f"/api/v1/public/editais/{edital.id}/versao-vigente").json()[
        "content"
    ]["attachments"]
    assert de_entao[0]["artifactId"] == str(artefato_de_entao)
    assert vigente[0]["artifactId"] == str(artefato_novo.id)
    assert de_entao[0]["id"] == vigente[0]["id"], "a identidade normativa é a mesma"

    # Passo 7 — os dois artefatos coexistem, e os hashes são distintos.
    respostas = [
        client.get(reverse("public-anexo", args=[item]))
        for item in (artefato_de_entao, artefato_novo.id)
    ]
    assert [resposta.status_code for resposta in respostas] == [200, 200]
    assert respostas[0].content != respostas[1].content
    assert respostas[0]["ETag"] != respostas[1]["ETag"]
