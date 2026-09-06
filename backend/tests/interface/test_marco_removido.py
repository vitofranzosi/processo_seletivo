"""Removido o marco, a recusa não pode oferecer um caminho impossível (E2E17-002).

Três recusas impedem divulgar um ato, e só duas admitem o mesmo remédio. Quando o ato foi sucedido
ou envelheceu, o marco continua na norma: existe o que recomputar, e emitir o ato sucessor é o
caminho. Quando uma Retificação **removeu** o marco, não há regra vigente com que recomputar coisa
alguma — a 015 devolve `recomputavel=False` — e mandar emitir sucessor instrui o operador a fazer
o impossível.

O beco tinha duas paredes, e a auditoria bateu nas duas de uma vez:

1. a **mensagem** prometia um ato sucessor que não existe;
2. o **botão** levava à tela da classificação, que é da presidência e da auditoria — e quem só
   publica recebe 404 nela, em qualquer das três recusas.

Por isso a cobertura é dupla: o domínio decide se há sucessor, e a interface decide se oferece o
caminho a quem pode segui-lo.
"""

import pytest
from django.urls import reverse

from processo_seletivo.divulgacao.domain.publicabilidade import (
    CAMINHO_DO_SUCESSOR,
    DESATUALIZADO,
    MARCO_REMOVIDO,
    SUCEDIDO,
    aferir,
)
from tests.fixtures.divulgacao import emitir, montar_ato_publicavel
from tests.fixtures.publicacao import retify
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]


@pytest.fixture
def cenario(gestor, api_client, manager_headers, process_payload):
    return montar_ato_publicavel(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=61,
        codigo="0761",
        pontuacoes=("90.0000", "70.0000"),
        primeiro=761,
    )


@pytest.fixture
def sem_o_marco(cenario, api_client):
    """A Retificação que remove o marco da norma vigente, com o ato já emitido."""
    retify(
        api_client,
        cenario["edital"],
        [
            {
                "targetPath": (
                    f"/profiles/id={cenario['perfil']}"
                    f"/classificationMilestones/id={cenario['marco']}"
                ),
                "operation": "REMOVE",
            }
        ],
        suffix="remove-marco-017",
    )
    return cenario


@pytest.fixture
def com_a_regra_mudada(cenario, api_client):
    """Uma Retificação que envelhece o ato **sem** remover o marco: aqui há sucessor a emitir."""
    retify(
        api_client,
        cenario["edital"],
        [
            {
                "targetPath": (
                    f"/profiles/id={cenario['perfil']}"
                    f"/classificationMilestones/id={cenario['marco']}/operation"
                ),
                "operation": "REPLACE",
                "newValue": "MEDIA_PONDERADA",
            }
        ],
        suffix="regra-017",
    )
    return cenario


def _previa(cenario):
    return reverse(
        "interface:previa-de-publicacao",
        args=[cenario["edital"].id, cenario["marco"], cenario["ato"].id],
    )


def _ordenacao(cenario):
    return reverse("interface:ordenacao", args=[cenario["edital"].id, cenario["marco"]])


def _liga_para(corpo, endereco):
    """Se o documento oferece **aquele** endereço.

    Pelo `href` fechado, e não por substring: o endereço da classificação é prefixo do endereço do
    ato de ordenação, e procurar solto encontraria a trilha de navegação de qualquer tela e diria
    que o caminho está lá quando não está.
    """
    return f'href="{endereco}"' in corpo


def _publicacoes(cenario):
    return reverse("interface:publicacoes-do-marco", args=[cenario["edital"].id, cenario["marco"]])


# --- domínio -------------------------------------------------------------------------------


def test_a_recusa_por_marco_removido_nao_manda_emitir_sucessor(sem_o_marco):
    afericao = aferir(
        edital=sem_o_marco["edital"],
        marco_id=sem_o_marco["marco"],
        ato=sem_o_marco["ato"],
    )

    assert afericao.codigo == MARCO_REMOVIDO
    assert afericao.admite_sucessor is False
    assert CAMINHO_DO_SUCESSOR not in afericao.mensagem
    assert "sucessor" in afericao.mensagem, "a recusa **diz** que não há sucessor, e não o omite"


def test_a_recusa_por_ato_desatualizado_continua_mandando_emitir_sucessor(com_a_regra_mudada):
    """O marco permanece na norma: existe o que recomputar, e o caminho não pode sumir."""
    afericao = aferir(
        edital=com_a_regra_mudada["edital"],
        marco_id=com_a_regra_mudada["marco"],
        ato=com_a_regra_mudada["ato"],
    )

    assert afericao.codigo == DESATUALIZADO
    assert afericao.admite_sucessor is True
    assert CAMINHO_DO_SUCESSOR in afericao.mensagem


