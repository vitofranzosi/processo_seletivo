"""A experiência da convocação num navegador de verdade (121, SC-1152, SC-1153, SC-1156, SC-1162,
SC-1163).

O que só um navegador prova: onde a ação termina na primeira tela, se a página rola na horizontal
com a fonte e o zoom aumentados, para onde o foco vai depois do envio — **com o script desligado**,
porque a FR-3870 diz que o navegador o leva à confirmação sozinho —, e o nome do arquivo escolhido.
O percurso do link ao código à convocação também passa aqui, inteiro, numa janela sem sessão.

Os cenários são os da `118` (`tests/fixtures/jornada_do_convocado.py`) e o corr, que é o A corrigido
pela `120`. Toda página é vigiada pela política de conteúdo, como nas jornadas da `115`.
"""

import re

import pytest

expect = pytest.importorskip("playwright.sync_api", reason="sem o grupo opcional navegador").expect

from django.core import mail  # noqa: E402
from django.urls import reverse  # noqa: E402

from tests.fixtures import documentos_da_convocacao as cenarios  # noqa: E402
from tests.fixtures import jornada_do_convocado as jornada  # noqa: E402
from tests.navegador.test_jornada_dos_documentos_da_convocacao import (  # noqa: E402
    CELULAR,
    DESKTOP,
    Tela,
    sem_rolagem_horizontal,
)

pytestmark = pytest.mark.django_db(transaction=True)

ESTREITA = {"width": 320, "height": 812}


class TelaDaConvocacao(Tela):
    """A `Tela` da `115`, com as opções do contexto que a `121` precisa: o script desligado e a
    densidade de pixels do zoom."""

    def _nova(self, viewport, **opcoes):
        contexto = self._navegador.new_context(viewport=viewport, **opcoes)
        self._contextos.append(contexto)
        pagina = contexto.new_page()
        pagina.set_default_timeout(10_000)
        pagina.on(
            "console",
            lambda mensagem: (
                self.violacoes.append(mensagem.text)
                if "Content Security Policy" in mensagem.text
                else None
            ),
        )
        return pagina

    def candidato(self, inscricao, viewport=CELULAR, **opcoes):
        from django.contrib.sessions.backends.db import SessionStore
        from django.utils import timezone

        from processo_seletivo.identidade.models import CandidateIdentity
        from processo_seletivo.portal.identidade import CHAVE_SESSAO

        registro, _ = CandidateIdentity.objects.get_or_create(
            subject=inscricao.identity_subject, defaults={"created_at": timezone.now()}
        )
        sessao = SessionStore()
        sessao[CHAVE_SESSAO] = str(registro.pk)
        sessao.save()
        pagina = self._nova(viewport, **opcoes)
        pagina.context.add_cookies(
            [{"name": "sessionid", "value": sessao.session_key, "url": self.servidor.url}]
        )
        return pagina

    def sem_sessao(self, viewport=CELULAR):
        return self._nova(viewport)


@pytest.fixture
def tela(navegador, live_server, settings, request, raiz_de_arquivos):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    mail.outbox.clear()
    atual = TelaDaConvocacao(navegador, live_server, request.node.name)
    yield atual
    atual.fechar()
    assert atual.violacoes == [], "violação da política de conteúdo no console"


@pytest.fixture
def fx(gestor, api_client, manager_headers, process_payload):
    return jornada.Montagem(gestor, api_client, manager_headers, process_payload)


@pytest.fixture
def pdfs(tmp_path):
    def criar(nome, corpo=None, extensao="pdf"):
        caminho = tmp_path / f"{nome}.{extensao}"
        caminho.write_bytes(corpo if corpo is not None else b"%PDF-1.4\n" + nome.encode())
        return str(caminho)

    return criar


