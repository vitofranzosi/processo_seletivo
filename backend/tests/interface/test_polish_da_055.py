"""055 — o acabamento da folha e dos componentes.

As medidas de tela — 40 px, desnível zero, 45 px de linha — estão em
`specs/055-polish-folha-e-componentes/verificacao.md`, tiradas na página renderizada. O que fica
aqui é o que as produz: a regra na folha e a marcação no template. Uma regra que volte ao que era
desfaz a medida sem que nenhum outro teste perceba, porque nenhum comportamento muda — só o desenho.
"""

import re
from pathlib import Path

import pytest
from django.urls import reverse

from tests.interface.test_acessibilidade import FONTE, sem_prosa
from tests.interface.test_corte import _emitir_pela_tela, cliente_no_corte  # noqa: F401

RAIZ = Path(__file__).resolve().parents[2] / "processo_seletivo"
GESTAO = RAIZ / "interface/templates/interface"
PORTAL = RAIZ / "portal/templates/portal"
FOLHA = sem_prosa(FONTE)
FOLHA_DO_PORTAL = sem_prosa((PORTAL / "base.html").read_text())


def regra(seletor, folha=FOLHA):
    """O corpo da regra cujo seletor é exatamente `seletor`, ou `None`."""
    achado = re.search(rf"(?:^|[}}\n])[ \t]*{re.escape(seletor)}\{{([^}}]*)\}}", folha)
    return achado.group(1).replace("\n", "").replace(" ", "") if achado else None


# --- G1 — números com o seu rótulo (FR-1000 a FR-1003) ----------------------------------------


