"""O nível 2: o "Andamento da seleção" no lugar do cartão "Classificação" (127, B2, US5).

**Sem colunas fixas** (FR-4103): a matriz de cada Perfil vem da `jornada()` da `094`. No sorteio
ela começa pela relação; na pontuação, pelas Etapas; a Etapa governada fica entre o corte e a
apuração. **Recolhida** (FR-4101), uma linha por Perfil com o resumo em palavras; **para quem via o
cartão "Classificação"**, e só (D-004); com os mesmos destinos (FR-4108).
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.interface import andamento as a
from tests.fixtures.andamento import certame_p1, certame_s1
from tests.fixtures.convocacao import montar_cenario_da_convocacao
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

SECAO = re.compile(r'<section aria-labelledby="classificacao-titulo".*?</section>', re.S)


def detalhe(client, edital):
    resposta = client.get(reverse("interface:detalhe", args=[edital.id]))
    assert resposta.status_code == 200
    return resposta


def secao(resposta):
    achado = SECAO.search(resposta.content.decode())
    return achado.group(0) if achado else ""


def colunas(bloco):
    """Os títulos das colunas da primeira matriz, depois de "Lista"."""
    cabecalho = re.search(r"<thead>(.*?)</thead>", bloco, re.S).group(1)
    return re.findall(r'<th scope="col">([^<]+)</th>', cabecalho)[1:]


@pytest.fixture
def s1(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    return certame_s1(gestor, api_client, manager_headers, process_payload)


def test_o_andamento_toma_o_lugar_do_cartao_classificacao(client, s1):
    """FR-4100, FR-4101: o título muda, o lugar e o id continuam; uma linha por Perfil, fechada."""
    identificar(client, "carlos", ["gestor"])
    bloco = secao(detalhe(client, s1["edital"]))

    assert '<h2 id="classificacao-titulo">Andamento da seleção</h2>' in bloco
    assert '<p class="linha-das-inscricoes">' in bloco and "3 enviadas" in bloco
    assert bloco.count('<details class="perfil-do-andamento">') == 1, "fechada por padrão"
    assert "por sorteio" in bloco and "1 lista" in bloco


def test_s1_a_matriz_comeca_pela_relacao_e_as_etapas_sem_efeito_vem_no_fim(client, s1):
    """FR-4103, FR-4104, SC-1243: as colunas vêm da configuração."""
    identificar(client, "carlos", ["gestor"])
    bloco = secao(detalhe(client, s1["edital"]))

    assert colunas(bloco) == [
        "Relação",
        "Semente",
        "Sorteio",
        "Corte",
        "Apuração",
        "Resultado",
        "Convocação",
        "Análise documental",
        "Prova didática",
    ]
    assert f'colspan="2">{a.GRUPO_SEM_EFEITO}</th>' in bloco
    assert "sem efeito no GPS" in bloco


def test_p1_a_matriz_comeca_pelas_etapas_e_nao_tem_sorteio(
    client, gestor, api_client, manager_headers, process_payload, seletor_ligado
):
    """SC-1243: na pontuação não há coluna de relação, semente ou sorteio."""
    certame = certame_p1(gestor, api_client, manager_headers, process_payload)
    identificar(client, "maria", [])
    bloco = secao(detalhe(client, certame["edital"]))

    nomes = colunas(bloco)
    assert nomes[:3] == ["Análise documental", "Prova didática", "Ordem"]
    assert "Relação" not in nomes and "Sorteio" not in nomes
    assert nomes[-1] == "Entrevista", "a Etapa que nada consome, onde o Edital a pôs"


def test_p2_a_etapa_governada_fica_entre_o_corte_e_a_apuracao(
    client, gestor, api_client, manager_headers, process_payload, seletor_ligado
):
    edital, _, _ = montar_cenario_da_convocacao(
        gestor, api_client, manager_headers, process_payload, prefixo="b2-127"
    )
    identificar(client, "carlos", ["gestor"])
    bloco = secao(detalhe(client, edital))

    nomes = colunas(bloco)
    assert nomes[nomes.index("Corte") + 1] == "Entrevista"
    assert nomes[nomes.index("Entrevista") + 1] == "Apuração"
    assert a.GRUPO_DA_GOVERNADA in bloco


def test_o_perfil_sem_inscricao_e_uma_linha_so(
    client, gestor, api_client, manager_headers, process_payload, seletor_ligado
):
    """FR-4102."""
    vazio = certame_s1(gestor, api_client, manager_headers, process_payload, quantos=0)
    identificar(client, "carlos", ["gestor"])
    bloco = secao(detalhe(client, vazio["edital"]))

    assert "Não se aplica: nenhuma inscrição enviada." in bloco
    assert "<details" not in bloco


def test_os_destinos_do_cartao_classificacao_continuam(client, s1):
    """FR-4108: os destinos ficam fora da linha recolhida, à vista."""
    identificar(client, "carlos", ["gestor"])
    bloco = secao(detalhe(client, s1["edital"]))
    destinos = bloco.split('<ul class="destinos-do-perfil">', 1)[1]
    for rotulo in ("sorteio público", "conduzir o marco", "corte", "ocupação", "convocação"):
        assert f">{rotulo}</a>" in destinos, rotulo


@pytest.mark.parametrize("papel", ["elaborador", "homologador", "julgador"])
def test_quem_nao_via_o_cartao_classificacao_nao_ve_o_andamento(client, s1, papel):
    """D-004: o nível 2 é de quem via o cartão; o nível 1 continua para todos."""
    identificar(client, "pessoa", [papel])
    resposta = detalhe(client, s1["edital"])
    assert secao(resposta) == ""
    assert "contagem-de-providencias" in resposta.content.decode()


def test_quem_so_publica_nao_ve_o_perfil_sem_ordem(client, s1):
    """D-004: o cartão mostrava a quem publica só o marco com ordem a divulgar."""
    identificar(client, "paula.publicadora", ["publicador"])
    assert secao(detalhe(client, s1["edital"])) == ""


def test_nenhuma_pendencia_so_na_matriz(client, s1):
    """FR-4107: o que a matriz diz em aberto, o nível 1 também diz."""
    identificar(client, "carlos", ["gestor"])
    resposta = detalhe(client, s1["edital"])
    [perfil] = resposta.context["andamento"].perfis
    abertas = {c.natureza for p in perfil.pontos for c in p.celulas.values() if c and c.em_aberto}
    providencias = {item.natureza for item in resposta.context["nivel_1"].itens}
    assert abertas and abertas <= providencias, (abertas, providencias)


def test_a_matriz_rola_dentro_da_moldura(client, s1):
    """FR-4106: a moldura rola, e a página não; a regra está na folha da tela."""
    from django.conf import settings

    identificar(client, "carlos", ["gestor"])
    assert '<div class="moldura-do-andamento"' in secao(detalhe(client, s1["edital"]))
    folha = (
        settings.BASE_DIR / "processo_seletivo/interface/static/interface/telas/andamento.css"
    ).read_text()
    regra = folha.split(".moldura-do-andamento {", 1)[1].split("}", 1)[0]
    assert "overflow-x: auto" in regra


@pytest.mark.parametrize(
    ("subject", "papeis"),
    [("carlos", ["gestor"]), ("auditora", ["auditor"]), ("paula.publicadora", ["publicador"])],
    ids=["gestor", "auditor", "publicador"],
)
def test_todo_link_da_secao_abre_para_quem_o_recebe(
    client, gestor, api_client, manager_headers, process_payload, seletor_ligado, subject, papeis
):
    """Item 7 da revisão do B2, FR-4105: nenhum caminho oferecido que se vá recusar (033)."""
    edital, _, _ = montar_cenario_da_convocacao(
        gestor, api_client, manager_headers, process_payload, prefixo=f"links-{subject}"
    )
    identificar(client, subject, papeis)
    bloco = secao(detalhe(client, edital))
    links = sorted(set(re.findall(r'<a href="([^"]+)"', bloco)))
    assert links, "o cenário deveria oferecer caminho"
    for link in links:
        resposta = client.get(link.replace("&amp;", "&"))
        assert resposta.status_code == 200, (link, resposta.status_code)
