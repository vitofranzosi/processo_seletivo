"""A jornada demonstrável da `022`: quem preside abre o Processo e sabe onde ele está.

`SC-001` e `FR-005`. A frase que governa a feature é esta, e este teste é ela executada: quem
preside abre o Processo e identifica **o que aconteceu**, **o que deveria acontecer agora** e **se
existe condição que impede o próximo ato** — numa tela só, sem navegar.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.comissoes.domain.funcoes import Funcao
from tests.fixtures.comissao import constituir
from tests.fixtures.publicacao import publish_original
from tests.fixtures.supervisao import (
    SEGUNDO_SEED,
    etapa_ligada,
    publicar_no_processo,
    rascunhar,
    rascunho_com_periodo,
    submeter,
)
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.acceptance, pytest.mark.django_db(transaction=True)]


def texto(corpo):
    sem_folha = re.sub(r"(?s)<style>.*?</style>", " ", corpo)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", sem_folha))


def test_quem_preside_ve_situacao_volume_prazo_e_impedimento_numa_tela_so(
    gestor, api_client, manager_headers, client, seletor_ligado
):
    """O percurso inteiro, pelo canal de quem preside — e nenhum número vindo de lugar nenhum novo.

    Todo valor apresentado é reproduzível a partir dos registros das donas (`FR-005`): a soma é a
    das inscrições de cada Edital, o prazo é o Evento marcado do cronograma publicado, e o sinal é
    a Etapa que o próprio Edital publicou sem marco.
    """
    primeiro = publish_original(
        api_client,
        {**manager_headers, "HTTP_IDEMPOTENCY_KEY": "aceitacao-022-0001"},
        {
            "institutionalCode": "PS-2026-022",
            "title": "Processo Seletivo de Supervisão",
            "firstEdital": {"number": "11", "year": 2026, "title": "Edital de docentes"},
        },
        draft=rascunho_com_periodo(
            11,
            etapas=[
                etapa_ligada(11, nome="Análise documental"),
                # A segunda Etapa não declara Evento: é publicável e legítimo, e é o sinal que a
                # presidência precisa ver sem abrir a composição.
                {
                    "id": "00000000-0000-0000-0000-000000000560",
                    "name": "Prova didática",
                    "order": 2,
                    "eliminatory": False,
                    "classificatory": True,
                },
            ],
            status_do_periodo="EM_ANDAMENTO",
        ),
    )
    processo = primeiro.processo
    segundo = publicar_no_processo(
        api_client,
        manager_headers,
        processo,
        number="12",
        year=2026,
        title="Edital de técnicos",
        chave="aceitacao-022-segundo",
        draft=rascunho_com_periodo(
            SEGUNDO_SEED, etapas=[etapa_ligada(SEGUNDO_SEED)], status_do_periodo="EM_ANDAMENTO"
        ),
    )
    constituir(gestor, processo, [("maria", Funcao.PRESIDENTE)], prefixo="aceitacao-022")
    submeter(primeiro, 8, seed=11)
    submeter(segundo, 3, primeiro=100, seed=SEGUNDO_SEED)
    rascunhar(primeiro, 2, seed=11)

    identificar(client, "maria", [])
    # O caminho existe a partir da página do Processo: sem ele a capacidade não é alcançável.
    painel = client.get(reverse("interface:processo-detalhe", args=[processo.id])).content.decode()
    assert reverse("interface:supervisao", args=[processo.id]) in painel

    resposta = client.get(reverse("interface:supervisao", args=[processo.id]))
    assert resposta.status_code == 200
    lido = texto(resposta.content.decode())

    # O que aconteceu: a soma do Processo, desdobrada por Edital nomeado.
    assert "11 inscrições recebidas no Processo" in lido
    assert "2 em preenchimento" in lido
    assert "11/2026" in lido and "12/2026" in lido

    # O que deveria acontecer agora: o prazo de cada Edital, e o volume recente do Processo.
    assert "11 nas últimas 24 horas" in lido
    assert "Inscrições de" in lido
    assert "Encerra em" in lido

    # E se existe condição que impede o próximo ato.
    assert "está sem marco no cronograma" in lido
    assert (
        reverse("interface:compor-etapa", args=[primeiro.id, "etapas"]) in resposta.content.decode()
    )
