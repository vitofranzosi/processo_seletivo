"""A entrega documental à formalização de ponta a ponta, num navegador de verdade (117).

Como as jornadas da `115`, em três partes: a **preparação** pelas *fixtures* (o certame, os aptos, a
designação); as **ações** só no navegador; as **verificações** na tela, no ZIP baixado e no banco.

- **Cenário A** — a presidência define os documentos; o setor verifica todos os aptos, lê *completo*
  e baixa o pacote.
- **Cenário E** — o controle de acesso pelas URLs: fora do Perfil, sem designação, outra base.
- **Cenário F** — a verificação **parcial antes do download**: o arquivo ausente e o divergente são
  nomeados na tela, e o ZIP baixado é o `-parcial` com as três pessoas verificadas.

Nenhuma página pode ter violação da política de conteúdo no console, e nenhuma rola na horizontal a
375 px (FR-3680). `NAVEGADOR_CAPTURAS=<pasta>` grava as telas de cada passo marcado, a 1280 e a 375.
"""

import zipfile

import pytest

expect = pytest.importorskip("playwright.sync_api", reason="sem o grupo opcional navegador").expect

from processo_seletivo.formalizacao.application import definir  # noqa: E402
from processo_seletivo.formalizacao.models import ExportacaoDeFormalizacao  # noqa: E402
from tests.fixtures.documentos_da_convocacao import CERTIDAO, HISTORICO, IDENTIDADE  # noqa: E402
from tests.fixtures.formalizacao import (  # noqa: E402
    CERTIFICADO_DO_CURSO,
    TITULOS,
    definir_documentos,
    designar_direto,
    montar_cenario_da_formalizacao,
)
from tests.integration.formalizacao.apoio import adulterar, apagar, documentos_de  # noqa: E402
from tests.navegador.test_jornada_dos_documentos_da_convocacao import (  # noqa: E402
    CELULAR,
    Tela,
    sem_rolagem_horizontal,
)

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def tela(navegador, live_server, settings, request, raiz_de_arquivos):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    atual = Tela(navegador, live_server, request.node.name)
    yield atual
    atual.fechar()
    assert atual.violacoes == [], "violação da política de conteúdo no console"


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    return montar_cenario_da_formalizacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        aptas=5,
        indeferidas=1,
        sem_resposta=1,
        prefixo="navegador-117",
    )


def _url(tela, nome, *args):
    from django.urls import reverse

    return tela.servidor.url + reverse(nome, args=args)


def _nas_duas_larguras(tela, subject, papeis, url, rotulo):
    """A mesma tela a 1280 px e a 375 px: capturada nas duas, sem rolagem horizontal na estreita."""
    for viewport, sufixo in ((None, "1280"), (CELULAR, "375")):
        pagina = tela.gestao(subject, papeis, **({"viewport": viewport} if viewport else {}))
        pagina.goto(url)
        sem_rolagem_horizontal(pagina)
        tela.capturar(pagina, f"{rotulo}-{sufixo}")


def _verificar_todos(pagina):
    pagina.get_by_role("button", name="Verificar e exportar todos os aptos").click()
    pagina.wait_for_load_state()
    expect(pagina.get_by_role("heading", name="Verificação da exportação")).to_be_visible()


def _baixar(pagina, rotulo, destino):
    with pagina.expect_download() as baixado:
        pagina.get_by_role("button", name=rotulo).click()
    arquivo = baixado.value
    caminho = destino / arquivo.suggested_filename
    arquivo.save_as(caminho)
    return caminho


def test_cenario_a_define_verifica_completo_e_baixa(tela, certame, tmp_path):
    edital = certame.edital
    designar_direto(edital, "rui")

    # A presidência define, na condução: a lista começa sem marcação, e o aviso da inscrição está
    # ao lado dos documentos pedidos na inscrição.
    ana = tela.gestao("maria")
    ana.goto(_url(tela, "interface:formalizacao-definicao", edital.id))
    expect(ana.get_by_role("heading", name="Documentos para a formalização")).to_be_visible()
    expect(ana.get_by_text("Este documento foi pedido na inscrição.").first).to_be_visible()
    assert ana.locator("input[name=requisito]:checked").count() == 0
    tela.capturar(ana, "definicao-vazia-1280")
    for requisito in (IDENTIDADE, CERTIDAO, HISTORICO, CERTIFICADO_DO_CURSO):
        ana.locator(f"input[name=requisito][value='{requisito}']").check()
    ana.get_by_role("button", name="Gravar a definição").click()
    expect(ana.get_by_text("Diga por que estes documentos vão ao setor")).to_be_visible()
    ana.locator("textarea[name=motivo]").fill("Portaria 12/2026 do Registro Acadêmico")
    ana.get_by_role("button", name="Gravar a definição").click()
    expect(ana.get_by_text("Definição gravada.")).to_be_visible()
    expect(ana.get_by_text("Versão 1")).to_be_visible()
    tela.capturar(ana, "definicao-gravada-1280")
    assert str(TITULOS) not in definir.vigente(edital).requisitos
    _nas_duas_larguras(
        tela, "maria", [], _url(tela, "interface:formalizacao-definicao", edital.id), "definicao"
    )

    # O setor: a barra, a página, a verificação e o download.
    rui = tela.gestao("rui", ["formalizacao"])
    rui.goto(_url(tela, "interface:lista"))
    rui.get_by_role("link", name="Formalização").first.click()
    rui.get_by_role("link", name=str(edital)).click()
    expect(rui.get_by_role("heading", name="Documentos para formalização")).to_be_visible()
    assert rui.locator("article.pessoa-da-formalizacao").count() == 5
    expect(
        rui.get_by_text("enviado na inscrição; sem conferência na convocação").first
    ).to_be_visible()
    tela.capturar(rui, "pagina-do-edital-1280")
    _nas_duas_larguras(
        tela,
        "rui",
        ["formalizacao"],
        _url(tela, "interface:formalizacao-edital", edital.id),
        "pagina-do-edital",
    )
    _verificar_todos(rui)
    expect(rui.get_by_text("Pacote completo: 5 de 5 pessoas incluídas")).to_be_visible()
    tela.capturar(rui, "verificacao-completa-1280")
    caminho = _baixar(rui, "Baixar pacote (5 pessoas)", tmp_path)

    assert caminho.name.startswith("formalizacao-") and not caminho.name.endswith("-parcial.zip")
    with zipfile.ZipFile(caminho) as pacote:
        entradas = pacote.namelist()
    assert "manifesto.csv" in entradas
    assert len([e for e in entradas if e != "manifesto.csv"]) == 20
    assert ExportacaoDeFormalizacao.objects.get().resultado == "COMPLETO"

    rui.goto(_url(tela, "interface:formalizacao-edital", edital.id))
    expect(rui.get_by_text("Pacote completo: 5 de 5 pessoas incluídas")).to_be_visible()
    tela.capturar(rui, "historico-1280")


