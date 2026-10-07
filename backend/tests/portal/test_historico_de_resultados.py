"""Todo resultado divulgado continua alcançável pela página do Edital (047, US5).

`FR-772`, `FR-773`, `SC-285`. A `017` preservou o endereço de toda publicação sucedida, e a página
de uma sucedida já levava à vigente. Faltava a direção inversa: o preliminar que o definitivo
sucedeu só era alcançável por quem tinha guardado o endereço dele.
"""

import json
import re
import uuid

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.classificacao.models import AtoDeOrdenacao, OrigemDaOrdem
from processo_seletivo.divulgacao.models import Natureza, PublicacaoResultado
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.comissao import rascunho_com_etapas
from tests.fixtures.divulgacao import montar_ato_publicavel, publicar_o_ato
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.publicacao import publish_original
from tests.fixtures.sorteio import LISTA_PCD, LISTA_PPI, MARCO, marco_com_metodo

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

PCD = "Pessoas com deficiência"
PPI = "Pessoas pretas, pardas e indígenas"


@pytest.fixture
def cadeia(gestor, api_client, manager_headers, process_payload):
    """Preliminar sucedido por definitivo, no mesmo marco e na mesma lista."""
    cenario = montar_ato_publicavel(
        gestor, api_client, manager_headers, process_payload, seed=81, codigo="0881", primeiro=1811
    )
    preliminar = publicar_o_ato(cenario, chave="publicar-047-81")
    definitiva = publicar_o_ato(cenario, natureza="DEFINITIVA", chave="publicar-047-81-def")
    return cenario, preliminar, definitiva


def pagina_do_edital(client, edital):
    return client.get(reverse("portal:selecao", args=[edital.id])).content.decode()


def secao_de_resultados(corpo):
    achado = re.search(r'<section class="resultados.*?</section>', corpo, flags=re.S)
    return achado.group(0) if achado else ""


def main_do_resultado(client, publicacao):
    corpo = client.get(reverse("portal:resultado", args=[publicacao.id])).content.decode()
    return re.search(r"<main[^>]*>(.*)</main>", corpo, re.DOTALL).group(1)


def test_o_preliminar_sucedido_esta_a_um_clique_da_pagina_do_edital(client, cadeia):
    """`FR-772` e `SC-285`: o link para o preliminar está na primeira página que a pessoa abre."""
    cenario, preliminar, definitiva = cadeia

    secao = secao_de_resultados(pagina_do_edital(client, cenario["edital"]))
    vigentes = re.sub(
        r'<details class="publicacoes-anteriores">.*?</details>', "", secao, flags=re.S
    )
    historico = re.search(r'<details class="publicacoes-anteriores">.*?</details>', secao, re.S)

    assert f"/selecoes/resultados/{definitiva.id}/" in vigentes
    assert f"/selecoes/resultados/{preliminar.id}/" not in vigentes, "o histórico virou destaque"
    assert historico is not None
    assert f"/selecoes/resultados/{preliminar.id}/" in historico.group(0)
    assert "Resultado preliminar" in historico.group(0)
    assert "sucedido" in historico.group(0)
    assert timezone.localtime(preliminar.publicado_em).strftime("%d/%m/%Y") in historico.group(0)


def test_a_pagina_do_definitivo_leva_as_anteriores(client, cadeia):
    """`FR-773`: a direção inversa da `FR-044` da 017."""
    _, preliminar, definitiva = cadeia

    corpo = main_do_resultado(client, definitiva)

    assert "Publicações anteriores deste resultado" in corpo
    assert f"/selecoes/resultados/{preliminar.id}/" in corpo


def test_a_publicacao_sem_anterior_nao_desenha_historico(client, cadeia):
    _, preliminar, _ = cadeia

    assert "Publicações anteriores" not in main_do_resultado(client, preliminar)


def test_nenhum_identificador_de_ator_aparece(client, cadeia):
    """`FR-776`: quem publicou é registro de auditoria, e não informação pública."""
    cenario, preliminar, definitiva = cadeia

    secao = secao_de_resultados(pagina_do_edital(client, cenario["edital"]))

    for publicacao in (preliminar, definitiva):
        assert publicacao.publicado_por not in secao


# --- A cadeia de três e as listas ----------------------------------------------------------------


@pytest.fixture
def certame_com_listas(api_client, manager_headers, process_payload):
    rascunho = rascunho_com_etapas()
    marco_com_metodo(rascunho, perfil_id=PROFILE_ID, etapa_id=rascunho["stages"][1]["id"])
    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho)
    return edital, VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def _ato(edital, versao, *, lista_id=None, anterior=None):
    return AtoDeOrdenacao.objects.create(
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=lista_id,
        ato_anterior=anterior,
        motivo_da_sucessao="Sorteio anulado." if anterior is not None else "",
        origem=OrigemDaOrdem.SORTEIO,
        versao=versao,
        universo={
            "editalId": str(edital.id),
            "profileId": PROFILE_ID,
            "milestoneId": MARCO,
            "versionId": str(versao.id),
            "stageResults": [],
            "origem": "SORTEIO",
        },
        emitido_por="cpf:presidente",
        emitido_em=timezone.now(),
    )


