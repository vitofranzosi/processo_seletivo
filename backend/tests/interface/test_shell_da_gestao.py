"""O shell da gestão (076): a barra lateral e o cabeçalho de contexto em volta de toda tela.

O que importa provar é a promessa da barra — **nenhum item que a autorização recuse, nenhum que ela
abra e falte** —, comparada com a resposta real de cada destino, papel a papel. O desenho em si é
provado no navegador e pelo inventário visual (quickstart).
"""

import re

import pytest
from django.template.loader import render_to_string
from django.test import RequestFactory
from django.urls import reverse

from processo_seletivo.interface import navegacao
from processo_seletivo.interface.identidade import CHAVE_SESSAO, PAPEIS
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar

DESTINOS = [reverse(secao.rota) for secao in navegacao.SECOES]


def barra(corpo):
    return corpo.split('<div class="barra-lateral">')[1].split('<div class="area-de-trabalho">')[0]


def itens_da_barra(corpo):
    return re.findall(r'<li><a href="([^"]+)"', barra(corpo))


def caminho(corpo):
    return corpo.split('<p class="caminho-da-secao">')[1].split("</p>")[0]


# ---- a moldura -------------------------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.integration
def test_com_identidade_a_tela_tem_barra_e_cabecalho_de_contexto(client, seletor_ligado):
    """`FR-1710`, `FR-1717`, `FR-1718`."""
    identificar(client, "gustavo.gestor", ["gestor"])
    corpo = client.get(reverse("interface:lista")).content.decode()

    assert '<nav aria-label="Seções da gestão">' in corpo
    assert '<header class="cabecalho-de-contexto">' in corpo
    # O pé da barra: o nome, a responsabilidade e a saída, que continua um POST.
    pe = barra(corpo).split('<div class="pessoa-identificada">')[1]
    assert "<strong>gustavo.gestor</strong>" in pe
    assert "Gestor" in pe
    assert f'action="{reverse("interface:sair")}"' in pe
    # Trocar identidade leva à página de acesso, que oferece continuar ou trocar (075).
    contexto = corpo.split('<header class="cabecalho-de-contexto">')[1].split("</header>")[0]
    assert f'<a href="{reverse("interface:identificar")}">Trocar identidade</a>' in contexto


@pytest.mark.django_db
def test_sem_identidade_o_topo_tem_so_a_marca(seletor_ligado):
    """`FR-1711`: a base vista sem identidade não oferece seção a ninguém."""
    pedido = RequestFactory().get(reverse("interface:lista"))
    pedido.session = {}
    corpo = render_to_string("interface/base.html", request=pedido)

    assert '<header class="topo">' in corpo
    assert 'class="barra-lateral"' not in corpo
    assert "Seções da gestão" not in corpo
    assert '<a class="marca" href="/gestao/"' in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_o_salto_continua_o_primeiro_e_pula_a_barra(client, seletor_ligado):
    """`FR-1712`: o link de salto é o primeiro do `body`, e o alvo é o `main` de sempre, depois da
    barra e do caminho."""
    identificar(client, "gustavo.gestor", ["gestor"])
    corpo = client.get(reverse("interface:lista")).content.decode()

    depois_do_body = corpo.split("<body>")[1].lstrip()
    assert depois_do_body.startswith('<a class="pular" href="#conteudo">')
    assert '<main id="conteudo" tabindex="-1">' in corpo
    assert corpo.index('class="barra-lateral"') < corpo.index('<main id="conteudo"')
    assert corpo.index('class="caminho-da-secao"') < corpo.index('<main id="conteudo"')


@pytest.mark.django_db
@pytest.mark.integration
def test_no_celular_a_barra_recolhe_sem_script(client, seletor_ligado):
    """`FR-1719`: o botão abre o painel pelo comportamento nativo, e a moldura não traz script."""
    identificar(client, "gustavo.gestor", ["gestor"])
    corpo = client.get(reverse("interface:lista")).content.decode()
    moldura = barra(corpo)

    assert 'popovertarget="secoes-da-gestao">Seções</button>' in moldura
    assert '<div class="secoes-da-gestao" id="secoes-da-gestao" popover>' in moldura
    assert 'popovertargetaction="hide">Fechar</button>' in moldura
    assert "<script" not in moldura
    assert "<script" not in corpo.split('<main id="conteudo"')[0]


