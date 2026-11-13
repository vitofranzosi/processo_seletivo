"""A jornada da Retificação num navegador de verdade (123, FR-3949).

Os cenários A a G da auditoria de UX de 05/11/2026 (`doc/auditoria-ux-retificacao-2026-11-05/`),
agora sobre a tela com o MVP:

- **A, B e C pela busca** — o campo achado pelo rótulo, com o foco nele em duas ações;
- **B com o impeditivo** — a recusa do quadro já na conferência, com o caminho até a linha;
- **D, a múltipla** — três cartões «na proposta» depois de conferir, e cada linha do resumo levando
  ao campo;
- **a edição da devolvida** — aberta já com o que o ato contém;
- **G, a sucessiva** — a base de vigência futura dita como tal, nas cinco telas;
- **E, o extenso** — a busca no Edital ampliado, a 1280 e a 375 px;
- **e um percurso só pelo teclado**.

Em três partes, como as jornadas da `115`, da `120` e da `122`: a preparação pelas *fixtures*, as
ações só no navegador, e as verificações na tela e no banco. Nenhuma página pode ter violação da
política de conteúdo.

**A contagem de ações** é a do roteiro da auditoria: cada `fill`, `click` e `press` conta 1; o
`goto` inicial não conta.
"""

import pytest

expect = pytest.importorskip("playwright.sync_api", reason="sem o grupo opcional navegador").expect

from django.urls import reverse  # noqa: E402

from processo_seletivo.publicacoes.models_retificacao import Retificacao  # noqa: E402
from tests.fixtures.edital_da_auditoria import (  # noqa: E402
    referencia_do_campo,
    retificacao_devolvida,
    retificacao_futura,
    versao_mais_recente,
)
from tests.fixtures.publicacao import create_retification  # noqa: E402
from tests.fixtures.snapshot import PERFIL  # noqa: E402
from tests.navegador.test_jornada_dos_documentos_da_convocacao import (  # noqa: E402
    CELULAR,
    Tela,
)

pytestmark = pytest.mark.django_db(transaction=True)

RESULTADOS = "ol.resultados-da-busca a.ir-ao-campo"


@pytest.fixture
def tela(navegador, live_server, settings, request):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    atual = Tela(navegador, live_server, request.node.name)
    yield atual
    atual.fechar()
    assert atual.violacoes == [], "violação da política de conteúdo no console"


class Acoes:
    """Conta as ações da pessoa, como o roteiro da auditoria contava."""

    def __init__(self, pagina):
        self.pagina = pagina
        self.total = 0

    def preencher(self, seletor, valor):
        self.total += 1
        self.pagina.locator(seletor).fill(valor)

    def clicar(self, localizador):
        self.total += 1
        localizador.click()

    def teclar(self, tecla):
        self.total += 1
        self.pagina.keyboard.press(tecla)


def _retificar(tela, edital, subject="ana.elaboradora", papeis=("elaborador",), viewport=None):
    pagina = tela.gestao(subject, list(papeis), **({"viewport": viewport} if viewport else {}))
    pagina.goto(tela.servidor.url + reverse("interface:retificar", args=[edital.id]))
    return pagina


def _focado(pagina):
    return pagina.evaluate("document.activeElement && document.activeElement.id")


def _resultado(pagina, rotulo, onde):
    """O link «Ir ao campo» do resultado cujo rótulo e lugar são estes."""
    return (
        pagina.locator("ol.resultados-da-busca li")
        .filter(has_text=onde)
        .filter(has_text=rotulo)
        .locator("a.ir-ao-campo")
        .first
    )


