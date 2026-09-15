"""As duas telas públicas não gravam nada (024, FR-151, SC-047 — invariante 2 da §5).

**Por que é teste, e não confiança.** A feature inteira se sustenta em "só renderiza o que já foi
publicado". É fácil de afirmar e fácil de quebrar sem perceber: um contador de visitas, uma linha de
auditoria "para saber quem consultou", um cache gravado em tabela. Nenhum deles quebraria um teste
de conteúdo, e todos quebrariam a promessa — o registro de navegação de candidato é decisão de
proteção de dados sob o Princípio III, e não subproduto de tela (D-008).

**Afirmar sobre a consulta emitida, e não sobre contagem de linhas.** É a lição que
`tests/unit/divulgacao/test_conteudo.py` já registra: contar linhas responde "nada apareceu"; ler o
SQL responde "nada foi escrito". A primeira volta a passar no dia em que alguém gravar e apagar; a
segunda, não.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.auditoria.models import RegistroAuditoria
from tests.fixtures.edital import identificador
from tests.fixtures.publicacao import retify
from tests.fixtures.selecao import LINHA_GERAL_DO_DOCENTE, publicar_selecao

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

PERFIL = identificador(401, 0)
ESCRITA = ("insert into", "update ", "delete from")


def escritas(consultas):
    return [
        item["sql"] for item in consultas if any(verbo in item["sql"].lower() for verbo in ESCRITA)
    ]


@pytest.fixture
def selecao_retificada(api_client, manager_headers, process_payload):
    """Com Retificação publicada: é o caminho que lê mais coisas, e o que mais teria a gravar."""
    edital = publicar_selecao(api_client, manager_headers, process_payload)
    retify(
        api_client,
        edital,
        [
            # **O total e a linha da ampla mudam no mesmo ato** (027, FR-335): o Perfil docente
            # reparte 2 vagas entre a ampla e a PPP, e levar o total a 3 sem mover a linha
            # publicaria um quadro que não fecha. A vaga nova entra na ampla concorrência.
            {
                "targetPath": f"/profiles/id={PERFIL}/immediateVacancies",
                "operation": "REPLACE",
                "newValue": 3,
            },
            {
                "targetPath": (
                    f"/profiles/id={PERFIL}/vacancyTable/id={LINHA_GERAL_DO_DOCENTE}"
                    "/immediateVacancies"
                ),
                "operation": "REPLACE",
                "newValue": 2,
            },
        ],
    )
    return edital


def test_a_vitrine_nao_emite_escrita_alguma(client, selecao_retificada):
    """Inclusive com consulta ativa: filtrar não persiste preferência de ninguém (D-002)."""
    with CaptureQueriesContext(connection) as consultas:
        client.get(reverse("portal:vitrine"))
        client.get(reverse("portal:vitrine"), {"busca": "informatica", "ordem": "recentes"})

    assert escritas(consultas.captured_queries) == []


def test_a_pagina_da_selecao_nao_emite_escrita_alguma(client, selecao_retificada):
    with CaptureQueriesContext(connection) as consultas:
        client.get(reverse("portal:selecao", args=[selecao_retificada.id]))

    assert escritas(consultas.captured_queries) == []


def test_nenhuma_das_duas_registra_auditoria(client, selecao_retificada):
    """A trilha registra ato sensível praticado por alguém identificado.

    Aqui não há ator e não há ato: registrar produziria trilha de leitura anônima, que é vigilância
    de candidato com outro nome.
    """
    antes = RegistroAuditoria.objects.count()

    client.get(reverse("portal:vitrine"), {"busca": "informatica"})
    client.get(reverse("portal:selecao", args=[selecao_retificada.id]))

    assert RegistroAuditoria.objects.count() == antes
