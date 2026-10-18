"""O assistente na página pública da seleção, no desenvolvimento local (074).

Prende o que a entrega promete e o que ela não pode abrir:
- desligada a chave, nem painel nem rota (`FR-1680`, `FR-1683`);
- ligada, o candidato conversa sem identidade da gestão, pelos mesmos envios do protótipo
  (`FR-1681`);
- a conversa é da sessão e do Edital, separada da do protótipo (`FR-1682`);
- e a página que traz o painel não vai para cache compartilhado.
"""

import re

import pytest
from django.test import Client
from django.urls import reverse

from processo_seletivo.duvidas.domain.estruturas_do_piloto import RESPOSTA_DA_SUGESTAO
from processo_seletivo.duvidas.models import TrocaDoPiloto
from tests.fixtures.corpus import publicar_do_corpus
from tests.fixtures.inferencia import devolucao, saida
from tests.fixtures.inferencia_corpus import fonte
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ENVIOS = ("perguntar", "sugestao", "nova")


@pytest.fixture(autouse=True)
def _ambiente(sem_rede):
    """Nenhum caso alcança a rede."""


@pytest.fixture
def ligada(settings):
    settings.ASSISTENTE_NA_PAGINA_DO_EDITAL = True


@pytest.fixture
def edital_91(api_client):
    edital, _ = publicar_do_corpus(api_client, "91", chave="pagina91")
    return edital


def _pagina(edital):
    return reverse("portal:selecao", args=[edital.id])


def _envio(edital, nome):
    return reverse(f"portal:assistente-{nome}", args=[edital.id])


def _painel(resposta):
    corpo = re.sub(r"\s+", " ", resposta.content.decode())
    encontrado = re.search(r'<dialog id="pd-painel".*?</dialog>', corpo)
    return encontrado.group(0) if encontrado else ""


def _perguntas(painel):
    """As perguntas da conversa, sem os botões das sugestões."""
    return re.findall(
        r'<h3 class="pd-pergunta"[^>]*>(?:<span[^>]*>[^<]*</span>)?([^<]*)</h3>', painel
    )


def _todos(mensagens):
    total = fonte(mensagens, lugar="INF-BJN", rotulo="Vagas imediatas")
    return devolucao(saida("RESPONDIDA", ("dado", "Sim, os quatro obrigatórios.", [total["id"]])))


def test_desligada_a_pagina_nao_traz_o_painel_e_as_rotas_nao_existem(
    client, edital_91, porta_falsa
):
    porta = porta_falsa()

    resposta = client.get(_pagina(edital_91))

    assert resposta.status_code == 200
    assert "pd-painel" not in resposta.content.decode()
    for nome in ENVIOS:
        assert client.post(_envio(edital_91, nome), {"sugestao": "P-01"}).status_code == 404
    assert porta.chamadas == []
    assert not TrocaDoPiloto.objects.exists()


def test_ligada_o_candidato_abre_o_painel_sem_identidade_da_gestao(client, edital_91, ligada):
    resposta = client.get(_pagina(edital_91) + "?painel=1")

    painel = _painel(resposta)
    assert "Assistente do edital" in painel
    assert re.search(r'<dialog id="pd-painel"[^>]* open>', painel)
    assert "Ambiente local de desenvolvimento" in painel
    assert "Protótipo interno" not in painel
    # Os envios são os do portal, e nenhum aponta para a gestão.
    for nome in ENVIOS:
        assert f'action="{_envio(edital_91, nome)}"' in painel
    assert "/gestao/" not in painel
    # A conversa é da sessão: a página não vai para cache compartilhado.
    assert "private" in resposta["Cache-Control"]


def test_a_simulacao_e_so_do_prototipo(client, edital_91, ligada):
    """A página inteira, e não só o painel: a navegação dos estados vem antes do `<dialog>`."""
    corpo = client.get(_pagina(edital_91) + "?painel=1&simulacao=resposta").content.decode()

    assert "pd-painel" in corpo
    assert '<nav class="pd-estados"' not in corpo and "estados simulados" not in corpo
    assert "ilustrativas" not in corpo


def test_a_sugestao_e_respondida_pela_070_e_volta_para_a_pagina(
    client, edital_91, ligada, porta_falsa
):
    porta = porta_falsa()

    resposta = client.post(_envio(edital_91, "sugestao"), {"sugestao": "P-05", "perfil": "INF-BJN"})

    assert resposta.status_code == 302
    assert resposta.url == _pagina(edital_91) + "?painel=1#troca-1"
    assert porta.chamadas == []
    troca = TrocaDoPiloto.objects.get()
    assert troca.estado == RESPOSTA_DA_SUGESTAO
    painel = _painel(client.get(_pagina(edital_91) + "?painel=1"))
    assert "Na opção Polo Bom Jesus do Norte, são obrigatórios:" in painel


def test_a_pergunta_livre_segue_pela_perguntar_com_o_historico(
    client, edital_91, ligada, porta_falsa, contador_falso
):
    contador_falso()
    porta = porta_falsa(_todos)
    client.post(_envio(edital_91, "sugestao"), {"sugestao": "P-05", "perfil": "INF-BJN"})

    resposta = client.post(_envio(edital_91, "perguntar"), {"pergunta": "Preciso enviar todos?"})

    assert resposta.url == _pagina(edital_91) + "?painel=1#troca-2"
    mensagens = porta.chamadas[0]["mensagens"]
    assert mensagens[2]["content"].startswith("Que documentos preciso enviar?")
    assert mensagens[-1]["content"] == "Preciso enviar todos?"
    assert "Sim, os quatro obrigatórios." in _painel(client.get(_pagina(edital_91) + "?painel=1"))