def test_cenario_e_o_controle_de_acesso_pelas_urls(tela, certame, gestor):
    edital = certame.edital
    definir_documentos(edital, gestor)
    designar_direto(edital, "bia", perfis=["00000000-0000-0000-0000-00000000abcd"])
    inscricao = certame.inscricoes_aptas[0]
    documento = documentos_de(edital, inscricao)[0]
    arquivo = _url(
        tela,
        "interface:formalizacao-documento",
        edital.id,
        inscricao.id,
        documento.origem,
        documento.objeto_id,
    )
    pagina_do_setor = _url(tela, "interface:formalizacao-edital", edital.id)

    bia = tela.gestao("bia", ["formalizacao"])
    assert bia.goto(arquivo).status == 404
    rui_sem_designacao = tela.gestao("rui", ["formalizacao"])
    assert rui_sem_designacao.goto(pagina_do_setor).status == 404
    ana = tela.gestao("maria")
    resposta = ana.goto(pagina_do_setor)
    assert resposta.status == 403
    expect(ana.get_by_text("papel Formalização")).to_be_visible()
    tela.capturar(ana, "recusa-da-presidencia-1280")
    # Quem confere não alcança a página do setor, e o setor não alcança a conferência (FR-3665).
    joao = tela.gestao("joao")
    assert joao.goto(pagina_do_setor).status == 403


def test_cenario_f_a_verificacao_parcial_vem_antes_do_download(tela, certame, gestor, tmp_path):
    edital = certame.edital
    definir_documentos(edital, gestor)
    designar_direto(edital, "rui")
    ausente, divergente = certame.inscricoes_aptas[0], certame.inscricoes_aptas[1]
    apagar(documentos_de(edital, ausente)[0])
    adulterar(documentos_de(edital, divergente)[2])

    rui = tela.gestao("rui", ["formalizacao"])
    rui.goto(_url(tela, "interface:formalizacao-edital", edital.id))
    _verificar_todos(rui)

    # Antes de qualquer download, a tela diz o resultado e nomeia os dois, com o motivo.
    expect(rui.get_by_text("Pacote parcial: 3 de 5 pessoas incluídas")).to_be_visible()
    nao_incluidas = rui.locator("section.nao-incluidas")
    expect(nao_incluidas.get_by_text(f"{ausente.protocolo} {ausente.nome}")).to_be_visible()
    expect(nao_incluidas.get_by_text("arquivo indisponível")).to_be_visible()
    expect(nao_incluidas.get_by_text(f"{divergente.protocolo} {divergente.nome}")).to_be_visible()
    expect(nao_incluidas.get_by_text("arquivo diferente do conferido")).to_be_visible()
    assert not ExportacaoDeFormalizacao.objects.exists()
    tela.capturar(rui, "verificacao-parcial-1280")

    estreita = tela.gestao("rui", ["formalizacao"], viewport=CELULAR)
    estreita.goto(_url(tela, "interface:formalizacao-edital", edital.id))
    _verificar_todos(estreita)
    expect(estreita.get_by_text("Pacote parcial: 3 de 5 pessoas incluídas")).to_be_visible()
    sem_rolagem_horizontal(estreita)
    tela.capturar(estreita, "verificacao-parcial-375")

    caminho = _baixar(rui, "Baixar pacote parcial (3 pessoas)", tmp_path)
    assert caminho.name.endswith("-parcial.zip")
    with zipfile.ZipFile(caminho) as pacote:
        pastas = {e.split("/")[0] for e in pacote.namelist() if "/" in e}
    assert len(pastas) == 3
    assert not any(ausente.protocolo in pasta for pasta in pastas)
    assert ExportacaoDeFormalizacao.objects.get().resultado == "PARCIAL"

    # O arquivo ausente, aberto pela página, é indisponível — e não erro do servidor.
    documento = documentos_de(edital, ausente)[0]
    resposta = rui.goto(
        _url(
            tela,
            "interface:formalizacao-documento",
            edital.id,
            ausente.id,
            documento.origem,
            documento.objeto_id,
        )
    )
    assert resposta.status == 409
    expect(rui.get_by_text("Arquivo indisponível").first).to_be_visible()
    tela.capturar(rui, "arquivo-indisponivel-1280")
