"""Orientação dentro da tela de Retificação.

Um Edital institucional publicado rende dezenas de linhas editáveis e vários metros de rolagem.
A tela as entregava numa lista plana: sem sumário, sem divisão, e com a Modalidade desenhada como
irmã do Perfil de que ela é. Quem vinha corrigir **um** prazo lia legenda por legenda até achar.

O que se afirma aqui é o que a divisão **não** pode custar: a referência opaca de cada campo é a
posição na lista (FR-019), e o POST reconstrói a mesma lista para traduzi-la de volta. Reordenar
para exibir apontaria cada campo enviado para o vizinho dele.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.interface import retificacao as retificacao_ui
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    """Um Edital com Modalidade, Etapa e Seção — o mínimo para haver o que dividir e aninhar."""
    from tests.fixtures.snapshot import rascunho_com_etapas

    return publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_com_etapas(), anexos=2
    )


@pytest.fixture
def vigente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def abrir(client, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    return client.get(reverse("interface:retificar", args=[edital.id])).content.decode()


# --- a divisão em seções ------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_cada_linha_cai_na_secao_a_que_ela_pertence(vigente):
    grupos = retificacao_ui.campos_editaveis(vigente.content)
    secoes = {secao["id"]: secao for secao in retificacao_ui.agrupar_em_secoes(grupos)}

    assert [grupo["tipo"] for grupo in secoes["identificacao"]["grupos"]] == ["Edital"]
    assert {grupo["tipo"] for grupo in secoes["cronograma"]["grupos"]} == {"Evento"}
    assert {grupo["tipo"] for grupo in secoes["anexos"]["grupos"]} == {"Anexo"}
    # Perfil e o que pertence a ele ficam na mesma seção — é a relação que a lista plana perdia.
    assert "Modalidade" in {grupo["tipo"] for grupo in secoes["perfis"]["grupos"]}


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_dividir_em_secoes_nao_reordena_nem_renumera(vigente):
    """A referência é a posição na lista, e a lista é a mesma antes e depois da divisão.

    É a condição de FR-019 continuar de pé: se a exibição reordenasse, `g7c2` chegaria ao POST
    significando um campo e seria traduzido em outro.
    """
    grupos = retificacao_ui.campos_editaveis(vigente.content)
    achatado = [
        grupo for secao in retificacao_ui.agrupar_em_secoes(grupos) for grupo in secao["grupos"]
    ]

    assert [grupo["referencia"] for grupo in achatado] == [grupo["referencia"] for grupo in grupos]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_secao_que_acrescenta_existe_mesmo_vazia(api_client, manager_headers, process_payload):
    """Sem Anexo nenhum, o botão que cria o primeiro não teria onde ficar."""
    sem_anexos = publish_original(api_client, manager_headers, process_payload)
    conteudo = VersaoConsolidada.objects.filter(edital=sem_anexos).latest("materialized_at")
    secoes = retificacao_ui.agrupar_em_secoes(retificacao_ui.campos_editaveis(conteudo.content))

    anexos = next(secao for secao in secoes if secao["id"] == "anexos")
    assert anexos["grupos"] == []


def test_secao_sem_linha_e_sem_acrescentar_nao_aparece():
    """Um título seguido de nada não é informação, e no sumário é um salto para o vazio."""
    secoes = retificacao_ui.agrupar_em_secoes(retificacao_ui.campos_editaveis({}))

    assert [secao["id"] for secao in secoes] == ["identificacao", "perfis", "cronograma", "anexos"]


# --- o que a tela entrega -----------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_indice_do_topo_alcanca_cada_secao(client, seletor_ligado, edital):
    """Âncora que não resolve é um link que não leva a lugar nenhum — e some sem erro."""
    corpo = abrir(client, edital)

    indice = re.search(r'<nav class="indice".*?</nav>', corpo, re.S)
    assert indice, "a tela precisa de um sumário para ser percorrida"
    alvos = re.findall(r'<a href="#([\w-]+)">', indice.group(0))
    assert len(alvos) > 1, alvos
    for alvo in alvos:
        assert f'id="{alvo}"' in corpo, f"o índice aponta para #{alvo}, que não existe na página"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_modalidade_e_desenhada_sob_o_perfil_de_que_ela_e(client, seletor_ligado, edital):
    corpo = abrir(client, edital)

    linhas = dict(
        (nome, classes)
        for classes, nome in re.findall(
            r'<fieldset class="([^"]*)" data-linha data-nome="([^"]*)"', corpo
        )
    )

    perfil = next(nome for nome in linhas if nome.startswith("Perfil "))
    modalidade = next(nome for nome in linhas if nome.startswith("Modalidade "))
    assert "aninhada" not in linhas[perfil]
    assert "aninhada" in linhas[modalidade], "a Modalidade pertence ao Perfil, e não é irmã dele"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_campo_de_arquivo_diz_qual_pdf_esta_publicado_hoje(client, seletor_ligado, edital):
    """Um seletor de arquivo vazio não distingue "não há anexo" de "há um, e trocar é opcional"."""
    corpo = abrir(client, edital)

    assert "Deixe em branco para manter" in corpo
    # O nome do arquivo que a coleção publicou, e não uma frase genérica sobre haver algo lá.
    assert re.search(r"Hoje: [^<]*\.pdf", corpo), "a tela precisa nomear o PDF vigente"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_conferir_o_que_vai_mudar_nao_exige_a_justificativa(
    client, seletor_ligado, edital, vigente
):
    """Fundamentar vem depois de conferir, e não antes.

    A justificativa é exigida para **criar** a Retificação. Exigi-la também para ver o resumo
    obrigava a escrever a fundamentação de uma alteração antes de poder olhar se a alteração é a
    que se queria — e num Edital extenso é justamente o resumo que responde isso.
    """
    corpo = abrir(client, edital)
    assert re.search(r"<button[^>]*formnovalidate[^>]*>\s*Ver o que vai mudar", corpo), (
        "o botão de conferir precisa dispensar a validação do navegador"
    )

    from tests.interface.test_retificar import campos

    enviado = campos(vigente, **{"/title": "Título retificado"})
    resposta = client.post(
        reverse("interface:retificar", args=[edital.id]), {**enviado, "justificativa": ""}
    )

    assert resposta.status_code == 200
    assert "O que vai mudar" in resposta.content.decode()
