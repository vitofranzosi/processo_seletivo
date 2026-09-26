"""As advertências que se repetem por Evento chegam dobradas (estudo de esforço, §12, itens 6 e 13).

O estudo mediu onze avisos idênticos de data passada, e treze de ano divergente logo após o reuso,
empurrando os impedimentos para fora da tela da Revisão. Nenhum some: o achado continua sendo um
por Evento (FR-343a), e cada um mantém a frase e o caminho dentro do grupo.
"""

import re
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.editais.models import EventoCronograma
from processo_seletivo.interface.templatetags.interface_extras import agrupar_repetidas
from tests.interface.conftest import compor_rascunho, identificar
from tests.interface.test_compor import eventos, perfis
from tests.interface.test_selo_do_cronograma import datar


def pendencia(codigo, severidade="aviso", mensagem=""):
    return {"codigo": codigo, "severidade": severidade, "mensagem": mensagem or codigo}


def test_as_repetidas_viram_um_grupo_no_lugar_da_primeira():
    itens = [
        pendencia("edital_description_missing"),
        pendencia("schedule_event_in_past", mensagem="A"),
        pendencia("stage_labels", "erro"),
        pendencia("schedule_event_in_past", mensagem="B"),
        pendencia("schedule_event_in_past", mensagem="C"),
    ]

    entradas = agrupar_repetidas(itens)

    assert [entrada.get("item", {}).get("codigo") for entrada in entradas] == [
        "edital_description_missing",
        None,
        "stage_labels",
    ]
    grupo = entradas[1]
    assert grupo["resumo"] == "3 Eventos com data que já passou"
    assert [item["mensagem"] for item in grupo["itens"]] == ["A", "B", "C"]


def test_as_duas_familias_se_dobram_separadas():
    itens = [pendencia("schedule_event_in_past")] * 2 + [
        pendencia("schedule_event_year_mismatch")
    ] * 13

    resumos = [entrada["resumo"] for entrada in agrupar_repetidas(itens)]

    assert resumos == [
        "2 Eventos com data que já passou",
        "13 Eventos que começam em ano diferente do ano do Edital",
    ]


def test_uma_so_nao_se_dobra():
    """Resumo de um item é a mesma frase, mais longa."""
    itens = [pendencia("schedule_event_in_past")]

    assert agrupar_repetidas(itens) == [{"item": itens[0]}]


def test_impedimento_nunca_se_dobra():
    """Um impedimento sob um resumo seria um impedimento que a pessoa pode não abrir."""
    itens = [pendencia("schedule_event_in_past", "erro")] * 3

    assert all("item" in entrada for entrada in agrupar_repetidas(itens))


@pytest.mark.django_db
def test_a_revisao_dobra_os_eventos_vencidos_e_mantem_cada_um(client, seletor_ligado, edital):
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(
        client,
        edital,
        perfis(),
        eventos(
            **{
                "evento-1-id": "aaaaaaaa-0000-4000-8000-00000000e0a2",
                "evento-1-type": "Resultado",
                "evento-1-description": "Resultado final",
                "evento-1-startAt": "2026-11-26T00:00",
            }
        ),
    )
    composto = edital
    agora = timezone.now()
    datar(composto, inicio=agora - timedelta(days=9), fim=agora - timedelta(days=1))
    vencidos = EventoCronograma.objects.filter(cronograma__edital=composto).count()
    assert vencidos >= 2, "o cenário precisa de mais de um Evento para haver o que dobrar"

    corpo = client.get(
        reverse("interface:compor-etapa", args=[composto.id, "revisao"])
    ).content.decode()

    grupo = re.search(r'<details class="repetidas">(.*?)</details>', corpo, re.S)
    assert grupo, "os avisos de data passada não foram dobrados"
    assert f"{vencidos} Eventos com data que já passou" in grupo.group(1)
    assert grupo.group(1).count("que já passou. O Edital será publicado") == vencidos
    # Fora do grupo, nenhum: dobrar não é duplicar.
    assert corpo.count("que já passou. O Edital será publicado") == vencidos
