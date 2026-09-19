"""O custo do cálculo é do conjunto, não uma consulta por participante (015, SC-002/SC-003)."""

import time

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.classificacao.application.calculo import calcular_ordem
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from tests.fixtures.comissao import rascunho_com_etapas
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.publicacao import publish_original
from tests.interface.conftest import identificar
from tests.performance.escala import escala

pytestmark = [pytest.mark.performance, pytest.mark.django_db(transaction=True)]

MARCO = "00000000-0000-4000-8000-000000000481"
BUDGET_SECONDS = 2.8
ESCALA = escala()
SEMENTE = 5


@pytest.fixture
def edital_em_escala(api_client, manager_headers, process_payload):
    rascunho = rascunho_com_etapas(avaliacoes=1, maxima="100.0000", minima="0.0000")
    etapa = rascunho["stages"][1]
    etapa["weight"] = "1.0000"
    rascunho["profiles"][0]["classificationMilestones"] = [
        {
            "id": MARCO,
            "code": "FINAL",
            "name": "Classificação final",
            "stages": [etapa["id"]],
            "orderProduction": "POR_PONTUACAO",
            "operation": "SOMA_PONDERADA",
            "normalization": "NENHUMA",
            "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
            "tiebreakers": [],
        }
    ]
    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho)
    _acrescentar_inscricoes(edital, quantidade=SEMENTE, inicio=1)
    return edital


def _acrescentar_inscricoes(edital, *, quantidade, inicio):
    versao = VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")
    agora = timezone.now()
    Inscricao.objects.bulk_create(
        [
            Inscricao(
                identity_subject=f"cpf:escala-{numero:04d}",
                edital=edital,
                profile_id=PROFILE_ID,
                status=Inscricao.Status.SUBMETIDA,
                protocolo=f"E{numero:04d}",
                nome=f"Participante {numero:04d}",
                cpf="111.444.777-35",
                cpf_normalizado="11144477735",
                email=f"escala{numero}@example.test",
                versao_aceita=versao,
                declaracoes_aceitas_em=agora,
                submitted_at=agora,
                created_at=agora,
            )
            for numero in range(inicio, inicio + quantidade)
        ]
    )


def _calcular(edital):
    return calcular_ordem(edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO)


def test_numero_de_consultas_nao_cresce_ate_mil_participantes(edital_em_escala):
    with CaptureQueriesContext(connection) as pequeno:
        _calcular(edital_em_escala)
    _acrescentar_inscricoes(edital_em_escala, quantidade=ESCALA - SEMENTE, inicio=SEMENTE + 1)
    with CaptureQueriesContext(connection) as grande:
        proposta = _calcular(edital_em_escala)

    print(
        f"\n[escala] ordenacao: {SEMENTE} → {ESCALA} participantes, "
        f"{len(pequeno)} → {len(grande)} consultas"
    )
    assert len(proposta["universo"]["participants"]) == ESCALA
    assert len(grande) == len(pequeno)


def test_tela_de_mil_participantes_fica_abaixo_do_teto(
    edital_em_escala,
    client,
    seletor_ligado,
):
    _acrescentar_inscricoes(edital_em_escala, quantidade=ESCALA - SEMENTE, inicio=SEMENTE + 1)
    identificar(client, "gestora", ["gestor"])

    inicio = time.monotonic()
    resposta = client.get(reverse("interface:ordenacao", args=[edital_em_escala.id, MARCO]))
    duracao = time.monotonic() - inicio

    assert resposta.status_code == 200
    print(f"\n[escala] ordenacao: {ESCALA} participantes, tela em {duracao:.3f}s")
    assert duracao < BUDGET_SECONDS, f"a tela levou {duracao:.3f}s com {ESCALA} participantes"


# --- O cálculo por recorte não vira N+1 sobre o conteúdo publicado (034) -----------------------
#
# **Não prende requisito nenhum, e é higiene de engenharia.** Vem do *Technical Context* do
# `plan.md` da `034`: o cálculo por recorte multiplica o número de leituras de um marco pelo número
# de recortes dele, e este projeto já reprova leitura de condição de participação por listagem. O
# que não pode acontecer é o recorte reservado custar consulta por participante, ou reabrir o
# conteúdo publicado uma vez por pessoa.

MODALIDADE_EM_ESCALA = "00000000-0000-4000-8000-000000000491"
LINHA_GERAL_EM_ESCALA = "00000000-0000-4000-8000-000000000492"
LINHA_COTA_EM_ESCALA = "00000000-0000-4000-8000-000000000493"


