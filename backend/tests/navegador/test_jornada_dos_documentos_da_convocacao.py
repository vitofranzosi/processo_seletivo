"""Os documentos da convocação de ponta a ponta, num navegador de verdade (115, SC-1081, SC-1089).

Como as jornadas da `107`, em três partes:

1. **Preparação** — o certame até a convocação, pelas *fixtures* da `019`; a pessoa convocada com a
   sessão do portal aberta, como depois do código de acesso;
2. **Ações** — só no navegador: o candidato a 375 px, a comissão em desktop;
3. **Verificações** — na tela, no banco e na trilha.

Nenhuma página pode ter violação da política de conteúdo no console, e a do candidato não pode
rolar na horizontal. `NAVEGADOR_CAPTURAS=<pasta>` grava as telas de cada passo marcado.
"""

import os
import re
import time
from pathlib import Path

import pytest

expect = pytest.importorskip("playwright.sync_api", reason="sem o grupo opcional navegador").expect

from processo_seletivo.convocacao.domain import nomes  # noqa: E402
from processo_seletivo.convocacao.models import (  # noqa: E402
    ConferenciaDeDocumento,
    DesfechoDaConvocacao,
)
from tests.fixtures import documentos_da_convocacao as cenarios  # noqa: E402
from tests.fixtures.corte import MARCO  # noqa: E402
from tests.fixtures.documentos_da_convocacao import (  # noqa: E402
    CERTIDAO,
    CERTIFICADO,
    CERTIFICADO_DO_MEDIO,
    HISTORICO,
    IDENTIDADE,
    RESIDENCIA,
)

pytestmark = pytest.mark.django_db(transaction=True)

CELULAR = {"width": 375, "height": 812}
DESKTOP = {"width": 1280, "height": 900}


class Tela:
    """Um navegador por pessoa, com o console vigiado e as capturas do caso."""

    def __init__(self, navegador, servidor, caso):
        self._navegador = navegador
        self.servidor = servidor
        self._capturas = os.getenv("NAVEGADOR_CAPTURAS")
        self._caso = re.sub(r"\W+", "-", caso)
        self._passo = 0
        self._contextos = []
        self.violacoes = []

    def _nova(self, viewport):
        contexto = self._navegador.new_context(viewport=viewport)
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

    def gestao(self, subject, papeis=(), viewport=DESKTOP):
        """A sessão da gestão pelo seletor de identidade, como `identificar` dos testes de tela.

        O seletor é a entrada de demonstração que o ambiente local oferece, e a sessão que ele abre
        é a mesma que o navegador leva — o cookie é só o transporte.
        """
        from django.test import Client
        from django.urls import reverse

        cliente = Client()
        resposta = cliente.post(
            reverse("interface:identificar"), {"subject": subject, "papeis": list(papeis)}
        )
        assert resposta.status_code == 302, resposta.content
        pagina = self._nova(viewport)
        pagina.context.add_cookies(
            [
                {
                    "name": "sessionid",
                    "value": cliente.cookies["sessionid"].value,
                    "url": self.servidor.url,
                }
            ]
        )
        return pagina

    def candidato(self, inscricao, viewport=CELULAR):
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
        pagina = self._nova(viewport)
        pagina.context.add_cookies(
            [{"name": "sessionid", "value": sessao.session_key, "url": self.servidor.url}]
        )
        return pagina

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
def tela(navegador, live_server, settings, request, raiz_de_arquivos):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    atual = Tela(navegador, live_server, request.node.name)
    yield atual
    atual.fechar()
    assert atual.violacoes == [], "violação da política de conteúdo no console"


@pytest.fixture
def pdfs(tmp_path):
    def criar(nome, corpo=None):
        caminho = tmp_path / f"{nome}.pdf"
        caminho.write_bytes(b"%PDF-1.4\n" + (corpo or nome.encode()))
        return str(caminho)

    return criar


def sem_rolagem_horizontal(pagina):
    largura = pagina.evaluate("document.documentElement.scrollWidth")
    assert largura <= pagina.viewport_size["width"], f"a página rola na horizontal ({largura} px)"


