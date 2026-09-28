"""O candidato lê a data-limite recalculada depois da Retificação que concede (026, US3, SC-099).

É a metade da jornada que acontece do outro lado do balcão: o Edital publicou um prazo, a
Retificação o corrigiu, e quem abre "Recorrer" precisa ler a data **nova** — contada da divulgação
do resultado, e não da Retificação.

O que este arquivo guarda é a ligação entre os dois lados. A tela administrativa já tem teste
próprio; aqui se confere que a correção chega a quem ela governa.

**E só a que concede** (RC-121, decisão do usuário de 28/09). A janela de ato já divulgado segue a
versão que o ato citou, salvo o que a vigente concede: alongar alcança o resultado divulgado, e
encurtar não — o segundo teste prende o lado que a decisão acrescentou.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.divulgacao import entrar_como_titular
from tests.fixtures.publicacao import retify
from tests.integration.recursos.test_janela import JANELA_DE_CINCO, montar

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

INSTANTE = re.compile(r"(\d{2})/(\d{2})/(\d{4}) às \d{2}h\d{2}")


def corpo(resposta):
    return re.search(r"<main[^>]*>(.*)</main>", resposta.content.decode(), re.DOTALL).group(1)


def _retificar_a_duracao(api_client, edital, dias):
    vigente = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    perfil = next(p for p in vigente.content["profiles"] if p.get("classificationMilestones"))
    marco = perfil["classificationMilestones"][0]
    retify(
        api_client,
        edital,
        [
            {
                "operation": "REPLACE",
                "targetPath": (
                    f"/profiles/id={perfil['id']}"
                    f"/classificationMilestones/id={marco['id']}/appealWindow/durationDays"
                ),
                "newValue": dias,
            }
        ],
        suffix="prazo",
    )


def _limite_na_tela(client, inscricao):
    return INSTANTE.search(corpo(client.get(reverse("portal:recorrer", args=[inscricao.id]))))


def test_o_candidato_le_a_data_limite_recalculada_depois_da_retificacao(
    client, gestor, api_client, manager_headers, process_payload
):
    """De cinco para dez dias: a data que a tela mostra anda cinco dias para frente.

    A contagem continua saindo da **divulgação do resultado**, e não da Retificação — é o prazo do
    ato que abre o direito, e não do ato que corrigiu a norma.
    """
    cenario = montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=26,
        codigo="0261",
        janela=dict(JANELA_DE_CINCO),
    )
    edital = cenario["edital"]
    inscricao = cenario["inscricoes"][0]

    entrar_como_titular(client, inscricao)
    antes = corpo(client.get(reverse("portal:recorrer", args=[inscricao.id])))
    limite_antes = INSTANTE.search(antes)
    assert limite_antes, "a tela do candidato precisa dizer até quando cabe recorrer"

    _retificar_a_duracao(api_client, edital, 10)

    depois = corpo(client.get(reverse("portal:recorrer", args=[inscricao.id])))
    limite_depois = INSTANTE.search(depois)
    assert limite_depois, "depois da Retificação a tela continua dizendo até quando"
    assert limite_depois.group(0) != limite_antes.group(0), (
        "o prazo foi corrigido de cinco para dez dias e a data-limite não mudou — o candidato "
        "continua lendo a janela antiga"
    )


def test_a_retificacao_que_encurta_nao_alcanca_o_resultado_ja_divulgado(
    client, gestor, api_client, manager_headers, process_payload
):
    """De cinco para dois dias: a data de quem já teve o resultado divulgado não se move (RC-121).

    Antes da decisão de 28/09, a interposição lia a janela na versão vigente, e a Retificação que
    encurtava a janela encurtava também o prazo de um resultado já divulgado — tirava dias de um
    direito que já estava correndo.
    """
    cenario = montar(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        seed=27,
        codigo="0271",
        janela=dict(JANELA_DE_CINCO),
    )
    inscricao = cenario["inscricoes"][0]
    entrar_como_titular(client, inscricao)
    limite_antes = _limite_na_tela(client, inscricao)
    assert limite_antes, "a tela do candidato precisa dizer até quando cabe recorrer"

    _retificar_a_duracao(api_client, cenario["edital"], 2)

    limite_depois = _limite_na_tela(client, inscricao)
    assert limite_depois, "depois da Retificação a tela continua dizendo até quando"
    assert limite_depois.group(0) == limite_antes.group(0), (
        "a Retificação encurtou o prazo de um resultado já divulgado"
    )