@pytest.mark.parametrize(
    "template", ["corte.html", "corte_historico.html", "ocupacao.html", "ocupacao_historico.html"]
)
def test_os_numeros_vao_para_o_bloco_da_convocacao(template):
    corpo = (GESTAO / template).read_text()

    assert '<dl class="resumo">' not in corpo, "a fileira em que o número fica entre dois rótulos"
    assert '<ul class="resumo"' in corpo
    assert 'class="resumo">' not in re.sub(r"<ul class=\"resumo\"[^>]*>", "", corpo), (
        "`.resumo` só no bloco de números — na `section`, fazia título e números virarem fileira"
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_faixa_calculada_poe_cada_numero_no_bloco_do_seu_rotulo(cliente_no_corte):  # noqa: F811
    client, edital, marco = cliente_no_corte

    corpo = client.get(reverse("interface:corte", args=[edital.id, marco])).content.decode()

    bloco = re.search(
        r'<ul class="resumo" aria-label="A faixa calculada[^"]*">(.*?)</ul>', corpo, re.S
    )
    assert bloco, "a faixa calculada em blocos"
    rotulos = re.findall(r"<li><strong>.*?</strong>([^<]+)", bloco.group(1), re.S)
    assert [r.strip() for r in rotulos] == [
        "Alvo declarado",
        "Alvo apurado",
        "Suplentes",
        "Progridem",
        "Ficam fora",
        "Última posição alcançada",
    ]


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_historico_do_corte_separa_numeros_de_proveniencia(cliente_no_corte):  # noqa: F811
    """D-020: a regra em blocos, como a faixa; a proveniência em rótulo e valor — são nomes, datas e
    identificadores, que no corpo de 1,25 rem de um bloco atravessariam a tela."""
    from processo_seletivo.classificacao.models import Corte

    client, edital, marco = cliente_no_corte
    _emitir_pela_tela(client, edital, marco)
    corte = Corte.objects.get(edital=edital, marco_id=marco)

    corpo = client.get(
        reverse("interface:corte-historico", args=[edital.id, corte.id])
    ).content.decode()

    assert '<dl class="participantes">' in corpo
    assert "</strong>Suplentes</li>" in corpo
    assert "</strong>Faixa seguinte</li>" in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_a_ocupacao_apurada_mostra_os_quatro_blocos(client, seletor_ligado, cenario, gestor):
    from tests.fixtures.corte import MARCO
    from tests.integration.ocupacao.test_emissao import apurar
    from tests.interface.conftest import identificar

    edital, _, _ = cenario
    apurar(edital, gestor)
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(reverse("interface:ocupacao", args=[edital.id, MARCO])).content.decode()

    for rotulo in ("Publicadas", "Efetivas", "Ocupadas", "A ocupar"):
        assert re.search(rf"<li><strong>\d+</strong>{rotulo}</li>", corpo), rotulo
    assert not re.search(r"<section[^>]*class=\"resumo\"", corpo)


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_sem_apuracao_so_a_publicada_vai_ao_bloco(client, seletor_ligado, cenario):
    """FR-1001: o bloco é o mesmo, e as três quantidades de apuração continuam sem desenho."""
    from tests.fixtures.corte import MARCO
    from tests.interface.conftest import identificar

    edital, _, _ = cenario
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(reverse("interface:ocupacao", args=[edital.id, MARCO])).content.decode()

    assert re.search(r"<li><strong>\d+</strong>Publicadas</li>", corpo)
    assert "Ocupadas" not in corpo


# --- G2 e G3 — tabelas (FR-1004, FR-1005) --------------------------------------------------------


def test_a_celula_tem_o_preenchimento_do_portal():
    assert "padding:.5rem.75rem" in regra("th,td")
    # As duas que declaravam o mesmo valor saíram: igual à global, eram só caracteres a mais numa
    # folha que viaja para a tela que está no teto.
    assert "padding" not in regra(".conferencia-lote th,.conferencia-lote td")
    assert "padding" not in regra(".distribuicao th,.distribuicao td")


def test_a_pontuacao_da_ordem_fica_a_direita():
    assert "text-align:right" in regra(".tabela td.numero,.tabela th.numero")
    corpo = (GESTAO / "ordenacao.html").read_text()
    tabela = corpo[corpo.rindex("<table", 0, corpo.index("Pontuação combinada")) :]

    assert tabela.startswith('<table class="tabela">')
    assert '<th scope="col" class="numero">Pontuação combinada</th>' in tabela
    assert '<td class="numero">{% if item.pontuacao is None %}' in tabela


# --- G4 e G5 — botões (FR-1006 a FR-1009) --------------------------------------------------------


def test_principal_e_secundario_tem_a_mesma_caixa():
    geometria = regra(".botao,:is(.navegacao-etapa,.salvar,.filtros) .acao")
    assert geometria, "a ação que divide a barra com o botão tem a caixa dele"
    assert "line-height:1.375rem" in geometria, "sem ela, link e botão da mesma classe divergem"
    assert "padding:.5rem1.1rem" in geometria

    assert "border:1pxsolidtransparent" in regra(".botao")
    secundario = regra(".botao.secundario")
    assert "border-color:var(--verde)" in secundario
    assert "border:" not in secundario, "uma borda de largura própria faria outra altura"
    assert "border:none" not in regra(".botao.perigoso")


def test_fora_da_barra_a_acao_de_linha_continua_pequena():
    assert "padding:.25rem.7rem" in regra(".acao")
    assert "font-size:.8125rem" in regra(".acao")


@pytest.mark.parametrize(
    ("template", "rotulo"),
    [
        ("inscricoes.html", "Filtrar"),
        ("distribuicao.html", "Filtrar"),
        ("comissao.html", "Filtrar"),
        ("matriculas.html", "Ver o que sairá vazio"),
    ],
)
def test_a_acao_principal_nao_tem_o_desenho_de_acao_de_linha(template, rotulo):
    corpo = (GESTAO / template).read_text()

    assert f'<button type="submit" class="botao">{rotulo}</button>' in corpo


# --- G6 — títulos (FR-1010, FR-1011) -------------------------------------------------------------


def test_a_escala_dos_tres_niveis():
    assert "font-size:1.6rem" in regra("h1")
    assert "font-size:1.15rem" in regra("h2")
    assert regra("h3") == "font-size:1rem"
    assert regra("h1,h2,h3") == "font-weight:600"


def test_nenhum_conteiner_poe_h2_no_tamanho_de_h3():
    """`.barra-do-painel h2` fica: é rótulo de barra de ferramentas, e não título de seção.

    A escolha e o porquê estão na D-008 do research da `055`.
    """
    encolhem = [
        seletor.strip()
        for seletor, corpo in re.findall(r"([^{}\n]*\bh2)\{([^}]*)\}", FOLHA)
        if "font-size:1rem" in corpo.replace(" ", "")
    ]

    assert encolhem == [".barra-do-painel h2"]


def test_o_titulo_da_secao_da_retificacao_nao_grita():
    assert "uppercase" not in regra(".secao-da-retificacao>h2")


# --- G7 e G8 — controles e barra de filtro (FR-1012 a FR-1014) -----------------------------------


def test_uma_altura_por_folha_para_os_controles_de_uma_linha():
    assert regra("select,input:not([type$=box],[type=radio],[type=file])") == "height:2.5rem"
    assert (
        regra(
            ".campo :is(input,select):not([type=checkbox],[type=radio],[type=file])",
            FOLHA_DO_PORTAL,
        )
        == "height:2.625rem"
    ), "a mesma altura que a consulta da Vitrine declara"


def test_a_barra_de_filtro_alinha_pelo_topo_e_o_botao_desce_a_altura_do_rotulo():
    """Os três números andam juntos: se o rótulo mudar de tamanho, o botão desalinha."""
    assert "align-items:flex-start" in regra(".filtro,.filtros")
    margem = re.search(
        r"margin:([\d.]+)rem00", regra(".filtro .salvar,.filtros .acoes,.filtro .escolha")
    )
    rotulo = regra(".campo label")
    fonte = float(re.search(r"font-size:([\d.]+)rem", rotulo).group(1))
    abaixo = float(re.search(r"margin-bottom:([\d.]+)rem", rotulo).group(1))
    entrelinha = float(re.search(r"line-height:([\d.]+)", regra("body")).group(1))

    assert float(margem.group(1)) == pytest.approx(fonte * entrelinha + abaixo)
    assert regra(".filtro .escolha") == "height:2.5rem"


@pytest.mark.parametrize(
    ("template", "campo"),
    [("inscricoes.html", "ajuda-busca-inscricoes"), ("distribuicao.html", "ajuda-avaliador")],
)
def test_a_ajuda_do_filtro_continua_ligada_ao_campo(template, campo):
    corpo = (GESTAO / template).read_text()

    assert f'aria-describedby="{campo}"' in corpo
    assert f'<span class="ajuda" id="{campo}">' in corpo


# --- D1 e F7 — espaço pelo conteúdo (FR-1015, FR-1016) -------------------------------------------


def test_a_selecao_sem_sorteio_nao_reserva_a_area_dele():
    larga = FOLHA_DO_PORTAL[FOLHA_DO_PORTAL.index("@media (min-width:60rem){") :]

    sem = regra(".corpo-da-selecao", larga)
    com = regra(".corpo-da-selecao:has(>.sorteio-da-selecao)", larga)

    assert '"vagascronograma""documentoscronograma"' in sem
    assert "sorteio" not in sem
    assert '"vagassorteio""vagascronograma""documentoscronograma"' in com


def test_o_campo_curto_do_requerimento_nao_estica_a_linha():
    grade = regra(".grade-de-campos", FOLHA_DO_PORTAL)

    assert "auto-fill" in grade, "`auto-fit` recolhe a coluna vazia e estica o campo sozinho"
    assert regra(".grade-de-campos .largo>:is(input,select)", FOLHA_DO_PORTAL) == "max-width:40rem"


def test_os_campos_da_comissao_tem_largura_pelo_conteudo():
    corpo = (GESTAO / "comissao.html").read_text()

    assert '<input id="identity_subject" name="identity_subject" type="text"' in corpo
    assert '<input id="display_label" name="display_label" type="text"' in corpo
    assert "{% block estilo_da_pagina %}#identity_subject{max-width:20rem}{% endblock %}" in corpo


def test_o_campo_de_arquivo_nao_herda_a_largura_da_linha():
    arquivo = regra('input[type="file"].arquivo')
    assert "width:auto" in arquivo
    # A última declaração não pode terminar em porcentagem: `100%` seguido da chave de fechamento
    # forma, no corpo servido, a dupla que a varredura de sintaxe não interpretada procura.
    assert not arquivo.endswith("%")
