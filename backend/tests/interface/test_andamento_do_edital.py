"""O nível 1 no detalhe do Edital publicado, por família e por papel (127, US1 a US3).

**O que se prova é o que a pessoa lê**, pela tela: "O que fazer agora" começa pelas providências em
aberto, na ordem fixa (FR-4082) — as suas com link, as de outros papéis com o papel e sem link, as
que esperam com a razão —, e a Etapa que nada consome vira "Atenção" sem ser cobrada (D-010).

As famílias: S1 (sorteio sem Etapa consumida, como o 35), P1 (pontuação com avaliação, como o
91) e P2 (pontuação com Etapa governada e convocação, como o 51). S3 e P3 são compostos nos
testes puros.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.interface import andamento
from tests.conftest import ator_institucional
from tests.fixtures.andamento import certame_p1, certame_s1
from tests.fixtures.convocacao import montar_cenario_da_convocacao
from tests.fixtures.sorteio import certame_de_sorteio
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

NENHUM_ATO = "Nenhum ato disponível para seus papéis nesta situação."


def cartao(client, edital):
    resposta = client.get(reverse("interface:detalhe", args=[edital.id]))
    assert resposta.status_code == 200
    corpo = resposta.content.decode()
    inicio = corpo.index('id="acoes-titulo"')
    return corpo[inicio : corpo.index('id="participantes-titulo"')], corpo, resposta


def itens(bloco, classe):
    achado = re.search(rf'<ul class="providencias {classe}">(.*?)</ul>', bloco, re.S)
    return re.findall(r"<li>(.*?)</li>", achado.group(1), re.S) if achado else []


@pytest.fixture
def s1(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    return certame_s1(gestor, api_client, manager_headers, process_payload)


@pytest.fixture
def p1(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    return certame_p1(gestor, api_client, manager_headers, process_payload)


# --- S1 · quem conduz ------------------------------------------------------------------------


def test_s1_quem_conduz_le_a_sua_providencia_primeiro_com_link(client, s1):
    """SC-1231, FR-4080, FR-4084: a contagem, "Sua" em texto, e o verbo como link."""
    identificar(client, "carlos", ["gestor"])
    bloco, corpo, _ = cartao(client, s1["edital"])

    assert "1 providência em aberto · 1 é sua" in bloco
    [sua] = itens(bloco, "suas")
    assert '<span class="marca-sua">Sua</span>' in sua
    assert "Congelar a relação</a>" in sua
    assert "/sorteio" in sua
    assert NENHUM_ATO not in bloco, "FR-4086: não diz que não há ato ao lado da providência"


def test_s1_as_etapas_que_nada_consome_sao_atencao_e_nao_providencia(client, s1):
    """SC-1231, D-010: declaradas, e nenhuma é cobrada."""
    identificar(client, "carlos", ["gestor"])
    bloco, _, _ = cartao(client, s1["edital"])

    assert "<strong>Atenção:</strong> Análise documental e Prova didática estão declaradas" in bloco
    assert "Distribuir" not in bloco


def test_depois_da_publicacao_a_trilha_de_situacao_sai(client, s1):
    """D-002, FR-4089: o selo diz a situação, e o imutável cabe numa linha no pé do cartão."""
    identificar(client, "carlos", ["gestor"])
    bloco, corpo, _ = cartao(client, s1["edital"])

    assert 'aria-label="Situação do Edital no fluxo"' not in corpo
    assert '<p class="imutavel em-uma-linha"><strong>Conteúdo imutável.</strong>' in bloco
    assert bloco.index("contagem-de-providencias") < bloco.index("imutavel em-uma-linha")


def test_s1_com_providencia_da_pessoa_nenhuma_acao_vem_cheia(client, s1):
    """FR-4088: a ação principal passa a ser a providência."""
    identificar(client, "carlos", ["gestor"])
    bloco, _, _ = cartao(client, s1["edital"])

    acoes = bloco.split('class="lista-acoes', 1)[1]
    assert 'class="botao"' not in acoes.split("terminais", 1)[0]


def test_s1_a_presidencia_conduz_e_le_a_providencia_como_sua(client, s1):
    """FR-4055: a presidência da comissão é a mesma porta que a gestão."""
    identificar(client, "maria", ["avaliador"])
    bloco, _, _ = cartao(client, s1["edital"])
    assert "1 é sua" in bloco


# --- S1 · os outros papéis -------------------------------------------------------------------


@pytest.mark.parametrize("papel", ["publicador", "elaborador", "homologador", "julgador"])
def test_s1_quem_nao_conduz_le_o_papel_e_nao_recebe_link(client, s1, papel):
    """FR-4056, FR-4081, D-004: o nível 1 é de todos; o link, só de quem abre a tela."""
    identificar(client, "pessoa", [papel])
    bloco, _, _ = cartao(client, s1["edital"])

    assert "1 providência em aberto · nenhuma é sua" in bloco
    [de_outro] = itens(bloco, "de-outros")
    assert "<strong>Quem conduz a seleção:</strong> congelar a relação" in de_outro
    assert "<a " not in de_outro
    # Sem providência sua, a frase de sempre continua (FR-1070 da `057`, FR-4086).
    assert NENHUM_ATO in bloco or "lista-acoes" in bloco


def test_s1_o_auditor_le_as_telas_mas_nada_e_dele(client, s1):
    """FR-4055: quem só consulta não pratica a condução."""
    identificar(client, "auditora", ["auditor"])
    bloco, _, _ = cartao(client, s1["edital"])
    assert "nenhuma é sua" in bloco
    assert itens(bloco, "suas") == []


def test_o_perfil_sem_inscricao_nao_e_providencia(
    client, gestor, api_client, manager_headers, process_payload, seletor_ligado
):
    """FR-4102, caso-limite: sem inscrito, nada a fazer — e o porquê é dito."""
    vazio = certame_s1(gestor, api_client, manager_headers, process_payload, quantos=0)
    identificar(client, "carlos", ["gestor"])
    bloco, _, _ = cartao(client, vazio["edital"])

    assert "<strong>Nada em aberto:</strong> nenhum Perfil com marco recebeu inscrição." in bloco
    assert "providências em aberto" not in bloco


# --- inscrições em curso ----------------------------------------------------------------------


def test_com_as_inscricoes_abertas_congelar_aguarda_com_a_data(
    client, gestor, api_client, manager_headers, process_payload, seletor_ligado
):
    """Caso-limite: congelar e distribuir esperam o fim do período, e a razão diz até quando."""
    certame = certame_de_sorteio(
        gestor, api_client, manager_headers, process_payload, periodo_aberto=True
    )
    identificar(client, "carlos", ["gestor"])
    bloco, _, _ = cartao(client, certame["edital"])

    espera = itens(bloco, "em-espera")
    assert espera, "o que espera o fim das inscrições aparece, e não some"
    assert all("Aguarda" in item for item in espera)
    assert any("As inscrições ficam abertas até" in item for item in espera)
    assert itens(bloco, "suas") == []


# --- P1 · a presidência e o avaliador ---------------------------------------------------------


def test_p1_a_presidencia_le_distribuir_como_sua_e_a_ordem_nao_e_providencia(client, p1):
    """SC-1233, FR-4057: o objeto da presidência que a `104` não tinha (G-04)."""
    identificar(client, "maria", ["avaliador"])
    bloco, _, _ = cartao(client, p1["edital"])

    suas = itens(bloco, "suas")
    assert any("Distribuir 1 inscrição sem avaliador suficiente</a>" in item for item in suas)
    assert any("/distribuicao/" in item for item in suas)
    assert "Emitir a ordem" not in bloco, "a ordem espera as Etapas (G-02)"
    outros = itens(bloco, "de-outros")
    assert any("Os avaliadores alocados:</strong> avaliar 2" in item for item in outros)


def test_p1_a_entrevista_que_nada_consome_e_atencao(client, p1):
    identificar(client, "maria", ["avaliador"])
    bloco, _, _ = cartao(client, p1["edital"])
    assert "Entrevista está declarada no Edital, e nenhum ato do GPS depende do resultado" in bloco


def test_p1_o_avaliador_le_avaliar_como_sua_com_a_mesa(client, p1):
    """FR-4063: a carga de Minhas Etapas, a mesma da faixa da `104`."""
    identificar(client, "joao", ["avaliador"])
    bloco, _, _ = cartao(client, p1["edital"])

    suas = itens(bloco, "suas")
    assert any("Avaliar 2 inscrições</a>" in item for item in suas)
    mesa = reverse("interface:minha-etapa", args=[p1["edital"].id, p1["etapa"]])
    assert any(mesa in item for item in suas)


def test_p1_a_derivacao_da_ordem_e_depois_com_as_etapas_nomeadas(p1):
    """G-02: a condução diria *Falta*; o andamento diz *Depois*, e de quê."""
    resultado = andamento.do_edital(p1["edital"], ator_institucional("maria"))
    [perfil] = resultado.perfis
    ordem = next(p for p in perfil.pontos if p.tipo == andamento.ORDEM)
    celula = ordem.celula(None)
    assert celula.situacao == andamento.DEPOIS
    assert "Prova didática" in celula.razao


# --- P2 · a convocação ------------------------------------------------------------------------


def test_p2_depois_da_apuracao_convocar_os_titulares_e_de_quem_conduz(
    client, gestor, api_client, manager_headers, process_payload, seletor_ligado
):
    """FR-4073: a mesma prévia dos titulares que a tela da convocação lê."""
    edital, _, _ = montar_cenario_da_convocacao(
        gestor, api_client, manager_headers, process_payload
    )
    identificar(client, "carlos", ["gestor"])
    bloco, _, _ = cartao(client, edital)

    suas = itens(bloco, "suas")
    assert any("Convocar" in item and "/convocacao" in item for item in suas), suas


def test_antes_da_publicacao_nada_desta_feature_aparece(
    client, gestor, api_client, manager_headers, process_payload, seletor_ligado
):
    """Caso-limite: em elaboração o cartão é o de hoje, com a trilha e o bastão."""
    from processo_seletivo.processos.models import Edital

    resposta = api_client.post(
        "/api/v1/admin/processos", process_payload, format="json", **manager_headers
    )
    assert resposta.status_code == 201, resposta.content
    edital = Edital.objects.get(processo_id=resposta.json()["id"])
    assert andamento.do_edital(edital, gestor) is None
    identificar(client, "carlos", ["gestor"])
    _, corpo, _ = cartao(client, edital)
    assert 'aria-label="Situação do Edital no fluxo"' in corpo
    assert "contagem-de-providencias" not in corpo


def test_uma_falha_na_derivacao_nao_derruba_o_detalhe(client, s1, monkeypatch):
    """Item 2 do code review: sem andamento, o cartão volta a ser o de antes da 127."""

    def quebra(self, **_):
        raise KeyError("conteúdo inesperado")

    monkeypatch.setattr(andamento._Leitor, "andamento", quebra)
    identificar(client, "carlos", ["gestor"])
    _, corpo, resposta = cartao(client, s1["edital"])
    assert resposta.context["andamento"] is None
    assert "contagem-de-providencias" not in corpo
    assert 'aria-label="Situação do Edital no fluxo"' in corpo
