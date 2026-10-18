"""As telas dos avisos aos candidatos, quinto grupo da etapa 4 (086).

Nas seis telas dos avisos a trilha mora no cabeçalho de contexto, e só lá: as quatro de um
Edital passam pelo Processo, como o detalhe do Edital; a prévia diz a porta por onde se chegou; e
os modelos começam na seção da barra. Os estados vazios, o rodapé dos formulários e a faixa de
ações são os comuns. O desenho em si é provado no navegador e pelo inventário visual refeito
(quickstart): aqui fica o que a marcação garante.
"""

import re

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.avisos.application.modelos import criar
from processo_seletivo.avisos.domain import nomes
from tests.fixtures.avisos import PUBLICADORA, avisar_resultado
from tests.fixtures.divulgacao import montar_ato_publicavel, publicar_o_ato
from tests.integration.avisos.test_aviso_da_chamada import (  # noqa: F401 — fixture
    chamada_publicada,
)
from tests.interface.conftest import identificar
from tests.interface.test_telas_da_presidencia import (
    ate_o_processo,
    comeca_pelo_titulo,
    niveis_em_ordem,
)
from tests.interface.test_telas_de_uso_diario import cabecalho, conteudo, trilha_unica_no_cabecalho

TEMPLATES_DOS_AVISOS = (
    "avisos_do_edital.html",
    "aviso.html",
    "aviso_previa.html",
    "aviso_interromper.html",
    "modelos_de_aviso.html",
    "modelo_de_aviso.html",
)


@pytest.fixture(autouse=True)
def _seletor(seletor_ligado):
    """Sem o seletor de identidade, `/gestao/` devolve 503 antes de qualquer autorização."""


@pytest.fixture
def publicado(gestor, api_client, manager_headers, process_payload):
    cenario = montar_ato_publicavel(
        gestor, api_client, manager_headers, process_payload, pontuacoes=("90.0000", "70.0000")
    )
    cenario["publicacao"] = publicar_o_ato(cenario)
    cenario["processo"] = cenario["edital"].processo
    return cenario


def ate_o_edital(edital):
    return [
        *ate_o_processo(edital.processo),
        f'<a href="{reverse("interface:detalhe", args=[edital.id])}">'
        f"Edital {edital.number}/{edital.year}</a> ›",
    ]


def ate_os_avisos(edital):
    return [
        *ate_o_edital(edital),
        f'<a href="{reverse("interface:avisos-do-edital", args=[edital.id])}">'
        "Avisos aos candidatos</a> ›",
    ]


def ate_o_aviso(edital, aviso_id, solicitado_em):
    return [
        *ate_os_avisos(edital),
        f'<a href="{reverse("interface:aviso", args=[aviso_id])}">'
        f"Aviso de {timezone.localtime(solicitado_em):%d/%m/%Y}</a> ›",
    ]


def abrir_url(client, url):
    resposta = client.get(url)
    assert resposta.status_code == 200, url
    return resposta.content.decode()


def termina_em(trilha, atual):
    assert trilha.rstrip().endswith(f'<span aria-current="page">{atual}</span>'), trilha


def links_da_trilha(trilha):
    return re.findall(r'<a href="([^"]+)">([^<]+)</a>', trilha)


def _aviso(cenario):
    from processo_seletivo.avisos.models import Aviso

    declarado = avisar_resultado(cenario["edital"], cenario["publicacao"].marco_id)
    return Aviso.objects.get(pk=declarado["aviso"])


def _url_da_previa(cenario):
    return (
        reverse(
            "interface:aviso-do-resultado",
            args=[cenario["edital"].id, cenario["publicacao"].marco_id],
        )
        + f"?natureza={nomes.PRELIMINAR}"
    )


# ---- a trilha no cabeçalho: as telas de um Edital ---------------------------------------------


