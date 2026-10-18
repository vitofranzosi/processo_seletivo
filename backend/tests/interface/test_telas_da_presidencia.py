"""As telas da presidência da comissão, terceiro incremento (079).

Na Comissão, na conferência da inclusão, na Alocação e na Distribuição a trilha mora no cabeçalho
de contexto, e só lá; na Distribuição, os lugares da Etapa vêm logo abaixo do título, e nenhuma ação
sai do lugar; a Comissão tem título para os membros e estado vazio que leva à inclusão; a Alocação
salva "alocação". O desenho em si é provado no navegador e pelo inventário visual refeito
(quickstart): aqui fica o que a marcação garante.
"""

import re

import pytest
from django.urls import reverse

from tests.interface.conftest import identificar
from tests.interface.test_acessibilidade_da_012 import cenario  # noqa: F401 — fixture
from tests.interface.test_shell_da_gestao import barra
from tests.interface.test_telas_de_uso_diario import (
    TEMPLATES,
    conteudo,
    trilha_unica_no_cabecalho,
)

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def comeca_pelo_titulo(corpo):
    return conteudo(corpo).split(">", 1)[1].lstrip().startswith("<h1>")


def niveis_em_ordem(trilha, niveis):
    posicoes = [trilha.index(nivel) for nivel in niveis]
    assert posicoes == sorted(posicoes)


def ate_o_processo(processo):
    return [
        f'<a href="{reverse("interface:lista")}">Processos Seletivos</a> ›',
        f'<a href="{reverse("interface:processo-detalhe", args=[processo.id])}">'
        f"{processo.institutional_code}</a> ›",
    ]


def abrir(client, rota, *args):
    resposta = client.get(reverse(rota, args=args))
    assert resposta.status_code == 200, rota
    return resposta.content.decode()


# ---- a trilha no cabeçalho -------------------------------------------------------------------


def test_na_comissao_a_trilha_sobe_ao_cabecalho(client, seletor_ligado, cenario):  # noqa: F811
    """`FR-1780`, `FR-1781`, `SC-692`: GPS › Processos Seletivos › código › Comissão."""
    identificar(client, "maria", [])
    processo = cenario["processo"]
    corpo = abrir(client, "interface:comissao", processo.id)

    trilha = trilha_unica_no_cabecalho(corpo)
    niveis_em_ordem(trilha, ate_o_processo(processo))
    assert trilha.rstrip().endswith('<span aria-current="page">Comissão</span>')
    assert comeca_pelo_titulo(corpo)
    # A seção é a do endereço: a barra e a trilha dizem a mesma coisa.
    assert f'<a href="{reverse("interface:lista")}" aria-current="true">' in barra(corpo)


@pytest.mark.parametrize(
    "envio",
    [
        {"acao": "incluir", "identity_subject": "nova.pessoa", "funcao": "MEMBRO"},
        {"acao": "incluir_lote", "lista": "nova.pessoa\noutra.pessoa", "funcao": "MEMBRO"},
    ],
    ids=["um", "lista"],
)
def test_na_conferencia_a_trilha_passa_pela_comissao(client, seletor_ligado, cenario, envio):  # noqa: F811
    """`FR-1780`, `FR-1781`, `FR-1789`: a conferência, de um e da lista, com a Comissão a um clique;
    o conteúdo dela não muda."""
    identificar(client, "maria", [])
    processo = cenario["processo"]
    resposta = client.post(
        reverse("interface:comissao", args=[processo.id]),
        {**envio, "chave_idempotencia": "conferir-079"},
    )
    corpo = resposta.content.decode()

    trilha = trilha_unica_no_cabecalho(corpo)
    comissao = reverse("interface:comissao", args=[processo.id])
    niveis_em_ordem(trilha, [*ate_o_processo(processo), f'<a href="{comissao}">Comissão</a> ›'])
    assert trilha.rstrip().endswith('<span aria-current="page">Conferir</span>')
    assert comeca_pelo_titulo(corpo)
    assert "<h1>Confira antes de incluir</h1>" in corpo
    assert "Cancelar e voltar" in conteudo(corpo)


def test_na_alocacao_a_trilha_sobe_e_a_barra_continua_no_topo(client, seletor_ligado, cenario):  # noqa: F811
    """`FR-1780`, `FR-1781`, `FR-1784`: a trilha no cabeçalho, e a barra no topo em qualquer
    largura, sem o script da preferência (DP-4 da 076)."""
    identificar(client, "maria", [])
    processo = cenario["processo"]
    corpo = abrir(client, "interface:alocacoes", processo.id)

    trilha = trilha_unica_no_cabecalho(corpo)
    niveis_em_ordem(trilha, ate_o_processo(processo))
    assert trilha.rstrip().endswith('<span aria-current="page">Alocação por Etapa</span>')
    assert comeca_pelo_titulo(corpo)
    assert '<div class="shell shell-barra-no-topo">' in corpo
    assert "shell.js" not in corpo
    # A trilha não entra na moldura da matriz.
    assert "Trilha de navegação" not in corpo.split('<div class="distribuicao-moldura">')[1]


