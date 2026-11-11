"""O barema da Mesa ao portal, num navegador de verdade (146, T028).

Como as outras jornadas, em três partes:

1. **Preparação** — o Edital com o barema do 14/2026 publicado na Etapa do marco e uma inscrição
   com os dois documentos, distribuída à avaliadora. Configurar e publicar o barema pela tela é o
   incremento A, verificado à mão no PR dele; aqui a jornada começa onde o B começa.
2. **Ações** — só no navegador: a avaliadora pontua a ficha em desktop e a 375 px, vê o total ao
   vivo, é recusada pelo pendente e conclui; o candidato, a 375 px, lê a pontuação por critério.
3. **Verificações** — na tela e no banco.

Nenhuma página pode ter violação da política de conteúdo no console — o total ao vivo é arquivo
estático justamente por isso —, e nenhuma rola na horizontal a 375 px.
"""

from decimal import Decimal

import pytest

expect = pytest.importorskip("playwright.sync_api", reason="sem o grupo opcional navegador").expect

from processo_seletivo.avaliacoes.models import Avaliacao  # noqa: E402
from processo_seletivo.resultados.application.consolidacao import consolidar  # noqa: E402
from tests.fixtures.barema import montar_marco_com_barema  # noqa: E402
from tests.fixtures.comissao import inscrever  # noqa: E402
from tests.fixtures.divulgacao import emitir, publicar_o_ato  # noqa: E402
from tests.fixtures.mesa import distribuir_para  # noqa: E402
from tests.fixtures.tela_do_navegador import CELULAR, Tela  # noqa: E402

pytestmark = pytest.mark.django_db(transaction=True)

SEED = 152
QUICKSTART = {
    "Diploma de Doutorado": "1",
    "Diploma de Mestrado": "0",
    "Especialização": "3",
    "Curso de formação de orientadores": "0",
    "Exercício de docência em EaD": "52",
}


@pytest.fixture
def tela(navegador, live_server, settings, request, raiz_de_arquivos):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    atual = Tela(navegador, live_server, request.node.name)
    yield atual
    atual.fechar()
    assert atual.violacoes == [], "violação da política de conteúdo no console"


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    cenario = montar_marco_com_barema(
        gestor, api_client, manager_headers, process_payload, seed=SEED, codigo="0152"
    )
    cenario["inscricoes"] = inscrever(
        cenario["edital"],
        2,
        primeiro=1521,
        perfil=cenario["perfil"],
        documentos=[cenario["titulos"], cenario["declaracao"]],
        modalidades=cenario["modalidade"],
    )
    distribuir_para(cenario, gestor, ["joao"], cenario["inscricoes"], chave="jornada-146")
    return cenario


def endereco_da_mesa(tela, cenario, inscricao):
    return (
        f"{tela.servidor.url}/gestao/minhas-etapas/{cenario['edital'].id}/{cenario['etapa']}"
        f"/inscricoes/{inscricao.id}/"
    )


def preencher(pagina, valores):
    for nome, valor in valores.items():
        rotulo = f"Quantidade — {nome}"
        campo = pagina.get_by_label(rotulo, exact=True)
        campo.fill(valor)


def sem_rolagem_horizontal(pagina):
    return pagina.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


