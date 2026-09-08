"""Substituir o artefato de um Anexo pela tela, e o que acontece **entre** as duas fases (020).

O formulário de Retificação confere antes de confirmar, e o arquivo só existe no primeiro POST.
Esta suíte existe porque nenhum teste percorria essa fenda: os de aceitação entravam pela API já
com identidade e resumo corretos, e por isso não viam que a confirmação gravava resumo em branco —
a Retificação nasceria condenada, para ser recusada só na publicação.
"""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from processo_seletivo.editais.models import AnexoEdital, ArtefatoAnexo
from processo_seletivo.publicacoes.models_retificacao import AlteracaoNormativa, Retificacao
from tests.fixtures.anexos import pdf_de_teste
from tests.fixtures.publicacao import publish_original
from tests.fixtures.snapshot import rascunho_completo
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def publicado(api_client, manager_headers, process_payload):
    return publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_completo(), anexos=1
    )


def campo_do_arquivo(corpo):
    """A referência opaca do campo de arquivo — a tela não expõe caminho normativo (FR-019)."""
    import re

    achado = re.search(r'name="arquivo:(g\d+c\d+)"', corpo)
    assert achado, "a tela de Retificação não oferece o campo de arquivo do Anexo"
    return achado.group(1)


def abrir(client, publicado):
    return client.get(reverse("interface:retificar", args=[publicado.id])).content.decode()


def base_da_composicao(corpo):
    """A versão sobre a qual o ato é composto viaja em campo oculto, como no formulário real."""
    import re

    achado = re.search(r'name="base" value="([^"]+)"', corpo)
    assert achado, "a tela não declarou a versão base"
    return achado.group(1)


def test_a_tela_oferece_o_anexo_com_rotulo_ordem_e_arquivo(client, seletor_ligado, publicado):
    identificar(client, "ana.elaboradora", ["elaborador"])

    corpo = abrir(client, publicado)

    assert "Anexo 1 — ANEXO 1 — FORMULÁRIO" in corpo
    assert 'type="file"' in corpo
    assert 'enctype="multipart/form-data"' in corpo


def test_conferir_e_confirmar_sem_reenviar_o_arquivo_grava_identidade_e_resumo(
    client, seletor_ligado, publicado
):
    """O defeito que esta suíte nasceu para pegar (FR-034, FR-035).

    O resumo é lido do artefato **no servidor**, nas duas fases. Um mapa montado no envio voltaria
    vazio na confirmação, e a Alteração do resumo iria em branco — a integridade recusaria a
    publicação depois, longe da causa.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo_inicial = abrir(client, publicado)
    referencia = campo_do_arquivo(corpo_inicial)
    base = base_da_composicao(corpo_inicial)
    arquivo = SimpleUploadedFile(
        "retificado.pdf", pdf_de_teste("Z"), content_type="application/pdf"
    )

    conferencia = client.post(
        reverse("interface:retificar", args=[publicado.id]),
        {
            "base": base,
            "justificativa": "Formulário corrigido",
            f"arquivo:{referencia}": arquivo,
        },
    )
    corpo = conferencia.content.decode()
    novo = ArtefatoAnexo.objects.get(congelado_em__isnull=True)
    client.post(
        reverse("interface:retificar", args=[publicado.id]),
        {
            "base": base,
            "justificativa": "Formulário corrigido",
            "confirmar": "1",
            f"campo:{referencia}": str(novo.id),
        },
    )

    assert "Arquivo do anexo" in corpo
    alteracoes = {
        alteracao.target_path.rsplit("/", 1)[-1]: alteracao.new_value
        for alteracao in AlteracaoNormativa.objects.all()
    }
    assert alteracoes["artifactId"] == str(novo.id)
    assert alteracoes["artifactHash"] == novo.document_hash, (
        "o resumo é do artefato, e não uma string vazia herdada da fase anterior"
    )


def test_confirmar_citando_artefato_de_outra_pessoa_e_recusado(client, seletor_ligado, publicado):
    """A fronteira do artefato pendente: não congelado **e** enviado por quem está retificando."""
    from tests.fixtures.anexos import criar_artefato

    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo_inicial = abrir(client, publicado)
    referencia = campo_do_arquivo(corpo_inicial)
    base = base_da_composicao(corpo_inicial)
    alheio = criar_artefato(marca="Y")  # `enviado_por` é "preparador", e não a pessoa da sessão

    resposta = client.post(
        reverse("interface:retificar", args=[publicado.id]),
        {
            "base": base,
            "justificativa": "Tentativa",
            "confirmar": "1",
            f"campo:{referencia}": str(alheio.id),
        },
    )

    assert not Retificacao.objects.exists()
    assert "não foi encontrado" in resposta.content.decode()


def test_o_ciclo_inteiro_pela_tela_publica_e_os_dois_artefatos_respondem(
    client, api_client, seletor_ligado, publicado
):
    """A jornada da US3 pelo canal do ator, sem escrita direta no banco em passo nenhum."""
    from tests.fixtures.publicacao import publish_retification

    identificar(client, "ana.elaboradora", ["elaborador"])
    antigo = AnexoEdital.objects.get(edital=publicado).artefato_id
    corpo_inicial = abrir(client, publicado)
    referencia = campo_do_arquivo(corpo_inicial)
    base = base_da_composicao(corpo_inicial)

    client.post(
        reverse("interface:retificar", args=[publicado.id]),
        {
            "base": base,
            "justificativa": "Formulário corrigido",
            f"arquivo:{referencia}": SimpleUploadedFile(
                "retificado.pdf", pdf_de_teste("Z"), content_type="application/pdf"
            ),
        },
    )
    novo = ArtefatoAnexo.objects.get(congelado_em__isnull=True)
    client.post(
        reverse("interface:retificar", args=[publicado.id]),
        {
            "base": base,
            "justificativa": "Formulário corrigido",
            "confirmar": "1",
            f"campo:{referencia}": str(novo.id),
        },
    )
    publish_retification(api_client, Retificacao.objects.get(), suffix="tela")

    respostas = [client.get(reverse("public-anexo", args=[item])) for item in (antigo, novo.id)]
    assert [resposta.status_code for resposta in respostas] == [200, 200]
    assert respostas[0].content != respostas[1].content
