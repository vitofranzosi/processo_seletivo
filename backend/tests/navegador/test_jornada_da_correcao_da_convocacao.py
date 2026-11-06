"""A correção da convocação de ponta a ponta, num navegador de verdade (120, SC-1141, SC-1142).

Como as jornadas da `115`, em três partes:

1. **Preparação** — o estado do cenário G da `118`, pelas *fixtures*: um documento pendente com
   motivo, o Requerimento declarado na convocação em rascunho e nunca enviado, e o vencimento
   decorrido sem desfecho. No navegador o relógio não se adianta: a convocação nasce com vencimento
   de poucos segundos, e o caso espera ele passar, como o vencido da `115`;
2. **Ações** — só no navegador: a comissão corrige em desktop; o convocado, a 375 px, vê o prazo
   novo, complementa o documento e envia o Requerimento;
3. **Verificações** — na tela, no banco e na trilha.

**É a condição de conclusão da feature** (FR-3854): se a jornada não fecha por defeito do portal, o
defeito é registrado, e a `120` não se declara concluída. Nenhuma página pode ter violação da
política de conteúdo no console, e a do candidato não pode rolar na horizontal.
"""

import re
import time
import uuid
from datetime import timedelta

import pytest

expect = pytest.importorskip("playwright.sync_api", reason="sem o grupo opcional navegador").expect

from django.urls import reverse  # noqa: E402
from django.utils import timezone  # noqa: E402

from processo_seletivo.auditoria.models import RegistroAuditoria  # noqa: E402
from processo_seletivo.convocacao.application.convocar import CONVOCAR  # noqa: E402
from processo_seletivo.convocacao.models import (  # noqa: E402
    ApresentacaoDeDocumento,
    ConferenciaDeDocumento,
    Convocacao,
    ItemDaListaDaConvocacao,
)
from tests.fixtures import documentos_da_convocacao as cenarios  # noqa: E402
from tests.fixtures import jornada_do_convocado as jornada  # noqa: E402
from tests.fixtures.corte import MARCO  # noqa: E402
from tests.fixtures.documentos_da_convocacao import HISTORICO  # noqa: E402
from tests.navegador.test_jornada_dos_documentos_da_convocacao import (  # noqa: E402
    DESKTOP,
    Tela,
    abrir_convocacao,
    enviar,
    pagina_dos_documentos,
    sem_rolagem_horizontal,
)

pytestmark = pytest.mark.django_db(transaction=True)

MOTIVO = "A mensagem saiu com dois dias de atraso; o prazo é dado de novo."
ESPERA = 6


@pytest.fixture
def tela(navegador, live_server, settings, request, raiz_de_arquivos):
    settings.INTERFACE_SELETOR_IDENTIDADE = True
    atual = Tela(navegador, live_server, request.node.name)
    yield atual
    atual.fechar()
    assert atual.violacoes == [], "violação da política de conteúdo no console"


@pytest.fixture
def fx(gestor, api_client, manager_headers, process_payload):
    return jornada.Montagem(gestor, api_client, manager_headers, process_payload)


@pytest.fixture
def pdfs(tmp_path):
    def criar(nome):
        caminho = tmp_path / f"{nome}.pdf"
        caminho.write_bytes(b"%PDF-1.4\n" + nome.encode())
        return str(caminho)

    return criar


def _vencida_com_pendencia(fx):
    """O estado do cenário G, com o vencimento real decorrido em vez do relógio adiantado."""
    from processo_seletivo.requerimentos.application import preencher
    from tests.fixtures.requerimento import campos_de_exemplo

    certame = jornada.certame(
        fx, prefixo="nav-120", documentos=cenarios.documentos_do_aluno(), requerimento=True
    )
    edital = certame[0]
    pessoa, raiz = cenarios.convocar_primeira(
        certame, fx.gestor, chave="nav-120", vencimento=timezone.now() + timedelta(seconds=ESPERA)
    )
    cenarios.comunicar(edital, fx.gestor, raiz, chave="nav-120-comunicar")
    cenarios.apresentar(pessoa, raiz, HISTORICO, corpo=b"sem a pagina 2")
    cenarios.conferir(
        fx.gestor, raiz, HISTORICO, "PENDENTE", chave="nav-120-p1", motivo="Falta a página 2."
    )
    # O rascunho feito no prazo, que continua sendo o ponto de partida depois da correção.
    preencher.abrir_rascunho(inscricao=pessoa)
    preencher.gravar(inscricao=pessoa, dados=campos_de_exemplo(), expected_revision=None)
    restante = (raiz.vencimento - timezone.now()).total_seconds()
    time.sleep(max(restante, 0) + 1)
    return edital, pessoa, raiz