def montar(letra, fx, gestor):
    """O cenário pela letra; `corr` é o A, comunicado, corrigido pela `120`."""
    if letra != "corr":
        return jornada.montar(letra, fx)
    from processo_seletivo.convocacao.models import Convocacao
    from tests.integration.convocacao.test_correcao_da_convocacao import corrigir

    cenario = jornada.montar("A", fx)
    corrigir(cenario.edital, gestor, cenario.convocacao, chave="j121-corr")
    cenario.convocacao = Convocacao.objects.get(convocacao_anterior=cenario.convocacao)
    cenario.letra = "corr"
    return cenario


def abrir(tela, pagina, cenario):
    pagina.goto(tela.servidor.url + reverse("portal:convocacao", args=[cenario.pessoa.id]))
    expect(pagina.locator("main h1")).to_be_visible()


@pytest.mark.parametrize("letra", ["A", "C1", "C2", "F", "J", "corr"])
def test_a_acao_na_primeira_tela_com_folga(tela, fx, gestor, letra):
    """SC-1152: a 375 × 812, com a fonte padrão, a ação termina dentro da primeira tela com folga
    de pelo menos uma linha de texto corrido."""
    cenario = montar(letra, fx, gestor)
    pagina = tela.candidato(cenario.pessoa)
    abrir(tela, pagina, cenario)

    linha = pagina.evaluate("parseFloat(getComputedStyle(document.body).lineHeight)")
    acao = pagina.locator(".acao-da-chamada a").bounding_box()

    assert acao["y"] + acao["height"] + linha <= CELULAR["height"], (acao, linha)
    expect(pagina.locator(".acao-da-chamada a")).to_have_text("Ver o que preciso fazer")
    tela.capturar(pagina, f"primeira-tela-{letra}")


@pytest.mark.parametrize("letra", ["C1", "F", "G", "I1", "corr"])
def test_sem_rolagem_horizontal_a_320_com_fonte_e_zoom(tela, fx, gestor, letra):
    """SC-1153 (WCAG 1.4.10): a 320 px, com a fonte do navegador a 150 % e com zoom de 200 %.

    O zoom de 200 % numa janela de 640 px é uma página de 320 px de CSS com o dobro de pixels por
    ponto: é o que o contexto com `device_scale_factor=2` reproduz. A fonte a 150 % é a do elemento
    raiz, que o portal respeita por usar `rem`.
    """
    cenario = montar(letra, fx, gestor)
    for opcoes, fonte in (({}, None), ({}, "150%"), ({"device_scale_factor": 2}, None)):
        pagina = tela.candidato(cenario.pessoa, viewport=ESTREITA, **opcoes)
        with cenario.relogio():
            abrir(tela, pagina, cenario)
            if fonte:
                pagina.evaluate(f"document.documentElement.style.fontSize = '{fonte}'")
            sem_rolagem_horizontal(pagina)
        tela.capturar(pagina, f"estreita-{letra}-{fonte or opcoes or 'padrao'}")


def test_do_link_ao_codigo_a_convocacao(tela, fx, gestor):
    """SC-1156, FR-3880: a janela sem sessão, o acesso que diz para onde se vai, o código que chega
    numa mensagem separada, e a convocação, sem passar pela lista."""
    from processo_seletivo.identidade.application import associacao
    from processo_seletivo.identidade.domain.enderecos import canonizar
    from processo_seletivo.identidade.models import CandidateIdentity

    cenario = montar("C1", fx, gestor)
    pessoa = cenario.pessoa
    identidade, _ = CandidateIdentity.objects.get_or_create(
        subject=pessoa.identity_subject, defaults={"created_at": pessoa.created_at}
    )
    associacao.associar_credencial(identidade, canonizar(pessoa.email), pessoa.email)
    destino = reverse("portal:convocacao", args=[pessoa.id])
    pagina = tela.sem_sessao()

    pagina.goto(tela.servidor.url + destino)
    expect(pagina.get_by_role("heading", name="Entre para ver a sua convocação")).to_be_visible()
    expect(
        pagina.get_by_text("Depois do código, você vai direto para a convocação.")
    ).to_be_visible()
    tela.capturar(pagina, "acesso-a-caminho-da-convocacao")
    pagina.get_by_label("Seu e-mail").fill(pessoa.email)
    pagina.get_by_role("button", name="Receber código").click()
    expect(
        pagina.get_by_text("Depois do código, você vai direto para a convocação.")
    ).to_be_visible()
    codigo = re.search(r"\b(\d{6})\b", mail.outbox[-1].body).group(1)
    pagina.get_by_label("Código de seis dígitos").fill(codigo)
    pagina.get_by_role("button", name="Entrar", exact=True).click()

    expect(pagina).to_have_url(tela.servidor.url + destino)
    expect(pagina.get_by_role("heading", name="Você foi convocado!", level=1)).to_be_visible()


