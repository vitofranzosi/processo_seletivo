"""057 — o polish das telas de operação.

As medidas de tela — a linha da Lista, "Quem atuou", a média por evento da Auditoria, a largura da
Alocação — estão em `specs/057-polish-telas-de-operacao/verificacao.md`, tiradas na página
renderizada. O que fica aqui é o que as produz: a repartição das ações, a regra na folha e a
marcação no template. A lista de destinos de cada tela, antes e depois, está no mesmo diretório.
"""

import re
from pathlib import Path

import pytest
from django.template.loader import render_to_string
from django.urls import reverse

from processo_seletivo.interface import acoes, revisao
from processo_seletivo.interface.acoes import Acao
from processo_seletivo.interface.templatetags.interface_extras import contagem
from tests.interface.conftest import identificar
from tests.interface.test_acessibilidade import FONTE, PORTAL, _estilo_proprio, sem_prosa
from tests.interface.test_acoes import homologado

RAIZ = Path(__file__).resolve().parents[2] / "processo_seletivo"
GESTAO = RAIZ / "interface/templates/interface"
FOLHA = sem_prosa(FONTE)


def regra(seletor, folha=FOLHA):
    """O corpo da regra cujo seletor é exatamente `seletor`, sem espaços, ou `None`."""
    achado = re.search(rf"(?:^|[}}\n])[ \t]*{re.escape(seletor)}\{{([^}}]*)\}}", folha)
    return achado.group(1).replace("\n", "").replace(" ", "") if achado else None


def da_pagina(template):
    """A folha própria de uma tela: as regras que só ela desenha não vão na folha comum."""
    return sem_prosa(_estilo_proprio(GESTAO / template))


def _acao(chave, motivo="", quantidade=None, estilo="secundario"):
    return Acao(
        chave, chave.capitalize(), f"/{chave}", estilo=estilo, motivo=motivo, quantidade=quantidade
    )


PUBLICADO = [
    _acao("retificar"),
    _acao("inscricoes", quantidade=7),
    _acao("recursos", quantidade=0),
    _acao("matriculas"),
    _acao("auditoria"),
    _acao("encerrar"),
    _acao("cancelar", estilo="perigoso"),
]


# --- T2 — a hierarquia no Detalhe do Edital (FR-1043 a FR-1047) --------------------------------


def test_a_hierarquia_reparte_sem_perder_acao():
    """FR-1064: nenhuma ação entra nem sai. Publicado, a do dia é "Inscrições recebidas"."""
    grupo = acoes.hierarquia(PUBLICADO)

    assert grupo.principal.chave == "inscricoes"
    assert [a.chave for a in grupo.terminais] == ["encerrar", "cancelar"]
    assert [a.chave for a in grupo.secundarias] == [
        "retificar",
        "recursos",
        "matriculas",
        "auditoria",
    ]
    juntas = [grupo.principal, *grupo.secundarias, *grupo.terminais]
    assert sorted(a.chave for a in juntas) == sorted(a.chave for a in PUBLICADO)


def test_o_ato_que_avanca_e_a_principal_e_o_retrocesso_nao():
    """Em revisão, "Homologar" — e não "Devolver", que é retrocesso, nem "Visualizar"."""
    em_revisao = [_acao("visualizar"), _acao("homologar"), _acao("devolver")]
    assert acoes.hierarquia(em_revisao).principal.chave == "homologar"
    assert acoes.hierarquia([_acao("visualizar"), _acao("devolver")]).principal is None


def test_a_preferida_impedida_nao_e_substituida():
    """FR-1045: "Publicar" impedido continua a principal, desabilitado; nada sobe no lugar dele."""
    homologado_ = [
        _acao("visualizar"),
        _acao("revogar-homologacao"),
        _acao("publicar", motivo="Publicar exige outra pessoa autorizada."),
    ]
    grupo = acoes.hierarquia(homologado_)
    assert grupo.principal.chave == "publicar" and not grupo.principal.disponivel
    assert [a.chave for a in grupo.secundarias] == ["visualizar", "revogar-homologacao"]


def test_sem_acao_o_grupo_e_vazio():
    """FR-1046: a frase de ausência depende de o grupo ser falso."""
    assert not acoes.hierarquia([])


