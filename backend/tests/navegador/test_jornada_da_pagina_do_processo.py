"""A página do Processo num navegador de verdade (147, SC-1661, SC-1662, FR-5315, UX-440).

O que só o navegador mede:

- **a primeira dobra**: a 1366 × 768, "O que fazer agora" e o título de "Precisa de atenção", com o
  total, aparecem sem rolar (SC-1661);
- **as larguras**: a 390, 1366 e 1920 px nada rola na horizontal (SC-1662);
- **a ordem no estreito**: a Atenção vem antes dos marcos (UX-440);
- **a CSP**: nenhuma violação — a única pista dela é o navegador;
- **o teclado**: o grupo de atenção de um Edital abre com Enter.

A altura do Processo de 31 Editais (SC-1660) é medida no banco de demonstração da rodada 1, e não
aqui: publicar trinta Editais custaria minutos por caso.
"""

import pytest

pytest.importorskip("playwright.sync_api", reason="sem o grupo opcional navegador")

from django.test import Client  # noqa: E402
from django.urls import reverse  # noqa: E402

from tests.fixtures.supervisao import SEGUNDO_SEED, submeter  # noqa: E402
from tests.interface.conftest import identificar  # noqa: E402

pytestmark = pytest.mark.django_db(transaction=True)

OUVIR_A_CSP = """
window.__violacoes = [];
document.addEventListener('securitypolicyviolation', (e) => {
  window.__violacoes.push(e.violatedDirective + ' ' + (e.blockedURI || 'inline'));
});
"""


def abrir(navegador, live_server, processo, largura, altura):
    cliente = Client()
    identificar(cliente, "maria", [])
    contexto = navegador.new_context(viewport={"width": largura, "height": altura}, locale="pt-BR")
    contexto.add_cookies(
        [
            {
                "name": "sessionid",
                "value": cliente.cookies["sessionid"].value,
                "url": live_server.url,
            }
        ]
    )
    contexto.add_init_script(OUVIR_A_CSP)
    pagina = contexto.new_page()
    pagina.goto(live_server.url + reverse("interface:processo-detalhe", args=[processo.id]))
    return pagina


def rola_de_lado(pagina):
    return pagina.evaluate(
        "document.documentElement.scrollWidth > document.documentElement.clientWidth"
    )


@pytest.fixture
def com_atencao(settings, processo_a, edital_a, edital_c, comissao_de_a):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    submeter(edital_c, 2, seed=SEGUNDO_SEED)
    return processo_a


def test_o_que_fazer_e_a_atencao_na_primeira_dobra_sem_violacao(
    navegador, live_server, com_atencao
):
    pagina = abrir(navegador, live_server, com_atencao, 1366, 768)

    for seletor in ("#acoes-processo", "#atencao-titulo"):
        caixa = pagina.locator(seletor).bounding_box()
        assert caixa is not None and caixa["y"] + caixa["height"] < 768, seletor
    assert " em 1 Edital)" in pagina.locator("#atencao-titulo").inner_text()
    assert not rola_de_lado(pagina)
    assert pagina.evaluate("window.__violacoes") == []

    # O teclado alterna o grupo de um Edital. Com um Edital só, ele nasce aberto (FR-5317).
    grupo = pagina.locator(".atencao-por-edital details").first
    assert grupo.evaluate("d => d.open")
    pagina.locator(".atencao-por-edital summary").first.focus()
    pagina.keyboard.press("Enter")
    assert not grupo.evaluate("d => d.open")


@pytest.mark.parametrize(("largura", "altura"), [(390, 844), (1920, 1080)])
def test_nada_rola_de_lado(navegador, live_server, com_atencao, largura, altura):
    pagina = abrir(navegador, live_server, com_atencao, largura, altura)
    assert not rola_de_lado(pagina)
    assert pagina.evaluate("window.__violacoes") == []


def test_no_estreito_a_atencao_vem_antes_dos_marcos(navegador, live_server, com_atencao):
    pagina = abrir(navegador, live_server, com_atencao, 390, 844)
    atencao = pagina.locator("#atencao-titulo").bounding_box()
    marcos = pagina.locator("#marcos-titulo").bounding_box()
    trabalho = pagina.locator("#acoes-processo").bounding_box()
    assert trabalho["y"] < atencao["y"] < marcos["y"]
