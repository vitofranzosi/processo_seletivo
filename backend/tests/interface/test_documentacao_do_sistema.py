"""A Visão do Sistema servida pela gestão (105).

O manual é mantido por PRs de documentação, que não passam por aqui (`#341` é um). Por isso os dois
guardiões do fim leem o `index.html` do disco, e não um recorte fixo: um arquivo novo que o manual
passe a pedir, ou um `<script>` embutido que volte, reprovam a suíte antes de virar tela sem estilo
e sem erro no servidor — a CSP só se queixa no console do navegador.
"""

from html.parser import HTMLParser
from urllib.parse import urlsplit

import pytest
from django.urls import reverse

from processo_seletivo.interface import documentacao
from processo_seletivo.shared.politica_de_conteudo import CABECALHO, POLITICA
from tests.interface.conftest import identificar

INICIO = reverse("interface:documentacao")


def arquivo(caminho):
    return reverse("interface:documentacao-arquivo", args=[caminho])


class _Marcacao(HTMLParser):
    """As referências locais do manual e o que nele a política de conteúdo recusaria."""

    def __init__(self):
        super().__init__()
        self.referencias = []
        self.embutidos = []
        self._em_script_sem_src = False

    def handle_starttag(self, tag, attrs):
        atributos = dict(attrs)
        if tag == "style":
            self.embutidos.append("<style>")
        if tag == "script" and "src" not in atributos:
            self.embutidos.append("<script> sem src")
        for nome, valor in attrs:
            if nome == "style":
                self.embutidos.append(f'<{tag} style="{valor}">')
            elif nome.startswith("on"):
                self.embutidos.append(f"<{tag} {nome}>")
            elif nome in ("src", "href") and valor:
                if valor.startswith(("data:", "javascript:")):
                    self.embutidos.append(f'<{tag} {nome}="{valor[:40]}…">')
                elif tag in ("link", "script", "img") and not urlsplit(valor).scheme:
                    self.referencias.append(valor)


def _marcacao():
    leitor = _Marcacao()
    leitor.feed((documentacao.PASTA / "index.html").read_text())
    return leitor


# ---- a porta ---------------------------------------------------------------------------------


@pytest.mark.django_db
def test_sem_identidade_leva_a_identificacao_e_volta_ao_manual(client, seletor_ligado):
    """`FR-2902`: a mesma porta das outras telas, com o manual como destino de volta."""
    resposta = client.get(INICIO)

    assert resposta.status_code == 302
    assert resposta["Location"].startswith(reverse("interface:identificar"))
    assert "proximo=%2Fgestao%2Fdocumentacao%2F" in resposta["Location"]


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.parametrize("papeis", [[], ["elaborador"], ["gestor"]], ids=["so-vinculo", "e", "g"])
def test_toda_identidade_le_o_manual_sob_a_politica(client, seletor_ligado, papeis):
    """`FR-2902`, `FR-2904`, `D-001`: quem só tem vínculo também lê, e o HTML vai sob a CSP."""
    identificar(client, "pessoa.qualquer", papeis)

    resposta = client.get(INICIO)

    assert resposta.status_code == 200
    assert resposta["Content-Type"] == "text/html; charset=utf-8"
    assert resposta[CABECALHO] == POLITICA
    assert b"<title>Vis\xc3\xa3o do Sistema" in resposta.content


@pytest.mark.django_db
@pytest.mark.parametrize(
    "caminho",
    [
        "CHANGELOG-2026-10.md",
        "assets/nao-existe.css",
        "../../backend/config/settings/base.py",
        "assets/../index.html",
    ],
)
def test_arquivo_fora_da_lista_e_inexistente(client, seletor_ligado, caminho):
    """`FR-2903`, `SC-993`, `D-002`: a pasta não é servida, e caminho que sai dela também não."""
    identificar(client, "gustavo.gestor", ["gestor"])

    assert client.get(arquivo(caminho)).status_code == 404


@pytest.mark.django_db
def test_o_manual_nao_aceita_outro_metodo(client, seletor_ligado):
    identificar(client, "gustavo.gestor", ["gestor"])

    assert client.post(INICIO).status_code == 405


# ---- os guardiões do manual ------------------------------------------------------------------


@pytest.mark.django_db
def test_todo_arquivo_que_o_manual_pede_esta_na_lista_e_abre(client, seletor_ligado):
    """`FR-2903`, `SC-991`: um `assets/` novo no manual sem entrada na lista seria um 404 calado."""
    identificar(client, "gustavo.gestor", ["gestor"])
    referencias = _marcacao().referencias

    assert referencias, "o leitor não achou referência nenhuma — o manual mudou de forma?"
    for referencia in referencias:
        assert referencia in documentacao.ARQUIVOS, referencia
        resposta = client.get(arquivo(referencia))
        assert resposta.status_code == 200, referencia
        assert resposta["Content-Type"] == documentacao.ARQUIVOS[referencia]


def test_nada_no_manual_e_embutido():
    """`FR-2904`, `SC-992`: `style-src` e `script-src` só da própria origem, e `img-src` também."""
    assert _marcacao().embutidos == []


def test_o_voltar_do_manual_leva_ao_inicio_da_gestao():
    """`FR-2905`, `D-004`: relativo, para valer sob qualquer prefixo em que a gestão estiver."""
    pagina = (documentacao.PASTA / "index.html").read_text()

    assert '<a class="voltar-a-gestao" href="../">' in pagina
    assert reverse("interface:lista") == INICIO.removesuffix("documentacao/")
