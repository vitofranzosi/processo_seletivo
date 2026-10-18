"""As telas de uso diário, primeiro incremento (077).

A lista oferece só a ação dela; nas quatro telas de uso diário a trilha mora no cabeçalho de
contexto, e só lá; e as cinco telas que estouravam a 375 px cabem. O desenho em si é provado no
navegador e pelo inventário visual refeito (quickstart): aqui fica o que a marcação garante.
"""

from pathlib import Path

import pytest
from django.urls import reverse

from tests.interface.conftest import identificar
from tests.interface.test_acessibilidade_da_012 import cenario  # noqa: F401 — fixture
from tests.interface.test_shell_da_gestao import barra, itens_da_barra

TEMPLATES = (
    Path(__file__).resolve().parents[2] / "processo_seletivo" / "interface" / "templates"
) / "interface"

SECOES_DA_BARRA = ("interface:visao-geral", "interface:autoridades", "interface:modelos-de-aviso")


def cabecalho(corpo):
    return corpo.split('<header class="cabecalho-de-contexto">')[1].split("</header>")[0]


def conteudo(corpo):
    return corpo.split('<main id="conteudo"')[1].split("</main>")[0]


def trilha_unica_no_cabecalho(corpo):
    """A trilha da página, desde que seja uma só e more no cabeçalho (`FR-1746`, `FR-1747`)."""
    assert corpo.count('aria-label="Trilha de navegação"') == 1
    assert 'aria-label="Trilha de navegação"' not in conteudo(corpo)
    abertura = '<nav aria-label="Trilha de navegação" class="caminho-da-secao">'
    trilha = cabecalho(corpo).split(abertura)[1].split("</nav>")[0]
    assert trilha.lstrip().startswith('<abbr title="Gestão de Processos Seletivos">GPS</abbr> ›')
    # A própria tela fecha a trilha, como página atual.
    assert trilha.rstrip().endswith("</span>")
    assert trilha.count('aria-current="page"') == 1
    return trilha


# ---- a lista oferece o que é dela ------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.integration
def test_a_faixa_da_lista_tem_so_novo_processo(client, seletor_ligado):
    """`FR-1740`, `FR-1741`, `SC-670`: uma ação, e as três seções só na barra."""
    identificar(client, "gustavo.gestor", ["gestor"])
    corpo = client.get(reverse("interface:lista")).content.decode()

    faixa = conteudo(corpo).split('<p class="acoes-do-painel">')[1].split("</p>")[0]
    assert faixa.count("<a ") == 1
    assert ">Novo Processo Seletivo</a>" in faixa
    for rota in SECOES_DA_BARRA:
        assert f'href="{reverse(rota)}"' not in conteudo(corpo), rota
        assert reverse(rota) in itens_da_barra(corpo), rota


@pytest.mark.django_db
@pytest.mark.integration
def test_sem_acao_a_lista_nao_tem_faixa(client, seletor_ligado):
    """`FR-1741`: quem não cria Processo não vê a faixa, nem vazia."""
    identificar(client, "inventario.auditora", ["auditor"])
    corpo = client.get(reverse("interface:lista")).content.decode()

    assert "acoes-do-painel" not in conteudo(corpo)
    assert "Novo Processo Seletivo" not in corpo


# ---- onde estou, dito uma vez só -------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize(
    ("rota", "rotulo"),
    [("interface:lista", "Processos Seletivos"), ("interface:minhas-etapas", "Minhas Etapas")],
)
def test_na_raiz_da_secao_a_trilha_tem_um_nivel(client, seletor_ligado, rota, rotulo):
    """`FR-1746`: a lista e Minhas Etapas são a própria seção, como página atual."""
    identificar(client, "gustavo.gestor", ["gestor"])
    corpo = client.get(reverse(rota)).content.decode()

    trilha = trilha_unica_no_cabecalho(corpo)
    assert f'<span aria-current="page">{rotulo}</span>' in trilha
    assert "<a " not in trilha


@pytest.mark.django_db
@pytest.mark.integration
def test_na_etapa_a_trilha_sobe_ao_cabecalho(client, seletor_ligado, cenario):  # noqa: F811
    """`FR-1746`, `FR-1747`, `SC-673`: GPS › Minhas Etapas › a Etapa."""
    identificar(client, "joao", [])
    corpo = client.get(
        reverse("interface:minha-etapa", args=[cenario["edital"].id, cenario["etapa"]])
    ).content.decode()

    trilha = trilha_unica_no_cabecalho(corpo)
    assert f'<a href="{reverse("interface:minhas-etapas")}">Minhas Etapas</a> ›' in trilha
    # O conteúdo começa pelo título: a trilha que o abria subiu.
    assert conteudo(corpo).split(">", 1)[1].lstrip().startswith("<h1>")
    # Por quem está alocado, a seção continua a do endereço (`FR-1752`).
    assert f'<a href="{reverse("interface:minhas-etapas")}" aria-current="true">' in barra(corpo)


