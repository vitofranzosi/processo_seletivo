"""Os destinos que a tela do Edital oferece, por ator (033, US1).

**Dois requisitos moram aqui, e eles falham de modos opostos.** A `FR-473` falha quando um destino
que o ator alcança **não** é oferecido — foi o `ACH-40`, e é o que este arquivo abre prendendo. A
`FR-476` falha quando um destino que ele **não** alcança é oferecido — defeito que o código já
corrigiu uma vez, quando quem julga recursos via "Classificação final" e recebia erro ao clicar.
Um teste que prende uma não prende a outra, e por isso os dois lados estão aqui.

**A lista esperada da presidência foi medida, e não desejada** (`FR-475`). Antes de escrever
qualquer linha de implementação, a tela foi renderizada para os seis papéis e o que ela entregava
foi anotado: a presidência via a ordenação do marco e a ocupação, e mais nada. É contra isso que
"nenhum a menos" se afere — contra a intenção, "nenhum a menos" seria sempre verdade.
"""

import re

import pytest
from django.urls import reverse

from tests.fixtures.divulgacao import montar_ato_publicavel, montar_marco
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True)]

_SECAO = re.compile(r'<section aria-labelledby="classificacao-titulo".*?</section>', re.DOTALL)
_LINK = re.compile(r'<a href="([^"]+)"[^>]*>([^<]*)</a>')


def _destinos(client, edital):
    """Os caminhos que o bloco de classificação oferece, como pares (rótulo, URL).

    Lidos **da seção**, e não do documento: a tela do Edital é cheia de link, e procurar a URL da
    divulgação no corpo inteiro acharia o menu, a trilha ou o histórico e responderia "oferece"
    sem que o bloco tivesse mudado.
    """
    corpo = client.get(reverse("interface:detalhe", args=[edital.id])).content.decode()
    bloco = _SECAO.search(corpo)
    if bloco is None:
        return None
    return [(texto.strip(), href) for href, texto in _LINK.findall(bloco.group(0))]


def _urls(destinos):
    return [url for _, url in (destinos or [])]


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload):
    """Edital publicado, marco classificatório e **ato emitido** — há o que divulgar."""
    return montar_ato_publicavel(
        gestor, api_client, manager_headers, process_payload, seed=91, codigo="0791"
    )


@pytest.fixture
def sem_ato(gestor, api_client, manager_headers, process_payload):
    """O mesmo, com o marco **sem ato emitido**: não há o que divulgar."""
    return montar_marco(
        gestor, api_client, manager_headers, process_payload, seed=92, codigo="0792"
    )


def _divulgacao(certame):
    return reverse(
        "interface:previa-de-publicacao",
        args=[certame["edital"].id, certame["marco"], certame["ato"].id],
    )


# --- FR-474 e SC-164 · o Publicador puro -------------------------------------------------------


def test_o_publicador_puro_ve_o_caminho_ate_a_divulgacao(client, seletor_ligado, certame):
    """`FR-474` e `SC-164`: o `ACH-40`, do lado de quem o sofria.

    Paula tem `resultado:publicar` e **nenhum vínculo de comissão**. A tela de divulgação abre
    para ela desde sempre; o que não existia era caminho até lá. Hoje ela só chega montando a URL.
    """
    identificar(client, "paula.publicadora", ["publicador"])

    destinos = _destinos(client, certame["edital"])

    assert destinos is not None, "o bloco de classificação não apareceu para quem publica"
    assert _divulgacao(certame) in _urls(destinos)


def test_o_publicador_puro_nao_ve_o_que_nao_e_dele(client, seletor_ligado, certame):
    """`FR-476`: a divulgação é dele; ordenação, corte e ocupação não são.

    Oferecer o que se vai recusar é pior do que não oferecer — e aqui o custo é nomeado: cada um
    desses caminhos responderia "não encontrado" a Paula.
    """
    identificar(client, "paula.publicadora", ["publicador"])

    assert _urls(_destinos(client, certame["edital"])) == [_divulgacao(certame)]


