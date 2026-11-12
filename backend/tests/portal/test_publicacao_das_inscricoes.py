"""O ato sobre as inscrições no portal: a página pública, o PDF, a seleção e a situação (148).

Quem consulta não tem conta, e lê só protocolo e nome de quem consta (D-010). O candidato lê a
própria situação em linguagem simples — "recebida", "aceita", "não aceita" —, e o vocabulário que
a 063 proíbe no topo continua proibido (UX-058, UX-156).
"""

import pytest
from django.urls import reverse

from tests.fixtures.divulgacao import entrar_como_titular
from tests.fixtures.inscricoes_publicadas import (
    analisar,
    evento_de_recurso,
    inscrever_no,
    montar,
    publicar,
)
from tests.portal.test_acompanhamento_pela_situacao import conferir_vocabulario, topo

pytestmark = [pytest.mark.django_db(transaction=True)]


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    cenario = montar(gestor, api_client, manager_headers, seed=1510, codigo="1510")
    cenario["inscricoes"] = inscrever_no(cenario, 2, primeiro=401)
    return cenario


def test_a_pagina_publica_mostra_quem_consta_e_nenhum_dado_pessoal(client, cenario):
    ato = publicar(cenario, "RECEBIDAS", chave="portal-1")

    resposta = client.get(reverse("portal:publicacao-das-inscricoes", args=[ato.id]))
    corpo = resposta.content.decode()

    assert resposta.status_code == 200
    assert "Relação de inscrições recebidas" in corpo
    assert "Esta é a versão que vale." in corpo
    assert "não que foi deferida ou homologada" in corpo
    for inscricao in cenario["inscricoes"]:
        assert inscricao.nome in corpo
        assert inscricao.protocolo in corpo
        assert inscricao.email not in corpo
        assert inscricao.cpf not in corpo
        assert inscricao.cpf_normalizado not in corpo
    assert 'style="' not in corpo


def test_o_pdf_sai_dos_bytes_gravados(client, cenario):
    ato = publicar(cenario, "RECEBIDAS", chave="portal-pdf")

    resposta = client.get(reverse("portal:publicacao-das-inscricoes-documento", args=[ato.id]))

    assert resposta.status_code == 200
    assert resposta["Content-Type"] == "application/pdf"
    assert resposta["ETag"] == f'"{ato.documento_hash}"'
    assert resposta.content == bytes(ato.documento)


def test_o_sucedido_diz_que_foi_sucedido_e_leva_ao_vigente(client, cenario, gestor):
    analisar(
        cenario,
        gestor,
        [(cenario["inscricoes"][0], "FAVORAVEL"), (cenario["inscricoes"][1], "DESFAVORAVEL")],
        sufixo="portal-cadeia",
    )
    recebidas = publicar(cenario, "RECEBIDAS", chave="portal-r")
    preliminar = publicar(
        cenario, "PRELIMINAR", prazo=evento_de_recurso(cenario["seed"]), chave="portal-p"
    )

    antiga = client.get(reverse("portal:publicacao-das-inscricoes", args=[recebidas.id]))
    vigente = client.get(reverse("portal:publicacao-das-inscricoes", args=[preliminar.id]))

    assert "Este ato foi sucedido." in antiga.content.decode()
    assert (
        reverse("portal:publicacao-das-inscricoes", args=[preliminar.id]) in antiga.content.decode()
    )
    corpo = vigente.content.decode()
    assert "Prazo de recurso aberto" in corpo
    # Desde a revisão de 12/11, a indeferida é contada em cada lista do Perfil (FR-5443).
    assert "Inscrições indeferidas nesta lista: 1." in corpo
    assert cenario["inscricoes"][1].nome not in corpo
    assert "Publicações anteriores sobre as inscrições (1)" in corpo


def test_a_selecao_oferece_o_ato_vigente(client, cenario):
    ato = publicar(cenario, "RECEBIDAS", chave="portal-selecao")

    corpo = client.get(reverse("portal:selecao", args=[cenario["edital"].id])).content.decode()

    assert 'id="inscricoes-publicadas-titulo">Inscrições</h2>' in corpo
    assert reverse("portal:publicacao-das-inscricoes", args=[ato.id]) in corpo


def _situacao(client, inscricao):
    entrar_como_titular(client, inscricao)
    resposta = client.get(reverse("portal:acompanhamento", args=[inscricao.id]))
    assert resposta.status_code == 200
    return conferir_vocabulario(resposta.content.decode())


def test_o_candidato_le_que_a_inscricao_foi_recebida_e_o_que_isso_nao_quer_dizer(client, cenario):
    publicar(cenario, "RECEBIDAS", chave="portal-sit-r")

    bloco = topo(_situacao(client, cenario["inscricoes"][0]))

    assert "Inscrição recebida" in bloco
    assert "e não que já foi aceita" in bloco
    assert "Ver a relação publicada" in bloco


def test_o_indeferido_le_que_nao_foi_aceito_ve_o_parecer_e_pode_recorrer(client, cenario, gestor):
    deferida, indeferida = cenario["inscricoes"]
    analisar(
        cenario,
        gestor,
        [(deferida, "FAVORAVEL"), (indeferida, "DESFAVORAVEL")],
        sufixo="portal-sit-p",
    )
    publicar(cenario, "PRELIMINAR", prazo=evento_de_recurso(cenario["seed"]), chave="portal-sit-p")

    pagina = _situacao(client, indeferida)
    bloco = topo(pagina)
    assert "Inscrição não aceita (resultado preliminar)" in bloco
    assert "Análise documental" in bloco
    assert "Faltou o diploma" in pagina
    assert "31/12/2099" in bloco

    client.logout()
    bloco_da_deferida = topo(_situacao(client, deferida))
    assert "Inscrição aceita (resultado preliminar)" in bloco_da_deferida
    assert "pode mudar" in bloco_da_deferida


def test_homologada_le_aceita_e_que_isso_nao_e_classificacao(client, cenario, gestor):
    deferida, indeferida = cenario["inscricoes"]
    analisar(cenario, gestor, [(deferida, "FAVORAVEL"), (indeferida, "FAVORAVEL")], sufixo="h")
    publicar(cenario, "HOMOLOGACAO", chave="portal-sit-h")

    bloco = topo(_situacao(client, deferida))

    assert "Inscrição aceita" in bloco
    assert "ainda não é a classificação" in bloco