def test_a_sugestao_da_opcao_pergunta_qual_na_propria_pagina(client, edital_91, ligada):
    resposta = client.post(_envio(edital_91, "sugestao"), {"sugestao": "P-05"})

    assert resposta.url == _pagina(edital_91) + "?painel=1&escolher=P-05"
    assert "Para qual opção?" in _painel(client.get(resposta.url))


def test_a_conversa_e_da_sessao_e_do_edital(client, edital_91, ligada, api_client):
    outro, _ = publicar_do_corpus(api_client, "92", chave="pagina92")
    client.post(_envio(edital_91, "sugestao"), {"sugestao": "P-05", "perfil": "INF-BJN"})

    assert _perguntas(_painel(client.get(_pagina(edital_91) + "?painel=1"))) == [
        "Que documentos preciso enviar? — Polo Bom Jesus do Norte"
    ]
    assert not _perguntas(_painel(client.get(_pagina(outro) + "?painel=1")))
    # Outra sessão não vê a conversa desta.
    assert not _perguntas(_painel(Client().get(_pagina(edital_91) + "?painel=1")))
    # Nova conversa começa do zero, e a anterior continua gravada.
    client.post(_envio(edital_91, "nova"))
    assert not _perguntas(_painel(client.get(_pagina(edital_91) + "?painel=1")))
    assert TrocaDoPiloto.objects.count() == 1


def test_a_conversa_do_prototipo_nao_aparece_na_pagina(client, edital_91, ligada, seletor_ligado):
    identificar(client, "pessoa", ["gestor", "participante-piloto-assistente"])
    client.post(
        reverse("interface:assistente-prototipo-sugestao", args=[edital_91.id]),
        {"sugestao": "P-05", "perfil": "INF-BJN"},
    )

    assert not _perguntas(_painel(client.get(_pagina(edital_91) + "?painel=1")))
    # E o protótipo, com a chave ligada, continua com um painel só.
    prototipo = client.get(reverse("interface:assistente-prototipo", args=[edital_91.id]))
    assert prototipo.content.decode().count('id="pd-painel"') == 1


def test_edital_sem_pagina_publica_nao_chega_ao_modelo(client, ligada, porta_falsa):
    porta = porta_falsa()
    inexistente = "00000000-0000-0000-0000-000000000000"

    resposta = client.post(
        reverse("portal:assistente-perguntar", args=[inexistente]), {"pergunta": "Oi?"}
    )

    assert resposta.status_code == 404
    assert porta.chamadas == []


def test_mostrar_a_pagina_nao_grava_conversa_na_sessao(client, edital_91, ligada):
    """A conversa nasce no primeiro envio: quem só lê a página não ganha conversa nem sessão."""
    client.get(_pagina(edital_91) + "?painel=1")

    assert "assistente_do_edital" not in client.session

    client.post(_envio(edital_91, "sugestao"), {"sugestao": "P-05", "perfil": "INF-BJN"})

    assert str(edital_91.id) in client.session["assistente_do_edital"]


def test_nova_conversa_tem_teto_por_sessao_e_edital(client, edital_91, ligada, settings):
    """O limite de turnos é por conversa; "Nova conversa" não o zera sem fim (`FR-1685`)."""
    settings.ASSISTENTE_CONVERSAS_POR_SESSAO = 2
    client.post(_envio(edital_91, "sugestao"), {"sugestao": "P-05", "perfil": "INF-BJN"})

    segunda = client.post(_envio(edital_91, "nova"))
    terceira = client.post(_envio(edital_91, "nova"))

    assert segunda.url == _pagina(edital_91) + "?painel=1"
    assert terceira.url == _pagina(edital_91) + "?painel=1&limite=1"
    painel = _painel(client.get(terceira.url))
    assert "chegou ao limite de conversas" in painel
    # A conversa em curso continua: o teto impede a próxima, e não apaga a atual.
    conversa = client.session["assistente_do_edital"][str(edital_91.id)]
    assert not TrocaDoPiloto.objects.filter(conversa=conversa).exists()
    assert TrocaDoPiloto.objects.count() == 1


def test_ligada_a_pagina_com_o_painel_fica_sob_a_recusa(client, edital_91, ligada):
    """092, `FR-2136`: com a chave da 074 ligada, a página pública traz o painel do protótipo, e o
    inventário da 092 não a captura — ela só existe no desenvolvimento local. A página inteira vai
    em recusa, como o resto do portal, e o painel não pode trazer estilo embutido: a folha dele vem
    por `<link>` (091), e a política recusaria qualquer outra."""
    from processo_seletivo.shared import politica_de_conteudo as politica
    from tests.interface.folha import folha_aplicada

    resposta = client.get(_pagina(edital_91) + "?painel=1")
    corpo = resposta.content.decode()

    assert "pd-painel" in corpo
    assert resposta["Content-Security-Policy"] == politica.POLITICA
    assert "Content-Security-Policy-Report-Only" not in resposta
    assert not re.search(r"<style\b|\sstyle\s*=", corpo)
    assert "interface/telas/prototipo-do-assistente.css" in corpo
    assert "--verde:" in folha_aplicada(corpo)