def _publicar(
    edital, ato, *, lista_id=None, natureza=Natureza.PRELIMINAR, anterior=None, lista_nome=""
):
    """A mesma gravação de `test_publicacao_por_lista.py`: o que se testa aqui é a leitura.

    `lista_nome` é o que `compor` grava no cabeçalho: o nome da Modalidade, ou vazio no ato sem
    lista.
    """
    cabecalho = {"marco": "Classificacao final", "lista": lista_nome}
    return PublicacaoResultado.objects.create(
        edital=edital,
        ato=ato,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=lista_id,
        natureza=natureza,
        publicacao_anterior=anterior,
        conteudo_publico=json.dumps({"cabecalho": cabecalho, "posicoes": []}).encode(),
        conteudo_publico_hash="0" * 64,
        publicado_por="cpf:publicadora",
        publicado_em=timezone.now(),
        signatario_id=uuid.uuid4(),
        signatario_nome="Diretora-Geral",
        signatario_cargo="Diretoria",
    )


def test_a_cadeia_de_tres_aparece_em_ordem_e_so_a_ultima_e_vigente(client, certame_com_listas):
    edital, versao = certame_com_listas
    primeiro = _ato(edital, versao, lista_id=LISTA_PPI)
    p1 = _publicar(edital, primeiro, lista_id=LISTA_PPI)
    p2 = _publicar(edital, primeiro, lista_id=LISTA_PPI, natureza=Natureza.DEFINITIVA, anterior=p1)
    segundo = _ato(edital, versao, lista_id=LISTA_PPI, anterior=primeiro)
    p3 = _publicar(edital, segundo, lista_id=LISTA_PPI, natureza=Natureza.DEFINITIVA, anterior=p2)

    secao = secao_de_resultados(pagina_do_edital(client, edital))
    historico = re.search(r'<details class="publicacoes-anteriores">.*?</details>', secao, re.S)

    vigentes = secao.replace(historico.group(0), "")
    assert f"/resultados/{p3.id}/" in vigentes
    anteriores = historico.group(0)
    assert anteriores.index(f"/resultados/{p2.id}/") < anteriores.index(f"/resultados/{p1.id}/")
    assert "Publicações anteriores (2)" in anteriores


def test_o_historico_de_uma_lista_nao_aparece_sob_outra(client, certame_com_listas):
    """A decisão do eixo da lista, da 021: a cadeia da PPI não é a da PcD.

    **Desde a 062 o histórico é um bloco por etapa** (D-001), e não um por lista — a garantia muda
    de lugar sem mudar de conteúdo: a linha vigente da PcD não carrega histórico, e o item sucedido
    da PPI diz que é da PPI.
    """
    edital, versao = certame_com_listas
    da_ppi = _ato(edital, versao, lista_id=LISTA_PPI)
    ppi_1 = _publicar(edital, da_ppi, lista_id=LISTA_PPI, lista_nome=PPI)
    _publicar(
        edital,
        da_ppi,
        lista_id=LISTA_PPI,
        natureza=Natureza.DEFINITIVA,
        anterior=ppi_1,
        lista_nome=PPI,
    )
    da_pcd = _ato(edital, versao, lista_id=LISTA_PCD)
    pcd = _publicar(edital, da_pcd, lista_id=LISTA_PCD, lista_nome=PCD)

    secao = secao_de_resultados(pagina_do_edital(client, edital))
    linhas = re.findall(r'<li class="lista-divulgada">.*?</li>', secao, re.S)
    linha_da_pcd = next(linha for linha in linhas if f"/resultados/{pcd.id}/" in linha)
    historico = re.search(r'<details class="publicacoes-anteriores">.*?</details>', secao, re.S)
    item_da_ppi = re.search(
        rf'<li><a href="/selecoes/resultados/{ppi_1.id}/">.*?</li>', historico.group(0), re.S
    )

    assert f"/resultados/{ppi_1.id}/" not in linha_da_pcd
    assert "publicacoes-anteriores" not in linha_da_pcd
    assert item_da_ppi is not None
    assert item_da_ppi.group(0).split("<span")[0].endswith(PPI)
    assert PCD not in item_da_ppi.group(0)


def test_as_ordens_de_um_mesmo_marco_tem_links_que_se_distinguem(client, certame_com_listas):
    """Três listas no mesmo marco eram três links de texto idêntico, e as anteriores também (#255).

    A página do Edital dizia natureza e marco, e só a lista distingue as três ordens: quem chegava
    não tinha como saber qual abrir, e o leitor de tela anunciava três vezes o mesmo link. A ampla
    concorrência, gravada sem nome, aparece pelo nome do recorte, como no documento oficial.

    **Desde a 062 o texto visível é só o nome da lista**, e o que distingue a vigente da anterior
    da mesma lista é o nome acessível, que continua pela natureza, pela etapa e pelo Perfil (D-006).
    """
    edital, versao = certame_com_listas
    for lista_id, nome in ((None, ""), (LISTA_PCD, PCD), (LISTA_PPI, PPI)):
        ato = _ato(edital, versao, lista_id=lista_id)
        preliminar = _publicar(edital, ato, lista_id=lista_id, lista_nome=nome)
        _publicar(
            edital,
            ato,
            lista_id=lista_id,
            natureza=Natureza.DEFINITIVA,
            anterior=preliminar,
            lista_nome=nome,
        )

    secao = secao_de_resultados(pagina_do_edital(client, edital))
    links = re.findall(r'<a href="/selecoes/resultados/[^"]+/">(.*?)</a>', secao, re.S)
    visiveis = [link.split("<span")[0] for link in links]
    acessiveis = [re.sub(r"<[^>]+>", "", link) for link in links]

    assert len(links) == 6
    assert len(set(acessiveis)) == 6, f"nomes acessíveis indistinguíveis: {acessiveis}"
    for nome in ("Ampla concorrência", PCD, PPI):
        assert visiveis.count(nome) == 2, "a vigente e a anterior, cada uma com o nome da lista"
