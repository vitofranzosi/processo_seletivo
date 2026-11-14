"""A composição declara a quem a Etapa se aplica (163, US1, UX-730, UX-731).

A divisão do trabalho é a das outras escolhas do cartão: **a folha esconde, o servidor descarta**.
Sem `:has`, a lista de Modalidades aparece sempre, e uma marca esquecida nela não pode restringir a
Etapa quando a opção é "Todas as inscrições".
"""

import re

import pytest

from processo_seletivo.editais.models.etapas import EtapaAvaliacao
from tests.interface.conftest import compor_rascunho, identificar
from tests.interface.test_compor import etapa, etapas_form, eventos, perfis

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def elaborando(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, perfis(), eventos())
    edital.refresh_from_db()
    return edital


def _gravada():
    return EtapaAvaliacao.objects.order_by("order").first()


def test_a_etapa_nasce_alcancando_todas_as_inscricoes(client, elaborando):
    """FR-6961, UX-730: a opção marcada é "Todas", e a lista oferece o código com os Perfis."""
    client.post(etapa(elaborando, "etapas"), etapas_form())
    corpo = client.get(etapa(elaborando, "etapas")).content.decode()

    assert "A quem a Etapa se aplica" in corpo
    assert re.search(r'name="etapa-0-alcance" value="TODAS"\s+checked', corpo)
    assert 'value="PCD"' in corpo
    assert "Pessoa com deficiência (PCD) — todos os Perfis" in corpo
    assert _gravada().alcance is None


def test_so_estas_modalidades_grava_os_codigos_marcados(client, elaborando):
    """FR-6960: a forma restrita grava a lista ordenada dos códigos."""
    resposta = client.post(
        etapa(elaborando, "etapas"),
        etapas_form(**{"etapa-0-alcance": "RESTRITA", "etapa-0-modalityCodes": ["PCD"]}),
    )

    assert resposta.status_code == 302, resposta.content
    assert _gravada().alcance == ["PCD"]
    corpo = client.get(etapa(elaborando, "etapas")).content.decode()
    assert re.search(r'name="etapa-0-alcance" value="RESTRITA"\s+checked', corpo)


def test_a_marca_esquecida_nao_restringe_a_etapa_para_todas(client, elaborando):
    """O servidor descarta: sem `:has`, a lista aparece, e a marca não vale sob "Todas"."""
    client.post(
        etapa(elaborando, "etapas"),
        etapas_form(**{"etapa-0-alcance": "TODAS", "etapa-0-modalityCodes": ["PCD"]}),
    )

    assert _gravada().alcance is None


def test_so_estas_sem_nenhuma_marcada_e_recusada_junto_do_campo(client, elaborando):
    """FR-6962: a lista vazia é contradição, e a recusa diz como corrigir."""
    resposta = client.post(
        etapa(elaborando, "etapas"),
        etapas_form(**{"etapa-0-alcance": "RESTRITA"}),
    )

    corpo = resposta.content.decode()
    assert resposta.status_code == 200
    assert "nenhuma foi escolhida" in corpo
    assert 'id="recusa-etapa-0-modalityCodes"' in corpo
    assert not EtapaAvaliacao.objects.exists()


def test_gravar_outra_etapa_do_assistente_preserva_o_alcance(client, elaborando):
    """`etapas_persistidas` reenvia o alcance: sem isso, gravar o Cronograma o apagaria."""
    client.post(
        etapa(elaborando, "etapas"),
        etapas_form(**{"etapa-0-alcance": "RESTRITA", "etapa-0-modalityCodes": ["PCD"]}),
    )
    compor_rascunho(client, elaborando, perfis(), eventos())

    assert _gravada().alcance == ["PCD"]


def test_a_folha_esconde_a_lista_so_quando_todas_esta_marcada():
    """UX-730: a regra é "esconde quando a outra opção está marcada", e nunca "por padrão"."""
    from pathlib import Path

    folha = (
        Path(__file__).resolve().parents[2]
        / "processo_seletivo/interface/static/interface/gestao/telas.css"
    ).read_text(encoding="utf-8")

    assert (
        'fieldset.etapa:has(input[name$="-alcance"][value="TODAS"]:checked) .so-restrita' in folha
    )