@pytest.mark.django_db
@pytest.mark.integration
def test_pela_gestao_a_trilha_continua_pela_alocacao(client, seletor_ligado, cenario):  # noqa: F811
    """`FR-1747`, `FR-1752`: a porta da gestão continua dizendo por onde se chegou — a trilha da
    Alocação, a partir da seção —, e a barra marca a mesma seção que a trilha nomeia."""
    identificar(client, "carlos", ["gestor"])
    processo = cenario["processo"]
    corpo = client.get(
        reverse("interface:minha-etapa", args=[cenario["edital"].id, cenario["etapa"]])
    ).content.decode()

    trilha = trilha_unica_no_cabecalho(corpo)
    niveis = [
        f'<a href="{reverse("interface:lista")}">Processos Seletivos</a> ›',
        f'<a href="{reverse("interface:processo-detalhe", args=[processo.id])}">'
        f"{processo.institutional_code}</a> ›",
        f'<a href="{reverse("interface:alocacoes", args=[processo.id])}">Alocação por Etapa</a> ›',
    ]
    posicoes = [trilha.index(nivel) for nivel in niveis]
    assert posicoes == sorted(posicoes)
    assert "Minhas Etapas" not in trilha
    assert f'<a href="{reverse("interface:lista")}" aria-current="true">' in barra(corpo)
    assert barra(corpo).count("aria-current") == 1


@pytest.mark.django_db
@pytest.mark.integration
def test_na_inscricao_da_mesa_a_trilha_sobe_ao_cabecalho(client, seletor_ligado, cenario):  # noqa: F811
    """`FR-1746`, `FR-1747`, `SC-673`: cada nível acima da tela a um clique, do cabeçalho."""
    identificar(client, "joao", [])
    edital, etapa, inscricao = cenario["edital"], cenario["etapa"], cenario["inscricao"]
    corpo = client.get(
        reverse("interface:mesa-inscricao", args=[edital.id, etapa, inscricao.id])
    ).content.decode()

    trilha = trilha_unica_no_cabecalho(corpo)
    assert f'<a href="{reverse("interface:minhas-etapas")}">Minhas Etapas</a> ›' in trilha
    mesa = reverse("interface:minha-etapa", args=[edital.id, etapa])
    assert f'<a href="{mesa}">Minha Mesa</a> ›' in trilha
    assert f'<span aria-current="page">Inscrição {inscricao.protocolo}</span>' in trilha


@pytest.mark.django_db
@pytest.mark.integration
def test_fora_das_telas_de_uso_diario_o_cabecalho_e_o_da_076(client, seletor_ligado, cenario):  # noqa: F811
    """`FR-1748`: a Supervisão do Processo continua com a trilha no conteúdo, e o cabeçalho para na
    seção. Era a trilha da avaliação até a 080 (`FR-1800` da 080), e a auditoria do Edital até a
    083 (`FR-1850` da 083), que as levaram ao cabeçalho."""
    identificar(client, "carlos", ["gestor", "auditor"])
    corpo = client.get(
        reverse("interface:supervisao", args=[cenario["processo"].id])
    ).content.decode()

    assert '<p class="caminho-da-secao">' in cabecalho(corpo)
    assert 'aria-label="Trilha de navegação"' not in cabecalho(corpo)
    assert 'aria-label="Trilha de navegação"' in conteudo(corpo)


# ---- nenhuma tela rola para o lado -----------------------------------------------------------

# As conclusões preservadas, reaproveitar e os anexos da composição estouravam por causas que não
# eram delas — a moldura sem posição e o `fieldset` que não encolhe —, e a 078 as levou à folha
# comum (`FR-1760` a `FR-1762` da 078, provados em `test_telas_de_quem_elabora.py`). Fica aqui a do
# sorteio, que é da tela.
CORRECOES = {
    "sorteio.html": ".imutavel code{overflow-wrap:anywhere}",
}


@pytest.mark.parametrize(("template", "regra"), CORRECOES.items())
def test_cada_correcao_vale_so_na_sua_tela(template, regra):
    """`FR-1743`, `FR-1745`: a regra está na folha da tela, e não na comum, que toda tela recebe.

    A largura medida é a do inventário refeito; aqui fica a garantia de que a correção não vazou.
    """
    folha_da_tela = (TEMPLATES / template).read_text().split("{% block estilo_da_pagina %}")[1]
    assert regra in folha_da_tela.split("{% endblock %}")[0]
    assert regra not in (TEMPLATES / "base.html").read_text()


def test_a_tabela_da_retificacao_rola_na_propria_moldura():
    """`FR-1743`, `FR-1744`: a tabela das alterações, inteira, dentro da moldura que rola."""
    secao = (TEMPLATES / "retificacao_detalhe.html").read_text().split('id="alteracoes-titulo"')[1]
    moldura = secao.split('<div class="tabela-rolavel">')[1].split("</div>")[0]
    assert "<table>" in moldura and "</table>" in moldura
