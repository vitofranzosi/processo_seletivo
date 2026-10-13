"""O desfecho prevalece sobre o período, mas só depois de acontecer (070, `CA-29`, `R-006`).

O estado do Edital é o de agora. Com instante de referência anterior ao ato de cancelamento, a
resposta não pode dizer que o Edital já estava cancelado.
"""

from datetime import timedelta

import pytest

from processo_seletivo.duvidas.application.consultar import consultar
from processo_seletivo.processos.application.finalizacao import cancel_edital, cancel_process
from processo_seletivo.processos.models import AtoAdministrativo
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.seguranca.domain import Actor
from tests.fixtures.corpus import publicar_do_corpus

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.integration]

GESTORA = Actor(
    "gestora.duvidas",
    "cefor",
    frozenset({"processo:cancelar", "edital:cancelar"}),
)
MOTIVO = "Cancelamento para o teste da fonte de consulta do assistente de dúvidas."


def _cancelar(edital):
    edital.refresh_from_db()
    cancel_edital(
        actor=GESTORA,
        edital_id=edital.id,
        expected_revision=edital.revision,
        reason=MOTIVO,
        idempotency_key=f"cancelar-duvidas-{edital.id}",
        correlation_id="070-desfecho",
    )
    return AtoAdministrativo.objects.filter(aggregate_id=edital.id).latest("occurred_at")


def test_ca29_o_edital_cancelado_nao_esta_em_curso(api_client):
    edital, _ = publicar_do_corpus(api_client, "91", chave="d-ca29")
    ato = _cancelar(edital)

    depois = consultar(
        edital_id=edital.id, instante=ato.occurred_at + timedelta(minutes=1), pergunta="P-01"
    )
    assert depois.explicacao.conteudo.startswith("As inscrições não estão em curso")
    assert any(
        a.tipo == "DESFECHO" and "Este Edital foi cancelado" in a.texto for a in depois.avisos
    )

    # Entre a última versão e o cancelamento: o Edital acabou de ser publicado, e um minuto antes
    # do ato ainda não havia versão vigente nenhuma.
    ultima = VersaoConsolidada.objects.filter(edital=edital).latest("valid_from").valid_from
    antes = consultar(
        edital_id=edital.id, instante=ultima + (ato.occurred_at - ultima) / 2, pergunta="P-01"
    )
    assert not [a for a in antes.avisos if a.tipo == "DESFECHO"]


def test_com_os_dois_desfechos_vale_o_do_edital(api_client):
    """O Processo só se cancela com todo Edital já final (`finalizacao.py`): pelo fluxo real, o
    desfecho do Processo sozinho não se alcança. O caso dele está em
    `tests/unit/duvidas/test_casos_da_revisao.py`."""
    edital, _ = publicar_do_corpus(api_client, "91", chave="d-processo")
    _cancelar(edital)
    edital.processo.refresh_from_db()
    cancel_process(
        actor=GESTORA,
        processo_id=edital.processo_id,
        expected_revision=edital.processo.revision,
        reason=MOTIVO,
        idempotency_key=f"cancelar-processo-duvidas-{edital.processo_id}",
        correlation_id="070-desfecho",
    )
    resposta = consultar(
        edital_id=edital.id,
        instante=AtoAdministrativo.objects.latest("occurred_at").occurred_at + timedelta(minutes=1),
        pergunta="P-01",
    )
    # O do Edital vence o do Processo (`desfechos`): o Edital cancelado é o que se diz.
    assert any(a.tipo == "DESFECHO" and "Este Edital" in a.texto for a in resposta.avisos)
