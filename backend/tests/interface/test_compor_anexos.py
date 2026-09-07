"""A etapa `Anexos` do assistente (020, FR-015, FR-015a, FR-010a, FR-019).

É o **primeiro caminho de escrita de arquivo** da interface administrativa: até aqui só o portal do
candidato recebia arquivo. A coleção fica fora do `replace_draft`, e cada operação tem comando
próprio — por isso a etapa não posta no POST genérico do assistente, e por isso os dois modos de
falha do rascunho precisam de teste explícito.
"""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from processo_seletivo.editais.models import AnexoEdital, ArtefatoAnexo
from processo_seletivo.processos.models import Edital
from tests.fixtures.anexos import criar_anexo, pdf_de_teste
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    criado = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    return Edital.objects.get(processo_id=criado.json()["id"])


def arquivo(marca="A", nome="requerimento.pdf"):
    return SimpleUploadedFile(nome, pdf_de_teste(marca), content_type="application/pdf")


def acao(client, edital, **campos):
    return client.post(reverse("interface:anexos", args=[edital.id]), campos)


def test_a_etapa_existe_no_assistente(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])

    corpo = client.get(
        reverse("interface:compor-etapa", args=[edital.id, "anexos"])
    ).content.decode()

    assert "Anexos do Edital" in corpo
    assert "Este Edital ainda não publica anexo nenhum" in corpo


def test_subir_o_arquivo_e_o_que_cria_o_anexo(client, seletor_ligado, edital):
    """FR-015a — não existe Anexo sem artefato, e por isso não há estado intermediário a validar."""
    identificar(client, "ana.elaboradora", ["elaborador"])

    acao(client, edital, acao="anexar", rotulo="ANEXO I — REQUERIMENTO", arquivo=arquivo())

    anexo = AnexoEdital.objects.get(edital=edital)
    assert anexo.rotulo == "ANEXO I — REQUERIMENTO"
    assert anexo.artefato.document_hash
    assert anexo.artefato.congelado_em is None, "rascunho: só a publicação congela"


def test_o_que_nao_e_pdf_e_recusado_pelo_conteudo(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])

    acao(
        client,
        edital,
        acao="anexar",
        rotulo="ANEXO I",
        arquivo=SimpleUploadedFile("foto.pdf", b"\xff\xd8\xff imagem", content_type="image/jpeg"),
    )

    assert not AnexoEdital.objects.filter(edital=edital).exists()


def test_substituir_troca_os_bytes_e_nao_preserva_o_anterior(client, seletor_ligado, edital):
    """FR-010a — artefato que nenhuma publicação referencia não é histórico de nada."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    acao(client, edital, acao="anexar", rotulo="ANEXO I", arquivo=arquivo("A"))
    anexo = AnexoEdital.objects.get(edital=edital)
    anterior = anexo.artefato_id

    acao(client, edital, acao="substituir", anexo=str(anexo.id), arquivo=arquivo("B"))

    anexo.refresh_from_db()
    assert anexo.artefato_id != anterior, "a identidade do Anexo é a mesma; os bytes não"
    assert not ArtefatoAnexo.objects.filter(pk=anterior).exists()


def test_remover_deixa_lacuna_e_nao_renumera_ninguem(client, seletor_ligado, edital):
    """FR-008 — renumerar aqui faria o conteúdo publicado divergir do que está impresso no PDF."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    for posicao in range(3):
        acao(
            client,
            edital,
            acao="anexar",
            rotulo=f"ANEXO {posicao + 1}",
            arquivo=arquivo(chr(ord("A") + posicao)),
        )
    segundo = AnexoEdital.objects.get(edital=edital, order=2)

    acao(client, edital, acao="remover", anexo=str(segundo.id))

    restantes = list(AnexoEdital.objects.filter(edital=edital).order_by("order"))
    assert [anexo.order for anexo in restantes] == [1, 3], "a lacuna fica"
    assert [anexo.rotulo for anexo in restantes] == ["ANEXO 1", "ANEXO 3"]


def test_reordenar_nao_toca_em_rotulo_nenhum(client, seletor_ligado, edital):
    """FR-007 — a ordem é campo próprio justamente para que mexê-la não mexa no rótulo."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    for posicao in range(2):
        acao(
            client,
            edital,
            acao="anexar",
            rotulo=f"ANEXO {posicao + 1}",
            arquivo=arquivo(chr(ord("A") + posicao)),
        )
    primeiro, segundo = AnexoEdital.objects.filter(edital=edital).order_by("order")

    client.post(
        reverse("interface:anexos", args=[edital.id]),
        {"acao": "reordenar", "ordem": [str(segundo.id), str(primeiro.id)]},
    )

    invertidos = list(AnexoEdital.objects.filter(edital=edital).order_by("order"))
    assert [anexo.id for anexo in invertidos] == [segundo.id, primeiro.id]
    assert [anexo.rotulo for anexo in invertidos] == ["ANEXO 2", "ANEXO 1"]


def test_gravar_outra_etapa_do_assistente_nao_apaga_os_anexos(client, seletor_ligado, edital):
    """O modo de falha do `replace_draft`, que é a razão de a coleção ficar fora dele (R-006)."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    criar_anexo(edital, rotulo="ANEXO I — REQUERIMENTO", order=1)

    client.post(
        reverse("interface:compor-etapa", args=[edital.id, "conteudo"]),
        {"secao-0-key": "objeto", "secao-0-content": "Texto do objeto."},
    )

    assert AnexoEdital.objects.filter(edital=edital).count() == 1
