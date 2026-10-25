"""A tela do relatório consolidado: porta, escolha, página e emissão (100, FR-2554 a FR-2559)."""

import pytest
from django.urls import reverse

from tests.fixtures.relatorio import dia, montar_cenario
from tests.interface.conftest import identificar

pytestmark = pytest.mark.django_db


@pytest.fixture
def dois_editais(db):
    return (
        montar_cenario(final="pendente"),
        montar_cenario(final="sem-pendencia", numero="62", publicado_em=dia(10, 2, 9)),
    )


def test_a_visao_geral_oferece_o_relatorio_a_quem_tem_a_porta(client, seletor_ligado, db):
    identificar(client, "gustavo.gestor", ["gestor"])
    pagina = client.get(reverse("interface:visao-geral")).content.decode()
    assert reverse("interface:relatorio-consolidado") in pagina


def test_sem_a_capacidade_a_recusa_diz_o_que_falta(client, seletor_ligado, dois_editais):
    """FR-2554 e a gramática da `033`: 403 explicado, e não 404."""
    identificar(client, "paulo.presidente", ["elaborador"])
    for nome in ("interface:relatorio-consolidado", "interface:relatorio-consolidado-ver"):
        resposta = client.get(reverse(nome), {"criterio": "numero", "ano": "2026"})
        assert resposta.status_code == 403, nome
        assert "consultar a visão institucional" in resposta.content.decode()
    resposta = client.post(reverse("interface:relatorio-consolidado-pdf"), {"ano": "2026"})
    assert resposta.status_code == 403


def test_a_escolha_lista_os_editais_marcados(client, seletor_ligado, dois_editais):
    identificar(client, "gustavo.gestor", ["gestor"])
    resposta = client.get(
        reverse("interface:relatorio-consolidado"), {"atalho": "ano", "ano": "2026"}
    )
    corpo = resposta.content.decode()
    assert resposta.status_code == 200
    assert "no-store" in resposta["Cache-Control"]
    assert "Editais com primeira publicação entre 01/01/2026 e 31/12/2026" in corpo
    for cenario in dois_editais:
        assert f'value="{cenario.edital.pk}" checked' in corpo
    assert "Os números de cada um serão os do momento da emissão" in corpo


def test_aplicar_outro_criterio_nao_herda_os_marcados(client, seletor_ligado, dois_editais):
    identificar(client, "gustavo.gestor", ["gestor"])
    e61, e62 = (c.edital for c in dois_editais)
    resposta = client.get(
        reverse("interface:relatorio-consolidado"),
        {"acao": "aplicar", "atalho": "s2", "ano": "2026", "escolha": "1", "edital": [str(e62.pk)]},
    )
    corpo = resposta.content.decode()
    assert f'value="{e61.pk}" checked' in corpo
    assert str(e62.pk) not in corpo


def test_a_pagina_traz_a_camada_executiva_e_a_emissao(client, seletor_ligado, dois_editais):
    identificar(client, "gustavo.gestor", ["gestor"])
    e61, e62 = (c.edital for c in dois_editais)
    resposta = client.get(
        reverse("interface:relatorio-consolidado-ver"),
        {"atalho": "ano", "ano": "2026", "escolha": "1", "edital": [str(e61.pk), str(e62.pk)]},
    )
    corpo = resposta.content.decode()
    assert resposta.status_code == 200
    assert "no-store" in resposta["Cache-Control"]
    for trecho in (
        "Relatório Consolidado de Gestão dos Processos Seletivos",
        "Conjunto analisado",
        "O período escolheu os Editais",
        "Inscrições por vaga",
        "Convocações aceitas",
        "Pontos de atenção",
        "O GPS não registra matrículas.",
        "Baixar PDF",
        "Por Edital",
    ):
        assert trecho in corpo, trecho
    assert f'name="edital" value="{e61.pk}"' in corpo, "o POST leva o mesmo conjunto"
    assert reverse("interface:relatorio-consolidado-pdf") in corpo


def test_conjunto_vazio_recusa_a_pagina(client, seletor_ligado, dois_editais):
    identificar(client, "gustavo.gestor", ["gestor"])
    resposta = client.get(
        reverse("interface:relatorio-consolidado-ver"), {"atalho": "ano", "ano": "2024"}
    )
    assert resposta.status_code == 422
    assert "Nenhum Edital publicado entra neste conjunto" in resposta.content.decode()


def test_outra_unidade_nao_ve_os_editais_do_cefor(client, seletor_ligado, dois_editais):
    identificar(client, "gustavo.gestor", ["gestor"], escopo="outra-unidade")
    e61 = dois_editais[0].edital
    corpo = client.get(
        reverse("interface:relatorio-consolidado"), {"criterio": "manual", "edital": str(e61.pk)}
    ).content.decode()
    assert str(e61.pk) not in corpo


def test_a_emissao_so_aceita_envio(client, seletor_ligado, db):
    identificar(client, "gustavo.gestor", ["gestor"])
    assert client.get(reverse("interface:relatorio-consolidado-pdf")).status_code == 405
