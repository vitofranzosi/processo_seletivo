"""Reenviar o lote não cria nada — nem Atribuição, nem evento (FR-084, FR-086).

Duas mil atribuições distribuídas em lotes reenviáveis: timeout, duplo clique e F5 são o caminho
normal, não a exceção. O invólucro de comando da 011 já resolve os três, e o que este arquivo
verifica é o **resultado observável** de herdá-lo.
"""

import pytest

from processo_seletivo.auditoria.models import RegistroAuditoria
from processo_seletivo.avaliacoes.application.distribuicao import (
    ATRIBUIR,
    distribuir,
    remover_atribuicao,
)
from processo_seletivo.avaliacoes.models import Atribuicao
from processo_seletivo.comissoes.application.comissao import alterar_funcao
from processo_seletivo.comissoes.domain.funcoes import Funcao
from processo_seletivo.shared.api.problems import DomainError
from tests.conftest import ator_institucional
from tests.fixtures.comissao import alocar_em, constituir, inscrever

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def cenario(gestor, processo_a, edital_a, comissao_de_a, etapa_a1):
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    return {
        "joao": comissao_de_a["joao"],
        "maria": comissao_de_a["maria"],
        "inscricoes": inscrever(edital_a, 3),
    }


def lote(gestor, edital, etapa_id, membro, inscricoes, chave):
    return distribuir(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=etapa_id,
        membro_ids=[membro.id],
        inscricao_ids=[i.id for i in inscricoes],
        idempotency_key=chave,
        correlation_id="teste",
    )


def test_o_reenvio_devolve_o_desfecho_original(gestor, edital_a, etapa_a1, cenario):
    """**O desfecho, e não um vazio.**

    Zero atribuídas e zero recusadas seria resposta falsa: a tela diria que o lote não fez nada,
    quando ele fez tudo. E recusa não é reconstruível depois — o estado que a produziu mudou no ato
    seguinte —, então o resultado é guardado na reserva (FR-084, FR-097).
    """
    primeiro = lote(gestor, edital_a, etapa_a1, cenario["joao"], cenario["inscricoes"], "mesma")
    atribuicoes = Atribuicao.objects.count()
    eventos = RegistroAuditoria.objects.filter(operation=ATRIBUIR).count()

    repetido = lote(gestor, edital_a, etapa_a1, cenario["joao"], cenario["inscricoes"], "mesma")

    assert repetido == primeiro
    assert repetido["feitas"] == 3
    assert Atribuicao.objects.count() == atribuicoes
    assert RegistroAuditoria.objects.filter(operation=ATRIBUIR).count() == eventos


def test_o_reenvio_devolve_tambem_as_recusas(gestor, edital_a, etapa_a1, cenario):
    """A metade que só o registro guarda: a repetição não recalcularia as recusas."""
    lote(gestor, edital_a, etapa_a1, cenario["joao"], cenario["inscricoes"], "a")
    primeiro = lote(gestor, edital_a, etapa_a1, cenario["joao"], cenario["inscricoes"], "b")

    repetido = lote(gestor, edital_a, etapa_a1, cenario["joao"], cenario["inscricoes"], "b")

    assert primeiro["recusadas"] == 3
    assert repetido["motivos"] == primeiro["motivos"]


def test_a_mesma_chave_com_outro_conteudo_e_conflito(gestor, edital_a, etapa_a1, cenario):
    """Repetir é devolver o desfecho; **mudar** o conteúdo sob a mesma chave é outra coisa."""
    lote(gestor, edital_a, etapa_a1, cenario["joao"], cenario["inscricoes"][:1], "mesma")

    with pytest.raises(DomainError) as recusa:
        lote(gestor, edital_a, etapa_a1, cenario["joao"], cenario["inscricoes"][1:], "mesma")

    assert recusa.value.code == "idempotency_conflict"


def test_quem_perdeu_a_presidencia_no_intervalo_nao_conclui_o_ato(
    gestor, processo_a, edital_a, etapa_a1, cenario
):
    """A base é reavaliada **depois** do bloqueio, e a presidência é dado que muda (FR-086).

    Maria preside e distribui pela presidência; rebaixada, ela deixa de alcançar o Processo — e a
    repetição não pode responder a quem já não pode.
    """
    maria = ator_institucional("maria")
    lote(maria, edital_a, etapa_a1, cenario["joao"], cenario["inscricoes"][:1], "de-maria")
    # A 011 recusa deixar a comissão sem presidente enquanto há alocação ativa: para rebaixar
    # Maria é preciso que outra pessoa presida antes. O invariante dela continua valendo aqui.
    constituir(gestor, processo_a, [("ana", Funcao.PRESIDENTE)], prefixo="sucessao")
    alterar_funcao(
        actor=gestor,
        processo_id=processo_a.id,
        membro_id=cenario["maria"].id,
        funcao=Funcao.MEMBRO,
        idempotency_key="rebaixar-maria",
        correlation_id="teste",
    )

    with pytest.raises(DomainError) as recusa:
        lote(maria, edital_a, etapa_a1, cenario["joao"], cenario["inscricoes"][1:2], "de-maria-2")

    assert recusa.value.status == 404


def test_a_remocao_tambem_e_idempotente(gestor, edital_a, etapa_a1, cenario):
    criadas = lote(gestor, edital_a, etapa_a1, cenario["joao"], cenario["inscricoes"], "a")
    argumentos = {
        "actor": gestor,
        "processo_id": edital_a.processo_id,
        "atribuicao_ids": criadas["ids"],
        "idempotency_key": "remocao",
        "correlation_id": "teste",
    }
    removidas = remover_atribuicao(**argumentos)

    repetidas = remover_atribuicao(**argumentos)

    assert removidas["feitas"] == 3
    assert repetidas == removidas
    assert Atribuicao.objects.filter(ativo=True).count() == 0
