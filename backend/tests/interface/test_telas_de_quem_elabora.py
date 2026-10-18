"""As telas de quem elabora, segundo incremento (078).

As duas causas latentes que a 077 corrigiu tela a tela sobem para a folha comum; no detalhe do
Processo, no do Edital e na composição, a trilha mora no cabeçalho de contexto e "O que fazer agora"
vem antes do resto; os Editais do Processo são a tabela da lista. O desenho em si é provado no
navegador e pelo inventário visual refeito (quickstart): aqui fica o que a marcação garante.
"""

import re

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.interface.views import CHAVES_ETAPA
from processo_seletivo.processos.models import ProcessoSeletivo
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar
from tests.interface.folha import FOLHA_COMUM, GESTAO_CSS, sem_comentarios
from tests.interface.test_telas_de_uso_diario import (
    TEMPLATES,
    conteudo,
    trilha_unica_no_cabecalho,
)

# A folha comum saiu do modelo para `gestao.css` na 089.
FOLHA = FOLHA_COMUM


def regras_fora_de_media(folha):
    return re.sub(r"@media[^{]*\{(?:[^{}]|\{[^{}]*\})*\}", "", sem_comentarios(folha))


def antes(corpo, primeiro, segundo):
    """`primeiro` aparece no conteúdo antes de `segundo`, e os dois aparecem."""
    miolo = conteudo(corpo)
    assert primeiro in miolo, primeiro
    assert segundo in miolo, segundo
    return miolo.index(primeiro) < miolo.index(segundo)


def comeca_pelo_titulo(corpo):
    return conteudo(corpo).split(">", 1)[1].lstrip().startswith("<h1>")


# ---- as causas latentes, na folha comum ------------------------------------------------------


ROLA = re.compile(r"overflow(?:-[xy])?:(?:auto|scroll)")
POSICIONA = re.compile(r"position:(?:relative|absolute|fixed|sticky)")


def regras(folha):
    """`(seletores, corpo)` de cada regra da folha, sem os comentários."""
    for seletor, corpo in re.findall(r"([^{}]+)\{([^{}]*)\}", sem_comentarios(folha)):
        yield {s.strip() for s in seletor.split(",") if s.strip()}, corpo


def test_toda_moldura_que_rola_e_referencia_do_que_carrega():
    """`FR-1760`: toda moldura que rola na gestão — em `x` ou em `y`, por `auto` ou `scroll`, pela
    forma longa ou pela abreviada — é posicionada. As que só rolam no estreito ganham posição no
    mesmo `@media`, e na tela larga continuam bloco comum (058, `FR-1071`; o cabeçalho fixo da
    distribuição)."""
    rolam, posicionadas = set(), set()
    # A folha comum entra junto dos modelos (089): fora do modelo, uma moldura nova nela escaparia.
    for fonte in [*TEMPLATES.glob("*.html"), GESTAO_CSS]:
        for seletores, corpo in regras(fonte.read_text()):
            if ROLA.search(corpo):
                rolam |= {s for s in seletores if s.startswith(".")}
            # Qualquer posição que não a estática serve de referência — o painel da barra no
            # celular (076) é `position:fixed`, e já contém o que carrega.
            if POSICIONA.search(corpo):
                posicionadas |= seletores
    # Uma moldura nova sem posição traria a causa de volta em silêncio.
    assert {".tabela-rolavel", ".rolagem", ".rolavel-no-estreito", ".serie .barras"} <= rolam
    assert rolam <= posicionadas, rolam - posicionadas
    estreito = re.search(r"@media \(max-width:60rem\)\{[^@]*?\{position:relative\}", FOLHA)
    assert estreito and ".rolavel-no-estreito" in estreito.group(0)


def test_todo_grupo_de_campos_pode_encolher():
    """`FR-1761`: a regra geral de `fieldset` encolhe até a largura disponível."""
    regra = re.search(r"^fieldset\{([^}]*)\}", regras_fora_de_media(FOLHA), re.MULTILINE)
    assert regra and "min-width:0" in regra.group(1)