def _contagens():
    return (
        ItemDaListaDaConvocacao.objects.count(),
        ApresentacaoDeDocumento.objects.count(),
        ConferenciaDeDocumento.objects.count(),
    )


def test_corrigida_na_gestao_o_convocado_complementa_e_envia(tela, fx, pdfs):
    from processo_seletivo.portal.obrigacoes import data_e_hora
    from processo_seletivo.requerimentos.application import preencher
    from processo_seletivo.requerimentos.domain import nomes as nomes_do_requerimento

    edital, pessoa, raiz = _vencida_com_pendencia(fx)
    antes = _contagens()
    candidata = tela.candidato(pessoa)
    comissao = tela.gestao("carlos", ["gestor"], viewport=DESKTOP)

    # 1. O portal fechou o documento e o Requerimento juntos.
    abrir_convocacao(candidata, tela.servidor, pessoa)
    expect(candidata.get_by_text(re.compile("O prazo terminou em")).first).to_be_visible()
    expect(candidata.get_by_text("Escolher arquivo PDF")).to_have_count(0)
    sem_rolagem_horizontal(candidata)
    tela.capturar(candidata, "portal-antes")

    # 2. A comissão corrige pelo cartão, lendo a prévia antes do botão.
    comissao.goto(tela.servidor.url + reverse("interface:convocacao", args=[edital.id, MARCO]))
    expect(comissao.get_by_text("Vencimento decorrido").first).to_be_visible()
    comissao.locator("summary", has_text="Corrigir esta convocação").first.click()
    formulario = comissao.locator("form[data-correcao]").first
    expect(formulario.get_by_text("O que reabre")).to_be_visible()
    expect(
        formulario.get_by_text(re.compile("A mensagem da convocação sai de novo"))
    ).to_be_visible()
    novo = timezone.localtime(timezone.now() + timedelta(days=5)).replace(second=0, microsecond=0)
    formulario.locator("textarea[name=motivo]").fill(MOTIVO)
    formulario.locator("input[name=vencimento]").fill(novo.strftime("%Y-%m-%dT%H:%M"))
    expect(formulario.get_by_text(re.compile("O prazo é estendido até"))).to_be_visible()
    tela.capturar(comissao, "gestao-previa")
    formulario.get_by_role("button", name=re.compile("Corrigir a convocação de")).click()
    comissao.wait_for_load_state()
    expect(comissao.get_by_text(re.compile("corrigida. O vencimento passou de"))).to_be_visible()
    expect(comissao.get_by_text(re.compile("o prazo foi estendido"))).to_be_visible()
    expect(comissao.get_by_text("Prazo em curso").first).to_be_visible()
    tela.capturar(comissao, "gestao-resultado")

    sucessora = Convocacao.objects.get(convocacao_anterior=raiz)
    assert sucessora.chamada == raiz.chamada and sucessora.motivo_da_sucessao == MOTIVO

    # 3. O portal mostra o prazo novo, e o documento e o Requerimento reabrem juntos.
    abrir_convocacao(candidata, tela.servidor, pessoa)
    expect(candidata.get_by_text(re.compile(re.escape(data_e_hora(novo)))).first).to_be_visible()
    expect(candidata.get_by_text(re.compile("O prazo terminou em"))).to_have_count(0)
    sem_rolagem_horizontal(candidata)
    tela.capturar(candidata, "portal-prazo-novo")
    enviar(candidata, cenarios.item(raiz, HISTORICO).id, pdfs("historico-completo"))
    expect(candidata.locator("#confirmacao")).to_contain_text(
        "O arquivo aguarda a conferência da comissão."
    )

    candidata.goto(tela.servidor.url + reverse("portal:requerimento", args=[pessoa.id]))
    candidata.locator("#aceite").check()
    candidata.get_by_role("button", name="Enviar requerimento").click()
    candidata.wait_for_load_state()
    sem_rolagem_horizontal(candidata)
    tela.capturar(candidata, "portal-requerimento-enviado")
    assert preencher.vigente_de(pessoa).status == nomes_do_requerimento.ENVIADO

    # 4. A comissão vê a complementação e o histórico com a corrigida e o motivo.
    pagina_dos_documentos(comissao, tela.servidor, edital, sucessora)
    tela.capturar(comissao, "gestao-documentos")
    comissao.goto(
        tela.servidor.url + reverse("interface:convocacao-historico", args=[edital.id, MARCO])
    )
    expect(comissao.get_by_text(re.compile(f"sucedida — {re.escape(MOTIVO)}"))).to_be_visible()
    tela.capturar(comissao, "gestao-historico")

    # 5. Uma sucessora, um evento de trilha com o motivo e os dois vencimentos, nada perdido.
    itens, apresentacoes, conferencias = _contagens()
    assert itens == antes[0], "a sucessora usa a lista da chamada"
    assert apresentacoes == antes[1] + 1, "só a complementação nova"
    assert conferencias == antes[2], "nenhuma conferência se perdeu"
    assert Convocacao.objects.filter(inscricao_id=pessoa.id).count() == 2
    registro = RegistroAuditoria.objects.get(operation=CONVOCAR, aggregate_id=sucessora.id)
    assert f"Motivo da sucessão: {MOTIVO}" in registro.reason
    assert f"Sucede a convocação {raiz.id}" in registro.reason


