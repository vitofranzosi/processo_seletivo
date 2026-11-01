"""A Retificação de Edital encerrado ou cancelado não anuncia próximo passo (113, FR-3544).

Desde o A-09 nenhum ato dela é aceito, e a seção "Retificações em curso" dizia quem agiria a
seguir — alguém que nada podia fazer.
"""

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models_retificacao import Retificacao
from tests.integration.processos.test_encerramento_seguro import cancelar
from tests.integration.publicacoes.test_retificacao_de_edital_encerrado import levar_a
from tests.interface.test_auditoria_passagem_da_retificacao import sessao
from tests.unit.processos.test_pendencias_do_edital import criar

# O seletor de identidade é o que abre `/gestao/` nos testes: sem ele a tela responde 503. Ligado
# aqui, e não no ambiente, porque o CI não tem o `.env` que o liga na máquina de desenvolvimento.
pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.usefixtures("seletor_ligado")]


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    from tests.fixtures.publicacao import publish_original

    return publish_original(api_client, manager_headers, process_payload)


def secao(corpo):
    inicio = corpo.index('<ul class="retificacoes-em-curso">')
    return corpo[inicio : corpo.index("</ul>", inicio)]


def test_encerrado_com_retificacao_em_elaboracao_e_em_revisao(api_client, edital):
    from tests.integration.processos.test_encerramento_seguro import encerrar

    criar(api_client, edital, titulo="Um")
    levar_a(criar(api_client, edital, titulo="Dois"), Retificacao.Status.EM_REVISAO)
    encerrar(edital)

    for papeis in (["gestor"], ["elaborador"], ["homologador"]):
        cliente = sessao("ana.elaboradora", papeis)
        corpo = cliente.get(reverse("interface:detalhe", args=[edital.id])).content.decode()
        trecho = secao(corpo)
        assert trecho.count("Não pode mais prosseguir:") == 2
        assert "o Edital foi encerrado" in trecho
        assert "Aguardando" not in trecho
        assert "O próximo ato é seu" not in trecho
        assert "Continuar a elaboração" not in trecho


def test_cancelado_com_retificacao_homologada(api_client, edital):
    levar_a(criar(api_client, edital), Retificacao.Status.HOMOLOGADA)
    cancelar(edital)
    edital.refresh_from_db()
    assert edital.status == Edital.Status.CANCELADO

    corpo = (
        sessao("carla.publicadora", ["publicador"])
        .get(reverse("interface:detalhe", args=[edital.id]))
        .content.decode()
    )
    trecho = secao(corpo)
    assert "Não pode mais prosseguir:" in trecho
    assert "o Edital foi cancelado" in trecho
    assert "O próximo ato é seu" not in trecho


def test_com_o_edital_publicado_o_proximo_passo_continua(api_client, edital):
    levar_a(criar(api_client, edital), Retificacao.Status.HOMOLOGADA)

    corpo = (
        sessao("carla.publicadora", ["publicador"])
        .get(reverse("interface:detalhe", args=[edital.id]))
        .content.decode()
    )
    assert "Não pode mais prosseguir" not in secao(corpo)


def test_a_marca_da_lista_tambem_diz_que_esta_parada(api_client, edital):
    from tests.integration.processos.test_encerramento_seguro import encerrar

    levar_a(criar(api_client, edital), Retificacao.Status.EM_REVISAO)
    encerrar(edital)

    corpo = sessao("bruno.homologador", ["homologador"]).get(reverse("interface:lista"))
    texto = corpo.content.decode()
    inicio = texto.index('class="marca-da-retificacao"')
    marca = texto[inicio : texto.index("</a>", inicio)]
    assert "não pode mais prosseguir" in marca
    assert "aguarda" not in marca