def test_todo_cartao_em_colunas_pode_encolher():
    """`FR-1777`: o cartão é item flex de `.colunas`, e encolhe até a largura disponível."""
    assert any(
        ".colunas>.cartao" in seletores and "min-width:0" in corpo
        for seletores, corpo in regras(regras_fora_de_media(FOLHA))
    )


MOLDURAS = (".tabela-rolavel", ".rolagem", ".rolavel-no-estreito", ".distribuicao-moldura")


@pytest.mark.parametrize(
    "template",
    [t for t in sorted(TEMPLATES.glob("*.html")) if t.name != "base.html"],
    ids=lambda t: t.name,
)
def test_nenhuma_tela_repete_a_decisao_da_folha_comum(template):
    """`FR-1762`, `SC-680`: as três causas são da folha comum, e nenhuma tela as corrige de novo —
    nem as três da 077, nem a vista do conjunto, que tinha a sua desde a 052 (`UX-121`). Só o par
    exato *causa e correção* reprova: outro `min-width:0` ou outro `position:relative` na tela é
    decisão dela."""
    for seletores, corpo in regras(template.read_text()):
        for seletor in seletores:
            ultimo = seletor.split()[-1]
            if "position:relative" in corpo:
                assert not ultimo.endswith(MOLDURAS), (template.name, seletor)
            if "min-width:0" in corpo:
                assert not re.match(r"fieldset(\.|$|\[)", ultimo), (template.name, seletor)
                assert ".colunas>.cartao" not in seletor, (template.name, seletor)


def test_o_produto_da_trilha_tem_uma_fonte_so():
    """O produto que abre toda trilha do cabeçalho vem de um parcial, e nenhuma tela o copia."""
    literal = '<abbr title="Gestão de Processos Seletivos">GPS</abbr>'
    assert literal in (TEMPLATES / "_produto_na_trilha.html").read_text()
    for template in TEMPLATES.glob("*.html"):
        if template.name == "_produto_na_trilha.html":
            continue
        texto = template.read_text()
        assert literal not in texto, template.name
        if "{% block caminho_do_contexto %}" in texto:
            bloco = texto.split("{% block caminho_do_contexto %}")[1].split("{% endblock %}")[0]
            assert '{% include "interface/_produto_na_trilha.html" %}' in bloco, template.name


@pytest.mark.django_db
def test_reler_o_edital_nao_perde_o_processo(edital):
    """A trilha da composição lê o Processo, e a tela remontada depois de uma gravação relê o
    Edital: relido, ele continua trazendo o Processo, sem consulta a mais (`FR-1768`)."""
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    from processo_seletivo.interface.views import _recarregar
    from processo_seletivo.processos.application.selectors import obter_edital
    from processo_seletivo.seguranca.domain import Actor

    ator = Actor(subject="ana", institution_scope=edital.institution_scope, permissions=frozenset())
    relido = obter_edital(actor=ator, edital_id=edital.id)
    with CaptureQueriesContext(connection) as consultas:
        _recarregar(relido)
        codigo = relido.processo.institutional_code
    assert codigo == edital.processo.institutional_code
    assert len(consultas.captured_queries) == 1


# ---- fixtures --------------------------------------------------------------------------------


@pytest.fixture
def publicado(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload)


@pytest.fixture
def processo_sem_edital(db):
    agora = timezone.now()
    return ProcessoSeletivo.objects.create(
        institution_scope="cefor",
        institutional_code="PS-VAZIO",
        title="Processo sem Edital",
        created_at=agora,
        created_by="gestor-a",
        last_changed_at=agora,
    )


def abrir_processo(client, processo):
    return client.get(reverse("interface:processo-detalhe", args=[processo.id])).content.decode()


def abrir_edital(client, edital):
    return client.get(reverse("interface:detalhe", args=[edital.id])).content.decode()