def test_com_a_apuracao_superada_nenhum_cartao_oferece_formulario(tela, fx):
    from processo_seletivo.ocupacao.application.efeitos import registrar_efeito
    from processo_seletivo.ocupacao.domain import nomes as nomes_da_ocupacao
    from tests.fixtures.edital import PROFILE_ID

    certame = jornada.certame(fx, prefixo="nav-120-superada")
    edital = certame[0]
    cenarios.convocar_primeira(
        certame, fx.gestor, chave="nav-120-s", vencimento=timezone.now() + timedelta(days=3)
    )
    registrar_efeito(
        edital=edital,
        perfil_id=PROFILE_ID,
        marco_id=MARCO,
        lista_id=None,
        inscricao_id=uuid.uuid4(),
        especie=nomes_da_ocupacao.EFEITO_EXCLUSAO,
        fundamento="Desistência expressa da titular",
        ato_de_origem_id=uuid.uuid4(),
        rotulo_da_origem="desfecho de convocação",
        registrado_por="teste",
        registrado_em=timezone.now(),
    )
    comissao = tela.gestao("carlos", ["gestor"], viewport=DESKTOP)

    comissao.goto(tela.servidor.url + reverse("interface:convocacao", args=[edital.id, MARCO]))
    comissao.locator("summary", has_text="Corrigir esta convocação").first.click()

    expect(comissao.get_by_text("A correção está impedida.").first).to_be_visible()
    expect(comissao.locator("form[data-correcao]")).to_have_count(0)
    tela.capturar(comissao, "gestao-impedida")


@pytest.mark.parametrize("comunicada", [True, False], ids=["prazo-em-curso", "sem-comunicacao"])
def test_corrige_pela_tela_nos_outros_estados_em_aberto(tela, fx, comunicada):
    """SC-1141: a correção acontece num envio de formulário nos três estados em aberto — o vencido
    está no caso de ponta a ponta acima."""
    certame = jornada.certame(fx, prefixo=f"nav-120-{'c' if comunicada else 's'}")
    edital = certame[0]
    _, raiz = cenarios.convocar_primeira(
        certame, fx.gestor, chave="nav-120-e", vencimento=timezone.now() + timedelta(days=3)
    )
    if comunicada:
        cenarios.comunicar(edital, fx.gestor, raiz, chave="nav-120-e-comunicar")
    comissao = tela.gestao("carlos", ["gestor"], viewport=DESKTOP)
    situacao = "Prazo em curso" if comunicada else "Sem comunicação enviada"

    comissao.goto(tela.servidor.url + reverse("interface:convocacao", args=[edital.id, MARCO]))
    expect(comissao.locator("h3", has_text=situacao).first).to_be_visible()
    comissao.locator("summary", has_text="Corrigir esta convocação").first.click()
    formulario = comissao.locator("form[data-correcao]").first
    expect(formulario.get_by_text("O que reabre")).to_have_count(0)
    antecipado = timezone.localtime(timezone.now() + timedelta(days=1))
    formulario.locator("textarea[name=motivo]").fill("O vencimento foi informado errado.")
    formulario.locator("input[name=vencimento]").fill(antecipado.strftime("%Y-%m-%dT%H:%M"))
    expect(formulario.get_by_text(re.compile("O prazo é antecipado para"))).to_be_visible()
    tela.capturar(comissao, "gestao-previa-" + ("em-curso" if comunicada else "sem-comunicacao"))
    formulario.get_by_role("button", name=re.compile("Corrigir a convocação de")).click()
    comissao.wait_for_load_state()

    expect(comissao.get_by_text(re.compile("o prazo foi antecipado"))).to_be_visible()
    assert Convocacao.objects.filter(convocacao_anterior=raiz).count() == 1
