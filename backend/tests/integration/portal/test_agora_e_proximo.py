"""O que acontece agora e o que vem depois, no cabeçalho da página pública (047, US3).

`FR-767`, `FR-768`, `SC-287`. A resposta sai da lista de marcos que o pulso da gestão lê, e não de
texto digitado. Nenhum dos Eventos deste arquivo se chama "análise": o caso que afirma que a
página nunca inventa essa fase precisa de um HTML em que a palavra só apareceria inventada.
"""

import re
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.processos.application.finalizacao import close_edital
from processo_seletivo.processos.models import Edital
from processo_seletivo.seguranca.domain import Actor
from tests.fixtures.publicacao import encerrar_inscricoes, retify
from tests.fixtures.selecao import identificador, publicar_selecao, rascunho_de_selecao

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

PERIODO = identificador(500, 0)
PROVA = identificador(501, 0)
ENTREVISTA = identificador(502, 0)
RESULTADO = identificador(503, 0)


def evento(identidade, descricao, inicio, *, fim=None, ordem=0, **extra):
    return {
        "id": identidade,
        "type": descricao,
        "description": descricao,
        "startAt": inicio.isoformat(),
        **({"endAt": fim.isoformat()} if fim else {}),
        "order": ordem,
        **extra,
    }


def periodo(agora):
    return evento(
        PERIODO,
        "Período de inscrições",
        agora - timedelta(days=5),
        fim=agora + timedelta(days=2),
        isRegistrationPeriod=True,
    )


def publicar(api_client, manager_headers, process_payload, eventos):
    rascunho = rascunho_de_selecao()
    rascunho["schedule"] = eventos
    return publicar_selecao(api_client, manager_headers, process_payload, rascunho=rascunho)


def bloco(client, edital):
    corpo = client.get(reverse("portal:selecao", args=[edital.id])).content.decode()
    achado = re.search(r'<div class="agora-e-proximo">.*?</div>', corpo, flags=re.S)
    return corpo, (achado.group(0) if achado else "")


def encerradas(api_client, edital, agora):
    """As inscrições encerradas por Retificação, que é como um Edital publicado chega lá (028)."""
    return encerrar_inscricoes(api_client, edital, agora - timedelta(hours=1))


def test_o_proximo_e_o_de_inicio_mais_proximo(client, api_client, manager_headers, process_payload):
    agora = timezone.now()
    edital = publicar(
        api_client,
        manager_headers,
        process_payload,
        [
            periodo(agora),
            evento(RESULTADO, "Resultado preliminar", agora + timedelta(days=30), ordem=3),
            evento(PROVA, "Prova escrita", agora + timedelta(days=10), ordem=1),
            evento(ENTREVISTA, "Entrevista", agora + timedelta(days=20), ordem=2),
        ],
    )
    edital = encerradas(api_client, edital, agora)

    corpo, trecho = bloco(client, edital)

    assert "Próximo:" in trecho
    assert "Prova escrita" in trecho
    assert "Entrevista" not in trecho and "Resultado preliminar" not in trecho
    assert "Período de inscrições" not in trecho, "o período já é dito pela frase do período"
    # `SC-287`: a resposta está no cabeçalho, antes da seção do cronograma.
    assert corpo.index('class="agora-e-proximo"') < corpo.index('class="marco')


def test_os_empatados_no_inicio_aparecem_todos_na_ordem_publicada(
    client, api_client, manager_headers, process_payload
):
    agora = timezone.now()
    mesmo_dia = agora + timedelta(days=10)
    edital = publicar(
        api_client,
        manager_headers,
        process_payload,
        [
            periodo(agora),
            evento(ENTREVISTA, "Entrevista", mesmo_dia, ordem=1),
            evento(PROVA, "Banca de títulos", mesmo_dia, ordem=2),
        ],
    )
    edital = encerradas(api_client, edital, agora)

    _, trecho = bloco(client, edital)

    assert trecho.index("Entrevista") < trecho.index("Banca de títulos")