def test_a_recusa_por_ato_sucedido_continua_mandando_emitir_sucessor(cenario, gestor):
    """O marco permanece na norma: o ato é que deixou de ser o vigente."""
    sucessor = emitir(cenario, gestor, chave="emitir-sucessor-017")
    assert sucessor.id != cenario["ato"].id

    afericao = aferir(edital=cenario["edital"], marco_id=cenario["marco"], ato=cenario["ato"])

    assert afericao.codigo == SUCEDIDO
    assert afericao.admite_sucessor is True
    assert CAMINHO_DO_SUCESSOR in afericao.mensagem


# --- interface -----------------------------------------------------------------------------


def test_a_previa_do_marco_removido_nao_oferece_o_caminho_da_classificacao(
    client, seletor_ligado, sem_o_marco
):
    identificar(client, "paula.publicadora", ["publicador"])

    corpo = client.get(_previa(sem_o_marco)).content.decode()

    assert "Este ato não pode ser divulgado" in corpo
    assert "Ir para a classificação do marco" not in corpo
    assert not _liga_para(corpo, _ordenacao(sem_o_marco))
    assert "Não há ato sucessor a emitir" in corpo


def test_a_previa_nao_oferece_a_classificacao_a_quem_nao_a_alcanca(
    client, seletor_ligado, com_a_regra_mudada
):
    """Mesmo havendo sucessor a emitir: link para porta fechada responde 404, e 404 não explica."""
    identificar(client, "paula.publicadora", ["publicador"])

    corpo = client.get(_previa(com_a_regra_mudada)).content.decode()

    assert "Este ato não pode ser divulgado" in corpo
    assert not _liga_para(corpo, _ordenacao(com_a_regra_mudada))
    # A instrução permanece no texto: quem lê fica sabendo o que precisa acontecer, e quem pode
    # fazê-lo é quem recebe o caminho.
    assert CAMINHO_DO_SUCESSOR in corpo


def test_a_previa_oferece_a_classificacao_a_quem_a_alcanca(
    client, seletor_ligado, com_a_regra_mudada
):
    identificar(client, "paula.publicadora", ["publicador", "auditor"])

    corpo = client.get(_previa(com_a_regra_mudada)).content.decode()

    assert _liga_para(corpo, _ordenacao(com_a_regra_mudada))


def test_o_historico_das_publicacoes_nao_oferece_o_caminho_a_quem_recebe_404(
    client, seletor_ligado, cenario
):
    """A outra tela que oferecia o mesmo CTA — e o condicionava à capacidade errada."""
    identificar(client, "paula.publicadora", ["publicador"])

    corpo = client.get(_publicacoes(cenario)).content.decode()

    assert "Ir para a classificação do marco" not in corpo
    assert not _liga_para(corpo, _ordenacao(cenario))


def test_o_historico_oferece_o_caminho_a_quem_alcanca_a_classificacao(
    client, seletor_ligado, cenario
):
    identificar(client, "paula.publicadora", ["publicador", "auditor"])

    corpo = client.get(_publicacoes(cenario)).content.decode()

    assert _liga_para(corpo, _ordenacao(cenario))


def test_a_classificacao_do_marco_removido_abre_para_quem_a_alcanca(
    client, seletor_ligado, sem_o_marco
):
    """Removido o marco, a tela da 015 continua respondendo: o ato histórico não some com ele."""
    identificar(client, "paulo.presidente", ["gestor"])

    resposta = client.get(_ordenacao(sem_o_marco))

    assert resposta.status_code == 200, resposta.content
    corpo = resposta.content.decode()
    assert "não existe na norma vigente" in corpo


def test_o_endereco_que_nao_abre_responde_institucionalmente(client, seletor_ligado, sem_o_marco):
    """Acesso manual à tela fechada: página do produto, e nunca a de depuração do Django."""
    identificar(client, "paula.publicadora", ["publicador"])

    resposta = client.get(_ordenacao(sem_o_marco))

    assert resposta.status_code == 404
    corpo = resposta.content.decode()
    assert "Página não encontrada" in corpo
    assert "Cefor" in corpo
    assert "URLconf" not in corpo, "a lista de rotas não é resposta a ninguém"
    assert "Raised by" not in corpo