def abrir_convocacao(pagina, servidor, pessoa):
    from django.urls import reverse

    from processo_seletivo.portal import obrigacoes

    pagina.goto(servidor.url + reverse("portal:convocacao", args=[pessoa.id]))
    # O heading de primeiro nível é o título por estado (121, FR-3858), e não mais "Convocação".
    titulo = pagina.locator("main h1")
    expect(titulo).to_be_visible()
    assert titulo.inner_text() in obrigacoes.TITULOS.values(), titulo.inner_text()


def enviar(pagina, item_id, arquivo):
    cartao = pagina.locator(f"#item-{item_id}")
    resumo = cartao.locator("details.envio-de-novo:not([open]) > summary")
    if resumo.count():
        resumo.click()
    cartao.locator("input[type=file]").set_input_files(arquivo)
    cartao.get_by_role("button", name="Enviar").click()
    pagina.wait_for_load_state()


def pagina_dos_documentos(gestao, servidor, edital, convocacao):
    from django.urls import reverse

    gestao.goto(servidor.url + reverse("interface:convocacao", args=[edital.id, MARCO]))
    gestao.locator(f"a[href*='/convocacao/{convocacao.id}/documentos']").first.click()
    expect(gestao.get_by_role("heading", name="Documentos da convocação")).to_be_visible()


def abrir_e_conferir(gestao, item_id, resultado, motivo=""):
    """Abre a versão vigente — a abertura que o "conforme" exige — e registra a conferência."""
    cartao = gestao.locator(f"#item-{item_id}")
    if resultado == "CONFORME":
        endereco = cartao.get_by_role("link", name="Abrir").last.get_attribute("href")
        resposta = gestao.context.request.get(gestao.url.split("/gestao/")[0] + endereco)
        assert resposta.ok and resposta.body().startswith(b"%PDF")
        gestao.reload()
        cartao = gestao.locator(f"#item-{item_id}")
        expect(cartao.get_by_text("aberto por você").last).to_be_visible()
    fechado = cartao.locator("details.como-preencher:not([open]) > summary").filter(
        has_text=re.compile("Conferir a versão|Registrar outra conferência|Conferir este documento")
    )
    if fechado.count():
        fechado.click()
    cartao.locator(f"input[name=resultado][value={resultado}]").check()
    if motivo:
        cartao.locator("textarea[name=motivo]").fill(motivo)
    cartao.get_by_role("button", name="Registrar conferência").click()
    expect(gestao.get_by_text("Conferência registrada.")).to_be_visible()


def registrar_aceite(gestao, servidor, edital):
    from django.urls import reverse

    gestao.goto(servidor.url + reverse("interface:convocacao", args=[edital.id, MARCO]))
    # Pronta para o desfecho, o formulário já vem aberto no cartão (143, FR-5013): clicar no
    # resumo o fecharia. Nos outros passos, ele vem recolhido, como antes.
    desfecho = gestao.locator("details.desfecho-da-chamada").first
    if not desfecho.evaluate("elemento => elemento.open"):
        desfecho.locator("summary", has_text="Registrar desfecho").click()
    gestao.locator("select[name=especie]").first.select_option("ACEITE")
    gestao.locator("textarea[name=fundamento]").first.fill("Documentação conferida e conforme.")
    gestao.get_by_role("button", name="Registrar desfecho").first.click()
    gestao.wait_for_load_state()
    # O fundamento chega ao candidato, e o desfecho passa sempre pela conferência do texto (FR-3993
    # da `125`, D-004): o primeiro clique só mostra a prévia; o ato é o da confirmação.
    gestao.locator("#conferir-o-texto button[value=confirmar]").click()
    gestao.wait_for_load_state()


def _item(convocacao, requisito):
    return cenarios.item(convocacao, requisito).id


# --- US1: o aluno, no molde do 72/2026 ----------------------------------------------------------


