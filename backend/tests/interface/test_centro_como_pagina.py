"""O Centro de Controle passa a ser a página do Edital (138).

**A rota escolhe a composição** (FR-4860): o Centro quando há andamento, o detalhe quando não. **O
ato volta com retorno** onde chega (FR-4865, FR-4866): cada um dos sete atos do conjunto do Edital,
praticado pela tela de confirmação, como quem clica. **Os endereços antigos continuam levando**
(FR-4863), e **a página anterior** fica por um ciclo, por um link só (FR-4873 a FR-4875).
"""

import re
from pathlib import Path

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.interface import andamento, atos
from processo_seletivo.processos.models import Edital
from tests.fixtures.andamento import certame_s1
from tests.fixtures.autoridades import registrar_unidade
from tests.fixtures.divulgacao import montar_ato_publicavel
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import compor_rascunho, identificar
from tests.interface.test_fluxo import EVENTOS, MARCOS, PERFIS, SIGNATARIO, praticar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

CENTRO = "interface/centro_do_edital.html"
DETALHE = "interface/detalhe.html"
TEMPLATES = Path(__file__).resolve().parents[2] / "processo_seletivo/interface/templates"


def desenhado(resposta):
    """O template da página, e não o dos parciais que ela inclui."""
    return resposta.templates[0].name


def chegada(client, resposta):
    """A página em que o ato chega, pelo redirecionamento que a tela do ato devolve."""
    assert resposta.status_code == 302, resposta.content
    assert resposta.url.startswith(reverse("interface:detalhe", args=[Edital.objects.get().id]))
    return client.get(resposta.url)


def retorno(ato):
    return f"Ato registrado: {atos.ATOS[ato].rotulo}."


@pytest.fixture
def cenario_de_divulgacao(gestor, api_client, manager_headers, process_payload):
    """Uma ordem emitida a divulgar, como a de `test_publicar_resultado.py`, com chaves próprias."""
    return montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=138,
        codigo="0138",
        pontuacoes=("90.0000", "70.0000", None),
        primeiro=1381,
    )


