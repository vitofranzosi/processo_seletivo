"""A tela do impedimento: a confirmação declara o alcance antes do ato (FR-041)."""

import pytest
from django.urls import reverse

from processo_seletivo.avaliacoes.models import Atribuicao, Impedimento
from tests.fixtures.mesa import concluir_como, distribuir_para, inscricoes_de, montar_banca
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    return montar_banca(gestor, api_client, manager_headers, seed=14, codigo="E1")


@pytest.fixture
def tela(cenario):
    return reverse("interface:impedimentos", args=[cenario["edital"].id, cenario["etapa"]])


@pytest.fixture
def presidente(client, seletor_ligado):
    identificar(client, "carlos", ["gestor"])
    return client


@pytest.fixture
def com_conclusao(cenario, gestor):
    inscricao = inscricoes_de(cenario, 1, primeiro=1500)[0]
    distribuir_para(cenario, gestor, ["joao"], [inscricao], chave="tela")
    concluir_como(cenario, "joao", inscricao, pontuacao="95")
    return inscricao


def test_o_primeiro_envio_declara_o_alcance_em_vez_de_registrar(
    presidente, tela, cenario, com_conclusao
):
    """Retirar trabalho não pode ser efeito colateral silencioso de registrar um motivo."""
    corpo = presidente.post(
        tela,
        {
            "identity_subject": "joao",
            "inscricao_id": str(com_conclusao.id),
            "motivo": "Parentesco declarado.",
        },
    ).content.decode()

    assert "Confirme antes de registrar" in corpo
    assert "1</strong> atribuição" in corpo
    assert "avaliação já concluída" in corpo
    # Nada foi registrado ainda: o alcance é declarado **antes** do ato.
    assert not Impedimento.objects.exists()
    assert Atribuicao.objects.filter(inscricao=com_conclusao, ativo=True).exists()


def test_a_confirmacao_registra_e_diz_o_que_alcancou(presidente, tela, cenario, com_conclusao):
    envio = {
        "identity_subject": "joao",
        "inscricao_id": str(com_conclusao.id),
        "motivo": "Parentesco declarado.",
    }
    presidente.post(tela, envio)

    presidente.post(tela, {**envio, "confirmar": "1", "chave_idempotencia": "tela-1"})
    corpo = presidente.get(tela).content.decode()

    assert Impedimento.objects.count() == 1
    assert not Atribuicao.objects.filter(inscricao=com_conclusao, ativo=True).exists()
    assert "Impedimento registrado" in corpo
    assert "preservada e agora inelegível" in corpo


def test_o_alcance_preventivo_e_dito_como_tal(presidente, tela, cenario):
    """Impedir quem não tem atribuição ativa é ato legítimo, e a tela não finge o contrário."""
    inscricao = inscricoes_de(cenario, 1, primeiro=1510)[0]

    corpo = presidente.post(
        tela,
        {
            "identity_subject": "ana",
            "inscricao_id": str(inscricao.id),
            "motivo": "Impedimento preventivo.",
        },
    ).content.decode()

    assert "o impedimento é preventivo e nada" in corpo


def test_a_tela_mostra_o_ato_e_o_motivo_ao_lado_da_inelegivel(
    presidente, tela, cenario, com_conclusao
):
    """FR-093: invalidação **visível** é o que impede a seleção silenciosa."""
    envio = {
        "identity_subject": "joao",
        "inscricao_id": str(com_conclusao.id),
        "motivo": "Conflito de interesse superveniente.",
        "confirmar": "1",
        "chave_idempotencia": "tela-2",
    }
    presidente.post(tela, envio)

    corpo = presidente.get(tela).content.decode()

    assert "Conflito de interesse superveniente." in corpo
    assert "AVALIACAO_TORNAR_INELEGIVEL" in corpo
    assert "carlos" in corpo
    assert "95.0000" in corpo


def test_a_tela_nao_e_armazenavel_pelo_navegador(presidente, tela, cenario, com_conclusao):
    resposta = presidente.get(tela)

    assert "no-store" in resposta["Cache-Control"]