def test_o_detalhe_desenha_as_terminais_por_ultimo_e_so_contornadas():
    detalhe = (GESTAO / "detalhe.html").read_text()
    principal = detalhe.index("grupo.principal %}{% include")
    terminais = detalhe.index('class="lista-acoes em-linha terminais"')
    assert principal < terminais, "as que encerram ou interrompem vêm por último"
    assert "Nenhum ato disponível para seus papéis nesta situação." in detalhe
    assert '<div class="colunas ao-topo">' in detalhe

    folha = da_pagina("detalhe.html")
    assert "flex-direction:row" in regra(".lista-acoes.em-linha", folha)
    # O filete só existe quando há grupo acima dele: sem a lista, não há o que separar.
    assert "border-top:1px" in regra(".lista-acoes+.terminais", folha)
    contorno = regra(".terminais .botao", folha)
    assert "background:var(--branco)" in contorno and "color:var(--vermelho)" in contorno
    assert "align-items:flex-start" in regra(".colunas.ao-topo", folha)
    for seletor in (".lista-acoes.em-linha", ".terminais .botao", ".colunas.ao-topo"):
        assert regra(seletor) is None, f"{seletor} é desta tela, e não da folha comum"


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_o_homologado_tem_publicar_como_unica_cheia(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """SC-398 na tela: uma ação cheia, e Cancelar no grupo de baixo, contornado."""
    alvo = homologado(api_client, manager_headers, process_payload)
    identificar(client, "pub", ["publicador", "gestor"])

    corpo = client.get(reverse("interface:detalhe", args=[alvo.id])).content.decode()

    cheias = [
        rotulo
        for classes, rotulo in re.findall(r'<a class="([^"]*)" href="[^"]*">([^<]+)<', corpo)
        if classes.split() == ["botao"]
    ]
    assert cheias == ["Publicar"], cheias
    _, terminais = corpo.split('class="lista-acoes em-linha terminais"', 1)
    assert "Cancelar" in terminais.split("</ul>", 1)[0]


# --- T2 — a Condução do marco (FR-1048) --------------------------------------------------------


def test_a_conducao_destaca_so_o_primeiro_gesto():
    marco = (GESTAO / "marco.html").read_text()
    assert 'class="botao{% if not forloop.first %} secundario{% endif %}"' in marco
    assert '<div class="gestos">' in marco
    assert re.search(r"\.gestos\{display:flex;flex-wrap:wrap", marco)


# --- T1 — a coluna da Lista (FR-1049, FR-1050) -------------------------------------------------


def test_a_lista_poe_as_frequentes_primeiro_e_as_terminais_no_fim():
    linha = acoes.da_linha([a for a in PUBLICADO if a.chave != "auditoria"])
    assert linha.principal is None, "na Lista não há ação cheia (D-004)"
    assert [a.chave for a in linha.secundarias] == [
        "inscricoes",
        "recursos",
        "retificar",
        "matriculas",
    ]
    assert [a.chave for a in linha.terminais] == ["encerrar", "cancelar"]
    lista = (GESTAO / "lista.html").read_text()
    assert '<span class="acoes terminais">' in lista
    assert "border-left:1px" in regra(".acoes>*+.terminais", da_pagina("lista.html"))


def test_o_contador_zero_esmaece_sem_perder_o_rotulo():
    zerada = render_to_string(
        "interface/_acao_de_linha.html",
        {"acao": Acao("recursos", "Recursos aguardando decisão (0)", "/r", quantidade=0)},
    )
    assert 'class="acao zerada" href="/r">Recursos aguardando decisão (0)</a>' in zerada
    com_sete = render_to_string(
        "interface/_acao_de_linha.html",
        {"acao": Acao("inscricoes", "Inscrições recebidas (7)", "/i", quantidade=7)},
    )
    assert "zerada" not in com_sete
    assert "color:var(--texto-fraco)" in regra(".acao.zerada", da_pagina("lista.html"))


# --- D2 — o glossário recolhido (FR-1051 a FR-1053) --------------------------------------------

GLOSSARIOS = [
    "marco.html",
    "ordenacao.html",
    "corte.html",
    "corte_historico.html",
    "ocupacao.html",
    "convocacao.html",
    "sorteio.html",
    "matriculas.html",
]


@pytest.mark.parametrize("template", GLOSSARIOS)
def test_o_glossario_fica_recolhido_e_a_garantia_a_vista(template):
    fonte = re.sub(
        r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}",
        "",
        (GESTAO / template).read_text(),
        flags=re.S,
    )
    recolhido = re.search(
        r'<details class="como-preencher">\s*<summary>Termos desta tela</summary>\s*'
        r'<p class="definicoes">.*?</p>\s*</details>',
        fonte,
        re.S,
    )
    assert recolhido, f"{template}: o glossário fica num details fechado, no mesmo lugar"
    assert fonte.count('class="definicoes"') == 1
    # A garantia ao operador não é glossário: continua fora do details.
    for faixa in re.finditer(r'<p class="imutavel">', fonte):
        assert not (recolhido.start() < faixa.start() < recolhido.end())


def test_o_glossario_do_assistente_fica_como_esta():
    """FR-1053: `compor_perfis.html` é da 056 e não entra."""
    assert "Termos desta tela" not in (GESTAO / "compor_perfis.html").read_text()


# --- F8 — números, datas e plurais (FR-1058 a FR-1060) -----------------------------------------


def test_a_revisao_escreve_numeros_datas_e_plurais_como_gente():
    assert contagem(1, "vaga,vagas") == "1 vaga"
    assert contagem(2, "vaga imediata,vagas imediatas") == "2 vagas imediatas"
    assert contagem(0, "vaga imediata,vagas imediatas") == "0 vagas imediatas"
    assert revisao._versao("2014-06-09") == "09/06/2014"
    assert revisao._versao("2ª edição") == "2ª edição", "versão que não é data sai como está"
    fonte = (RAIZ / "interface/revisao.py").read_text()
    assert not re.findall(r'f"[^"\n]*\(s\)', fonte), "nenhum plural com parênteses na Revisão"