@pytest.fixture
def edital_em_escala_com_cota(api_client, manager_headers, process_payload):
    """O mesmo Edital em escala, com uma Modalidade reservada e metade dos inscritos nela.

    **Metade, e não um punhado**: um recorte reservado com três pessoas teria custo constante por
    acidente, e não por desenho. O que se mede é que o custo do recorte não acompanha o tamanho
    dele.
    """
    rascunho = rascunho_com_etapas(avaliacoes=1, maxima="100.0000", minima="0.0000")
    etapa = rascunho["stages"][1]
    etapa["weight"] = "1.0000"
    perfil = rascunho["profiles"][0]
    perfil["classificationMilestones"] = [
        {
            "id": MARCO,
            "code": "FINAL",
            "name": "Classificação final",
            "stages": [etapa["id"]],
            "orderProduction": "POR_PONTUACAO",
            "operation": "SOMA_PONDERADA",
            "normalization": "NENHUMA",
            "rounding": {"scale": 2, "mode": "MEIO_PARA_CIMA"},
            "tiebreakers": [],
        }
    ]
    perfil["competitionModalities"] = [
        {
            "id": MODALIDADE_EM_ESCALA,
            "code": "PPI",
            "name": "Pretos, pardos e indígenas",
            "vacancies": 0,
        }
    ]
    perfil["vacancyTable"] = [
        {"id": LINHA_GERAL_EM_ESCALA, "modalityId": None, "immediateVacancies": 1},
        {
            "id": LINHA_COTA_EM_ESCALA,
            "modalityId": MODALIDADE_EM_ESCALA,
            "immediateVacancies": 1,
        },
    ]
    perfil["immediateVacancies"] = 2
    edital = publish_original(api_client, manager_headers, process_payload, draft=rascunho)
    _acrescentar_inscricoes(edital, quantidade=SEMENTE, inicio=1)
    return edital


def _autodeclarar_metade(edital):
    ids = list(
        Inscricao.objects.filter(edital=edital).order_by("protocolo").values_list("id", flat=True)
    )
    Inscricao.objects.filter(id__in=ids[::2]).update(modality_id=MODALIDADE_EM_ESCALA)


def test_o_recorte_reservado_custa_as_mesmas_consultas_que_a_ampla(edital_em_escala_com_cota):
    """O filtro do recorte entra na consulta, e não numa leitura a mais por pessoa."""
    _acrescentar_inscricoes(
        edital_em_escala_com_cota, quantidade=ESCALA - SEMENTE, inicio=SEMENTE + 1
    )
    _autodeclarar_metade(edital_em_escala_com_cota)

    with CaptureQueriesContext(connection) as da_ampla:
        calcular_ordem(edital=edital_em_escala_com_cota, perfil_id=PROFILE_ID, marco_id=MARCO)
    with CaptureQueriesContext(connection) as do_recorte:
        proposta = calcular_ordem(
            edital=edital_em_escala_com_cota,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            lista_id=MODALIDADE_EM_ESCALA,
        )

    print(
        f"\n[escala] ordenacao por recorte: {len(da_ampla)} consultas na ampla, "
        f"{len(do_recorte)} no recorte reservado"
    )
    assert len(proposta["universo"]["participants"]) > 0, "a premissa: o recorte não está vazio"
    assert len(do_recorte) == len(da_ampla)


def test_o_numero_de_consultas_do_recorte_nao_cresce_com_o_universo(edital_em_escala_com_cota):
    """A mesma garantia da ampla, agora por recorte: custo do conjunto, e não do participante."""
    _autodeclarar_metade(edital_em_escala_com_cota)
    with CaptureQueriesContext(connection) as pequeno:
        calcular_ordem(
            edital=edital_em_escala_com_cota,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            lista_id=MODALIDADE_EM_ESCALA,
        )
    _acrescentar_inscricoes(
        edital_em_escala_com_cota, quantidade=ESCALA - SEMENTE, inicio=SEMENTE + 1
    )
    _autodeclarar_metade(edital_em_escala_com_cota)
    with CaptureQueriesContext(connection) as grande:
        calcular_ordem(
            edital=edital_em_escala_com_cota,
            perfil_id=PROFILE_ID,
            marco_id=MARCO,
            lista_id=MODALIDADE_EM_ESCALA,
        )

    print(
        f"\n[escala] ordenacao por recorte: {SEMENTE} → {ESCALA} participantes, "
        f"{len(pequeno)} → {len(grande)} consultas"
    )
    assert len(grande) == len(pequeno)
