"""T049 — a demonstração de fronteira: o que a página da atribuição **não** tem (§50 da spec)."""

import re

import pytest
from django.urls import reverse

from tests.fixtures.comissao import alocar_em
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

PROIBIDOS = [
    "Avaliar",
    "Concluir avaliação",
    "Nota",
    "Parecer",
    "Apto",
    "Inapto",
    "Pontuação",
    "Documento do candidato",
    "CPF",
]


@pytest.fixture
def pagina(client, seletor_ligado, gestor, processo_a, edital_a, comissao_de_a, etapa_a1):
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    identificar(client, "joao", [])
    return client.get(reverse("interface:minha-etapa", args=[edital_a.id, etapa_a1]))


def test_a_pagina_contextualiza_a_atribuicao(pagina):
    corpo = pagina.content.decode()

    assert "Alocado nesta Etapa" in corpo
    assert "Análise documental" in corpo


def test_a_pagina_nao_oferece_nenhum_controle_de_avaliacao(pagina):
    """FR-051 e FR-052: nem existente, nem desabilitado.

    Lido do **conteúdo**, e não da resposta inteira: o `<style>` da base administrativa comenta
    regras de outras telas, e a `010` acrescentou ali uma que menciona CPF — a marca de
    coincidência na listagem do que chegou. Afirmar sobre a página toda mediria o CSS, e um
    comentário de folha de estilo não é controle de avaliação.
    """
    corpo = re.sub(r"<style>.*?</style>", "", pagina.content.decode(), flags=re.S)

    for proibido in PROIBIDOS:
        assert proibido not in corpo, proibido
    assert "disabled" not in corpo


def test_quem_chega_pela_gestao_e_avisado_de_que_nao_esta_alocado(
    client, seletor_ligado, gestor, processo_a, edital_a, comissao_de_a, etapa_a1, etapa_a2
):
    """D-006: as duas portas existem, e a página diz por qual delas o ator entrou."""
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(
        reverse("interface:minha-etapa", args=[edital_a.id, etapa_a2])
    ).content.decode()

    assert "pela gestão da comissão" in corpo
    assert "Você está alocado nesta Etapa" not in corpo


def test_minhas_etapas_prioriza_etapa_edital_e_processo(
    client, seletor_ligado, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """UX-009."""
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    identificar(client, "joao", [])

    corpo = client.get(reverse("interface:minhas-etapas")).content.decode()

    assert "Análise documental" in corpo
    assert f"Edital {edital_a.number}/{edital_a.year}" in corpo
    assert processo_a.title in corpo


def test_o_periodo_aparece_em_data_brasileira(pagina):
    """O conteúdo publicado guarda ISO; a tela mostra dd/mm/aaaa, como as demais."""
    import re

    corpo = pagina.content.decode()
    assert re.search(r"\d{2}/\d{2}/\d{4}", corpo), corpo[:400]
