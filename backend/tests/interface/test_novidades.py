"""A página Novidades do GPS e a contagem da barra (168).

As notas destes casos são de um arquivo próprio, escrito pelo teste: o conteúdo real muda toda
semana, e o que se prova aqui é o comportamento — quem vê o quê, quando conta e quando deixa de
contar.
"""

import re

import pytest
from django.test import RequestFactory
from django.urls import reverse

from processo_seletivo.interface import navegacao
from processo_seletivo.interface.identidade import CHAVE_SESSAO
from processo_seletivo.novidades import catalogo, leitura
from processo_seletivo.novidades.models import LeituraDasNovidades
from tests.interface.conftest import identificar


def _nota(id, data, categoria="novidade", relevancia="relevante", **extra):
    linhas = [
        "[[nota]]",
        f'id = "{id}"',
        f"data = {data}",
        f'categoria = "{categoria}"',
        f'relevancia = "{relevancia}"',
        f'titulo = "Título {id}"',
        f'resumo = "Resumo de {id}."',
        "prs = [1]",
        "specs = []",
    ]
    linhas += [f'{campo} = "{valor}"' for campo, valor in extra.items()]
    return "\n".join(linhas) + "\n"


@pytest.fixture
def notas(tmp_path, monkeypatch):
    """Troca o arquivo das notas pelo do caso. Devolve a função que o escreve."""
    arquivo = tmp_path / "novidades.toml"
    monkeypatch.setattr(catalogo, "ARQUIVO", arquivo)
    catalogo._LIDO.clear()

    def escrever(*blocos):
        arquivo.write_text("\n".join(blocos), encoding="utf-8")
        catalogo._LIDO.clear()

    yield escrever
    catalogo._LIDO.clear()


TRES = (
    _nota("c", "2026-11-12", "correcao"),
    _nota("b", "2026-11-11", "melhoria", destino="interface:visao-geral", documentacao="agenda"),
    _nota("a", "2026-10-30"),
)


def _barra(corpo):
    return corpo.split('<div class="barra-lateral">')[1].split('<div class="area-de-trabalho">')[0]


def _contagem(corpo):
    achado = re.search(
        r'rotulo-da-secao">Novidades</span><span class="contagem-de-novidades">'
        r'<span aria-hidden="true">([^<]+)</span><span class="oculto">([^<]+)</span>',
        _barra(corpo),
    )
    return achado.groups() if achado else None


def _pagina(client, **parametros):
    return client.get(reverse("interface:novidades"), parametros).content.decode()


# ---- a barra ---------------------------------------------------------------------------------


@pytest.mark.django_db
def test_sem_identidade_a_pagina_pede_identificacao(client, seletor_ligado, notas):
    notas(*TRES)
    resposta = client.get(reverse("interface:novidades"))
    assert resposta.status_code == 302
    assert reverse("interface:identificar") in resposta["Location"]


@pytest.mark.django_db
def test_a_barra_conta_o_que_a_identidade_nao_viu_e_esquece_depois_da_visita(
    client, seletor_ligado, notas
):
    """FR-7413, FR-7414, FR-7416 e UX-805: número pequeno, texto acessível, e some depois."""
    notas(*TRES)
    identificar(client, "gustavo.gestor", ["gestor"])
    lista = client.get(reverse("interface:lista")).content.decode()
    assert _contagem(lista) == ("3", ", 3 não vistas")
    rotulos = re.findall(r'rotulo-da-secao">([^<]+)</span>', _barra(lista))
    assert rotulos.index("Novidades") == rotulos.index("Documentação do Sistema") - 1

    _pagina(client)

    assert _contagem(client.get(reverse("interface:lista")).content.decode()) is None
    assert set(LeituraDasNovidades.objects.get(subject="gustavo.gestor").vistas) == {"a", "b", "c"}


@pytest.mark.django_db
def test_a_contagem_tem_teto_de_exibicao(client, seletor_ligado, notas):
    notas(*[_nota(f"n{i:02d}", "2026-11-01") for i in range(12)])
    identificar(client, "gustavo.gestor", ["gestor"])
    assert _contagem(client.get(reverse("interface:lista")).content.decode()) == (
        "9+",
        ", 12 não vistas",
    )