def test_a_avaliadora_pontua_pela_ficha_e_o_candidato_le_por_criterio(tela, cenario, gestor):
    from django.urls import reverse

    primeira, segunda = cenario["inscricoes"]
    url = reverse(
        "interface:mesa-inscricao", args=[cenario["edital"].id, cenario["etapa"], primeira.id]
    )
    joao = tela.gestao("joao")
    joao.goto(f"{tela.servidor.url}{url}")
    ficha = joao.locator("[data-ficha-do-barema]")
    expect(ficha).to_be_visible()
    tela.capturar(joao, "ficha-vazia-desktop")

    # O total ao vivo, com o limite dito em texto — o Mestrado ainda em branco.
    preencher(joao, {k: v for k, v in QUICKSTART.items() if k != "Diploma de Mestrado"})
    expect(ficha.locator("[data-total-da-ficha]")).to_contain_text("70 de 100")
    expect(ficha).to_contain_text("limitada ao máximo")
    expect(ficha.locator("[data-pendentes-da-ficha]")).to_have_text(
        "Pendentes: Diploma de Mestrado."
    )
    tela.capturar(joao, "ficha-parcial-desktop")

    # Concluir com o pendente: recusado, nomeando-o, e o digitado volta.
    joao.get_by_role("button", name="Concluir avaliação").click()
    expect(joao.get_by_role("alert")).to_contain_text("Diploma de Mestrado")
    expect(
        joao.get_by_label("Quantidade — Exercício de docência em EaD", exact=True)
    ).to_have_value("52")
    tela.capturar(joao, "recusa-do-pendente")

    joao.get_by_label("Quantidade — Diploma de Mestrado", exact=True).fill("0")
    joao.get_by_label("Parecer").fill("Títulos conferidos pela ficha.")
    joao.get_by_role("button", name="Concluir avaliação").click()
    expect(joao.locator("p.sucesso")).to_contain_text("concluída")

    avaliacao = Avaliacao.objects.get(inscricao_id=primeira.id)
    assert avaliacao.estado == Avaliacao.Estado.CONCLUIDA
    assert avaliacao.pontuacao == Decimal("70.0000")

    # A concluída é leitura, com as parcelas.
    joao.goto(f"{tela.servidor.url}{url}")
    expect(joao.locator(".ficha-do-barema")).to_contain_text("limitada ao máximo")
    tela.capturar(joao, "concluida-desktop")

    # A segunda inscrição, a 375 px: a ficha empilha e a página não rola de lado.
    celular = tela._nova(CELULAR)
    celular.context.add_cookies(joao.context.cookies())
    celular.goto(
        f"{tela.servidor.url}"
        + reverse(
            "interface:mesa-inscricao",
            args=[cenario["edital"].id, cenario["etapa"], segunda.id],
        )
    )
    # O erro dito na linha antes de enviar: pontos fracionários numa quantidade.
    preencher(celular, {"Especialização": "1.5"})
    expect(celular.locator("[data-criterio-da-ficha]").nth(2)).to_contain_text(
        "a quantidade é um número inteiro"
    )
    tela.capturar(celular, "erro-na-linha-375px")
    preencher(celular, {**QUICKSTART, "Especialização": "1", "Exercício de docência em EaD": "20"})
    expect(celular.locator("[data-total-da-ficha]")).to_contain_text("45 de 100")
    assert sem_rolagem_horizontal(celular)
    tela.capturar(celular, "ficha-375px")
    # Pelo teclado, e não pelo clique: depois da captura de página inteira, o clique no rodapé do
    # viewport emulado pode cair fora do botão e o envio some sem erro — é do emulador, não da tela.
    celular.get_by_role("button", name="Concluir avaliação").focus()
    celular.keyboard.press("Enter")
    expect(celular.locator("p.sucesso")).to_contain_text("concluída")

    # A presidência reabre a primeira: a ficha volta preenchida, para reconfirmação (FR-5222).
    from processo_seletivo.avaliacoes.application.avaliacao import reabrir

    reaberta = reabrir(
        actor=gestor,
        processo_id=cenario["processo"].id,
        avaliacao_id=avaliacao.id,
        motivo="Conferência da docência declarada.",
        expected_revision=Avaliacao.objects.get(pk=avaliacao.pk).revision,
        idempotency_key="jornada-146-reabrir",
        correlation_id="jornada",
    )
    joao.goto(f"{tela.servidor.url}{url}")
    expect(
        joao.get_by_label("Quantidade — Exercício de docência em EaD", exact=True)
    ).to_have_value("52")
    expect(joao.locator("[data-total-da-ficha]")).to_contain_text("70 de 100")
    tela.capturar(joao, "reaberta-desktop")
    joao.get_by_role("button", name="Concluir avaliação").focus()
    joao.keyboard.press("Enter")
    expect(joao.locator("p.sucesso")).to_contain_text("concluída")
    assert Avaliacao.objects.get(pk=reaberta.pk).estado == Avaliacao.Estado.CONCLUIDA

    # A presidência consolida, emite e publica o preliminar pelos comandos de sempre.
    consolidar(
        actor=gestor,
        processo_id=cenario["processo"].id,
        edital_id=cenario["edital"].id,
        etapa_id=cenario["etapa"],
        inscricao_ids=[primeira.id, segunda.id],
        idempotency_key="jornada-146-consolidar",
        correlation_id="jornada",
    )
    ato = emitir(cenario, gestor, chave="jornada-146-emitir")
    publicar_o_ato(cenario, chave="jornada-146-publicar", ato=ato)

    candidato = tela.candidato(primeira)
    candidato.goto(f"{tela.servidor.url}" + reverse("portal:acompanhamento", args=[primeira.id]))
    tabela = candidato.locator("ul.ficha-da-etapa")
    expect(tabela).to_contain_text("Exercício de docência em EaD")
    expect(tabela).to_contain_text("limitada ao máximo")
    assert sem_rolagem_horizontal(candidato)
    tela.capturar(candidato, "portal-375px")