def test_sem_script_o_foco_vai_a_confirmacao(tela, fx, gestor, pdfs):
    """SC-1162, FR-3870: o navegador foca o alvo da âncora `#confirmacao`, focável, sem script."""
    cenario = montar("C1", fx, gestor)
    item = cenarios.item(cenario.convocacao, cenarios.CERTIDAO)
    pagina = tela.candidato(cenario.pessoa, java_script_enabled=False)
    abrir(tela, pagina, cenario)

    cartao = pagina.locator(f"#item-{item.id}")
    cartao.locator("input[type=file]").set_input_files(pdfs("certidao"))
    cartao.get_by_role("button", name="Enviar").click()
    pagina.wait_for_load_state()

    assert pagina.url.endswith("#confirmacao")
    confirmacao = pagina.locator("#confirmacao")
    expect(confirmacao).to_be_focused()
    expect(confirmacao).to_contain_text("Recebemos: Certidão de nascimento ou casamento, em ")
    expect(confirmacao).to_contain_text("O arquivo aguarda a conferência da comissão.")
    expect(confirmacao).to_contain_text("Próxima tarefa:")
    texto = confirmacao.inner_text().lower()
    for proibido in ("aceito", "aprovado", "conferido", "atendido"):
        assert proibido not in texto, proibido
    tela.capturar(pagina, "confirmacao-sem-script")


def test_com_script_o_foco_vai_a_recusa_no_cartao(tela, fx, gestor, pdfs):
    """SC-1162, FR-3871: a recusa no cartão do item, com o foco nela, e sem confirmação."""
    cenario = montar("C1", fx, gestor)
    item = cenarios.item(cenario.convocacao, cenarios.CERTIDAO)
    pagina = tela.candidato(cenario.pessoa)
    abrir(tela, pagina, cenario)

    cartao = pagina.locator(f"#item-{item.id}")
    cartao.locator("input[type=file]").set_input_files(pdfs("foto", b"\xff\xd8\xff", "jpg"))
    cartao.get_by_role("button", name="Enviar").click()
    pagina.wait_for_load_state()

    recusa = pagina.locator(f"#item-{item.id} [data-recusa]")
    expect(recusa).to_be_focused()
    expect(pagina.locator("#confirmacao")).to_have_count(0)
    tela.capturar(pagina, "recusa-no-cartao")


def test_escolhido_o_arquivo_o_cartao_diz_o_nome(tela, fx, gestor, pdfs):
    """SC-1163: o nome do arquivo escolhido, e zero "Nenhum arquivo escolhido" no cartão."""
    cenario = montar("C1", fx, gestor)
    item = cenarios.item(cenario.convocacao, cenarios.HISTORICO)
    pagina = tela.candidato(cenario.pessoa, viewport=DESKTOP)
    abrir(tela, pagina, cenario)

    cartao = pagina.locator(f"#item-{item.id}")
    cartao.locator("input[type=file]").set_input_files(pdfs("historico-escolar"))

    expect(cartao.locator("[data-nome-do-arquivo]")).to_have_text("historico-escolar.pdf")
    expect(cartao.get_by_text("Nenhum arquivo escolhido")).to_have_count(0)