@pytest.fixture
def s1(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    return certame_s1(gestor, api_client, manager_headers, process_payload)


# ---------------------------------------------------------------------------------------------
# A escolha da composição
# ---------------------------------------------------------------------------------------------


def test_o_edital_publicado_abre_no_centro_sem_marca_de_validacao(client, s1):
    """FR-4860, FR-4867, FR-4868, SC-1522: o Centro na rota do Edital, com o caminho do Edital."""
    edital = s1["edital"]
    identificar(client, "carlos", ["gestor"])
    resposta = client.get(reverse("interface:detalhe", args=[edital.id]))

    assert resposta.status_code == 200
    assert desenhado(resposta) == CENTRO
    texto = resposta.content.decode()
    assert "Onde estamos" in texto
    assert "em validação" not in texto.lower() and "provisóri" not in texto.lower()
    nome = f"Edital {edital.number}/{edital.year}"
    assert f"<title>{nome}" in texto
    caminho = texto.split('class="caminho-da-secao"', 1)[1].split("</nav>", 1)[0]
    assert caminho.rstrip().endswith(f'<span aria-current="page">{nome}</span>')
    assert "Centro de Controle" not in caminho


def test_o_cancelado_abre_no_detalhe(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """FR-4860: o cancelado não tem andamento."""
    edital = publish_original(api_client, manager_headers, process_payload)
    Edital.objects.filter(pk=edital.pk).update(status=Edital.Status.CANCELADO)
    identificar(client, "carlos", ["gestor"])

    resposta = client.get(reverse("interface:detalhe", args=[edital.id]))
    assert desenhado(resposta) == DETALHE
    assert "Abrir o Centro de Controle" not in resposta.content.decode()


def test_a_derivacao_indisponivel_abre_no_detalhe(client, s1, monkeypatch):
    """FR-4860, caso-limite: a orientação que falha não derruba a página."""

    def falha(*args, **kwargs):
        raise RuntimeError("derivação indisponível")

    monkeypatch.setattr(andamento._Leitor, "andamento", falha)
    identificar(client, "carlos", ["gestor"])

    resposta = client.get(reverse("interface:detalhe", args=[s1["edital"].id]))
    assert resposta.status_code == 200
    assert desenhado(resposta) == DETALHE


def test_a_leitura_do_andamento_e_uma_so(client, s1, monkeypatch):
    """FR-4861: a rota lê o andamento uma vez para decidir e desenhar."""
    chamadas = []
    original = andamento.do_edital

    def contando(*args, **kwargs):
        chamadas.append(1)
        return original(*args, **kwargs)

    monkeypatch.setattr(andamento, "do_edital", contando)
    identificar(client, "carlos", ["gestor"])
    client.get(reverse("interface:detalhe", args=[s1["edital"].id]))
    assert len(chamadas) == 1


# ---------------------------------------------------------------------------------------------
# O retorno dos sete atos
# ---------------------------------------------------------------------------------------------


def test_os_sete_atos_do_edital_mostram_o_retorno_onde_chegam(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """FR-4865, FR-4866, SC-1521, US2: antes da publicação e no cancelado, o detalhe; publicar e
    encerrar, o Centro — com o mesmo "Ato registrado" e, depois de publicar, a conferência da
    116."""
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    vistos = {}

    def confere(ato, papel, pagina, **campos):
        identificar(client, papel.replace("ador", "") + ".teste", [papel])
        resposta = chegada(client, praticar(client, Edital.objects.get(), ato, **campos)[0])
        assert resposta.status_code == 200
        assert desenhado(resposta) == pagina, ato
        assert retorno(ato) in resposta.content.decode(), ato
        vistos[ato] = resposta
        return resposta

    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, Edital.objects.get(), PERFIS, EVENTOS, marcos=MARCOS)
    confere("submeter", "elaborador", DETALHE)
    confere("devolver", "homologador", DETALHE, motivo="Falta conferir o cronograma")
    confere("submeter", "elaborador", DETALHE)
    confere("homologar", "homologador", DETALHE, motivo="Conferido")
    confere("revogar-homologacao", "homologador", DETALHE, motivo="Rever o cronograma")
    confere("homologar", "homologador", DETALHE, motivo="Conferido de novo")
    publicado = confere("publicar", "publicador", CENTRO, **SIGNATARIO)
    # A conferência do concurso na Caixa (116, FR-3646): o que ela disse no ato, também no Centro.
    assert publicado.context["conferencia_do_ato"]
    assert 'class="conferencia-do-ato"' in publicado.content.decode()
    confere("encerrar", "gestor", CENTRO, motivo="Etapas concluídas")
    # O cancelamento parte do publicado, e o encerrado não se cancela: o caso seguinte.
    assert set(vistos) == set(atos.ATOS) - {"cancelar"}


def test_cancelar_chega_ao_detalhe_com_o_retorno(
    client, seletor_ligado, api_client, manager_headers, process_payload
):
    """FR-4866: o sétimo ato. O cancelado não tem andamento, e o retorno é o do detalhe."""
    edital = publish_original(api_client, manager_headers, process_payload)
    identificar(client, "gabi.gestora", ["gestor"])
    resposta, _ = praticar(client, edital, "cancelar", motivo="Interrompido pela comissão")
    assert resposta.status_code == 302, resposta.content
    pagina = client.get(resposta.url)
    assert desenhado(pagina) == DETALHE
    assert retorno("cancelar") in pagina.content.decode()


# ---------------------------------------------------------------------------------------------
# O endereço do Centro
# ---------------------------------------------------------------------------------------------


def test_o_endereco_do_centro_leva_a_pagina_do_edital_com_a_mesma_consulta(client, s1):
    """FR-4863, SC-1523: um redirecionamento, com os parâmetros."""
    edital = s1["edital"]
    identificar(client, "carlos", ["gestor"])
    pagina = reverse("interface:detalhe", args=[edital.id])
    centro = reverse("interface:centro-do-edital", args=[edital.id])

    assert client.get(centro).url == pagina
    resposta = client.get(centro + "?fase=classificacao&ato=publicar")
    assert resposta.status_code == 302
    assert resposta.url == pagina + "?fase=classificacao&ato=publicar"
    final = client.get(resposta.url)
    assert desenhado(final) == CENTRO
    assert final.context["fase"].chave == "classificacao"


def test_o_endereco_do_centro_nao_tem_porta_propria(client, s1):
    """D-003: a resposta é a mesma para qualquer identificador; o 404 é o da página do Edital."""
    registrar_unidade("campus-138")
    identificar(client, "carlos", ["gestor"], escopo="campus-138")
    resposta = client.get(reverse("interface:centro-do-edital", args=[s1["edital"].id]))

    assert resposta.status_code == 302
    assert client.get(resposta.url).status_code == 404


# ---------------------------------------------------------------------------------------------
# A página anterior
# ---------------------------------------------------------------------------------------------


def test_a_pagina_anterior_e_o_detalhe_com_o_caminho_de_volta(client, s1):
    """FR-4873, FR-4875, SC-1525."""
    edital = s1["edital"]
    identificar(client, "carlos", ["gestor"])
    resposta = client.get(reverse("interface:pagina-anterior", args=[edital.id]))

    assert resposta.status_code == 200
    assert desenhado(resposta) == DETALHE
    texto = resposta.content.decode()
    caminho = texto.split('class="caminho-da-secao"', 1)[1].split("</nav>", 1)[0]
    pagina = reverse("interface:detalhe", args=[edital.id])
    assert f'<a href="{pagina}">Edital {edital.number}/{edital.year}</a>' in caminho
    assert caminho.rstrip().endswith('<span aria-current="page">Página anterior</span>')
    # O detalhe de antes: o andamento da seleção e "Quem atuou" continuam lá.
    assert 'id="participantes-titulo"' in texto


def test_a_pagina_anterior_tem_a_porta_do_edital(client, s1):
    """FR-4873: o mesmo 404 e a mesma identificação."""
    url = reverse("interface:pagina-anterior", args=[s1["edital"].id])
    assert reverse("interface:identificar") in client.get(url).url

    registrar_unidade("campus-138")
    identificar(client, "carlos", ["gestor"], escopo="campus-138")
    assert client.get(url).status_code == 404


def test_um_link_so_leva_a_pagina_anterior(client, s1):
    """FR-4874, UX-345: um link, no fim da administração do Centro, e nenhum outro template."""
    edital = s1["edital"]
    identificar(client, "carlos", ["gestor"])
    texto = client.get(reverse("interface:detalhe", args=[edital.id])).content.decode()

    anterior = reverse("interface:pagina-anterior", args=[edital.id])
    assert texto.count(anterior) == 1
    administracao = texto.split('id="administracao"', 1)[1]
    assert anterior in administracao
    paragrafo = administracao.split(anterior, 1)[0].rsplit("<p", 1)[1]
    assert 'class="cc-fraco cc-pagina-anterior"' in paragrafo
    assert "botao" not in paragrafo and "acao" not in paragrafo

    quem_cita = sorted(
        str(p.relative_to(TEMPLATES))
        for p in TEMPLATES.rglob("*.html")
        if "pagina-anterior" in p.read_text()
    )
    assert quem_cita == ["interface/centro_do_edital.html"]


# ---------------------------------------------------------------------------------------------
# O que só o detalhe oferecia
# ---------------------------------------------------------------------------------------------


def test_o_centro_oferece_o_que_so_o_detalhe_oferecia(client, s1):
    """FR-4871, FR-4872, D-005: dúvidas, o aviso de conteúdo imutável e as datas de "Quem atuou"."""
    edital = s1["edital"]
    identificar(client, "carlos", ["gestor"])
    resposta = client.get(reverse("interface:detalhe", args=[edital.id]))
    texto = resposta.content.decode()
    administracao = texto.split('id="administracao"', 1)[1]

    assert reverse("interface:duvidas", args=[edital.id]) in administracao
    assert reverse("interface:assistente", args=[edital.id]) not in administracao
    assert "<strong>Conteúdo imutável.</strong>" in administracao
    assert "Autoridade, unidade e datas" not in texto
    # **No fuso da aplicação**, como o template a mostra. O instante vem em UTC, e formatá-lo cru dá
    # o dia seguinte entre 21h e meia-noite de Brasília — a falha do CI do #460, às 00:15 UTC.
    publicou_em = timezone.localtime(resposta.context["participantes"]["publicou_em"])
    assert publicou_em.strftime("%d/%m/%Y") in administracao.split("<h3>Quem atuou</h3>", 1)[1]


def test_o_imutavel_cala_a_conducao_para_quem_pode_retificar(client, s1):
    """FR-4871: a condução da 037 é a mesma do detalhe — some para quem recebe `Retificar`."""
    url = reverse("interface:detalhe", args=[s1["edital"].id])
    identificar(client, "carlos", ["gestor"])
    sem = client.get(url).context["conducao_do_imutavel"]
    identificar(client, "elisa", ["elaborador"])
    com = client.get(url).context["conducao_do_imutavel"]

    assert {sem, com} != {""} and "" in {sem, com}


# ---------------------------------------------------------------------------------------------
# A revisão do PR #451
# ---------------------------------------------------------------------------------------------


def test_quem_so_divulga_chega_ao_marco_pelo_centro(client, seletor_ligado, cenario_de_divulgacao):
    """FR-4108 da 127, `ACH-40`: quem só tem `resultado:publicar` não vê a matriz, e no detalhe
    chegava ao marco pelos destinos fora dela. No Centro, os mesmos destinos, em "Telas dos
    marcos"."""
    edital = cenario_de_divulgacao["edital"]
    identificar(client, "paula.publicadora", ["publicador"])

    anterior = client.get(reverse("interface:pagina-anterior", args=[edital.id])).content.decode()
    lista = anterior.split('<ul class="destinos-do-perfil">', 1)[1].split("</ul>", 1)[0]
    destinos = re.findall(r'<a href="([^"]+)"', lista)
    assert destinos, "o detalhe deixou de oferecer destino a quem divulga"

    pagina = client.get(reverse("interface:detalhe", args=[edital.id]) + "?fase=classificacao")
    assert desenhado(pagina) == CENTRO
    assert not pagina.context["andamento"].ve_a_matriz
    texto = pagina.content.decode()
    secao = texto.split('aria-labelledby="telas-dos-marcos-titulo"', 1)[1].split("</section>", 1)[0]
    assert all(f'href="{url}"' in secao for url in destinos), (destinos, secao)
    # A nota da fase consultada não remete mais à "página atual", que agora é o próprio Centro.
    assert "página atual" not in texto


def test_quem_ve_a_matriz_le_os_destinos_em_onde_cada_lista_esta(client, s1):
    """A seção nova é só de quem não vê a matriz: os demais leem "Telas do marco" na matriz."""
    identificar(client, "carlos", ["gestor"])
    pagina = client.get(reverse("interface:detalhe", args=[s1["edital"].id]))

    assert pagina.context["andamento"].ve_a_matriz
    assert "telas-dos-marcos-titulo" not in pagina.content.decode()


def test_a_atencao_das_etapas_sem_efeito_aparece_no_centro(client, s1):
    """FR-4087 da 127: a "Atenção" que o detalhe mostrava, em "O que fazer agora"."""
    identificar(client, "carlos", ["gestor"])
    texto = client.get(reverse("interface:detalhe", args=[s1["edital"].id])).content.decode()

    agora = texto.split('id="agora-titulo"', 1)[1].split("</section>", 1)[0]
    assert (
        '<p class="atencao-do-andamento"><strong>Atenção:</strong> Análise documental e Prova '
        "didática estão declaradas" in agora
    )