@pytest.mark.django_db
def test_a_barra_conta_sem_consultar_o_banco(settings, notas, django_assert_num_queries):
    """FR-7415: a contagem vem da sessão; a barra continua sem consulta (`FR-1715` da 076)."""
    notas(*TRES)
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    pedido = RequestFactory().get("/gestao/")
    pedido.session = {
        CHAVE_SESSAO: {"subject": "g", "escopo": "cefor", "papeis": ["gestor"], "origem": "x"},
        leitura.NAO_VISTAS: ["a", "c", "nota-que-saiu"],
    }
    with django_assert_num_queries(0):
        barra = navegacao.contexto_da_navegacao(pedido)["navegacao"]["barra"]
    itens = {item["rotulo"]: item for grupo in barra for item in grupo["itens"]}
    assert itens["Novidades"]["contagem"] == 2
    assert itens["Processos Seletivos"]["contagem"] == 0


@pytest.mark.django_db
def test_a_sessao_aberta_antes_da_feature_nao_mostra_numero(client, seletor_ligado, notas):
    """Caso-limite: sem a chave na sessão, a barra não inventa contagem."""
    notas(*TRES)
    identificar(client, "gustavo.gestor", ["gestor"])
    sessao = client.session
    del sessao[leitura.NAO_VISTAS]
    sessao.save()
    assert _contagem(client.get(reverse("interface:lista")).content.decode()) is None


# ---- desde sua última visita -----------------------------------------------------------------


@pytest.mark.django_db
def test_primeira_visita_nao_tem_bloco_e_diz_de_quando_e_o_historico(client, seletor_ligado, notas):
    notas(*TRES)
    identificar(client, "gustavo.gestor", ["gestor"])
    corpo = _pagina(client)
    assert "Desde sua última visita" not in corpo
    assert "Esta é a sua primeira visita: a página reúne as mudanças desde 30 de outubro" in corpo


@pytest.mark.django_db
def test_quem_volta_ve_o_que_chegou_e_o_bloco_dura_a_sessao(client, seletor_ligado, notas):
    """US1, cenários 1 a 5: FR-7417 e `D-002` — o que é novo se decide pelo identificador."""
    from django.utils import timezone

    LeituraDasNovidades.objects.create(
        subject="gustavo.gestor", vistas=["a"], ultima_visita=timezone.now()
    )
    notas(*TRES)
    identificar(client, "gustavo.gestor", ["gestor"])
    assert _contagem(client.get(reverse("interface:lista")).content.decode())[0] == "2"

    corpo = _pagina(client)
    bloco = corpo.split('class="desde-a-ultima-visita"')[1].split("</section>")[0]
    assert re.findall(r'href="[^"]*#(\w+)">Título', bloco) == ["c", "b"]
    assert "Também chegaram 1 melhoria, desde" in bloco
    # Recarregar não esvazia o bloco: a visita é a sessão.
    assert 'class="desde-a-ultima-visita"' in _pagina(client)

    identificar(client, "gustavo.gestor", ["gestor"])
    corpo = _pagina(client)
    assert 'class="desde-a-ultima-visita"' not in corpo
    assert "Nada novo desde a sua última visita" in corpo


@pytest.mark.django_db
def test_trocar_de_unidade_reconta_sem_apagar_o_bloco_da_visita(client, seletor_ligado, notas):
    """FR-7417: a troca de unidade muda as capacidades, e não a sessão — o bloco fica."""
    from django.utils import timezone

    LeituraDasNovidades.objects.create(
        subject="gustavo.gestor", vistas=["a"], ultima_visita=timezone.now()
    )
    notas(*TRES)
    identificar(client, "gustavo.gestor", ["gestor"])
    _pagina(client)
    pedido = RequestFactory().get("/gestao/")
    pedido.session = client.session
    leitura.recontar(pedido, navegacao.identidade.ator_da_sessao(pedido))
    pedido.session.save()
    corpo = _pagina(client)
    assert 'class="desde-a-ultima-visita"' in corpo
    assert "Nada novo" not in corpo


@pytest.mark.django_db
def test_nota_vista_que_volta_a_ser_alcancavel_nao_reaparece_como_nova(
    client, seletor_ligado, notas
):
    from django.utils import timezone

    LeituraDasNovidades.objects.create(
        subject="gustavo.gestor", vistas=["a", "b", "c", "antiga"], ultima_visita=timezone.now()
    )
    notas(*TRES)
    identificar(client, "gustavo.gestor", ["gestor"])
    _pagina(client)
    assert "antiga" in LeituraDasNovidades.objects.get(subject="gustavo.gestor").vistas