def test_o_plural_se_resolve_num_lugar_so():
    """Os quatro módulos que escreviam `vaga(s)` para a tela passam pelo mesmo `contagem`.

    No Retificar só o resumo do acréscimo é da tela: `objeto_legivel` alimenta o registro do gesto,
    e fica como está até alguém decidir sobre ele (FR-1060, `doc/achado-f8-...`).
    """
    for modulo in ("revisao", "supervisao", "conducao_do_marco", "retificacao"):
        fonte = (RAIZ / f"interface/{modulo}.py").read_text()
        assert "contagem(" in fonte, modulo
        if modulo != "retificacao":
            assert not re.findall(r"f\"[^\"\n]*\bvaga\(s\)", fonte), modulo
    resumo = (RAIZ / "interface/retificacao.py").read_text()
    assert '"depois": contagem(' in resumo


# --- T3 — sem caixa dentro de caixa (FR-1054 a FR-1057) ----------------------------------------


def test_a_atencao_e_lista_com_faixa_ambar():
    assert "border-left:4pxsolidvar(--amarelo)" in regra(".sinais")
    sinal = regra(".sinais .sinal")
    assert "border" not in sinal and "background" not in sinal, "sem moldura por sinal"
    assert "border-top:1px" in regra(".sinais .sinal+.sinal")
    assert "var(--verde)" not in (regra(".sinais") + sinal)


def test_o_evento_de_auditoria_nao_e_cartao():
    evento = regra(".auditoria li")
    assert (
        "background" not in evento and "border-left" not in evento and "border-radius" not in evento
    )
    assert "border-bottom:1px" in evento
    assert "flex-basis:100%" in regra(".auditoria .motivo")


def test_os_documentos_da_inscricao_seguem_a_mesa():
    detalhe = re.sub(
        r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}",
        "",
        (GESTAO / "inscricao_detalhe.html").read_text(),
        flags=re.S,
    )
    assert '<ul class="documentos">' in detalhe
    assert "requisitos-apresentados" not in detalhe
    for dado in (
        "SHA-256",
        ">Visualizar<",
        ">Baixar<",
        "Não apresentado.",
        "facultativo",
        "documento.razao",
        "nome_original",
        "documento.tamanho",
        "uploaded_at",
    ):
        assert dado in detalhe, dado
    # As regras dos cartões saíram com eles, e o resumo do arquivo foi para a página.
    assert regra(".requisitos-apresentados") is None and regra(".acoes-do-documento") is None
    assert regra(".resumo-do-arquivo") is None
    folha = da_pagina("inscricao_detalhe.html")
    assert regra(".resumo-do-arquivo", folha)
    # Três colunas, sem as células vazias que viravam faixas em branco abaixo de 34 rem.
    assert regra("ul.documentos", folha) == "grid-template-columns:minmax(0,1fr)autoauto"
    assert '<span class="modelo"></span>' not in detalhe and '<span class="leitura">' not in detalhe
    assert 'class="instrucao"' not in detalhe, "o arquivo não se veste de instrução do Edital"


def test_a_ficha_curta_tem_a_largura_do_conteudo():
    assert "width:fit-content" in regra(".ficha.curta")
    for template in ("distribuicao.html", "minha_etapa.html"):
        assert '<dl class="ficha curta">' in (GESTAO / template).read_text(), template
    assert '<dl class="ficha">' in (GESTAO / "mesa_inscricao.html").read_text(), "a da mesa fica"


# --- T4 — a matriz de Alocação (FR-1061, FR-1062) ----------------------------------------------


def test_a_matriz_agrupa_por_edital_e_fixa_o_cabecalho():
    alocacoes = (GESTAO / "alocacoes.html").read_text()
    assert "{% regroup matriz.colunas by edital as grupos %}" in alocacoes
    assert '<th scope="colgroup" colspan="{{ grupo.list|length }}">' in alocacoes
    cabecalho = alocacoes[alocacoes.index("<thead>") : alocacoes.index("</thead>")]
    assert 'class="codigo"' not in cabecalho, "o Edital não se repete em cada coluna"
    for rotulo in ("Distribuir", 'aria-label="Marcar todos em', 'aria-label="Desmarcar todos em'):
        assert rotulo in cabecalho

    assert "position:sticky;top:0" in regra(".distribuicao thead", da_pagina("alocacoes.html"))
    assert regra(".distribuicao thead") is None, "regra só desta tela, fora da folha comum"
    assert "sticky" not in regra(".distribuicao thead th"), "duas linhas fixas se sobrepunham"


# --- D5 — o envio do portal (FR-1063) ----------------------------------------------------------


def test_o_envio_de_documento_e_uma_linha():
    documentos = (RAIZ / "portal/templates/portal/_documentos.html").read_text()
    escolher = re.search(r'<div class="escolher">(.*?)</div>', documentos, re.S).group(1)
    assert "data-arquivo" in escolher and "data-nome-do-arquivo" in escolher
    assert '<button type="submit" class="acao">Enviar</button>' in escolher
    assert '<div class="linha">' not in documentos
    assert ".envio .linha{" not in PORTAL.read_text()