def test_aluno_envia_corrige_a_pendencia_e_fica_apto(
    tela, pdfs, gestor, api_client, manager_headers, process_payload
):
    from django.utils import timezone

    cenario = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_aluno(),
        prefixo="nav-aluno-115",
    )
    edital, _, _ = cenario
    pessoa, convocacao = cenarios.convocar_primeira(
        cenario, gestor, vencimento=timezone.now() + timezone.timedelta(days=5)
    )
    cenarios.comunicar(edital, gestor, convocacao)
    candidata = tela.candidato(pessoa)
    comissao = tela.gestao("carlos", ["gestor"])

    # O candidato vê o que apresentar, e envia três dos quatro, com o histórico incompleto.
    abrir_convocacao(candidata, tela.servidor, pessoa)
    # Os blocos da `118` (FR-3735) no lugar da lista única; "Falta enviar." continua.
    # A chamada da 121 no lugar de "O que fazer agora" (FR-3735 da 118, revista).
    expect(candidata.get_by_role("heading", name="Você foi convocado!", level=1)).to_be_visible()
    expect(candidata.get_by_text("Falta enviar")).to_have_count(4)
    sem_rolagem_horizontal(candidata)
    tela.capturar(candidata, "candidato-lista")
    for requisito, nome in (
        (CERTIDAO, "certidao"),
        (HISTORICO, "historico-incompleto"),
        (CERTIFICADO_DO_MEDIO, "certificado"),
    ):
        enviar(candidata, _item(convocacao, requisito), pdfs(nome))
        # A volta é a confirmação da 121, no topo da chamada (FR-3870).
        expect(candidata.locator("#confirmacao")).to_contain_text(
            "O arquivo aguarda a conferência da comissão."
        )
    tela.capturar(candidata, "candidato-enviados")

    # A comissão confere: dois conformes, o histórico pendente, e o aceite recusado.
    pagina_dos_documentos(comissao, tela.servidor, edital, convocacao)
    tela.capturar(comissao, "comissao-documentos")
    abrir_e_conferir(comissao, _item(convocacao, CERTIDAO), "CONFORME")
    abrir_e_conferir(comissao, _item(convocacao, CERTIFICADO_DO_MEDIO), "CONFORME")
    abrir_e_conferir(comissao, _item(convocacao, HISTORICO), "PENDENTE", "Falta a página 2.")
    tela.capturar(comissao, "comissao-pendencia")
    registrar_aceite(comissao, tela.servidor, edital)
    expect(
        comissao.get_by_text("todo documento obrigatório da convocação precisa estar")
    ).to_be_visible()
    assert not DesfechoDaConvocacao.objects.filter(convocacao=convocacao).exists()

    # O candidato lê a pendência e complementa; envia o que faltava.
    abrir_convocacao(candidata, tela.servidor, pessoa)
    expect(candidata.get_by_text("Precisa de correção: Falta a página 2.")).to_be_visible()
    tela.capturar(candidata, "candidato-pendencia")
    enviar(candidata, _item(convocacao, HISTORICO), pdfs("historico-completo"))
    enviar(candidata, _item(convocacao, RESIDENCIA), pdfs("residencia"))
    sem_rolagem_horizontal(candidata)

    # A comissão confere o resto e registra o aceite.
    pagina_dos_documentos(comissao, tela.servidor, edital, convocacao)
    expect(comissao.get_by_text("Complementado, aguardando conferência")).to_be_visible()
    abrir_e_conferir(comissao, _item(convocacao, HISTORICO), "CONFORME")
    abrir_e_conferir(comissao, _item(convocacao, RESIDENCIA), "CONFORME")
    registrar_aceite(comissao, tela.servidor, edital)
    expect(comissao.get_by_text("Apto para formalização").first).to_be_visible()
    tela.capturar(comissao, "comissao-apto")

    desfecho = DesfechoDaConvocacao.objects.get(convocacao=convocacao)
    assert desfecho.especie == nomes.ACEITE
    assert ConferenciaDeDocumento.objects.filter(item__chamada=convocacao).count() == 5


# --- US2 e US5: o bolsista, no molde do 146/2025, e a alocação à conferência --------------------