def test_na_distribuicao_a_trilha_continua_pela_alocacao(client, seletor_ligado, cenario):  # noqa: F811
    """`FR-1780`, `FR-1781`: a mesma trilha da Etapa aberta pela gestão (`FR-1752` da 077)."""
    identificar(client, "maria", [])
    edital, etapa, processo = cenario["edital"], cenario["etapa"], cenario["processo"]
    corpo = abrir(client, "interface:distribuicao", edital.id, etapa)

    trilha = trilha_unica_no_cabecalho(corpo)
    alocacoes = reverse("interface:alocacoes", args=[processo.id])
    niveis_em_ordem(
        trilha, [*ate_o_processo(processo), f'<a href="{alocacoes}">Alocação por Etapa</a> ›']
    )
    nome = re.search(r"<h1>(.*?)</h1>", corpo).group(1)
    assert trilha.rstrip().endswith(f'<span aria-current="page">{nome}</span>')
    assert comeca_pelo_titulo(corpo)


# As filhas da Distribuição tinham aqui o guardião da `FR-1782`, com o cabeçalho da 076 e a trilha
# no conteúdo. A 080 as levou ao cabeçalho (`FR-1800` da 080), e o guardião mudou para lá:
# `test_telas_filhas_da_distribuicao.py`, que também prova a Auditoria do Edital ainda de fora.


# ---- os lugares da Etapa, na Distribuição ----------------------------------------------------

LUGARES = ("Impedimentos", "Registrar ocorrência", "Resultados", "Trilha")


def test_os_lugares_da_etapa_vem_logo_abaixo_do_titulo(client, seletor_ligado, cenario):  # noqa: F811
    """`FR-1785`, `SC-693`: a faixa antes da ficha, com os mesmos quatro links, na mesma ordem,
    no mesmo desenho."""
    identificar(client, "maria", [])
    edital, etapa = cenario["edital"], cenario["etapa"]
    pagina = conteudo(abrir(client, "interface:distribuicao", edital.id, etapa))

    assert pagina.count('<p class="acoes-do-painel">') == 1
    inicio = pagina.index('<p class="acoes-do-painel">')
    faixa = pagina[inicio : pagina.index("</p>", inicio)]
    assert pagina.index('<p class="sub">') < inicio < pagina.index('<dl class="ficha curta">')
    rotas = (
        "interface:impedimentos",
        "interface:registrar-ocorrencia",
        "interface:resultados-da-etapa",
        "interface:trilha-da-avaliacao",
    )
    esperados = [
        f'<a class="acao" href="{reverse(rota, args=[edital.id, etapa])}">{rotulo}</a>'
        for rota, rotulo in zip(rotas, LUGARES, strict=True)
    ]
    niveis_em_ordem(faixa, esperados)


def test_as_mensagens_do_ultimo_envio_vem_antes_da_faixa():
    """`FR-1785`: título, o que acabou de acontecer, e então os lugares — a ordem da Comissão e da
    Alocação."""
    texto = (TEMPLATES / "distribuicao.html").read_text()
    corpo = texto.split("{% block conteudo %}")[1]

    marcos = ["<h1>", "{% if erro %}", "{% if resultado %}", '<p class="acoes-do-painel">']
    niveis_em_ordem(corpo, marcos)


def test_nenhuma_acao_da_distribuicao_sai_do_lugar():
    """`FR-1786`: os avisos, os desfechos e as ações continuam na ordem de antes da 079, cada um ao
    lado do número ou da frase a que responde — e a faixa vem antes de todos."""
    corpo = (TEMPLATES / "distribuicao.html").read_text().split("{% block conteudo %}")[1]

    marcos = [
        '<p class="acoes-do-painel">',
        '<dl class="ficha curta">',
        'aria-label="Filtrar por cobertura"',
        "{% if bloqueio_da_etapa %}",
        "{% if inscricoes_em_curso %}",
        "{% if consolidacao %}",
        'aria-label="Filtrar por prontidão para consolidar"',
        '<input type="hidden" name="alcance" value="prontas">',
        '<h2 id="carga">',
        '<h2 id="orfas">',
        "conclusões\n  preservadas</a>",
        '<h2 id="rodizio">',
        "Confirmar esta distribuição",
        "Propor distribuição",
        '<h2 id="inscricoes">',
        "<dfn>Consolidar</dfn> é transformar",
        # Os botões, e não o rótulo solto: um comentário do template cita o segundo deles.
        '<button type="submit" class="botao">Distribuir as selecionadas</button>',
        "formaction=\"{% url 'interface:consolidar-resultados' edital.id etapa.id %}\"",
        '<button type="submit" class="acao perigoso">Retirar as selecionadas</button>',
    ]
    niveis_em_ordem(corpo, marcos)
    assert corpo.count('<p class="acoes-do-painel">') == 1
    # O desenho das ações não muda: as cheias continuam cheias, e a retirada contornada de perigo.
    assert '<button type="submit" class="acao perigoso">Retirar as selecionadas</button>' in corpo
    assert corpo.count('class="botao"') == 6


