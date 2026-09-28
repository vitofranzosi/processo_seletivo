"""Corte que não governa Etapa chega à apuração e à convocação (RC-113; 014, `FR-224`).

**A `FR-224` admite o corte que declara não governar Etapa alguma**, e é a forma do 69/2026 — o
marco terminal: sorteia, publica, convoca. A ocupação lia a habilitação na Etapa governada, e sem
Etapa governada devolvia o conjunto vazio: ninguém ocupava, ninguém era chamável, e a forma mais
simples da amostra parava antes da convocação sem recusa nenhuma que dissesse por quê.

Sem Etapa governada não há Resultado posterior a exigir: quem progrediu na faixa é quem segue. É
o mesmo cenário da `016`, com a única diferença de o corte declarar `NONE` — e é por isso que ele
não consolida a Entrevista, que aqui ninguém consome.
"""

import pytest

from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.publicacoes.domain.vocabulario_da_regra import (
    FORMA_POR_MENSAGEM_INDIVIDUAL,
)
from tests.fixtures.convocacao import apurar, convocar
from tests.fixtures.corte import MARCO, regra
from tests.fixtures.edital import PROFILE_ID
from tests.fixtures.ocupacao import montar_cenario_da_ocupacao

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def cenario(db, gestor, api_client, manager_headers, process_payload, raiz_de_arquivos):
    """Quatro inscritos, faixa de dois, quadro de três — e o corte não governa Etapa."""
    return montar_cenario_da_ocupacao(
        gestor,
        api_client,
        manager_headers,
        process_payload,
        prefixo="rc-113",
        cut=regra(governedStage="NONE"),
        forma=FORMA_POR_MENSAGEM_INDIVIDUAL,
    )


def contexto(edital):
    return selectors.contexto_do_recorte(
        edital=edital, perfil_id=PROFILE_ID, marco_id=MARCO, lista_id=None
    )


def test_quem_progrediu_ocupa_sem_etapa_governada(cenario, gestor):
    """Os dois que a faixa alcançou ocupam, e sobra uma das três vagas — não as três."""
    edital, _, _ = cenario

    declarado = apurar(edital, gestor, chave="rc-113-apurar")

    assert declarado["universo"]["cutId"], "a apuração leu o corte, e ele não governa Etapa"
    assert declarado["ocupadas"] == 2
    assert declarado["faltando"] == 1


def test_quem_progrediu_e_chamavel_sem_etapa_governada(cenario, gestor):
    """A fila tem os dois da faixa, na ordem, e a primeira convocação do certame acontece."""
    edital, _, _ = cenario
    apurar(edital, gestor, chave="rc-113-apurar")

    lido = contexto(edital)

    assert len(lido["fila"]) == 2, "a faixa de dois é a fila inteira, e ninguém fora dela"
    declarado = convocar(edital, gestor, lido["fila"][0], idempotency_key="rc-113-convoca")
    assert Convocacao.objects.filter(id=declarado["id"]).exists()
