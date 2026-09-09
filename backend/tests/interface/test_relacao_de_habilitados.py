"""A tela publica, e **não** oferece editar (021, FR-002, FR-030).

A prova que importa aqui é negativa: não há caminho de incluir, excluir ou renumerar participante,
não há campo de semente e não há botão de simular. A relação é projeção de fatos oficiais, e a
ausência desses controles é o que torna a afirmação verdadeira — e não uma validação que alguém
possa remover.
"""

import re

import pytest
from django.urls import reverse

from tests.fixtures.sorteio import certame_de_sorteio
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def certame(gestor, api_client, manager_headers, process_payload, seletor_ligado):
    return certame_de_sorteio(gestor, api_client, manager_headers, process_payload)


def _abrir(client, certame):
    identificar(client, "maria", [])
    return client.get(reverse("interface:sorteio", args=[certame["edital"].id, certame["marco"]]))


def test_a_tela_mostra_o_metodo_lido_do_edital_e_a_previa_da_relacao(client, certame):
    corpo = _abrir(client, certame).content.decode()

    assert "Método declarado no Edital" in corpo
    assert "IFES-SORTEIO-SHA256-v1" in corpo
    assert "Loteria Federal" in corpo
    assert "Publicar e congelar a relação" in corpo
    for inscricao in certame["inscricoes"]:
        assert inscricao.protocolo in corpo


def test_a_tela_nao_oferece_editar_o_metodo(client, certame):
    """Quem conduz o sorteio lê o método; alterá-lo é Retificação (D-013, FR-014)."""
    corpo = _abrir(client, certame).content.decode()

    assert 'name="draw-algorithm"' not in corpo
    assert 'name="algorithm"' not in corpo
    assert "Alterá-lo é uma Retificação" in corpo


def test_a_tela_nao_oferece_incluir_excluir_nem_renumerar(client, certame):
    corpo = _abrir(client, certame).content.decode()

    for proibido in ("Incluir participante", "Excluir participante", "Renumerar", "numero_publico"):
        assert proibido not in corpo


def test_a_tela_nao_tem_campo_de_semente_nem_botao_de_simular(client, certame):
    """Não é filtro nem validação: os controles não existem (FR-017, FR-030).

    A asserção é sobre **controles**, e não sobre a palavra: a página explica, em prosa, que o
    universo é comprometido antes de a semente existir — e uma varredura por substring acusaria
    essa frase. O que não pode existir é campo que aceite semente e botão que ensaie a ordem.
    """
    corpo = _abrir(client, certame).content.decode()

    for atributo in ('name="semente"', 'name="seed"', 'name="simular"', 'name="refazer"'):
        assert atributo not in corpo
    for rotulo in (">Simular", ">Pré-visualizar", ">Refazer", ">Sortear de novo"):
        assert rotulo not in corpo
    # **O único destino de POST desta tela é publicar relação.** É a asserção que sobrevive à
    # marcação: se amanhã alguém acrescentar uma rota de simulação ou de reexecução, ela aparece
    # como uma `action` a mais, e este teste a denuncia.
    acoes = {
        acao
        for acao in re.findall(r'<form method="post" action="([^"]+)"', corpo)
        if "sorteio" in acao
    }
    esperadas = {
        reverse(nome, args=[certame["edital"].id, certame["marco"]])
        for nome in (
            "interface:publicar-relacao-do-sorteio",
            "interface:observar-ocorrencia-do-sorteio",
        )
    }
    assert acoes == esperadas


def test_a_publicacao_congela_e_a_tela_passa_a_dizer_isso(client, certame):
    identificar(client, "maria", [])
    resposta = client.post(
        reverse(
            "interface:publicar-relacao-do-sorteio", args=[certame["edital"].id, certame["marco"]]
        ),
        {"lista_id": "", "chave_idempotencia": "tela-relacao-1"},
    )

    assert resposta.status_code == 302
    corpo = client.get(resposta["Location"]).content.decode()
    assert "Relação publicada e congelada" in corpo
    assert "Relação congelada em" in corpo
    assert "Motivo da sucessão" in corpo, "publicar outra passa a exigir motivo"
