"""Acrescentar, remover, rotular e reordenar Anexos por Retificação (020, D-008, US5).

As cinco operações da D-008 fecham aqui. As três que já existiam — substituir, e agora rotular e
ordenar — são campos; as duas novas são acréscimo e remoção, e a remoção arrasta uma consequência
que a tela precisa resolver no mesmo ato: o vínculo do requisito não pode sobreviver ao Anexo.

**O que nenhuma delas faz é renumerar.** O rótulo é campo do autor, e o PDF pode trazer "ANEXO VI"
impresso — derivar número de posição faria o conteúdo publicado divergir dos bytes em silêncio.
"""

import re

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from processo_seletivo.editais.models import AnexoEdital, ArtefatoAnexo, DocumentoExigido
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.anexos import pdf_de_teste
from tests.fixtures.publicacao import publish_original, publish_retification
from tests.fixtures.snapshot import rascunho_completo
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def publicado(api_client, manager_headers, process_payload):
    """Três anexos, para que remover o do meio possa deixar lacuna sem ambiguidade."""
    return publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_completo(), anexos=3
    )


def abrir(client, publicado):
    return client.get(reverse("interface:retificar", args=[publicado.id])).content.decode()


def base_de(corpo):
    return re.search(r'name="base" value="([^"]+)"', corpo).group(1)


def referencia_do_campo(corpo, titulo, rotulo):
    """A referência opaca de um campo, achada pelo título do grupo — a tela não expõe caminho."""
    grupo = re.search(rf"<legend[^>]*>{re.escape(titulo)}.*?(?=<fieldset|</form)", corpo, re.S)
    assert grupo, f"grupo {titulo!r} não está na tela"
    campo = re.search(rf'{re.escape(rotulo)}.*?name="campo:(g\d+c\d+)"', grupo.group(0), re.S)
    assert campo, f"campo {rotulo!r} não está no grupo {titulo!r}"
    return campo.group(1)


def referencia_do_grupo(corpo, titulo):
    grupo = re.search(rf'<legend[^>]*>{re.escape(titulo)}.*?name="remover:(g\d+)"', corpo, re.S)
    assert grupo, f"grupo {titulo!r} não é removível"
    return grupo.group(1)


def enviar(client, publicado, campos, *, confirmar=False):
    corpo = abrir(client, publicado)
    dados = {"base": base_de(corpo), "justificativa": "Ajuste na coleção de anexos", **campos}
    if confirmar:
        dados["confirmar"] = "1"
    return client.post(reverse("interface:retificar", args=[publicado.id]), dados)


def conteudo_vigente(publicado):
    return VersaoConsolidada.objects.filter(edital=publicado).latest("materialized_at").content


def test_alterar_o_rotulo_de_um_anexo_nao_toca_no_rotulo_de_nenhum_outro(
    client, api_client, seletor_ligado, publicado
):
    """FR-006 e FR-007 — o número está dentro do rótulo, e ninguém o recalcula."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = abrir(client, publicado)
    campo = referencia_do_campo(corpo, "Anexo 2 —", "Rótulo")

    enviar(client, publicado, {f"campo:{campo}": "ANEXO II — AUTODECLARAÇÃO"}, confirmar=True)
    publish_retification(api_client, _retificacao(), suffix="rotulo")

    rotulos = [anexo["label"] for anexo in conteudo_vigente(publicado)["attachments"]]
    assert rotulos == ["ANEXO 1 — FORMULÁRIO", "ANEXO II — AUTODECLARAÇÃO", "ANEXO 3 — FORMULÁRIO"]


def test_remover_um_anexo_deixa_lacuna_e_preserva_os_rotulos(
    client, api_client, seletor_ligado, publicado
):
    """FR-008 — renumerar aqui faria a numeração publicada divergir do que está impresso no PDF."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    grupo = referencia_do_grupo(abrir(client, publicado), "Anexo 2 —")

    enviar(client, publicado, {f"remover:{grupo}": "1"}, confirmar=True)
    publish_retification(api_client, _retificacao(), suffix="remocao")

    anexos = conteudo_vigente(publicado)["attachments"]
    assert [anexo["label"] for anexo in anexos] == [
        "ANEXO 1 — FORMULÁRIO",
        "ANEXO 3 — FORMULÁRIO",
    ]
    assert [anexo["order"] for anexo in anexos] == [1, 3], "a lacuna fica"