# ---- o que fazer, antes do resto -------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.integration
def test_no_processo_o_que_fazer_vem_antes_dos_editais_e_do_pulso(client, seletor_ligado, edital):
    """`FR-1764`, `FR-1766`, `SC-683`: o cartão sobe inteiro, com "Elaborar o Edital" dentro."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = abrir_processo(client, edital.processo)

    assert antes(corpo, 'id="acoes-processo"', 'id="editais-titulo"')
    cartao = conteudo(corpo).split('id="acoes-processo"')[1].split("</section>")[0]
    assert reverse("interface:compor", args=[edital.id]) in cartao
    assert ">Elaborar o Edital" in cartao


@pytest.mark.django_db
@pytest.mark.integration
def test_no_processo_publicado_o_pulso_vem_depois_e_os_atos_nao_mudam(
    client, seletor_ligado, publicado
):
    """`FR-1764`: o pulso continua na página, depois; os atos continuam os mesmos, na mesma ordem
    (058, `FR-1069`)."""
    identificar(client, "marcia.gestora", ["gestor"])
    corpo = abrir_processo(client, publicado.processo)

    assert antes(corpo, 'id="acoes-processo"', 'id="editais-titulo"')
    assert antes(corpo, 'id="editais-titulo"', 'id="conducao-titulo"')
    cartao = conteudo(corpo).split('id="acoes-processo"')[1].split("</section>")[0]
    assert cartao.index("Encerrar Processo") < cartao.index("Cancelar Processo")
    assert "irreversível" in cartao


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize(
    ("quem", "papeis"),
    [
        ("marcia.gestora", ["gestor"]),
        ("ana.elaboradora", ["elaborador"]),
        ("bruno.homologador", ["homologador"]),
        ("paula.publicadora", ["publicador"]),
    ],
)
def test_no_edital_o_que_fazer_vem_antes_de_quem_atuou(
    client, seletor_ligado, publicado, quem, papeis
):
    """`FR-1765`, `FR-1766`, `SC-683`: para todo papel, e com as colunas pelo topo (057)."""
    identificar(client, quem, papeis)
    corpo = abrir_edital(client, publicado)

    assert antes(corpo, 'id="acoes-titulo"', 'id="participantes-titulo"')
    assert '<div class="colunas ao-topo">' in conteudo(corpo)


# ---- onde estou, dito uma vez só -------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.integration
def test_no_processo_a_trilha_sobe_ao_cabecalho(client, seletor_ligado, edital):
    """`FR-1767`, `FR-1768`, `SC-684`: GPS › Processos Seletivos › o código."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    processo = edital.processo
    corpo = abrir_processo(client, processo)

    trilha = trilha_unica_no_cabecalho(corpo)
    assert f'<a href="{reverse("interface:lista")}">Processos Seletivos</a> ›' in trilha
    assert f'<span aria-current="page">{processo.institutional_code}</span>' in trilha
    assert comeca_pelo_titulo(corpo)


@pytest.mark.django_db
@pytest.mark.integration
def test_no_edital_a_trilha_sobe_ao_cabecalho(client, seletor_ligado, edital):
    """`FR-1767`, `FR-1768`, `SC-684`: GPS › Processos Seletivos › o código › o Edital."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    processo = edital.processo
    corpo = abrir_edital(client, edital)

    trilha = trilha_unica_no_cabecalho(corpo)
    niveis = [
        f'<a href="{reverse("interface:lista")}">Processos Seletivos</a> ›',
        f'<a href="{reverse("interface:processo-detalhe", args=[processo.id])}">'
        f"{processo.institutional_code}</a> ›",
        f'<span aria-current="page">Edital {edital.number}/{edital.year}</span>',
    ]
    posicoes = [trilha.index(nivel) for nivel in niveis]
    assert posicoes == sorted(posicoes)
    assert comeca_pelo_titulo(corpo)


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize("etapa", CHAVES_ETAPA)
def test_em_toda_etapa_da_composicao_a_trilha_passa_pelo_processo(
    client, seletor_ligado, edital, etapa
):
    """`FR-1767`, `FR-1768`, `SC-684`: o Processo, que a trilha da composição pulava, entra entre a
    seção e o Edital; o passo continua marcado na navegação das etapas, e não na trilha."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    processo = edital.processo
    corpo = client.get(reverse("interface:compor-etapa", args=[edital.id, etapa])).content.decode()

    trilha = trilha_unica_no_cabecalho(corpo)
    niveis = [
        f'<a href="{reverse("interface:lista")}">Processos Seletivos</a> ›',
        f'<a href="{reverse("interface:processo-detalhe", args=[processo.id])}">'
        f"{processo.institutional_code}</a> ›",
        f'<a href="{reverse("interface:detalhe", args=[edital.id])}">'
        f"Edital {edital.number}/{edital.year}</a> ›",
        '<span aria-current="page">Compor</span>',
    ]
    posicoes = [trilha.index(nivel) for nivel in niveis]
    assert posicoes == sorted(posicoes)
    assert comeca_pelo_titulo(corpo)
    assert 'aria-current="step"' in conteudo(corpo)