# ---- quem vê o quê ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_a_configuracao_desligada_esconde_a_nota(client, seletor_ligado, settings, notas):
    """US3, FR-7410, `D-003`."""
    notas(*TRES, _nota("aviso", "2026-10-01", requer_configuracao="AVISOS_AOS_CANDIDATOS"))
    settings.AVISOS_AOS_CANDIDATOS = False
    identificar(client, "gustavo.gestor", ["gestor"])
    assert _contagem(client.get(reverse("interface:lista")).content.decode())[0] == "3"
    corpo = _pagina(client)
    assert "Título aviso" not in corpo
    assert "aviso" not in LeituraDasNovidades.objects.get(subject="gustavo.gestor").vistas

    settings.AVISOS_AOS_CANDIDATOS = True
    assert "Título aviso" in _pagina(client)


@pytest.mark.django_db
def test_a_nota_de_um_publico_so_aparece_para_ele(client, seletor_ligado, notas):
    """FR-7411, `D-004`: o seletor não dá `acesso:consultar` a ninguém."""
    notas(*TRES, _nota("acessos", "2026-10-01", para_capacidade="acesso:consultar"))
    identificar(client, "gustavo.gestor", ["gestor"])
    assert "Título acessos" not in _pagina(client)


@pytest.mark.django_db
def test_basta_uma_das_capacidades_do_publico(client, seletor_ligado, notas):
    """FR-7411: a nota de vários públicos aparece a quem tem qualquer uma das capacidades."""
    notas(
        *TRES,
        '[[nota]]\nid = "vg"\ndata = 2026-10-01\ncategoria = "novidade"\nrelevancia = "relevante"\n'
        'titulo = "Título vg"\nresumo = "R."\nprs = [9]\nspecs = []\n'
        'para_capacidade = ["acesso:administrar", "visao:consultar"]\n',
    )
    identificar(client, "gustavo.gestor", ["gestor"])
    assert "Título vg" in _pagina(client)
    identificar(client, "eva.elaboradora", ["elaborador"])
    assert "Título vg" not in _pagina(client)


@pytest.mark.django_db
def test_o_link_so_vai_para_quem_alcanca_a_secao(client, seletor_ligado, notas):
    """FR-7412: a Visão Geral é do Gestor; o Elaborador lê a nota sem o link."""
    notas(*TRES)
    identificar(client, "gustavo.gestor", ["gestor"])
    assert f'<a href="{reverse("interface:visao-geral")}">Abrir Visão Geral</a>' in _pagina(client)

    identificar(client, "eva.elaboradora", ["elaborador"])
    corpo = _pagina(client)
    assert "Título b" in corpo
    assert "Abrir Visão Geral" not in corpo
    assert f'href="{reverse("interface:documentacao")}#agenda"' in corpo


# ---- a linha do tempo ------------------------------------------------------------------------


@pytest.mark.django_db
def test_a_linha_do_tempo_agrupa_por_mes_da_mais_recente(client, seletor_ligado, notas):
    """FR-7401 a FR-7404 e FR-7408."""
    notas(*TRES)
    identificar(client, "gustavo.gestor", ["gestor"])
    corpo = _pagina(client)
    assert re.findall(r'<h3 id="mes-de-novidades-\d+">([^<]+)</h3>', corpo) == [
        "Novembro de 2026",
        "Outubro de 2026",
    ]
    assert re.findall(r'<li class="novidade r-\w+" id="(\w+)">', corpo) == ["c", "b", "a"]
    assert '<span class="categoria-da-novidade c-correcao">Correção</span>' in corpo
    assert "As datas são as de chegada da mudança ao GPS" in corpo


@pytest.mark.django_db
def test_o_exemplo_aparece_como_na_pratica(client, seletor_ligado, notas):
    """FR-7427, UX-806: a cena concreta logo abaixo do resumo."""
    notas(_nota("x", "2026-11-12", exemplo="Você abre o Edital 12/2026 e vê o que falta."))
    identificar(client, "gustavo.gestor", ["gestor"])
    cartao = _pagina(client).split('<li class="novidade r-relevante" id="x">')[1].split("</li>")[0]
    assert (
        '<p class="exemplo-da-novidade"><strong>Na prática:</strong> '
        "Você abre o Edital 12/2026 e vê o que falta.</p>"
    ) in cartao
    assert cartao.index("Resumo de x.") < cartao.index("Na prática")


@pytest.mark.django_db
def test_o_filtro_por_categoria_conta_e_guarda_a_escolha(client, seletor_ligado, notas):
    """US4, FR-7405."""
    notas(*TRES)
    identificar(client, "gustavo.gestor", ["gestor"])
    corpo = _pagina(client, categoria="correcao")
    assert re.findall(r'<li class="novidade r-\w+" id="(\w+)">', corpo) == ["c"]
    filtros = corpo.split('class="filtros-das-novidades"')[1].split("</nav>")[0]
    assert 'aria-current="page">Correções <span class="quantidade-do-filtro">1</span>' in filtros
    assert 'Todas <span class="quantidade-do-filtro">3</span>' in filtros
    # Filtro inventado cai no padrão, sem 404.
    assert len(re.findall(r'<li class="novidade r-', _pagina(client, categoria="x"))) == 3


