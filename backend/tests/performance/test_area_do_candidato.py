"""T097 — custo de consulta da área do candidato.

Contagem de consultas, e não tempo de parede: o que importa detectar é o custo **crescer com o
histórico**. Uma área que faz uma leitura por inscrição parece rápida com duas e some com dez —
e foi exatamente esse o defeito que a revisão encontrou na listagem.
"""

import uuid

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.inscricoes.models import Inscricao
from tests.fixtures.candidato import MARIA, PERFIL_DOCENTE, PERFIL_TECNICO, identificar

pytestmark = [pytest.mark.django_db, pytest.mark.performance]


def rascunho(selecao, perfil):
    return Inscricao.objects.create(
        id=uuid.uuid4(),
        identity_subject=MARIA.subject,
        edital_id=selecao.id,
        profile_id=perfil,
        nome=MARIA.nome,
        cpf=MARIA.cpf,
        cpf_normalizado="12345678909",
        email=MARIA.email,
        created_at=timezone.now(),
    )


def consultas_da_lista(client):
    with CaptureQueriesContext(connection) as capturadas:
        client.get(reverse("portal:inscricoes"))
    return len(capturadas)


def test_a_lista_nao_cresce_com_o_numero_de_inscricoes(client, selecao):
    """Uma leitura por Edital, e não uma por inscrição.

    Duas inscrições no **mesmo** Edital custam o mesmo que uma: é essa a propriedade que o
    agrupamento por Edital garante, e a que a versão anterior não tinha.
    """
    identificar(client, MARIA)
    rascunho(selecao, PERFIL_DOCENTE)
    com_uma = consultas_da_lista(client)

    rascunho(selecao, PERFIL_TECNICO)
    com_duas = consultas_da_lista(client)

    assert com_duas == com_uma, f"{com_uma} -> {com_duas}"


def test_a_lista_vazia_e_barata(client, selecao):
    identificar(client, MARIA)
    assert consultas_da_lista(client) <= 8


def test_a_lista_com_inscricoes_cabe_no_orcamento(client, selecao):
    identificar(client, MARIA)
    rascunho(selecao, PERFIL_DOCENTE)
    rascunho(selecao, PERFIL_TECNICO)

    assert consultas_da_lista(client) <= 12