# ---- a barra nunca oferece o que a autorização recusa ----------------------------------------


IDENTIDADES = [pytest.param([], id="so-vinculo")] + [
    pytest.param([papel], id=papel) for papel in PAPEIS
]


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize("papeis", IDENTIDADES)
def test_os_itens_sao_exatamente_os_destinos_que_abrem(client, seletor_ligado, papeis):
    """`FR-1714`, `FR-1721`, `SC-661`: para cada papel — e para quem só tem vínculo —, o item está
    na barra se, e só se, o destino responde 200 àquela identidade."""
    identificar(client, "pessoa.qualquer", papeis)
    corpo = client.get(reverse("interface:lista")).content.decode()

    abrem = [destino for destino in DESTINOS if client.get(destino).status_code == 200]

    assert itens_da_barra(corpo) == abrem


@pytest.mark.django_db
@pytest.mark.integration
def test_grupo_sem_item_nao_aparece(client, seletor_ligado):
    """`FR-1714`: o Elaborador não alcança nenhuma seção da unidade, e o título do grupo some."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = client.get(reverse("interface:lista")).content.decode()

    assert ">Trabalho</p>" in barra(corpo)
    assert ">Unidade</p>" not in barra(corpo)
    assert "Visão Geral" not in barra(corpo)


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize("papel", sorted(PAPEIS))
def test_a_lista_e_a_barra_oferecem_as_mesmas_secoes(client, seletor_ligado, papel):
    """`R-002`: os botões da lista e os itens da barra leem o mesmo predicado."""
    identificar(client, "pessoa.qualquer", [papel])
    corpo = client.get(reverse("interface:lista")).content.decode()
    conteudo = corpo.split('<main id="conteudo"')[1]

    for rota in ("interface:visao-geral", "interface:autoridades", "interface:modelos-de-aviso"):
        destino = reverse(rota)
        assert (f'href="{destino}"' in conteudo) == (destino in itens_da_barra(corpo)), rota


@pytest.mark.django_db
def test_montar_a_barra_nao_consulta_o_banco(settings, django_assert_num_queries):
    """`FR-1715`: as capacidades vêm da sessão."""
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    pedido = RequestFactory().get("/gestao/editais/x/")
    pedido.session = {
        CHAVE_SESSAO: {
            "subject": "g",
            "escopo": "cefor",
            "papeis": ["gestor"],
            "origem": "demonstracao",
        }
    }
    with django_assert_num_queries(0):
        contexto = navegacao.contexto_da_navegacao(pedido)
        grupos = [grupo["nome"] for grupo in contexto["navegacao"]["barra"]]

    assert grupos == ["Trabalho", "Unidade"]


def test_a_barra_so_se_monta_quando_lida(monkeypatch):
    """Os fragmentos que o htmx troca não têm barra: o processador não pode montá-la para eles."""

    def nao_devia_ler(request):
        raise AssertionError("a barra foi montada sem que ninguém a lesse")

    monkeypatch.setattr(navegacao.identidade, "ator_da_sessao", nao_devia_ler)
    pedido = RequestFactory().get("/gestao/editais/x/fragmentos/etapa")

    contexto = navegacao.contexto_da_navegacao(pedido)

    assert list(contexto) == ["navegacao"]


def test_o_portal_nao_recebe_barra(settings):
    """O processador roda em toda página; fora da gestão ele não lê nada."""
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    pedido = RequestFactory().get("/selecoes/")
    pedido.session = {
        CHAVE_SESSAO: {
            "subject": "g",
            "escopo": "cefor",
            "papeis": ["gestor"],
            "origem": "demonstracao",
        }
    }

    assert navegacao.contexto_da_navegacao(pedido) == {}


# ---- saber onde se está ----------------------------------------------------------------------


@pytest.mark.parametrize(
    ("caminho_pedido", "secao"),
    [
        ("/gestao/", "Processos Seletivos"),
        ("/gestao/editais/2c4491c3-68f1-4d17-aa05-5c1cf6a1567b/", "Processos Seletivos"),
        ("/gestao/processos/6bb9dc91-75bd-48c1-9994-344cabc538d0/comissao", "Processos Seletivos"),
        ("/gestao/minhas-etapas", "Minhas Etapas"),
        ("/gestao/minhas-etapas/a/b/inscricoes/c", "Minhas Etapas"),
        ("/gestao/visao-geral", "Visão Geral"),
        ("/gestao/autoridades", "Autoridades da unidade"),
        ("/gestao/modelos-de-aviso/novo", "Modelos de aviso"),
    ],
)
def test_a_secao_sai_do_endereco(caminho_pedido, secao):
    """`FR-1716`: cada tela pertence a uma seção só — a de prefixo mais longo."""
    assert navegacao.secao_do_caminho(caminho_pedido).rotulo == secao


@pytest.mark.django_db
@pytest.mark.integration
def test_na_propria_secao_o_item_e_a_pagina_atual(client, seletor_ligado):
    """`FR-1716`, `FR-1718`: na Visão Geral o item é a página atual, e o caminho acaba nela."""
    identificar(client, "gustavo.gestor", ["gestor"])
    corpo = client.get(reverse("interface:visao-geral")).content.decode()

    assert f'<a href="{reverse("interface:visao-geral")}" aria-current="page">Visão Geral</a>' in (
        barra(corpo)
    )
    assert barra(corpo).count("aria-current") == 1
    assert caminho(corpo).endswith("› Visão Geral")


@pytest.mark.django_db
@pytest.mark.integration
def test_abaixo_da_secao_o_caminho_a_nomeia_e_nao_repete_a_trilha(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """`FR-1716`, `FR-1718`: no Edital, a seção é Processos Seletivos; o caminho do topo para nela,
    em texto — o link já está na barra —, e a trilha da própria tela continua uma só."""
    edital = publish_original(api_client, manager_headers, process_payload)
    identificar(client, "gustavo.gestor", ["gestor"])
    corpo = client.get(reverse("interface:detalhe", args=[edital.id])).content.decode()

    assert f'<a href="{reverse("interface:lista")}" aria-current="true">' in barra(corpo)
    assert caminho(corpo).endswith("› Processos Seletivos")
    assert "<a " not in caminho(corpo)
    assert f"{edital.number}/{edital.year}" not in caminho(corpo)
    assert corpo.count('aria-label="Trilha de navegação"') == 1


# ---- a tela larga ----------------------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.integration
def test_na_alocacao_a_barra_fica_recolhida(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """`FR-1724`: a matriz da Alocação não cabe ao lado da barra a 1.280 px, e a `057` a quer sem
    rolagem interna (`FR-1062`). Ali a barra fica recolhida; nas outras telas, não."""
    edital = publish_original(api_client, manager_headers, process_payload)
    identificar(client, "gustavo.gestor", ["gestor"])

    alocacao = client.get(reverse("interface:alocacoes", args=[edital.processo_id])).content
    lista = client.get(reverse("interface:lista")).content

    assert '<div class="shell shell-recolhida">' in alocacao.decode()
    assert '<div class="shell">' in lista.decode()


def test_sem_popover_o_painel_toma_a_largura_da_barra():
    """Navegador sem `popover` não esconde o painel: no celular e na Alocação, a barra do topo
    quebra a linha e o painel ocupa a largura toda, em vez de se espremer ao lado da marca."""
    from pathlib import Path

    folha = (Path(navegacao.__file__).parent / "templates/interface/base.html").read_text()
    bloco = folha.split("@supports not selector(:popover-open){")[1].split("\n}")[0]

    assert ".barra-lateral{flex-wrap:wrap}" in bloco
    assert ".secoes-da-gestao{flex-basis:100%;min-width:0}" in bloco
    assert ".shell-recolhida .barra-lateral{flex-wrap:wrap}" in bloco
