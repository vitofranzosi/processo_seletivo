"""O histórico das divulgações do marco: o que valeu, o que vale, e para quem cada caminho aparece.

A pergunta que esta tela responde é "isto ainda vale?", e ela precisa respondê-la **sem depender de
cor** — quem lê por leitor de tela, quem imprime em preto e branco e quem não distingue verde de
cinza recebem a mesma informação porque ela está escrita (FR-052).
"""

import re

import pytest
from django.urls import reverse

from tests.fixtures.divulgacao import montar_ato_publicavel, publicar_o_ato
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def com_sucessao(gestor, api_client, manager_headers, process_payload):
    """P1 preliminar, sucedida por P2 definitiva — a cadeia que a US5 existe para mostrar."""
    cenario = montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=65,
        codigo="0765",
        pontuacoes=("90.0000", "70.0000"),
        primeiro=1301,
    )
    primeira = publicar_o_ato(cenario, chave="publicar-0765-p1", natureza="PRELIMINAR")
    segunda = publicar_o_ato(cenario, chave="publicar-0765-p2", natureza="DEFINITIVA")
    return cenario, primeira, segunda


def _historico(cenario):
    return reverse("interface:publicacoes-do-marco", args=[cenario["edital"].id, cenario["marco"]])


def _linhas(corpo):
    corpo_da_tabela = re.search(r"<tbody>(.*?)</tbody>", corpo, re.DOTALL).group(1)
    return re.findall(r"<tr>(.*?)</tr>", corpo_da_tabela, re.DOTALL)


def test_as_duas_publicacoes_aparecem_com_a_vigente_identificada(
    client, seletor_ligado, com_sucessao
):
    """FR-068: natureza, instante, autor, autoridade e situação — as cinco, por linha."""
    cenario, primeira, segunda = com_sucessao
    identificar(client, "paula.publicadora", ["publicador"])

    corpo = client.get(_historico(cenario)).content.decode()
    linhas = _linhas(corpo)

    assert len(linhas) == 2
    # A mais recente primeiro: a pergunta "o que vale hoje?" é respondida no alto.
    assert "Vigente" in linhas[0] and "Resultado definitivo" in linhas[0]
    assert "Sucedida" in linhas[1] and "Resultado preliminar" in linhas[1]
    assert "paula.publicadora" in linhas[0]
    assert "Diretora do Cefor" in linhas[0]
    assert primeira.publicado_em.astimezone().strftime("%d/%m/%Y") in corpo
    assert reverse("portal:resultado", args=[segunda.id]) in corpo


def test_a_situacao_e_legivel_sem_depender_de_cor(client, seletor_ligado, com_sucessao):
    """FR-052: as palavras estão lá, e não apenas uma classe que pinta a linha."""
    cenario, *_ = com_sucessao
    identificar(client, "paula.publicadora", ["publicador"])

    corpo = client.get(_historico(cenario)).content.decode()
    sem_marcacao = re.sub(r"<[^>]+>", " ", _linhas(corpo)[0])

    assert "Vigente" in sem_marcacao
    assert "Sucedida" in re.sub(r"<[^>]+>", " ", _linhas(corpo)[1])


def test_a_auditora_consulta_e_nao_recebe_a_acao_de_publicar(client, seletor_ligado, com_sucessao):
    """Consultar é de dois; agir é de um (FR-022, FR-069)."""
    cenario, *_ = com_sucessao
    identificar(client, "iris", ["auditor"])

    resposta = client.get(_historico(cenario))
    corpo = resposta.content.decode()

    assert resposta.status_code == 200
    assert "Resultado definitivo" in corpo
    assert "Publicar resultado" not in corpo
    assert "/publicar" not in corpo


def test_o_caminho_para_o_ato_de_origem_aparece_a_quem_tem_autorizacao(
    client, seletor_ligado, com_sucessao
):
    """FR-022: a tela da 015 tem porta própria, e o caminho segue a autorização de quem lê."""
    cenario, *_ = com_sucessao
    identificar(client, "iris", ["auditor"])

    corpo = client.get(_historico(cenario)).content.decode()

    assert "Ato de origem" in corpo
    assert (
        reverse(
            "interface:ato-de-ordenacao",
            args=[cenario["edital"].id, cenario["marco"], cenario["ato"].id],
        )
        in corpo
    )


def test_o_caminho_para_o_ato_de_origem_nao_aparece_a_quem_nao_tem(
    client, seletor_ligado, com_sucessao
):
    """Oferecê-lo a quem receberia 404 seria oferecer um beco — o defeito que a 007 tirou."""
    cenario, *_ = com_sucessao
    # Publicador puro: alcança o histórico, e **não** a tela do ato, cuja porta é a presidência da
    # comissão ou a auditoria.
    identificar(client, "paula.publicadora", ["publicador"])

    corpo = client.get(_historico(cenario)).content.decode()

    assert "Ato de origem" not in corpo
    assert (
        client.get(
            reverse(
                "interface:ato-de-ordenacao",
                args=[cenario["edital"].id, cenario["marco"], cenario["ato"].id],
            )
        ).status_code
        == 404
    ), "o teste só vale se a porta do ato de fato recusar quem não a tem"


def test_o_marco_sem_divulgacao_diz_isso_em_vez_de_mostrar_tabela_vazia(
    gestor, api_client, manager_headers, process_payload, client, seletor_ligado
):
    cenario = montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=66,
        codigo="0766",
        pontuacoes=("90.0000",),
        primeiro=1401,
    )
    identificar(client, "paula.publicadora", ["publicador"])

    corpo = client.get(_historico(cenario)).content.decode()

    assert "Nenhum resultado foi divulgado neste marco ainda" in corpo
    assert "<tbody>" not in corpo


def test_a_declaracao_de_encerramento_do_prazo_e_consultavel(client, seletor_ligado, com_sucessao):
    """SC-018: gravada com autor, instante e texto — e **consultável**, não só gravada.

    A caminhada da T125 encontrou o buraco: sem janela computável, publicar como definitivo exige a
    declaração expressa, o sistema a recusa quando falta e a grava quando vem — e nenhuma tela a
    mostrava depois. Uma afirmação de que o prazo se encerrou, guardada onde ninguém lê, não é ato
    auditável: é uma linha de banco.
    """
    cenario, _primeira, _segunda = com_sucessao
    identificar(client, "paula.publicadora", ["publicador"])

    corpo = client.get(_historico(cenario)).content.decode()
    linhas = _linhas(corpo)

    assert "O prazo recursal encerrou-se sem interposição, conforme o Edital." in linhas[0], (
        "a definitiva precisa mostrar o fundamento escrito de quem declarou o prazo encerrado"
    )
    assert "encerrou-se sem interposição" not in linhas[1], (
        "a preliminar não declara prazo nenhum, e não pode herdar a declaração da sucessora"
    )