def test_o_anexo_removido_continua_na_publicacao_anterior(
    client, api_client, seletor_ligado, publicado
):
    """FR-033 — remover é deixar de existir na versão seguinte, e nunca apagar do histórico."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    grupo = referencia_do_grupo(abrir(client, publicado), "Anexo 2 —")
    antes = conteudo_vigente(publicado)["attachments"][1]

    enviar(client, publicado, {f"remover:{grupo}": "1"}, confirmar=True)
    publish_retification(api_client, _retificacao(), suffix="historico")

    original = VersaoConsolidada.objects.filter(edital=publicado).earliest("materialized_at")
    assert any(item["id"] == antes["id"] for item in original.content["attachments"])
    assert client.get(reverse("public-anexo", args=[antes["artifactId"]])).status_code == 200


def test_acrescentar_um_anexo_exige_o_arquivo_e_o_resumo_vem_do_artefato(
    client, api_client, seletor_ligado, publicado
):
    """FR-031 — o Anexo acrescentado nasce com a forma que `edital_snapshot` produz."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    enviar(
        client,
        publicado,
        {
            "novo-anexo-0-label": "ANEXO IV — TERMO LGPD",
            "novo-anexo-0-order": "4",
            "arquivo::novo-anexo-0-artifactId": SimpleUploadedFile(
                "termo.pdf", pdf_de_teste("W"), content_type="application/pdf"
            ),
        },
    )
    novo = ArtefatoAnexo.objects.get(congelado_em__isnull=True)
    enviar(
        client,
        publicado,
        {
            "novo-anexo-0-label": "ANEXO IV — TERMO LGPD",
            "novo-anexo-0-order": "4",
            "novo-anexo-0-artifactId": str(novo.id),
        },
        confirmar=True,
    )
    publish_retification(api_client, _retificacao(), suffix="acrescimo")

    acrescentado = conteudo_vigente(publicado)["attachments"][-1]
    assert acrescentado["label"] == "ANEXO IV — TERMO LGPD"
    assert acrescentado["artifactHash"] == novo.document_hash
    assert client.get(reverse("public-anexo", args=[novo.id])).status_code == 200


def test_acrescentar_sem_arquivo_e_recusado(client, seletor_ligado, publicado):
    """Não existe Anexo sem artefato, e a regra vale também para o que a Retificação cria."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    resposta = enviar(
        client,
        publicado,
        {"novo-anexo-0-label": "ANEXO IV — SEM ARQUIVO", "novo-anexo-0-order": "4"},
        confirmar=True,
    )

    assert "envie o arquivo" in resposta.content.decode().lower()


@pytest.fixture
def publicado_com_vinculo(api_client, manager_headers, process_payload):
    """Três anexos, e o primeiro requisito apontando o segundo — **antes** da publicação.

    O vínculo tem de estar no **conteúdo publicado**, e não na tabela de elaboração: é o conteúdo
    que a Retificação projeta. Ligar depois de publicar não muda a versão vigente, e o teste
    provaria apenas que nada acontece.
    """

    def vincular(edital):
        segundo = AnexoEdital.objects.filter(edital=edital).order_by("order")[1]
        primeiro = DocumentoExigido.objects.filter(edital=edital).order_by("order").first()
        if primeiro is not None:
            DocumentoExigido.objects.filter(pk=primeiro.pk).update(anexo=segundo)

    return publish_original(
        api_client,
        manager_headers,
        process_payload,
        draft=rascunho_completo(),
        anexos=3,
        antes_de_submeter=vincular,
    )


def test_remover_o_anexo_desfaz_o_vinculo_do_requisito_no_mesmo_ato(
    client, api_client, seletor_ligado, publicado_com_vinculo
):
    """FR-022 — o vínculo não sobrevive ao alvo, e a tela resolve isso sem pedir nada à pessoa.

    Sem esta emissão automática, a Retificação seria recusada pela referência pendurada e quem a
    compôs veria uma recusa que não teria como resolver: tirar o anexo e soltar o vínculo são
    coisas que se fazem no mesmo lugar.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    publicado = publicado_com_vinculo
    vigente = conteudo_vigente(publicado)
    vinculado = next(item for item in vigente["documentRequirements"] if item.get("attachmentId"))
    grupo = referencia_do_grupo(abrir(client, publicado), "Anexo 2 —")

    resposta = enviar(client, publicado, {f"remover:{grupo}": "1"})
    corpo = resposta.content.decode()

    assert "não fornece modelo" in corpo, "o resumo mostra o desvínculo, em vez de fazê-lo calado"
    enviar(client, publicado, {f"remover:{grupo}": "1"}, confirmar=True)
    publish_retification(api_client, _retificacao(), suffix="desvinculo")
    depois = conteudo_vigente(publicado)
    requisito = next(
        item for item in depois["documentRequirements"] if item["id"] == vinculado["id"]
    )
    assert requisito["attachmentId"] is None, "o vínculo não sobreviveu ao alvo"
    assert all(item["id"] != vinculado["attachmentId"] for item in depois["attachments"])


def _retificacao():
    from processo_seletivo.publicacoes.models_retificacao import Retificacao

    return Retificacao.objects.latest("created_at")
