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
    """`FR-1719`: o botão abre o painel pelo comportamento nativo, sem script nenhum no caminho."""
    identificar(client, "gustavo.gestor", ["gestor"])
    corpo = client.get(reverse("interface:lista")).content.decode()
    moldura = barra(corpo)

    assert 'popovertarget="secoes-da-gestao">Seções</button>' in moldura
    assert '<div class="secoes-da-gestao" id="secoes-da-gestao" popover>' in moldura
    assert 'popovertargetaction="hide">Fechar</button>' in moldura
    # O botão do celular não tem ligação de script: quem abre o painel é o atributo.
    assert re.search(r'<button type="button" class="abrir-secoes" popovertarget="[^"]+">', moldura)


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

    destino = reverse("interface:visao-geral")
    assert re.search(
        rf'<a href="{destino}" aria-current="page">.*?'
        r'<span class="rotulo-da-secao">Visão Geral</span>',
        barra(corpo),
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
def test_na_alocacao_a_barra_fica_no_topo(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """`FR-1724`: a matriz da Alocação não cabe ao lado da barra a 1.280 px, e a `057` a quer sem
    rolagem interna (`FR-1062`). Ali a barra fica no topo, sem o script da preferência
    (`FR-1730`); nas outras telas, não."""
    edital = publish_original(api_client, manager_headers, process_payload)
    identificar(client, "gustavo.gestor", ["gestor"])

    alocacao = client.get(reverse("interface:alocacoes", args=[edital.processo_id])).content
    lista = client.get(reverse("interface:lista")).content

    assert '<div class="shell shell-barra-no-topo">' in alocacao.decode()
    assert "shell.js" not in alocacao.decode()
    assert '<div class="shell">' in lista.decode()
    assert "shell.js" in lista.decode()


def test_sem_popover_o_painel_toma_a_largura_da_barra():
    """Navegador sem `popover` não esconde o painel: no celular e na Alocação, a barra do topo
    quebra a linha e o painel ocupa a largura toda, em vez de se espremer ao lado da marca."""
    from pathlib import Path

    folha = (Path(navegacao.__file__).parent / "templates/interface/base.html").read_text()
    bloco = folha.split("@supports not selector(:popover-open){")[1].split("\n}")[0]

    assert ".barra-lateral{flex-wrap:wrap}" in bloco
    assert ".secoes-da-gestao{flex-basis:100%;min-width:0}" in bloco
    assert ".shell-barra-no-topo .barra-lateral{flex-wrap:wrap}" in bloco


# ---- a barra retrátil (US5) ------------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.integration
def test_o_controle_nasce_escondido_e_diz_o_que_fara(client, seletor_ligado):
    """`FR-1727`, `FR-1729`: sem script, o controle não aparece e a barra fica expandida — o
    desenho sem `data-barra`. O script, que o liga, vem de arquivo estático, sem `defer`, dentro da
    própria `.shell` (`FR-1728`, `FR-1732`)."""
    identificar(client, "gustavo.gestor", ["gestor"])
    corpo = client.get(reverse("interface:lista")).content.decode()

    controle = re.search(r"<button[^>]*data-alternar-barra[^>]*>(.*?)</button>", corpo, re.S)
    assert controle, "o controle de recolher precisa existir na moldura"
    abertura = controle.group(0).split(">")[0]
    assert " hidden" in abertura
    assert 'aria-expanded="true"' in abertura
    assert 'aria-controls="secoes-da-gestao"' in abertura
    assert "Recolher a barra lateral" in controle.group(1)

    assert '<div class="shell">' in corpo
    assert 'data-barra="' not in corpo
    script = re.search(r'<script src="([^"]+)"([^>]*)></script>', barra_e_script(corpo))
    assert script and script.group(1).endswith("interface/shell.js")
    assert "defer" not in script.group(2)


def barra_e_script(corpo):
    return corpo.split('<div class="shell')[1].split('<div class="area-de-trabalho">')[0]


@pytest.mark.django_db
@pytest.mark.integration
def test_cada_item_tem_icone_decorativo_e_nome_acessivel(client, seletor_ligado):
    """`FR-1726`, `FR-1731`: o ícone é decorativo, o nome é o texto do item — que vira a dica
    quando a barra recolhe —, e cada seção tem o seu ícone."""
    identificar(client, "gustavo.gestor", ["gestor"])
    moldura = barra(client.get(reverse("interface:lista")).content.decode())

    itens = re.findall(
        r'<li><a href="[^"]+"[^>]*><svg class="icone-da-secao" aria-hidden="true">'
        r'<use href="#([\w-]+)"/></svg><span class="rotulo-da-secao">([^<]+)</span></a></li>',
        moldura,
    )
    assert [rotulo for _, rotulo in itens] == [secao.rotulo for secao in navegacao.SECOES]
    icones = [icone for icone, _ in itens]
    assert len(set(icones)) == len(icones), "dois itens com o mesmo ícone"
    for icone in icones + ["i-sair", "i-painel"]:
        assert f'<symbol id="{icone}"' in moldura or f'<symbol id="{icone}"' in barra_e_script(
            client.get(reverse("interface:lista")).content.decode()
        ), icone
    # O "Sair" também é ícone com nome por extenso.
    assert '<span class="rotulo-da-secao">Sair</span></button>' in moldura


@pytest.mark.parametrize(
    ("nome", "esperado"),
    [("gustavo.gestor", "GG"), ("ana", "A"), ("demo.auditor-x", "DA"), ("", "")],
)
def test_as_iniciais_do_avatar(nome, esperado):
    """`FR-1725`: o avatar da barra recolhida."""
    assert navegacao.iniciais(nome) == esperado


@pytest.mark.django_db
@pytest.mark.integration
def test_a_pessoa_aparece_como_avatar_e_nome(client, seletor_ligado):
    """`FR-1725`: o avatar fica nos dois estados; o nome e as responsabilidades, só na expandida."""
    identificar(client, "gustavo.gestor", ["gestor", "auditor"])
    pe = barra(client.get(reverse("interface:lista")).content.decode()).split(
        '<div class="pessoa-identificada">'
    )[1]

    assert '<span class="iniciais" aria-hidden="true" title="gustavo.gestor">GG</span>' in pe
    assert "<strong>gustavo.gestor</strong><span>Gestor, Auditor</span>" in pe


def test_a_folha_recolhe_so_na_tela_larga_e_sem_movimento_forcado():
    """`FR-1727`, `FR-1730`: os dois estados são da tela larga, a transição só existe a partir de um
    gesto e some sob movimento reduzido."""
    from pathlib import Path

    folha = (Path(navegacao.__file__).parent / "templates/interface/base.html").read_text()
    larga = folha.split("@media (min-width:64rem){\n  .shell{")[1].split("\n}")[0]

    assert ".shell[data-barra=recolhida]{grid-template-columns:4.25rem minmax(0,1fr)}" in larga
    assert ".shell[data-animar]{transition:grid-template-columns" in larga
    reduzido = folha.split("@media (prefers-reduced-motion:reduce){")[1].split("\n}")[0]
    assert ".shell[data-animar]{transition:none}" in reduzido
