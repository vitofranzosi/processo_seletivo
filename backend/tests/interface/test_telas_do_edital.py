"""As telas do Edital que a 078 não cobriu, quinto incremento (083).

Em Novo Edital, Retificar, no detalhe da Retificação e na conferência de cada ato, na Prévia, em
Partir de um Edital anterior e na conferência da troca, na Condução do marco e na conferência do
gesto, na Prévia de publicação, nos Resultados divulgados e na Auditoria do Edital, a trilha mora
no cabeçalho de contexto, e só lá — a do detalhe do Edital, com os níveis que cada tela já
mostrava e ela no fim. A recusa do último envio vem logo abaixo do título em Retificar e na Prévia
de publicação; no detalhe da Retificação, "O que fazer agora" vem antes da Vigência; e "Filtrar",
em Partir de um Edital anterior, tem o desenho das Inscrições. O desenho em si é provado no
navegador e pelo inventário visual refeito (quickstart): aqui fica o que a marcação garante.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.divulgacao import montar_ato_publicavel
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar
from tests.interface.test_reaproveitar import escolher
from tests.interface.test_retificar import LINHA_GERAL, VAGAS, campos
from tests.interface.test_telas_da_presidencia import (
    ate_o_processo,
    comeca_pelo_titulo,
    niveis_em_ordem,
)
from tests.interface.test_telas_de_uso_diario import conteudo, trilha_unica_no_cabecalho


def ate_o_edital(edital):
    detalhe = reverse("interface:detalhe", args=[edital.id])
    return [
        *ate_o_processo(edital.processo),
        f'<a href="{detalhe}">Edital {edital.number}/{edital.year}</a> ›',
    ]


def termina_em(trilha, atual):
    assert trilha.rstrip().endswith(f'<span aria-current="page">{atual}</span>'), trilha


def na_secao_processos(corpo):
    """A seção é a do endereço: a barra e o começo da trilha dizem a mesma coisa."""
    assert f'<a href="{reverse("interface:lista")}" aria-current="true">' in corpo


def da_tela(client, rota, *args):
    resposta = client.get(reverse(rota, args=args))
    assert resposta.status_code == 200, rota
    return resposta.content.decode()


# ---- o Edital em elaboração: Novo Edital e a Prévia ------------------------------------------


@pytest.mark.django_db
@pytest.mark.integration
def test_em_novo_edital_a_trilha_termina_no_processo(client, seletor_ligado, edital):
    """`FR-1850`, `FR-1851`, `FR-1852`: GPS › Processos Seletivos › código › Novo Edital."""
    identificar(client, "marcia.gestora", ["gestor"])
    corpo = da_tela(client, "interface:edital-criar", edital.processo_id)

    trilha = trilha_unica_no_cabecalho(corpo)
    niveis_em_ordem(trilha, ate_o_processo(edital.processo))
    termina_em(trilha, "Novo Edital")
    assert comeca_pelo_titulo(corpo)
    na_secao_processos(corpo)


@pytest.mark.django_db
@pytest.mark.integration
def test_na_previa_a_trilha_passa_pelo_processo(client, seletor_ligado, edital):
    """`FR-1850`, `FR-1851`, `FR-1852`; a Prévia não muda de ações (D-006)."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = da_tela(client, "interface:previa", edital.id)

    trilha = trilha_unica_no_cabecalho(corpo)
    niveis_em_ordem(trilha, ate_o_edital(edital))
    termina_em(trilha, "Prévia")
    assert comeca_pelo_titulo(corpo)
    detalhe = reverse("interface:detalhe", args=[edital.id])
    assert f'<a href="{detalhe}" class="botao">‹ Voltar</a>' in conteudo(corpo)


# ---- Partir de um Edital anterior ------------------------------------------------------------


@pytest.fixture
def origem(api_client, manager_headers, process_payload):
    """Um Edital publicado do escopo: é o que pode servir de origem.

    Declarada aqui, e não importada de `test_reaproveitar.py`: importada, ela sombreava o parâmetro
    e pedia `noqa` em cada caso — o que a revisão da 077 apontou no cenário da presidência —, e a
    origem rica de lá, do acervo e com anexo, não é o que estas telas precisam."""
    return publish_original(api_client, manager_headers, process_payload)


