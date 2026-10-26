"""A tela do relatório do Edital: a ação, a página e as portas (099, FR-2513 a FR-2515)."""

import pytest
from django.urls import reverse

from tests.fixtures.relatorio import montar_cenario
from tests.interface.conftest import identificar

pytestmark = pytest.mark.django_db


@pytest.fixture
def cenario(db):
    return montar_cenario(final="pendente")


def test_a_gestao_ve_a_acao_e_a_pagina_com_a_camada_executiva(client, seletor_ligado, cenario):
    identificar(client, "gustavo.gestor", ["gestor"])
    url = reverse("interface:relatorio-do-edital", args=[cenario.edital.id])

    detalhe = client.get(reverse("interface:detalhe", args=[cenario.edital.id]))
    assert url in detalhe.content.decode()

    pagina = client.get(url)
    corpo = pagina.content.decode()
    assert pagina.status_code == 200
    assert "no-store" in pagina["Cache-Control"]
    for trecho in (
        "Relatório do Edital 61/2026",
        "Encerrado em 20/10/2026",
        "Situação das providências",
        "Visão geral",
        "Inscrições por vaga",
        "Resultados por perfil de vaga",
        "Professor de Informática",
        "Emitir e baixar PDF",
    ):
        assert trecho in corpo, trecho
    assert reverse("interface:relatorio-do-edital-pdf", args=[cenario.edital.id]) in corpo


def test_a_presidencia_do_processo_tambem_alcanca(client, seletor_ligado, cenario):
    identificar(client, "paulo.presidente", ["elaborador"])
    resposta = client.get(reverse("interface:relatorio-do-edital", args=[cenario.edital.id]))
    assert resposta.status_code == 200


def test_quem_e_da_unidade_sem_a_base_recebe_a_recusa_explicada(client, seletor_ligado, cenario):
    """FR-2514 e a gramática da `033`: 403 que diz o que falta, e não 404."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.get(reverse("interface:relatorio-do-edital", args=[cenario.edital.id]))
    assert resposta.status_code == 403
    assert "Peça" in resposta.content.decode()
    detalhe = client.get(reverse("interface:detalhe", args=[cenario.edital.id]))
    assert "Relatório do Edital" not in detalhe.content.decode()


def test_outra_unidade_recebe_nao_encontrado(client, seletor_ligado, cenario):
    identificar(client, "gustavo.gestor", ["gestor"], escopo="outra-unidade")
    resposta = client.get(reverse("interface:relatorio-do-edital", args=[cenario.edital.id]))
    assert resposta.status_code == 404


def test_edital_nao_publicado_tem_a_acao_indisponivel_e_recusa(client, seletor_ligado, edital):
    """Caso-limite: antes da publicação a ação aparece desabilitada, com o motivo."""
    identificar(client, "gustavo.gestor", ["gestor"])
    detalhe = client.get(reverse("interface:detalhe", args=[edital.id])).content.decode()
    assert "O relatório fica disponível quando o Edital for publicado." in detalhe
    resposta = client.get(reverse("interface:relatorio-do-edital", args=[edital.id]))
    assert resposta.status_code == 409


def test_a_emissao_so_aceita_envio(client, seletor_ligado, cenario):
    identificar(client, "gustavo.gestor", ["gestor"])
    resposta = client.get(reverse("interface:relatorio-do-edital-pdf", args=[cenario.edital.id]))
    assert resposta.status_code == 405


def test_a_lista_de_processos_nao_oferece_o_relatorio(client, seletor_ligado, cenario):
    """A ação é do detalhe: na lista, ela custaria uma consulta à comissão por linha."""
    identificar(client, "paulo.presidente", ["elaborador"])
    lista = client.get(reverse("interface:lista")).content.decode()
    assert reverse("interface:relatorio-do-edital", args=[cenario.edital.id]) not in lista


def test_so_a_falha_de_serializacao_vira_tente_de_novo(
    client, seletor_ligado, cenario, monkeypatch
):
    """Erro de banco que não é concorrência sobe como defeito, e não como "baixe de novo"."""
    from django.db import IntegrityError, OperationalError

    from processo_seletivo.interface import relatorio_pdf

    identificar(client, "gustavo.gestor", ["gestor"])
    url = reverse("interface:relatorio-do-edital-pdf", args=[cenario.edital.id])

    class Serializacao(Exception):
        sqlstate = "40001"

    def concorrente(*args, **kwargs):
        raise OperationalError("could not serialize access") from Serializacao()

    monkeypatch.setattr(relatorio_pdf, "compor", concorrente)
    assert client.post(url).status_code == 409

    def defeito(*args, **kwargs):
        raise IntegrityError("defeito")

    monkeypatch.setattr(relatorio_pdf, "compor", defeito)
    client.raise_request_exception = True
    with pytest.raises(IntegrityError):
        client.post(url)


# --- Polish de 25/10/2026: a página fala como o PDF, e a emissão se diz emissão ---------------


def _pagina(client, cenario):
    identificar(client, "gustavo.gestor", ["gestor"])
    return client.get(reverse("interface:relatorio-do-edital", args=[cenario.edital.id]))


def test_os_cartoes_da_pagina_sao_os_do_pdf(client, seletor_ligado, cenario):
    """Mesmo valor, mesmo "de N", mesma base: a tela usa a função de cartões do documento."""
    from processo_seletivo.interface import relatorio_pdf

    resposta = _pagina(client, cenario)
    lido = resposta.context["relatorio"]
    esperados = relatorio_pdf.cartoes(lido.indicadores, relatorio_pdf.COMPLEMENTOS_DO_DE).cartoes
    assert resposta.context["cartoes"] == esperados
    corpo = resposta.content.decode()
    assert corpo.count('<p class="rotulo">') == 6
    assert '<span class="de">de 2 realizadas</span>' in corpo


def test_a_emissao_se_diz_emissao_e_e_descrita_ao_botao(client, seletor_ligado, cenario):
    """O clique gera emissão numerada e auditada: o botão e a frase dizem isso."""
    corpo = _pagina(client, cenario).content.decode()
    assert 'aria-describedby="sobre-a-emissao">Emitir e baixar PDF</button>' in corpo
    assert "A emissão fica registrada na trilha do Edital." in corpo
    assert 'role="status" data-situacao-da-emissao' in corpo
    assert "interface/emissao-do-relatorio.js" in corpo


def test_a_providencia_em_curso_tem_marca_em_texto_so_quando_ha(
    client, seletor_ligado, cenario, db
):
    """A marca é texto, e não só cor; sem pendência, não há marca."""
    corpo = _pagina(client, cenario).content.decode()
    assert '<span class="marca-das-providencias">Em curso</span>' in corpo
    encerrado = montar_cenario(final="sem-pendencia", numero="62")
    corpo = client.get(
        reverse("interface:relatorio-do-edital", args=[encerrado.edital.id])
    ).content.decode()
    assert "marca-das-providencias" not in corpo
    assert "nenhuma providência pendente registrada no GPS" in corpo


def test_as_datas_usam_os_rotulos_e_a_legenda_do_pdf(client, seletor_ligado, cenario):
    from processo_seletivo.interface import relatorio_pdf

    resposta = _pagina(client, cenario)
    corpo = resposta.content.decode()
    naturezas = {d.natureza for d in resposta.context["relatorio"].datas}
    for natureza in naturezas:
        assert f'<td class="natureza-da-data">{relatorio_pdf.NATUREZAS[natureza]}</td>' in corpo
    for natureza, explicacao in relatorio_pdf.EXPLICACOES_DAS_NATUREZAS:
        assert (explicacao in corpo) == (natureza in naturezas)
