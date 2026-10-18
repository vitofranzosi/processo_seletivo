"""As telas de inscrições e de recursos, sétimo incremento (085).

Nas Inscrições, na Inscrição recebida, nos Recursos e no Recurso a trilha mora no cabeçalho de
contexto, e só lá — é a do Edital com a tela no fim, e passa a levar ao Processo. Ela não traz dado
pessoal que a tela não mostrava, não custa consulta, e não muda o que o Recurso oferece a quem não
alcança o destino. Sem inscrição recebida, a lista mostra o estado vazio, e os rascunhos são região
nomeada. O desenho em si é provado no navegador e pelo inventário visual refeito (quickstart): aqui
fica o que a marcação garante.
"""

import uuid

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from tests.fixtures.candidato import PERFIL_DOCENTE
from tests.fixtures.comissao import inscrever
from tests.fixtures.recursos_us4 import cenario_julgavel
from tests.interface.conftest import identificar
from tests.interface.test_telas_da_presidencia import (
    abrir,
    ate_o_processo,
    comeca_pelo_titulo,
    niveis_em_ordem,
)
from tests.interface.test_telas_de_uso_diario import (
    cabecalho,
    conteudo,
    trilha_unica_no_cabecalho,
)

JULGADORA = "lucia.julgadora"


def ate_o_edital(edital):
    detalhe = reverse("interface:detalhe", args=[edital.id])
    return [
        *ate_o_processo(edital.processo),
        f'<a href="{detalhe}">Edital {edital.number}/{edital.year}</a> ›',
    ]


def sem_consulta_ao_processo(captura):
    """Nenhuma ida ao banco só pelo Processo: ele vem junto do Edital (`FR-1917`).

    Contar a página inteira prenderia este teste a tudo o que ela lê; o que a trilha poderia
    acrescentar é exatamente a leitura preguiçosa do Processo, e é ela que se procura.
    """
    so_o_processo = 'FROM "processos_processoseletivo"'
    return not [q["sql"] for q in captura.captured_queries if so_o_processo in q["sql"]]


@pytest.fixture
def cenario(selecao):
    """Um Edital publicado com uma inscrição enviada, com protocolo.

    Declarado aqui, e não importado do módulo da `012`: a montagem da presidência é mais do que
    estas telas pedem, e importar a fixture de outro módulo é o que a `081` desfaz, no PR 298."""
    inscricao = inscrever(selecao, 1, primeiro=2885, perfil=PERFIL_DOCENTE)[0]
    return {"edital": selecao, "inscricao": inscricao}


@pytest.fixture
def peca(gestor, api_client, manager_headers, process_payload):
    """Edital publicado, marco divulgado e um recurso interposto e admitido."""
    return cenario_julgavel(
        gestor, api_client, manager_headers, process_payload, seed=185, codigo="0885"
    )


# ---- as inscrições ---------------------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.integration
def test_nas_inscricoes_a_trilha_e_a_do_edital_com_a_tela(client, seletor_ligado, cenario):
    """`FR-1910`, `FR-1911`, `FR-1912`, `SC-752`, `SC-753`: GPS › Processos Seletivos › código ›
    Edital › Inscrições, uma vez só, e o conteúdo começa pelo título."""
    identificar(client, "carlos", ["gestor"])
    edital = cenario["edital"]
    with CaptureQueriesContext(connection) as captura:
        corpo = abrir(client, "interface:inscricoes", edital.id)

    trilha = trilha_unica_no_cabecalho(corpo)
    niveis_em_ordem(trilha, ate_o_edital(edital))
    assert trilha.rstrip().endswith('<span aria-current="page">Inscrições</span>')
    assert comeca_pelo_titulo(corpo)
    # A seção é a do endereço: a barra e a trilha dizem a mesma coisa.
    assert f'<a href="{reverse("interface:lista")}" aria-current="true">' in corpo
    assert sem_consulta_ao_processo(captura)


@pytest.mark.django_db
@pytest.mark.integration
def test_na_inscricao_recebida_a_trilha_passa_pelas_inscricoes(client, seletor_ligado, cenario):
    """`FR-1910`, `FR-1911`, `FR-1912`, `FR-1914`, `FR-1917`: … › Edital › Inscrições ›
    protocolo, e nada da pessoa além do protocolo que a página já mostrava."""
    identificar(client, "carlos", ["gestor"])
    edital, inscricao = cenario["edital"], cenario["inscricao"]
    with CaptureQueriesContext(connection) as captura:
        corpo = abrir(client, "interface:inscricao-recebida", inscricao.id)

    trilha = trilha_unica_no_cabecalho(corpo)
    inscricoes = reverse("interface:inscricoes", args=[edital.id])
    niveis_em_ordem(trilha, [*ate_o_edital(edital), f'<a href="{inscricoes}">Inscrições</a> ›'])
    assert trilha.rstrip().endswith(f'<span aria-current="page">{inscricao.protocolo}</span>')
    assert comeca_pelo_titulo(corpo)
    assert inscricao.nome not in trilha
    assert inscricao.email not in trilha
    assert f"Protocolo {inscricao.protocolo}" in conteudo(corpo)
    assert sem_consulta_ao_processo(captura)

    # `FR-1913`: a trilha só leva a portas que quem consulta a inscrição já abre.
    for destino in (
        reverse("interface:processo-detalhe", args=[edital.processo_id]),
        reverse("interface:detalhe", args=[edital.id]),
        inscricoes,
    ):
        assert client.get(destino).status_code == 200, destino