def test_bolsista_devolve_a_ficha_o_alocado_confere_e_a_presidencia_aceita(
    tela, pdfs, gestor, api_client, manager_headers, process_payload
):
    from django.urls import reverse

    from processo_seletivo.editais.models.documentos import DocumentoExigido
    from tests.fixtures.anexos import criar_anexo
    from tests.fixtures.publicacao import publish_original

    def ligar_o_modelo(edital):
        anexo = criar_anexo(edital, rotulo="ANEXO I — FICHA E TERMO DO BOLSISTA")
        DocumentoExigido.objects.filter(edital=edital, key="ficha-termo").update(anexo=anexo)

    def com_o_modelo(api_client, manager_headers, process_payload, *, draft=None):
        return publish_original(
            api_client,
            manager_headers,
            process_payload,
            draft=draft,
            antes_de_submeter=ligar_o_modelo,
        )

    cenario = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_bolsista(),
        prefixo="nav-bolsista-115",
        publicar=com_o_modelo,
    )
    edital, _, _ = cenario
    pessoa, convocacao = cenarios.convocar_primeira(cenario, gestor)
    candidato = tela.candidato(pessoa)
    gestora = tela.gestao("carlos", ["gestor"])
    membro = tela.gestao("joao")
    presidencia = tela.gestao("maria")

    # A gestão aloca o membro à conferência, pela tela das alocações.
    gestora.goto(tela.servidor.url + reverse("interface:alocacoes", args=[edital.processo_id]))
    secao = gestora.locator("section", has_text="Conferência dos documentos da convocação")
    from processo_seletivo.comissoes.models import MembroComissao

    joao = MembroComissao.objects.get(processo=edital.processo, identity_subject="joao")
    secao.locator("select[name=membro_id]").select_option(str(joao.id))
    secao.get_by_role("button", name="Alocar à conferência").click()
    gestora.wait_for_load_state()
    tela.capturar(gestora, "gestao-alocacao")

    # O bolsista baixa o modelo e devolve a ficha assinada.
    abrir_convocacao(candidato, tela.servidor, pessoa)
    expect(candidato.get_by_role("link", name=re.compile("Baixar o modelo"))).to_be_visible()
    expect(candidato.get_by_text("Requerimento de Matrícula")).to_have_count(0)
    tela.capturar(candidato, "bolsista-lista")
    enviar(candidato, _item(convocacao, cenarios.FICHA), pdfs("ficha-assinada"))
    sem_rolagem_horizontal(candidato)

    # O membro alocado confere, e não vê o formulário de desfecho.
    pagina_dos_documentos(membro, tela.servidor, edital, convocacao)
    abrir_e_conferir(membro, _item(convocacao, cenarios.FICHA), "CONFORME")
    tela.capturar(membro, "membro-conferiu")
    membro.goto(tela.servidor.url + reverse("interface:convocacao", args=[edital.id, MARCO]))
    expect(membro.locator("summary", has_text="Registrar desfecho")).to_have_count(0)

    # A presidência registra o aceite.
    registrar_aceite(presidencia, tela.servidor, edital)
    expect(presidencia.get_by_text("Apto para formalização").first).to_be_visible()
    corpo = presidencia.content().lower()
    assert "bolsa concedida" not in corpo and "vinculad" not in corpo

    assert DesfechoDaConvocacao.objects.get(convocacao=convocacao).registrado_por == "maria"
    assert ConferenciaDeDocumento.objects.get(item__chamada=convocacao).conferido_por == "joao"


# --- US3: o certificado da inscrição, no molde do 89/2026 ---------------------------------------


def test_o_certificado_da_inscricao_atende_sem_reenvio(
    tela, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos
):
    cenario = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_certificado(),
        documentos_da_inscricao=(IDENTIDADE, CERTIFICADO),
        prefixo="nav-certificado-115",
    )
    edital, _, _ = cenario
    pessoa, convocacao = cenarios.convocar_primeira(cenario, gestor)
    arquivos = cenarios.arquivos_no_armazenamento(raiz_de_arquivos)
    candidata = tela.candidato(pessoa)
    comissao = tela.gestao("carlos", ["gestor"])

    abrir_convocacao(candidata, tela.servidor, pessoa)
    # "Atendido" antes da conferência saiu (FR-3746 da `118`): ela já o enviou, e a comissão vai
    # conferir.
    expect(
        candidata.get_by_text(re.compile("Você já enviou este documento na inscrição"))
    ).to_be_visible()
    tela.capturar(candidata, "candidata-aproveitado")

    pagina_dos_documentos(comissao, tela.servidor, edital, convocacao)
    expect(comissao.get_by_text(re.compile("documento enviado na inscrição em"))).to_be_visible()
    abrir_e_conferir(comissao, _item(convocacao, cenarios.CERTIFICADO_NA_CONVOCACAO), "CONFORME")
    tela.capturar(comissao, "comissao-aproveitado")
    registrar_aceite(comissao, tela.servidor, edital)
    expect(comissao.get_by_text("Apto para formalização").first).to_be_visible()

    assert cenarios.arquivos_no_armazenamento(raiz_de_arquivos) == arquivos, "sem cópia (SC-1083)"