@pytest.fixture
def destino(api_client, manager_headers, origem):
    """O Edital em elaboração, vazio, de outro Processo — onde a origem se reaproveita."""
    criado = api_client.post(
        "/api/v1/admin/processos",
        {
            "institutionalCode": "PS-2027-083",
            "title": "Processo Seletivo 2027",
            "firstEdital": {"number": "83", "year": 2027, "title": "Edital da nova oferta"},
        },
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "destino-083-0001"},
    )
    assert criado.status_code == 201, criado.content
    return Edital.objects.get(processo_id=criado.json()["id"])


@pytest.mark.django_db
@pytest.mark.usefixtures("seletor_ligado")
def test_em_partir_de_um_anterior_a_trilha_passa_pela_composicao(client, destino):
    """`FR-1850`, `FR-1851`, `FR-1852`: … › Edital › Compor › Partir de um Edital anterior."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = da_tela(client, "interface:reaproveitar", destino.id)

    trilha = trilha_unica_no_cabecalho(corpo)
    compor = reverse("interface:compor-etapa", args=[destino.id, "identificacao"])
    niveis_em_ordem(trilha, [*ate_o_edital(destino), f'<a href="{compor}">Compor</a> ›'])
    termina_em(trilha, "Partir de um Edital anterior")
    assert comeca_pelo_titulo(corpo)


@pytest.mark.django_db
@pytest.mark.usefixtures("seletor_ligado")
def test_em_partir_de_um_anterior_filtrar_e_a_acao_do_filtro(client, destino, origem):
    """`FR-1858`: "Filtrar" com o desenho de ação principal e "Limpar" com o de secundária, como
    nas Inscrições; a escolha continua com o dela."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    sem_busca = conteudo(da_tela(client, "interface:reaproveitar", destino.id))
    assert '<button type="submit" class="botao">Filtrar</button>' in sem_busca
    assert ">Limpar</a>" not in sem_busca
    assert '<button type="submit" class="botao">Usar como base</button>' in sem_busca

    url = reverse("interface:reaproveitar", args=[destino.id])
    com_busca = conteudo(client.get(url, {"busca": str(origem.year)}).content.decode())
    assert f'<a class="acao" href="{url}">Limpar</a>' in com_busca