def test_cenarios_a_b_c_pela_busca(tela, edital_da_auditoria):
    versao = versao_mais_recente(edital_da_auditoria)
    pagina = _retificar(tela, edital_da_auditoria)

    # A — o término das inscrições, pelo rótulo, em duas ações.
    a = Acoes(pagina)
    a.preencher("#filtro-da-retificacao", "término inscricao")
    a.clicar(_resultado(pagina, "Término", "INSCRICAO"))
    termino = referencia_do_campo(versao, "Evento 1", "Término")
    assert _focado(pagina) == f"c-{termino}"
    assert a.total == 2
    pagina.locator(f"#c-{termino}").fill("2026-12-12T23:59")
    tela.capturar(pagina, "a-termino")

    # B — as vagas: o Perfil e as linhas do quadro, e não a Lista de concorrência.
    b = Acoes(pagina)
    b.preencher("#filtro-da-retificacao", "vagas")
    rotulos = pagina.locator("ol.resultados-da-busca .rotulo").all_inner_texts()
    assert rotulos and set(rotulos) == {"Vagas imediatas"}
    b.clicar(_resultado(pagina, "Vagas imediatas", "Linha do quadro Ampla concorrência — P1"))
    linha = referencia_do_campo(
        versao, "Linha do quadro Ampla concorrência — P1", "Vagas imediatas"
    )
    assert _focado(pagina) == f"c-{linha}"
    assert b.total == 2

    # O que foi digitado continua lá: a busca não mexe em valor (FR-3924).
    assert pagina.locator(f"#c-{termino}").input_value() == "2026-12-12T23:59"

    # C — os requisitos de participação de cada Perfil, e a Seção como cartão.
    pagina.locator("#filtro-da-retificacao").fill("requisito")
    textos = pagina.locator("ol.resultados-da-busca li").all_inner_texts()
    assert sum("Requisitos de participação" in t for t in textos) == 3
    assert any("Requisitos gerais" in t and "Ir ao cartão" in t for t in textos)

    # «remuneração» e «prazo» acham o campo; «candidato» não lê o texto das Seções.
    pagina.locator("#filtro-da-retificacao").fill("remuneracao")
    assert set(pagina.locator("ol.resultados-da-busca .rotulo").all_inner_texts()) == {
        "Remuneração"
    }
    pagina.locator("#filtro-da-retificacao").fill("prazo")
    assert "Prazo em dias" in pagina.locator("ol.resultados-da-busca .rotulo").all_inner_texts()
    pagina.locator("#filtro-da-retificacao").fill("candidato")
    assert (
        "Texto da seção" not in pagina.locator("ol.resultados-da-busca .rotulo").all_inner_texts()
    )
    tela.capturar(pagina, "c-busca")


def test_cenario_b_o_impeditivo_na_conferencia(tela, edital_da_auditoria):
    versao = versao_mais_recente(edital_da_auditoria)
    vagas = referencia_do_campo(versao, "Perfil P1", "Vagas imediatas")
    linha = referencia_do_campo(
        versao, "Linha do quadro Ampla concorrência — P1", "Vagas imediatas"
    )
    pagina = _retificar(tela, edital_da_auditoria)

    pagina.locator(f"#c-{vagas}").fill("2")
    pagina.get_by_role("button", name="Ver o que vai mudar").click()
    secao = pagina.locator("#impeditivos")
    expect(secao).to_be_visible()
    expect(secao).to_contain_text("será recusado enquanto houver")
    tela.capturar(pagina, "b-impeditivo")

    secao.locator("a.ir-ao-campo").first.click()
    assert _focado(pagina) == f"c-{linha}", "o link leva à linha do quadro, com o foco nela"
    pagina.locator(f"#c-{linha}").fill("2")
    pagina.get_by_role("button", name="Ver o que vai mudar").click()
    expect(pagina.locator("#impeditivos")).to_have_count(0)

    pagina.locator("#justificativa").fill("Mais uma vaga, com a linha do quadro.")
    pagina.get_by_role("button", name="Criar Retificação").click()
    pagina.wait_for_url("**/retificacoes/**")
    assert Retificacao.objects.filter(edital=edital_da_auditoria).count() == 1


def test_cenario_d_a_marca_sobrevive_a_conferencia(tela, edital_da_auditoria):
    versao = versao_mais_recente(edital_da_auditoria)
    campos = [
        (referencia_do_campo(versao, "Evento 1", "Término"), "2026-12-12T23:59"),
        (referencia_do_campo(versao, "Perfil P3", "Localidade"), "Serra"),
        (referencia_do_campo(versao, "Seção Prazo de validade", "Texto da seção"), "Dois anos."),
    ]
    pagina = _retificar(tela, edital_da_auditoria)
    for ref, valor in campos:
        pagina.locator(f"#c-{ref}").fill(valor)
    pagina.get_by_role("button", name="Ver o que vai mudar").click()

    marcados = pagina.locator("fieldset.linha[data-na-proposta]")
    expect(marcados).to_have_count(3)
    expect(marcados.locator("legend .na-proposta")).to_have_count(3)
    barra = pagina.locator(".barra-de-acoes")
    expect(barra).to_contain_text("3 cartões com alteração na proposta")
    expect(barra).to_contain_text("Nenhuma alteração nova desde a última conferência")
    tela.capturar(pagina, "d-conferencia")

    pagina.locator("#so-alteradas").check()
    expect(pagina.locator("fieldset.linha[data-linha]:visible")).to_have_count(3)
    pagina.locator("#so-alteradas").uncheck()

    for ref, _ in campos:
        link = pagina.locator(f'.consequencias a.ir-ao-campo[href="#c-{ref}"]')
        acoes = Acoes(pagina)
        acoes.clicar(link)
        assert _focado(pagina) == f"c-{ref}"
        assert acoes.total == 1

    pagina.locator(f"#c-{campos[1][0]}").fill("Cariacica")
    expect(barra).to_contain_text("1 campo alterado desde a última conferência")
    expect(barra).to_contain_text("3 cartões com alteração na proposta")