def test_o_evento_em_curso_aparece_como_acontecendo_agora(
    client, api_client, manager_headers, process_payload
):
    agora = timezone.now()
    edital = publicar(
        api_client,
        manager_headers,
        process_payload,
        [
            periodo(agora),
            evento(
                PROVA,
                "Prova escrita",
                agora - timedelta(hours=2),
                fim=agora + timedelta(days=1),
                ordem=1,
            ),
        ],
    )
    edital = encerradas(api_client, edital, agora)

    _, trecho = bloco(client, edital)

    assert "Acontecendo agora:" in trecho
    assert "Prova escrita" in trecho


def test_sem_evento_pendente_o_bloco_some_e_nada_e_inventado(
    client, api_client, manager_headers, process_payload
):
    """`FR-768`: nunca *"em análise"*, nem outra fase que nenhum fato registrou."""
    agora = timezone.now()
    edital = publicar(
        api_client,
        manager_headers,
        process_payload,
        [periodo(agora), evento(PROVA, "Prova escrita", agora + timedelta(days=1), ordem=1)],
    )
    edital = encerradas(api_client, edital, agora)
    # O Evento restante vence por Retificação, e o Edital fica sem nada pendente.
    retify(
        api_client,
        edital,
        [
            {
                "targetPath": f"/schedule/id={PROVA}/startAt",
                "operation": "REPLACE",
                "newValue": (agora - timedelta(minutes=30)).isoformat(),
            }
        ],
        suffix="sem-pendente",
    )

    corpo, trecho = bloco(client, edital)

    assert trecho == ""
    assert "análise" not in corpo.lower()


def test_o_cancelado_nunca_e_proximo(client, api_client, manager_headers, process_payload):
    agora = timezone.now()
    edital = publicar(
        api_client,
        manager_headers,
        process_payload,
        [
            periodo(agora),
            evento(
                PROVA, "Prova suprimida", agora + timedelta(days=5), ordem=1, status="CANCELADO"
            ),
            evento(ENTREVISTA, "Entrevista", agora + timedelta(days=15), ordem=2),
        ],
    )
    edital = encerradas(api_client, edital, agora)

    _, trecho = bloco(client, edital)

    assert "Prova suprimida" not in trecho
    assert "Entrevista" in trecho


def test_edital_com_desfecho_nao_tem_bloco(client, api_client, manager_headers, process_payload):
    agora = timezone.now()
    edital = publicar(
        api_client,
        manager_headers,
        process_payload,
        [periodo(agora), evento(PROVA, "Prova escrita", agora + timedelta(days=10), ordem=1)],
    )
    edital = Edital.objects.get(pk=edital.id)
    close_edital(
        actor=Actor("gestora.agora", "cefor", frozenset({"edital:encerrar"})),
        edital_id=edital.id,
        expected_revision=edital.revision,
        reason="Encerramento do teste.",
        idempotency_key="encerrar-agora-e-proximo",
        correlation_id="047-agora",
    )

    _, trecho = bloco(client, edital)

    assert trecho == ""


def test_retificacao_com_vigencia_futura_nao_muda_o_proximo_de_agora(
    client, api_client, manager_headers, process_payload
):
    """Caso-limite: o próximo é o da versão vigente, e não o da Retificação que ainda não vale."""
    agora = timezone.now()
    edital = publicar(
        api_client,
        manager_headers,
        process_payload,
        [
            periodo(agora),
            evento(PROVA, "Prova escrita", agora + timedelta(days=10), ordem=1),
            evento(ENTREVISTA, "Entrevista", agora + timedelta(days=20), ordem=2),
        ],
    )
    edital = encerradas(api_client, edital, agora)
    retify(
        api_client,
        edital,
        [
            {
                "targetPath": f"/schedule/id={ENTREVISTA}/startAt",
                "operation": "REPLACE",
                "newValue": (agora + timedelta(days=5)).isoformat(),
            }
        ],
        effective_at=agora + timedelta(days=3),
        suffix="futura",
    )

    _, trecho = bloco(client, edital)

    assert "Prova escrita" in trecho
    assert "Entrevista" not in trecho
