"""As telas de resultado e dos atos depois da inscrição (084).

Nas onze telas que pendem do Edital — da Classificação à exportação para matrícula — a trilha mora
no cabeçalho de contexto, e só lá: é a do Edital, com os níveis que cada tela já tinha depois dele e
a tela no fim. Nada mais muda, e é por isso que metade deste arquivo prova o que ficou: são as telas
dos atos que não se desfazem, e nenhum botão delas muda de rótulo, de desenho ou de lugar. O desenho
em si é provado no navegador e pelo inventário visual refeito (quickstart).
"""

import re
from collections import Counter
from pathlib import Path

import pytest
from django.urls import reverse

from tests.fixtures.corte import MARCO
from tests.fixtures.recortes import MODALIDADE_PPI, montar_cenario_7_1_2
from tests.interface.conftest import identificar
from tests.interface.test_corte import _emitir_pela_tela, cliente_no_corte  # noqa: F401
from tests.interface.test_telas_da_presidencia import (
    ate_o_processo,
    comeca_pelo_titulo,
    niveis_em_ordem,
)
from tests.interface.test_telas_de_uso_diario import (
    conteudo,
    trilha_unica_no_cabecalho,
)

GESTAO = Path(__file__).resolve().parents[2] / "processo_seletivo/interface/templates/interface"
TELAS = (
    "ordenacao.html",
    "ordenacao_confirmar.html",
    "ato_ordenacao.html",
    "sorteio.html",
    "corte.html",
    "corte_historico.html",
    "ocupacao.html",
    "ocupacao_historico.html",
    "convocacao.html",
    "convocacao_historico.html",
    "matriculas.html",
)


def ate_o_edital(edital):
    return [
        *ate_o_processo(edital.processo),
        f'<a href="{reverse("interface:detalhe", args=[edital.id])}">'
        f"Edital {edital.number}/{edital.year}</a> ›",
    ]


def confere(corpo, edital, *niveis, atual):
    """A trilha do Edital, os níveis da tela em ordem, a tela no fim e o conteúdo pelo título."""
    trilha = trilha_unica_no_cabecalho(corpo)
    niveis_em_ordem(trilha, [*ate_o_edital(edital), *niveis])
    assert trilha.rstrip().endswith(f'<span aria-current="page">{atual}</span>'), trilha
    assert comeca_pelo_titulo(corpo)
    # A seção é a do endereço: a barra e a trilha dizem a mesma coisa.
    assert f'<a href="{reverse("interface:lista")}" aria-current="true">' in corpo
    return trilha


# ---- a marcação, nas onze ----------------------------------------------------------------------


@pytest.mark.parametrize("tela", TELAS)
def test_a_trilha_mora_no_bloco_do_cabecalho(tela):
    """`FR-1880`, `FR-1881`, `FR-1882`: o bloco da `077`, o produto pelo parcial da `078`, a trilha
    do Edital no começo — e nenhuma trilha no conteúdo, que começa pelo título.

    É a única prova da conferência da emissão que não pede um envio, e a única do corte histórico e
    da exportação que não monta o certame inteiro: as demais estão abaixo, pela página renderizada.
    """
    fonte = (GESTAO / tela).read_text()
    bloco = re.search(r"\{% block caminho_do_contexto %\}(.*?)\{% endblock %\}", fonte).group(1)

    assert bloco.startswith(
        '<nav aria-label="Trilha de navegação" class="caminho-da-secao">'
        '{% include "interface/_produto_na_trilha.html" %} '
        "<a href=\"{% url 'interface:lista' %}\">Processos Seletivos</a> › "
        "<a href=\"{% url 'interface:processo-detalhe' processo.id %}\">"
        "{{ processo.institutional_code }}</a> › "
        "<a href=\"{% url 'interface:detalhe' edital.id %}\">"
        "Edital {{ edital.number }}/{{ edital.year }}</a> › "
    )
    assert bloco.count('aria-current="page"') == 1
    corpo = fonte.split("{% block conteudo %}", 1)[1]
    assert "Trilha de navegação" not in corpo
    assert 'class="trilha"' not in corpo
    assert corpo.lstrip().startswith("<h1>")