# ---- a Comissão ------------------------------------------------------------------------------


def secao_dos_membros(corpo):
    return (
        conteudo(corpo)
        .split('<section aria-labelledby="membros-titulo">')[1]
        .split("</section>")[0]
    )


def test_os_membros_tem_titulo_com_a_comissao_inteira(
    client, seletor_ligado, processo_a, comissao_de_a
):
    """`FR-1787`: "Membros (2)", com o filtro e a lista sob ele, antes das seções de inclusão; o
    título conta a comissão inteira, inclusive filtrada."""
    identificar(client, "maria", [])
    corpo = abrir(client, "interface:comissao", processo_a.id)
    secao = secao_dos_membros(corpo)

    assert '<h2 id="membros-titulo">Membros (2)</h2>' in secao
    assert 'class="filtro" role="search"' in secao
    assert 'aria-label="Membros da comissão"' in secao
    assert conteudo(corpo).index("membros-titulo") < conteudo(corpo).index("adicionar-titulo")

    filtrada = client.get(
        reverse("interface:comissao", args=[processo_a.id]) + "?q=joao"
    ).content.decode()
    assert '<h2 id="membros-titulo">Membros (2)</h2>' in filtrada
    assert "1 de 2 membros." in secao_dos_membros(filtrada)


def test_comissao_vazia_nao_tem_filtro_e_leva_a_inclusao(client, seletor_ligado, processo_a):
    """`FR-1788`: sem ninguém, nada a procurar; o estado vazio leva ao formulário, logo abaixo."""
    identificar(client, "carlos", ["gestor"])
    corpo = abrir(client, "interface:comissao", processo_a.id)
    secao = secao_dos_membros(corpo)

    assert '<h2 id="membros-titulo">Membros (0)</h2>' in secao
    assert 'role="search"' not in secao
    assert "Só quem está sem Etapa" not in corpo
    assert (
        '<p class="vazio" role="status">Esta comissão ainda não tem membros.\n'
        '  <a href="#adicionar-titulo">Adicionar membro</a></p>'
    ) in secao
    assert '<h2 id="adicionar-titulo">Adicionar membro</h2>' in conteudo(corpo)


def test_recorte_vazio_mantem_o_filtro(client, seletor_ligado, processo_a, comissao_de_a):
    """`FR-1788`: com membros, o filtro continua, para ser desfeito, e o vazio é o do filtro."""
    identificar(client, "maria", [])
    corpo = client.get(
        reverse("interface:comissao", args=[processo_a.id]) + "?q=ninguem"
    ).content.decode()
    secao = secao_dos_membros(corpo)

    assert 'role="search"' in secao
    assert "Limpar" in secao
    assert '<p class="vazio" role="status">Nenhum membro corresponde ao filtro.</p>' in secao
    assert "Esta comissão ainda não tem membros." not in secao


# ---- a Alocação ------------------------------------------------------------------------------


def test_a_alocacao_salva_alocacao(client, seletor_ligado, cenario):  # noqa: F811
    """`FR-1790`: o botão depois da matriz diz o que faz, no mesmo desenho."""
    identificar(client, "maria", [])
    corpo = abrir(client, "interface:alocacoes", cenario["processo"].id)

    botao = '<button type="submit" class="botao">Salvar alocação</button>'
    assert f'<p class="salvar">{botao}</p>' in corpo
    assert "Salvar distribuição" not in corpo
    depois_da_matriz = corpo.split("</table>")[-1]
    assert "Salvar alocação" in depois_da_matriz


def test_sem_presidencia_a_alocacao_continua_sem_botao(client, seletor_ligado, gestor, processo_a):
    """`FR-1790`: as mesmas condições — sem presidência, nada a salvar."""
    from tests.fixtures.comissao import constituir

    constituir(gestor, processo_a, [("joao", "MEMBRO")])
    identificar(client, "carlos", ["gestor"])
    corpo = abrir(client, "interface:alocacoes", processo_a.id)

    assert "Salvar alocação" not in corpo
    assert "Designe a presidência antes de distribuir" in corpo
