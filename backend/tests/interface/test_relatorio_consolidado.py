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
        "Emitir e baixar PDF",
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


# --- Polish de 25/10/2026: a página fala como o PDF, e a emissão se diz emissão ---------------


def _pagina(client, *editais):
    identificar(client, "gustavo.gestor", ["gestor"])
    return client.get(
        reverse("interface:relatorio-consolidado-ver"),
        {"atalho": "ano", "ano": "2026", "escolha": "1", "edital": [str(e.pk) for e in editais]},
    )


def test_os_cartoes_da_pagina_sao_os_do_pdf(client, seletor_ligado, dois_editais):
    """Mesmo valor, mesmo "de N" com o complemento do consolidado, mesma base (FR-2574)."""
    from processo_seletivo.interface import relatorio_consolidado_pdf, relatorio_pdf

    resposta = _pagina(client, *(c.edital for c in dois_editais))
    lido = resposta.context["consolidado"]
    esperados = relatorio_pdf.cartoes(
        lido.indicadores, relatorio_consolidado_pdf.COMPLEMENTOS_DO_DE
    ).cartoes
    assert resposta.context["cartoes"] == esperados
    corpo = resposta.content.decode()
    assert corpo.count('<p class="rotulo">') == 6
    for cartao in esperados:
        if cartao.de:
            assert f'<span class="de">{cartao.de}</span>' in corpo
    assert any(c.de.endswith(" realizadas") for c in esperados), "o complemento chega à tela"


def test_a_emissao_se_diz_emissao_e_e_descrita_ao_botao(client, seletor_ligado, dois_editais):
    """Cada clique é emissão numerada e auditada na trilha da unidade: botão e frase dizem isso."""
    corpo = _pagina(client, *(c.edital for c in dois_editais)).content.decode()
    assert 'aria-describedby="sobre-a-emissao">Emitir e baixar PDF</button>' in corpo
    assert "A emissão fica registrada na trilha da unidade." in corpo
    assert "data-emissao" in corpo
    assert 'role="status" data-situacao-da-emissao' in corpo
    assert "interface/emissao-do-relatorio.js" in corpo, "o mesmo script da página do Edital"


def test_a_providencia_em_curso_tem_marca_em_texto_so_quando_ha(
    client, seletor_ligado, dois_editais
):
    """A marca é texto, e não só cor; sem Edital com pendência no conjunto, não há marca."""
    pendente, sem_pendencia = (c.edital for c in dois_editais)
    corpo = _pagina(client, pendente, sem_pendencia).content.decode()
    assert '<span class="marca-das-providencias">Em curso</span>' in corpo
    corpo = _pagina(client, sem_pendencia).content.decode()
    assert "marca-das-providencias" not in corpo