@pytest.mark.django_db
@pytest.mark.integration
def test_no_rascunho_a_pagina_atual_e_em_preenchimento(client, seletor_ligado, inscricao_de_maria):
    """`FR-1911`: sem protocolo, a trilha diz o que a tela já dizia."""
    identificar(client, "carlos", ["gestor"])
    corpo = abrir(client, "interface:inscricao-recebida", inscricao_de_maria.id)

    trilha = trilha_unica_no_cabecalho(corpo)
    assert trilha.rstrip().endswith('<span aria-current="page">Em preenchimento</span>')
    assert comeca_pelo_titulo(corpo)


@pytest.mark.django_db
@pytest.mark.integration
def test_sem_inscricao_recebida_a_lista_mostra_o_estado_vazio(client, seletor_ligado, selecao):
    """`FR-1918`: o estado normal antes de as inscrições abrirem não tem o desenho de aviso."""
    identificar(client, "carlos", ["gestor"])
    corpo = abrir(client, "interface:inscricoes", selecao.id)

    assert '<p class="vazio">Nenhuma inscrição recebida até agora.</p>' in corpo
    assert '<p class="aviso">Nenhuma inscrição recebida' not in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_os_rascunhos_sao_regiao_nomeada_e_continuam_advertidos(
    client, seletor_ligado, inscricao_de_maria
):
    """`FR-1918`, `FR-1919`: a região dos rascunhos tem o nome do título, e a advertência continua
    aviso."""
    identificar(client, "carlos", ["gestor"])
    corpo = abrir(client, "interface:inscricoes", inscricao_de_maria.edital_id)

    regiao = corpo.split('<section aria-labelledby="em-preenchimento">')[1].split("</section>")[0]
    assert '<h2 id="em-preenchimento">Em preenchimento — 1</h2>' in regiao
    assert '<p class="aviso">Rascunhos abertos e ainda não enviados.' in regiao
    assert "Rascunhos em preenchimento neste Edital" in regiao
    assert '<p class="vazio">Nenhuma inscrição recebida até agora.</p>' in corpo


# ---- os recursos -----------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_nos_recursos_e_no_recurso_a_trilha_e_a_do_edital(client, seletor_ligado, peca):
    """`FR-1910` a `FR-1913`, `FR-1917`, `SC-752`, `SC-753`: … › Edital › Recursos, e no recurso
    … › Recursos › protocolo; cada nível abre para quem julga."""
    edital, recurso = peca["cenario"]["edital"], peca["recurso"]
    identificar(client, JULGADORA, ["julgador"])

    with CaptureQueriesContext(connection) as captura:
        lista = abrir(client, "interface:recursos", edital.id)
    trilha = trilha_unica_no_cabecalho(lista)
    niveis_em_ordem(trilha, ate_o_edital(edital))
    assert trilha.rstrip().endswith('<span aria-current="page">Recursos</span>')
    assert comeca_pelo_titulo(lista)
    assert sem_consulta_ao_processo(captura)

    with CaptureQueriesContext(connection) as captura:
        corpo = abrir(client, "interface:recurso", recurso.id)
    trilha = trilha_unica_no_cabecalho(corpo)
    recursos = reverse("interface:recursos", args=[edital.id])
    niveis_em_ordem(trilha, [*ate_o_edital(edital), f'<a href="{recursos}">Recursos</a> ›'])
    assert trilha.rstrip().endswith(f'<span aria-current="page">{recurso.protocolo}</span>')
    assert comeca_pelo_titulo(corpo)
    assert sem_consulta_ao_processo(captura)

    # `FR-1913`: a trilha só leva a portas que quem julga já abre.
    for destino in (
        reverse("interface:lista"),
        reverse("interface:processo-detalhe", args=[edital.processo_id]),
        reverse("interface:detalhe", args=[edital.id]),
        recursos,
    ):
        assert client.get(destino).status_code == 200, destino


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_recurso_continua_condicionando_os_caminhos(client, seletor_ligado, peca):
    """`FR-1914`, `FR-1920`: quem só julga não recebe caminho para a inscrição — nem na trilha, nem
    no bloco de conferir —, e as ações ficam onde estavam. O impedimento antes de qualquer botão é
    provado em `authorization/test_julgamento_de_recurso.py`, que esta feature não muda."""
    recurso, inscricao = peca["recurso"], peca["recurso"].inscricao
    identificar(client, JULGADORA, ["julgador"])
    corpo = abrir(client, "interface:recurso", recurso.id)
    trilha = trilha_unica_no_cabecalho(corpo)

    documentos = reverse("interface:inscricao-recebida", args=[inscricao.id])
    assert documentos not in corpo
    assert "documentos da inscrição</a>" not in corpo
    assert inscricao.nome not in trilha
    assert "Julgar não as concede." in conteudo(corpo)
    assert '<button type="submit" class="botao">Registrar a decisão</button>' in corpo


# ---- fora do escopo --------------------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.integration
def test_a_recusa_continua_com_o_cabecalho_da_076(client, seletor_ligado):
    """`FR-1915`, D-002: a recusa responde por toda a gestão e não tem de onde tirar uma trilha."""
    identificar(client, "carlos", ["gestor"])
    resposta = client.get(reverse("interface:inscricoes", args=[uuid.uuid4()]))

    assert resposta.status_code == 404
    corpo = resposta.content.decode()
    assert 'aria-label="Trilha de navegação"' not in corpo
    assert '<p class="caminho-da-secao">' in cabecalho(corpo)