# O que cada tela oferecia antes da 084, botão a botão — rótulo e desenho. Os atos que não se
# desfazem estão aqui com o peso que já tinham (D-004): uma mudança de desenho em qualquer um deles
# é decisão de governança, e tem de passar por este arquivo, à vista.
BOTOES = {
    "ordenacao.html": [("botao", "Emitir ordem")],
    "ordenacao_confirmar.html": [("botao perigoso", "Emitir a ordem")],
    "ato_ordenacao.html": [],
    "sorteio.html": [
        ("botao", "Observar a ocorrência {{ proxima_referencia }} na fonte"),
        ("botao perigoso", "Anular e constituir o sucessor"),
        ("botao", "Realizar o sorteio"),
        ("acao", "Publicar relação nova, sucedendo a atual"),
        ("botao", "Publicar e congelar a relação"),
    ],
    "corte.html": [("botao", "Emitir corte"), ("botao", "Emitir faixa seguinte")],
    "corte_historico.html": [],
    "ocupacao.html": [
        ("botao", "Apurar a ocupação deste recorte"),
        ("botao", "Emitir nova apuração"),
        ("botao", "Pedir a faixa seguinte com este déficit"),
    ],
    "ocupacao_historico.html": [],
    "convocacao.html": [
        (
            "botao",
            'Convocar {{ titulares.pessoas|length|plural:"a,as" }} {{ titulares.pessoas|length }}',
        ),
        (
            "botao",
            'Registrar o não atendimento {{ vencidos.linhas|length|plural:"da,das" }} '
            "{{ vencidos.linhas|length }}",
        ),
        (
            "botao",
            'Registrar a publicação {{ pendentes.linhas|length|plural:"da,das" }} '
            "{{ pendentes.linhas|length }}",
        ),
        (
            "botao",
            "Emitir {{ pendentes.linhas|length }} "
            '{{ pendentes.linhas|length|plural:"comunicação,comunicações" }}',
        ),
        ("botao", "Convocar"),
        ("botao", "Convocar para regularizar"),
        ("botao", "Registrar desfecho"),
        ("botao", "Registrar atestado"),
        ("acao", "Emitir a comunicação de novo"),
        ("botao", "Emitir a comunicação"),
    ],
    "convocacao_historico.html": [],
    "matriculas.html": [("botao", "Ver o que sairá vazio"), ("botao", "Baixar o arquivo")],
}


@pytest.mark.parametrize("tela", TELAS)
def test_nenhum_botao_muda_de_rotulo_desenho_ou_lugar(tela):
    """`FR-1886`, D-004: os botões de envio, na ordem em que aparecem, com o desenho de antes."""
    fonte = (GESTAO / tela).read_text()
    achados = [
        (classe, " ".join(rotulo.split()))
        for classe, rotulo in re.findall(
            r'<button type="submit" class="([^"]+)">(.*?)</button>', fonte, re.S
        )
    ]

    assert achados == BOTOES[tela]
    assert fonte.count('<button type="submit"') == len(BOTOES[tela])


def test_nenhuma_acao_que_nao_se_desfaz_ganhou_peso():
    """`FR-1886`: a contagem de desenhos das onze, somada — duas de perigo, duas secundárias."""
    desenhos = Counter(classe for botoes in BOTOES.values() for classe, _ in botoes)

    assert desenhos == {"botao": 20, "botao perigoso": 2, "acao": 2}


# ---- pela página renderizada -------------------------------------------------------------------


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload):
    """Edital 7/1/2, com a ordem da ampla emitida e os dois recortes reservados ainda sem a sua."""
    edital, _, _ = montar_cenario_7_1_2(
        gestor, api_client, manager_headers, process_payload, prefixo="telas-084"
    )
    return edital


def _abrir(client, rota, *args, lista=None):
    endereco = reverse(rota, args=args)
    resposta = client.get(f"{endereco}?lista={lista}" if lista else endereco)
    assert resposta.status_code == 200, rota
    return resposta.content.decode()


