"""A jornada da SC-1165, num navegador de verdade (122).

> O operador realiza o sorteio e divulga os resultados dos três recortes válidos, identifica o que
> já foi publicado e conclui o trabalho sem receber cobrança sobre a lista excedente. Se consultar
> um registro antigo dessa lista, entende sua origem e por que ele não participa da operação atual.

Em três partes, como as jornadas da `115` e da `120`:

1. **Preparação** — pelas *fixtures*: o Edital do caso de 05/11 (AC apontada como a ampla), os três
   recortes sorteados e o ato que o sorteio fazia em AC antes da `122`;
2. **Ações** — só no navegador: a presidência confere a tela do sorteio; o Publicador puro sai da
   página do Edital, chega ao quadro e divulga os três recortes, um a um;
3. **Verificações** — na tela e no banco. Nenhuma página pode ter violação da política de conteúdo.
"""

import pytest

expect = pytest.importorskip("playwright.sync_api", reason="sem o grupo opcional navegador").expect

from django.urls import reverse  # noqa: E402

from processo_seletivo.divulgacao.models import PublicacaoResultado  # noqa: E402
from tests.fixtures.recorte_excedente import LISTA_AC, certame_com_ac  # noqa: E402
from tests.navegador.test_jornada_dos_documentos_da_convocacao import Tela  # noqa: E402

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def tela(navegador, live_server, settings, request):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    atual = Tela(navegador, live_server, request.node.name)
    yield atual
    atual.fechar()
    assert atual.violacoes == [], "violação da política de conteúdo no console"


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload):
    return certame_com_ac(
        gestor, api_client, manager_headers, process_payload, acervo=True, prefixo="nav-122"
    )


def test_a_jornada_dos_tres_recortes_sem_cobranca_da_lista_excedente(tela, certame):
    edital, marco = certame["edital"], certame["marco"]
    base = tela.servidor.url

    # A presidência confere o sorteio: três recortes, e o registro antigo à parte, explicado.
    presidencia = tela.gestao("maria")
    presidencia.goto(base + reverse("interface:sorteio", args=[edital.id, marco]))
    recortes = presidencia.locator("section[aria-labelledby='titulo-recortes'] h3")
    expect(recortes).to_have_count(3)
    historico = presidencia.locator("section[aria-labelledby='titulo-historico-excedente']")
    expect(historico).to_contain_text("dava lista própria à Modalidade apontada como a ampla")
    expect(historico.locator("button")).to_have_count(0)
    tela.capturar(presidencia, "sorteio")

    # O Publicador puro: da página do Edital ao quadro, por um caminho só.
    publicador = tela.gestao("paula.publicadora", ["publicador"])
    publicador.goto(base + reverse("interface:detalhe", args=[edital.id]))
    classificacao = publicador.locator("section[aria-labelledby='classificacao-titulo']")
    expect(classificacao.get_by_role("link", name="divulgar o resultado")).to_have_count(1)
    classificacao.get_by_role("link", name="divulgar o resultado").click()
    publicador.wait_for_load_state()
    tela.capturar(publicador, "quadro")

    # Cada recorte que falta leva à prévia dele; publica-se, e o quadro volta a dizer "Feito".
    quadro = base + reverse("interface:marco", args=[edital.id, marco])
    for _ in range(3):
        publicador.goto(quadro)
        celula = publicador.locator("td[data-operacao='publicar'][data-estado='falta'] a").first
        celula.click()
        publicador.wait_for_load_state()
        expect(publicador.get_by_role("button", name="Publicar este resultado")).to_be_visible()
        publicador.get_by_role("button", name="Publicar este resultado").click()
        publicador.wait_for_load_state()

    publicador.goto(quadro)
    expect(publicador.locator("td[data-operacao='publicar'][data-estado='falta']")).to_have_count(0)
    expect(publicador.locator("td[data-operacao='publicar'][data-estado='feito']")).to_have_count(3)
    tela.capturar(publicador, "quadro-feito")

    # Nenhuma cobrança sobre a lista excedente.
    publicador.goto(base + reverse("interface:supervisao", args=[edital.processo_id]))
    expect(publicador.locator("body")).not_to_contain_text("Ampla Concorrência (AC)")
    tela.capturar(publicador, "supervisao")

    assert PublicacaoResultado.objects.filter(edital=edital).count() == 3
    assert not PublicacaoResultado.objects.filter(edital=edital, lista_id=LISTA_AC).exists()