def test_a_edicao_da_devolvida_abre_marcada(tela, edital_da_auditoria, api_client):
    devolvida = retificacao_devolvida(
        api_client,
        edital_da_auditoria,
        [
            {
                "targetPath": f"/profiles/id={PERFIL['C']}/locality",
                "operation": "REPLACE",
                "newValue": "Serra",
            },
            {
                "targetPath": f"/profiles/id={PERFIL['B']}/workload",
                "operation": "REPLACE",
                "newValue": "40 horas semanais",
            },
        ],
    )
    pagina = tela.gestao("ana.elaboradora", ["elaborador"])
    pagina.goto(tela.servidor.url + reverse("interface:retificacao-editar", args=[devolvida.id]))
    expect(pagina.locator("fieldset.linha[data-na-proposta]")).to_have_count(2)
    barra = pagina.locator(".barra-de-acoes")
    expect(barra).to_contain_text("2 cartões com alteração na proposta")
    expect(barra).to_contain_text("Nenhuma alteração nova nesta edição")
    tela.capturar(pagina, "edicao")


def test_cenario_g_a_base_de_vigencia_futura(tela, edital_da_auditoria, api_client):
    retificacao_futura(api_client, edital_da_auditoria)
    pagina = _retificar(tela, edital_da_auditoria)
    expect(pagina.locator(".aviso .versao-base")).to_contain_text("ainda não vigora")
    expect(pagina.locator("body")).not_to_contain_text("Vigente hoje")
    tela.capturar(pagina, "g-retificar")

    item = create_retification(
        api_client,
        edital_da_auditoria,
        [
            {
                "targetPath": f"/profiles/id={PERFIL['C']}/workload",
                "operation": "REPLACE",
                "newValue": "30 horas semanais",
            }
        ],
        suffix="g-sobre-a-futura",
    )
    gestao = tela.gestao("bruno.gestor", ["gestor", "homologador", "publicador"])
    for destino in (
        reverse("interface:retificacao-detalhe", args=[item.id]),
        *(
            reverse("interface:retificacao-ato", args=[item.id, acao])
            for acao in ("homologar", "devolver", "publicar")
        ),
    ):
        gestao.goto(tela.servidor.url + destino)
        expect(gestao.locator("body")).to_contain_text(
            "«Antes» é o conteúdo da versão-base desta Retificação."
        )
        expect(gestao.locator("body")).to_contain_text("ainda não vigora")
        expect(gestao.locator("body")).not_to_contain_text("Vigente hoje")


def test_cenario_e_o_edital_extenso(tela, edital_extenso):
    versao = versao_mais_recente(edital_extenso)
    pagina = _retificar(tela, edital_extenso)
    a = Acoes(pagina)
    a.preencher("#filtro-da-retificacao", "vagas")
    itens = pagina.locator("ol.resultados-da-busca li")
    assert 0 < itens.count() <= 25
    a.clicar(_resultado(pagina, "Vagas imediatas", "Linha do quadro Ampla concorrência — CURSO-4"))
    linha = referencia_do_campo(
        versao, "Linha do quadro Ampla concorrência — CURSO-4", "Vagas imediatas"
    )
    assert _focado(pagina) == f"c-{linha}"
    assert a.total == 2

    pagina.locator("#filtro-da-retificacao").fill("evento 11")
    expect(pagina.locator(RESULTADOS).first).to_be_visible()
    tela.capturar(pagina, "e-extenso-1280")

    estreita = _retificar(tela, edital_extenso, viewport=CELULAR)
    estreita.locator("#filtro-da-retificacao").fill("vagas")
    sobra = estreita.evaluate(
        "document.documentElement.scrollWidth - document.documentElement.clientWidth"
    )
    assert sobra <= 0, f"rolagem lateral de {sobra}px a 375"
    tela.capturar(estreita, "e-extenso-375")


def test_so_pelo_teclado(tela, edital_da_auditoria):
    versao = versao_mais_recente(edital_da_auditoria)
    remuneracao = referencia_do_campo(versao, "Perfil P1", "Remuneração")
    pagina = _retificar(tela, edital_da_auditoria)

    pagina.locator("#filtro-da-retificacao").focus()
    pagina.keyboard.type("remuneração p1")
    pagina.keyboard.press("Enter")
    assert pagina.evaluate("document.activeElement.classList.contains('ir-ao-campo')")
    pagina.keyboard.press("Enter")
    assert _focado(pagina) == f"c-{remuneracao}"
    pagina.keyboard.press("Control+A")
    pagina.keyboard.type("R$ 5.000,00 mensais")

    pagina.get_by_role("button", name="Ver o que vai mudar").focus()
    pagina.keyboard.press("Enter")
    pagina.wait_for_load_state()
    pagina.locator(f'.consequencias a.ir-ao-campo[href="#c-{remuneracao}"]').focus()
    pagina.keyboard.press("Enter")
    assert _focado(pagina) == f"c-{remuneracao}"
    assert pagina.locator(f"#c-{remuneracao}").input_value() == "R$ 5.000,00 mensais"
