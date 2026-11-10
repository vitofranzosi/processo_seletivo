"""O Centro de Controle num navegador de verdade, no C06 da `134` (136, SC-1470, SC-1477, FR-4747).

O que só o navegador mede — e que o cliente de teste não vê:

- **a primeira dobra**: a 1440 × 900, "Onde estamos", o mapa e a ação em destaque aparecem sem rolar
  (a tarefa 1 e a 2 da validação com operadores);
- **a tela estreita**: a 375 px, nada rola na horizontal;
- **a CSP**: nenhuma violação, que no servidor não deixa rastro — a única pista é o navegador;
- **o teclado**: o Tab percorre o mapa antes das providências, na ordem visual.

É inspeção automatizada, e não teste com pessoas: a validação com operadores é do plano de produção
do estudo, e fica para a homologação.
"""

import pytest

pytest.importorskip("playwright.sync_api", reason="sem o grupo opcional navegador")

from django.test import Client  # noqa: E402
from django.urls import reverse  # noqa: E402

from processo_seletivo.processos.models import Edital  # noqa: E402
from processo_seletivo.treinamento import construcao as k  # noqa: E402
from processo_seletivo.treinamento.models import CenarioDeTreinamento  # noqa: E402
from tests.fixtures.autoridades import AUTORIDADE_DA_SUITE  # noqa: E402
from tests.fixtures.treinamento import carregar  # noqa: E402
from tests.interface.conftest import identificar  # noqa: E402

pytestmark = pytest.mark.django_db(transaction=True)

#: Registra toda violação da CSP antes de qualquer script da página.
OUVIR_A_CSP = """
window.__violacoes = [];
document.addEventListener('securitypolicyviolation', (e) => {
  window.__violacoes.push(e.violatedDirective + ' ' + (e.blockedURI || 'inline'));
});
"""


@pytest.fixture
def c06(settings, raiz_de_arquivos):
    settings.CENARIOS_DE_TREINAMENTO = True
    settings.SORTEIO_FONTE_DE_DEMONSTRACAO = True
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    saida = carregar("C06", autoridade=str(AUTORIDADE_DA_SUITE))
    assert "C06  CRIADO" in saida, saida
    manifesto = CenarioDeTreinamento.objects.get(codigo="C06")
    return Edital.objects.get(processo=manifesto.processo)


def sessao_da_presidencia(live_server):
    """A identidade pelo seletor, num cliente, e o cookie dela levado ao navegador."""
    cliente = Client()
    identificar(cliente, k.PRESIDENCIA, [])
    return {
        "name": "sessionid",
        "value": cliente.cookies["sessionid"].value,
        "url": live_server.url,
    }


def abrir(navegador, live_server, edital, largura, altura=900):
    contexto = navegador.new_context(viewport={"width": largura, "height": altura}, locale="pt-BR")
    contexto.add_cookies([sessao_da_presidencia(live_server)])
    contexto.add_init_script(OUVIR_A_CSP)
    pagina = contexto.new_page()
    pagina.goto(live_server.url + reverse("interface:centro-do-edital", args=[edital.id]))
    return pagina


def na_primeira_dobra(pagina, seletor, altura=900):
    caixa = pagina.locator(seletor).first.bounding_box()
    assert caixa is not None, seletor
    return caixa["y"] < altura and caixa["height"] > 0


def test_o_c06_na_primeira_dobra_sem_rolagem_e_sem_violacao(navegador, live_server, c06):
    pagina = abrir(navegador, live_server, c06, 1440)

    assert pagina.get_by_text("Onde estamos").is_visible()
    assert na_primeira_dobra(pagina, ".cc-onde")
    assert na_primeira_dobra(pagina, ".cc-mapa")
    assert na_primeira_dobra(pagina, ".cc-destaque")
    assert "Fixar os participantes" in pagina.locator(".cc-destaque").inner_text()
    assert pagina.evaluate("window.__violacoes") == []

    estreita = abrir(navegador, live_server, c06, 375, 812)
    largura = estreita.evaluate(
        "[document.documentElement.scrollWidth, document.documentElement.clientWidth]"
    )
    assert largura[0] <= largura[1], largura
    assert estreita.evaluate("window.__violacoes") == []


def test_o_tab_percorre_o_mapa_antes_das_providencias(navegador, live_server, c06):
    """FR-4747: a ordem do teclado é a ordem visual."""
    pagina = abrir(navegador, live_server, c06, 1440)
    pagina.locator("h1").click()
    paradas = []
    for _ in range(40):
        pagina.keyboard.press("Tab")
        paradas.append(
            pagina.evaluate(
                "(() => { const e = document.activeElement;"
                " if (!e || !e.closest('main')) return '';"
                " if (e.closest('.cc-mapa')) return 'mapa';"
                " if (e.closest('.cc-agora')) return 'agora';"
                " return 'outro'; })()"
            )
        )
        if "agora" in paradas:
            break
    assert "mapa" in paradas and "agora" in paradas, paradas
    assert paradas.index("mapa") < paradas.index("agora"), paradas