@pytest.mark.django_db
@pytest.mark.integration
def test_nos_avisos_do_edital_a_trilha_passa_pelo_processo(client, publicado):
    """`FR-1940`, `FR-1941`, `FR-1945`, `SC-762`, `SC-763`: GPS › Processos Seletivos › código ›
    Edital › Avisos aos candidatos, uma vez só, e o conteúdo começa pelo título."""
    identificar(client, "publicadora", ["publicador"])
    corpo = abrir_url(client, reverse("interface:avisos-do-edital", args=[publicado["edital"].id]))

    trilha = trilha_unica_no_cabecalho(corpo)
    niveis_em_ordem(trilha, ate_o_edital(publicado["edital"]))
    termina_em(trilha, "Avisos aos candidatos")
    assert comeca_pelo_titulo(corpo)
    # A seção é a do endereço: a barra e a trilha dizem a mesma coisa.
    assert f'<a href="{reverse("interface:lista")}" aria-current="true">' in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_no_aviso_e_na_interrupcao_a_trilha_passa_pelos_avisos(client, publicado):
    """`FR-1941`: o histórico pende dos Avisos aos candidatos, e a interrupção, do aviso — que a
    trilha de antes saltava."""
    aviso = _aviso(publicado)
    edital = publicado["edital"]
    identificar(client, "publicadora", ["publicador"])

    historico = abrir_url(client, reverse("interface:aviso", args=[aviso.id]))
    trilha = trilha_unica_no_cabecalho(historico)
    niveis_em_ordem(trilha, ate_os_avisos(edital))
    termina_em(trilha, f"Aviso de {timezone.localtime(aviso.solicitado_em):%d/%m/%Y}")
    assert comeca_pelo_titulo(historico)

    interromper = abrir_url(client, reverse("interface:aviso-interromper", args=[aviso.id]))
    trilha = trilha_unica_no_cabecalho(interromper)
    niveis_em_ordem(trilha, ate_o_aviso(edital, aviso.id, aviso.solicitado_em))
    termina_em(trilha, "Interromper")
    assert comeca_pelo_titulo(interromper)


@pytest.mark.django_db
@pytest.mark.integration
def test_a_interrupcao_recusada_tem_a_mesma_trilha_e_o_erro_abaixo_do_titulo(client, publicado):
    """`FR-1941`, `FR-1949`: o erro logo abaixo do título, com o foco nele; os botões no rodapé."""
    aviso = _aviso(publicado)
    identificar(client, "publicadora", ["publicador"])
    url = reverse("interface:aviso-interromper", args=[aviso.id])
    resposta = client.post(url, {"motivo": "", "chave": "interromper-086"})
    corpo = resposta.content.decode()

    assert resposta.status_code >= 400
    termina_em(trilha_unica_no_cabecalho(corpo), "Interromper")
    pagina = conteudo(corpo)
    erro = pagina.index('<p class="erro" role="alert" tabindex="-1" autofocus>')
    assert pagina.index('<p class="sub">') < erro < pagina.index("titulo-consequencias")
    rodape = pagina.split('<p class="salvar">')[1].split("</p>")[0]
    assert '<button type="submit" class="botao perigoso">Interromper o envio</button>' in rodape
    assert ">Voltar sem interromper</a>" in rodape
    assert rodape.index("Interromper o envio") < rodape.index("Voltar sem interromper")


# ---- a prévia diz a porta ---------------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.integration
def test_a_previa_do_resultado_pende_dos_avisos_do_edital(client, publicado):
    """`FR-1942`, `FR-1951`: o nível acima é a lista dos avisos; a frase de que é uma prévia
    continua a primeira coisa depois do título, e o envio continua depois das consequências."""
    identificar(client, "publicadora", ["publicador"])
    corpo = abrir_url(client, _url_da_previa(publicado))

    trilha = trilha_unica_no_cabecalho(corpo)
    niveis_em_ordem(trilha, ate_os_avisos(publicado["edital"]))
    termina_em(trilha, "Avisar candidatos")
    assert comeca_pelo_titulo(corpo)
    pagina = conteudo(corpo)
    assert pagina.index('<p class="sub">') < pagina.index('<p class="imutavel">Esta é uma')
    assert pagina.index('<p class="imutavel">') < pagina.index(
        '<section aria-labelledby="titulo-quem">'
    )
    assert pagina.index("titulo-consequencias") < pagina.index('class="botao perigoso"')