# --- FR-475 · a contraprova que mais importa ---------------------------------------------------


def test_a_presidencia_sem_publicar_nao_perde_destino_nenhum(client, seletor_ligado, certame):
    """`FR-475`: esta feature acrescenta destino, e **nunca** retira.

    A lista abaixo é a que a tela entregava **antes** da feature, medida contra este mesmo
    cenário. Se ela encolher, a 033 tirou caminho de quem já o tinha — o que é regressão, e não
    melhoria, por melhor que seja o resto.
    """
    edital, marco = certame["edital"], certame["marco"]
    identificar(client, "maria", [])

    esperados = [
        reverse("interface:ordenacao", args=[edital.id, marco]),
        # **O corte entrou na lista com a `037`** (`FR-538`), e o marco deste cenário é justamente
        # o que não declara regra de corte — era dele que o caminho sumia. A promessa deste caso
        # continua sendo "nenhum a menos", e ela não é desfeita por um a mais.
        reverse("interface:corte", args=[edital.id, marco]),
        reverse("interface:ocupacao", args=[edital.id, marco]),
    ]

    assert _urls(_destinos(client, edital)) == esperados


def test_a_presidencia_sem_publicar_nao_ve_a_divulgacao(client, seletor_ligado, certame):
    """O recíproco de `FR-476`, no eixo oposto: presidir não concede divulgar.

    É a mesma segregação que `_edital_para_publicar` já defende no servidor — quem emitiu o ato
    não ganha, por tê-lo emitido, o poder de divulgá-lo.
    """
    identificar(client, "maria", [])

    assert _divulgacao(certame) not in _urls(_destinos(client, certame["edital"]))


# --- FR-473 e FR-476 · a união, o vazio e o julgador -------------------------------------------


def test_quem_preside_e_publica_ve_a_uniao_sem_repetir(client, seletor_ligado, certame):
    """`FR-473`: o caso normal numa equipe de duas ou três pessoas.

    A asserção de **não repetir** não é estética: a derivação por destino consulta o mesmo marco
    por mais de um eixo, e a forma natural de errar é somar as listas em vez de uni-las.
    """
    edital, marco = certame["edital"], certame["marco"]
    identificar(client, "maria", ["publicador"])

    urls = _urls(_destinos(client, edital))

    assert urls == [
        reverse("interface:ordenacao", args=[edital.id, marco]),
        # Acrescentado pela `037` (`FR-538`) — ver o caso da presidência, acima.
        reverse("interface:corte", args=[edital.id, marco]),
        reverse("interface:ocupacao", args=[edital.id, marco]),
        _divulgacao(certame),
    ]
    assert len(urls) == len(set(urls)), f"destino repetido na união dos dois eixos: {urls}"


def test_quem_nao_alcanca_nada_nao_ve_o_bloco(client, seletor_ligado, certame):
    """`FR-476`: ausência de bloco não é recusa — é ausência."""
    identificar(client, "estranho", [])

    assert _destinos(client, certame["edital"]) is None


def test_quem_julga_recursos_continua_sem_ver_o_bloco(client, seletor_ligado, certame):
    """A regressão que a feature não pode reintroduzir.

    Quem julga recursos não gere a comissão, não a preside e não consulta auditoria. Ele via
    "Classificação final" e recebia erro ao clicar; o código corrigiu isso, e derivar por destino
    é justamente o desenho que pode desfazer a correção sem que nada mais acuse.
    """
    identificar(client, "juliana", ["julgador"])

    assert _destinos(client, certame["edital"]) is None