# --- US8: a chamada nova aproveita o que a anterior recebeu -------------------------------------


def test_a_chamada_nova_aproveita_e_confere_de_novo(
    tela, gestor, api_client, manager_headers, process_payload
):
    from processo_seletivo.convocacao.models import Convocacao
    from tests.fixtures.convocacao import apurar, convocar
    from tests.fixtures.corte import regra
    from tests.integration.convocacao.test_aproveitamento_entre_chamadas import (
        _chamada_nova_da_reclassificada,
    )

    cenario = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_aluno(),
        prefixo="nav-chamada-115",
        geral=2,
        cut=regra(surplusCount=1),
    )
    edital, _, _ = cenario

    def na_primeira(pessoa, primeira):
        cenarios.apresentar(pessoa, primeira, CERTIDAO, corpo=b"certidao")
        cenarios.conferir(gestor, primeira, CERTIDAO, "CONFORME", chave="nav-c1")

    pessoa, _, segunda = _chamada_nova_da_reclassificada(cenario, gestor, na_primeira)
    assert Convocacao.objects.filter(inscricao=pessoa).count() == 2
    assert apurar and convocar  # o percurso é o da integração, pelo caminho real
    candidata = tela.candidato(pessoa)
    comissao = tela.gestao("carlos", ["gestor"])

    abrir_convocacao(candidata, tela.servidor, pessoa)
    expect(candidata.get_by_text(re.compile("Aproveitado da chamada anterior"))).to_be_visible()
    tela.capturar(candidata, "candidata-chamada-nova")

    pagina_dos_documentos(comissao, tela.servidor, edital, segunda)
    cartao = comissao.locator(f"#item-{_item(segunda, CERTIDAO)}")
    expect(cartao.get_by_text("Recebido, aguardando conferência")).to_be_visible()
    cartao.locator("input[name=resultado][value=CONFORME]").check()
    cartao.get_by_role("button", name="Registrar conferência").click()
    expect(
        comissao.get_by_text("Abra o documento antes de conferi-lo como conforme.")
    ).to_be_visible()
    abrir_e_conferir(comissao, _item(segunda, CERTIDAO), "CONFORME")
    tela.capturar(comissao, "comissao-chamada-nova")


# --- US4: o prazo, e nada automático -----------------------------------------------------------


def test_depois_do_prazo_nada_se_envia_e_nada_se_decide_sozinho(
    tela, gestor, api_client, manager_headers, process_payload
):
    from django.utils import timezone

    cenario = cenarios.montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        documentos=cenarios.documentos_do_aluno(),
        prefixo="nav-prazo-115",
    )
    edital, _, _ = cenario
    pessoa, convocacao = cenarios.convocar_primeira(
        cenario, gestor, vencimento=timezone.now() + timezone.timedelta(seconds=2)
    )
    cenarios.comunicar(edital, gestor, convocacao)
    time.sleep(3)
    candidata = tela.candidato(pessoa)

    abrir_convocacao(candidata, tela.servidor, pessoa)
    # O núcleo único do vencido (FR-3748 da `118`).
    expect(
        candidata.get_by_text(
            re.compile("O prazo terminou em .* quem registra o resultado é a comissão.")
        )
    ).to_be_visible()
    expect(candidata.get_by_text("Escolher arquivo PDF")).to_have_count(0)
    tela.capturar(candidata, "candidata-prazo-vencido")

    assert not DesfechoDaConvocacao.objects.filter(convocacao=convocacao).exists()