ATUAIS = {
    "interface:corte": "Corte",
    "interface:ocupacao": "Ocupação de vagas",
    "interface:convocacao": "Convocação",
}


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_nas_telas_do_marco_a_trilha_e_a_do_edital_com_a_tela(client, seletor_ligado, certame):
    """`FR-1880`, `FR-1881`, `FR-1882`, `SC-742`, `SC-743`: GPS › Processos Seletivos › código ›
    Edital › tela, uma vez só, e o conteúdo começa pelo título."""
    identificar(client, "carlos", ["gestor"])

    corpo = _abrir(client, "interface:ordenacao", certame.id, MARCO)
    confere(corpo, certame, atual=re.search(r"<h1>(.*?)</h1>", corpo).group(1))

    for rota, atual in ATUAIS.items():
        confere(_abrir(client, rota, certame.id, MARCO), certame, atual=atual)


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_nos_historicos_a_trilha_passa_pela_tela_de_origem_no_mesmo_recorte(
    client, seletor_ligado, certame
):
    """`FR-1881`: o histórico pende da tela de onde se abre, e a Convocação volta ao recorte."""
    identificar(client, "carlos", ["gestor"])
    ocupacao = reverse("interface:ocupacao", args=[certame.id, MARCO])
    convocacao = reverse("interface:convocacao", args=[certame.id, MARCO])

    corpo = _abrir(client, "interface:ocupacao-historico", certame.id, MARCO, lista=MODALIDADE_PPI)
    confere(corpo, certame, f'<a href="{ocupacao}">Ocupação de vagas</a> ›', atual="Histórico")

    corpo = _abrir(
        client, "interface:convocacao-historico", certame.id, MARCO, lista=MODALIDADE_PPI
    )
    confere(
        corpo,
        certame,
        f'<a href="{convocacao}?lista={MODALIDADE_PPI}">Convocação</a> ›',
        atual="Histórico",
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_na_conferencia_da_emissao_o_marco_volta_ao_recorte(client, seletor_ligado, certame):
    """`FR-1880`, `FR-1881`, `FR-1886`: a trilha termina em marco › Conferir, e o marco leva ao
    recorte que se confere (`FR-497` da 034); "Emitir a ordem" continua com o desenho de perigo."""
    identificar(client, "carlos", ["gestor"])
    corpo = client.post(
        reverse("interface:emitir-ordenacao", args=[certame.id, MARCO]),
        {"chave_idempotencia": "telas-084-conferir", "lista": MODALIDADE_PPI},
    ).content.decode()

    destino = reverse("interface:ordenacao", args=[certame.id, MARCO])
    confere(corpo, certame, f'<a href="{destino}?lista={MODALIDADE_PPI}">', atual="Conferir")
    assert "<h1>Confira antes de emitir</h1>" in corpo
    assert '<button type="submit" class="botao perigoso">Emitir a ordem</button>' in corpo
    assert "Cancelar e voltar" in conteudo(corpo)


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_ato_de_classificacao_ganha_o_edital_na_trilha(client, seletor_ligado, certame):
    """`FR-1881`, `SC-743`: a única das onze que pulava o Edital. O caminho até o ato é lido da
    própria Classificação, como o de quem chega lá."""
    identificar(client, "carlos", ["gestor"])
    ordenacao = reverse("interface:ordenacao", args=[certame.id, MARCO])
    pagina = _abrir(client, "interface:ordenacao", certame.id, MARCO)
    ato = re.search(r'href="([^"]+/atos/[^"]+)">Consultar ato e proveniência', pagina).group(1)

    resposta = client.get(ato)
    assert resposta.status_code == 200
    ato_id = ato.rstrip("/").rsplit("/", 1)[1]
    confere(
        resposta.content.decode(),
        certame,
        f'<a href="{ordenacao}">Classificação</a> ›',
        atual=f"Ato {ato_id}",
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_quem_audita_le_a_mesma_trilha_de_quem_conduz(client, seletor_ligado, certame):
    """`FR-1883`: nenhum nível aparece, some ou deixa de ser link conforme quem lê."""
    trilhas = []
    for nome, papeis in (("carlos", ["gestor"]), ("auditora", ["auditor"])):
        identificar(client, nome, papeis)
        corpo = _abrir(client, "interface:ocupacao", certame.id, MARCO)
        trilhas.append(trilha_unica_no_cabecalho(corpo))

    assert trilhas[0] == trilhas[1]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_no_corte_historico_a_trilha_termina_na_emissao(cliente_no_corte):  # noqa: F811
    """`FR-1880`, `FR-1881`: abaixo do Edital, como antes — o corte histórico pende do Edital, e
    não do marco, e continua legível depois de a Retificação remover o marco."""
    from processo_seletivo.classificacao.models import Corte

    client, edital, marco = cliente_no_corte
    _emitir_pela_tela(client, edital, marco)
    corte = Corte.objects.get(edital=edital, marco_id=marco)

    corpo = _abrir(client, "interface:corte-historico", edital.id, corte.id)
    trilha = confere(corpo, edital, atual=re.search(r"Corte de [\d/]+ [\d:]+", corpo).group(0))
    assert trilha.count("<a href=") == 3, "Processos Seletivos, o Processo e o Edital"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_no_sorteio_a_trilha_e_a_do_edital(
    client, seletor_ligado, gestor, api_client, manager_headers, process_payload
):
    """`FR-1880`, `FR-1881`, `FR-1886`: a tela dos atos de sorteio, com os botões de antes."""
    from tests.fixtures.sorteio import certame_de_sorteio

    sorteio = certame_de_sorteio(gestor, api_client, manager_headers, process_payload)
    identificar(client, "maria", [])
    edital, marco = sorteio["edital"], sorteio["marco"]

    corpo = _abrir(client, "interface:sorteio", edital.id, marco)
    atual = re.search(r"<h1>(.*?)</h1>", corpo).group(1)
    confere(corpo, edital, atual=atual)


@pytest.mark.django_db
@pytest.mark.integration
def test_na_exportacao_a_trilha_e_a_do_edital(
    client, seletor_ligado, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    """`FR-1880`, `FR-1881`, `FR-1883`: a exportação abre para quem só exporta, com a mesma
    trilha."""
    from tests.fixtures.matriculas import montar_cenario_da_exportacao

    edital, _ = montar_cenario_da_exportacao(
        gestor, api_client, manager_headers, process_payload, prefixo="084-trilha", quantos=1
    )
    identificar(client, "exportadora", ["exportador"])

    corpo = _abrir(client, "interface:exportar-matriculas", edital.id)
    confere(corpo, edital, atual="Exportar para matrícula")