def test_a_auditoria_continua_lendo_o_que_lia(client, seletor_ligado, certame):
    """A `FR-475` vista do outro eixo: quem audita não perde leitura, e não ganha ação."""
    edital, marco = certame["edital"], certame["marco"]
    identificar(client, "iris", ["auditor"])

    assert _urls(_destinos(client, edital)) == [
        reverse("interface:ordenacao", args=[edital.id, marco]),
        # Acrescentado pela `037` (`FR-538`) — ver o caso da presidência, acima.
        reverse("interface:corte", args=[edital.id, marco]),
        reverse("interface:ocupacao", args=[edital.id, marco]),
    ]


# --- as duas ausências que não são recusa ------------------------------------------------------


def test_marco_sem_ato_emitido_nao_oferece_divulgacao(client, seletor_ligado, sem_ato):
    """Oferecer caminho que termina em nada é o mesmo defeito, com outra roupa.

    O marco existe e é classificatório; o que não existe é ato a divulgar. O Publicador puro não
    alcança mais nada neste Edital, então o bloco inteiro não tem por que aparecer para ele.
    """
    identificar(client, "paula.publicadora", ["publicador"])

    assert _destinos(client, sem_ato["edital"]) is None


def test_edital_nao_publicado_nao_mostra_o_bloco_para_ninguem(client, seletor_ligado, edital):
    """A segunda ausência: sem conteúdo publicado não há marco a listar.

    Vale para ator nenhum — inclusive para quem preside e para quem publica —, e a razão não é
    autorização: é que não existe marco publicado sobre o qual oferecer coisa alguma.
    """
    for subject, papeis in (("maria", []), ("paula.publicadora", ["publicador"])):
        identificar(client, subject, papeis)

        assert _destinos(client, edital) is None


# --- 037 · FR-538 e FR-540 · o destino do corte deixa de pender da regra -----------------------


@pytest.fixture
def com_regra_de_corte(gestor, api_client, manager_headers, process_payload):
    """O contraponto do `certame`: um marco que **declara** regra de corte.

    Vem de outro módulo de fixtures porque é lá que o cenário do corte mora, e duplicá-lo aqui
    criaria uma segunda verdade sobre o que é "marco com regra".
    """
    from tests.fixtures.corte import MARCO, montar_cenario_do_corte

    edital, _, _ = montar_cenario_do_corte(
        gestor, api_client, manager_headers, process_payload, prefixo="destinos-037"
    )
    return edital, MARCO


def test_o_marco_sem_regra_de_corte_passa_a_oferecer_o_destino(client, seletor_ligado, certame):
    """`FR-538`: era dele que o caminho sumia, e é ele quem mais precisa da tela.

    A tela de destino **já explica** por que não há faixa, com frase escrita para este caso — o
    que faltava era só o link. Condicioná-lo à regra escondia a explicação de quem não declarou a
    regra, que é precisamente quem precisava lê-la.
    """
    edital, marco = certame["edital"], certame["marco"]
    identificar(client, "maria", [])

    assert reverse("interface:corte", args=[edital.id, marco]) in _urls(_destinos(client, edital))


def test_o_marco_com_regra_de_corte_continua_oferecendo_o_destino(
    client, seletor_ligado, com_regra_de_corte
):
    """A outra metade da `FR-538`: acrescentar não pode ter virado substituir."""
    edital, marco = com_regra_de_corte
    identificar(client, "carlos", ["gestor"])

    assert reverse("interface:corte", args=[edital.id, marco]) in _urls(_destinos(client, edital))


def test_quem_nao_alcanca_a_classificacao_nao_recebe_o_destino_do_corte(
    client, seletor_ligado, certame
):
    """`FR-540`: o que saiu foi a condição da **regra**, e não a do alcance.

    As duas moram a dez linhas uma da outra, e confundi-las produz becos opostos. Paula publica
    resultado e não classifica: o corte não é dela, e continua não lhe sendo oferecido — ainda que
    o marco agora ofereça o destino a quem classifica.
    """
    edital, marco = certame["edital"], certame["marco"]
    identificar(client, "paula.publicadora", ["publicador"])

    assert reverse("interface:corte", args=[edital.id, marco]) not in _urls(
        _destinos(client, edital)
    )
