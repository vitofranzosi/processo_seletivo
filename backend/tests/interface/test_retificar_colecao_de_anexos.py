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
    """**Seis** anexos, e o cenário é remover o quarto.

    Três bastariam para haver lacuna, e não bastam para o que a FR-008 afirma: com o do meio, um
    engano de renumeração ainda produziria uma sequência plausível. Com seis, remover o quarto tem
    de deixar 1, 2, 3, 5 e 6 — e qualquer recálculo aparece.
    """
    return publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_completo(), anexos=6
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


def ocultos_de(corpo, prefixo):
    """Os campos ocultos que a conferência devolveu, como o navegador os reenviaria.

    Fabricar o segundo POST a partir do banco prova que o servidor sabe; provar que o **formulário**
    devolve o que a confirmação precisa é outra coisa — e é a que faltava.
    """
    return {
        nome: valor
        # Tolerante a quebra de linha entre os atributos: o template quebra, e um regex de uma
        # linha só encontraria metade dos campos — e o teste acusaria o produto por um defeito seu.
        for nome, valor in re.findall(
            r'<input type="hidden"\s+name="([^"]+)"\s+value="([^"]*)"', corpo
        )
        if nome.startswith(prefixo)
    }


def conteudo_vigente(publicado):
    return VersaoConsolidada.objects.filter(edital=publicado).latest("materialized_at").content


def test_alterar_o_rotulo_de_um_anexo_nao_toca_no_rotulo_de_nenhum_outro(
    client, api_client, seletor_ligado, publicado
):
    """FR-006 e FR-007 — o número está dentro do rótulo, e ninguém o recalcula."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = abrir(client, publicado)
    campo = referencia_do_campo(corpo, "ANEXO 2 — FORMULÁRIO", "Rótulo")

    enviar(client, publicado, {f"campo:{campo}": "ANEXO II — AUTODECLARAÇÃO"}, confirmar=True)
    publish_retification(api_client, _retificacao(), suffix="rotulo")

    rotulos = [anexo["label"] for anexo in conteudo_vigente(publicado)["attachments"]]
    assert rotulos == [
        "ANEXO 1 — FORMULÁRIO",
        "ANEXO II — AUTODECLARAÇÃO",
        "ANEXO 3 — FORMULÁRIO",
        "ANEXO 4 — FORMULÁRIO",
        "ANEXO 5 — FORMULÁRIO",
        "ANEXO 6 — FORMULÁRIO",
    ]


def test_alterar_a_ordem_editorial_nao_toca_no_rotulo_de_ninguem(
    client, api_client, seletor_ligado, publicado
):
    """FR-007 — a ordem é campo próprio, e mexer nela não recalcula rótulo nenhum.

    É a metade da FR-007 que o teste do rótulo não cobria: lá se mudava o texto e se conferia que os
    outros textos ficaram; aqui se muda a **posição** e se confere a mesma coisa.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    campo = referencia_do_campo(abrir(client, publicado), "ANEXO 2 — FORMULÁRIO", "Ordem editorial")

    enviar(client, publicado, {f"campo:{campo}": "9"}, confirmar=True)
    publish_retification(api_client, _retificacao(), suffix="ordem")

    anexos = conteudo_vigente(publicado)["attachments"]
    por_rotulo = {anexo["label"]: anexo["order"] for anexo in anexos}
    assert por_rotulo["ANEXO 2 — FORMULÁRIO"] == 9
    assert por_rotulo["ANEXO 1 — FORMULÁRIO"] == 1
    assert por_rotulo["ANEXO 3 — FORMULÁRIO"] == 3
    assert sorted(por_rotulo) == [f"ANEXO {n} — FORMULÁRIO" for n in range(1, 7)], (
        "nenhum rótulo foi reescrito porque uma posição mudou"
    )


def test_remover_um_anexo_deixa_lacuna_e_preserva_os_rotulos(
    client, api_client, seletor_ligado, publicado
):
    """FR-008 — renumerar aqui faria a numeração publicada divergir do que está impresso no PDF."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    grupo = referencia_do_grupo(abrir(client, publicado), "ANEXO 4 — FORMULÁRIO")

    enviar(client, publicado, {f"remover:{grupo}": "1"}, confirmar=True)
    publish_retification(api_client, _retificacao(), suffix="remocao")

    anexos = conteudo_vigente(publicado)["attachments"]
    assert [anexo["label"] for anexo in anexos] == [
        f"ANEXO {n} — FORMULÁRIO" for n in (1, 2, 3, 5, 6)
    ]
    assert [anexo["order"] for anexo in anexos] == [1, 2, 3, 5, 6], "a lacuna fica no lugar do 4"


def test_o_anexo_removido_continua_na_publicacao_anterior(
    client, api_client, seletor_ligado, publicado
):
    """FR-033 — remover é deixar de existir na versão seguinte, e nunca apagar do histórico."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    grupo = referencia_do_grupo(abrir(client, publicado), "ANEXO 4 — FORMULÁRIO")
    antes = conteudo_vigente(publicado)["attachments"][3]

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

    identidade = _identidade_da_linha_nova(client, publicado)
    conferencia = enviar(
        client,
        publicado,
        {
            "novo-anexo-0-id": identidade,
            "novo-anexo-0-label": "ANEXO VII — TERMO LGPD",
            "novo-anexo-0-order": "7",
            "arquivo::novo-anexo-0-artifactId": SimpleUploadedFile(
                "termo.pdf", pdf_de_teste("W"), content_type="application/pdf"
            ),
        },
    ).content.decode()

    # A confirmação reenvia o que a conferência devolveu — inclusive a identidade da linha e a do
    # artefato —, que é o que o navegador faz e o que torna repetir o envio inofensivo.
    devolvidos = ocultos_de(conferencia, "novo-anexo-0-")
    assert devolvidos.get("novo-anexo-0-artifactId"), (
        "a conferência precisa devolver a identidade do artefato; sem ela a confirmação a perde"
    )
    enviar(
        client,
        publicado,
        {
            "novo-anexo-0-label": "ANEXO VII — TERMO LGPD",
            "novo-anexo-0-order": "7",
            **devolvidos,
        },
        confirmar=True,
    )
    publish_retification(api_client, _retificacao(), suffix="acrescimo")

    novo = ArtefatoAnexo.objects.get(pk=devolvidos["novo-anexo-0-artifactId"])
    acrescentado = conteudo_vigente(publicado)["attachments"][-1]
    assert acrescentado["id"] == identidade, "a identidade é a que nasceu no fragmento"
    assert acrescentado["label"] == "ANEXO VII — TERMO LGPD"
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
    grupo = referencia_do_grupo(abrir(client, publicado), "ANEXO 2 — FORMULÁRIO")

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


def _identidade_da_linha_nova(client, publicado):
    """A identidade que o fragmento gera para a linha acrescentada, lida do HTML dele."""
    corpo = client.get(reverse("interface:fragmento-retificacao-anexo")).content.decode()
    achado = re.search(r'name="novo-anexo-\d+-id" value="([^"]+)"', corpo)
    assert achado, "o fragmento precisa nascer com identidade própria"
    return achado.group(1)


def _retificacao():
    from processo_seletivo.publicacoes.models_retificacao import Retificacao

    return Retificacao.objects.latest("created_at")