@pytest.mark.django_db
@pytest.mark.integration
def test_a_previa_recusada_mantem_a_trilha_e_o_erro_depois_da_frase_da_previa(client, publicado):
    """Caso-limite e D-003: recusada a confirmação, a prévia volta com a mesma trilha, e o erro vem
    logo depois da frase de que é uma prévia — antes de tudo o mais —, com o foco nele."""
    identificar(client, "publicadora", ["publicador"])
    resposta = client.post(
        _url_da_previa(publicado),
        {
            "acao": "confirmar",
            "natureza": nomes.PRELIMINAR,
            "assinatura": "assinatura-vencida",
            "chave": "previa-recusada-086",
            "assunto": "Processo Seletivo Ifes — Nova publicação disponível",
            "corpo": "Olá, {nome_do_candidato}. Saiu o resultado: {area_do_candidato}",
        },
    )
    corpo = resposta.content.decode()

    assert resposta.status_code >= 400
    trilha = trilha_unica_no_cabecalho(corpo)
    niveis_em_ordem(trilha, ate_os_avisos(publicado["edital"]))
    termina_em(trilha, "Avisar candidatos")
    pagina = conteudo(corpo)
    erro = pagina.index('<p class="erro" role="alert" tabindex="-1" autofocus>')
    assert pagina.index('<p class="imutavel">Esta é uma') < erro
    assert erro < pagina.index('<section aria-labelledby="titulo-quem">')


@pytest.mark.django_db
@pytest.mark.integration
def test_a_previa_do_reenvio_pende_do_aviso_anterior(client, publicado, settings):
    """`FR-1942`, `FR-1943`, `SC-763`: a lista e o aviso anterior, cada um com o seu nome — antes,
    "Avisos aos candidatos" levava ao aviso anterior."""
    from processo_seletivo.avisos.application.despacho import despachar
    from tests.fixtures import correio

    aviso = _aviso(publicado)
    correio.usar(settings, correio.recusa(550), correio.recusa(550))
    despachar()
    identificar(client, "publicadora", ["publicador"])
    corpo = abrir_url(
        client,
        reverse("interface:aviso-reenviar", args=[aviso.id]) + f"?motivo={nomes.REENVIO_DE_FALHAS}",
    )

    trilha = trilha_unica_no_cabecalho(corpo)
    niveis_em_ordem(trilha, ate_o_aviso(publicado["edital"], aviso.id, aviso.solicitado_em))
    termina_em(trilha, "Avisar candidatos")


@pytest.mark.django_db
@pytest.mark.integration
def test_todo_link_da_trilha_leva_aonde_diz(client, publicado, settings):
    """`FR-1943`: nas telas de um Edital, cada rótulo de trilha leva a uma tela só, e o mesmo
    rótulo nunca a duas."""
    from processo_seletivo.avisos.application.despacho import despachar
    from tests.fixtures import correio

    aviso = _aviso(publicado)
    correio.usar(settings, correio.recusa(550), correio.recusa(550))
    despachar()
    identificar(client, "publicadora", ["publicador"])
    edital = publicado["edital"]
    urls = [
        reverse("interface:avisos-do-edital", args=[edital.id]),
        reverse("interface:aviso", args=[aviso.id]),
        reverse("interface:aviso-interromper", args=[aviso.id]),
        _url_da_previa(publicado),
        reverse("interface:aviso-reenviar", args=[aviso.id]) + f"?motivo={nomes.REENVIO_DE_FALHAS}",
    ]
    destino_por_rotulo = {}
    for url in urls:
        for destino, rotulo in links_da_trilha(trilha_unica_no_cabecalho(abrir_url(client, url))):
            destino_por_rotulo.setdefault(rotulo, set()).add(destino)

    assert destino_por_rotulo["Avisos aos candidatos"] == {
        reverse("interface:avisos-do-edital", args=[edital.id])
    }
    assert all(len(destinos) == 1 for destinos in destino_por_rotulo.values()), destino_por_rotulo


@pytest.mark.django_db
@pytest.mark.integration
def test_quem_so_consulta_le_a_mesma_trilha_de_quem_avisa(client, publicado):
    """`FR-1946`: nenhum nível aparece, some ou deixa de ser link conforme quem lê."""
    aviso = _aviso(publicado)
    for url in (
        reverse("interface:avisos-do-edital", args=[publicado["edital"].id]),
        reverse("interface:aviso", args=[aviso.id]),
    ):
        identificar(client, "publicadora", ["publicador"])
        de_quem_avisa = trilha_unica_no_cabecalho(abrir_url(client, url))
        identificar(client, "auditora", ["auditor"])
        de_quem_consulta = trilha_unica_no_cabecalho(abrir_url(client, url))
        assert de_quem_consulta == de_quem_avisa, url