@pytest.mark.django_db
def test_a_pagina_continua_nas_anteriores(client, seletor_ligado, notas):
    """US4, FR-7406: 12 por página."""
    notas(*[_nota(f"n{i:02d}", f"2026-11-{30 - i:02d}") for i in range(14)])
    identificar(client, "gustavo.gestor", ["gestor"])
    primeira = _pagina(client)
    assert len(re.findall(r'<li class="novidade r-', primeira)) == 12
    assert "Atualizações anteriores" in primeira
    segunda = _pagina(client, pagina=2)
    assert re.findall(r'<li class="novidade r-\w+" id="(\w+)">', segunda) == ["n12", "n13"]
    assert "Atualizações mais recentes" in segunda


@pytest.mark.django_db
def test_arquivo_invalido_nao_derruba_a_gestao(client, seletor_ligado, notas):
    """Caso-limite: a página diz que está indisponível, e o resto continua de pé."""
    notas('[[nota]]\nid = "x"\n')
    identificar(client, "gustavo.gestor", ["gestor"])
    lista = client.get(reverse("interface:lista"))
    assert lista.status_code == 200
    assert _contagem(lista.content.decode()) is None
    assert "As novidades estão indisponíveis neste momento" in _pagina(client)


@pytest.mark.django_db
def test_o_conteudo_real_abre_sem_jargao_na_tela(client, seletor_ligado):
    """SC-2506, sobre o arquivo de verdade."""
    identificar(client, "gustavo.gestor", ["gestor", "auditor"])
    corpo = _pagina(client)
    conteudo = corpo.split('<main id="conteudo"')[1]
    # A primeira nota do arquivo, e não um título fixo: a curadoria acrescenta no topo toda semana.
    assert catalogo.notas()[0].titulo in conteudo
    assert not re.search(r"#\d{3}|\bPR\b|FR-\d", re.sub(r'href="[^"]*"', "", conteudo))


# ---- o peso pela relevância (FR-7601, FR-7604) e só o que mudou (`D-014`) ----------------------


@pytest.mark.django_db
def test_a_pagina_e_so_do_que_mudou(client, seletor_ligado, notas):
    """`D-014`: nenhuma vitrine de capacidades antes do histórico; a primeira visita aponta o manual
    a quem quer aprender a usar o GPS do começo."""
    notas(*TRES)
    identificar(client, "gustavo.gestor", ["gestor"])
    corpo = _pagina(client)
    assert "Descubra o que o GPS" not in corpo and "faz parte de" not in corpo
    assert f'href="{reverse("interface:documentacao")}#comece"' in corpo


@pytest.mark.django_db
def test_a_incremental_e_uma_linha_enxuta(client, seletor_ligado, notas):
    """FR-7601, UX-822: o ajuste não ganha o mesmo peso da capacidade nova."""
    notas(_nota("y", "2026-11-12", "correcao", "incremental", exemplo="Uma cena.", onde="Ali."))
    identificar(client, "gustavo.gestor", ["gestor"])
    cartao = (
        _pagina(client).split('<li class="novidade r-incremental" id="y">')[1].split("</li>")[0]
    )
    assert "Resumo de y." in cartao
    assert "Na prática" not in cartao and "Como usar" not in cartao


@pytest.mark.django_db
def test_a_visita_abre_pela_mudanca_de_maior_peso(client, seletor_ligado, notas):
    """FR-7604: a transformadora abre o bloco, mesmo mais antiga; o resto vem contado, com teto."""
    from django.utils import timezone

    LeituraDasNovidades.objects.create(
        subject="gustavo.gestor", vistas=["velha"], ultima_visita=timezone.now()
    )
    notas(
        *[_nota(f"m{i}", "2026-11-12", "correcao", "incremental") for i in range(5)],
        _nota("grande", "2026-11-10", "novidade", "transformadora", exemplo="Cena."),
        _nota("velha", "2026-10-01"),
    )
    identificar(client, "gustavo.gestor", ["gestor"])
    bloco = _pagina(client).split('class="desde-a-ultima-visita"')[1].split("</section>")[0]
    principal = bloco.split('class="principal-da-visita"')[1].split("</p>")[0]
    assert "#grande" in principal
    assert "Também chegaram 5 correções" in bloco
    assert bloco.count("<li>") == 3
    assert "E mais 2, em" in bloco