@pytest.mark.django_db
@pytest.mark.usefixtures("seletor_ligado")
def test_na_conferencia_da_troca_a_trilha_e_a_de_partir_de_um_anterior(client, destino, origem):
    """`FR-1851`: a conferência da troca tem a trilha da tela de onde se abre, com ela no fim
    (D-001); `FR-1859`: "Substituir o conteúdo" não muda, e nada foi trocado."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    escolher(client, destino, origem)
    corpo = client.post(
        reverse("interface:reaproveitar", args=[destino.id]),
        {"origem": str(origem.id), "chave_idempotencia": "troca-083"},
    ).content.decode()

    trilha = trilha_unica_no_cabecalho(corpo)
    niveis_em_ordem(
        trilha,
        [
            *ate_o_edital(destino),
            f'<a href="{reverse("interface:compor", args=[destino.id])}">Compor</a> ›',
            f'<a href="{reverse("interface:reaproveitar", args=[destino.id])}">'
            "Partir de um Edital anterior</a> ›",
        ],
    )
    termina_em(trilha, "Confirmar")
    assert comeca_pelo_titulo(corpo)
    assert '<button type="submit" class="botao perigoso">Substituir o conteúdo</button>' in corpo


# ---- o Edital publicado: Retificar, a Retificação e a Auditoria ------------------------------


@pytest.fixture
def publicado(api_client, manager_headers, process_payload):
    return publish_original(api_client, manager_headers, process_payload)


def criar_retificacao(client, edital):
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    client.post(
        reverse("interface:retificar", args=[edital.id]),
        {
            **campos(vigente, **{VAGAS: "9", LINHA_GERAL: "9"}),
            "justificativa": "Ampliação",
            "confirmar": "1",
        },
    )
    return Retificacao.objects.get(edital=edital)


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_na_retificacao_a_trilha_passa_pelo_processo_e_o_que_fazer_vem_primeiro(
    client, seletor_ligado, publicado
):
    """`FR-1850`, `FR-1851`, `FR-1852`, `SC-732`, `SC-733` em Retificar, no detalhe e na
    conferência de um ato; `FR-1857` no detalhe; `FR-1859` na conferência."""
    edital = publicado
    identificar(client, "ana.elaboradora", ["elaborador"])

    corpo = da_tela(client, "interface:retificar", edital.id)
    trilha = trilha_unica_no_cabecalho(corpo)
    niveis_em_ordem(trilha, ate_o_edital(edital))
    termina_em(trilha, "Retificar")
    assert comeca_pelo_titulo(corpo)
    na_secao_processos(corpo)

    retificacao = criar_retificacao(client, edital)
    corpo = da_tela(client, "interface:retificacao-detalhe", retificacao.id)
    trilha = trilha_unica_no_cabecalho(corpo)
    niveis_em_ordem(trilha, ate_o_edital(edital))
    termina_em(trilha, "Retificação")
    assert comeca_pelo_titulo(corpo)
    # Sob `/gestao/retificacoes/`, e a seção continua a da trilha.
    na_secao_processos(corpo)
    pagina = conteudo(corpo)
    acoes = pagina.index('<h2 id="acoes-titulo">O que fazer agora</h2>')
    assert acoes < pagina.index('<h2 id="vigencia-titulo">Vigência</h2>')
    assert pagina.index('<h2 id="vigencia-titulo">') < pagina.index('id="alteracoes-titulo"')
    # Pelo topo, como o detalhe do Edital: cada cartão com a altura do próprio conteúdo.
    assert '<div class="colunas ao-topo">' in pagina

    detalhe = reverse("interface:retificacao-detalhe", args=[retificacao.id])
    corpo = da_tela(client, "interface:retificacao-ato", retificacao.id, "submeter")
    trilha = trilha_unica_no_cabecalho(corpo)
    niveis_em_ordem(trilha, [*ate_o_edital(edital), f'<a href="{detalhe}">Retificação</a> ›'])
    assert trilha.rstrip().endswith("</span>")
    assert comeca_pelo_titulo(corpo)
    # O desenho, e não a grafia: o `{% if %}` vazio da classe deixa um espaço que não é desta regra.
    assert re.search(r'<button type="submit" class="botao\s*">\s*Confirmar:', corpo)
    assert f'<a href="{detalhe}" class="acao">Cancelar e voltar</a>' in corpo


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_em_retificar_a_recusa_vem_antes_de_como_funciona(client, seletor_ligado, publicado):
    """`FR-1856`: a recusa logo depois do título, com o mesmo papel e o mesmo foco."""
    edital = publicado
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    identificar(client, "ana.elaboradora", ["elaborador"])
    pagina = conteudo(
        client.post(
            reverse("interface:retificar", args=[edital.id]),
            {**campos(vigente), "justificativa": "Nada muda", "confirmar": "1"},
        ).content.decode()
    )

    recusa = pagina.index('<div class="erro" role="alert" tabindex="-1" autofocus>')
    assert pagina.index('<p class="sub">') < recusa < pagina.index("Como funciona.")
    assert "Nenhum campo foi alterado" in pagina


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_na_auditoria_do_edital_a_trilha_sobe_ao_cabecalho(client, seletor_ligado, publicado):
    """`FR-1850`, `FR-1851`, `FR-1852`: o modelo das três auditorias não tem mais trilha no
    conteúdo (D-002)."""
    identificar(client, "carlos", ["gestor", "auditor"])
    corpo = da_tela(client, "interface:auditoria", publicado.id)

    trilha = trilha_unica_no_cabecalho(corpo)
    niveis_em_ordem(trilha, ate_o_edital(publicado))
    termina_em(trilha, "Auditoria")
    assert comeca_pelo_titulo(corpo)


# ---- o marco: a Condução, a conferência, a Prévia de publicação e os Resultados divulgados ----


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload):
    """Edital publicado, marco classificatório e ato emitido — há o que divulgar."""
    return montar_ato_publicavel(
        gestor, api_client, manager_headers, process_payload, seed=93, codigo="0793"
    )


def classificacao(certame):
    return reverse("interface:ordenacao", args=[certame["edital"].id, certame["marco"]])


def ato_de_classificacao(certame):
    edital, marco, ato = certame["edital"], certame["marco"], certame["ato"]
    return reverse("interface:ato-de-ordenacao", args=[edital.id, marco, ato.id])


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_no_marco_a_trilha_passa_pelo_processo_e_a_conferencia_pelo_marco(
    client, seletor_ligado, certame
):
    """`FR-1850`, `FR-1851`, `FR-1852` na Condução e na conferência do gesto; `FR-1856`: o
    desfecho fica depois dos termos (D-007); `FR-1859`: o gesto confirmado não muda."""
    edital, marco = certame["edital"], certame["marco"]
    identificar(client, "carlos", ["gestor"])
    corpo = da_tela(client, "interface:marco", edital.id, marco)

    trilha = trilha_unica_no_cabecalho(corpo)
    niveis_em_ordem(trilha, ate_o_edital(edital))
    assert trilha.rstrip().endswith("</span>")
    assert comeca_pelo_titulo(corpo)

    gestos = re.findall(r'<form method="post" action="([^"]+)" class="conferencia">', corpo)
    conferiveis = [acao for acao in gestos if not acao.rstrip("/").endswith("publicar")]
    assert conferiveis, f"o cenário não oferece gesto além de publicar: {gestos}"
    gesto = conferiveis[0]
    conferencia = client.post(gesto, {}).content.decode()
    trilha = trilha_unica_no_cabecalho(conferencia)
    conducao = reverse("interface:marco", args=[edital.id, marco])
    niveis_em_ordem(trilha, [*ate_o_edital(edital), f'<a href="{conducao}">'])
    termina_em(trilha, "Conferir")
    assert comeca_pelo_titulo(conferencia)
    assert "<h1>Confira antes de confirmar</h1>" in conferencia


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_na_publicacao_o_nivel_da_classificacao_nomeia_e_so_abre_para_quem_alcanca(
    client, seletor_ligado, certame
):
    """`FR-1850`, `FR-1851`, `FR-1854` (D-003) na Prévia de publicação e nos Resultados
    divulgados; `FR-1859`: "Publicar este resultado" não muda."""
    edital, marco, ato = certame["edital"], certame["marco"], certame["ato"]

    identificar(client, "paula.publicadora", ["publicador"])
    previa = da_tela(client, "interface:previa-de-publicacao", edital.id, marco, ato.id)
    trilha = trilha_unica_no_cabecalho(previa)
    niveis_em_ordem(trilha, [*ate_o_edital(edital), "Ato de classificação ›"])
    assert ato_de_classificacao(certame) not in trilha
    termina_em(trilha, "Publicar resultado")
    assert comeca_pelo_titulo(previa)
    assert 'class="botao perigoso"' in previa and "Publicar este resultado</button>" in previa

    historico = da_tela(client, "interface:publicacoes-do-marco", edital.id, marco)
    trilha = trilha_unica_no_cabecalho(historico)
    niveis_em_ordem(trilha, [*ate_o_edital(edital), "Classificação ›"])
    assert classificacao(certame) not in trilha
    termina_em(trilha, "Resultados divulgados")
    assert comeca_pelo_titulo(historico)

    identificar(client, "maria", ["publicador"])
    previa = da_tela(client, "interface:previa-de-publicacao", edital.id, marco, ato.id)
    trilha = trilha_unica_no_cabecalho(previa)
    assert f'<a href="{ato_de_classificacao(certame)}">Ato de classificação</a> ›' in trilha
    historico = da_tela(client, "interface:publicacoes-do-marco", edital.id, marco)
    trilha = trilha_unica_no_cabecalho(historico)
    assert f'<a href="{classificacao(certame)}">Classificação</a> ›' in trilha


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
def test_na_previa_de_publicacao_a_recusa_vem_antes_da_frase_da_previa(
    client, seletor_ligado, certame
):
    """`FR-1856`: a recusa logo depois do título; o que acontece ao confirmar continua antes do
    formulário."""
    edital, marco, ato = certame["edital"], certame["marco"], certame["ato"]
    identificar(client, "paula.publicadora", ["publicador"])
    pagina = conteudo(
        client.post(
            reverse("interface:publicar-resultado", args=[edital.id, marco, ato.id]),
            {"chave_idempotencia": "recusa-083", "natureza": "nao-existe"},
        ).content.decode()
    )

    recusa = pagina.index('<p class="erro" role="alert" tabindex="-1" autofocus>')
    assert pagina.index('<p class="sub">') < recusa < pagina.index("Esta é uma <strong>prévia")
    assert pagina.index("O que acontece ao confirmar") < pagina.index('<form method="post"')