@pytest.mark.integration
@pytest.mark.django_db
def test_a_previa_da_chamada_pende_da_convocacao_e_o_reenvio_do_aviso(
    chamada_publicada,  # noqa: F811
    gestor,
    client,
):
    """`FR-1942`, `FR-1943`: pela Convocação, a Convocação no mesmo recorte de "Cancelar"; no
    reenvio de um aviso de chamada, o aviso anterior vence a origem — "Convocação" não leva ao
    aviso."""
    from processo_seletivo.avisos.application.interromper import interromper
    from processo_seletivo.avisos.models import Aviso
    from tests.fixtures.avisos import avisar_chamada
    from tests.fixtures.corte import MARCO

    edital, _, _, ancora = chamada_publicada
    identificar(client, "gestora", ["gestor"])
    url = (
        reverse("interface:aviso-da-chamada", args=[edital.id, MARCO]) + f"?comunicacao={ancora.id}"
    )
    corpo = abrir_url(client, url)
    convocacao = reverse("interface:convocacao", args=[edital.id, MARCO])

    trilha = trilha_unica_no_cabecalho(corpo)
    niveis_em_ordem(trilha, [*ate_o_edital(edital), f'<a href="{convocacao}">Convocação</a> ›'])
    termina_em(trilha, "Avisar candidatos")
    assert f'<a class="botao secundario" href="{convocacao}">Cancelar</a>' in conteudo(corpo)

    aviso = Aviso.objects.get(
        pk=avisar_chamada(edital, MARCO, ancora.id, ator=gestor, agora=timezone.now())["aviso"]
    )
    interromper(
        actor=gestor,
        aviso_id=aviso.id,
        motivo="Texto errado.",
        idempotency_key="interromper-086",
        correlation_id="teste-086",
    )
    reenvio = abrir_url(
        client,
        reverse("interface:aviso-reenviar", args=[aviso.id])
        + f"?motivo={nomes.REENVIO_JUSTIFICADO}",
    )
    trilha = trilha_unica_no_cabecalho(reenvio)
    niveis_em_ordem(trilha, ate_o_aviso(edital, aviso.id, aviso.solicitado_em))
    assert ">Convocação</a>" not in trilha


# ---- os modelos ------------------------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.integration
def test_nos_modelos_a_trilha_comeca_na_secao_da_barra(client):
    """`FR-1944`, `FR-1950`, `SC-763`: a lista é a raiz da seção, sem link e sem "Processos
    Seletivos"; "Novo modelo" na faixa de ações."""
    identificar(client, "publicadora", ["publicador"])
    corpo = abrir_url(client, reverse("interface:modelos-de-aviso"))

    trilha = trilha_unica_no_cabecalho(corpo)
    termina_em(trilha, "Modelos de aviso")
    assert "<a " not in trilha
    assert ">Processos Seletivos</a>" not in cabecalho(corpo)
    assert comeca_pelo_titulo(corpo)
    assert f'<a href="{reverse("interface:modelos-de-aviso")}" aria-current="page">' in corpo
    faixa = conteudo(corpo).split('<p class="acoes-do-painel">')[1].split("</p>")[0]
    assert (
        f'<a class="botao" href="{reverse("interface:modelo-de-aviso-novo")}">Novo modelo</a>'
        in faixa
    )
    assert '<p class="vazio">A unidade ainda não tem modelos de aviso.</p>' in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_no_modelo_a_trilha_volta_aos_modelos(client):
    """`FR-1944`, `FR-1949`: a seção como link e o modelo — ou "Novo modelo" — como página atual;
    os botões no rodapé do formulário, como antes."""
    modelo = criar(actor=PUBLICADORA, nome="Meu modelo", assunto="Assunto", corpo="Texto.")
    identificar(client, "publicadora", ["publicador"])
    secao = f'<a href="{reverse("interface:modelos-de-aviso")}">Modelos de aviso</a> ›'

    for url, atual in (
        (reverse("interface:modelo-de-aviso", args=[modelo.id]), "Meu modelo"),
        (reverse("interface:modelo-de-aviso-novo"), "Novo modelo"),
    ):
        corpo = abrir_url(client, url)
        trilha = trilha_unica_no_cabecalho(corpo)
        assert secao in trilha
        termina_em(trilha, atual)
        assert ">Processos Seletivos</a>" not in cabecalho(corpo)
        assert comeca_pelo_titulo(corpo)
        rodape = conteudo(corpo).split('<p class="salvar">')[1].split("</p>")[0]
        assert '<button type="submit" class="botao">Salvar o modelo</button>' in rodape
        assert ">Cancelar</a>" in rodape