# ---- os Editais do Processo ------------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.integration
def test_os_editais_do_processo_sao_a_tabela_da_lista(client, seletor_ligado, publicado):
    """`FR-1771`, `FR-1773`: Edital, Título e Situação, uma linha por Edital, na moldura."""
    identificar(client, "marcia.gestora", ["gestor"])
    corpo = abrir_processo(client, publicado.processo)

    regiao = conteudo(corpo).split('id="editais-titulo"')[1].split("</section>")[0]
    moldura = regiao.split('<div class="tabela-rolavel">')[1].split("</div>")[0]
    assert '<table aria-labelledby="editais-titulo">' in moldura
    cabecalhos = re.findall(r'<th scope="col">([^<]+)</th>', moldura)
    assert cabecalhos == ["Edital", "Título", "Situação"]
    destino = reverse("interface:detalhe", args=[publicado.id])
    assert (
        f'<th scope="row"><a class="codigo" href="{destino}">'
        f"{publicado.number}/{publicado.year}</a></th>"
    ) in moldura
    assert f'<td><a href="{destino}">{publicado.title}</a></td>' in moldura
    assert f'<span class="situacao s-{publicado.status}">' in moldura
    assert moldura.count("<tr>") == 2  # o cabeçalho e o Edital


@pytest.mark.django_db
@pytest.mark.integration
def test_processo_sem_edital_mostra_o_estado_vazio(client, seletor_ligado, processo_sem_edital):
    """`FR-1772`: a frase da lista, no estado vazio comum; a ação só para quem cria Edital."""
    identificar(client, "gustavo.gestor", ["gestor"])
    corpo = abrir_processo(client, processo_sem_edital)

    regiao = conteudo(corpo).split('id="editais-titulo"')[1].split("</section>")[0]
    assert '<p class="vazio">Nenhum Edital neste Processo.</p>' in regiao
    assert "<table" not in regiao
    criar = reverse("interface:edital-criar", args=[processo_sem_edital.id])
    assert f'href="{criar}"' in regiao

    identificar(client, "bruno.homologador", ["homologador"])
    regiao = (
        conteudo(abrir_processo(client, processo_sem_edital))
        .split('id="editais-titulo"')[1]
        .split("</section>")[0]
    )
    assert '<p class="vazio">Nenhum Edital neste Processo.</p>' in regiao
    assert f'href="{criar}"' not in regiao


@pytest.mark.django_db
@pytest.mark.integration
def test_sem_secao_do_processo_a_faixa_nao_vem(client, seletor_ligado, edital):
    """`FR-1776`: quem não alcança Supervisão, Comissão, Alocação nem Auditoria não vê a faixa —
    nem vazia —; o gestor continua vendo as mesmas seções."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    assert "acoes-do-painel" not in conteudo(abrir_processo(client, edital.processo))

    identificar(client, "marcia.gestora", ["gestor"])
    corpo = abrir_processo(client, edital.processo)
    faixa = conteudo(corpo).split('<p class="acoes-do-painel">')[1].split("</p>")[0]
    processo = edital.processo
    for rota in ("interface:supervisao", "interface:comissao", "interface:alocacoes"):
        assert reverse(rota, args=[processo.id]) in faixa, rota
