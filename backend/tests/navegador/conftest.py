"""O ambiente dos testes de navegador (107, `FR-3131`, `FR-3132`).

Três peças, todas daqui: o servidor da suíte (`live_server`), a página do provedor
(`provedor.PaginaDoProvedor`) e um Chromium dirigido pelo Playwright. A preparação — identidades,
vínculos, quem o provedor autentica — é das *fixtures* e do começo de cada caso; as ações são só do
navegador; as verificações vêm depois, no banco.

`NAVEGADOR_VISIVEL=1` abre o navegador na tela e desacelera cada passo, para uma pessoa assistir à
jornada. `NAVEGADOR_CAPTURAS=<pasta>` grava uma captura em cada passo marcado.

Sem a biblioteca do grupo `navegador`, os casos pulam, como os do tokenizer sem o `assistente`.
"""

import os
import re
from pathlib import Path

import pytest
from django.db import connections

from tests.fixtures import provedor_simulado
from tests.navegador.provedor import PaginaDoProvedor
from tests.seguranca.conftest import campus_a  # noqa: F401  (fixture)

try:
    from playwright import sync_api
except ImportError:  # o grupo opcional não está instalado: cada módulo de teste pula sozinho
    sync_api = None


def pytest_collection_modifyitems(items):
    for item in items:
        if "tests/navegador/" in str(item.fspath):
            item.add_marker(pytest.mark.navegador)


@pytest.fixture
def provedor_no_navegador(settings, monkeypatch):
    """O provedor simulado da `106`, com a página de autorização servida por este teste."""
    pagina = PaginaDoProvedor().subir()
    provedor_simulado.limpar()
    monkeypatch.setattr(provedor_simulado, "ENDERECO_DE_AUTORIZACAO", pagina.endereco)
    settings.GESTAO_PROVEDOR_INSTITUCIONAL = provedor_simulado.CAMINHO
    yield pagina
    pagina.derrubar()
    provedor_simulado.limpar()


@pytest.fixture
def navegador(monkeypatch):
    # O Playwright síncrono mantém um laço de eventos na linha principal, e o ORM do Django recusa
    # consultas onde há laço rodando. As consultas aqui são da preparação e das verificações, fora
    # do navegador; a permissão vale só durante o caso.
    monkeypatch.setenv("DJANGO_ALLOW_ASYNC_UNSAFE", "true")
    visivel = os.getenv("NAVEGADOR_VISIVEL") == "1"
    with sync_api.sync_playwright() as playwright:
        chromium = playwright.chromium.launch(headless=not visivel, slow_mo=500 if visivel else 0)
        yield chromium
        chromium.close()
        # Sem isto sobrava uma sessão aberta no banco de teste a cada caso — a conexão que o ORM
        # abriu com o Playwright ativo, e que a limpeza do pytest-django não fechava —, e o
        # `DROP DATABASE` do fim da suíte esperava por ela e desistia (medido em 30/10: 13 s por
        # caso, e o aviso de desmontagem; com o fechamento, 5 s e nenhum aviso).
        connections.close_all()


class Jornada:
    """Um navegador por pessoa: cada uma tem a própria sessão, como em computadores diferentes."""

    def __init__(self, navegador, servidor, provedor, nome_do_caso):
        self._navegador = navegador
        self.servidor = servidor
        self.provedor = provedor
        self._capturas = os.getenv("NAVEGADOR_CAPTURAS")
        self._caso = re.sub(r"\W+", "-", nome_do_caso)
        self._passo = 0
        self._contextos = []

    def pessoa(self):
        contexto = self._navegador.new_context(viewport={"width": 1280, "height": 900})
        self._contextos.append(contexto)
        pagina = contexto.new_page()
        pagina.set_default_timeout(10_000)
        return pagina

    def entrar(self, pagina, identificador, *, nome="", email=""):
        """A entrada inteira pela tela: a página de acesso, o provedor, o retorno."""
        self.provedor.preparar(identificador, nome=nome, email=email)
        pagina.goto(f"{self.servidor.url}/gestao/identificar")
        pagina.get_by_role("link", name="Entrar com a conta institucional").click()
        pagina.get_by_role("link", name="Continuar").click()
        pagina.wait_for_load_state()

    def capturar(self, pagina, rotulo):
        if not self._capturas:
            return
        self._passo += 1
        destino = Path(self._capturas) / f"{self._caso}-{self._passo:02d}-{rotulo}.png"
        destino.parent.mkdir(parents=True, exist_ok=True)
        pagina.screenshot(path=str(destino), full_page=True)

    def fechar(self):
        for contexto in self._contextos:
            contexto.close()


@pytest.fixture
def jornada(navegador, live_server, provedor_no_navegador, request):
    atual = Jornada(navegador, live_server, provedor_no_navegador, request.node.name)
    yield atual
    atual.fechar()