@pytest.mark.django_db
@pytest.mark.integration
def test_o_modelo_recusado_termina_em_novo_modelo(client):
    """Caso-limite: o erro abaixo do título, e a trilha a do modelo novo."""
    identificar(client, "publicadora", ["publicador"])
    resposta = client.post(
        reverse("interface:modelo-de-aviso-novo"),
        {"nome": "Ruim", "assunto": "Assunto", "corpo": "Sua posição é {posicao}."},
    )
    corpo = resposta.content.decode()

    assert resposta.status_code == 422
    termina_em(trilha_unica_no_cabecalho(corpo), "Novo modelo")
    pagina = conteudo(corpo)
    assert (
        pagina.index("<h1>") < pagina.index('<p class="erro" role="alert"') < pagina.index("<form")
    )


# ---- o estado vazio ---------------------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.integration
def test_os_avisos_do_edital_vazios_tem_o_estado_vazio_comum(
    client, gestor, api_client, manager_headers, process_payload
):
    """`FR-1948`: sem resultado publicado e sem aviso, as duas frases no desenho comum."""
    cenario = montar_ato_publicavel(
        gestor, api_client, manager_headers, process_payload, pontuacoes=("90.0000",)
    )
    identificar(client, "publicadora", ["publicador"])
    pagina = conteudo(
        abrir_url(client, reverse("interface:avisos-do-edital", args=[cenario["edital"].id]))
    )

    assert '<p class="vazio">Nenhum resultado foi publicado neste Edital ainda.</p>' in pagina
    assert '<p class="vazio">Nenhum aviso foi confirmado neste Edital.</p>' in pagina
    assert 'class="nenhuma"' not in pagina


# ---- o que não muda ---------------------------------------------------------------------------


def test_as_acoes_que_nao_se_desfazem_nao_mudam_de_desenho():
    """`FR-1951`: o perigo continua perigo, e as demais ações com o desenho de antes (D-005)."""
    from tests.interface.test_polish_da_055 import GESTAO

    esperados = {
        "aviso_previa.html": [
            'class="botao perigoso"{% if not contagens.com_endereco or previa.erro %} disabled'
            "{% endif %}>Enviar a {{ contagens.com_endereco }} pessoa",
            '<button type="submit" class="botao secundario">Usar este modelo</button>',
            'value="previa" class="botao secundario">Atualizar a prévia</button>',
            'value="previa" class="acao">Ver a mensagem de outra pessoa</button>',
        ],
        "aviso.html": [
            '<a class="botao perigoso" href="{% url \'interface:aviso-interromper\' aviso.id %}">'
            "Interromper o envio</a>",
        ],
        "aviso_interromper.html": [
            '<button type="submit" class="botao perigoso">Interromper o envio</button>',
        ],
        "avisos_do_edital.html": ['<a class="acao" href="{% url \'interface:aviso-do-resultado\''],
        "modelos_de_aviso.html": ['<button type="submit" class="acao">{% if modelo.ativo %}'],
    }
    for template, trechos in esperados.items():
        corpo = (GESTAO / template).read_text()
        for trecho in trechos:
            assert corpo.count(trecho) == 1, (template, trecho)


def test_nenhuma_das_seis_tem_trilha_no_conteudo():
    """`FR-1945`: a trilha de cada uma está no bloco do cabeçalho, e o conteúdo não tem outra."""
    from tests.interface.test_polish_da_055 import GESTAO

    for template in TEMPLATES_DOS_AVISOS:
        corpo = (GESTAO / template).read_text()
        assert corpo.count('aria-label="Trilha de navegação"') == 1, template
        assert 'class="trilha"' not in corpo, template
        assert "{% block caminho_do_contexto %}" in corpo, template
